import datetime as dt
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name):
    path = Path(__file__).with_name(name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FETCH = load("fetch_noaa_crw_mhw_point")
DETECT = load("detect_noaa_crw_marine_heatwave")


def test_daily_url_is_exact_and_versioned():
    assert FETCH.file_url(dt.date(2026, 8, 1)).endswith("/2026/noaa-crw_mhw_v1.0.1_category_20260801.nc")


def test_duration_test_rejects_four_and_accepts_five_days():
    four = [[f"2026-08-0{day}", 1, 0] for day in range(1, 5)]
    five = [[f"2026-08-0{day}", 1, 0] for day in range(1, 6)]
    assert DETECT.detect(four) == []
    assert DETECT.detect(five)[0]["duration_days"] == 5


def test_land_or_ice_mask_breaks_a_run():
    rows = [[f"2026-08-{day:02d}", 2, int(day == 3)] for day in range(1, 7)]
    assert DETECT.detect(rows) == []


def test_committed_source_and_detection_are_checksum_linked():
    source_path = ROOT / "atlas" / "data" / "noaa-crw-mhw-point-north-atlantic-2026.json"
    detection_path = ROOT / "research" / "osw-d1-noaa-crw-mhw-point-2026.json"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    detection = json.loads(detection_path.read_text(encoding="utf-8"))
    assert len(source["rows"]) == len(source["files"]) == source["window"]["day_count"] == 32
    assert source["rows"][0][0] == "2026-07-20" and source["rows"][-1][0] == "2026-08-20"
    assert all(len(item["raw_file_sha256"]) == 64 for item in source["files"])
    assert detection["source_artifact_sha256"] == hashlib.sha256(source_path.read_bytes()).hexdigest()
    assert detection["status"] == "detected_object"
    assert detection["events"] == [{
        "start_date": "2026-07-23",
        "end_date": "2026-08-18",
        "duration_days": 27,
        "maximum_category": 2,
        "category_day_counts": {"0": 1, "1": 15, "2": 11},
        "left_censored": False,
        "right_censored": False,
    }]


def test_detection_build_is_deterministic(tmp_path):
    output = tmp_path / "detection.json"
    DETECT.build(output_path=output)
    assert output.read_bytes() == (ROOT / "research" / "osw-d1-noaa-crw-mhw-point-2026.json").read_bytes()
