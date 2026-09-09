import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("build_tracked_mhw_lineage_view.py")
SPEC = importlib.util.spec_from_file_location("build_tracked_mhw_lineage_view", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_lineage_view_is_deterministic(tmp_path):
    output = tmp_path / "lineage.svg"
    MODULE.build(output_path=output)
    assert output.read_bytes() == (ROOT / "figures" / "osw-d3-noaa-crw-mhw-lineage-2026.svg").read_bytes()


def test_lineage_view_exposes_break_and_semantic_boundary(tmp_path):
    svg = MODULE.build(output_path=tmp_path / "lineage.svg")
    assert "BREAK · 11 AUGUST" in svg
    assert "exact native pixels" in svg and "not parcels" in svg
    assert "<title>" in svg and "<desc>" in svg
