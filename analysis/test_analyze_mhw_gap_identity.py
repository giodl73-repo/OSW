import importlib.util
import hashlib
import json
from pathlib import Path

import numpy as np


SCRIPT = Path(__file__).with_name("analyze_mhw_gap_identity.py")
ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("analyze_mhw_gap_identity", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_bridge_metrics_separate_exact_overlap_fractions():
    before = {(0, 0), (0, 1), (0, 2)}
    after = {(0, 1), (0, 2), (0, 3), (0, 4)}
    assert MODULE.bridge_metrics(before, after) == {
        "intersection_pixels": 2,
        "iou": 0.4,
        "pre_gap_retained_fraction": 0.6667,
        "post_gap_inherited_fraction": 0.5,
        "spatial_dilation_cells_required": 0,
    }


def test_decode_runs_recovers_native_cells():
    latitudes = np.array([10.0, 10.05])
    longitudes = np.array([20.0, 20.05, 20.1])
    rows = [[10.05, [[20.0, 20.1, 1]]]]
    assert MODULE.decode_runs(rows, latitudes, longitudes) == {(1, 0), (1, 1), (1, 2)}


def test_committed_gap_identity_contract():
    payload = json.loads((ROOT / "research" / "osw-d4-noaa-crw-mhw-gap-identity-2026.json").read_text(encoding="utf-8"))
    for source in payload["source_artifacts"]:
        path = ROOT / source["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == source["sha256"]
    assert payload["status"] == "policy_dependent_reconnection"
    assert payload["bridge_metrics"] == {
        "intersection_pixels": 122,
        "iou": 0.2542,
        "pre_gap_retained_fraction": 0.8414,
        "post_gap_inherited_fraction": 0.267,
        "spatial_dilation_cells_required": 0,
    }
    assert [item["reconnects"] for item in payload["policy_bakeoff"]] == [False, True, True]
    assert payload["post_gap_lineage"]["day_count"] == 7
