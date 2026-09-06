import importlib.util
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("analyze_mhw_lineage_family_pruning.py")
SPEC = importlib.util.spec_from_file_location("mhw_family_pruning", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def synthetic_family():
    node = lambda node_id, area, primary=False: {
        "node_id": node_id, "on_d3_primary_branch": primary, "summary": {"area_km2": area}
    }
    return {
        "nodes": [
            node("2026-07-22-C01", 100, True),
            node("2026-07-23-C01", 100, True),
            node("2026-07-24-C01", 100, True),
            node("2026-07-24-C02", 5),
        ],
        "edges": [
            {"from": "2026-07-22-C01", "to": "2026-07-23-C01"},
            {"from": "2026-07-23-C01", "to": "2026-07-24-C01"},
            {"from": "2026-07-23-C01", "to": "2026-07-24-C02"},
        ],
    }


def test_pruning_recomputes_topology_after_removal():
    full = MODULE.retained_graph(synthetic_family(), 0)
    pruned = MODULE.retained_graph(synthetic_family(), 10)
    assert (full["node_count"], full["split_node_count"], full["side_component_count"]) == (4, 1, 1)
    assert (pruned["node_count"], pruned["split_node_count"], pruned["side_component_count"]) == (3, 0, 0)


def test_committed_family_pruning_contract():
    path = ROOT / "research" / "osw-d8-noaa-crw-mhw-family-pruning-2026.json"
    if not path.exists():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema"] == "osw.ocean-object-lineage-pruning-sensitivity.v1"
    source = ROOT / payload["source_artifact"]["path"]
    assert hashlib.sha256(source.read_bytes()).hexdigest() == payload["source_artifact"]["sha256"]
    assert [item["minimum_component_area_km2"] for item in payload["results"]] == MODULE.THRESHOLDS_KM2
    assert {item["primary_node_count"] for item in payload["results"]} == {21}
    assert [item["side_component_count"] for item in payload["results"]] == [7, 4, 4, 2, 1, 0]
    assert [item["split_node_count"] for item in payload["results"]] == [5, 3, 3, 2, 1, 0]
    assert [item["merge_node_count"] for item in payload["results"]] == [1, 1, 1, 0, 0, 0]
