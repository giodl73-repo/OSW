import pathlib
import xml.etree.ElementTree as ET


ROOT = pathlib.Path(__file__).parents[1]
SVG = ROOT / "figures/osw-m4-oras5-nordic-section-geometry.svg"


def test_geometry_plate_is_valid_and_names_all_sections() -> None:
    text = SVG.read_text(encoding="utf-8")
    ET.fromstring(text)
    for token in ("CLOSED ROOM NOW HAS DEPTH", "Denmark Strait", "Iceland–Scotland", "North Sea", "FRAM", "Norway–Svalbard"):
        assert token in text


def test_geometry_plate_preserves_method_boundary() -> None:
    text = SVG.read_text(encoding="utf-8")
    for token in ("ONLY FRAM IS A DEEP GATE", "internal mask/area consistency pass", "not independent production-thickness validation or transport"):
        assert token in text
