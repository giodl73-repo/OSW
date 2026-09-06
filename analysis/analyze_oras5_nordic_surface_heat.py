"""Integrate native monthly surface heat flux over the closed Nordic Seas mask."""

from __future__ import annotations

import argparse
import calendar
import json
import pathlib

import netCDF4
import numpy as np

from fetch_oras5_drake_surface_heat import sha256_file


def analyze(control_path: pathlib.Path, metrics_path: pathlib.Path, heat_path: pathlib.Path) -> dict:
    control = json.loads(control_path.read_text(encoding="utf-8"))
    with netCDF4.Dataset(metrics_path) as dataset:
        area = np.asarray(dataset.variables["e1t"][:], dtype=float) * np.asarray(dataset.variables["e2t"][:], dtype=float)
    with netCDF4.Dataset(heat_path) as dataset:
        months = np.asarray(dataset.variables["month"][:], dtype=int)
        flux = np.ma.filled(dataset.variables["sohefldo"][:], np.nan).astype(float)
        units = getattr(dataset.variables["sohefldo"], "units", None)
    if flux.shape[1:] != area.shape:
        raise ValueError("surface heat and T-cell metric shapes differ")
    inside = np.zeros(area.shape, dtype=bool)
    indices = np.asarray(control["inside_t_cells"], dtype=int)
    inside[indices[:, 0], indices[:, 1]] = True
    room_area = float(area[inside].sum())
    records = []
    weighted_power = 0.0
    total_seconds = 0.0
    for month, field in zip(months, flux):
        valid = inside & np.isfinite(field)
        seconds = calendar.monthrange(int(month) // 100, int(month) % 100)[1] * 86400.0
        power = float(np.sum(field[valid] * area[valid]))
        records.append({
            "month": str(int(month)),
            "days": int(seconds / 86400),
            "valid_inside_cell_count": int(np.sum(valid)),
            "valid_area_fraction": float(area[valid].sum() / room_area),
            "area_mean_flux_W_m2": float(power / area[valid].sum()),
            "integrated_downward_power_TW": power / 1e12,
            "monthly_downward_energy_ZJ": power * seconds / 1e21,
        })
        weighted_power += power * seconds
        total_seconds += seconds
    annual_power = weighted_power / total_seconds
    return {
        "schema": "osw.oras5.nordic-surface-heat-analysis.v1",
        "status": "twelve_month_native_surface_flux_integrated_over_closed_room",
        "sign_convention": "positive downward into the ocean; negative means net ocean heat loss to the overlying system",
        "field_units": units,
        "inside_wet_t_cell_count": int(np.sum(inside)),
        "room_surface_area_m2": room_area,
        "months": records,
        "time_weighted_2018": {
            "area_mean_flux_W_m2": annual_power / room_area,
            "integrated_downward_power_TW": annual_power / 1e12,
            "net_downward_energy_ZJ": weighted_power / 1e21,
            "warming_month_count": sum(record["integrated_downward_power_TW"] > 0 for record in records),
            "cooling_month_count": sum(record["integrated_downward_power_TW"] < 0 for record in records),
        },
        "checks": {
            "month_count": len(records),
            "all_months_cover_complete_room": all(np.isclose(record["valid_area_fraction"], 1.0) for record in records),
            "control_cell_count_matches": int(np.sum(inside)) == control["topology"]["inside_wet_t_cell_count"],
        },
        "sources": {
            "control_volume": {"path": f"research/{control_path.name}", "sha256": sha256_file(control_path)},
            "t_metrics": {"path": f"atlas/data/{metrics_path.name}", "sha256": sha256_file(metrics_path)},
            "surface_heat": {"path": f"atlas/data/{heat_path.name}", "sha256": sha256_file(heat_path)},
        },
        "boundary": "One ORAS5 member and one year of monthly-mean reanalysis surface forcing. This is not a climatology, observation-only estimate, advective convergence, storage tendency, complete budget, causal attribution, or Arctic delivery.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-control-volume.json"))
    parser.add_argument("--metrics", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-nordic-t-metrics.nc"))
    parser.add_argument("--heat", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-nordic-surface-heat-2018.nc"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-surface-heat-2018.json"))
    args = parser.parse_args()
    result = analyze(args.control, args.metrics, args.heat)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}: {result['time_weighted_2018']['integrated_downward_power_TW']:+.1f} TW")


if __name__ == "__main__":
    main()
