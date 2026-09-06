"""Screen surface horizontal advection across the North Atlantic MHW bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "atlas" / "data" / "rtofs-mhw-bridge-north-atlantic-20260807-20260812.json"
OUTPUT = ROOT / "research" / "osw-d11-rtofs-mhw-horizontal-advection-2026.json"
EARTH_RADIUS_M = 6_371_008.8


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode(row: dict, key: str, scale: int) -> np.ndarray:
    return np.asarray([[np.nan if value is None else value / scale for value in line] for line in row[key]], dtype=float)


def planar_gradient(temperature: np.ndarray, latitude: np.ndarray, longitude: np.ndarray, mask: np.ndarray, diagonals: bool = True):
    gradient_x = np.full(temperature.shape, np.nan)
    gradient_y = np.full(temperature.shape, np.nan)
    offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if diagonals:
        offsets += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    height, width = temperature.shape
    for y, x in zip(*np.where(mask & np.isfinite(temperature))):
        design, difference = [], []
        for dy, dx in offsets:
            yy, xx = y + dy, x + dx
            if not (0 <= yy < height and 0 <= xx < width and mask[yy, xx] and np.isfinite(temperature[yy, xx])):
                continue
            east_m = EARTH_RADIUS_M * math.cos(math.radians(latitude[y, x])) * math.radians(longitude[yy, xx] - longitude[y, x])
            north_m = EARTH_RADIUS_M * math.radians(latitude[yy, xx] - latitude[y, x])
            design.append([east_m, north_m])
            difference.append(temperature[yy, xx] - temperature[y, x])
        if len(design) >= 3:
            gradient_x[y, x], gradient_y[y, x] = np.linalg.lstsq(np.asarray(design), np.asarray(difference), rcond=None)[0]
    return gradient_x, gradient_y


def advection(row: dict, latitude: np.ndarray, longitude: np.ndarray, mask: np.ndarray, diagonals: bool = True):
    temperature = decode(row, "temperature_c_milli", 1000)
    eastward = decode(row, "eastward_velocity_m_s_e4", 10_000)
    northward = decode(row, "northward_velocity_m_s_e4", 10_000)
    gradient_x, gradient_y = planar_gradient(temperature, latitude, longitude, mask, diagonals)
    return -(eastward * gradient_x + northward * gradient_y) * 86_400


def weighted_summary(values: np.ndarray, latitude: np.ndarray, valid: np.ndarray) -> dict:
    sample = values[valid]
    weights = np.cos(np.deg2rad(latitude[valid]))
    return {
        "latitude_weighted_mean_c_per_day": round(float(np.average(sample, weights=weights)), 4),
        "median_c_per_day": round(float(np.median(sample)), 4),
        "p05_c_per_day": round(float(np.percentile(sample, 5)), 4),
        "p95_c_per_day": round(float(np.percentile(sample, 95)), 4),
        "positive_cell_fraction": round(float(np.mean(sample > 0)), 4),
        "valid_cell_count": int(len(sample)),
    }


def encode_map(values: np.ndarray, valid: np.ndarray) -> list:
    return [[None if not valid[y, x] else int(round(values[y, x] * 1000)) for x in range(values.shape[1])] for y in range(values.shape[0])]


def run(source_path: Path = SOURCE) -> dict:
    source = json.loads(source_path.read_text(encoding="utf-8"))
    grid = source["grid"]
    latitude = np.asarray(grid["latitude_degrees_north_e6"], dtype=float) / 1_000_000
    longitude = np.asarray(grid["longitude_degrees_east_e6"], dtype=float) / 1_000_000
    mask = np.asarray(grid["inside_declared_box"], dtype=bool)
    rows = source["rows"]
    advection_8 = [advection(row, latitude, longitude, mask, True) for row in rows]
    advection_4 = [advection(row, latitude, longitude, mask, False) for row in rows]
    anchor_distance = (latitude - 42.125) ** 2 + ((longitude + 49.875) * math.cos(math.radians(42.125))) ** 2
    anchor_distance[~mask] = np.inf
    anchor_y, anchor_x = np.unravel_index(np.argmin(anchor_distance), anchor_distance.shape)
    intervals = []
    for index in range(len(rows) - 1):
        start, end = rows[index], rows[index + 1]
        start_temperature = decode(start, "temperature_c_milli", 1000)
        end_temperature = decode(end, "temperature_c_milli", 1000)
        observed = end_temperature - start_temperature
        horizontal = (advection_8[index] + advection_8[index + 1]) / 2
        horizontal_4 = (advection_4[index] + advection_4[index + 1]) / 2
        remainder = observed - horizontal
        valid = mask & np.isfinite(observed) & np.isfinite(horizontal)
        valid_four = valid & np.isfinite(horizontal_4)
        observed_summary = weighted_summary(observed, latitude, valid)
        advection_summary = weighted_summary(horizontal, latitude, valid)
        remainder_summary = weighted_summary(remainder, latitude, valid)
        four_mean = weighted_summary(horizontal_4, latitude, valid_four)["latitude_weighted_mean_c_per_day"]
        eight_mean = advection_summary["latitude_weighted_mean_c_per_day"]
        intervals.append({
            "start": start["date"], "end": end["date"],
            "surface_temperature_tendency": observed_summary,
            "endpoint_mean_horizontal_advection": advection_summary,
            "unresolved_remainder": remainder_summary,
            "gradient_stencil_sensitivity": {"four_neighbor_mean_c_per_day": four_mean, "eight_neighbor_mean_c_per_day": eight_mean, "difference_c_per_day": round(eight_mean - four_mean, 4)},
            "anchor": {
                "surface_temperature_tendency_c_per_day": round(float(observed[anchor_y, anchor_x]), 4),
                "endpoint_mean_horizontal_advection_c_per_day": round(float(horizontal[anchor_y, anchor_x]), 4),
                "unresolved_remainder_c_per_day": round(float(remainder[anchor_y, anchor_x]), 4),
            },
        })
        if start["date"] == "2026-08-11":
            bridge_maps = {
                "encoding": "integer thousandths degree C per day; null outside declared box",
                "surface_temperature_tendency_c_per_day_milli": encode_map(observed, valid),
                "endpoint_mean_horizontal_advection_c_per_day_milli": encode_map(horizontal, valid),
                "unresolved_remainder_c_per_day_milli": encode_map(remainder, valid),
            }
    bridge = intervals[-1]
    observed_mean = bridge["surface_temperature_tendency"]["latitude_weighted_mean_c_per_day"]
    advective_mean = bridge["endpoint_mean_horizontal_advection"]["latitude_weighted_mean_c_per_day"]
    start_mld = decode(rows[-2], "mixed_layer_thickness_m_centi", 100)
    end_mld = decode(rows[-1], "mixed_layer_thickness_m_centi", 100)
    mld_valid = mask & np.isfinite(start_mld) & np.isfinite(end_mld)
    mld_weights = np.cos(np.deg2rad(latitude[mld_valid]))
    return {
        "schema": "osw.ocean-object-rtofs-horizontal-advection-screen.v1",
        "detection_id": "OSW-D11",
        "status": "partial_model_surface_temperature_tendency_screen",
        "object_id": "OBJ046",
        "object_name": "marine heatwave",
        "source_artifact": {"path": str(source_path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(source_path)},
        "method": {
            "equation": "unresolved remainder = next-day surface temperature minus current surface temperature - endpoint-mean[-u*dT/dx - v*dT/dy] * one day",
            "gradient": "local tangent-plane least-squares fit to eight neighboring wet grid centers; four-neighbor sensitivity retained",
            "spatial_summary": "cos(latitude)-weighted mean over the fixed declared RTOFS box; diagnostic weighting, not exact native cell-area integration",
            "temporal_support": "daily 00 UTC snapshots; advection trapezoidally averaged at interval endpoints",
        },
        "anchor_grid_center": {"latitude_degrees_north": round(float(latitude[anchor_y, anchor_x]), 6), "longitude_degrees_east": round(float(longitude[anchor_y, anchor_x]), 6)},
        "intervals": intervals,
        "bridge_interval_maps": bridge_maps,
        "bridge_evaluation": {
            "result": "horizontal advection is not the dominant modeled box-mean warming term",
            "box_mean_temperature_tendency_c_per_day": observed_mean,
            "box_mean_horizontal_advection_c_per_day": advective_mean,
            "box_mean_unresolved_remainder_c_per_day": bridge["unresolved_remainder"]["latitude_weighted_mean_c_per_day"],
            "same_sign_advection_fraction_of_temperature_tendency": round(advective_mean / observed_mean, 3),
            "mixed_layer_thickness": {
                "box_mean_start_m": round(float(np.average(start_mld[mld_valid], weights=mld_weights)), 3),
                "box_mean_end_m": round(float(np.average(end_mld[mld_valid], weights=mld_weights)), 3),
                "anchor_start_m": round(float(start_mld[anchor_y, anchor_x]), 2),
                "anchor_end_m": round(float(end_mld[anchor_y, anchor_x]), 2),
                "interpretation": "diagnostic shoaling changes the surface layer exposed to forcing, but is not by itself an entrainment or heat-budget term",
            },
            "finding": "From August 11 to 12 the RTOFS fixed box warms 0.5396 C/day while endpoint-mean horizontal advection contributes 0.0708 C/day, leaving 0.4688 C/day unresolved. At the anchor the model warms 0.601 C/day while horizontal advection contributes -0.109 C/day, opposing the local warming.",
        },
        "next_evidence": "Add collocated surface radiative and turbulent fluxes; then test mixed-layer-depth scaling while retaining vertical mixing, entrainment, diffusion, assimilation increments, and numerical tendency in the remainder.",
        "boundary": "This is an offline Eulerian screen of one operational assimilative model, not its native tracer budget. Differencing surface snapshots and multiplying surface velocity by an estimated surface-temperature gradient does not close mixed-layer heat storage. The remainder combines surface forcing, vertical advection and mixing, entrainment, diffusion, assimilation increments, numerical/time-sampling error, and gradient error. Agreement or disagreement with separate SST analyses is not model validation or causal attribution.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    payload = run(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")
    print(payload["bridge_evaluation"]["finding"])


if __name__ == "__main__":
    main()
