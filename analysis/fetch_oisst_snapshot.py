"""Fetch and package one reproducible NOAA OISST display snapshot.

The output is a compact JavaScript data artifact so Atlas 02 also works when
opened directly from disk. Temperatures are stored as integer hundredths of a
degree Celsius; missing values remain null. Supported fields are absolute sea
surface temperature (sst), the published 1971-2000 anomaly (anom), and the
time-matched estimated analysis error (err).
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import math
import pathlib
import urllib.parse
import urllib.request


DATASET_ID = "ncdc_oisst_v2_avhrr_by_time_zlev_lat_lon"
ERDDAP = "https://www.ncei.noaa.gov/erddap/griddap"
NCSS = "https://www.ncei.noaa.gov/thredds/ncss/grid/OisstBase/NetCDF/V2.1/AVHRR"
DOI = "https://doi.org/10.25921/RE9P-PT57"
DEFAULT_DATE = "2026-08-01"
DEFAULT_STRIDE = 8
VARIABLES = {
    "sst": {
        "name": "sea surface temperature",
        "window": "OCEANLINES_OISST",
        "baseline": None,
        "boundary": "SST is a surface temperature field, not full-depth heat content or heat transport.",
    },
    "anom": {
        "name": "sea surface temperature anomaly",
        "window": "OCEANLINES_OISST_ANOMALY",
        "baseline": "1971-2000 climatological mean",
        "boundary": "SST anomaly is departure from a historical surface climatology, not absolute temperature, heat content, or attribution.",
    },
    "err": {
        "name": "estimated sea surface temperature analysis error",
        "window": "OCEANLINES_OISST_ERROR",
        "baseline": None,
        "boundary": "Estimated OISST analysis error describes product uncertainty at the surface; it is not forecast error, a confidence interval, or uncertainty in full-depth heat content.",
    },
}


def build_query(date: str, stride: int, variable: str = "sst") -> str:
    if variable not in VARIABLES:
        raise ValueError(f"unsupported variable: {variable}")
    constraint = (
        f"{variable}[({date}T12:00:00Z)][(0.0)]"
        f"[(-89.875):{stride}:(89.875)]"
        f"[(0.125):{stride}:(359.875)]"
    )
    # Encode square brackets so urllib and intermediary proxies preserve the
    # ERDDAP constraint as one query expression.
    return f"{ERDDAP}/{DATASET_ID}.csv0?{urllib.parse.quote(constraint, safe='():.-')}"


def build_ncss_query(date: str, stride: int, variable: str = "sst") -> str:
    if variable not in VARIABLES:
        raise ValueError(f"unsupported variable: {variable}")
    month = date.replace("-", "")[:6]
    day = date.replace("-", "")
    query = urllib.parse.urlencode({
        "var": variable, "north": "89.875", "west": "0.125",
        "east": "359.875", "south": "-89.875", "horizStride": stride,
        "time": f"{date}T12:00:00Z", "accept": "netcdf3",
    })
    return f"{NCSS}/{month}/oisst-avhrr-v02r01.{day}.nc?{query}"


def fetch(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "OSW/0.1 (public research atlas)"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def parse_rows(raw: bytes) -> tuple[list[int | None], list[float], list[float]]:
    values: list[int | None] = []
    latitudes: list[float] = []
    longitudes: list[float] = []
    reader = csv.reader(io.StringIO(raw.decode("utf-8")))
    for row in reader:
        if len(row) != 5:
            raise ValueError(f"expected five columns, got {len(row)}")
        latitude = float(row[2])
        longitude = float(row[3])
        value = float(row[4])
        latitudes.append(latitude)
        longitudes.append(longitude)
        values.append(None if math.isnan(value) else round(value * 100))
    return values, latitudes, longitudes


def parse_netcdf(raw: bytes, variable: str) -> tuple[list[int | None], list[float], list[float]]:
    try:
        from netCDF4 import Dataset
    except ImportError as error:
        raise RuntimeError("the NCSS backend requires netCDF4; install requirements-observations.txt") from error
    with Dataset("oisst-snapshot.nc", memory=raw) as dataset:
        latitudes_axis = [float(value) for value in dataset.variables["lat"][:]]
        longitudes_axis = [float(value) for value in dataset.variables["lon"][:]]
        grid = dataset.variables[variable][0, 0, :, :]
        values = []
        for value in grid.flat:
            if bool(getattr(value, "mask", False)):
                values.append(None)
                continue
            number = float(value)
            values.append(None if math.isnan(number) else round(number * 100))
    latitudes = [latitude for latitude in latitudes_axis for _ in longitudes_axis]
    longitudes = longitudes_axis * len(latitudes_axis)
    return values, latitudes, longitudes


def package(raw: bytes, date: str, stride: int, retrieved_at: str, variable: str = "sst", backend: str = "erddap") -> dict:
    definition = VARIABLES[variable]
    values, latitudes, longitudes = parse_rows(raw) if backend == "erddap" else parse_netcdf(raw, variable)
    unique_latitudes = list(dict.fromkeys(latitudes))
    unique_longitudes = list(dict.fromkeys(longitudes))
    expected = len(unique_latitudes) * len(unique_longitudes)
    if expected != len(values):
        raise ValueError(f"incomplete rectangular grid: {len(values)} of {expected}")
    if len(values) < 1000:
        raise ValueError("snapshot is unexpectedly small")
    valid_values = [value for value in values if value is not None]
    return {
        "schema": "oceanlines.oisst.snapshot.v2",
        "status": "observational surface field",
        "source": "NOAA/NCEI OISST v2.1 AVHRR-only final",
        "dataset_id": DATASET_ID,
        "doi": DOI,
        "date": date,
        "retrieved_at": retrieved_at,
        "query_url": build_query(date, stride, variable) if backend == "erddap" else build_ncss_query(date, stride, variable),
        "source_format": "csv0" if backend == "erddap" else "netcdf3",
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "variable_id": variable,
        "variable": definition["name"],
        "baseline": definition["baseline"],
        "units": "degree_C",
        "depth_m": 0.0,
        "precision": 0.01,
        "display_stride": stride,
        "native_resolution_degrees": 0.25,
        "shape": [len(unique_latitudes), len(unique_longitudes)],
        "latitude": {"start": unique_latitudes[0], "step": unique_latitudes[1] - unique_latitudes[0]},
        "longitude": {"start": unique_longitudes[0], "step": unique_longitudes[1] - unique_longitudes[0]},
        "values_c_hundredths": values,
        "summary": {
            "cells": len(values),
            "valid_ocean_cells": len(valid_values),
            "missing_or_land_cells": len(values) - len(valid_values),
            "minimum_c": min(valid_values) / 100,
            "maximum_c": max(valid_values) / 100,
        },
        "boundary": definition["boundary"],
    }


def write_artifact(payload: dict, output: pathlib.Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    output.write_text(
        "// Generated by analysis/fetch_oisst_snapshot.py; do not edit by hand.\n"
        f"window.{VARIABLES[payload['variable_id']]['window']}={serialized};\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=DEFAULT_DATE, help="final-product day, YYYY-MM-DD")
    parser.add_argument("--variable", choices=sorted(VARIABLES), default="sst", help="OISST field to package")
    parser.add_argument("--backend", choices=("erddap", "ncss"), default="erddap", help="official NOAA subset service")
    parser.add_argument("--stride", type=int, default=DEFAULT_STRIDE, help="stride over the native 0.25-degree grid")
    parser.add_argument("--retrieved-at", help="ISO provenance time; defaults to current UTC")
    parser.add_argument("--output", type=pathlib.Path, help="artifact path; defaults from variable and date")
    args = parser.parse_args()
    dt.date.fromisoformat(args.date)
    if args.stride < 1:
        parser.error("--stride must be positive")
    if args.output is None:
        label = {"sst": "oisst", "anom": "oisst-anomaly", "err": "oisst-error"}[args.variable]
        args.output = pathlib.Path(f"atlas/data/{label}-{args.date}.js")
    retrieved_at = args.retrieved_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    url = build_query(args.date, args.stride, args.variable) if args.backend == "erddap" else build_ncss_query(args.date, args.stride, args.variable)
    raw = fetch(url)
    payload = package(raw, args.date, args.stride, retrieved_at, args.variable, args.backend)
    write_artifact(payload, args.output)
    print(f"wrote {args.output} ({payload['shape'][0]} x {payload['shape'][1]} cells)")
    print(f"source sha256 {payload['source_sha256']}")


if __name__ == "__main__":
    main()
