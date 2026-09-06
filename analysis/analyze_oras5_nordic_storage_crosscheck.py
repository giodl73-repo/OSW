"""Compare reconstructed Nordic storage with archived ORAS5 column heat content."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib

import netCDF4
import numpy as np

from fetch_oras5_drake_surface_heat import sha256_file


def midpoint(month: str) -> dt.datetime:
    year, number = int(month[:4]), int(month[4:])
    start = dt.datetime(year, number, 1, tzinfo=dt.timezone.utc)
    stop = dt.datetime(year + (number == 12), 1 if number == 12 else number + 1, 1, tzinfo=dt.timezone.utc)
    return start + (stop - start) / 2


def analyze(root: pathlib.Path) -> dict:
    control_path = root / "research/osw-m4-oras5-nordic-control-volume.json"
    metrics_path = root / "atlas/data/oras5-nordic-t-metrics.nc"
    column_path = root / "atlas/data/oras5-nordic-column-heat-2018.nc"
    budget_path = root / "research/osw-m4-oras5-nordic-partial-budget-2018.json"
    source_path = root / "research/osw-m4-oras5-nordic-column-heat-source-2018.json"
    control = json.loads(control_path.read_text(encoding="utf-8"))
    budget = json.loads(budget_path.read_text(encoding="utf-8"))
    with netCDF4.Dataset(metrics_path) as metrics:
        area = np.asarray(metrics.variables["e1t"][:], dtype=float) * np.asarray(metrics.variables["e2t"][:], dtype=float)
    with netCDF4.Dataset(column_path) as dataset:
        months = [str(int(value)) for value in np.asarray(dataset.variables["month"][:])]
        column_heat = np.ma.filled(dataset.variables["sohtcbtm"][:], np.nan).astype(float)
        units = getattr(dataset.variables["sohtcbtm"], "units", None)
    cells = np.asarray(control["inside_t_cells"], dtype=int)
    inside = np.zeros(area.shape, dtype=bool)
    inside[cells[:, 0], cells[:, 1]] = True
    if column_heat.shape[1:] != area.shape:
        raise ValueError("column heat and T-cell metric shapes differ")
    totals = []
    for month, field in zip(months, column_heat):
        valid = inside & np.isfinite(field)
        if int(np.sum(valid)) != int(np.sum(inside)):
            raise ValueError(f"{month} column heat does not cover the complete room")
        totals.append(float(np.sum(field[valid] * area[valid])))
    times = [midpoint(month).timestamp() for month in months]
    native_tendency = []
    for index in range(len(months)):
        previous_index = max(0, index - 1)
        next_index = min(len(months) - 1, index + 1)
        native_tendency.append((totals[next_index] - totals[previous_index]) / (times[next_index] - times[previous_index]) / 1e12)
    reconstructed = np.asarray([record["storage_tendency_TW"]["0.0"] for record in budget["months"]], dtype=float)
    native = np.asarray(native_tendency, dtype=float)
    if months != [record["month"] for record in budget["months"]]:
        raise ValueError("column heat and partial budget months differ")
    records = []
    for month, native_value, reconstructed_value, budget_record in zip(months, native, reconstructed, budget["months"]):
        remainder = native_value + budget_record["boundary_totals"]["outward_heat_TW"]["0.0"] - budget_record["surface_downward_TW"]
        records.append({
            "month": month,
            "archived_column_storage_tendency_TW": float(native_value),
            "reconstructed_temperature_storage_tendency_TW": float(reconstructed_value),
            "storage_difference_TW": float(native_value - reconstructed_value),
            "remainder_with_archived_storage_TW": float(remainder),
        })
    differences = native - reconstructed
    weights = np.asarray([record["days"] for record in json.loads((root / "research/osw-m4-oras5-nordic-surface-heat-2018.json").read_text(encoding="utf-8"))["months"]], dtype=float)
    old_remainder = np.asarray([record["unresolved_remainder_TW"]["0.0"] for record in budget["months"]])
    new_remainder = np.asarray([record["remainder_with_archived_storage_TW"] for record in records])
    return {
        "schema": "osw.oras5.nordic-storage-crosscheck.v1",
        "status": "archived_column_heat_storage_compared_with_reconstructed_temperature_storage",
        "field": "sohtcbtm",
        "field_units": units,
        "months": records,
        "summary": {
            "storage_tendency_correlation": float(np.corrcoef(native, reconstructed)[0, 1]),
            "storage_tendency_rmse_TW": float(np.sqrt(np.mean(differences ** 2))),
            "maximum_absolute_storage_difference_TW": float(np.max(np.abs(differences))),
            "time_weighted_reconstructed_storage_TW": float(np.average(reconstructed, weights=weights)),
            "time_weighted_archived_column_storage_TW": float(np.average(native, weights=weights)),
            "time_weighted_original_remainder_TW": float(np.average(old_remainder, weights=weights)),
            "time_weighted_archived_storage_remainder_TW": float(np.average(new_remainder, weights=weights)),
        },
        "sources": {
            "control": sha256_file(control_path),
            "metrics": sha256_file(metrics_path),
            "column_heat": sha256_file(column_path),
            "column_heat_receipt": sha256_file(source_path),
            "partial_budget": sha256_file(budget_path),
        },
        "boundary": "The archived total-column heat-content field is an independent ORAS5 storage diagnostic. The revised remainder still uses offline monthly-mean velocity times adjacent-mean temperature and therefore is not model-native budget closure or attribution to mixing, ice, diffusion, or assimilation.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path("."))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-storage-crosscheck-2018.json"))
    args = parser.parse_args()
    result = analyze(args.root.resolve())
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
