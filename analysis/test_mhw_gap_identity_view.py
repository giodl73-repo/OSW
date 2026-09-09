import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("build_mhw_gap_identity_view.py")
SPEC = importlib.util.spec_from_file_location("build_mhw_gap_identity_view", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_gap_view_is_deterministic(tmp_path):
    output = tmp_path / "gap.svg"
    MODULE.build(output_path=output)
    assert output.read_bytes() == (ROOT / "figures" / "osw-d4-noaa-crw-mhw-gap-identity-2026.svg").read_bytes()


def test_gap_view_exposes_both_valid_policy_results(tmp_path):
    svg = MODULE.build(output_path=tmp_path / "gap.svg")
    assert "SPLIT · uninterrupted" in svg and "JOIN · permit one gap day" in svg
    assert "122 exact grid locations" in svg and "DILATION CELLS NEEDED" in svg
    assert "not continuous threshold evidence" in svg
