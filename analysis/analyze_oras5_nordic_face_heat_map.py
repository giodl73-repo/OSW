"""Resolve time-weighted upwind heat convergence on every Nordic boundary face."""

from __future__ import annotations

import argparse
import calendar
import json
import pathlib

import netCDF4
import numpy as np

from analyze_oras5_nordic_partial_budget import CP0, MONTHS, RHO0, local_value
from audit_nemo_face_thickness_reconstruction import reconstruct_t
from fetch_oras5_drake_surface_heat import sha256_file


def analyze(root: pathlib.Path) -> dict:
    control_path = root / "research/osw-m4-oras5-nordic-control-volume.json"
    mesh_path = root / "atlas/data/oras5-nordic-seas-mesh.nc"
    anatomy_path = root / "research/osw-m4-oras5-nordic-heat-exchange-anatomy-2018.json"
    control = json.loads(control_path.read_text(encoding="utf-8"))
    anatomy = json.loads(anatomy_path.read_text(encoding="utf-8"))
    with netCDF4.Dataset(mesh_path) as mesh:
        thickness, _ = reconstruct_t(np.asarray(mesh.variables["e3t_0"][:], dtype=float), np.asarray(mesh.variables["mbathy"][:]), np.asarray(mesh.variables["e3t_ps"][:]))
        umask = np.asarray(mesh.variables["umask"][:], dtype=bool)
        vmask = np.asarray(mesh.variables["vmask"][:], dtype=bool)
        e2u = np.asarray(mesh.variables["e2u"][:], dtype=float)
        e1v = np.asarray(mesh.variables["e1v"][:], dtype=float)
    days = np.asarray([calendar.monthrange(2018, int(month[-2:]))[1] for month in MONTHS], dtype=float)
    accumulators = []
    for section in control["sections"]:
        section_accumulators = []
        for face in section["faces"]:
            y, x = int(face["y"]), int(face["x"])
            if face["face"] == "U":
                wet_area = float(np.sum(np.where(umask[:, y, x], np.minimum(thickness[:, y, x], thickness[:, y, x + 1]) * e2u[y, x], 0.0)))
            else:
                wet_area = float(np.sum(np.where(vmask[:, y, x], np.minimum(thickness[:, y, x], thickness[:, y + 1, x]) * e1v[y, x], 0.0)))
            section_accumulators.append({"convergence": 0.0, "inward_heat": 0.0, "outward_heat": 0.0, "inward_volume": 0.0, "outward_volume": 0.0, "wet_area_m2": wet_area, "monthly": []})
        accumulators.append(section_accumulators)
    for month, weight in zip(MONTHS, days):
        state_path = root / f"atlas/data/oras5-nordic-budget-state-{month}.nc"
        with netCDF4.Dataset(state_path) as state:
            temperature = state.variables["votemper"]
            for section_index, section in enumerate(control["sections"]):
                for face_index, face in enumerate(section["faces"]):
                    y, x = int(face["y"]), int(face["x"])
                    sign = int(face["sign_outward_from_nordic_seas"])
                    if face["face"] == "U":
                        velocity = np.ma.filled(local_value(state.variables["vozocrtx"], y, x), np.nan)
                        negative = np.ma.filled(local_value(temperature, y, x), np.nan)
                        positive = np.ma.filled(local_value(temperature, y, x + 1), np.nan)
                        wet, width = umask[:, y, x], e2u[y, x]
                        face_thickness = np.minimum(thickness[:, y, x], thickness[:, y, x + 1])
                    else:
                        velocity = np.ma.filled(local_value(state.variables["vomecrty"], y, x), np.nan)
                        negative = np.ma.filled(local_value(temperature, y, x), np.nan)
                        positive = np.ma.filled(local_value(temperature, y + 1, x), np.nan)
                        wet, width = vmask[:, y, x], e1v[y, x]
                        face_thickness = np.minimum(thickness[:, y, x], thickness[:, y + 1, x])
                    donor = np.where(velocity >= 0, negative, positive)
                    if np.any(~np.isfinite(velocity[wet])) or np.any(~np.isfinite(donor[wet])):
                        raise ValueError(f"{month} {section['id']} face {face_index} has missing wet state")
                    q = np.where(wet, sign * velocity * face_thickness * width, 0.0)
                    inward, outward = q < 0, q > 0
                    inward_heat = RHO0 * CP0 * float(np.sum(donor[inward] * -q[inward])) / 1e12
                    outward_heat = RHO0 * CP0 * float(np.sum(donor[outward] * q[outward])) / 1e12
                    target = accumulators[section_index][face_index]
                    target["convergence"] += weight * (inward_heat - outward_heat)
                    target["inward_heat"] += weight * inward_heat
                    target["outward_heat"] += weight * outward_heat
                    target["inward_volume"] += weight * float(np.sum(-q[inward]) / 1e6)
                    target["outward_volume"] += weight * float(np.sum(q[outward]) / 1e6)
                    target["monthly"].append({
                        "month": month,
                        "net_heat_convergence_TW_at_0C": inward_heat - outward_heat,
                        "inward_heat_TW_at_0C": inward_heat,
                        "outward_heat_TW_at_0C": outward_heat,
                    })
    sections = []
    total_days = float(days.sum())
    for source, values in zip(control["sections"], accumulators):
        faces = []
        for index, (face, value) in enumerate(zip(source["faces"], values)):
            convergence = value["convergence"] / total_days
            inward_heat = value["inward_heat"] / total_days
            outward_heat = value["outward_heat"] / total_days
            inward_volume = value["inward_volume"] / total_days
            outward_volume = value["outward_volume"] / total_days
            gross_volume = inward_volume + outward_volume
            exchange_speed = gross_volume * 1e6 / value["wet_area_m2"]
            thermal_factor = convergence * 1e12 / (RHO0 * CP0 * gross_volume * 1e6)
            faces.append({
                "index": index, "face": face["face"], "y": face["y"], "x": face["x"],
                "longitude_deg": face["longitude_deg"], "latitude_deg": face["latitude_deg"],
                "wet_cross_sectional_area_m2": value["wet_area_m2"],
                "net_heat_convergence_TW_at_0C": convergence,
                "net_heat_flux_density_MW_m2_at_0C": convergence * 1e6 / value["wet_area_m2"],
                "inward_heat_TW_at_0C": inward_heat,
                "outward_heat_TW_at_0C": outward_heat,
                "inward_volume_Sv": inward_volume,
                "outward_volume_Sv": outward_volume,
                "gross_volume_exchange_Sv": gross_volume,
                "gross_exchange_speed_m_s": exchange_speed,
                "net_thermal_transport_factor_C_at_0C": thermal_factor,
                "inward_effective_temperature_C": inward_heat * 1e12 / (RHO0 * CP0 * inward_volume * 1e6) if inward_volume > 0 else None,
                "outward_effective_temperature_C": outward_heat * 1e12 / (RHO0 * CP0 * outward_volume * 1e6) if outward_volume > 0 else None,
                "monthly": value["monthly"],
            })
        sections.append({"id": source["id"], "name": source["name"], "faces": faces, "net_heat_convergence_TW_at_0C": float(sum(face["net_heat_convergence_TW_at_0C"] for face in faces))})
    expected = {section["id"]: section["net_heat_convergence_TW_at_0C"] for section in anatomy["time_weighted_2018"]}
    residuals = {section["id"]: section["net_heat_convergence_TW_at_0C"] - expected[section["id"]] for section in sections}
    flat = [face | {"section_id": section["id"]} for section in sections for face in section["faces"]]
    absolute = sorted((abs(face["net_heat_convergence_TW_at_0C"]) for face in flat), reverse=True)
    gross = float(sum(absolute)); net = float(sum(face["net_heat_convergence_TW_at_0C"] for face in flat))
    total_rank = sorted(range(len(flat)), key=lambda index: abs(flat[index]["net_heat_convergence_TW_at_0C"]), reverse=True)
    density_rank = sorted(range(len(flat)), key=lambda index: abs(flat[index]["net_heat_flux_density_MW_m2_at_0C"]), reverse=True)
    top_20_overlap = len(set(total_rank[:20]) & set(density_rank[:20]))
    area = np.asarray([face["wet_cross_sectional_area_m2"] for face in flat])
    speed = np.asarray([face["gross_exchange_speed_m_s"] for face in flat])
    thermal = np.abs(np.asarray([face["net_thermal_transport_factor_C_at_0C"] for face in flat]))
    heat = np.abs(np.asarray([face["net_heat_convergence_TW_at_0C"] for face in flat]))

    def log_spread(values: np.ndarray) -> float:
        positive = values[values > 0]
        return float(np.percentile(positive, 90) / np.percentile(positive, 10))

    identity_error = max(abs(
        face["net_heat_convergence_TW_at_0C"]
        - RHO0 * CP0 * face["wet_cross_sectional_area_m2"]
        * face["gross_exchange_speed_m_s"]
        * face["net_thermal_transport_factor_C_at_0C"] / 1e12
    ) for face in flat)
    monthly_values = np.asarray([[entry["net_heat_convergence_TW_at_0C"] for entry in face["monthly"]] for face in flat])
    monthly_ranks = np.argsort(-np.abs(monthly_values), axis=0)
    annual_top_20 = set(total_rank[:20])
    monthly_top_20_overlap = [len(annual_top_20 & set(monthly_ranks[:20, month_index])) for month_index in range(12)]
    annual_leader = total_rank[0]
    annual_leader_ranks = [int(np.flatnonzero(monthly_ranks[:, month_index] == annual_leader)[0] + 1) for month_index in range(12)]
    stable_sign = np.all(monthly_values > 0, axis=1) | np.all(monthly_values < 0, axis=1)
    return {
        "schema": "osw.oras5.nordic-face-heat-map.v1",
        "status": "all_284_boundary_faces_time_weighted",
        "sign_convention": "positive net heat convergence enters the Nordic room; negative leaves",
        "sections": sections,
        "summary": {
            "face_count": len(flat),
            "positive_face_count": int(sum(face["net_heat_convergence_TW_at_0C"] > 0 for face in flat)),
            "negative_face_count": int(sum(face["net_heat_convergence_TW_at_0C"] < 0 for face in flat)),
            "maximum_positive_face": max(flat, key=lambda face: face["net_heat_convergence_TW_at_0C"]),
            "maximum_negative_face": min(flat, key=lambda face: face["net_heat_convergence_TW_at_0C"]),
            "gross_absolute_face_heat_TW": gross,
            "net_face_heat_convergence_TW": net,
            "opposing_face_cancellation_fraction": 1 - abs(net) / gross,
            "top_absolute_face_share": {str(count): float(sum(absolute[:count]) / gross) for count in (1, 5, 10, 20, 50, 100)},
            "top_20_total_and_density_overlap_count": top_20_overlap,
            "maximum_positive_flux_density_face": max(flat, key=lambda face: face["net_heat_flux_density_MW_m2_at_0C"]),
            "maximum_negative_flux_density_face": min(flat, key=lambda face: face["net_heat_flux_density_MW_m2_at_0C"]),
            "driver_p90_to_p10_spread": {
                "wet_cross_sectional_area": log_spread(area),
                "gross_exchange_speed": log_spread(speed),
                "absolute_net_thermal_transport_factor": log_spread(thermal),
                "absolute_net_heat_convergence": log_spread(heat),
            },
            "maximum_driver_identity_error_TW": float(identity_error),
            "monthly_persistence": {
                "same_nonzero_sign_all_12_months_face_count": int(np.sum(stable_sign)),
                "annual_top_20_same_nonzero_sign_all_12_months_count": int(np.sum(stable_sign[list(annual_top_20)])),
                "annual_top_20_monthly_top_20_overlap": {month: overlap for month, overlap in zip(MONTHS, monthly_top_20_overlap)},
                "annual_top_20_monthly_overlap_mean": float(np.mean(monthly_top_20_overlap)),
                "annual_leader_positive_month_count": int(np.sum(monthly_values[annual_leader] > 0)),
                "annual_leader_monthly_absolute_rank_min": min(annual_leader_ranks),
                "annual_leader_monthly_absolute_rank_max": max(annual_leader_ranks),
                "annual_leader_monthly_absolute_ranks": {month: rank for month, rank in zip(MONTHS, annual_leader_ranks)},
            },
            "section_sum_residual_TW": residuals,
        },
        "checks": {"face_count_matches_control": len(flat) == 284, "all_section_sums_match_anatomy": all(abs(value) < 1e-9 for value in residuals.values()), "driver_identity_closes": bool(identity_error < 1e-12)},
        "sources": {"control": sha256_file(control_path), "mesh": sha256_file(mesh_path), "anatomy": sha256_file(anatomy_path)},
        "boundary": "Annual face values use day-weighted monthly-mean velocity and upstream donor temperature. Face TW includes wet width and depth; MW/m² divides by reconstructed wet cross-sectional area and is a cross-section-average transport intensity, not surface heat flux. The signed thermal transport factor is net heat divided by gross volume exchange and is an exact accounting factor, not a water-mass temperature. Neither measure is native FCT/TVD, submonthly eddy covariance, climatology, uncertainty, or a causal pathway beyond the boundary.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path("."))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-face-heat-map-2018.json"))
    args = parser.parse_args()
    result = analyze(args.root.resolve())
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
