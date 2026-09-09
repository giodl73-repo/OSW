import importlib.util
import json
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis" / "build_ocean_object_matrix.py"
SVG = ROOT / "figures" / "osw-ocean-object-matrix.svg"
SUMMARY = ROOT / "research" / "ocean-object-matrix-summary.json"


def load_builder():
    spec = importlib.util.spec_from_file_location("object_matrix", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_object_matrix_contract():
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert summary["object_count"] == 116
    assert summary["type_count"] == 13
    assert sum(summary["counts_by_type"].values()) == 116
    assert len(summary["identity_tests"]) == 24
    text = SVG.read_text(encoding="utf-8")
    assert "CONCEPTUAL MATRIX · NOT A MAP OR NATURAL HIERARCHY" in text
    assert "guides/13-HOW-TO-NAME-AN-OCEAN-PATCH.md" in text
    assert text.count('role="group"') >= 4
    root = ET.fromstring(text)
    assert root.attrib["viewBox"] == "0 0 1600 1100"


def test_object_matrix_build_is_deterministic(tmp_path):
    builder = load_builder()
    svg_a, json_a = tmp_path / "a.svg", tmp_path / "a.json"
    svg_b, json_b = tmp_path / "b.svg", tmp_path / "b.json"
    builder.build(svg_a, json_a)
    builder.build(svg_b, json_b)
    assert svg_a.read_bytes() == svg_b.read_bytes() == SVG.read_bytes()
    assert json_a.read_bytes() == json_b.read_bytes() == SUMMARY.read_bytes()
