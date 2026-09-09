"""Measure fixed-depth upper-ocean storage across the North Atlantic MHW bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "atlas" / "data" / "rtofs-mhw-upper-ocean-north-atlantic-20260807-20260812.json"
D12 = ROOT / "research" / "osw-d12-gfs-surface-flux-screen-2026.json"
OUTPUT = ROOT / "research" / "osw-d13-rtofs-mhw-upper-ocean-storage-2026.json"
RHO_KG_M3 = 1025.0
CP_J_KG_K = 3990.0
SECONDS_PER_DAY = 86_400.0
COLUMN_LIMITS_M = (10, 20, 30, 50)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode(row: dict) -> np.ndarray:
    return np.asarray([[[np.nan if value is None else value / 1000 for value in line] for line in layer]
                       for layer in row["potential_temperature_c_milli_by_depth"]], dtype=float)


def weighted_summary(values: np.ndarray, latitude: np.ndarray, valid: np.ndarray, digits: int = 4) -> dict:
    sample = values[valid]
    weights = np.cos(np.deg2rad(latitude[valid]))
    return {
        "latitude_weighted_mean": round(float(np.average(sample, weights=weights)), digits),
        "median": round(float(np.median(sample)), digits),
        "p05": round(float(np.percentile(sample, 5)), digits),
        "p95": round(float(np.percentile(sample, 95)), digits),
        "positive_cell_fraction": round(float(np.mean(sample > 0)), 4),
        "valid_cell_count": int(len(sample)),
    }


def encode_map(values: np.ndarray, valid: np.ndarray, scale: int) -> list:
    return [[None if not valid[y, x] else int(round(values[y, x] * scale)) for x in range(values.shape[1])] for y in range(values.shape[0])]


def run(source_path: Path = SOURCE, d12_path: Path = D12) -> dict:
    source = json.loads(source_path.read_text(encoding="utf-8"))
    d12 = json.loads(d12_path.read_text(encoding="utf-8"))
    depth = np.asarray(source["vertical_support"]["standard_depths_m"], dtype=float)
    latitude = np.asarray(source["grid"]["latitude_degrees_north_e6"], dtype=float) / 1_000_000
    longitude = np.asarray(source["grid"]["longitude_degrees_east_e6"], dtype=float) / 1_000_000
    mask = np.asarray(source["grid"]["inside_declared_box"], dtype=bool)
    states = [decode(row) for row in source["rows"]]
    anchor_distance = ((latitude - 42.125) ** 2 +
                       ((longitude + 49.875) * math.cos(math.radians(42.125))) ** 2)
    anchor_distance[~mask] = np.inf
    anchor_y, anchor_x = np.unravel_index(np.argmin(anchor_distance), anchor_distance.shape)
    intervals, bridge_maps = [], None
    for index in range(len(states) - 1):
        start, end = source["rows"][index]["date"], source["rows"][index + 1]["date"]
        if d12["intervals"][index]["start"] != start or d12["intervals"][index]["end"] != end:
            raise ValueError("RTOFS storage and D12 forcing intervals do not align")
        change = states[index + 1] - states[index]
        valid = mask & np.all(np.isfinite(change), axis=0)
        depth_profile = [round(float(np.average(change[level][valid], weights=np.cos(np.deg2rad(latitude[valid])))), 4) for level in range(len(depth))]
        columns = {}
        maps = {}
        for limit in COLUMN_LIMITS_M:
            levels = depth <= limit
            integrated_change = np.trapezoid(change[levels], depth[levels], axis=0)
            mean_change = integrated_change / limit
            storage = integrated_change * RHO_KG_M3 * CP_J_KG_K / SECONDS_PER_DAY
            columns[f"zero_to_{limit}_m"] = {
                "column_mean_temperature_change_c": weighted_summary(mean_change, latitude, valid),
                "storage_tendency_w_m2": weighted_summary(storage, latitude, valid, 2),
                "anchor_column_mean_temperature_change_c": round(float(mean_change[anchor_y, anchor_x]), 4),
                "anchor_storage_tendency_w_m2": round(float(storage[anchor_y, anchor_x]), 2),
            }
            maps[limit] = (mean_change, storage)
        surface_change = change[0]
        column_50 = maps[50][0]
        surface_intensification = surface_change - column_50
        gfs_flux = d12["intervals"][index]["gfs_net_downward_surface_flux_w_m2"]["latitude_weighted_mean"]
        storage_50 = columns["zero_to_50_m"]["storage_tendency_w_m2"]["latitude_weighted_mean"]
        intervals.append({
            "start": start,
            "end": end,
            "box_mean_temperature_change_by_standard_depth_c": {str(int(z)): value for z, value in zip(depth, depth_profile)},
            "surface_temperature_change_c": weighted_summary(surface_change, latitude, valid),
            "fixed_columns": columns,
            "surface_minus_0_50_m_column_mean_change_c": weighted_summary(surface_intensification, latitude, valid),
            "cross_system_surface_flux_comparison": {
                "gfs_net_downward_surface_flux_w_m2": gfs_flux,
                "rtofs_0_50_m_storage_tendency_w_m2": storage_50,
                "surface_flux_fraction_of_same_sign_storage": round(gfs_flux / storage_50, 3) if gfs_flux * storage_50 > 0 else None,
                "storage_minus_surface_flux_w_m2": round(storage_50 - gfs_flux, 2),
            },
        })
        if start == "2026-08-11":
            bridge_maps = {
                "grid": "RTOFS subset grid from source artifact",
                "surface_temperature_change_c_milli": encode_map(surface_change, valid, 1000),
                "zero_to_50_m_column_mean_temperature_change_c_milli": encode_map(column_50, valid, 1000),
                "surface_minus_column_mean_change_c_milli": encode_map(surface_intensification, valid, 1000),
            }
    bridge = intervals[-1]
    comparison = bridge["cross_system_surface_flux_comparison"]
    column = bridge["fixed_columns"]["zero_to_50_m"]
    surface_mean = bridge["surface_temperature_change_c"]["latitude_weighted_mean"]
    column_mean = column["column_mean_temperature_change_c"]["latitude_weighted_mean"]
    return {
        "schema": "osw.ocean-object-rtofs-upper-ocean-storage-screen.v1",
        "detection_id": "OSW-D13",
        "status": "fixed_depth_upper_ocean_storage_screen",
        "object_id": "OBJ046",
        "object_name": "marine heatwave",
        "source_artifacts": [
            {"path": str(source_path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(source_path), "role": "operational assimilative upper-ocean temperature"},
            {"path": str(d12_path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(d12_path), "role": "cross-system forecast-derived surface-flux comparison"},
        ],
        "method": {
            "storage_equation": "fixed-column storage tendency = rho * cp * trapezoidal integral from 0 to H of [temperature(next day) - temperature(current day)] dz / 86400",
            "constants": {"representative_seawater_density_kg_m3": RHO_KG_M3, "representative_seawater_heat_capacity_j_kg_k": CP_J_KG_K},
            "fixed_column_limits_m": list(COLUMN_LIMITS_M),
            "vertical_sampling": "15 RTOFS standard-depth potential-temperature samples from 0 through 50 m; exact samples exist at every reported column limit",
            "spatial_summary": "cos(latitude)-weighted grid-center means over 4,221 fixed-box cells; not exact native cell-area integration",
            "reference_note": "a constant temperature reference cancels in fixed-depth day-to-day storage differences under constant rho and cp",
        },
        "anchor_grid_center": {"latitude_degrees_north": round(float(latitude[anchor_y, anchor_x]), 6), "longitude_degrees_east": round(float(longitude[anchor_y, anchor_x]), 6)},
        "intervals": intervals,
        "bridge_interval_maps": bridge_maps,
        "bridge_evaluation": {
            "result": "surface intensification accompanies genuine fixed-column heat gain",
            "box_surface_temperature_change_c": surface_mean,
            "box_zero_to_50_m_column_mean_temperature_change_c": column_mean,
            "surface_to_column_mean_change_ratio": round(surface_mean / column_mean, 3),
            "box_zero_to_50_m_storage_tendency_w_m2": comparison["rtofs_0_50_m_storage_tendency_w_m2"],
            "gfs_net_downward_surface_flux_w_m2": comparison["gfs_net_downward_surface_flux_w_m2"],
            "gfs_surface_flux_fraction_of_rtofs_storage_scale": comparison["surface_flux_fraction_of_same_sign_storage"],
            "box_storage_minus_surface_flux_scale_w_m2": comparison["storage_minus_surface_flux_w_m2"],
            "anchor_zero_to_50_m_column_mean_temperature_change_c": column["anchor_column_mean_temperature_change_c"],
            "anchor_zero_to_50_m_storage_tendency_w_m2": column["anchor_storage_tendency_w_m2"],
            "finding": "The box surface warms much faster than its fixed 0-50 m column mean, but the column still gains heat. GFS surface gain is about half the box-scale RTOFS storage tendency; the much larger anchor storage change cannot be supplied by local surface flux alone.",
        },
        "next_evidence": "Add 0-50 m RTOFS horizontal-advection convergence and sensitivity to deeper fixed columns, then separate vertical boundary exchange, mixing, shortwave penetration, and assimilation increments where native diagnostics permit.",
        "boundary": "This is fixed-depth storage from standard-depth-interpolated potential temperature with constant representative rho and cp, not native-layer ocean heat content. The GFS comparison crosses operational systems and cannot be subtracted as a native closure. Spatial extremes may reflect fronts, advection, interpolation, analysis increments, or other model processes. Surface intensification does not by itself diagnose mixed-layer shoaling, vertical mixing, entrainment, or causation.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--d12", type=Path, default=D12)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    payload = run(args.source, args.d12)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")
    print(json.dumps(payload["bridge_evaluation"], indent=2))


if __name__ == "__main__":
    main()
