"""Add native ORAS5 net downward surface heat flux to the M4 Drake budget probe."""

from __future__ import annotations

import argparse
import json
import pathlib

import netCDF4
import numpy as np

try:
    from analyze_oras5_drake_control_box import BOUNDS, sha256_file
except ModuleNotFoundError:
    from analysis.analyze_oras5_drake_control_box import BOUNDS, sha256_file


def integrate_surface_flux(flux_w_m2: np.ndarray, area_m2: np.ndarray) -> np.ndarray:
    if flux_w_m2.ndim != 3 or area_m2.ndim != 2 or flux_w_m2.shape[1:] != area_m2.shape:
        raise ValueError(f"surface flux {flux_w_m2.shape} and area {area_m2.shape} do not align")
    return np.nansum(flux_w_m2 * area_m2[None, :, :], axis=(1, 2)) / 1e15


def run(monthly_budget_path: pathlib.Path, surface_path: pathlib.Path, metrics_path: pathlib.Path, surface_receipt_path: pathlib.Path) -> dict:
    budget = json.loads(monthly_budget_path.read_text(encoding="utf-8"))
    receipt = json.loads(surface_receipt_path.read_text(encoding="utf-8"))
    with netCDF4.Dataset(surface_path) as dataset:
        flux = np.ma.filled(dataset.variables["sohefldo"][:], np.nan)
        months = [str(value) for value in dataset.variables["month"][:]]
        flux_metadata = {
            "units": getattr(dataset.variables["sohefldo"], "units", None),
            "long_name": getattr(dataset.variables["sohefldo"], "long_name", None),
            "standard_name": getattr(dataset.variables["sohefldo"], "standard_name", None),
        }
    with netCDF4.Dataset(metrics_path) as dataset:
        area = np.ma.filled(dataset.variables["e1t"][:], np.nan) * np.ma.filled(dataset.variables["e2t"][:], np.nan)
    box_area = area[BOUNDS["t_y_start"]:BOUNDS["t_y_stop_exclusive"], BOUNDS["t_x_start"]:BOUNDS["t_x_stop_exclusive"]]
    monthly_surface = integrate_surface_flux(flux, box_area)
    expected_months = [item["month"] for item in budget["monthly"]]
    if months != expected_months:
        raise ValueError(f"surface months {months} != budget months {expected_months}")

    monthly = []
    valid_areas = [float(np.nansum(box_area[np.isfinite(month_flux)])) for month_flux in flux]
    for month, power, valid_area in zip(months, monthly_surface, valid_areas):
        monthly.append({
            "month": month,
            "net_downward_surface_heat_PW": float(power),
            "wet_surface_area_m2": valid_area,
            "area_mean_net_downward_surface_heat_W_m2": float(power * 1e15 / valid_area),
        })

    intervals = []
    for index, original in enumerate(budget["intervals"]):
        surface = .5 * (monthly_surface[index] + monthly_surface[index + 1])
        after_surface = original["unclosed_PW"] - surface
        intervals.append({
            **original,
            "endpoint_mean_net_downward_surface_heat_PW": float(surface),
            "remaining_after_surface_heat_PW": float(after_surface),
            "surface_fraction_of_pre_surface_remainder": float(surface / original["unclosed_PW"]),
        })

    total_days = sum(item["days"] for item in intervals)
    mean_surface = sum(item["endpoint_mean_net_downward_surface_heat_PW"] * item["days"] for item in intervals) / total_days
    original_span = budget["sampled_span"]
    span = {
        **original_span,
        "time_weighted_mean_net_downward_surface_heat_PW": mean_surface,
        "mean_remaining_after_surface_heat_PW": original_span["mean_unclosed_PW"] - mean_surface,
        "surface_fraction_of_pre_surface_remainder": mean_surface / original_span["mean_unclosed_PW"],
    }
    return {
        "schema": "oceanlines.osw.m4-drake-surface-budget.v1",
        "status": "native_surface_heat_added_to_offline_storage_advection_probe",
        "monthly_surface_heat": monthly,
        "intervals": intervals,
        "sampled_span": span,
        "common_wet_surface_area_m2": min(valid_areas),
        "field_metadata": flux_metadata,
        "sources": {
            "monthly_budget": {"path": str(monthly_budget_path), "sha256": sha256_file(monthly_budget_path)},
            "surface_heat": {"path": str(surface_path), "sha256": sha256_file(surface_path)},
            "surface_receipt": {"path": str(surface_receipt_path), "sha256": sha256_file(surface_receipt_path)},
            "t_metrics": {"path": str(metrics_path), "sha256": sha256_file(metrics_path)},
            "remote_sources": receipt["sources"],
        },
        "equation": "remaining = storage tendency + net outward advective heat transport - net downward surface heat flux",
        "boundary": "The native monthly ORAS5 sohefldo term reduces the offline remainder but does not close or attribute it. Monthly means and endpoint trapezoids are not model-native time-integrated diagnostics. Ice-ocean exchange, mixing, diffusion, freshwater/reference-temperature effects, assimilation increments, and other tracer-budget terms remain unresolved; ORAS5 surface restoring is part of the reanalysis context.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--monthly-budget", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-drake-monthly-budget-2018.json"))
    parser.add_argument("--surface", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-drake-surface-heat-2018.nc"))
    parser.add_argument("--t-metrics", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-drake-t-metrics.nc"))
    parser.add_argument("--surface-receipt", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-drake-surface-heat-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-drake-surface-budget-2018.json"))
    args = parser.parse_args()
    result = run(args.monthly_budget, args.surface, args.t_metrics, args.surface_receipt)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
