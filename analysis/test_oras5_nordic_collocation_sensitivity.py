import pathlib

import numpy as np

from analyze_oras5_nordic_collocation_sensitivity import analyze


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_collocation_sensitivity_reproduces_baseline_and_is_complete() -> None:
    result = analyze(ROOT)
    assert result["checks"] == {"month_count": 12, "method_count": 4, "adjacent_mean_matches_partial_budget": True}
    assert set(result["summary"]) == {"adjacent_mean", "upwind", "inside_cell", "outside_cell"}
    assert result["summary"]["adjacent_mean"]["convergence_shift_from_adjacent_mean_TW"] == 0
    assert len(result["time_weighted_section_convergence_TW_at_0C"]) == 5
    assert all(np.isfinite(value) for method in result["summary"].values() for value in method.values())
    assert "omit submonthly covariance" in result["boundary"]
