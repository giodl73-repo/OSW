"""Package time-resolved OSCAR fields for a historical M2 pathway pilot.

This artifact preserves the individual velocity snapshots used by the existing
seasonal pilot.  It is a solver input, not a trajectory, current boundary, or
heat-transport product.
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


DATASET_ID = "yearly_336c_0b32_9cd3"
ERDDAP = "https://oceanwatch.pifsc.noaa.gov/erddap/griddap"
INFO_URL = f"https://oceanwatch.pifsc.noaa.gov/erddap/info/{DATASET_ID}/index.html"
DEFAULT_START = "2017-12-01"
DEFAULT_STOP = "2018-11-21"
DEFAULT_SPACE_STRIDE = 20
DEFAULT_NORTH = 80.0
DEFAULT_SOUTH = -80.0
DEFAULT_WEST = 20.0
DEFAULT_EAST = 379.6666667


def build_query(
    start: str, stop: str, space_stride: int,
    north: float = DEFAULT_NORTH, south: float = DEFAULT_SOUTH,
    west: float = DEFAULT_WEST, east: float = DEFAULT_EAST,
) -> str:
    dt.date.fromisoformat(start)
    dt.date.fromisoformat(stop)
    if space_stride < 1:
        raise ValueError("space stride must be positive")
    if north <= south or east <= west:
        raise ValueError("expected north > south and east > west")
    def coordinate(value: float) -> str:
        return f"{value:.10f}".rstrip("0").rstrip(".")
    support = (
        f"[({start}):1:({stop})][(15)]"
        f"[({coordinate(north)}):{space_stride}:({coordinate(south)})]"
        f"[({coordinate(west)}):{space_stride}:({coordinate(east)})]"
    )
    constraint = f"u{support},v{support}"
    return f"{ERDDAP}/{DATASET_ID}.csv0?{urllib.parse.quote(constraint, safe='():,.-')}"


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "OSW/0.1 (public research atlas)"})
    with urllib.request.urlopen(request, timeout=300) as response:
        return response.read()


def parse_timestamp(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def package(raw: bytes, start: str, stop: str, space_stride: int, retrieved_at: str, query_url: str) -> dict:
    values: dict[tuple[str, float, float], tuple[float, float]] = {}
    times: set[str] = set()
    latitudes: set[float] = set()
    longitudes: set[float] = set()

    for row in csv.reader(io.StringIO(raw.decode("utf-8"))):
        if len(row) != 6:
            raise ValueError(f"expected six ERDDAP columns, got {len(row)}")
        time, latitude, longitude = row[0], float(row[2]), float(row[3])
        parse_timestamp(time)
        key = (time, latitude, longitude)
        if key in values:
            raise ValueError(f"duplicate OSCAR grid cell: {key}")
        values[key] = (float(row[4]), float(row[5]))
        times.add(time); latitudes.add(latitude); longitudes.add(longitude)

    ordered_times = sorted(times, key=parse_timestamp)
    ordered_latitudes = sorted(latitudes, reverse=True)
    ordered_longitudes = sorted(longitudes)
    if len(ordered_times) < 2 or not ordered_latitudes or not ordered_longitudes:
        raise ValueError("incomplete time-resolved OSCAR response")

    expected_rows = len(ordered_times) * len(ordered_latitudes) * len(ordered_longitudes)
    if len(values) != expected_rows:
        raise ValueError(f"incomplete OSCAR grid: expected {expected_rows} rows, got {len(values)}")

    cadence_days = [
        (parse_timestamp(b) - parse_timestamp(a)).total_seconds() / 86400
        for a, b in zip(ordered_times, ordered_times[1:])
    ]
    if min(cadence_days) < 4.5 or max(cadence_days) > 6.5:
        raise ValueError(f"unexpected OSCAR cadence: {min(cadence_days)} to {max(cadence_days)} days")

    frames = []
    for time in ordered_times:
        u_values: list[int | None] = []
        v_values: list[int | None] = []
        valid_cells = 0
        for latitude in ordered_latitudes:
            for longitude in ordered_longitudes:
                u, v = values[(time, latitude, longitude)]
                if math.isfinite(u) and math.isfinite(v):
                    u_values.append(round(u * 1000)); v_values.append(round(v * 1000))
                    valid_cells += 1
                else:
                    u_values.append(None); v_values.append(None)
        frames.append({
            "time": time,
            "valid_cells": valid_cells,
            "u_mm_s": u_values,
            "v_mm_s": v_values,
        })

    encoded_fields = json.dumps(frames, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return {
        "schema": "oceanlines.oscar.historical-timeseries.v1",
        "status": "historical one-year time-varying surface-velocity solver input",
        "source": "NOAA PIFSC ERDDAP mirror of ESR OSCAR third-degree 5-day archive",
        "dataset_id": DATASET_ID,
        "source_version": "2017.0",
        "source_info_url": INFO_URL,
        "period_start": start,
        "period_stop": stop,
        "retrieved_at": retrieved_at,
        "query_url": query_url,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "field_sha256": hashlib.sha256(encoded_fields).hexdigest(),
        "source_units": "m s-1",
        "stored_velocity_units": "mm s-1",
        "velocity_quantization_mm_s": 1,
        "nominal_depth_m": 15,
        "nominal_cadence_days": 5,
        "observed_cadence_days": {"minimum": min(cadence_days), "maximum": max(cadence_days)},
        "display_stride": space_stride,
        "native_resolution_degrees": 1 / 3,
        "shape": [len(ordered_times), len(ordered_latitudes), len(ordered_longitudes)],
        "flattening_order": "latitude-major within each frame; latitude north-to-south; longitude ascending",
        "latitude_values": ordered_latitudes,
        "longitude_values": ordered_longitudes,
        "sampled_extent": {
            "north": max(ordered_latitudes), "south": min(ordered_latitudes),
            "west": min(ordered_longitudes), "east": max(ordered_longitudes),
        },
        "joint_mask_definition": "u and v are both finite; null is missing or land and never means zero velocity",
        "frames": frames,
        "boundary": (
            "Time-varying solver input from one historical year of an older, coarse-sampled OSCAR "
            "surface product. It is not a trajectory, climatology, Lagrangian coherent structure, "
            "full-depth circulation, region boundary, parcel heat content, or heat transport."
        ),
    }


def write_artifact(payload: dict, output: pathlib.Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "// Generated by analysis/fetch_oscar_timeseries_pilot.py; do not edit by hand.\n"
        f"window.OSW_OSCAR_TIMESERIES={json.dumps(payload, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8", newline="\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default=DEFAULT_START)
    parser.add_argument("--stop", default=DEFAULT_STOP)
    parser.add_argument("--space-stride", type=int, default=DEFAULT_SPACE_STRIDE)
    parser.add_argument("--north", type=float, default=DEFAULT_NORTH)
    parser.add_argument("--south", type=float, default=DEFAULT_SOUTH)
    parser.add_argument("--west", type=float, default=DEFAULT_WEST)
    parser.add_argument("--east", type=float, default=DEFAULT_EAST)
    parser.add_argument("--retrieved-at")
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("atlas/data/oscar-timeseries-2018.js"))
    args = parser.parse_args()
    query_url = build_query(
        args.start, args.stop, args.space_stride,
        args.north, args.south, args.west, args.east,
    )
    retrieved_at = args.retrieved_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    payload = package(fetch(query_url), args.start, args.stop, args.space_stride, retrieved_at, query_url)
    write_artifact(payload, args.output)
    print(f"wrote {args.output} ({payload['shape'][0]} x {payload['shape'][1]} x {payload['shape'][2]})")
    print(f"source sha256 {payload['source_sha256']}")
    print(f"field sha256 {payload['field_sha256']}")


if __name__ == "__main__":
    main()
