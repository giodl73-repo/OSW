"""Build a dated, partial Gulf Stream streamline from pinned NOAA LSA velocity."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
from pyproj import Geod
from shapely.geometry import LineString

from build_cartographic_current_state_join import load_states, project
from build_gulf_stream_navo_state_snapshot import geographic_line_length_km


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research" / "noaa-lsa-geostrophic-gulf-stream-20260925.json"
OUTPUT = ROOT / "research" / "gulf-stream-geostrophic-path-20260925.json"
GEOD = Geod(ellps="WGS84")
SEED_GATE_LON = -72.875
SEED_LAT_MIN, SEED_LAT_MAX = 36.5, 37.0
DOWNSTREAM_GATE_LON = -50.0
MIN_SPEED_M_S = 0.15
MAX_DISTANCE_KM = 4000


def load_field(source: dict):
    height, width = source["subset_shape"]
    scale = source["velocity_scale_m_s_per_raw_unit"]
    missing = source["raw_fill_value"]
    fields = {}
    for name in ("ugos", "vgos"):
        raw = np.asarray(source["velocity_fields_raw_int32"][name], dtype=np.int32)
        if raw.shape != (height, width):
            raise ValueError(f"Wrong source subset shape: {name}")
        values = raw.astype(float) * scale
        values[raw == missing] = np.nan
        fields[name] = values
    return fields


def sample_velocity(source: dict, fields: dict, lon: float, lat: float) -> tuple[float, float] | None:
    origin_lon, origin_lat = source["grid_origin_lon_lat"]
    lon_step, lat_step = source["grid_step_degrees"]
    fi = (lat - origin_lat) / lat_step
    fj = (lon - origin_lon) / lon_step
    i, j = math.floor(fi), math.floor(fj)
    if i < 0 or j < 0 or i + 1 >= fields["ugos"].shape[0] or j + 1 >= fields["ugos"].shape[1]:
        return None
    latitude_weight, longitude_weight = fi - i, fj - j

    def interpolate(field: np.ndarray) -> float | None:
        values = (field[i, j], field[i + 1, j], field[i, j + 1], field[i + 1, j + 1])
        if not all(math.isfinite(value) for value in values):
            return None
        return float((1 - latitude_weight) * (1 - longitude_weight) * values[0]
                     + latitude_weight * (1 - longitude_weight) * values[1]
                     + (1 - latitude_weight) * longitude_weight * values[2]
                     + latitude_weight * longitude_weight * values[3])

    eastward = interpolate(fields["ugos"])
    northward = interpolate(fields["vgos"])
    return (eastward, northward) if eastward is not None and northward is not None else None


def trace(source: dict, fields: dict, seed_lat: float, step_km: float) -> dict:
    if not math.isfinite(step_km) or step_km <= 0 or not math.isfinite(seed_lat) or not -90 < seed_lat < 90:
        raise ValueError("Invalid trace step or seed")
    lon, lat = SEED_GATE_LON, seed_lat
    coordinates = [[lon, lat]]
    speed_samples = []
    distance_km = 0.0
    stop_reason = "distance_cap"
    for _ in range(math.ceil(MAX_DISTANCE_KM / step_km) + 1):
        remaining_km = MAX_DISTANCE_KM - distance_km
        if remaining_km < 1e-6:
            break
        actual_step_km = min(step_km, remaining_km)
        velocity = sample_velocity(source, fields, lon, lat)
        if velocity is None:
            stop_reason = "missing_grid_velocity"
            break
        eastward, northward = velocity
        speed = math.hypot(eastward, northward)
        if speed < MIN_SPEED_M_S:
            stop_reason = "speed_below_threshold"
            break
        bearing = math.degrees(math.atan2(eastward, northward))
        midpoint_lon, midpoint_lat, _ = GEOD.fwd(lon, lat, bearing, actual_step_km * 500)
        midpoint_velocity = sample_velocity(source, fields, midpoint_lon, midpoint_lat)
        if midpoint_velocity is None:
            stop_reason = "missing_midpoint_velocity"
            break
        midpoint_speed = math.hypot(*midpoint_velocity)
        if midpoint_speed < MIN_SPEED_M_S:
            stop_reason = "midpoint_speed_below_threshold"
            break
        midpoint_bearing = math.degrees(math.atan2(*midpoint_velocity))
        next_lon, next_lat, _ = GEOD.fwd(lon, lat, midpoint_bearing, actual_step_km * 1000)
        if next_lon >= DOWNSTREAM_GATE_LON:
            fraction = (DOWNSTREAM_GATE_LON - lon) / (next_lon - lon)
            next_lon, next_lat = DOWNSTREAM_GATE_LON, lat + fraction * (next_lat - lat)
            segment_km = GEOD.inv(lon, lat, next_lon, next_lat)[2] / 1000
            stop_reason = "downstream_longitude_gate"
        else:
            segment_km = GEOD.inv(lon, lat, next_lon, next_lat)[2] / 1000
        coordinates.append([round(next_lon, 6), round(next_lat, 6)])
        speed_samples.append(speed)
        distance_km += segment_km
        lon, lat = next_lon, next_lat
        if stop_reason == "downstream_longitude_gate":
            break
    return {
        "seed_lon_lat": [SEED_GATE_LON, seed_lat],
        "step_km": step_km,
        "stop_reason": stop_reason,
        "segment_length_km": round(distance_km, 1),
        "last_lon_lat": coordinates[-1],
        "minimum_sampled_speed_m_s": round(min(speed_samples), 3) if speed_samples else None,
        "point_count": len(coordinates),
        "coordinates_lon_lat": coordinates,
    }


def build() -> dict:
    source_bytes = SOURCE.read_bytes()
    source = json.loads(source_bytes)
    if source["source_response_sha256"] != "53b1c541d4edf529bba2358f255890e2f0c392ef8e57208d04882c732c99f12f":
        raise ValueError("Unexpected NOAA source file")
    fields = load_field(source)
    origin_lat = source["grid_origin_lon_lat"][1]
    lat_step = source["grid_step_degrees"][1]
    candidate_lats = [round(origin_lat + i * lat_step, 6)
                      for i in range(source["subset_shape"][0])
                      if SEED_LAT_MIN <= origin_lat + i * lat_step <= SEED_LAT_MAX]
    candidates = [(lat, sample_velocity(source, fields, SEED_GATE_LON, lat)) for lat in candidate_lats]
    if not candidates or any(value is None for _, value in candidates):
        raise ValueError("Seed gate has missing velocity")
    seed_lat, _ = max(candidates, key=lambda item: item[1][0])
    representative = trace(source, fields, seed_lat, 10)
    if representative["stop_reason"] != "downstream_longitude_gate":
        raise ValueError(f"Representative trace did not reach the downstream gate: {representative['stop_reason']}")
    sensitivities = [trace(source, fields, seed_lat + delta, 10) for delta in (-0.25, 0.25)]
    step_sensitivities = [trace(source, fields, seed_lat, step) for step in (5, 20)]
    line = LineString([project(*point) for point in representative["coordinates_lon_lat"]])
    state_relations = []
    for code, shape in sorted(load_states().items()):
        intersection = line.intersection(shape)
        if intersection.length <= 0:
            continue
        state_relations.append({
            "state_code": code,
            "predicate": "dated_geostrophic_streamline_segment_intersection",
            "intersection_length_km": round(geographic_line_length_km(intersection), 1),
        })
    return {
        "schema": "osw.almanac.gulf-stream-geostrophic-streamline.v1",
        "current_id": "gulf-stream-system",
        "observation_date": "2026-09-25",
        "source_subset": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_subset_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "source_url": source["source_url"],
        "source_response_sha256": source["source_response_sha256"],
        "product_page": source["product_page"],
        "field": "altimetry_derived_absolute_surface_geostrophic_velocity",
        "seed_gate": {"longitude": SEED_GATE_LON, "latitude_min": SEED_LAT_MIN,
                      "latitude_max": SEED_LAT_MAX,
                      "selection": "maximum eastward velocity among the two 0.25-degree grid centers in the declared gate"},
        "downstream_gate_longitude": DOWNSTREAM_GATE_LON,
        "minimum_speed_m_s": MIN_SPEED_M_S,
        "integration_method": "Frozen-time WGS84 geodesic midpoint integration; bilinear wet-cell interpolation of eastward and northward velocity; first downstream gate crossing or declared stop.",
        "representative": representative,
        "adjacent_seed_sensitivity": [{key: value for key, value in row.items() if key != "coordinates_lon_lat"}
                                      for row in sensitivities],
        "step_size_sensitivity": [{key: value for key, value in row.items() if key != "coordinates_lon_lat"}
                                  for row in step_sensitivities],
        "state_relations": state_relations,
        "length_role": "partial_dated_geostrophic_streamline_reach_not_whole_current_length",
        "physical_limit": "A 0.25-degree daily altimetry-derived surface geostrophic field omits ageostrophic and depth structure. Seed choice and numerical step change the trace. The line is a one-day frozen-field diagnostic, not a measured current axis, parcel trajectory, permanent state passage, or whole Gulf Stream length.",
    }


def main() -> None:
    output = build()
    OUTPUT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(output["representative"]["segment_length_km"], output["representative"]["stop_reason"],
          output["state_relations"])


if __name__ == "__main__":
    main()
