import hashlib
import json
import pathlib
import xml.etree.ElementTree as ET

from analyze_rtofs_mhw_advection import run


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "atlas/data/rtofs-mhw-bridge-north-atlantic-20260807-20260812.json"


def test_compact_rtofs_source_is_complete_and_pinned():
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert payload["window"]["day_count"] == len(payload["rows"]) == 6
    assert payload["grid"]["shape"] == [67, 63]
    assert payload["grid"]["valid_box_cells"] == 4221
    encoded = json.dumps(payload["rows"], separators=(",", ":")).encode()
    assert hashlib.sha256(encoded).hexdigest() == payload["extracted_rows_sha256"] == "137be844c3f98fce0af15437e9824e0c78f3ef80ac90098f846f338f6f089099"
    assert all(day["three_dimensional"]["etag"] and day["two_dimensional"]["etag"] for day in payload["files"])


def test_bridge_warming_is_not_dominated_by_horizontal_advection():
    result = run()
    bridge = result["bridge_evaluation"]
    assert bridge["box_mean_temperature_tendency_c_per_day"] == 0.5396
    assert bridge["box_mean_horizontal_advection_c_per_day"] == 0.0708
    assert bridge["box_mean_unresolved_remainder_c_per_day"] == 0.4688
    assert bridge["same_sign_advection_fraction_of_temperature_tendency"] == 0.131
    assert result["intervals"][-1]["anchor"] == {
        "surface_temperature_tendency_c_per_day": 0.601,
        "endpoint_mean_horizontal_advection_c_per_day": -0.109,
        "unresolved_remainder_c_per_day": 0.71,
    }
    assert bridge["mixed_layer_thickness"]["box_mean_start_m"] == 19.497
    assert bridge["mixed_layer_thickness"]["box_mean_end_m"] == 7.801
    assert abs(result["intervals"][-1]["gradient_stencil_sensitivity"]["difference_c_per_day"]) < 0.002


def test_committed_analysis_matches_and_svg_carries_boundary():
    committed = json.loads((ROOT / "research/osw-d11-rtofs-mhw-horizontal-advection-2026.json").read_text(encoding="utf-8"))
    assert committed == run()
    svg = ROOT / "figures/osw-d11-rtofs-mhw-horizontal-advection-2026.svg"
    ET.parse(svg)
    text = svg.read_text(encoding="utf-8")
    for token in ("HORIZONTAL ADVECTION IS NOT THE MAIN TERM", "13%", "UNRESOLVED REMAINDER", "NOT MODEL-NATIVE TRACER BUDGET", "OSW-D11"):
        assert token in text
