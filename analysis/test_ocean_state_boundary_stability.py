import json
import pathlib

import numpy as np

from analyze_ocean_state_boundary_stability import diagnose, haversine_km


ROOT = pathlib.Path(__file__).parent.parent


def test_haversine_and_frozen_peak_diagnosis():
    assert np.isclose(haversine_km(0, 0, 1, 0), 111.195, atol=0.01)
    profile = [
        {"offset_native_faces": offset, "median_absolute_gradient_degC_per_km": value, "median_normal_face_spacing_km": 25.0}
        for offset, value in [(-2, 0.004), (-1, 0.006), (0, 0.010), (1, 0.005), (2, 0.004)]
    ]
    result = diagnose(profile, {"minimum_gradient_degC_per_km": 0.005, "minimum_peak_to_local_median_ratio": 1.25, "front_envelope_fraction_of_peak": 0.8, "static_match_maximum_absolute_offset_faces": 1})
    assert result["front_detected"] is True
    assert result["diagnosed_peak_offset_native_faces"] == 0
    assert result["static_edge_match"] is True


def test_stability_thresholds_are_outcome_blind():
    payload = json.loads((ROOT / "research/ocean-state-boundary-stability-thresholds-v1.json").read_text(encoding="utf-8"))
    assert payload["status"] == "frozen_before_stability_outcomes"
    assert payload["selected_edge"] == "SANT--SSTC"
    assert payload["diagnostic"]["normal_search_offsets_native_faces"] == list(range(-4, 5))
    assert "changing thresholds after viewing outcomes" in payload["prohibited_adjustments"]


def test_committed_stability_result_is_complete_and_negative():
    payload = json.loads((ROOT / "research/ocean-state-boundary-stability-pilot-2018.json").read_text(encoding="utf-8"))
    assert payload["status"] == "stage_5_single_year_temperature_gradient_test_complete"
    assert payload["thresholds"]["frozen_before_outcomes"] is True
    assert len(payload["records"]) == 16
    assert len(payload["season_summary"]) == 4
    assert payload["summary"]["temperature_front_disposition"] == "not_supported_as_persistent_temperature_front"
    assert payload["summary"]["interannual_stability"] == "unknown_single_year"
    assert not any(payload["summary"]["threshold_tests"].values())
    for record in payload["records"]:
        assert len(record["normal_gradient_profile"]) == 9
        assert -4 <= record["diagnosed_peak_offset_native_faces"] <= 4


def test_stability_browser_payload_matches_receipt():
    source = (ROOT / "exchange/stability.js").read_text(encoding="utf-8")
    prefix = "window.OSW_STABILITY = "
    assert source.startswith(prefix) and source.endswith(";\n")
    assert json.loads(source[len(prefix):-2]) == json.loads((ROOT / "research/ocean-state-boundary-stability-pilot-2018.json").read_text(encoding="utf-8"))
