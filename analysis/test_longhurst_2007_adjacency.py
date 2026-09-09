import json
from pathlib import Path

import numpy as np
from shapely.geometry import box

from acquire_longhurst_2007_adjacency import classify_contacts, sampled_neighbor_pairs


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research" / "longhurst-2007-province-adjacency.json"
REJECTED = ROOT / "research" / "longhurst-2007-province-adjacency-rejected.json"
RECEIPT = ROOT / "research" / "longhurst-2007-province-adjacency-source-receipt.json"
BROWSER = ROOT / "column" / "province-adjacency.js"


def load():
    return json.loads(DATA.read_text(encoding="utf-8"))


def test_synthetic_shared_edge_and_point_contact_are_distinct():
    edges, rejected = classify_contacts({
        "A": box(0, 0, 1, 1),
        "B": box(1, 0, 2, 1),
        "C": box(2, 1, 3, 2),
    })
    assert [(item["edge_id"], item["contact_class"]) for item in edges] == [
        ("A--B", "shared_source_edge")
    ]
    assert edges[0]["shared_boundary_length_km"] > 110
    assert [(item["candidate_id"], item["disposition"]) for item in rejected] == [
        ("B--C", "rejected_point_only_contact")
    ]


def test_sampled_neighbor_scan_wraps_the_longitude_seam():
    pairs, counts = sampled_neighbor_pairs(np.array([[0, -1, 1]], dtype=np.int16), ["E", "W"])
    assert pairs == {("E", "W")}
    assert counts[("E", "W")] == 1


def test_committed_graph_has_complete_symmetric_topology():
    payload = load()
    assert payload["schema"] == "osw-longhurst-2007-province-adjacency-v1"
    assert payload["summary"] == {
        "node_count": 54,
        "accepted_shared_edge_count": 128,
        "source_edges_with_sampled_grid_support": 127,
        "source_edges_without_sampled_grid_support": 1,
        "rejected_candidate_count": 10,
        "rejected_counts_by_disposition": {"rejected_point_only_contact": 10},
        "minimum_degree": 1,
        "maximum_degree": 11,
        "mean_degree": 4.740741,
        "fresh_to_committed_assignment_matching_cells": 1_036_800,
        "fresh_to_committed_assignment_total_cells": 1_036_800,
    }
    assert len(payload["normalized_repaired_geometry_sha256"]) == 64
    edges = {tuple(item["provinces"]): item for item in payload["edges"]}
    assert len(edges) == 128
    assert all(first < second for first, second in edges)
    assert all(item["shared_boundary_length_km"] > 0 for item in edges.values())
    nodes = {item["osw_code"]: item for item in payload["nodes"]}
    assert len(nodes) == 54
    assert sum(item["degree"] for item in nodes.values()) == 256
    for code, node in nodes.items():
        assert node["degree"] == len(node["neighbors"])
        assert all(code in nodes[neighbor]["neighbors"] for neighbor in node["neighbors"])


def test_grid_support_is_a_diagnostic_not_the_edge_identity():
    payload = load()
    unsupported = [item for item in payload["edges"] if not item["sampled_grid_support"]]
    assert len(unsupported) == 1
    assert unsupported[0]["edge_id"] == "CNRY--MEDI"
    assert 17 < unsupported[0]["shared_boundary_length_km"] < 18
    assert payload["contract"]["grid_support"].endswith("not the adjacency identity test.")


def test_rejected_log_preserves_point_contacts_without_promotion():
    payload = json.loads(REJECTED.read_text(encoding="utf-8"))
    assert payload["schema"] == "osw-longhurst-2007-province-adjacency-rejected-v1"
    assert len(payload["candidates"]) == 10
    assert {item["disposition"] for item in payload["candidates"]} == {"rejected_point_only_contact"}
    assert {item["candidate_id"] for item in payload["candidates"]} == {
        "AUSE--SSTC", "AUSW--TASM", "CARB--NAST W", "CNRY--ETRA",
        "GFST--NADR", "GUIN--NATR", "NAST E--NWCS", "NATR--NWCS",
        "NPSW--PNEC", "NPTG--WARM",
    }


def test_source_receipt_records_grid_equivalence_not_byte_identity():
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["schema"] == "osw-longhurst-2007-province-adjacency-source-receipt-v1"
    assert receipt["source"]["feature_count"] == 54
    assert receipt["source"]["license"].startswith("CC BY 4.0")
    assert receipt["source"]["citation"].startswith("Flanders Marine Institute")
    assert len(receipt["source"]["normalized_repaired_geometry_sha256"]) == 64
    assert receipt["compatibility"]["raw_response_bytes_match"] is False
    assert receipt["compatibility"]["full_assignment_grid_match"] is True
    assert receipt["compatibility"]["matching_cells"] == receipt["compatibility"]["total_cells"] == 1_036_800


def test_browser_payload_matches_research_payload():
    prefix = "window.OSW_PROVINCE_ADJACENCY = "
    text = BROWSER.read_text(encoding="utf-8")
    assert text.startswith(prefix) and text.endswith(";\n")
    assert json.loads(text[len(prefix):-2]) == load()
