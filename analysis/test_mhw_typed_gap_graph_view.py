import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).with_name("build_mhw_typed_gap_graph_view.py")
SPEC = importlib.util.spec_from_file_location("mhw_typed_gap_graph_view", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_view_build_is_deterministic_and_accessible(tmp_path):
    first, second = tmp_path / "first.svg", tmp_path / "second.svg"
    svg = MODULE.build(output_path=first)
    MODULE.build(output_path=second)
    committed = ROOT / "figures" / "osw-d9-noaa-crw-mhw-typed-gap-graph-2026.svg"
    assert first.read_bytes() == second.read_bytes()
    if committed.exists():
        assert first.read_bytes() == committed.read_bytes()
    assert "<title>" in svg and "<desc>" in svg
    assert "solid · consecutive active days" in svg
    assert "dashed · one inactive day" in svg
    assert "threshold-inactive day" in svg
    assert "28 nodes · 29 edges" in svg
    assert "35 nodes · 36 edges" in svg
    assert "orange marks = 5 split dates" in svg
    assert "not a complete post-gap branch-family" in svg
