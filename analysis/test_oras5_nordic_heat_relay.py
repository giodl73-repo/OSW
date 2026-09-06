import pathlib

from analyze_oras5_nordic_heat_relay import analyze


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_nordic_heat_relay_screen_is_explicitly_limited() -> None:
    result = analyze(ROOT / "research/osw-m4-oras5-nordic-heat-exchange-anatomy-2018.json", ROOT / "research/osw-m4-oras5-nordic-partial-budget-2018.json")
    assert all(result["checks"].values())
    correlations = result["summary"]["same_month_correlations"]
    assert correlations["southern_input_vs_northern_export"] > 0.8
    assert correlations["southern_input_vs_storage_tendency"] < -0.6
    assert correlations["surface_downward_vs_storage_tendency"] > 0.95
    assert result["summary"]["same_month_is_strongest_circular_alignment"] is True
    assert "does not establish parcel transit" in result["boundary"]
