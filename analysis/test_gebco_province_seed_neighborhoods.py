import hashlib
import importlib.util
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research" / "gebco-2026-province-seed-neighborhoods-source.json"
DATA = ROOT / "research" / "gebco-2026-province-seed-neighborhoods.json"
SUMMARY = ROOT / "research" / "gebco-2026-province-seed-neighborhoods-summary.json"
BROWSER = ROOT / "column" / "neighborhoods.js"
BUILDER = ROOT / "analysis" / "build_gebco_province_seed_neighborhoods.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("gebco_neighborhood_builder", BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_neighborhood_source_receipts_are_intact():
    receipt = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert receipt["schema"] == "osw-gebco-province-seed-neighborhood-source-v1"
    assert receipt["sampling"]["record_count"] == len(receipt["records"]) == 56
    assert receipt["sampling"]["shape"] == [33, 33]
    assert receipt["sampling"]["spacing_degrees"] == 0.25
    assert receipt["sampling"]["nominal_width_degrees"] == 8.0
    for record in receipt["records"]:
        elevation = record["elevation_response_ascii"].encode("utf-8")
        tid = record["tid_response_ascii"].encode("utf-8")
        assert hashlib.sha256(elevation).hexdigest() == record["elevation_response_sha256"]
        assert hashlib.sha256(tid).hexdigest() == record["tid_response_sha256"]


def test_neighborhood_derived_contract():
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert payload["schema"] == "osw-gebco-province-seed-neighborhood-v1"
    assert payload["shape"] == [33, 33]
    assert len(payload["neighborhoods"]) == 56
    assert summary["total_samples"] == 60_984
    assert summary["samples_per_neighborhood"] == 1_089
    assert summary["fully_wet_neighborhood_count"] == 29
    assert summary["mixed_land_water_neighborhood_count"] == 27
    assert summary["counts_by_tid_class"] == {
        "direct_measurement": 22_430,
        "indirect_or_interpolated": 32_855,
        "land": 4_560,
        "mixed_or_unknown": 1_139,
    }
    for neighborhood in payload["neighborhoods"].values():
        assert len(neighborhood["elevation_m"]) == 1_089
        assert len(neighborhood["tid"]) == 1_089
        assert neighborhood["summary"]["sample_count"] == 1_089
        assert len(neighborhood["summary"]["latitude_bounds"]) == 2
        assert len(neighborhood["summary"]["longitude_bounds"]) == 2
        assert neighborhood["summary"]["wet_sample_count"] + neighborhood["summary"]["land_sample_count"] == 1_089


def test_neighborhood_build_is_deterministic(tmp_path):
    output, summary, browser = tmp_path / "data.json", tmp_path / "summary.json", tmp_path / "neighborhoods.js"
    load_builder().build(output=output, summary_output=summary, browser_output=browser)
    assert output.read_bytes() == DATA.read_bytes()
    assert summary.read_bytes() == SUMMARY.read_bytes()
    assert browser.read_bytes() == BROWSER.read_bytes()
    assert re.match(rb"window\.OSW_BATHY_NEIGHBORHOODS = \{", browser.read_bytes())
