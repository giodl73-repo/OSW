import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("build_mhw_family_pruning_view.py")
SPEC = importlib.util.spec_from_file_location("mhw_family_pruning_view", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_view_build_is_deterministic_and_accessible(tmp_path):
    first, second = tmp_path / "first.svg", tmp_path / "second.svg"
    svg = MODULE.build(output_path=first)
    MODULE.build(output_path=second)
    committed = ROOT / "figures" / "osw-d8-noaa-crw-mhw-family-pruning-2026.svg"
    assert first.read_bytes() == second.read_bytes()
    if committed.exists():
        assert first.read_bytes() == committed.read_bytes()
    assert "<title>" in svg and "<desc>" in svg
    assert "every tested cutoff" in svg
    assert "21 trunk nodes" in svg
    assert "500 km² removes the merge" in svg
    assert "Small does not mean false" in svg
