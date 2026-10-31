"""Prospective synthetic support/promotion cases; no actual paper or facts loaded."""
import copy
import json
import xml.etree.ElementTree as ET

import pytest

from reported_current_width_evidence_v1 import NULL_FIELDS, SUPPORT, report_bytes, svg_bytes, validate


def synthetic():
    return {
        "schema": "osw.reported-current-width-evidence-facts.v1",
        "identity_status": "prepared_identity_pending_canonical_admission",
        "eligibility": {
            "canonical_identity_admitted": False, "canonical_width_admissions": 0,
            "new_independent_width_observations": 0, "width_ranking_eligible": False,
            "physical_seasonal_playback_eligible": False,
            **{k: None for k in NULL_FIELDS},
        },
        "source": {
            "access_scope": "retained_full_primary_article_selected_passages_reviewed",
            "original_asset_redistributed": False, "source_figures_digitized": False,
            "original_sha256": "synthetic", "publisher_url": "https://example.org/source",
        },
        "reported_widths": [
            {"id": f"synthetic:{i}", "support_kind": support, "reported_width_km": (i+1)*50,
             "canonical_width_admitted": False, "width_boundary_criterion": None,
             "width_edge_coordinates": None, "uncertainty_km": None,
             "width_depth_interval_m": None, "width_depth_level_m": None,
             "locator": "synthetic passage", "date_assignment": "unspecified",
             "geographic_scope": "synthetic scope", "label": "A & B <test>", "precision": "about"}
            for i, support in enumerate(sorted(SUPPORT))
        ],
    }


def test_synthetic_round_trip_without_promotion():
    facts = synthetic()
    before = copy.deepcopy(facts)
    report = json.loads(report_bytes(facts, {"input_sha256": {"synthetic": "pin"}}))
    assert report["source_facts"] == facts == before
    assert report["canonical_admission_verified"] is False
    assert report["independent_observations_created"] == 0
    xml = ET.fromstring(svg_bytes(facts))
    assert xml.attrib["role"] == "img"
    assert len(xml.findall(".//{http://www.w3.org/2000/svg}circle")) == 3


@pytest.mark.parametrize("value", [True, False, 0, -1, float("nan"), float("inf"), 301, "100"])
def test_invalid_width(value):
    facts = synthetic()
    facts["reported_widths"][0]["reported_width_km"] = value
    with pytest.raises(ValueError):
        validate(facts)


@pytest.mark.parametrize("field", NULL_FIELDS)
def test_no_derived_physical_or_annual_quantity(field):
    facts = synthetic()
    facts["eligibility"][field] = [50, 150]
    with pytest.raises(ValueError):
        validate(facts)


@pytest.mark.parametrize("field", ["canonical_identity_admitted", "canonical_width_admissions", "new_independent_width_observations", "width_ranking_eligible", "physical_seasonal_playback_eligible"])
def test_no_admission_promotion(field):
    facts = synthetic()
    facts["eligibility"][field] = 1
    with pytest.raises(ValueError):
        validate(facts)


@pytest.mark.parametrize("field", ["width_boundary_criterion", "width_edge_coordinates", "uncertainty_km", "width_depth_interval_m"])
def test_no_invented_edges_layer_or_error(field):
    facts = synthetic()
    facts["reported_widths"][0][field] = 10
    with pytest.raises(ValueError):
        validate(facts)


def test_duplicate_statement_and_erasure_rejected():
    facts = synthetic()
    facts["reported_widths"][1]["id"] = facts["reported_widths"][0]["id"]
    with pytest.raises(ValueError):
        validate(facts)
    facts = synthetic()
    facts["reported_widths"].pop()
    with pytest.raises(ValueError):
        validate(facts)


def test_different_support_and_depth_preserved():
    facts = synthetic()
    for row in facts["reported_widths"]:
        if row["support_kind"] == "source_reported_shipboard_survey_summary":
            row["width_depth_level_m"] = 21
    validate(facts)
    contextual = next(r for r in facts["reported_widths"] if r["support_kind"] != "source_reported_shipboard_survey_summary")
    contextual["width_depth_level_m"] = 75
    with pytest.raises(ValueError):
        validate(facts)


def test_abstract_or_redistribution_cannot_replace_full_primary_support():
    for field, value in [("access_scope", "abstract_only"), ("original_asset_redistributed", True), ("source_figures_digitized", True)]:
        facts = synthetic()
        facts["source"][field] = value
        with pytest.raises(ValueError):
            validate(facts)
