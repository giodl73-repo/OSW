import pathlib

import numpy as np

from analyze_oras5_nordic_heat_exchange_anatomy import analyze


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_heat_exchange_anatomy_is_complete_and_matches_upwind_total() -> None:
    result = analyze(ROOT)
    assert result["checks"]["month_count"] == 12
    assert result["checks"]["section_count"] == 5
    assert result["checks"]["all_branches_positive"]
    assert result["checks"]["all_depth_bins_reproduce_section_heat"]
    assert len(result["depth_bins_m"]) == 6
    assert all(len(section["depth_bins"]) == 6 for section in result["time_weighted_2018"])
    assert np.isclose(result["checks"]["net_convergence_sum_TW"], 139.8185219599363)
    assert all(section["inward_heat_TW_at_0C"] >= 0 for section in result["time_weighted_2018"])
    assert "not ORAS5 native" in result["boundary"]
