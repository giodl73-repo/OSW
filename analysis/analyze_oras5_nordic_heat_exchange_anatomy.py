"""Resolve inward and outward donor-water heat branches at each Nordic gate."""

from __future__ import annotations

import argparse
import calendar
import json
import pathlib

import netCDF4
import numpy as np

from analyze_oras5_nordic_partial_budget import CP0, MONTHS, RHO0, local_value
from audit_oras5_arctic_section_geometry import DEPTH_BINS_M, vertical_midpoints
from audit_nemo_face_thickness_reconstruction import reconstruct_t
from fetch_oras5_drake_surface_heat import sha256_file


def analyze(root: pathlib.Path) -> dict:
    control_path = root / "research/osw-m4-oras5-nordic-control-volume.json"
    mesh_path = root / "atlas/data/oras5-nordic-seas-mesh.nc"
    control = json.loads(control_path.read_text(encoding="utf-8"))
    with netCDF4.Dataset(mesh_path) as mesh:
        reference = np.asarray(mesh.variables["e3t_0"][:], dtype=float)
        thickness, _ = reconstruct_t(reference, np.asarray(mesh.variables["mbathy"][:]), np.asarray(mesh.variables["e3t_ps"][:]))
        umask = np.asarray(mesh.variables["umask"][:], dtype=bool)
        vmask = np.asarray(mesh.variables["vmask"][:], dtype=bool)
        e2u = np.asarray(mesh.variables["e2u"][:], dtype=float)
        e1v = np.asarray(mesh.variables["e1v"][:], dtype=float)
    midpoints = vertical_midpoints(reference)
    monthly = []
    for month in MONTHS:
        state_path = root / f"atlas/data/oras5-nordic-budget-state-{month}.nc"
        section_records = []
        with netCDF4.Dataset(state_path) as state:
            temperature = state.variables["votemper"]
            for section in control["sections"]:
                inward_volume = outward_volume = inward_theta_q = outward_theta_q = 0.0
                bin_accumulators = [dict(inward_volume=0.0, outward_volume=0.0, inward_theta_q=0.0, outward_theta_q=0.0) for _ in DEPTH_BINS_M]
                for face in section["faces"]:
                    y, x = int(face["y"]), int(face["x"])
                    sign = int(face["sign_outward_from_nordic_seas"])
                    if face["face"] == "U":
                        velocity = np.ma.filled(local_value(state.variables["vozocrtx"], y, x), np.nan)
                        negative = np.ma.filled(local_value(temperature, y, x), np.nan)
                        positive = np.ma.filled(local_value(temperature, y, x + 1), np.nan)
                        face_thickness = np.minimum(thickness[:, y, x], thickness[:, y, x + 1])
                        wet, width = umask[:, y, x], e2u[y, x]
                    else:
                        velocity = np.ma.filled(local_value(state.variables["vomecrty"], y, x), np.nan)
                        negative = np.ma.filled(local_value(temperature, y, x), np.nan)
                        positive = np.ma.filled(local_value(temperature, y + 1, x), np.nan)
                        face_thickness = np.minimum(thickness[:, y, x], thickness[:, y + 1, x])
                        wet, width = vmask[:, y, x], e1v[y, x]
                    donor = np.where(velocity >= 0, negative, positive)
                    if np.any(~np.isfinite(velocity[wet])) or np.any(~np.isfinite(donor[wet])):
                        raise ValueError(f"{month} {section['id']} has missing wet state")
                    q = np.where(wet, sign * velocity * face_thickness * width, 0.0)
                    inward = q < 0; outward = q > 0
                    inward_volume += float(np.sum(-q[inward]))
                    outward_volume += float(np.sum(q[outward]))
                    inward_theta_q += float(np.sum(donor[inward] * -q[inward]))
                    outward_theta_q += float(np.sum(donor[outward] * q[outward]))
                    for accumulator, (lower, upper) in zip(bin_accumulators, DEPTH_BINS_M):
                        level = midpoints >= lower
                        if upper is not None:
                            level &= midpoints < upper
                        inward_bin = inward & level; outward_bin = outward & level
                        accumulator["inward_volume"] += float(np.sum(-q[inward_bin]))
                        accumulator["outward_volume"] += float(np.sum(q[outward_bin]))
                        accumulator["inward_theta_q"] += float(np.sum(donor[inward_bin] * -q[inward_bin]))
                        accumulator["outward_theta_q"] += float(np.sum(donor[outward_bin] * q[outward_bin]))
                depth_bins = []
                for accumulator, (lower, upper) in zip(bin_accumulators, DEPTH_BINS_M):
                    iv, ov = accumulator["inward_volume"], accumulator["outward_volume"]
                    ih = RHO0 * CP0 * accumulator["inward_theta_q"] / 1e12
                    oh = RHO0 * CP0 * accumulator["outward_theta_q"] / 1e12
                    depth_bins.append({
                        "lower_m": lower, "upper_m": upper,
                        "inward_volume_Sv": iv / 1e6, "outward_volume_Sv": ov / 1e6,
                        "inward_transport_weighted_temperature_degC": accumulator["inward_theta_q"] / iv if iv else None,
                        "outward_transport_weighted_temperature_degC": accumulator["outward_theta_q"] / ov if ov else None,
                        "inward_heat_TW_at_0C": ih, "outward_heat_TW_at_0C": oh,
                        "net_heat_convergence_TW_at_0C": ih - oh,
                    })
                section_records.append({
                    "id": section["id"],
                    "inward_volume_Sv": inward_volume / 1e6,
                    "outward_volume_Sv": outward_volume / 1e6,
                    "inward_transport_weighted_temperature_degC": inward_theta_q / inward_volume if inward_volume else None,
                    "outward_transport_weighted_temperature_degC": outward_theta_q / outward_volume if outward_volume else None,
                    "inward_heat_TW_at_0C": RHO0 * CP0 * inward_theta_q / 1e12,
                    "outward_heat_TW_at_0C": RHO0 * CP0 * outward_theta_q / 1e12,
                    "net_heat_convergence_TW_at_0C": RHO0 * CP0 * (inward_theta_q - outward_theta_q) / 1e12,
                    "depth_bins": depth_bins,
                })
        monthly.append({"month": month, "sections": section_records})
    weights = np.asarray([calendar.monthrange(2018, int(month[-2:]))[1] for month in MONTHS], dtype=float)
    annual = []
    for index, section in enumerate(control["sections"]):
        inward_volume = float(np.average([record["sections"][index]["inward_volume_Sv"] for record in monthly], weights=weights))
        outward_volume = float(np.average([record["sections"][index]["outward_volume_Sv"] for record in monthly], weights=weights))
        inward_heat = float(np.average([record["sections"][index]["inward_heat_TW_at_0C"] for record in monthly], weights=weights))
        outward_heat = float(np.average([record["sections"][index]["outward_heat_TW_at_0C"] for record in monthly], weights=weights))
        annual.append({
            "id": section["id"],
            "inward_volume_Sv": inward_volume,
            "outward_volume_Sv": outward_volume,
            "net_inward_volume_Sv": inward_volume - outward_volume,
            "inward_effective_temperature_degC": inward_heat * 1e12 / (RHO0 * CP0 * inward_volume * 1e6) if inward_volume else None,
            "outward_effective_temperature_degC": outward_heat * 1e12 / (RHO0 * CP0 * outward_volume * 1e6) if outward_volume else None,
            "inward_heat_TW_at_0C": inward_heat,
            "outward_heat_TW_at_0C": outward_heat,
            "net_heat_convergence_TW_at_0C": inward_heat - outward_heat,
            "depth_bins": [
                {
                    "lower_m": bounds[0], "upper_m": bounds[1],
                    "inward_volume_Sv": float(np.average([record["sections"][index]["depth_bins"][bin_index]["inward_volume_Sv"] for record in monthly], weights=weights)),
                    "outward_volume_Sv": float(np.average([record["sections"][index]["depth_bins"][bin_index]["outward_volume_Sv"] for record in monthly], weights=weights)),
                    "inward_heat_TW_at_0C": float(np.average([record["sections"][index]["depth_bins"][bin_index]["inward_heat_TW_at_0C"] for record in monthly], weights=weights)),
                    "outward_heat_TW_at_0C": float(np.average([record["sections"][index]["depth_bins"][bin_index]["outward_heat_TW_at_0C"] for record in monthly], weights=weights)),
                    "net_heat_convergence_TW_at_0C": float(np.average([record["sections"][index]["depth_bins"][bin_index]["net_heat_convergence_TW_at_0C"] for record in monthly], weights=weights)),
                }
                for bin_index, bounds in enumerate(DEPTH_BINS_M)
            ],
        })
    return {
        "schema": "osw.oras5.nordic-heat-exchange-anatomy.v1",
        "status": "upwind_donor_inward_outward_branches_resolved",
        "sign_convention": "inward and outward branch magnitudes are positive; net convergence is inward heat minus outward heat",
        "months": monthly,
        "time_weighted_2018": annual,
        "depth_bins_m": [list(bounds) for bounds in DEPTH_BINS_M],
        "checks": {
            "month_count": len(monthly),
            "section_count": len(annual),
            "net_convergence_sum_TW": float(sum(section["net_heat_convergence_TW_at_0C"] for section in annual)),
            "all_branches_positive": all(section["inward_volume_Sv"] > 0 and section["outward_volume_Sv"] > 0 for section in annual),
            "all_depth_bins_reproduce_section_heat": all(np.isclose(sum(item["net_heat_convergence_TW_at_0C"] for item in section["depth_bins"]), section["net_heat_convergence_TW_at_0C"]) for section in annual),
        },
        "sources": {"control": sha256_file(control_path), "mesh": sha256_file(mesh_path)},
        "boundary": "Branch anatomy uses monthly-mean velocity and an upstream donor-cell temperature. It demonstrates directional thermal contrast but is not ORAS5 native FCT/TVD transport, submonthly covariance, observation-only exchange, or a closed heat budget.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path("."))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-heat-exchange-anatomy-2018.json"))
    args = parser.parse_args()
    result = analyze(args.root.resolve())
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result["time_weighted_2018"], indent=2))


if __name__ == "__main__":
    main()
