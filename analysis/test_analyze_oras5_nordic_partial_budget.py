import json
import pathlib

import numpy as np

import analyze_oras5_nordic_partial_budget as budget


ROOT = pathlib.Path(__file__).resolve().parents[1]
PAYLOAD = budget.analyze(ROOT)


def test_partial_budget_contains_twelve_months_and_five_sections() -> None:
    payload = PAYLOAD
    assert len(payload["months"]) == 12
    assert all(len(record["sections"]) == 5 for record in payload["months"])
    assert all(set(record["boundary_totals"]["outward_heat_TW"]) == {"-1.9", "0.0", "2.0", "5.0"} for record in payload["months"])


def test_remainder_identity_and_heat_reference_identity_hold() -> None:
    payload = PAYLOAD
    rho_cp = payload["constants"]["density_kg_m3"] * payload["constants"]["heat_capacity_J_kg_K"]
    for record in payload["months"]:
        for reference in ("-1.9", "0.0", "2.0", "5.0"):
            expected = record["storage_tendency_TW"][reference] + record["boundary_totals"]["outward_heat_TW"][reference] - record["surface_downward_TW"]
            assert np.isclose(record["unresolved_remainder_TW"][reference], expected)
        observed = record["boundary_totals"]["outward_heat_TW"]["5.0"] - record["boundary_totals"]["outward_heat_TW"]["0.0"]
        expected = -rho_cp * 5.0 * record["boundary_totals"]["outward_volume_Sv"] * 1e6 / 1e12
        assert np.isclose(observed, expected, rtol=0, atol=1e-5)


def test_committed_budget_matches_analysis() -> None:
    expected = PAYLOAD
    committed = json.loads((ROOT / "research/osw-m4-oras5-nordic-partial-budget-2018.json").read_text(encoding="utf-8"))
    assert committed == expected
