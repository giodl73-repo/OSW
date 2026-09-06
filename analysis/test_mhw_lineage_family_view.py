import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("build_mhw_lineage_family_view.py")
SPEC = importlib.util.spec_from_file_location("mhw_lineage_family_view", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_view_build_is_deterministic_and_accessible(tmp_path):
    first, second = tmp_path / "first.svg", tmp_path / "second.svg"
    svg = MODULE.build(output_path=first)
    MODULE.build(output_path=second)
    committed = ROOT / "figures" / "osw-d7-noaa-crw-mhw-lineage-family-2026.svg"
    assert first.read_bytes() == second.read_bytes()
    if committed.exists():
        assert first.read_bytes() == committed.read_bytes()
    assert "<title>" in svg and "<desc>" in svg
    assert "28" in svg and "29" in svg
    assert "5 terminate" in svg and "2 merge back" in svg
    assert "width = log(shared pixels)" in svg
    assert "TIME →" in svg
    assert "threshold-state genealogy" in svg
