"""Screen GFS surface energy against the RTOFS marine-heatwave bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
GFS_SOURCE = ROOT / "atlas" / "data" / "gfs-mhw-surface-flux-north-atlantic-20260807-20260812.json"
RTOFS_SOURCE = ROOT / "atlas" / "data" / "rtofs-mhw-bridge-north-atlantic-20260807-20260812.json"
D11_SOURCE = ROOT / "research" / "osw-d11-rtofs-mhw-horizontal-advection-2026.json"
OUTPUT = ROOT / "research" / "osw-d12-gfs-surface-flux-screen-2026.json"
RHO_KG_M3 = 1025.0
CP_J_KG_K = 3990.0
SECONDS_PER_DAY = 86_400.0


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode(values: list, scale: float) -> np.ndarray:
    return np.asarray([[np.nan if value is None else value / scale for value in row] for row in values], dtype=float)


def bilinear_rectilinear(source_latitude: np.ndarray, source_longitude: np.ndarray, values: np.ndarray,
                         target_latitude: np.ndarray, target_longitude: np.ndarray) -> np.ndarray:
    latitudes = source_latitude[:, 0]
    longitudes = source_longitude[0, :]
    field = values
    if latitudes[0] > latitudes[-1]:
        latitudes = latitudes[::-1]
        field = field[::-1, :]
    if longitudes[0] > longitudes[-1]:
        longitudes = longitudes[::-1]
        field = field[:, ::-1]
    y1 = np.searchsorted(latitudes, target_latitude, side="right")
    x1 = np.searchsorted(longitudes, target_longitude, side="right")
    y1 = np.clip(y1, 1, len(latitudes) - 1)
    x1 = np.clip(x1, 1, len(longitudes) - 1)
    y0, x0 = y1 - 1, x1 - 1
    fy = (target_latitude - latitudes[y0]) / (latitudes[y1] - latitudes[y0])
    fx = (target_longitude - longitudes[x0]) / (longitudes[x1] - longitudes[x0])
    return ((1 - fy) * (1 - fx) * field[y0, x0] + fy * (1 - fx) * field[y1, x0] +
            (1 - fy) * fx * field[y0, x1] + fy * fx * field[y1, x1])


def weighted_mean(values: np.ndarray, latitude: np.ndarray, valid: np.ndarray) -> float:
    return float(np.average(values[valid], weights=np.cos(np.deg2rad(latitude[valid]))))


def summary(values: np.ndarray, latitude: np.ndarray, valid: np.ndarray, digits: int = 3) -> dict:
    sample = values[valid]
    return {
        "latitude_weighted_mean": round(weighted_mean(values, latitude, valid), digits),
        "median": round(float(np.median(sample)), digits),
        "p05": round(float(np.percentile(sample, 5)), digits),
        "p95": round(float(np.percentile(sample, 95)), digits),
        "positive_cell_fraction": round(float(np.mean(sample > 0)), 4),
        "valid_cell_count": int(len(sample)),
    }


def depth_sensitivity(net_flux: np.ndarray, depth: np.ndarray, latitude: np.ndarray, valid: np.ndarray) -> dict:
    result = {}
    for floor_m in (0, 2, 5, 10):
        effective_depth = depth if floor_m == 0 else np.maximum(depth, floor_m)
        tendency = net_flux * SECONDS_PER_DAY / (RHO_KG_M3 * CP_J_KG_K * effective_depth)
        key = "native_diagnostic_depth" if floor_m == 0 else f"minimum_{floor_m}_m_depth"
        result[key + "_c_per_day"] = round(weighted_mean(tendency, latitude, valid), 4)
    mean_flux = weighted_mean(net_flux, latitude, valid)
    mean_depth = weighted_mean(depth, latitude, valid)
    result["box_mean_flux_over_box_mean_depth_c_per_day"] = round(
        mean_flux * SECONDS_PER_DAY / (RHO_KG_M3 * CP_J_KG_K * mean_depth), 4
    )
    result["latitude_weighted_mean_depth_m"] = round(mean_depth, 3)
    result["cell_fraction_below_2_m"] = round(float(np.mean(depth[valid] < 2)), 4)
    result["cell_fraction_below_5_m"] = round(float(np.mean(depth[valid] < 5)), 4)
    return result


def net_downward(row: dict) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    components = {
        "latent_up": decode(row["latent_heat_flux_upward_w_m2_centi"], 100),
        "sensible_up": decode(row["sensible_heat_flux_upward_w_m2_centi"], 100),
        "shortwave_down": decode(row["shortwave_downward_w_m2_centi"], 100),
        "longwave_down": decode(row["longwave_downward_w_m2_centi"], 100),
        "shortwave_up": decode(row["shortwave_upward_w_m2_centi"], 100),
        "longwave_up": decode(row["longwave_upward_w_m2_centi"], 100),
    }
    net = (components["shortwave_down"] + components["longwave_down"] -
           components["shortwave_up"] - components["longwave_up"] -
           components["latent_up"] - components["sensible_up"])
    return net, components


def encode_map(values: np.ndarray, valid: np.ndarray, scale: int) -> list:
    return [[None if not valid[y, x] else int(round(values[y, x] * scale)) for x in range(values.shape[1])] for y in range(values.shape[0])]


def run(gfs_path: Path = GFS_SOURCE, rtofs_path: Path = RTOFS_SOURCE, d11_path: Path = D11_SOURCE) -> dict:
    gfs = json.loads(gfs_path.read_text(encoding="utf-8"))
    rtofs = json.loads(rtofs_path.read_text(encoding="utf-8"))
    d11 = json.loads(d11_path.read_text(encoding="utf-8"))
    gfs_latitude = np.asarray(gfs["grid"]["latitude_degrees_north_e6"], dtype=float) / 1_000_000
    gfs_longitude = np.asarray(gfs["grid"]["longitude_degrees_east_e6"], dtype=float) / 1_000_000
    rtofs_latitude = np.asarray(rtofs["grid"]["latitude_degrees_north_e6"], dtype=float) / 1_000_000
    rtofs_longitude = np.asarray(rtofs["grid"]["longitude_degrees_east_e6"], dtype=float) / 1_000_000
    rtofs_mask = np.asarray(rtofs["grid"]["inside_declared_box"], dtype=bool)
    anchor_distance = ((rtofs_latitude - 42.125) ** 2 +
                       ((rtofs_longitude + 49.875) * math.cos(math.radians(42.125))) ** 2)
    anchor_distance[~rtofs_mask] = np.inf
    anchor_y, anchor_x = np.unravel_index(np.argmin(anchor_distance), anchor_distance.shape)
    intervals = []
    bridge_maps = None
    for index, gfs_row in enumerate(gfs["rows"]):
        if rtofs["rows"][index]["date"] != gfs_row["start"] or rtofs["rows"][index + 1]["date"] != gfs_row["end"]:
            raise ValueError("GFS forcing and RTOFS state intervals do not align")
        if d11["intervals"][index]["start"] != gfs_row["start"] or d11["intervals"][index]["end"] != gfs_row["end"]:
            raise ValueError("GFS forcing and D11 tendency intervals do not align")
        net_gfs, components = net_downward(gfs_row)
        net_rtofs = bilinear_rectilinear(gfs_latitude, gfs_longitude, net_gfs, rtofs_latitude, rtofs_longitude)
        start_mld = decode(rtofs["rows"][index]["mixed_layer_thickness_m_centi"], 100)
        end_mld = decode(rtofs["rows"][index + 1]["mixed_layer_thickness_m_centi"], 100)
        mean_mld = (start_mld + end_mld) / 2
        valid = rtofs_mask & np.isfinite(net_rtofs) & np.isfinite(start_mld) & np.isfinite(end_mld) & (start_mld > 0) & (mean_mld > 0)
        start_depth_tendency = net_rtofs * SECONDS_PER_DAY / (RHO_KG_M3 * CP_J_KG_K * start_mld)
        mean_depth_tendency = net_rtofs * SECONDS_PER_DAY / (RHO_KG_M3 * CP_J_KG_K * mean_mld)
        gfs_valid = np.isfinite(net_gfs)
        component_means = {name + "_w_m2": round(weighted_mean(field, gfs_latitude, gfs_valid), 2) for name, field in components.items()}
        d11_interval = d11["intervals"][index]
        modeled_tendency = d11_interval["surface_temperature_tendency"]["latitude_weighted_mean_c_per_day"]
        horizontal_advection = d11_interval["endpoint_mean_horizontal_advection"]["latitude_weighted_mean_c_per_day"]
        unresolved = d11_interval["unresolved_remainder"]["latitude_weighted_mean_c_per_day"]
        flux_mean_start = weighted_mean(start_depth_tendency, rtofs_latitude, valid)
        flux_mean_mid = weighted_mean(mean_depth_tendency, rtofs_latitude, valid)
        start_sensitivity = depth_sensitivity(net_rtofs, start_mld, rtofs_latitude, valid)
        mean_sensitivity = depth_sensitivity(net_rtofs, mean_mld, rtofs_latitude, valid)
        intervals.append({
            "start": gfs_row["start"],
            "end": gfs_row["end"],
            "gfs_box_component_means": component_means,
            "gfs_net_downward_surface_flux_w_m2": summary(net_gfs, gfs_latitude, gfs_valid, 2),
            "rtofs_grid_collocation": {
                "interpolation": "bilinear from rectilinear GFS Gaussian-grid centers to RTOFS grid centers",
                "net_downward_surface_flux_w_m2": summary(net_rtofs, rtofs_latitude, valid, 2),
                "mixed_layer_equivalent_tendency_start_depth_c_per_day": summary(start_depth_tendency, rtofs_latitude, valid, 4),
                "mixed_layer_equivalent_tendency_endpoint_mean_depth_c_per_day": summary(mean_depth_tendency, rtofs_latitude, valid, 4),
                "start_depth_sensitivity": start_sensitivity,
                "endpoint_mean_depth_sensitivity": mean_sensitivity,
            },
            "cross_system_scale_comparison": {
                "rtofs_surface_temperature_tendency_c_per_day": modeled_tendency,
                "rtofs_horizontal_advection_c_per_day": horizontal_advection,
                "rtofs_pre_flux_unresolved_remainder_c_per_day": unresolved,
                "gfs_flux_equivalent_start_depth_c_per_day": round(flux_mean_start, 4),
                "gfs_flux_equivalent_endpoint_mean_depth_c_per_day": round(flux_mean_mid, 4),
                "post_flux_scale_residual_start_depth_c_per_day": round(unresolved - flux_mean_start, 4),
                "post_flux_scale_residual_endpoint_mean_depth_c_per_day": round(unresolved - flux_mean_mid, 4),
            },
            "anchor": {
                "net_downward_surface_flux_w_m2": round(float(net_rtofs[anchor_y, anchor_x]), 2),
                "start_mixed_layer_depth_m": round(float(start_mld[anchor_y, anchor_x]), 2),
                "end_mixed_layer_depth_m": round(float(end_mld[anchor_y, anchor_x]), 2),
                "flux_equivalent_start_depth_c_per_day": round(float(start_depth_tendency[anchor_y, anchor_x]), 4),
                "flux_equivalent_endpoint_mean_depth_c_per_day": round(float(mean_depth_tendency[anchor_y, anchor_x]), 4),
                "rtofs_surface_temperature_tendency_c_per_day": d11_interval["anchor"]["surface_temperature_tendency_c_per_day"],
                "rtofs_horizontal_advection_c_per_day": d11_interval["anchor"]["endpoint_mean_horizontal_advection_c_per_day"],
            },
        })
        if gfs_row["start"] == "2026-08-11":
            floor_5_tendency = net_rtofs * SECONDS_PER_DAY / (RHO_KG_M3 * CP_J_KG_K * np.maximum(start_mld, 5))
            bridge_maps = {
                "grid": "RTOFS subset grid from source artifact",
                "net_downward_surface_flux_w_m2_centi": encode_map(net_rtofs, valid, 100),
                "start_mixed_layer_depth_m_centi": encode_map(start_mld, valid, 100),
                "mixed_layer_equivalent_tendency_start_depth_c_per_day_e4": encode_map(start_depth_tendency, valid, 10_000),
                "mixed_layer_equivalent_tendency_minimum_5_m_start_depth_c_per_day_e4": encode_map(floor_5_tendency, valid, 10_000),
                "mixed_layer_equivalent_tendency_endpoint_mean_depth_c_per_day_e4": encode_map(mean_depth_tendency, valid, 10_000),
            }
    bridge = intervals[-1]
    compare = bridge["cross_system_scale_comparison"]
    anchor = bridge["anchor"]
    return {
        "schema": "osw.ocean-object-gfs-surface-flux-screen.v1",
        "detection_id": "OSW-D12",
        "status": "cross_system_surface_energy_plausibility_screen",
        "object_id": "OBJ046",
        "object_name": "marine heatwave",
        "source_artifacts": [
            {"path": str(gfs_path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(gfs_path), "role": "forecast-derived surface forcing"},
            {"path": str(rtofs_path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(rtofs_path), "role": "operational assimilative ocean state and mixed-layer thickness"},
            {"path": str(d11_path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(d11_path), "role": "offline surface horizontal-advection screen"},
        ],
        "method": {
            "net_flux_equation": "Qnet_down = DSWRF + DLWRF - USWRF - ULWRF - LHTFL - SHTFL",
            "temperature_scale_equation": "dT/dt_flux = Qnet_down * 86400 / (rho * cp * mixed-layer thickness)",
            "constants": {"representative_seawater_density_kg_m3": RHO_KG_M3, "representative_seawater_heat_capacity_j_kg_k": CP_J_KG_K},
            "sign_convention": "positive net flux is downward into the surface; GFS LHTFL and SHTFL are treated as positive upward losses",
            "depth_variants": "RTOFS start-of-day diagnostic mixed-layer thickness and arithmetic endpoint mean; neither reconstructs entrainment heat content",
            "spatial_summary": "cos(latitude)-weighted grid-center means; GFS-to-RTOFS bilinear interpolation; not exact conservative remapping or native cell-area integration",
        },
        "anchor_grid_center": {"latitude_degrees_north": round(float(rtofs_latitude[anchor_y, anchor_x]), 6), "longitude_degrees_east": round(float(rtofs_longitude[anchor_y, anchor_x]), 6)},
        "intervals": intervals,
        "bridge_interval_maps": bridge_maps,
        "bridge_evaluation": {
            "result": "surface heat gain is contemporaneous and material but does not close the modeled bridge-day warming scale",
            "gfs_box_net_downward_surface_flux_w_m2": bridge["gfs_net_downward_surface_flux_w_m2"]["latitude_weighted_mean"],
            "rtofs_grid_flux_equivalent_start_depth_c_per_day": compare["gfs_flux_equivalent_start_depth_c_per_day"],
            "rtofs_grid_flux_equivalent_endpoint_mean_depth_c_per_day": compare["gfs_flux_equivalent_endpoint_mean_depth_c_per_day"],
            "fraction_of_rtofs_pre_flux_remainder_start_depth": round(compare["gfs_flux_equivalent_start_depth_c_per_day"] / compare["rtofs_pre_flux_unresolved_remainder_c_per_day"], 3),
            "fraction_of_rtofs_pre_flux_remainder_endpoint_mean_depth": round(compare["gfs_flux_equivalent_endpoint_mean_depth_c_per_day"] / compare["rtofs_pre_flux_unresolved_remainder_c_per_day"], 3),
            "depth_floor_sensitivity": {
                "start_depth": bridge["rtofs_grid_collocation"]["start_depth_sensitivity"],
                "endpoint_mean_depth": bridge["rtofs_grid_collocation"]["endpoint_mean_depth_sensitivity"],
                "interpretation": "native cellwise scaling is sensitive to sub-5-m diagnostic layers; the floor variants and box-mean slab are magnitude bounds, not alternative observations",
            },
            "anchor_net_downward_surface_flux_w_m2": anchor["net_downward_surface_flux_w_m2"],
            "anchor_flux_equivalent_start_depth_c_per_day": anchor["flux_equivalent_start_depth_c_per_day"],
            "anchor_flux_equivalent_endpoint_mean_depth_c_per_day": anchor["flux_equivalent_endpoint_mean_depth_c_per_day"],
            "finding": "The August 11 GFS interval supplies positive surface heat gain during the RTOFS bridge-day warming. Mixed-layer scaling determines how much warming that energy can support; the comparison remains a cross-system magnitude test, not a term-by-term closure.",
        },
        "next_evidence": "Use a single-system native mixed-layer heat budget or a collocated atmospheric reanalysis plus observed mixed-layer depth, including penetrating shortwave, entrainment, vertical mixing, vertical advection, and analysis increments.",
        "boundary": "This combines an operational GFS forecast with an operational assimilative RTOFS ocean state. Their grids, physics, initialization, and analysis cycles differ. Subtracting the GFS-derived temperature scale from the RTOFS remainder is diagnostic bookkeeping only, not model closure, independent validation, or causal attribution. Bulk surface flux is not automatically deposited uniformly within a diagnostic mixed layer; shortwave penetration, changing layer depth, vertical exchange, and assimilation remain unresolved.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gfs", type=Path, default=GFS_SOURCE)
    parser.add_argument("--rtofs", type=Path, default=RTOFS_SOURCE)
    parser.add_argument("--d11", type=Path, default=D11_SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    payload = run(args.gfs, args.rtofs, args.d11)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")
    print(json.dumps(payload["bridge_evaluation"], indent=2))


if __name__ == "__main__":
    main()
