"""Package four meteorological-season OSCAR motion diagnostics.

Each season contains mean zonal/meridional velocity, mean instantaneous speed,
and the OSW directional-persistence ratio. This is a one-year historical
seasonal pilot, not a climatology or heat-transport product.
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
DEFAULT_START = "2017-12-01"
DEFAULT_STOP = "2018-11-21"
DEFAULT_SPACE_STRIDE = 20
SEASON_ORDER = ("DJF", "MAM", "JJA", "SON")
SEASON_NAMES = {
    "DJF": "December–February", "MAM": "March–May",
    "JJA": "June–August", "SON": "September–November",
}


def season_key(timestamp: str) -> str:
    month = int(timestamp[5:7])
    if month in (12, 1, 2):
        return "DJF"
    if month in (3, 4, 5):
        return "MAM"
    if month in (6, 7, 8):
        return "JJA"
    return "SON"


def build_query(start: str, stop: str, space_stride: int) -> str:
    dt.date.fromisoformat(start)
    dt.date.fromisoformat(stop)
    if space_stride < 1:
        raise ValueError("space stride must be positive")
    support = (
        f"[({start}):1:({stop})][(15)]"
        f"[(80):{space_stride}:(-80)][(20):{space_stride}:(379.6666667)]"
    )
    constraint = f"u{support},v{support}"
    return f"{ERDDAP}/{DATASET_ID}.csv0?{urllib.parse.quote(constraint, safe='():,.-')}"


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "OSW/0.1 (public research atlas)"})
    with urllib.request.urlopen(request, timeout=300) as response:
        return response.read()


def summarize(
    vectors: dict[tuple[float, float], list[tuple[float, float]]],
    latitudes: list[float], longitudes: list[float], threshold: int,
) -> dict:
    mean_u: list[int | None] = []
    mean_v: list[int | None] = []
    mean_speed: list[int | None] = []
    persistence: list[int | None] = []
    sample_count: list[int] = []
    valid_ratios: list[float] = []
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
            mean_u.append(round(u_bar * 1000)); mean_v.append(round(v_bar * 1000))
            mean_speed.append(round(speed_bar * 1000)); persistence.append(round(ratio * 1000))
            valid_ratios.append(ratio)
    return {
        "minimum_samples": threshold,
        "mean_u_mm_s": mean_u,
        "mean_v_mm_s": mean_v,
        "mean_instantaneous_speed_mm_s": mean_speed,
        "directional_persistence_thousandths": persistence,
        "sample_count": sample_count,
        "summary": {
            "valid_cells": len(valid_ratios),
            "minimum_directional_persistence": min(valid_ratios),
            "maximum_directional_persistence": max(valid_ratios),
        },
    }


def package(raw: bytes, start: str, stop: str, space_stride: int, retrieved_at: str, query_url: str) -> dict:
    seasonal_vectors = {season: defaultdict(list) for season in SEASON_ORDER}
    seasonal_times = {season: [] for season in SEASON_ORDER}
    seasonal_seen_times = {season: set() for season in SEASON_ORDER}
    latitudes: list[float] = []
    longitudes: list[float] = []
    seen_latitudes: set[float] = set()
    seen_longitudes: set[float] = set()
    for row in csv.reader(io.StringIO(raw.decode("utf-8"))):
        if len(row) != 6:
            raise ValueError(f"expected six ERDDAP columns, got {len(row)}")
        time, latitude, longitude = row[0], float(row[2]), float(row[3])
        season = season_key(time)
        if time not in seasonal_seen_times[season]:
            seasonal_seen_times[season].add(time)
            seasonal_times[season].append(time)
        if latitude not in seen_latitudes:
            seen_latitudes.add(latitude); latitudes.append(latitude)
        if longitude not in seen_longitudes:
            seen_longitudes.add(longitude); longitudes.append(longitude)
        u, v = float(row[4]), float(row[5])
        if not math.isnan(u) and not math.isnan(v):
            seasonal_vectors[season][(latitude, longitude)].append((u, v))
    if not latitudes or not longitudes or any(not seasonal_times[season] for season in SEASON_ORDER):
        raise ValueError("incomplete seasonal OSCAR response")
    seasons = {}
    for season in SEASON_ORDER:
        threshold = max(2, math.ceil(len(seasonal_times[season]) * 0.7))
        seasons[season] = {
            "name": SEASON_NAMES[season],
            "sample_times": seasonal_times[season],
            **summarize(seasonal_vectors[season], latitudes, longitudes, threshold),
        }
    return {
        "schema": "oceanlines.oscar.seasonal-pilot.v1",
        "status": "historical one-year seasonal surface-velocity diagnostic",
        "source": "NOAA PIFSC ERDDAP mirror of ESR OSCAR third-degree 5-day archive",
        "dataset_id": DATASET_ID,
        "source_version": "2017.0",
        "source_info_url": INFO_URL,
        "period_start": start,
        "period_stop": stop,
        "retrieved_at": retrieved_at,
        "query_url": query_url,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "units": "m s-1",
        "nominal_depth_m": 15,
        "display_stride": space_stride,
        "native_resolution_degrees": 1 / 3,
        "shape": [len(latitudes), len(longitudes)],
        "latitude_values": latitudes,
        "longitude_values": longitudes,
        "season_order": list(SEASON_ORDER),
        "seasons": seasons,
        "diagnostic_definition": "seasonal magnitude(mean velocity) / seasonal mean(magnitude(velocity))",
        "boundary": (
            "One historical meteorological year from an older OSCAR product. Seasonal means and "
            "directional persistence are not a climatology, natural boundary, Lagrangian coherence, "
            "full-depth circulation, or heat transport."
        ),
    }


def write_artifact(payload: dict, output: pathlib.Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "// Generated by analysis/fetch_oscar_seasonal_pilot.py; do not edit by hand.\n"
        f"window.OSW_OSCAR_SEASONS={json.dumps(payload, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8", newline="\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default=DEFAULT_START)
    parser.add_argument("--stop", default=DEFAULT_STOP)
    parser.add_argument("--space-stride", type=int, default=DEFAULT_SPACE_STRIDE)
    parser.add_argument("--retrieved-at")
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("atlas/data/oscar-seasons-2018.js"))
    args = parser.parse_args()
    query_url = build_query(args.start, args.stop, args.space_stride)
    retrieved_at = args.retrieved_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    payload = package(fetch(query_url), args.start, args.stop, args.space_stride, retrieved_at, query_url)
    write_artifact(payload, args.output)
    counts = ", ".join(f"{season}={len(payload['seasons'][season]['sample_times'])}" for season in SEASON_ORDER)
    print(f"wrote {args.output} ({counts}; {payload['shape'][0]} x {payload['shape'][1]} cells)")
    print(f"source sha256 {payload['source_sha256']}")


if __name__ == "__main__":
    main()

