"""Integrate offline RTOFS horizontal temperature advection through 50 m."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from analyze_rtofs_mhw_advection import planar_gradient


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "atlas" / "data" / "rtofs-mhw-upper-ocean-north-atlantic-20260807-20260812.json"
D12 = ROOT / "research" / "osw-d12-gfs-surface-flux-screen-2026.json"
D13 = ROOT / "research" / "osw-d13-rtofs-mhw-upper-ocean-storage-2026.json"
OUTPUT = ROOT / "research" / "osw-d14-rtofs-mhw-upper-ocean-advection-2026.json"
RHO_KG_M3 = 1025.0
CP_J_KG_K = 3990.0
SECONDS_PER_DAY = 86_400.0
COLUMN_LIMITS_M = (10, 20, 30, 50)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode(row: dict, key: str, scale: int) -> np.ndarray:
    return np.asarray([[[np.nan if value is None else value / scale for value in line] for line in layer]
                       for layer in row[key]], dtype=float)


def weighted_summary(values: np.ndarray, latitude: np.ndarray, valid: np.ndarray, digits: int = 2) -> dict:
    sample = values[valid]
    return {
        "latitude_weighted_mean": round(float(np.average(sample, weights=np.cos(np.deg2rad(latitude[valid])))), digits),
        "median": round(float(np.median(sample)), digits),
        "p05": round(float(np.percentile(sample, 5)), digits),
        "p95": round(float(np.percentile(sample, 95)), digits),
        "positive_cell_fraction": round(float(np.mean(sample > 0)), 4),
        "valid_cell_count": int(len(sample)),
    }


def state_advection(row: dict, latitude: np.ndarray, longitude: np.ndarray, mask: np.ndarray, diagonals: bool) -> np.ndarray:
    temperature = decode(row, "potential_temperature_c_milli_by_depth", 1000)
    eastward = decode(row, "eastward_velocity_m_s_e4_by_depth", 10_000)
    northward = decode(row, "northward_velocity_m_s_e4_by_depth", 10_000)
    result = np.full(temperature.shape, np.nan)
    for level in range(temperature.shape[0]):
        valid = mask & np.isfinite(temperature[level]) & np.isfinite(eastward[level]) & np.isfinite(northward[level])
        gradient_x, gradient_y = planar_gradient(temperature[level], latitude, longitude, valid, diagonals)
        result[level] = -(eastward[level] * gradient_x + northward[level] * gradient_y) * SECONDS_PER_DAY
    return result


def encode_map(values: np.ndarray, valid: np.ndarray, scale: int) -> list:
    return [[None if not valid[y, x] else int(round(values[y, x] * scale)) for x in range(values.shape[1])] for y in range(values.shape[0])]


def run(source_path: Path = SOURCE, d12_path: Path = D12, d13_path: Path = D13) -> dict:
    source = json.loads(source_path.read_text(encoding="utf-8"))
    d12 = json.loads(d12_path.read_text(encoding="utf-8"))
    d13 = json.loads(d13_path.read_text(encoding="utf-8"))
    depth = np.asarray(source["vertical_support"]["standard_depths_m"], dtype=float)
    latitude = np.asarray(source["grid"]["latitude_degrees_north_e6"], dtype=float) / 1_000_000
    longitude = np.asarray(source["grid"]["longitude_degrees_east_e6"], dtype=float) / 1_000_000
    mask = np.asarray(source["grid"]["inside_declared_box"], dtype=bool)
    anchor_distance = ((latitude - 42.125) ** 2 + ((longitude + 49.875) * math.cos(math.radians(42.125))) ** 2)
    anchor_distance[~mask] = np.inf
    anchor_y, anchor_x = np.unravel_index(np.argmin(anchor_distance), anchor_distance.shape)
    print("estimating eight-neighbor depthwise advection", flush=True)
    advection_8 = [state_advection(row, latitude, longitude, mask, True) for row in source["rows"]]
    print("estimating four-neighbor sensitivity", flush=True)
    advection_4 = [state_advection(row, latitude, longitude, mask, False) for row in source["rows"]]
    intervals, bridge_maps = [], None
    for index in range(len(source["rows"]) - 1):
        start, end = source["rows"][index]["date"], source["rows"][index + 1]["date"]
        if d13["intervals"][index]["start"] != start or d12["intervals"][index]["start"] != start:
            raise ValueError("D12-D14 intervals do not align")
        endpoint_advection = (advection_8[index] + advection_8[index + 1]) / 2
        endpoint_advection_4 = (advection_4[index] + advection_4[index + 1]) / 2
        columns = {}
        for limit in COLUMN_LIMITS_M:
            levels = depth <= limit
            integrated = np.trapezoid(endpoint_advection[levels], depth[levels], axis=0) * RHO_KG_M3 * CP_J_KG_K / SECONDS_PER_DAY
            integrated_4 = np.trapezoid(endpoint_advection_4[levels], depth[levels], axis=0) * RHO_KG_M3 * CP_J_KG_K / SECONDS_PER_DAY
            valid = mask & np.isfinite(integrated) & np.isfinite(integrated_4)
            primary = weighted_summary(integrated, latitude, valid)
            sensitivity = weighted_summary(integrated_4, latitude, valid)
            columns[f"zero_to_{limit}_m"] = {
                "endpoint_mean_horizontal_advection_w_m2": primary,
                "four_neighbor_mean_w_m2": sensitivity["latitude_weighted_mean"],
                "eight_minus_four_neighbor_mean_w_m2": round(primary["latitude_weighted_mean"] - sensitivity["latitude_weighted_mean"], 2),
                "anchor_horizontal_advection_w_m2": round(float(integrated[anchor_y, anchor_x]), 2),
            }
            if limit == 50:
                integrated_50, valid_50 = integrated, valid
        storage = d13["intervals"][index]["fixed_columns"]["zero_to_50_m"]["storage_tendency_w_m2"]["latitude_weighted_mean"]
        horizontal = columns["zero_to_50_m"]["endpoint_mean_horizontal_advection_w_m2"]["latitude_weighted_mean"]
        surface_flux = d12["intervals"][index]["gfs_net_downward_surface_flux_w_m2"]["latitude_weighted_mean"]
        intervals.append({
            "start": start,
            "end": end,
            "depth_integrated_horizontal_advection": columns,
            "cross_system_partial_budget_scale": {
                "rtofs_fixed_0_50_m_storage_tendency_w_m2": storage,
                "rtofs_offline_0_50_m_horizontal_advection_w_m2": horizontal,
                "gfs_net_downward_surface_flux_w_m2": surface_flux,
                "storage_minus_horizontal_advection_minus_surface_flux_w_m2": round(storage - horizontal - surface_flux, 2),
            },
        })
        if start == "2026-08-11":
            column_change = np.asarray([[np.nan if value is None else value / 1000 for value in line]
                                        for line in d13["bridge_interval_maps"]["zero_to_50_m_column_mean_temperature_change_c_milli"]])
            storage_map = column_change * 50 * RHO_KG_M3 * CP_J_KG_K / SECONDS_PER_DAY
            surface_map = np.asarray([[np.nan if value is None else value / 100 for value in line]
                                      for line in d12["bridge_interval_maps"]["net_downward_surface_flux_w_m2_centi"]])
            map_valid = valid_50 & np.isfinite(storage_map) & np.isfinite(surface_map)
            residual_map = storage_map - integrated_50 - surface_map
            bridge_maps = {
                "grid": "RTOFS subset grid from source artifact",
                "fixed_0_50_m_storage_tendency_w_m2_centi": encode_map(storage_map, map_valid, 100),
                "offline_0_50_m_horizontal_advection_w_m2_centi": encode_map(integrated_50, map_valid, 100),
                "cross_system_partial_residual_w_m2_centi": encode_map(residual_map, map_valid, 100),
            }
    bridge = intervals[-1]
    budget = bridge["cross_system_partial_budget_scale"]
    advection = bridge["depth_integrated_horizontal_advection"]["zero_to_50_m"]
    anchor_storage = d13["bridge_evaluation"]["anchor_zero_to_50_m_storage_tendency_w_m2"]
    anchor_surface = d12["bridge_evaluation"]["anchor_net_downward_surface_flux_w_m2"]
    anchor_advection = advection["anchor_horizontal_advection_w_m2"]
    anchor_residual = round(anchor_storage - anchor_advection - anchor_surface, 2)
    return {
        "schema": "osw.ocean-object-rtofs-upper-ocean-advection-screen.v1",
        "detection_id": "OSW-D14",
        "status": "cross_system_partial_fixed_column_budget_screen",
        "object_id": "OBJ046",
        "object_name": "marine heatwave",
        "source_artifacts": [
            {"path": str(source_path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(source_path), "role": "RTOFS standard-depth temperature and horizontal velocity"},
            {"path": str(d13_path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(d13_path), "role": "RTOFS fixed-column storage proxy"},
            {"path": str(d12_path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(d12_path), "role": "GFS forecast-derived surface flux"},
        ],
        "method": {
            "advection_equation": "rho * cp * vertical integral of endpoint-mean[-u*dT/dx - v*dT/dy] dz / 86400",
            "gradient": "local tangent-plane least-squares fit at each standard depth to eight neighboring wet grid centers; four-neighbor sensitivity retained",
            "constants": {"representative_seawater_density_kg_m3": RHO_KG_M3, "representative_seawater_heat_capacity_j_kg_k": CP_J_KG_K},
            "temporal_support": "daily 00 UTC snapshots with endpoint advection averaged across each interval",
            "spatial_summary": "cos(latitude)-weighted grid-center means over the fixed box; not exact native cell-area integration",
        },
        "anchor_grid_center": {"latitude_degrees_north": round(float(latitude[anchor_y, anchor_x]), 6), "longitude_degrees_east": round(float(longitude[anchor_y, anchor_x]), 6)},
        "intervals": intervals,
        "bridge_interval_maps": bridge_maps,
        "bridge_evaluation": {
            "result": "depth-integrated horizontal advection is a major box-scale term hidden by the surface-only screen",
            "rtofs_fixed_0_50_m_storage_tendency_w_m2": budget["rtofs_fixed_0_50_m_storage_tendency_w_m2"],
            "rtofs_offline_0_50_m_horizontal_advection_w_m2": budget["rtofs_offline_0_50_m_horizontal_advection_w_m2"],
            "gfs_net_downward_surface_flux_w_m2": budget["gfs_net_downward_surface_flux_w_m2"],
            "cross_system_partial_residual_w_m2": budget["storage_minus_horizontal_advection_minus_surface_flux_w_m2"],
            "horizontal_advection_fraction_of_storage": round(budget["rtofs_offline_0_50_m_horizontal_advection_w_m2"] / budget["rtofs_fixed_0_50_m_storage_tendency_w_m2"], 3),
            "surface_plus_horizontal_fraction_of_storage": round((budget["rtofs_offline_0_50_m_horizontal_advection_w_m2"] + budget["gfs_net_downward_surface_flux_w_m2"]) / budget["rtofs_fixed_0_50_m_storage_tendency_w_m2"], 3),
            "gradient_stencil_difference_w_m2": advection["eight_minus_four_neighbor_mean_w_m2"],
            "anchor_fixed_0_50_m_storage_tendency_w_m2": anchor_storage,
            "anchor_horizontal_advection_w_m2": anchor_advection,
            "anchor_gfs_net_downward_surface_flux_w_m2": anchor_surface,
            "anchor_cross_system_partial_residual_w_m2": anchor_residual,
            "anchor_partial_residual_fraction_of_storage": round(anchor_residual / anchor_storage, 3),
            "finding": "Surface-only horizontal advection understates the role of motion in this event. Across 0-50 m, the RTOFS offline advection scale is 72.5% of modeled fixed-column storage; adding cross-system GFS surface gain gives 120.2%, leaving a modest negative box residual. At the anchor, horizontal advection grows strongly with integration depth but 53.8% of storage remains unresolved.",
        },
        "next_evidence": "Use native model heat-budget diagnostics or quantify vertical boundary advection, mixing, and assimilation increments; test deeper fixed columns and subdaily covariance.",
        "boundary": "This is an offline standard-depth Eulerian horizontal-advection screen, not RTOFS native tracer flux or conservative heat convergence. The partial residual crosses RTOFS with GFS and cannot close either model. It combines vertical advection, mixing, entrainment, diffusion, shortwave penetration, assimilation increments, standard-depth interpolation, time sampling, gradient error, and cross-system mismatch. It is not causal attribution.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--d12", type=Path, default=D12)
    parser.add_argument("--d13", type=Path, default=D13)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    payload = run(args.source, args.d12, args.d13)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")
    print(json.dumps(payload["bridge_evaluation"], indent=2))


if __name__ == "__main__":
    main()
