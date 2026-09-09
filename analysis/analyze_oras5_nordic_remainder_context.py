"""Compare Nordic partial-budget remainder timing with ice and mixed-layer state."""

from __future__ import annotations

import argparse
import json
import pathlib

import netCDF4
import numpy as np

from fetch_oras5_drake_surface_heat import sha256_file


def weighted_mean(field: np.ndarray, area: np.ndarray, mask: np.ndarray) -> float:
    valid = mask & np.isfinite(field)
    if not np.any(valid):
        raise ValueError("no valid cells for area-weighted mean")
    return float(np.sum(field[valid] * area[valid]) / np.sum(area[valid]))


def correlation(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.corrcoef(left, right)[0, 1])


def analyze(root: pathlib.Path) -> dict:
    control_path = root / "research/osw-m4-oras5-nordic-control-volume.json"
    metrics_path = root / "atlas/data/oras5-nordic-t-metrics.nc"
    context_path = root / "atlas/data/oras5-nordic-seasonal-context-2018.nc"
    context_receipt_path = root / "research/osw-m4-oras5-nordic-seasonal-context-source-2018.json"
    budget_path = root / "research/osw-m4-oras5-nordic-partial-budget-2018.json"
    control = json.loads(control_path.read_text(encoding="utf-8"))
    budget = json.loads(budget_path.read_text(encoding="utf-8"))
    with netCDF4.Dataset(metrics_path) as dataset:
        area = np.asarray(dataset.variables["e1t"][:], dtype=float) * np.asarray(dataset.variables["e2t"][:], dtype=float)
    with netCDF4.Dataset(context_path) as dataset:
        months = [str(int(value)) for value in np.asarray(dataset.variables["month"][:])]
        concentration = np.ma.filled(dataset.variables["ileadfra"][:], np.nan).astype(float)
        thickness = np.ma.filled(dataset.variables["iicethic"][:], np.nan).astype(float)
        mixed_layer = np.ma.filled(dataset.variables["somxl010"][:], np.nan).astype(float)
    cells = np.asarray(control["inside_t_cells"], dtype=int)
    inside = np.zeros(area.shape, dtype=bool); inside[cells[:, 0], cells[:, 1]] = True
    if months != [record["month"] for record in budget["months"]]:
        raise ValueError("context and budget months differ")
    records = []
    for index, (month, budget_record) in enumerate(zip(months, budget["months"])):
        ice = concentration[index]
        thick = thickness[index]
        mld = mixed_layer[index]
        valid_ice = inside & np.isfinite(ice)
        if np.nanmin(ice[valid_ice]) < -1e-6 or np.nanmax(ice[valid_ice]) > 1.000001:
            raise ValueError(f"{month} ice concentration outside [0, 1]")
        if np.any(valid_ice & (ice > 0) & ~np.isfinite(thick)) or np.any(thick[valid_ice & np.isfinite(thick)] < 0):
            raise ValueError(f"{month} ice thickness is missing or negative where ice is present")
        safe_thickness = np.where(np.isfinite(thick), thick, 0.0)
        ice_volume = float(np.sum(area[valid_ice] * ice[valid_ice] * safe_thickness[valid_ice]))
        records.append({
            "month": month,
            "unresolved_remainder_TW": budget_record["unresolved_remainder_TW"]["0.0"],
            "advective_convergence_TW": -budget_record["boundary_totals"]["outward_heat_TW"]["0.0"],
            "surface_downward_TW": budget_record["surface_downward_TW"],
            "storage_tendency_TW": budget_record["storage_tendency_TW"]["0.0"],
            "area_mean_ice_concentration": weighted_mean(ice, area, inside),
            "ice_extent_fraction_at_15_percent": float(np.sum(area[valid_ice & (ice >= 0.15)]) / np.sum(area[inside])),
            "ice_volume_proxy_km3": ice_volume / 1e9,
            "area_mean_mixed_layer_depth_m": weighted_mean(mld, area, inside),
        })
    arrays = {key: np.asarray([record[key] for record in records], dtype=float) for key in records[0] if key != "month"}
    remainder = arrays["unresolved_remainder_TW"]
    relationships = {
        key: correlation(remainder, arrays[key])
        for key in ("area_mean_ice_concentration", "ice_extent_fraction_at_15_percent", "ice_volume_proxy_km3", "area_mean_mixed_layer_depth_m", "surface_downward_TW", "advective_convergence_TW", "storage_tendency_TW")
    }
    return {
        "schema": "osw.oras5.nordic-remainder-context.v1",
        "status": "twelve_month_same_room_context_comparison",
        "months": records,
        "zero_lag_pearson_correlation_with_remainder": relationships,
        "checks": {
            "month_count": len(records),
            "ice_concentration_bounds_pass": True,
            "all_values_finite": all(np.isfinite(value) for values in arrays.values() for value in values),
        },
        "sources": {
            "control": sha256_file(control_path),
            "metrics": sha256_file(metrics_path),
            "seasonal_context": sha256_file(context_path),
            "seasonal_context_receipt": sha256_file(context_receipt_path),
            "partial_budget": sha256_file(budget_path),
        },
        "boundary": "Exploratory zero-lag correlations across only twelve monthly means from one ORAS5 year. They are seasonally confounded, provide no uncertainty estimate, and do not establish causation. Correlations with storage, advection, and surface flux are additionally algebraically coupled because those terms define the remainder.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path("."))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-remainder-context-2018.json"))
    args = parser.parse_args()
    result = analyze(args.root.resolve())
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result["zero_lag_pearson_correlation_with_remainder"], indent=2))


if __name__ == "__main__":
    main()
