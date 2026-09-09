import importlib.util
import json
import pathlib
import unittest
import xml.etree.ElementTree as ET


PATH = pathlib.Path(__file__).with_name("build_oras5_drake_control_box_view.py")
SPEC = importlib.util.spec_from_file_location("build_oras5_drake_control_box_view", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)
PAYLOAD = json.loads((PATH.parent.parent / "research/osw-m4-oras5-drake-control-box-2018.json").read_text(encoding="utf-8"))


class DrakeControlBoxViewTests(unittest.TestCase):
    def test_svg_is_valid_and_refuses_accumulation_claim(self):
        svg = module.build(PAYLOAD)
        ET.fromstring(svg)
        for label in ("ONE GATE BECOMES FOUR", "IN 124.87 SV", "OUT 58.00 SV", "OUT 66.11 SV", "OUT 0.77 SV"):
            self.assertIn(label, svg)
        self.assertIn("DOES NOT YET MEAN ACCUMULATION", svg)
        self.assertIn("0.000203 PW", svg)


if __name__ == "__main__":
    unittest.main()
