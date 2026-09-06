"""Calculate monthly storage, five-boundary advection, surface input, and remainder."""

from __future__ import annotations

import argparse
import calendar
import datetime as dt
import json
import pathlib

import netCDF4
import numpy as np

from audit_nemo_face_thickness_reconstruction import reconstruct_t
from fetch_oras5_arctic_state_subset import sha256_file


RHO0 = 1027.0
CP0 = 3992.0
REFERENCES = (-1.9, 0.0, 2.0, 5.0)
MONTHS = tuple(f"2018{month:02d}" for month in range(1, 13))


def midpoint(month: str) -> dt.datetime:
    year, number = int(month[:4]), int(month[4:])
    start = dt.datetime(year, number, 1, tzinfo=dt.timezone.utc)
    stop = dt.datetime(year + (number == 12), 1 if number == 12 else number + 1, 1, tzinfo=dt.timezone.utc)
    return start + (stop - start) / 2


def local_value(field, y, x):
    return field[:, y - int(field.local_y_start), x - int(field.local_x_start)]


def load_state(path: pathlib.Path):
    dataset = netCDF4.Dataset(path)
    return dataset


def analyze(root: pathlib.Path) -> dict:
    control_path = root / "research/osw-m4-oras5-nordic-control-volume.json"
    mesh_path = root / "atlas/data/oras5-nordic-seas-mesh.nc"
    metrics_path = root / "atlas/data/oras5-nordic-t-metrics.nc"
    surface_path = root / "research/osw-m4-oras5-nordic-surface-heat-2018.json"
    control = json.loads(control_path.read_text(encoding="utf-8"))
    surface = json.loads(surface_path.read_text(encoding="utf-8"))
    surface_by_month = {record["month"]: record for record in surface["months"]}
    with netCDF4.Dataset(mesh_path) as mesh:
        reference = np.asarray(mesh.variables["e3t_0"][:], dtype=float)
        thickness, _ = reconstruct_t(reference, np.asarray(mesh.variables["mbathy"][:]), np.asarray(mesh.variables["e3t_ps"][:]))
        umask = np.asarray(mesh.variables["umask"][:], dtype=bool)
        vmask = np.asarray(mesh.variables["vmask"][:], dtype=bool)
        e2u = np.asarray(mesh.variables["e2u"][:], dtype=float)
        e1v = np.asarray(mesh.variables["e1v"][:], dtype=float)
    with netCDF4.Dataset(metrics_path) as metrics:
        t_area = np.asarray(metrics.variables["e1t"][:], dtype=float) * np.asarray(metrics.variables["e2t"][:], dtype=float)
    cells = np.asarray(control["inside_t_cells"], dtype=int)
    storage_heat = []
    records = []
    source_receipts = []
    for month in MONTHS:
        state_path = root / f"atlas/data/oras5-nordic-budget-state-{month}.nc"
        receipt_path = root / f"research/osw-m4-oras5-nordic-budget-state-{month}.json"
        source_receipts.append({"month": month, "path": f"research/{receipt_path.name}", "sha256": sha256_file(receipt_path), "state_sha256": sha256_file(state_path)})
        with load_state(state_path) as state:
            temperature = state.variables["votemper"]
            temp_columns = np.stack([np.ma.filled(local_value(temperature, y, x), np.nan) for y, x in cells], axis=1)
            volumes = thickness[:, cells[:, 0], cells[:, 1]] * t_area[cells[:, 0], cells[:, 1]][None, :]
            wet = volumes > 0
            if np.any(~np.isfinite(temp_columns[wet])):
                raise ValueError(f"{month} has missing wet interior temperature")
            heat_cases = {str(reference_temp): float(RHO0 * CP0 * np.sum((temp_columns[wet] - reference_temp) * volumes[wet])) for reference_temp in REFERENCES}
            storage_heat.append(heat_cases)
            section_records = []
            for section in control["sections"]:
                volume_fluxes = []
                temperatures = []
                wet_cells = []
                for face in section["faces"]:
                    y, x = int(face["y"]), int(face["x"])
                    sign = int(face["sign_outward_from_nordic_seas"])
                    if face["face"] == "U":
                        velocity = np.ma.filled(local_value(state.variables["vozocrtx"], y, x), np.nan)
                        face_thickness = np.minimum(thickness[:, y, x], thickness[:, y, x + 1])
                        face_wet = umask[:, y, x]
                        width = e2u[y, x]
                        tracer = 0.5 * (np.ma.filled(local_value(temperature, y, x), np.nan) + np.ma.filled(local_value(temperature, y, x + 1), np.nan))
                    else:
                        velocity = np.ma.filled(local_value(state.variables["vomecrty"], y, x), np.nan)
                        face_thickness = np.minimum(thickness[:, y, x], thickness[:, y + 1, x])
                        face_wet = vmask[:, y, x]
                        width = e1v[y, x]
                        tracer = 0.5 * (np.ma.filled(local_value(temperature, y, x), np.nan) + np.ma.filled(local_value(temperature, y + 1, x), np.nan))
                    if np.any(~np.isfinite(velocity[face_wet])) or np.any(~np.isfinite(tracer[face_wet])):
                        raise ValueError(f"{month} {section['id']} has missing wet state")
                    volume_fluxes.append(sign * velocity * face_thickness * width)
                    temperatures.append(tracer)
                    wet_cells.append(face_wet)
                q = np.asarray(volume_fluxes).T
                theta = np.asarray(temperatures).T
                face_wet = np.asarray(wet_cells).T
                q = np.where(face_wet, q, 0.0)
                theta = np.where(face_wet, theta, 0.0)
                section_records.append({
                    "id": section["id"],
                    "outward_volume_Sv": float(np.sum(q) / 1e6),
                    "outward_positive_branch_Sv": float(np.sum(q[q > 0]) / 1e6),
                    "inward_negative_branch_Sv": float(np.sum(q[q < 0]) / 1e6),
                    "outward_heat_TW": {str(reference_temp): float(RHO0 * CP0 * np.sum((theta - reference_temp) * q) / 1e12) for reference_temp in REFERENCES},
                })
        totals = {
            "outward_volume_Sv": float(sum(section["outward_volume_Sv"] for section in section_records)),
            "outward_heat_TW": {str(reference_temp): float(sum(section["outward_heat_TW"][str(reference_temp)] for section in section_records)) for reference_temp in REFERENCES},
        }
        records.append({"month": month, "sections": section_records, "boundary_totals": totals, "surface_downward_TW": surface_by_month[month]["integrated_downward_power_TW"]})
    times = [midpoint(month).timestamp() for month in MONTHS]
    for index, record in enumerate(records):
        previous_index = max(0, index - 1); next_index = min(len(records) - 1, index + 1)
        seconds = times[next_index] - times[previous_index]
        record["storage_tendency_TW"] = {
            str(reference_temp): (storage_heat[next_index][str(reference_temp)] - storage_heat[previous_index][str(reference_temp)]) / seconds / 1e12
            for reference_temp in REFERENCES
        }
        record["unresolved_remainder_TW"] = {
            str(reference_temp): record["storage_tendency_TW"][str(reference_temp)] + record["boundary_totals"]["outward_heat_TW"][str(reference_temp)] - record["surface_downward_TW"]
            for reference_temp in REFERENCES
        }
        record["storage_derivative"] = "one-sided adjacent-month mean difference" if index in (0, len(records) - 1) else "centered adjacent-month mean difference"
    volume = np.array([record["boundary_totals"]["outward_volume_Sv"] for record in records])
    return {
        "schema": "osw.oras5.nordic-partial-budget.v1",
        "status": "twelve_month_offline_partial_budget_with_unresolved_remainder",
        "sign_convention": "boundary positive outward; surface positive downward into ocean; storage positive warming; storage + outward advection - downward surface = unresolved remainder",
        "constants": {"density_kg_m3": RHO0, "heat_capacity_J_kg_K": CP0, "reference_temperatures_degC": list(REFERENCES)},
        "storage_method": "fixed reconstructed native T-cell volume and monthly-mean potential temperature; finite differences between monthly-mean state midpoints",
        "advection_method": "monthly-mean native velocity times adjacent-mean monthly potential temperature on 284 faces; offline product, not model-native tracer advection",
        "months": records,
        "summary": {
            "outward_volume_Sv": {"minimum": float(volume.min()), "maximum": float(volume.max()), "mean": float(volume.mean())},
            "all_months_mass_imbalanced": bool(np.all(np.abs(volume) > 0.01)),
            "reference_dependence_is_material": bool(max(record["boundary_totals"]["outward_heat_TW"]["-1.9"] - record["boundary_totals"]["outward_heat_TW"]["5.0"] for record in records) > 10),
        },
        "sources": {"mesh": sha256_file(mesh_path), "metrics": sha256_file(metrics_path), "control": sha256_file(control_path), "surface_analysis": sha256_file(surface_path), "monthly_states": source_receipts},
        "boundary": "One ORAS5 member and one year. Monthly means, reconstructed partial steps, adjacent-mean tracers, and finite-difference storage do not reproduce the model-native conservative tracer budget. Ice, mixing, diffusion, assimilation, and numerical terms remain inside the unresolved remainder. This is not a climatology, uncertainty estimate, causal attribution, or Arctic delivery.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path("."))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-partial-budget-2018.json"))
    args = parser.parse_args()
    payload = analyze(args.root.resolve())
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: volume {payload['summary']['outward_volume_Sv']}")


if __name__ == "__main__":
    main()
