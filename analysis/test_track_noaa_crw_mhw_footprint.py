import importlib.util
import hashlib
import json
from pathlib import Path

import numpy as np


SCRIPT = Path(__file__).with_name("track_noaa_crw_mhw_footprint.py")
ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("track_noaa_crw_mhw_footprint", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_successor_requires_exact_overlap():
    previous = {(1, 1), (1, 2)}
    active = np.zeros((4, 5), dtype=bool)
    active[2, 1:3] = True
    selected, candidates = MODULE.select_successor(active, previous)
    assert selected is None and candidates == []


def test_successor_follows_greatest_intersection_after_split():
    previous = {(1, 1), (1, 2), (1, 3), (2, 1), (0, 3)}
    active = np.zeros((4, 6), dtype=bool)
    active[1, 1:3] = True
    active[1, 3] = True
    active[0, 3] = True
    active[1, 4] = True
    active[1, 2] = False
    selected, candidates = MODULE.select_successor(active, previous)
    assert len(candidates) == 2
    assert selected["component"] == {(0, 3), (1, 3), (1, 4)}
    assert selected["intersection_pixels"] == 2


def test_overlap_metrics_are_explicit():
    previous = {(0, 0), (0, 1), (0, 2)}
    active = np.array([[1, 1, 0, 0]], dtype=bool)
    selected, _ = MODULE.select_successor(active, previous)
    assert selected["intersection_pixels"] == 2
    assert selected["previous_retained_fraction"] == 2 / 3
    assert selected["current_inherited_fraction"] == 1


def test_committed_lineage_contract_and_checksum_chain():
    path = ROOT / "research" / "osw-d3-noaa-crw-mhw-lineage-2026.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    source = ROOT / payload["source_artifact"]
    seed = ROOT / payload["seed_artifact"]
    assert hashlib.sha256(source.read_bytes()).hexdigest() == payload["source_artifact_sha256"]
    assert hashlib.sha256(seed.read_bytes()).hexdigest() == payload["seed_artifact_sha256"]
    assert payload["tracked_window"] == {
        "start": "2026-07-21", "end": "2026-08-10", "day_count": 21,
        "left_censored": False, "right_censored": False,
    }
    assert payload["lineage_limits"]["preceding"]["date"] == "2026-07-20"
    assert payload["lineage_limits"]["following"]["date"] == "2026-08-11"
    assert payload["summary"]["maximum_daily_area_km2"] == 49439.2
    assert payload["summary"]["branch_ambiguous_transition_count"] == 5
    assert len(payload["daily_footprints"]) == 21
    assert len(payload["transitions"]) == 20
