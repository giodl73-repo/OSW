import pathlib

from analyze_oras5_nordic_face_jet_runs import analyze


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_face_jet_runs_partition_and_recover_heat() -> None:
    result = analyze(ROOT / "research/osw-m4-oras5-nordic-face-heat-map-2018.json")
    assert all(result["checks"].values())
    assert result["summary"]["run_count"] == 95
    assert result["summary"]["single_face_run_count"] == 51
    assert result["summary"]["top_10_absolute_run_share"] > 0.5
    assert result["summary"]["top_10_same_sign_all_12_months_count"] == 10
    assert result["summary"]["strongest_inward_run"]["face_count"] == 4
    assert result["summary"]["strongest_outward_run"]["face_count"] == 33
    assert "not objectively identified currents" in result["boundary"]
