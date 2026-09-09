"""Fetch and package one reproducible RG Argo pressure-layer anomaly.

The monthly RG extension is an objectively mapped anomaly product. It is not
an absolute-temperature field, a raw-float map, or an ocean heat-content
calculation.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import pathlib
import urllib.request


SOURCE_ROOT = "https://sio-argo.ucsd.edu/RG"
PRODUCT_VERSION = "2019"
VARIABLE = "ARGO_TEMPERATURE_ANOMALY"
WINDOW_PREFIX = "OCEANLINES_ARGO_TEMPERATURE_ANOMALY"


def window_name(pressure_dbar: float) -> str:
    if not float(pressure_dbar).is_integer():
        raise ValueError("browser artifacts require an integer pressure level")
    return f"{WINDOW_PREFIX}_{int(pressure_dbar)}DBAR"


def build_url(month: str) -> str:
    year, month_number = month.split("-")
    if len(year) != 4 or len(month_number) != 2:
        raise ValueError("month must use YYYY-MM")
    return f"{SOURCE_ROOT}/RG_ArgoClim_{year}{month_number}_{PRODUCT_VERSION}.nc.gz"


def read_source(url: str, source_file: pathlib.Path | None = None) -> bytes:
    if source_file is not None:
        return source_file.read_bytes()
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read()


def parse_layer(compressed: bytes, pressure_dbar: float, stride: int) -> dict:
    try:
        from netCDF4 import Dataset
        import numpy
    except ImportError as error:  # pragma: no cover - exercised by CLI users
        raise RuntimeError("Install requirements-observations.txt") from error

    if stride < 1:
        raise ValueError("stride must be at least 1")
    raw = gzip.decompress(compressed)
    with Dataset("rg-argo-month.nc", memory=raw) as dataset:
        required = {"LONGITUDE", "LATITUDE", "PRESSURE", "TIME", VARIABLE}
        missing = required.difference(dataset.variables)
        if missing:
            raise ValueError(f"RG Argo file is missing variables: {sorted(missing)}")

        pressures = numpy.asarray(dataset["PRESSURE"][:], dtype=float)
        matches = numpy.flatnonzero(numpy.isclose(pressures, pressure_dbar, atol=1e-6))
        if len(matches) != 1:
            available = ", ".join(f"{value:g}" for value in pressures)
            raise ValueError(f"pressure {pressure_dbar:g} dbar is unavailable; choose one of: {available}")
        pressure_index = int(matches[0])

        latitudes = numpy.asarray(dataset["LATITUDE"][::stride], dtype=float)
        longitudes = numpy.asarray(dataset["LONGITUDE"][::stride], dtype=float)
        field = numpy.ma.asarray(dataset[VARIABLE][0, pressure_index, ::stride, ::stride])
        if field.shape != (len(latitudes), len(longitudes)):
            raise ValueError("RG Argo layer dimensions do not match its coordinates")

        values = []
        for value in field.reshape(-1):
            values.append(None if numpy.ma.is_masked(value) else round(float(value) * 100))
        valid = [value for value in values if value is not None]
        if not valid:
            raise ValueError("RG Argo layer contains no valid values")

        return {
            "pressure_dbar": float(pressures[pressure_index]),
            "time_months_since_2004": float(dataset["TIME"][0]),
            "shape": [len(latitudes), len(longitudes)],
            "latitude": {
                "start": float(latitudes[0]),
                "step": float(latitudes[1] - latitudes[0]),
            },
            "longitude": {
                "start": float(longitudes[0]),
                "step": float(longitudes[1] - longitudes[0]),
            },
            "values_c_hundredths": values,
            "summary": {
                "cells": len(values),
                "valid_ocean_cells": len(valid),
                "missing_or_land_cells": len(values) - len(valid),
                "minimum_c": min(valid) / 100,
                "maximum_c": max(valid) / 100,
            },
        }


def package(
    compressed: bytes,
    month: str,
    pressure_dbar: float,
    stride: int,
    retrieved_at: str,
    source_url: str,
) -> dict:
    layer = parse_layer(compressed, pressure_dbar, stride)
    return {
        "schema": "oceanlines.argo.pressure-anomaly.v1",
        "status": "observationally constrained gridded subsurface anomaly",
        "source": "Scripps RG Argo Climatology monthly extension",
        "product_version": PRODUCT_VERSION,
        "argo_doi": "https://doi.org/10.17882/42182",
        "method_doi": "https://doi.org/10.1016/j.pocean.2009.03.004",
        "source_data_terms": (
            "International Argo Program data are freely available; acknowledge Argo "
            "and cite https://doi.org/10.17882/42182. The repository MIT license does "
            "not replace source-data citation requirements."
        ),
        "month": month,
        "retrieved_at": retrieved_at,
        "query_url": source_url,
        "source_format": "gzip-compressed NetCDF",
        "source_sha256": hashlib.sha256(compressed).hexdigest(),
        "variable_id": VARIABLE,
        "variable": "potential temperature anomaly",
        "baseline": "RG 2019 mean and annual cycle derived from 2004-2018 Argo data",
        "units": "degree_C",
        "precision": 0.01,
        "display_stride": stride,
        "native_resolution_degrees": 1.0,
        "uncertainty": (
            "No per-cell uncertainty field is packaged in this display artifact; "
            "objective mapping and sampling limitations must be interpreted from the product method."
        ),
        **layer,
        "boundary": (
            "Objectively mapped Argo anomaly at one pressure level; not absolute temperature, "
            "raw-float coverage, heat content, transport, or Antarctic shelf and cavity heat delivery. "
            "The RG grid ends at 64.5 degrees south and smooths unresolved spatial structure."
        ),
    }


def write_artifact(payload: dict, output: pathlib.Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, separators=(",", ":"), allow_nan=False)
    output.write_text(
        "// Generated by analysis/fetch_argo_snapshot.py; do not edit by hand.\n"
        f"window.{window_name(payload['pressure_dbar'])}={serialized};\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--month", required=True, help="fixed monthly extension in YYYY-MM form")
    parser.add_argument("--pressure-dbar", type=float, default=700.0)
    parser.add_argument("--stride", type=int, default=2, help="sample every N native grid cells")
    parser.add_argument("--retrieved-at", required=True, help="UTC ISO-8601 retrieval timestamp")
    parser.add_argument("--source-file", type=pathlib.Path, help="optional already-downloaded .nc.gz")
    parser.add_argument("--output", type=pathlib.Path, required=True)
    arguments = parser.parse_args()

    url = build_url(arguments.month)
    compressed = read_source(url, arguments.source_file)
    payload = package(
        compressed,
        arguments.month,
        arguments.pressure_dbar,
        arguments.stride,
        arguments.retrieved_at,
        url,
    )
    write_artifact(payload, arguments.output)


if __name__ == "__main__":
    main()
