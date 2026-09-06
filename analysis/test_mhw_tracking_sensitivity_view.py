import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("build_mhw_tracking_sensitivity_view.py")
SPEC = importlib.util.spec_from_file_location("mhw_tracking_sensitivity_view", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_view_build_is_deterministic_and_accessible(tmp_path):
    first = tmp_path / "first.svg"
    second = tmp_path / "second.svg"
    svg = MODULE.build(output_path=first)
    MODULE.build(output_path=second)
    committed = ROOT / "figures" / "osw-d5-noaa-crw-mhw-tracking-sensitivity-2026.svg"
    assert first.read_bytes() == second.read_bytes()
    if committed.exists():
        assert first.read_bytes() == committed.read_bytes()
    assert "<title>" in svg and "<desc>" in svg
    assert "SHAPES DIFFER BY ≤ 1 CELL" in svg
    assert "ALL FIVE LIFETIMES MATCH" in svg
    assert "18-day stable plateau" in svg
    assert "IoU = 0.198" in svg
    assert "IoU = shared cells / union" in svg
    assert "NOAA CRW Marine Heatwave Watch v1.0.1" in svg
