import importlib.util
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("build_mhw_lineage_family.py")
SPEC = importlib.util.spec_from_file_location("mhw_lineage_family", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_discover_candidates_preserves_both_sides_of_split():
    active = np.zeros((4, 7), dtype=bool)
    active[1, 1:3] = True
    active[1, 4:6] = True
    previous = [{(1, 1), (1, 2), (1, 3), (1, 4), (1, 5)}]
    candidates = MODULE.discover_candidates(active, previous)
    assert {frozenset(component) for component in candidates} == {
        frozenset({(1, 1), (1, 2)}), frozenset({(1, 4), (1, 5)}),
    }


def test_chronological_edge_uses_two_denominators():
    before = {(0, 0), (0, 1), (0, 2)}
    after = {(0, 1), (0, 2), (0, 3), (0, 4)}
    assert MODULE.chronological_edge(before, after) == {
        "intersection_pixels": 2,
        "iou": 0.4,
        "source_retained_fraction": 0.6667,
        "target_inherited_fraction": 0.5,
    }


def test_committed_lineage_family_contract():
    path = ROOT / "research" / "osw-d7-noaa-crw-mhw-lineage-family-2026.json"
    if not path.exists():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema"] == "osw.ocean-object-lineage-family.v1"
    for source in payload["source_artifacts"]:
        source_path = ROOT / source["path"]
        assert hashlib.sha256(source_path.read_bytes()).hexdigest() == source["sha256"]
    assert payload["tracked_window"]["start"] == "2026-07-21"
    assert payload["tracked_window"]["end"] == "2026-08-10"
    assert payload["summary"]["primary_branch_node_count"] == 21
    assert payload["summary"]["node_count"] == 28
    assert payload["summary"]["edge_count"] == 29
    assert payload["summary"]["off_primary_node_count"] == 7
    assert payload["summary"]["split_node_count"] == 5
    assert payload["summary"]["merge_node_count"] == 1
    assert payload["summary"]["off_primary_terminal_node_count"] == 5
    assert payload["summary"]["off_primary_merge_back_node_count"] == 2
    assert payload["summary"]["largest_off_primary_component_pixels"] == 54
    assert len(payload["nodes"]) == payload["summary"]["node_count"]
    assert len(payload["edges"]) == payload["summary"]["edge_count"]
    nodes = {item["node_id"] for item in payload["nodes"]}
    indegree = {node_id: 0 for node_id in nodes}
    outdegree = {node_id: 0 for node_id in nodes}
    for edge in payload["edges"]:
        assert edge["from"] in nodes and edge["to"] in nodes
        assert edge["from"][:10] < edge["to"][:10]
        indegree[edge["to"]] += 1
        outdegree[edge["from"]] += 1
    assert sum(value > 1 for value in outdegree.values()) == payload["summary"]["split_node_count"]
    assert sum(value > 1 for value in indegree.values()) == payload["summary"]["merge_node_count"]
