import importlib.util
import json
import pathlib
import unittest
import xml.etree.ElementTree as ET


PATH = pathlib.Path(__file__).with_name("build_oras5_drake_control_box_sensitivity_view.py")
SPEC = importlib.util.spec_from_file_location("build_oras5_drake_control_box_sensitivity_view", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)
PAYLOAD = json.loads((PATH.parent.parent / "research/osw-m4-oras5-drake-control-box-sensitivity-2018.json").read_text(encoding="utf-8"))


class DrakeControlBoxSensitivityViewTests(unittest.TestCase):
    def test_svg_is_valid_and_rejects_universal_residual(self):
        svg = module.build(PAYLOAD)
        ET.fromstring(svg)
        self.assertIn("THE BOX CLOSES / THE HEAT RESIDUAL MOVES", svg)
        self.assertIn("0.0336 PW", svg)
        self.assertIn("0.0535 PW", svg)
        self.assertIn("&lt; 0.010 SV", svg)
        self.assertIn("not to “Drake Passage” as a universal", svg)


if __name__ == "__main__":
    unittest.main()
