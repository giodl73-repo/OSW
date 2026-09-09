import json
import pathlib


ROOT = pathlib.Path(__file__).parent.parent


def load_result():
    return json.loads((ROOT / "research/ocean-state-zoning-evidence-matrix.json").read_text(encoding="utf-8"))


def test_policy_keeps_unknown_and_source_geography_safe():
    policy = json.loads((ROOT / "research/ocean-state-zoning-disposition-policy-v1.json").read_text(encoding="utf-8"))
    assert policy["status"] == "frozen_before_matrix_generation"
    assert policy["allowed_dispositions"] == ["retain", "merge", "split", "move", "demote", "unknown"]
    assert "Unknown is an intended result" in policy["boundary"]
    assert "No automated disposition deletes" in policy["reference_policy"]


def test_complete_matrix_has_only_bounded_evidence_dispositions():
    payload = load_result()
    assert payload["status"] == "stage_7_bounded_synthesis_complete_no_source_geography_revision"
    assert len(payload["matrix"]) == payload["summary"]["edge_count"] == 128
    assert payload["summary"]["disposition_counts"] == {"retain": 0, "merge": 0, "split": 0, "move": 0, "demote": 1, "unknown": 127}
    assert payload["candidate_revised_geography"]["source_geometry_changes"] == []
    assert payload["approval"]["publication"] == "not_authorized"
    assert all(item["rationale"] and item["decision_rule"] and item["falsification_or_upgrade"] for item in payload["matrix"])


def test_selected_and_event_edges_keep_claim_families_separate():
    payload = load_result()
    selected = next(item for item in payload["matrix"] if item["edge_id"] == "SANT--SSTC")
    assert selected["disposition"] == "demote"
    assert selected["stability"]["static_edge_match_fraction"] == 0
    assert selected["controls"]["temperature_front_static_advantage_fraction"] == 0
    assert selected["scope"].startswith("entire source edge remains reference geography")
    event = next(item for item in payload["matrix"] if item["edge_id"] == "GFST--NWCS")
    assert event["disposition"] == "unknown"
    assert event["event_route"]["status"] == "geometric_lineage_transition_only"
    assert event["event_route"]["heat_transport"] == "unsupported"


def test_every_edge_has_geometry_hypsometry_uncertainty_and_trace():
    for edge in load_result()["matrix"]:
        assert edge["geometry"]["status"] == "source_backed_reference_edge"
        assert edge["hypsometry"]["status"] == "sampled_global_depth_character_available"
        assert edge["uncertainty"]["status"] == "incomplete"
        assert edge["disposition"] in {"retain", "merge", "split", "move", "demote", "unknown"}


def test_decisions_browser_payload_matches_receipt():
    source = (ROOT / "exchange/decisions.js").read_text(encoding="utf-8")
    prefix = "window.OSW_DECISIONS = "
    assert source.startswith(prefix) and source.endswith(";\n")
    assert json.loads(source[len(prefix):-2]) == load_result()
