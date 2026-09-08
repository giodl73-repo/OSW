import csv
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research" / "gebco-2026-province-seed-depths-source.json"
TABLE = ROOT / "research" / "gebco-2026-province-seed-depths.csv"
SUMMARY = ROOT / "research" / "gebco-2026-province-seed-depths-summary.json"
BUILDER = ROOT / "analysis" / "build_gebco_province_seed_depths.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("gebco_seed_builder", BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_gebco_seed_source_receipts_are_complete_and_intact():
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    records = payload["records"]
    assert payload["schema"] == "osw-gebco-province-seed-source-v1"
    assert payload["source"]["release"] == "GEBCO_2026"
    assert payload["source"]["doi"] == "10.5285/4f68d5c7-45eb-f999-e063-7086abc036fa"
    assert payload["sampling"]["record_count"] == len(records) == 56
    assert len({record["code"] for record in records}) == 56
    for record in records:
        raw = record["response_ascii"].encode("utf-8")
        assert hashlib.sha256(raw).hexdigest() == record["response_sha256"]
        tid_raw = record["tid_response_ascii"].encode("utf-8")
        assert hashlib.sha256(tid_raw).hexdigest() == record["tid_response_sha256"]
        assert "GEBCO_2026.nc.ascii?elevation[" in record["query_url"]
        assert "gebco_2026_tid.nc.ascii?tid[" in record["tid_query_url"]
        assert record["tid_sampled_latitude"] == record["sampled_latitude"]
        assert record["tid_sampled_longitude"] == record["sampled_longitude"]
        assert abs(record["sampled_latitude"] - record["seed_latitude"]) <= 1 / 480 + 1e-10
        assert abs(record["sampled_longitude"] - record["seed_longitude"]) <= 1 / 480 + 1e-10


def test_gebco_seed_table_preserves_non_wet_results():
    with TABLE.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 56
    wet = [row for row in rows if row["cell_state"] == "wet"]
    non_wet = [row for row in rows if row["cell_state"] == "non_wet_seed"]
    assert len(wet) == 53
    assert {row["code"] for row in non_wet} == {"NEWZ", "NWCS", "REDS"}
    assert all(row["water_depth_m"] == "" and row["deepest_edition1_band"] == "unavailable" for row in non_wet)
    assert all(int(row["water_depth_m"]) == -int(row["elevation_m"]) for row in wet)
    assert all(row["tid_code"] == "0" and row["tid_class"] == "land" for row in non_wet)
    assert {row["tid_class"] for row in wet} <= {"direct_measurement", "indirect_or_interpolated", "mixed_or_unknown"}


def test_gebco_seed_table_build_is_deterministic(tmp_path):
    output = tmp_path / "seed-depths.csv"
    summary_output = tmp_path / "summary.json"
    load_builder().build(output=output, summary_output=summary_output)
    assert output.read_bytes() == TABLE.read_bytes()
    assert summary_output.read_bytes() == SUMMARY.read_bytes()


def test_gebco_seed_summary_keeps_quality_visible():
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert summary["record_count"] == 56
    assert summary["wet_count"] == 53
    assert summary["non_wet_codes"] == ["NEWZ", "NWCS", "REDS"]
    assert summary["counts_by_tid_class"] == {
        "direct_measurement": 28,
        "indirect_or_interpolated": 24,
        "land": 3,
        "mixed_or_unknown": 1,
    }
