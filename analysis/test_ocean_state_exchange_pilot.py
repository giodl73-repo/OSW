import json
import pathlib

import numpy as np

from analyze_ocean_state_exchange_pilot import CP0, RHO0, summarize_flux
from select_ocean_state_exchange_pilot import boundary_faces, displaced_control


ROOT = pathlib.Path(__file__).parent.parent


def test_native_face_sign_and_displaced_control_fixture():
    assignments = np.array([["A", "A", "B"], ["A", "B", "B"]])
    faces = boundary_faces(assignments)["A--B"]
    u = next(face for face in faces if face["face"] == "U" and face["y"] == 0)
    assert u["sign_first_to_second"] == 1
    assert displaced_control(u, "A", assignments) == {
        "face": "U", "y": 0, "x": 0, "sign_parallel_to_first_to_second": 1
    }
    v = next(face for face in faces if face["face"] == "V")
    assert v["sign_first_to_second"] == 1


def test_flux_components_and_reference_identity():
    q = np.array([2e6, -1e6])
    temperature = np.array([4.0, 3.0])
    at_zero = summarize_flux(q, temperature, 0.0)
    at_two = summarize_flux(q, temperature, 2.0)
    assert at_zero["positive_first_to_second_Sv"] == 2.0
    assert at_zero["negative_second_to_first_Sv"] == -1.0
    assert at_zero["gross_exchange_Sv"] == 3.0
    assert at_zero["net_first_to_second_Sv"] == 1.0
    expected_shift_pw = RHO0 * CP0 * 2.0 * np.sum(q) / 1e15
    assert np.isclose(at_two["net_first_to_second_PW"], at_zero["net_first_to_second_PW"] - expected_shift_pw)


def test_selection_record_is_complete_and_outcome_blind():
    payload = json.loads((ROOT / "research/ocean-state-exchange-pilot-selection-v1.json").read_text(encoding="utf-8"))
    assert payload["status"] == "pilot_selected_before_transport_outcomes"
    assert payload["candidate_source"]["candidate_count"] == len(payload["candidates"]) == 128
    assert payload["selected_edge"]["edge_id"] == "SANT--SSTC"
    assert payload["eligible_edge_count"] == 6
    assert len(payload["selected_face_pairs"]) == 16
    assert all(payload["selected_edge"]["eligibility"].values())
    assert {"velocity_magnitude", "transport_sign", "transport_magnitude", "temperature_contrast"}.issubset(payload["prohibited_selection_inputs"])


def test_exchange_record_passes_bounded_internal_gate():
    payload = json.loads((ROOT / "research/ocean-state-boundary-exchange-pilot-2018.json").read_text(encoding="utf-8"))
    assert payload["status"] == "stage_4_regional_native_grid_pilot_passes_internal_gates"
    assert payload["selection"]["selected_before_outcomes"] is True
    assert payload["geometry"]["measured_matched_face_count"] == 16
    assert len(payload["months"]) == 4
    assert payload["checks"]["missing_wet_values"] == 0
    assert payload["checks"]["maximum_volume_component_identity_residual_Sv"] < 1e-6
    assert payload["checks"]["maximum_reference_change_identity_residual_W"] < 1e8
    assert payload["checks"]["closure_scope"].startswith("open-edge transport only")
    assert payload["checks"]["product_sensitivity"].startswith("unsupported")
    assert payload["summary"]["seasonal_volume_sign_reversal"] is True
    assert payload["summary"]["seasonal_heat_sign_reversal_at_0C"] is False
    for month in payload["months"]:
        assert len(month["boundary"]["by_depth"]) == 4
        for depth in month["boundary"]["by_depth"]:
            cases = depth["reference_and_collocation_cases"]
            assert set(cases) == {"adjacent_mean", "upwind", "first_cell", "second_cell"}
            result = cases["adjacent_mean"]["0.0"]
            assert np.isclose(result["gross_exchange_Sv"], result["positive_first_to_second_Sv"] - result["negative_second_to_first_Sv"])


def test_exchange_browser_payload_matches_receipt():
    source = (ROOT / "exchange/exchange.js").read_text(encoding="utf-8")
    prefix = "window.OSW_EXCHANGE = "
    assert source.startswith(prefix) and source.endswith(";\n")
    browser = json.loads(source[len(prefix):-2])
    research = json.loads((ROOT / "research/ocean-state-boundary-exchange-pilot-2018.json").read_text(encoding="utf-8"))
    assert browser == research
