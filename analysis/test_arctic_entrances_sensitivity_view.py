import importlib.util
import json
import pathlib
import unittest
import xml.etree.ElementTree as ET


PATH = pathlib.Path(__file__).with_name("build_arctic_entrances_sensitivity_view.py")
SPEC = importlib.util.spec_from_file_location("build_arctic_entrances_sensitivity_view", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)
PAYLOAD = json.loads((PATH.parent.parent / "research/osw-m2-arctic-entrances-sensitivity-2018.json").read_text(encoding="utf-8"))


class ArcticEntrancesSensitivityViewTests(unittest.TestCase):
    def test_svg_is_valid_and_exposes_fram_dependence(self):
        svg = module.build(PAYLOAD)
        ET.fromstring(svg)
        self.assertIn("FRAM INFLOW MOVES WITH THE SCREEN", svg)
        self.assertIn("20 / 30", svg)
        self.assertIn("18 / 18", svg)
        self.assertIn("11 / 11", svg)
        self.assertIn("One latitude cannot stand for the whole gateway", svg)


if __name__ == "__main__":
    unittest.main()
