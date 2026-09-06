import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("build_detected_mhw_footprint_view.py")
SPEC = importlib.util.spec_from_file_location("build_detected_mhw_footprint_view", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_footprint_view_is_deterministic(tmp_path):
    output = tmp_path / "footprint.svg"
    MODULE.build(output_path=output)
    assert output.read_bytes() == (ROOT / "figures" / "osw-d2-noaa-crw-mhw-footprint-20260801.svg").read_bytes()


def test_footprint_view_carries_claim_boundary_and_accessible_text(tmp_path):
    svg = MODULE.build(output_path=tmp_path / "footprint.svg")
    assert "41,025" in svg and "1,769" in svg
    assert "four-neighbor" in svg and "not yet a tracked volume" in svg
    assert "<title>" in svg and "<desc>" in svg
