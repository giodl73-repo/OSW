import pathlib

from analyze_indonesian_gate_readiness import GATES, run, sha256_file


ROOT = pathlib.Path(__file__).parent.parent


def test_gate_audit_keeps_inflow_and_three_outflows_distinct():
    result = run(ROOT / "atlas/data/oscar-timeseries-indonesian-native-2018.js")
    assert result["period"]["fields"] == 71
    assert result["source"]["sha256"] == sha256_file(ROOT / result["source"]["path"])
    assert {gate["code"] for gate in result["gates"]} == {"MAK", "LIF", "LOM", "OMB", "TIM"}
    assert {gate["role"] for gate in result["gates"]} == {gate["role"] for gate in GATES}


def test_readiness_is_derived_from_minimum_finite_support():
    result = run(ROOT / "atlas/data/oscar-timeseries-indonesian-native-2018.js")
    for gate in result["gates"]:
        minimum = gate["finite_points_per_frame"]["minimum"]
        expected = "screenable_at_m2" if minimum >= 3 else "direction_only_underresolved" if minimum >= 1 else "not_screenable"
        assert gate["readiness"] == expected
        assert len(gate["seasons"]) == 4


def test_committed_gate_verdicts_preserve_resolution_failure():
    result = run(ROOT / "atlas/data/oscar-timeseries-indonesian-native-2018.js")
    verdicts = {gate["code"]: gate["verdict"] for gate in result["gates"]}
    assert verdicts == {"MAK": "surface_sign_conflict", "LIF": "surface_sign_conflict", "LOM": "direction_only_underresolved", "OMB": "direction_only_underresolved", "TIM": "usable_surface_hint"}
