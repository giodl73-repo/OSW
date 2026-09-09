import json
import pathlib

import numpy as np

from analyze_ocean_event_state_routes import decode_province_grid, pixel_area_km2, province_at


ROOT = pathlib.Path(__file__).parent.parent


def test_grid_lookup_and_pixel_area_fixture():
    payload = {"grid": {"shape": [2, 3], "longitude_start": 0.0, "latitude_start": 0.0, "spacing_degrees": 1.0}, "footprint_runs": [[0, 0, 1, "A"], [1, 1, 2, "B"]]}
    decoded = decode_province_grid(payload)
    assert province_at(0, 0, payload["grid"], decoded) == "A"
    assert province_at(2, 1, payload["grid"], decoded) == "B"
    assert province_at(2, 0, payload["grid"], decoded) is None
    assert pixel_area_km2(0) > pixel_area_km2(60)


def test_committed_event_route_preserves_evidence_boundaries():
    payload = json.loads((ROOT / "research/ocean-event-state-route-2026.json").read_text(encoding="utf-8"))
    assert payload["status"] == "stage_6_surface_event_route_complete_with_transport_unresolved"
    assert len(payload["primary_route"]["days"]) == 21
    assert payload["primary_route"]["province_sequence"] == ["GFST"]
    assert {item["province"] for item in payload["state_passports"]} == {"GFST", "NWCS"}
    assert payload["lineage_family_route"]["province_crossing_candidate_count"] == 1
    crossing = payload["lineage_family_route"]["crossing_candidates"][0]
    assert crossing["source_graph_edge"] == "GFST--NWCS"
    assert crossing["source_graph_edge_confirmed"] is True
    assert crossing["intersection_pixels"] == 13
    assert crossing["source_retained_fraction"] == 0.0062
    assert payload["evidence_ladder"]["volume_exchange"].startswith("unsupported")
    assert payload["evidence_ladder"]["heat_transport"].startswith("unsupported")
    assert len(payload["conditional_gap_extension"]["nodes"]) == 7
    assert {item["province_by_centroid"] for item in payload["conditional_gap_extension"]["nodes"]} == {"GFST"}


def test_primary_overlap_fractions_and_counts_are_conservative():
    payload = json.loads((ROOT / "research/ocean-event-state-route-2026.json").read_text(encoding="utf-8"))
    for day in payload["primary_route"]["days"]:
        assert np.isclose(sum(item["area_fraction"] for item in day["province_overlap"]), 1.0, atol=1e-6)
        assert sum(item["pixel_count"] for item in day["province_overlap"]) > 0
        assert day["dominant_province"] == "GFST"


def test_event_browser_payload_matches_receipt():
    source = (ROOT / "exchange/events.js").read_text(encoding="utf-8")
    prefix = "window.OSW_EVENTS = "
    assert source.startswith(prefix) and source.endswith(";\n")
    assert json.loads(source[len(prefix):-2]) == json.loads((ROOT / "research/ocean-event-state-route-2026.json").read_text(encoding="utf-8"))
