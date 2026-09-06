import json
import hashlib
import pathlib
import xml.etree.ElementTree as ET

from analyze_oisst_mhw_bridge import run


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_committed_bridge_source_is_complete_and_pinned():
    payload = json.loads((ROOT / "atlas/data/oisst-mhw-bridge-north-atlantic-20260807-20260812.json").read_text(encoding="utf-8"))
    assert payload["window"] == {"start": "2026-08-07", "end": "2026-08-12", "day_count": 6}
    assert len(payload["latitude_degrees_north"]) == 12
    assert len(payload["longitude_degrees_east"]) == 17
    assert all(len(field) == 12 and all(len(row) == 17 for row in field) for _, field in payload["rows"])
    assert payload["extracted_slice_sha256"] == "0ebca84b4498b1e14ab14d09251271f3a73324e4cd4b00569944e7f8fe4dd2dd"
    encoded_rows = json.dumps(payload["rows"], separators=(",", ":")).encode()
    assert hashlib.sha256(encoded_rows).hexdigest() == payload["extracted_slice_sha256"]
    assert payload["request"]["opendap_hyperslab"] == "sst[218:1:223][520:1:531][1234:1:1250]"


def test_crosscheck_separates_category_return_from_local_temperature_rebound():
    result = run()
    bridge = result["bridge_day_comparison"]
    assert bridge["crw_category_change"] == [0, 1]
    assert bridge["oisst_anchor_change_c"] == -0.13
    assert bridge["oisst_fixed_box_mean_change_c"] == 0.16
    assert bridge["oisst_fixed_box_maximum_change_c"] == 0.18
    assert result["identity_evaluation"]["result"] == "threshold return without separate-product local rebound"
    assert "does not identify" in result["boundary"]


def test_committed_analysis_matches_generator_and_svg_is_accessible():
    committed = json.loads((ROOT / "research/osw-d10-oisst-mhw-bridge-crosscheck-2026.json").read_text(encoding="utf-8"))
    assert committed == run()
    svg = ROOT / "figures/osw-d10-oisst-mhw-bridge-crosscheck-2026.svg"
    root = ET.parse(svg).getroot()
    assert root.tag.endswith("svg")
    text = svg.read_text(encoding="utf-8")
    for token in ("THE CATEGORY RETURNS", "nearest OISST cell", "Threshold return", "OSW-D10"):
        assert token in text
