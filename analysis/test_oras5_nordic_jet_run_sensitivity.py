import pathlib

from analyze_oras5_nordic_jet_run_sensitivity import analyze


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_jet_run_sensitivity_exposes_scale_dependence() -> None:
    result = analyze(ROOT / "research/osw-m4-oras5-nordic-face-heat-map-2018.json")
    assert all(result["checks"].values())
    assert result["summary"]["run_counts"] == [95, 53, 36, 29]
    assert result["summary"]["single_face_run_counts"] == [51, 13, 6, 4]
    assert result["summary"]["leader_component_is_strongest_inward"] == [True, True, False, False]
    assert result["summary"]["distance_run_counts"] == [95, 47, 37, 29]
    assert result["summary"]["distance_single_face_run_counts"] == [51, 10, 7, 6]
    assert [item["agreement_face_count"] for item in result["summary"]["matched_face_distance_agreement"]] == [277, 278, 266]
    assert result["cases"][2]["strongest_inward_run"]["net_heat_convergence_TW_at_0C"] > 140
    assert "no scale is selected as uniquely correct" in result["boundary"]
