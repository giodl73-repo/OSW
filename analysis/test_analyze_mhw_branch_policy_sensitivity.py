import importlib.util
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("analyze_mhw_branch_policy_sensitivity.py")
SPEC = importlib.util.spec_from_file_location("mhw_branch_sensitivity", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def candidates():
    return [
        {"component": {(0, 0), (0, 1), (0, 2), (0, 3)}, "intersection_pixels": 3, "iou": 0.50, "previous_retained_fraction": 0.6, "current_inherited_fraction": 0.75},
        {"component": {(1, 0), (1, 1)}, "intersection_pixels": 2, "iou": 0.66, "previous_retained_fraction": 0.4, "current_inherited_fraction": 1.0},
        {"component": {(2, 0), (2, 1), (2, 2), (2, 3), (2, 4)}, "intersection_pixels": 1, "iou": 0.11, "previous_retained_fraction": 0.2, "current_inherited_fraction": 0.2},
    ]


def test_branch_policies_choose_declared_scores():
    values = candidates()
    assert len(MODULE.choose_candidate(values, "greatest_intersection")["component"]) == 4
    assert len(MODULE.choose_candidate(values, "greatest_iou")["component"]) == 2
    assert len(MODULE.choose_candidate(values, "greatest_candidate_inherited_fraction")["component"]) == 2
    assert len(MODULE.choose_candidate(values, "largest_overlapping_component")["component"]) == 5


def test_component_hash_is_order_invariant():
    assert MODULE.component_sha256({(1, 2), (0, 3)}) == MODULE.component_sha256({(0, 3), (1, 2)})


def test_committed_branch_sensitivity_contract():
    path = ROOT / "research" / "osw-d6-noaa-crw-mhw-branch-sensitivity-2026.json"
    if not path.exists():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema"] == "osw.ocean-object-branch-sensitivity.v1"
    for source in payload["source_artifacts"]:
        source_path = ROOT / source["path"]
        assert hashlib.sha256(source_path.read_bytes()).hexdigest() == source["sha256"]
    assert [item["policy_id"] for item in payload["results"]] == [item["policy_id"] for item in MODULE.POLICIES]
    assert payload["results"][0]["tracked_window"] == {"start": "2026-07-21", "end": "2026-08-10", "day_count": 21}
    assert [item["tracked_window"]["day_count"] for item in payload["results"]] == [21, 21, 14, 21]
    assert payload["results"][2]["differs_from_baseline_on_dates"] == ["2026-07-30", "2026-08-03"]
    assert payload["results"][2]["forward_stop"]["date"] == "2026-08-04"
    fraction_transitions = {item["candidate_date"]: item for item in payload["results"][2]["transitions"]}
    assert fraction_transitions["2026-07-30"]["selected"]["pixel_count"] == 12
    assert fraction_transitions["2026-07-30"]["selected"]["candidate_inherited_fraction"] == 1.0
    assert fraction_transitions["2026-08-03"]["selected"]["pixel_count"] == 1
    assert fraction_transitions["2026-08-03"]["selected"]["candidate_inherited_fraction"] == 1.0
    assert [item["same_daily_components"] for item in payload["comparison_to_greatest_intersection"]] == [True, False, True]
