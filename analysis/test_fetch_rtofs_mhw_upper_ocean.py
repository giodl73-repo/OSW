import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))

import fetch_rtofs_mhw_upper_ocean as fetcher  # noqa: E402


def test_depth_request_is_explicit_and_rejects_nonpositive_values() -> None:
    assert fetcher.MAX_DEPTH_M == 50.0
    try:
        fetcher.build(max_depth_m=0)
    except ValueError as error:
        assert str(error) == "maximum depth must be positive"
    else:
        raise AssertionError("nonpositive depth must fail before retrieval")


def test_cli_exposes_a_separate_depth_request() -> None:
    source = (ROOT / "analysis" / "fetch_rtofs_mhw_upper_ocean.py").read_text(encoding="utf-8")
    assert 'parser.add_argument("--max-depth-m"' in source
    assert 'local_depths[-1] != max_depth_m' in source
