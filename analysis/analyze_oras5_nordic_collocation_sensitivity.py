"""Test Nordic boundary heat convergence against four tracer-to-face rules."""

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


METHODS = ("adjacent_mean", "upwind", "inside_cell", "outside_cell")


def analyze(root: pathlib.Path) -> dict:
    control_path = root / "research/osw-m4-oras5-nordic-control-volume.json"
    mesh_path = root / "atlas/data/oras5-nordic-seas-mesh.nc"
    budget_path = root / "research/osw-m4-oras5-nordic-partial-budget-2018.json"
    control = json.loads(control_path.read_text(encoding="utf-8"))
    budget = json.loads(budget_path.read_text(encoding="utf-8"))
    with netCDF4.Dataset(mesh_path) as mesh:
        thickness, _ = reconstruct_t(np.asarray(mesh.variables["e3t_0"][:], dtype=float), np.asarray(mesh.variables["mbathy"][:]), np.asarray(mesh.variables["e3t_ps"][:]))
        umask = np.asarray(mesh.variables["umask"][:], dtype=bool)
        vmask = np.asarray(mesh.variables["vmask"][:], dtype=bool)
        e2u = np.asarray(mesh.variables["e2u"][:], dtype=float)
        e1v = np.asarray(mesh.variables["e1v"][:], dtype=float)
    records = []
    for month, budget_record in zip(MONTHS, budget["months"]):
        state_path = root / f"atlas/data/oras5-nordic-budget-state-{month}.nc"
        section_totals = {method: [] for method in METHODS}
        with netCDF4.Dataset(state_path) as state:
            temperature = state.variables["votemper"]
            for section in control["sections"]:
                heat = {method: 0.0 for method in METHODS}
                for face in section["faces"]:
                    y, x = int(face["y"]), int(face["x"])
                    sign = int(face["sign_outward_from_nordic_seas"])
                    if face["face"] == "U":
                        velocity = np.ma.filled(local_value(state.variables["vozocrtx"], y, x), np.nan)
                        negative = np.ma.filled(local_value(temperature, y, x), np.nan)
                        positive = np.ma.filled(local_value(temperature, y, x + 1), np.nan)
                        face_thickness = np.minimum(thickness[:, y, x], thickness[:, y, x + 1])
                        wet = umask[:, y, x]
                        width = e2u[y, x]
                    else:
                        velocity = np.ma.filled(local_value(state.variables["vomecrty"], y, x), np.nan)
                        negative = np.ma.filled(local_value(temperature, y, x), np.nan)
                        positive = np.ma.filled(local_value(temperature, y + 1, x), np.nan)
                        face_thickness = np.minimum(thickness[:, y, x], thickness[:, y + 1, x])
                        wet = vmask[:, y, x]
                        width = e1v[y, x]
                    if np.any(~np.isfinite(velocity[wet])) or np.any(~np.isfinite(negative[wet])) or np.any(~np.isfinite(positive[wet])):
                        raise ValueError(f"{month} {section['id']} has missing wet state")
                    outward_q = np.where(wet, sign * velocity * face_thickness * width, 0.0)
                    tracers = {
                        "adjacent_mean": 0.5 * (negative + positive),
                        "upwind": np.where(velocity >= 0, negative, positive),
                        "inside_cell": negative if sign == 1 else positive,
                        "outside_cell": positive if sign == 1 else negative,
                    }
                    for method, tracer in tracers.items():
                        heat[method] += float(RHO0 * CP0 * np.sum(np.where(wet, tracer, 0.0) * outward_q) / 1e12)
                for method in METHODS:
                    section_totals[method].append({"id": section["id"], "outward_heat_TW_at_0C": heat[method]})
        method_records = {}
        for method in METHODS:
            outward = float(sum(section["outward_heat_TW_at_0C"] for section in section_totals[method]))
            remainder = budget_record["storage_tendency_TW"]["0.0"] + outward - budget_record["surface_downward_TW"]
            method_records[method] = {
                "advective_convergence_TW_at_0C": -outward,
                "unresolved_remainder_TW_at_0C": remainder,
                "sections": section_totals[method],
            }
        records.append({"month": month, "methods": method_records})
    weights = np.asarray([calendar.monthrange(2018, int(month[-2:]))[1] for month in MONTHS], dtype=float)
    summary = {}
    for method in METHODS:
        convergence = np.asarray([record["methods"][method]["advective_convergence_TW_at_0C"] for record in records])
        remainder = np.asarray([record["methods"][method]["unresolved_remainder_TW_at_0C"] for record in records])
        summary[method] = {
            "time_weighted_advective_convergence_TW_at_0C": float(np.average(convergence, weights=weights)),
            "time_weighted_unresolved_remainder_TW_at_0C": float(np.average(remainder, weights=weights)),
            "monthly_remainder_minimum_TW": float(remainder.min()),
            "monthly_remainder_maximum_TW": float(remainder.max()),
        }
    baseline = summary["adjacent_mean"]["time_weighted_advective_convergence_TW_at_0C"]
    for method in METHODS:
        summary[method]["convergence_shift_from_adjacent_mean_TW"] = summary[method]["time_weighted_advective_convergence_TW_at_0C"] - baseline
    section_summary = {}
    for section_index, section in enumerate(control["sections"]):
        section_summary[section["id"]] = {
            method: float(np.average([-record["methods"][method]["sections"][section_index]["outward_heat_TW_at_0C"] for record in records], weights=weights))
            for method in METHODS
        }
    return {
        "schema": "osw.oras5.nordic-collocation-sensitivity.v1",
        "status": "four_rule_offline_boundary_tracer_sensitivity",
        "methods": {
            "adjacent_mean": "arithmetic mean of the two neighboring T cells",
            "upwind": "monthly-mean donor cell selected by the sign of native velocity",
            "inside_cell": "T cell on the Nordic-room side of each outward-signed face",
            "outside_cell": "T cell outside the Nordic room at each outward-signed face",
        },
        "months": records,
        "summary": summary,
        "time_weighted_section_convergence_TW_at_0C": section_summary,
        "checks": {
            "month_count": len(records),
            "method_count": len(METHODS),
            "adjacent_mean_matches_partial_budget": all(np.isclose(record["methods"]["adjacent_mean"]["advective_convergence_TW_at_0C"], -budget_record["boundary_totals"]["outward_heat_TW"]["0.0"]) for record, budget_record in zip(records, budget["months"])),
        },
        "sources": {"control": sha256_file(control_path), "mesh": sha256_file(mesh_path), "partial_budget": sha256_file(budget_path)},
        "boundary": "Tracer-to-face rules diagnose one offline numerical choice. All cases still multiply separate monthly-mean velocity and temperature, omit submonthly covariance, and do not reproduce native conservative tracer advection, mixing, diffusion, ice exchange, or assimilation increments.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path("."))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-collocation-sensitivity-2018.json"))
    args = parser.parse_args()
    result = analyze(args.root.resolve())
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
