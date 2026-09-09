import importlib.util
import json
import pathlib
import unittest
import xml.etree.ElementTree as ET


PATH = pathlib.Path(__file__).with_name("build_oras5_drake_method_sensitivity_view.py")
SPEC = importlib.util.spec_from_file_location("build_oras5_drake_method_sensitivity_view", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)
PAYLOAD = json.loads((PATH.parent.parent / "research/osw-m3-oras5-drake-method-sensitivity-2018.json").read_text(encoding="utf-8"))


class DrakeMethodSensitivityViewTests(unittest.TestCase):
    def test_svg_is_valid_and_keeps_method_dimensions_separate(self):
        svg = module.build(PAYLOAD)
        ET.fromstring(svg)
        for label in ("MOVE THE GATE", "MOVE TEMPERATURE TO THE FACE", "MEAN", "WEST", "EAST", "UPWIND"):
            self.assertIn(label, svg)
        self.assertIn("0.111 SV", svg)
        self.assertIn("METHOD SENSITIVITY, NOT OBSERVATIONAL UNCERTAINTY", svg)


if __name__ == "__main__":
    unittest.main()
