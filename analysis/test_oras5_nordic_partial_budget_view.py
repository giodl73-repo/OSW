import pathlib
import xml.etree.ElementTree as ET


ROOT = pathlib.Path(__file__).parents[1]
SVG = ROOT / "figures/osw-m4-oras5-nordic-partial-budget-2018.svg"


def test_partial_budget_plate_is_valid_and_states_central_result() -> None:
    text = SVG.read_text(encoding="utf-8")
    ET.fromstring(text)
    for token in ("OFFLINE ROOM BUDGET DOES NOT CLOSE", "+96.8 TW advective convergence", "-106.8 TW surface input", "+37.7 TW mean unresolved remainder"):
        assert token in text


def test_partial_budget_plate_preserves_method_and_mass_boundaries() -> None:
    text = SVG.read_text(encoding="utf-8")
    for token in ("−0.064 to +0.074 Sv", "Small is not zero", "monthly-mean offline velocity", "remainder retains ice"):
        assert token in text
