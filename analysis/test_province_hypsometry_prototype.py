import json
from pathlib import Path

import numpy as np
import pytest

from acquire_province_hypsometry_prototype import ARCHETYPES, weighted_quantiles


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research" / "longhurst-2007-province-continuous-hypsometry-prototype.json"
RECEIPT = ROOT / "research" / "longhurst-2007-province-continuous-hypsometry-source-receipt.json"
BROWSER = ROOT / "column" / "province-hypsometry.js"


def load():
    return json.loads(DATA.read_text(encoding="utf-8"))


def test_weighted_quantiles_respect_area_weights_and_endpoints():
    result = weighted_quantiles(
        np.array([10, 20, 30], dtype=np.int32),
        np.array([1.0, 2.0, 1.0]),
        (0, 25, 50, 75, 100),
    )
    assert result == pytest.approx([10.0, 13.3333333333, 20.0, 26.6666666667, 30.0])


def test_prototype_selection_is_frozen_and_complete():
    payload = load()
    assert payload["schema"] == "osw-longhurst-2007-continuous-hypsometry-prototype-v1"
    assert payload["archetype_selection"]["status"] == "frozen before inspecting continuous-curve results"
    assert payload["archetype_selection"]["codes"] == list(ARCHETYPES)
    assert set(payload["provinces"]) == set(ARCHETYPES)
    assert payload["summary"] == {
        "prototype_province_count": 6,
        "fine_spacing_degrees": 0.25,
        "coarse_spacing_degrees": 0.5,
        "all_fresh_summary_compatibility_checks_pass": True,
    }


def test_curves_are_monotonic_and_resolution_sensitivity_is_explicit():
    payload = load()
    for province in payload["provinces"].values():
        for resolution in ("fine_0_25_degree", "coarse_0_5_degree_center_screen"):
            summary = province[resolution]
            assert summary["depth_quantile_percentiles"] == list(range(101))
            assert len(summary["depth_quantile_m"]) == 101
            assert summary["depth_quantile_m"] == sorted(summary["depth_quantile_m"])
            assert summary["depth_quantile_m"][0] == summary["minimum_depth_m"]
            assert summary["depth_quantile_m"][-1] == summary["maximum_depth_m"]
            assert 0 <= summary["shelf_area_fraction_lt_200m"] <= 1
        assert set(province["sensitivity"]["coarse_minus_fine_selected_quantiles_m"]) == {"p10", "p25", "p50", "p75", "p90"}


def test_fixed_archetypes_have_expected_distinct_fingerprints():
    provinces = load()["provinces"]
    assert provinces["NECS"]["fine_0_25_degree"]["shelf_area_fraction_lt_200m"] > 0.9
    assert provinces["NPPF"]["fine_0_25_degree"]["selected_depth_quantiles_m"]["p10"] > 4_000
    assert provinces["SUND"]["fine_0_25_degree"]["selected_depth_quantiles_m"] == {
        "p10": 17.0, "p25": 38.0, "p50": 75.0, "p75": 1_470.0, "p90": 3_273.05,
    }
    assert provinces["NADR"]["sensitivity"]["coarse_minus_fine_mean_depth_m"] == 29.72


def test_receipt_preserves_source_and_compatibility_identity():
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["schema"] == "osw-longhurst-2007-continuous-hypsometry-source-receipt-v1"
    assert receipt["sources"]["geometry"]["license"].startswith("CC BY 4.0")
    assert receipt["sources"]["geometry"]["citation"].startswith("Flanders Marine Institute")
    assert receipt["sources"]["elevation"]["license"].startswith("public domain")
    assert receipt["sources"]["elevation"]["doi"] == "10.5285/4f68d5c7-45eb-f999-e063-7086abc036fa"
    assert all(all(result.values()) for result in receipt["compatibility"].values())
    assert len(receipt["output_sha256"]) == 64


def test_browser_payload_matches_research_payload():
    prefix = "window.OSW_PROVINCE_HYPSOMETRY = "
    text = BROWSER.read_text(encoding="utf-8")
    assert text.startswith(prefix) and text.endswith(";\n")
    assert json.loads(text[len(prefix):-2]) == load()
