"""Test native ORAS5 surface water forcing against the M4 lateral volume residual."""

from __future__ import annotations

import argparse
import calendar
import json
import pathlib

import netCDF4
import numpy as np

try:
    from analyze_oras5_drake_control_box import BOUNDS, sha256_file
except ModuleNotFoundError:
    from analysis.analyze_oras5_drake_control_box import BOUNDS, sha256_file


RHO_REFERENCE_KG_M3 = 1026.0


def integrate_water_flux_sv(flux_kg_m2_s: np.ndarray, area_m2: np.ndarray, density_kg_m3: float = RHO_REFERENCE_KG_M3) -> np.ndarray:
    if density_kg_m3 <= 0:
        raise ValueError("reference density must be positive")
    if flux_kg_m2_s.ndim != 3 or area_m2.ndim != 2 or flux_kg_m2_s.shape[1:] != area_m2.shape:
        raise ValueError(f"surface water flux {flux_kg_m2_s.shape} and area {area_m2.shape} do not align")
    return np.nansum(flux_kg_m2_s * area_m2[None, :, :], axis=(1, 2)) / density_kg_m3 / 1e6


def run(monthly_budget_path: pathlib.Path, surface_water_path: pathlib.Path, metrics_path: pathlib.Path, receipt_path: pathlib.Path) -> dict:
    budget = json.loads(monthly_budget_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    with netCDF4.Dataset(surface_water_path) as dataset:
        flux = np.ma.filled(dataset.variables["sowaflup"][:], np.nan)
        months = [str(value) for value in dataset.variables["month"][:]]
        metadata = {
            "units": getattr(dataset.variables["sowaflup"], "units", None),
            "long_name": getattr(dataset.variables["sowaflup"], "long_name", None),
            "standard_name": getattr(dataset.variables["sowaflup"], "standard_name", None),
        }
    with netCDF4.Dataset(metrics_path) as dataset:
        area = np.ma.filled(dataset.variables["e1t"][:], np.nan) * np.ma.filled(dataset.variables["e2t"][:], np.nan)
    box_area = area[BOUNDS["t_y_start"]:BOUNDS["t_y_stop_exclusive"], BOUNDS["t_x_start"]:BOUNDS["t_x_stop_exclusive"]]
    surface_sv = integrate_water_flux_sv(flux, box_area)
    expected_months = [item["month"] for item in budget["monthly"]]
    if months != expected_months:
        raise ValueError(f"surface months {months} != budget months {expected_months}")

    monthly = []
    for month, surface, budget_month in zip(months, surface_sv, budget["monthly"]):
        lateral = budget_month["net_outward_volume_Sv"]
        monthly.append({
            "month": month,
            "net_outward_lateral_volume_Sv": lateral,
            "net_upward_surface_water_equivalent_Sv": float(surface),
            "lateral_plus_surface_residual_before_volume_storage_Sv": float(lateral + surface),
            "days": calendar.monthrange(int(month[:4]), int(month[4:]))[1],
        })
    total_days = sum(item["days"] for item in monthly)
    weighted = lambda key: sum(item[key] * item["days"] for item in monthly) / total_days
    lateral_mean = weighted("net_outward_lateral_volume_Sv")
    surface_mean = weighted("net_upward_surface_water_equivalent_Sv")
    remaining_mean = weighted("lateral_plus_surface_residual_before_volume_storage_Sv")
    return {
        "schema": "oceanlines.osw.m4-drake-surface-water.v1",
        "status": "native_surface_water_added_to_offline_lateral_volume_probe",
        "reference_density_kg_m3": RHO_REFERENCE_KG_M3,
        "monthly": monthly,
        "annual_weighted_summary": {
            "days": total_days,
            "mean_net_outward_lateral_volume_Sv": lateral_mean,
            "mean_net_upward_surface_water_equivalent_Sv": surface_mean,
            "mean_residual_before_volume_storage_Sv": remaining_mean,
            "absolute_mean_reduction_fraction": 1 - abs(remaining_mean) / abs(lateral_mean),
        },
        "field_metadata": metadata,
        "sources": {
            "monthly_budget": {"path": str(monthly_budget_path), "sha256": sha256_file(monthly_budget_path)},
            "surface_water": {"path": str(surface_water_path), "sha256": sha256_file(surface_water_path)},
            "surface_water_receipt": {"path": str(receipt_path), "sha256": sha256_file(receipt_path)},
            "t_metrics": {"path": str(metrics_path), "sha256": sha256_file(metrics_path)},
            "remote_sources": receipt["sources"],
        },
        "equation": "volume storage tendency + net outward lateral volume + net upward surface-water volume equivalent = 0",
        "boundary": "The comparison converts ORAS5 mass flux to a volume equivalent using a fixed 1026 kg/m3 reference density. It does not include free-surface/SSH volume storage, steric effects, sea-ice freshwater exchange beyond what is represented in sowaflup, or model-native volume-budget diagnostics. It is not heat transport.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--monthly-budget", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-drake-monthly-budget-2018.json"))
    parser.add_argument("--surface-water", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-drake-surface-water-2018.nc"))
    parser.add_argument("--t-metrics", type=pathlib.Path, default=pathlib.Path("atlas/data/oras5-drake-t-metrics.nc"))
    parser.add_argument("--surface-water-receipt", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-drake-surface-water-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-drake-surface-water-budget-2018.json"))
    args = parser.parse_args()
    result = run(args.monthly_budget, args.surface_water, args.t_metrics, args.surface_water_receipt)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
