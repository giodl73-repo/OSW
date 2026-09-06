import importlib.util
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("build_mhw_typed_gap_graph.py")
SPEC = importlib.util.spec_from_file_location("mhw_typed_gap_graph", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_coordinate_cells_expands_runs_exactly():
    rows = [[42.0, [[-50.0, -49.9, 1]]]]
    assert MODULE.coordinate_cells(rows) == {(42.0, -50.0), (42.0, -49.95), (42.0, -49.9)}


def test_overlap_metrics_keep_both_denominators():
    before = {(1, 1), (1, 2), (1, 3)}
    after = {(1, 2), (1, 3), (1, 4), (1, 5)}
    assert MODULE.overlap_metrics(before, after) == {
        "intersection_pixels": 2,
        "iou": 0.4,
        "source_retained_fraction": 0.6667,
        "target_inherited_fraction": 0.5,
    }


def test_committed_typed_gap_graph_contract():
    path = ROOT / "research" / "osw-d9-noaa-crw-mhw-typed-gap-graph-2026.json"
    if not path.exists():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema"] == "osw.ocean-object-typed-gap-graph.v1"
    for source in payload["source_artifacts"]:
        source_path = ROOT / source["path"]
        assert hashlib.sha256(source_path.read_bytes()).hexdigest() == source["sha256"]
    assert [item["reconnects"] for item in payload["policy_bakeoff"]] == [False, True]
    assert [(item["node_count"], item["edge_count"]) for item in payload["policy_bakeoff"]] == [(28, 29), (35, 36)]
    assert payload["typed_bridge"]["edge_type"] == "one_day_threshold_gap_exact_spatial_overlap"
    assert payload["typed_bridge"]["intersection_pixels"] == 122
    assert payload["typed_bridge"]["elapsed_days"] == 2
    assert payload["typed_bridge"]["threshold_inactive_days"] == 1
    assert payload["typed_bridge"]["active_source_pixels_remaining_on_inactive_date"] == 0
    assert payload["typed_bridge"]["spatial_dilation_cells_required"] == 0
    assert payload["post_gap_primary_lineage"]["day_count"] == 7
    assert len(payload["post_gap_primary_lineage"]["edges"]) == 6
    assert all(edge["edge_type"] == "adjacent_day_exact_overlap" for edge in payload["post_gap_primary_lineage"]["edges"])
    assert all(edge["elapsed_days"] == 1 and edge["threshold_inactive_days"] == 0 for edge in payload["post_gap_primary_lineage"]["edges"])
