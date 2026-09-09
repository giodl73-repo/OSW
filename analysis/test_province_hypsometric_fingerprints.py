import hashlib
import json
from pathlib import Path

from derive_province_hypsometric_fingerprints import derive


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research" / "longhurst-2007-gebco-2026-depths.json"
OUTPUT = ROOT / "research" / "longhurst-2007-province-hypsometric-fingerprints.json"
BROWSER = ROOT / "column" / "province-fingerprints.js"


def load():
    return json.loads(OUTPUT.read_text(encoding="utf-8"))


def test_fingerprint_artifact_is_source_bound_and_complete():
    payload = load()
    assert payload["schema"] == "osw-longhurst-2007-hypsometric-fingerprints-v1"
    assert payload["source_sha256"] == hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert payload["province_count"] == len(payload["provinces"]) == 54
    assert sum(payload["summary"]["counts_by_floor_character"].values()) == 54
    assert sum(payload["summary"]["counts_by_substantial_band_count"].values()) == 54


def test_fingerprint_classification_has_fixed_transparent_results():
    payload = load()
    assert payload["summary"]["counts_by_floor_character"] == {
        "abyssal-floor-led": 24,
        "deep-floor-led": 19,
        "shelf-led": 11,
    }
    assert payload["summary"]["counts_by_substantial_band_count"] == {
        "1": 1, "2": 22, "3": 17, "4": 13, "5": 1,
    }
    assert payload["provinces"]["SUND"]["floor_character"] == "shelf-led"
    assert payload["provinces"]["NADR"]["floor_character"] == "deep-floor-led"
    assert payload["provinces"]["SPSG"]["floor_character"] == "abyssal-floor-led"
    assert payload["provinces"]["KURO"]["substantial_seafloor_band_count"] == 5


def test_rank_shift_definition_and_hadal_flag_are_consistent():
    payload = load()
    for item in payload["provinces"].values():
        assert item["volume_rank_advantage_over_area"] == item["sampled_wet_area_rank"] - item["sampled_water_volume_rank"]
        assert 1 <= item["sampled_wet_area_rank"] <= 54
        assert 1 <= item["sampled_water_volume_rank"] <= 54
        assert 1 <= item["mean_water_depth_rank"] <= 54
        assert item["substantial_seafloor_band_count"] == len(item["substantial_seafloor_bands"])


def test_browser_payload_matches_and_derivation_is_deterministic(tmp_path):
    prefix = "window.OSW_PROVINCE_FINGERPRINTS = "
    text = BROWSER.read_text(encoding="utf-8")
    assert text.startswith(prefix) and text.endswith(";\n")
    assert json.loads(text[len(prefix):-2]) == load()
    rebuilt = tmp_path / "fingerprints.json"
    rebuilt_browser = tmp_path / "fingerprints.js"
    derive(SOURCE, rebuilt, rebuilt_browser)
    assert rebuilt.read_bytes() == OUTPUT.read_bytes()
    assert rebuilt_browser.read_bytes() == BROWSER.read_bytes()
