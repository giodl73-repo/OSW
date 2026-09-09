"""Discover, fetch, and package one reproducible OSCAR surface-current day.

The resulting JavaScript artifact contains thinned zonal and meridional
velocity components as signed integer millimetres per second. OSCAR v2.0 is a
satellite-informed diagnostic mixed-layer product averaged over an assumed
well-mixed upper 30 m. It is not full-depth velocity or ocean heat transport.

Earthdata payloads are protected. Supply a temporary EARTHDATA_TOKEN or use
--input with a NetCDF granule retrieved by NASA's official PO.DAAC subscriber.
No credential is written to the artifact.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import pathlib
import urllib.parse
import urllib.request


COLLECTION = "OSCAR_L4_OC_FINAL_V2.0"
COLLECTION_CONCEPT_ID = "C2098858642-POCLOUD"
CMR_GRANULES = "https://cmr.earthdata.nasa.gov/search/granules.json"
DOI = "https://doi.org/10.5067/OSCAR-25F20"
DEFAULT_DATE = "2025-01-01"
DEFAULT_STRIDE = 8
USER_AGENT = "OSW/0.1 (public research atlas)"


def build_cmr_query(date: str) -> str:
    day = dt.date.fromisoformat(date)
    start = f"{day.isoformat()}T00:00:00Z"
    stop = f"{day.isoformat()}T23:59:59Z"
    query = urllib.parse.urlencode({
        "collection_concept_id": COLLECTION_CONCEPT_ID,
        "temporal": f"{start},{stop}",
        "page_size": 10,
    })
    return f"{CMR_GRANULES}?{query}"


def fetch_bytes(url: str, token: str | None = None) -> bytes:
    headers = {"User-Agent": USER_AGENT}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=180) as response:
        return response.read()


def discover_granule(date: str) -> tuple[str, str, str]:
    query_url = build_cmr_query(date)
    response = json.loads(fetch_bytes(query_url).decode("utf-8"))
    entries = response.get("feed", {}).get("entry", [])
    candidates: list[tuple[str, str]] = []
    for entry in entries:
        title = entry.get("title", "")
        for link in entry.get("links", []):
            href = link.get("href", "")
            if href.endswith(".nc") and "inherited" not in link:
                candidates.append((title, href))
    if len(candidates) != 1:
        raise ValueError(
            f"expected one OSCAR NetCDF granule for {date}, found {len(candidates)}"
        )
    title, granule_url = candidates[0]
    return title, granule_url, query_url


def _axis(dataset, choices: tuple[str, ...]) -> tuple[str, list[float]]:
    for name in choices:
        if name in dataset.variables:
            return name, [float(value) for value in dataset.variables[name][:]]
    raise ValueError(f"missing coordinate axis; expected one of {choices}")


def _component_grid(dataset, variable: str, lat_name: str, lon_name: str):
    if variable not in dataset.variables:
        raise ValueError(f"missing OSCAR component: {variable}")
    source = dataset.variables[variable]
    dimensions = list(source.dimensions)
    index = []
    for dimension in dimensions:
        index.append(slice(None) if dimension in (lat_name, lon_name) else 0)
    grid = source[tuple(index)]
    remaining = [name for name in dimensions if name in (lat_name, lon_name)]
    if remaining == [lon_name, lat_name]:
        grid = grid.T
    elif remaining != [lat_name, lon_name]:
        raise ValueError(f"unsupported {variable} dimensions: {dimensions}")
    return grid


def _quantize(value) -> int | None:
    if bool(getattr(value, "mask", False)):
        return None
    number = float(value)
    return None if math.isnan(number) else round(number * 1000)


def package(
    raw: bytes,
    date: str,
    stride: int,
    retrieved_at: str,
    granule_id: str,
    granule_url: str,
    discovery_url: str,
) -> dict:
    try:
        from netCDF4 import Dataset
    except ImportError as error:
        raise RuntimeError(
            "OSCAR packaging requires netCDF4; install requirements-observations.txt"
        ) from error
    if stride < 1:
        raise ValueError("stride must be positive")
    with Dataset("oscar-snapshot.nc", memory=raw) as dataset:
        lat_name, latitudes = _axis(dataset, ("latitude", "lat"))
        lon_name, longitudes = _axis(dataset, ("longitude", "lon"))
        u_grid = _component_grid(dataset, "u", lat_name, lon_name)
        v_grid = _component_grid(dataset, "v", lat_name, lon_name)
        selected_latitudes = latitudes[::stride]
        selected_longitudes = longitudes[::stride]
        u_values: list[int | None] = []
        v_values: list[int | None] = []
        for lat_index in range(0, len(latitudes), stride):
            for lon_index in range(0, len(longitudes), stride):
                u_value = _quantize(u_grid[lat_index, lon_index])
                v_value = _quantize(v_grid[lat_index, lon_index])
                if u_value is None or v_value is None:
                    u_value = None
                    v_value = None
                u_values.append(u_value)
                v_values.append(v_value)
    expected = len(selected_latitudes) * len(selected_longitudes)
    if len(u_values) != expected or not selected_latitudes or not selected_longitudes:
        raise ValueError("incomplete OSCAR display grid")
    valid_speeds = [
        math.hypot(u / 1000, v / 1000)
        for u, v in zip(u_values, v_values)
        if u is not None and v is not None
    ]
    if not valid_speeds:
        raise ValueError("OSCAR granule contains no valid selected velocities")
    return {
        "schema": "oceanlines.oscar.snapshot.v1",
        "status": "modeled satellite-informed mixed-layer velocity",
        "source": "NASA PO.DAAC OSCAR Surface Currents Final v2.0",
        "collection": COLLECTION,
        "collection_concept_id": COLLECTION_CONCEPT_ID,
        "doi": DOI,
        "date": date,
        "retrieved_at": retrieved_at,
        "discovery_url": discovery_url,
        "granule_id": granule_id,
        "granule_url": granule_url,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "variables": {"u": "zonal total surface current", "v": "meridional total surface current"},
        "units": "m s-1",
        "stored_units": "mm s-1",
        "precision": 0.001,
        "assumed_mixed_layer_depth_m": 30,
        "display_stride": stride,
        "native_resolution_degrees": 0.25,
        "shape": [len(selected_latitudes), len(selected_longitudes)],
        "latitude_values": selected_latitudes,
        "longitude_values": selected_longitudes,
        "u_mm_s": u_values,
        "v_mm_s": v_values,
        "summary": {
            "cells": expected,
            "valid_ocean_cells": len(valid_speeds),
            "missing_or_land_cells": expected - len(valid_speeds),
            "minimum_speed_m_s": min(valid_speeds),
            "maximum_speed_m_s": max(valid_speeds),
        },
        "boundary": (
            "OSCAR is an average over an assumed well-mixed upper 30 m from a "
            "simplified physical model. This field is not full-depth velocity, "
            "a parcel trajectory, or ocean heat transport."
        ),
    }


def write_artifact(payload: dict, output: pathlib.Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    output.write_text(
        "// Generated by analysis/fetch_oscar_snapshot.py; do not edit by hand.\n"
        f"window.OSW_OSCAR={serialized};\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=DEFAULT_DATE, help="final-product day, YYYY-MM-DD")
    parser.add_argument("--stride", type=int, default=DEFAULT_STRIDE)
    parser.add_argument("--input", type=pathlib.Path, help="already retrieved OSCAR NetCDF granule")
    parser.add_argument("--retrieved-at", help="ISO provenance time; defaults to current UTC")
    parser.add_argument("--output", type=pathlib.Path)
    args = parser.parse_args()
    dt.date.fromisoformat(args.date)
    if args.stride < 1:
        parser.error("--stride must be positive")
    if args.output is None:
        args.output = pathlib.Path(f"atlas/data/oscar-currents-{args.date}.js")
    retrieved_at = args.retrieved_at or dt.datetime.now(dt.timezone.utc).replace(
        microsecond=0
    ).isoformat().replace("+00:00", "Z")
    granule_id, granule_url, discovery_url = discover_granule(args.date)
    if args.input:
        raw = args.input.read_bytes()
    else:
        token = os.environ.get("EARTHDATA_TOKEN")
        if not token:
            parser.error(
                "protected OSCAR download requires EARTHDATA_TOKEN or --input "
                "from the official PO.DAAC subscriber"
            )
        raw = fetch_bytes(granule_url, token)
    payload = package(
        raw, args.date, args.stride, retrieved_at,
        granule_id, granule_url, discovery_url,
    )
    write_artifact(payload, args.output)
    print(f"wrote {args.output} ({payload['shape'][0]} x {payload['shape'][1]} cells)")
    print(f"source sha256 {payload['source_sha256']}")


if __name__ == "__main__":
    main()

