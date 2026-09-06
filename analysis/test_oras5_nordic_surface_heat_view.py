import pathlib
import xml.etree.ElementTree as ET


ROOT = pathlib.Path(__file__).parents[1]
SVG = ROOT / "figures/osw-m4-oras5-nordic-surface-heat-2018.svg"


def test_surface_heat_plate_is_valid_and_states_the_result() -> None:
    text = SVG.read_text(encoding="utf-8")
    ET.fromstring(text)
    for token in ("ROOM BREATHES HEAT", "-39.4 W/m²", "-106.8 TW", "-3.37 ZJ", "SUMMER UPTAKE"):
        assert token in text


def test_surface_heat_plate_preserves_the_boundary() -> None:
    text = SVG.read_text(encoding="utf-8")
    for token in ("surface exchange", "not advective convergence", "not a climatology", "exact 12,550-cell"):
        assert token in text
