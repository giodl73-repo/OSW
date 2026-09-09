import importlib.util
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("analyze_mhw_tracking_sensitivity.py")
SPEC = importlib.util.spec_from_file_location("mhw_tracking_sensitivity", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_connectivity_distinguishes_corner_contacts():
    active = np.array([[True, False], [False, True]])
    assert MODULE.connected_component(active, (0, 0), 4) == {(0, 0)}
    assert MODULE.connected_component(active, (0, 0), 8) == {(0, 0), (1, 1)}


def test_anchored_window_stops_at_first_failed_edge():
    dates = ["2026-07-21", "2026-07-22", "2026-07-23", "2026-07-24", "2026-07-25"]
    tracked = {date: {(0, index)} for index, date in enumerate(dates)}
    transitions = {
        (dates[0], dates[1]): {"intersection_pixels": 2, "iou": 0.4},
        (dates[1], dates[2]): {"intersection_pixels": 2, "iou": 0.3},
        (dates[2], dates[3]): {"intersection_pixels": 2, "iou": 0.2},
        (dates[3], dates[4]): {"intersection_pixels": 2, "iou": 0.1},
    }
    result = MODULE.anchored_window(dates, tracked, transitions, {"metric": "iou", "minimum": 0.2})
    assert (result["start"], result["end"], result["day_count"]) == ("2026-07-21", "2026-07-24", 4)
    assert result["break_after"] == {
        "from": "2026-07-24", "to": "2026-07-25", "intersection_pixels": 2,
        "iou": 0.1, "tested_metric": "iou", "tested_value": 0.1, "required_minimum": 0.2,
    }


def test_committed_sensitivity_contract():
    path = ROOT / "research" / "osw-d5-noaa-crw-mhw-tracking-sensitivity-2026.json"
    if not path.exists():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema"] == "osw.ocean-object-tracking-sensitivity.v1"
    for source in payload["source_artifacts"]:
        source_path = ROOT / source["path"]
        assert hashlib.sha256(source_path.read_bytes()).hexdigest() == source["sha256"]
    assert [item["connectivity"] for item in payload["results"]] == [4, 8]
    assert all(len(item["threshold_windows"]) == 5 for item in payload["results"])
    four = payload["results"][0]
    eight = payload["results"][1]
    assert [item["day_count"] for item in four["threshold_windows"]] == [21, 21, 18, 18, 1]
    assert four["threshold_windows"] == eight["threshold_windows"]
    assert four["threshold_windows"][2]["break_after"]["iou"] == 0.198
    assert four["threshold_windows"][2]["break_after"]["intersection_pixels"] == 216
    assert four["gap_bridge"]["intersection_pixels"] == 122
    assert four["gap_bridge"] == eight["gap_bridge"]
    comparison = payload["cross_connectivity_comparison"]
    assert comparison["tracked_dates_equal"]
    assert not comparison["daily_components_equal"]
    assert comparison["equal_daily_component_count"] + comparison["differing_daily_component_count"] == comparison["tracked_day_count"] == 21
    assert comparison["daily_component_differences"]
    assert comparison["pre_gap_components_equal"] and comparison["post_gap_components_equal"]
    assert "not a literature-calibrated" in payload["controlled_choices"]["threshold_selection"]
