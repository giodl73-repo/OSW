"""Screen monthly timing among southern input, northern export, surface forcing, and storage."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib

import numpy as np


SOUTH = ("denmark_strait", "iceland_scotland_ridge", "northern_north_sea")
NORTH = ("fram_strait", "norway_svalbard")


def sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def correlation(first, second) -> float:
    return float(np.corrcoef(first, second)[0, 1])


def analyze(anatomy_path: pathlib.Path, budget_path: pathlib.Path) -> dict:
    anatomy = json.loads(anatomy_path.read_text(encoding="utf-8"))
    budget = json.loads(budget_path.read_text(encoding="utf-8"))
    months = []
    for exchange, state in zip(anatomy["months"], budget["months"]):
        assert exchange["month"] == state["month"]
        gates = {section["id"]: section["net_heat_convergence_TW_at_0C"] for section in exchange["sections"]}
        southern = sum(gates[key] for key in SOUTH)
        northern = -sum(gates[key] for key in NORTH)
        surface = state["surface_downward_TW"]
        storage = state["storage_tendency_TW"]["0.0"]
        months.append({
            "month": exchange["month"],
            "southern_gate_input_TW": southern,
            "northern_gate_export_TW": northern,
            "net_upwind_boundary_convergence_TW": southern - northern,
            "surface_downward_TW": surface,
            "storage_tendency_TW": storage,
            "upwind_consistent_unresolved_remainder_TW": storage - (southern - northern) - surface,
        })
    fields = {key: np.asarray([month[key] for month in months]) for key in months[0] if key != "month"}
    circular = [correlation(fields["southern_gate_input_TW"], np.roll(fields["northern_gate_export_TW"], shift)) for shift in range(12)]
    zero = circular[0]
    return {
        "schema": "osw.oras5.nordic-heat-relay.v1",
        "status": "monthly_timing_screen",
        "definitions": {"southern_input": list(SOUTH), "northern_export": list(NORTH)},
        "months": months,
        "summary": {
            "same_month_correlations": {
                "southern_input_vs_northern_export": correlation(fields["southern_gate_input_TW"], fields["northern_gate_export_TW"]),
                "southern_input_vs_surface_downward": correlation(fields["southern_gate_input_TW"], fields["surface_downward_TW"]),
                "southern_input_vs_storage_tendency": correlation(fields["southern_gate_input_TW"], fields["storage_tendency_TW"]),
                "surface_downward_vs_storage_tendency": correlation(fields["surface_downward_TW"], fields["storage_tendency_TW"]),
            },
            "southern_to_northern_circular_shift_correlations": {str(shift): value for shift, value in enumerate(circular)},
            "same_month_is_strongest_circular_alignment": bool(zero == max(circular)),
            "mean_powers_TW": {key: float(np.mean(value)) for key, value in fields.items()},
        },
        "checks": {
            "twelve_matched_months": len(months) == 12,
            "relay_identity_closes": all(abs(month["storage_tendency_TW"] - month["net_upwind_boundary_convergence_TW"] - month["surface_downward_TW"] - month["upwind_consistent_unresolved_remainder_TW"]) < 1e-10 for month in months),
        },
        "sources": {"heat_exchange_anatomy": sha256_file(anatomy_path), "partial_budget": sha256_file(budget_path)},
        "boundary": "Correlations use twelve seasonally confounded monthly means from one ORAS5 member/year. Circular shifts are a timing contrast, not a null distribution. Same-month association does not establish parcel transit, causality, residence time, interannual persistence, or native tracer-budget closure.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--anatomy", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-heat-exchange-anatomy-2018.json"))
    parser.add_argument("--budget", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-partial-budget-2018.json"))
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("research/osw-m4-oras5-nordic-heat-relay-2018.json"))
    args = parser.parse_args()
    result = analyze(args.anatomy, args.budget)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
