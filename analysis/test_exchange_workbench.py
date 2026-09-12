import json
import pathlib
import re


ROOT = pathlib.Path(__file__).parent.parent


def test_hydrography_browser_payload_matches_research_artifact():
    source = (ROOT / "exchange/hydrography.js").read_text(encoding="utf-8")
    match = re.fullmatch(r"window\.OSW_HYDROGRAPHY = (.*);\n?", source, re.DOTALL)
    assert match
    browser = json.loads(match.group(1))
    research = json.loads((ROOT / "research/ocean-state-hydrography-pilot-2018.json").read_text(encoding="utf-8"))
    assert browser == research


def test_exchange_inventory_view_has_accessible_equivalents_and_boundaries():
    html = (ROOT / "exchange/index.html").read_text(encoding="utf-8")
    script = (ROOT / "exchange/app.js").read_text(encoding="utf-8")
    responsive = (ROOT / "exchange/responsive.css").read_text(encoding="utf-8")
    for token in (
        'aria-live="polite"',
        'id="property-map"',
        'id="support-map"',
        'id="passport-grid"',
        'id="contrast-body"',
        'id="unsupported-list"',
        'id="state-body"',
        "Temperature distributions, not heat inventories",
    ):
        assert token in html
    for token in (
        "URLSearchParams",
        "history.replaceState",
        'setAttribute("aria-label"',
        "descriptive model screen",
        "coordinate_extent_deg",
        "inNativeDomain(sample)",
    ):
        assert token in script
    assert "overflow-x: hidden" in responsive
    assert ".table-wrap table" in responsive


def test_exchange_stage_has_accessible_tables_and_url_state():
    html = (ROOT / "exchange/index.html").read_text(encoding="utf-8")
    script = (ROOT / "exchange/exchange-stage.js").read_text(encoding="utf-8")
    for token in ('id="exchange-map"', 'id="exchange-score-grid"', 'id="depth-body"', 'id="season-body"', "one monthly mean"):
        assert token in html
    for token in ("setStage", "URLSearchParams", 'setAttribute("aria-label"', "matched_displaced_control"):
        assert token in script


def test_stability_stage_has_accessible_matrix_and_frozen_boundary():
    html = (ROOT / "exchange/index.html").read_text(encoding="utf-8")
    script = (ROOT / "exchange/stability-stage.js").read_text(encoding="utf-8")
    for token in ('id="stability-map"', 'id="stability-score-grid"', 'id="stability-matrix-body"', "not supported as a persistent temperature front"):
        assert token in html
    for token in ('setAttribute("aria-label"', "front_envelope_offsets_native_faces", "front_detected"):
        assert token in script


def test_events_stage_separates_route_from_transport():
    html = (ROOT / "exchange/index.html").read_text(encoding="utf-8")
    script = (ROOT / "exchange/events-stage.js").read_text(encoding="utf-8")
    for token in ('id="events-map"', 'id="events-sequence-body"', 'id="events-evidence-grid"', "dominant address stays put"):
        assert token in html
    for token in ('setAttribute("aria-label"', "province_crossing_candidate_count", "evidence_ladder"):
        assert token in script


def test_decisions_stage_exposes_complete_matrix_and_approval_boundary():
    html = (ROOT / "exchange/index.html").read_text(encoding="utf-8")
    script = (ROOT / "exchange/decisions-stage.js").read_text(encoding="utf-8")
    for token in ('id="decisions-map"', 'id="decision-matrix-body"', 'id="decision-edge-select"', "Owner approval, external scientific review"):
        assert token in html
    for token in ('setAttribute("aria-label"', "decisionsData.matrix.filter", "falsification_or_upgrade", "URLSearchParams"):
        assert token in script


def test_interior_stage_keeps_contents_context_and_unknowns_separate():
    html = (ROOT / "exchange/index.html").read_text(encoding="utf-8")
    stage = (ROOT / "exchange/interior-stage.js").read_text(encoding="utf-8")
    router = (ROOT / "exchange/exchange-stage.js").read_text(encoding="utf-8")
    for token in ('data-stage="interior"', 'id="interior-address-grid"', 'id="interior-contents-body"', 'id="interior-overlays"', 'id="interior-links"', 'id="interior-unknowns"', 'id="interior-boundary-context"'):
        assert token in html
    for token in ("not a dynamic-state diagnosis or a budget", "not evidence that the state has no features", "join_status"):
        assert token in stage
    assert "not_joined_to_interior_account" in (ROOT / "exchange/interior-ledger.js").read_text(encoding="utf-8")
    assert "showInterior" in router and '"interior"' in router
