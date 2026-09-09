import json
import pathlib

import netCDF4
import numpy as np

from analyze_oras5_nordic_remainder_context import analyze
from fetch_oras5_drake_surface_heat import sha256_file


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_seasonal_context_receipt_matches_payload() -> None:
    receipt = json.loads((ROOT / "research/osw-m4-oras5-nordic-seasonal-context-source-2018.json").read_text(encoding="utf-8"))
    path = ROOT / receipt["output"]["path"]
    assert receipt["shape_per_field"] == [12, 256, 296]
    assert receipt["output"]["sha256"] == sha256_file(path)
    with netCDF4.Dataset(path) as dataset:
        assert dataset.variables["ileadfra"].long_name == "Ice concentration"


def test_remainder_context_is_complete_and_bounded() -> None:
    result = analyze(ROOT)
    assert result["checks"] == {"month_count": 12, "ice_concentration_bounds_pass": True, "all_values_finite": True}
    assert all(0 <= record["area_mean_ice_concentration"] <= 1 for record in result["months"])
    assert all(0 <= record["ice_extent_fraction_at_15_percent"] <= 1 for record in result["months"])
    assert len(result["zero_lag_pearson_correlation_with_remainder"]) == 7
    assert "seasonally confounded" in result["boundary"]
