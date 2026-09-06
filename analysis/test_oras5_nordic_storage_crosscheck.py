import json
import pathlib

import numpy as np

from analyze_oras5_nordic_storage_crosscheck import analyze
from fetch_oras5_drake_surface_heat import sha256_file


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_column_heat_source_receipt_matches_payload() -> None:
    receipt = json.loads((ROOT / "research/osw-m4-oras5-nordic-column-heat-source-2018.json").read_text(encoding="utf-8"))
    assert receipt["shape"] == [12, 256, 296]
    assert receipt["field"] == "sohtcbtm"
    assert receipt["output"]["sha256"] == sha256_file(ROOT / receipt["output"]["path"])


def test_storage_crosscheck_is_finite_and_month_complete() -> None:
    result = analyze(ROOT)
    assert len(result["months"]) == 12
    assert all(np.isfinite(value) for value in result["summary"].values())
    assert result["summary"]["storage_tendency_correlation"] > 0.9
    assert "not model-native budget closure" in result["boundary"]
