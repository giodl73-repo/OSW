"""Package an annual-mean and directional-persistence OSCAR pilot.

The OSW persistence ratio is the magnitude of the time-mean velocity vector
divided by the mean instantaneous speed. A value near one means sampled vectors
are consistently aligned; a value near zero means directional cancellation.
It is a declared diagnostic, not a natural boundary or heat-transport metric.
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
from collections import defaultdict


DATASET_ID = "yearly_336c_0b32_9cd3"
ERDDAP = "https://oceanwatch.pifsc.noaa.gov/erddap/griddap"
INFO_URL = f"https://oceanwatch.pifsc.noaa.gov/erddap/info/{DATASET_ID}/index.html"
DEFAULT_START = "2018-01-01"
DEFAULT_STOP = "2018-11-21"
DEFAULT_TIME_STRIDE = 6
DEFAULT_SPACE_STRIDE = 16


def build_query(start: str, stop: str, time_stride: int, space_stride: int) -> str:
    dt.date.fromisoformat(start)
    dt.date.fromisoformat(stop)
    if time_stride < 1 or space_stride < 1:
        raise ValueError("strides must be positive")
    support = (
        f"[({start}):{time_stride}:({stop})][(15)]"
        f"[(80):{space_stride}:(-80)][(20):{space_stride}:(379.6666667)]"
    )
    constraint = f"u{support},v{support}"
    return f"{ERDDAP}/{DATASET_ID}.csv0?{urllib.parse.quote(constraint, safe='():,.-')}"


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "OSW/0.1 (public research atlas)"})
    with urllib.request.urlopen(request, timeout=240) as response:
        return response.read()


def package(
    raw: bytes, start: str, stop: str, time_stride: int, space_stride: int,
    retrieved_at: str, query_url: str, minimum_samples: int | None = None,
) -> dict:
    vectors: dict[tuple[float, float], list[tuple[float, float]]] = defaultdict(list)
    latitudes: list[float] = []
    longitudes: list[float] = []
    times: list[str] = []
    seen_latitudes: set[float] = set()
    seen_longitudes: set[float] = set()
    seen_times: set[str] = set()
    for row in csv.reader(io.StringIO(raw.decode("utf-8"))):
        if len(row) != 6:
            raise ValueError(f"expected six ERDDAP columns, got {len(row)}")
        time, latitude, longitude = row[0], float(row[2]), float(row[3])
        if time not in seen_times:
            seen_times.add(time)
            times.append(time)
        if latitude not in seen_latitudes:
            seen_latitudes.add(latitude)
            latitudes.append(latitude)
        if longitude not in seen_longitudes:
            seen_longitudes.add(longitude)
            longitudes.append(longitude)
        u, v = float(row[4]), float(row[5])
        if not math.isnan(u) and not math.isnan(v):
            vectors[(latitude, longitude)].append((u, v))
    if not times or not latitudes or not longitudes:
        raise ValueError("empty persistence response")
    threshold = minimum_samples if minimum_samples is not None else max(2, math.ceil(len(times) * 0.7))
    mean_u: list[int | None] = []
    mean_v: list[int | None] = []
    mean_speed: list[int | None] = []
    persistence: list[int | None] = []
    sample_count: list[int] = []
    valid_persistence: list[float] = []
    for latitude in latitudes:
        for longitude in longitudes:
            samples = vectors.get((latitude, longitude), [])
            sample_count.append(len(samples))
            if len(samples) < threshold:
                mean_u.append(None); mean_v.append(None); mean_speed.append(None); persistence.append(None)
                continue
            u_bar = sum(item[0] for item in samples) / len(samples)
            v_bar = sum(item[1] for item in samples) / len(samples)
            speed_bar = sum(math.hypot(*item) for item in samples) / len(samples)
            ratio = 0.0 if speed_bar <= 1e-12 else min(1.0, math.hypot(u_bar, v_bar) / speed_bar)
            mean_u.append(round(u_bar * 1000))
            mean_v.append(round(v_bar * 1000))
            mean_speed.append(round(speed_bar * 1000))
            persistence.append(round(ratio * 1000))
            valid_persistence.append(ratio)
    cells = len(latitudes) * len(longitudes)
    return {
        "schema": "oceanlines.oscar.persistence-pilot.v1",
        "status": "historical modeled surface-velocity persistence diagnostic",
        "source": "NOAA PIFSC ERDDAP mirror of ESR OSCAR third-degree 5-day archive",
        "dataset_id": DATASET_ID,
        "source_version": "2017.0",
        "source_info_url": INFO_URL,
        "period_start": start,
        "period_stop": stop,
        "sample_times": times,
        "time_stride": time_stride,
        "minimum_samples": threshold,
        "retrieved_at": retrieved_at,
        "query_url": query_url,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "units": "m s-1",
        "stored_velocity_units": "mm s-1",
        "stored_persistence_units": "thousandths",
        "nominal_depth_m": 15,
        "display_stride": space_stride,
        "native_resolution_degrees": 1 / 3,
        "shape": [len(latitudes), len(longitudes)],
        "latitude_values": latitudes,
        "longitude_values": longitudes,
        "mean_u_mm_s": mean_u,
        "mean_v_mm_s": mean_v,
        "mean_instantaneous_speed_mm_s": mean_speed,
        "directional_persistence_thousandths": persistence,
        "sample_count": sample_count,
        "diagnostic_definition": "magnitude(time-mean velocity) / time-mean(magnitude(velocity))",
        "summary": {
            "cells": cells,
            "valid_cells": len(valid_persistence),
            "missing_or_insufficient_cells": cells - len(valid_persistence),
            "minimum_directional_persistence": min(valid_persistence),
            "maximum_directional_persistence": max(valid_persistence),
        },
        "boundary": (
            "OSW directional persistence measures alignment among sampled historical surface vectors. "
            "It is not a fixed current boundary, Lagrangian coherence, full-depth circulation, or heat transport."
        ),
    }


def write_artifact(payload: dict, output: pathlib.Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "// Generated by analysis/fetch_oscar_persistence_pilot.py; do not edit by hand.\n"
        f"window.OSW_OSCAR_PERSISTENCE={json.dumps(payload, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8", newline="\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default=DEFAULT_START)
    parser.add_argument("--stop", default=DEFAULT_STOP)
    parser.add_argument("--time-stride", type=int, default=DEFAULT_TIME_STRIDE)
    parser.add_argument("--space-stride", type=int, default=DEFAULT_SPACE_STRIDE)
    parser.add_argument("--retrieved-at")
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("atlas/data/oscar-persistence-2018.js"))
    args = parser.parse_args()
    query_url = build_query(args.start, args.stop, args.time_stride, args.space_stride)
    retrieved_at = args.retrieved_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    payload = package(fetch(query_url), args.start, args.stop, args.time_stride, args.space_stride, retrieved_at, query_url)
    write_artifact(payload, args.output)
    print(f"wrote {args.output} ({len(payload['sample_times'])} times; {payload['shape'][0]} x {payload['shape'][1]} cells)")
    print(f"source sha256 {payload['source_sha256']}")


if __name__ == "__main__":
    main()

