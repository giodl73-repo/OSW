"""Build a twelve-month compact native Drake storage/advection budget probe."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib

import netCDF4
import numpy as np

try:
    from analyze_oras5_drake_control_box import BOUNDS, REFERENCES, boundary_transport, sha256_file
    from analyze_oras5_drake_storage_probe import RHO, CP, heat_content
    from audit_nemo_face_thickness_reconstruction import reconstruct_t
except ModuleNotFoundError:
    from analysis.analyze_oras5_drake_control_box import BOUNDS, REFERENCES, boundary_transport, sha256_file
    from analysis.analyze_oras5_drake_storage_probe import RHO, CP, heat_content
    from analysis.audit_nemo_face_thickness_reconstruction import reconstruct_t


MONTHS = tuple(f"2018{month:02d}" for month in range(1, 13))
DATES = {month: dt.datetime(2018, int(month[4:]), 15, tzinfo=dt.timezone.utc) for month in MONTHS}


def calculate_compact(mesh: dict, state: dict, cell_volume: np.ndarray, month: str) -> dict:
    b = BOUNDS
    thickness, _ = reconstruct_t(mesh["e3t_0"], mesh["mbathy"], mesh["e3t_ps"])
    u_thickness = np.minimum(thickness[:, :, :-1], thickness[:, :, 1:])
    v_thickness = np.minimum(thickness[:, :-1, :], thickness[:, 1:, :])
    t = state["votemper"]; u = state["vozocrtx"]; v = state["vomecrty"]
    definitions = (
        ("west", u[:, :, 0], .5 * (t[:, 1:87, 0] + t[:, 1:87, 1]), u_thickness[:, 54:140, 56], mesh["e2u"][54:140, 56], mesh["umask"][:, 54:140, 56], -1),
        ("east", u[:, :, 16], .5 * (t[:, 1:87, 16] + t[:, 1:87, 17]), u_thickness[:, 54:140, 72], mesh["e2u"][54:140, 72], mesh["umask"][:, 54:140, 72], 1),
        ("south", v[:, 0, :], .5 * (t[:, 0, 1:17] + t[:, 1, 1:17]), v_thickness[:, 53, 57:73], mesh["e1v"][53, 57:73], mesh["vmask"][:, 53, 57:73], -1),
        ("north", v[:, 86, :], .5 * (t[:, 86, 1:17] + t[:, 87, 1:17]), v_thickness[:, 139, 57:73], mesh["e1v"][139, 57:73], mesh["vmask"][:, 139, 57:73], 1),
    )
    boundaries = []
    for name, velocity, temperature, face_thickness, width, mask, sign in definitions:
        item = boundary_transport(velocity, temperature, face_thickness, width, mask, sign)
        item["name"] = name
        boundaries.append(item)
    volume = sum(item["volume_Sv"] for item in boundaries)
    heat_cases = [{
        "reference_temperature_degC": reference,
        "net_outward_PW": sum(next(case["net_PW"] for case in boundary["heat_transport_PW"] if case["reference_temperature_degC"] == reference) for boundary in boundaries),
    } for reference in REFERENCES]
    interior_temperature = t[:, 1:87, 1:17]
    wet = cell_volume > 0
    contents = [{"reference_temperature_degC": reference, "heat_content_EJ": heat_content(interior_temperature, cell_volume, reference) / 1e18} for reference in REFERENCES]
    return {
        "month": month, "representative_date": DATES[month].date().isoformat(), "boundaries": boundaries,
        "net_outward_volume_Sv": volume, "net_outward_heat_PW": heat_cases,
        "volume_weighted_temperature_degC": float((interior_temperature[wet] * cell_volume[wet]).sum() / cell_volume.sum()),
        "heat_content": contents,
    }


def run(mesh_path: pathlib.Path, metrics_path: pathlib.Path, budget_state_dir: pathlib.Path, control_box_path: pathlib.Path, storage_probe_path: pathlib.Path) -> dict:
    with netCDF4.Dataset(mesh_path) as dataset:
        mesh = {name: np.ma.filled(dataset.variables[name][:], 0) for name in ("e3t_0", "mbathy", "e3t_ps", "umask", "vmask", "e2u", "e1v")}
    with netCDF4.Dataset(metrics_path) as dataset:
        area = np.ma.filled(dataset.variables["e1t"][:], np.nan) * np.ma.filled(dataset.variables["e2t"][:], np.nan)
    thickness, _ = reconstruct_t(mesh["e3t_0"], mesh["mbathy"], mesh["e3t_ps"])
    cell_volume = thickness[:, 54:140, 57:73] * area[54:140, 57:73][None, :, :]
    monthly = []
    state_sources = []
    temperatures = {}
    for month in MONTHS:
        path = budget_state_dir / f"oras5-drake-budget-state-{month}.nc"
        with netCDF4.Dataset(path) as dataset:
            state = {name: np.ma.filled(dataset.variables[name][:], np.nan) for name in ("votemper", "vozocrtx", "vomecrty")}
        monthly.append(calculate_compact(mesh, state, cell_volume, month))
        temperatures[month] = state["votemper"][:, 1:87, 1:17]
        state_sources.append({"month": month, "path": str(path), "sha256": sha256_file(path)})
    intervals = []
    wet = cell_volume > 0
    for start, end in zip(MONTHS, MONTHS[1:]):
        seconds = (DATES[end] - DATES[start]).total_seconds()
        storage = RHO * CP * float((cell_volume[wet] * (temperatures[end][wet] - temperatures[start][wet])).sum()) / seconds / 1e15
        start_month = next(item for item in monthly if item["month"] == start)
        end_month = next(item for item in monthly if item["month"] == end)
        advective = .5 * (
            next(item["net_outward_PW"] for item in start_month["net_outward_heat_PW"] if item["reference_temperature_degC"] == 0)
            + next(item["net_outward_PW"] for item in end_month["net_outward_heat_PW"] if item["reference_temperature_degC"] == 0)
        )
        intervals.append({"start_month": start, "end_month": end, "days": seconds / 86400, "storage_tendency_PW": storage, "endpoint_mean_net_outward_advective_heat_PW_at_0C": advective, "unclosed_PW": storage + advective})
    total_seconds = (DATES[MONTHS[-1]] - DATES[MONTHS[0]]).total_seconds()
    weighted_advective_energy = sum(item["endpoint_mean_net_outward_advective_heat_PW_at_0C"] * item["days"] * 86400 for item in intervals)
    span = {
        "start": DATES[MONTHS[0]].date().isoformat(), "end": DATES[MONTHS[-1]].date().isoformat(), "days": total_seconds / 86400,
        "mean_storage_tendency_PW": sum(item["storage_tendency_PW"] * item["days"] for item in intervals) / sum(item["days"] for item in intervals),
        "time_weighted_mean_outward_advective_heat_PW_at_0C": weighted_advective_energy / total_seconds,
    }
    span["mean_unclosed_PW"] = span["mean_storage_tendency_PW"] + span["time_weighted_mean_outward_advective_heat_PW_at_0C"]
    control_box = json.loads(control_box_path.read_text(encoding="utf-8"))
    storage_probe = json.loads(storage_probe_path.read_text(encoding="utf-8"))
    anchors = []
    for month in ("201802", "201805", "201808", "201811"):
        compact = next(item for item in monthly if item["month"] == month)
        full_boundary = next(item for item in control_box["months"] if item["month"] == month)
        full_storage = next(item for item in storage_probe["heat_content"] if item["month"] == month)
        anchors.append({
            "month": month,
            "volume_residual_Sv": compact["net_outward_volume_Sv"] - full_boundary["net_outward_volume_Sv"],
            "heat_0C_residual_PW": next(item["net_outward_PW"] for item in compact["net_outward_heat_PW"] if item["reference_temperature_degC"] == 0) - next(item["net_boundary_PW"] for item in full_boundary["net_outward_heat_PW"] if item["reference_temperature_degC"] == 0),
            "temperature_residual_degC": compact["volume_weighted_temperature_degC"] - full_storage["volume_weighted_temperature_degC"],
        })
    return {
        "schema": "oceanlines.osw.m4-drake-monthly-budget.v1", "status": "twelve-month compact native storage/advection probe",
        "monthly": monthly, "intervals": intervals, "sampled_span": span, "four_month_anchor_audit": anchors,
        "sources": {"mesh": {"path": str(mesh_path), "sha256": sha256_file(mesh_path)}, "t_metrics": {"path": str(metrics_path), "sha256": sha256_file(metrics_path)}, "budget_states": state_sources, "control_box": {"path": str(control_box_path), "sha256": sha256_file(control_box_path)}, "storage_probe": {"path": str(storage_probe_path), "sha256": sha256_file(storage_probe_path)}},
        "boundary": "Twelve monthly means support eleven adjacent-month storage differences and trapezoidal endpoint advection over 15 January–15 December 2018. This is denser sampling, not a complete time-integrated model budget; surface/ice fluxes, mixing, diffusion, and native tracer tendencies remain absent.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-drake-mesh.nc"))
    parser.add_argument("--t-metrics", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-drake-t-metrics.nc"))
    parser.add_argument("--budget-state-dir", type=pathlib.Path, default=pathlib.Path("atlas/data"))
    parser.add_argument("--control-box", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-drake-control-box-2018.json"))
    parser.add_argument("--storage-probe", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-drake-storage-probe-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-drake-monthly-budget-2018.json"))
    args = parser.parse_args()
    result = run(args.mesh, args.t_metrics, args.budget_state_dir, args.control_box, args.storage_probe)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
