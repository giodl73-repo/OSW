"""Estimate sparse heat-content tendency inside the primary native Drake control box."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib

import netCDF4
import numpy as np

try:
    from analyze_oras5_drake_control_box import BOUNDS, MONTHS, sha256_file
    from audit_nemo_face_thickness_reconstruction import reconstruct_t
except ModuleNotFoundError:
    from analysis.analyze_oras5_drake_control_box import BOUNDS, MONTHS, sha256_file
    from analysis.audit_nemo_face_thickness_reconstruction import reconstruct_t


DATES = {"201802": dt.datetime(2018, 2, 15, tzinfo=dt.timezone.utc), "201805": dt.datetime(2018, 5, 15, tzinfo=dt.timezone.utc), "201808": dt.datetime(2018, 8, 15, tzinfo=dt.timezone.utc), "201811": dt.datetime(2018, 11, 15, tzinfo=dt.timezone.utc)}
REFERENCES = (-1.9, 0.0, 5.0)
RHO = 1027.0
CP = 3992.0


def heat_content(temperature, cell_volume, reference=0.0, rho=RHO, cp=CP) -> float:
    temperature = np.asarray(temperature, dtype=float)
    cell_volume = np.asarray(cell_volume, dtype=float)
    if temperature.shape != cell_volume.shape:
        raise ValueError("temperature and cell volume must share shape")
    wet = cell_volume > 0
    if np.any(~np.isfinite(temperature[wet])) or np.any(~np.isfinite(cell_volume[wet])):
        raise ValueError("wet heat-content cells must be finite")
    return float((rho * cp * cell_volume[wet] * (temperature[wet] - reference)).sum())


def run(mesh_path: pathlib.Path, metrics_path: pathlib.Path, state_dir: pathlib.Path, control_box_path: pathlib.Path) -> dict:
    with netCDF4.Dataset(mesh_path) as dataset:
        reference = np.ma.filled(dataset.variables["e3t_0"][:], 0)
        mbathy = np.ma.filled(dataset.variables["mbathy"][:], 0)
        partial = np.ma.filled(dataset.variables["e3t_ps"][:], 0)
    with netCDF4.Dataset(metrics_path) as dataset:
        e1t = np.ma.filled(dataset.variables["e1t"][:], np.nan)
        e2t = np.ma.filled(dataset.variables["e2t"][:], np.nan)
    thickness, _ = reconstruct_t(reference, mbathy, partial)
    b = BOUNDS
    ys = slice(b["t_y_start"], b["t_y_stop_exclusive"])
    xs = slice(b["t_x_start"], b["t_x_stop_exclusive"])
    cell_volume = thickness[:, ys, xs] * (e1t[ys, xs] * e2t[ys, xs])[None, :, :]
    if np.any(~np.isfinite(cell_volume)) or np.any(cell_volume < 0):
        raise ValueError("control-box cell volume must be finite and nonnegative")
    control_box = json.loads(control_box_path.read_text(encoding="utf-8"))
    boundary_heat0 = {
        month["month"]: next(item["net_boundary_PW"] for item in month["net_outward_heat_PW"] if item["reference_temperature_degC"] == 0)
        for month in control_box["months"]
    }
    temperatures = {}
    contents = []
    state_sources = []
    for month in MONTHS:
        path = state_dir / f"oras5-drake-state-{month}.nc"
        with netCDF4.Dataset(path) as dataset:
            temperature = np.ma.filled(dataset.variables["votemper"][:, ys, xs], np.nan)
        temperatures[month] = temperature
        cases = [{"reference_temperature_degC": reference_value, "heat_content_EJ": heat_content(temperature, cell_volume, reference_value) / 1e18} for reference_value in REFERENCES]
        contents.append({
            "month": month, "representative_date": DATES[month].date().isoformat(),
            "volume_weighted_temperature_degC": float((temperature[cell_volume > 0] * cell_volume[cell_volume > 0]).sum() / cell_volume.sum()),
            "heat_content": cases,
        })
        state_sources.append({"month": month, "path": str(path), "sha256": sha256_file(path)})
    intervals = []
    wet_cells = cell_volume > 0
    for start, end in zip(MONTHS, MONTHS[1:]):
        seconds = (DATES[end] - DATES[start]).total_seconds()
        direct_tendency = RHO * CP * float((cell_volume[wet_cells] * (temperatures[end][wet_cells] - temperatures[start][wet_cells])).sum()) / seconds / 1e15
        reference_tendencies = []
        for reference_value in REFERENCES:
            start_content = heat_content(temperatures[start], cell_volume, reference_value)
            end_content = heat_content(temperatures[end], cell_volume, reference_value)
            reference_tendencies.append({"reference_temperature_degC": reference_value, "storage_tendency_PW": (end_content - start_content) / seconds / 1e15})
        boundary_mean = .5 * (boundary_heat0[start] + boundary_heat0[end])
        intervals.append({
            "start_month": start, "end_month": end, "days_between_representative_dates": seconds / 86400,
            "storage_tendency_PW": direct_tendency,
            "reference_tendency_audit": reference_tendencies,
            "endpoint_mean_net_outward_advective_heat_PW_at_0C": boundary_mean,
            "unclosed_tendency_plus_advective_divergence_PW": direct_tendency + boundary_mean,
        })
    return {
        "schema": "oceanlines.osw.m4-drake-storage-probe.v1", "status": "sparse endpoint heat-content tendency probe",
        "geometry": {"bounds": BOUNDS, "wet_t_cell_count": int(np.count_nonzero(cell_volume)), "box_volume_m3": float(cell_volume.sum())},
        "heat_content": contents, "intervals": intervals,
        "sources": {
            "mesh": {"path": str(mesh_path), "sha256": sha256_file(mesh_path)},
            "t_metrics": {"path": str(metrics_path), "sha256": sha256_file(metrics_path)},
            "states": state_sources,
            "control_box": {"path": str(control_box_path), "sha256": sha256_file(control_box_path)},
        },
        "boundary": "Heat content uses constant density/heat capacity and native T-cell area/partial thickness. Three tendencies connect sparse monthly-mean representative dates and compare only with endpoint-average offline advective divergence. This is not a time-integrated model budget, closure residual, surface-flux estimate, mixing estimate, causal attribution, or Antarctic heat delivery.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-drake-mesh.nc"))
    parser.add_argument("--t-metrics", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-drake-t-metrics.nc"))
    parser.add_argument("--state-dir", type=pathlib.Path, default=pathlib.Path("atlas/data"))
    parser.add_argument("--control-box", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-drake-control-box-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-drake-storage-probe-2018.json"))
    args = parser.parse_args()
    result = run(args.mesh, args.t_metrics, args.state_dir, args.control_box)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
