"""Audit seed and date dependence of the partial Gulf Stream diagnostic.

Research-only receipt: it does not establish a stable current axis or enter
the release candidate's whole-current length ranking.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pyproj import Geod

from build_gulf_stream_geostrophic_path import (SEED_GATE_LON, SEED_LAT_MAX,
                                                SEED_LAT_MIN, load_field,
                                                sample_velocity, trace)
from fetch_noaa_lsa_geostrophic_repeat import DATES, EXPECTED_SHA256, receipt_path


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "research" / "noaa-lsa-geostrophic-gulf-stream-20260925.json"
OUTPUT = ROOT / "research" / "gulf-stream-geostrophic-repeat-20260918-20260927.json"
BASELINE_SHA256 = "53b1c541d4edf529bba2358f255890e2f0c392ef8e57208d04882c732c99f12f"
SUBSET_SHA256 = {
    "2026-09-18": "16d1702b16043376f354367914f83dcfd68c72963d45573248bf5e542849656a",
    "2026-09-24": "6e023c7a2e81198953bb01539652e7f51e07238c442e3a44ed1d2c2e59035064",
    "2026-09-25": "dca73ae0a47ec34e2f81920828a7fd5ecd6b69c11a7562f48013f2dca7f60318",
    "2026-09-26": "b6b6f75742ce0c74011c2b3edec0b97aca2e8817886cda438347d770d4733cca",
    "2026-09-27": "e58d303bc28df7eb9b695c2678c2c1f8b9bf85d953255e09c72a6fffbdc08490",
}
LONGITUDE_CHECKPOINTS = (-70.0, -65.0, -60.0, -55.0, -50.0)
GEOD = Geod(ellps="WGS84")


def first_eastward_crossing_latitude(coordinates: list[list[float]], longitude: float) -> float | None:
    for (lon0, lat0), (lon1, lat1) in zip(coordinates, coordinates[1:]):
        if lon0 <= longitude <= lon1 and lon1 > lon0:
            return round(lat0 + (longitude - lon0) * (lat1 - lat0) / (lon1 - lon0), 4)
    return None


def analyze_date(path: Path, expected_sha256: str) -> dict:
    source_bytes = path.read_bytes()
    source = json.loads(source_bytes)
    date = source["source_time_start"][:10]
    if hashlib.sha256(source_bytes).hexdigest() != SUBSET_SHA256[date]:
        raise ValueError(f"Unexpected pinned subset bytes in {path}")
    if source["source_response_sha256"] != expected_sha256:
        raise ValueError(f"Unexpected NOAA source digest in {path}")
    if source["subset_shape"] != [60, 140] or source["grid_step_degrees"] != [0.25, 0.25]:
        raise ValueError(f"Unexpected NOAA grid in {path}")
    fields = load_field(source)
    origin_lat = source["grid_origin_lon_lat"][1]
    lat_step = source["grid_step_degrees"][1]
    gate_lats = [round(origin_lat + i * lat_step, 6)
                 for i in range(source["subset_shape"][0])
                 if SEED_LAT_MIN <= origin_lat + i * lat_step <= SEED_LAT_MAX]
    gate_velocity = {lat: sample_velocity(source, fields, SEED_GATE_LON, lat) for lat in gate_lats}
    if not gate_velocity or any(value is None for value in gate_velocity.values()):
        raise ValueError(f"Missing velocity at seed gate in {path}")
    selected_lat = max(gate_lats, key=lambda lat: gate_velocity[lat][0])
    sample_lats = sorted(set((selected_lat - 0.25, selected_lat, selected_lat + 0.25, 36.875)))
    traces = []
    for lat in sample_lats:
        result = trace(source, fields, lat, 10)
        coordinates = result["coordinates_lon_lat"]
        westward_segments = [(a, b) for a, b in zip(coordinates, coordinates[1:]) if b[0] < a[0]]
        traces.append({
            "seed_latitude": lat,
            "seed_role": [role for role, value in (("daily_maximum_eastward", selected_lat),
                                                   ("fixed_baseline", 36.875),
                                                   ("south_adjacent", selected_lat - 0.25),
                                                   ("north_adjacent", selected_lat + 0.25)) if lat == value],
            "stop_reason": result["stop_reason"],
            "partial_length_km": result["segment_length_km"],
            "last_lon_lat": result["last_lon_lat"],
            "point_count": result["point_count"],
            "westward_step_count": len(westward_segments),
            "westward_segment_distance_km": round(sum(GEOD.inv(*a, *b)[2] for a, b in westward_segments) / 1000, 1),
            "maximum_latitude": round(max(point[1] for point in coordinates), 4),
            "first_eastward_crossing_latitudes": {
                str(lon): first_eastward_crossing_latitude(result["coordinates_lon_lat"], lon)
                for lon in LONGITUDE_CHECKPOINTS
            },
        })
    return {
        "date": source["source_time_start"][:10],
        "source_subset": str(path.relative_to(ROOT)).replace("\\", "/"),
        "source_subset_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "source_url": source["source_url"],
        "source_response_sha256": expected_sha256,
        "selected_seed_latitude": selected_lat,
        "gate_eastward_velocity_m_s": {str(lat): round(gate_velocity[lat][0], 4) for lat in gate_lats},
        "traces": traces,
    }


def build() -> dict:
    dates = sorted([(date, receipt_path(date), EXPECTED_SHA256[date]) for date in DATES]
                   + [("2026-09-25", BASELINE, BASELINE_SHA256)])
    observations = [analyze_date(path, expected) for _, path, expected in dates]
    selected = [next(row for row in item["traces"] if "daily_maximum_eastward" in row["seed_role"])
                for item in observations]
    fixed = [next(row for row in item["traces"] if "fixed_baseline" in row["seed_role"])
             for item in observations]
    adjacent = [row for item in observations for row in item["traces"]
                if "south_adjacent" in row["seed_role"] or "north_adjacent" in row["seed_role"]]
    def count_gate(rows: list[dict]) -> int:
        return sum(row["stop_reason"] == "downstream_longitude_gate" for row in rows)
    return {
        "schema": "osw.almanac.gulf-stream-geostrophic-repeat-audit.v1",
        "status": "research_only_not_released_or_ranked",
        "dates": [date for date, _, _ in dates],
        "field": "NOAA LSA daily 0.25-degree altimetry-derived absolute surface geostrophic velocity",
        "method": "Same frozen-time WGS84 midpoint integration, 10 km steps, 0.15 m/s minimum speed, -72.875-degree seed gate, and -50-degree downstream gate as the 2026-09-25 candidate trace.",
        "limitations": "Five chosen dates and nearby seeds do not determine a stable route, current width, whole-current length, parcel trajectory, or permanent OSW state passage. Geostrophic velocity omits ageostrophic and depth structure; positional uncertainty is not quantified.",
        "observations": observations,
        "summary": {
            "date_count": len(observations),
            "daily_selected_seeds_reaching_downstream_gate": count_gate(selected),
            "fixed_baseline_seeds_reaching_downstream_gate": count_gate(fixed),
            "adjacent_seeds_reaching_downstream_gate": count_gate(adjacent),
            "adjacent_seed_trace_count": len(adjacent),
            "daily_selected_seed_partial_lengths_km": [row["partial_length_km"] for row in selected],
            "fixed_baseline_seed_partial_lengths_km": [row["partial_length_km"] for row in fixed],
            "selected_seed_downstream_latitude_range": [min(row["last_lon_lat"][1] for row in selected if row["stop_reason"] == "downstream_longitude_gate"),
                                                         max(row["last_lon_lat"][1] for row in selected if row["stop_reason"] == "downstream_longitude_gate")],
        },
    }


if __name__ == "__main__":
    result = build()
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"]))
