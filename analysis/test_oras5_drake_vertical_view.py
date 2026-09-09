import importlib.util
import json
import pathlib
import unittest
import xml.etree.ElementTree as ET


PATH = pathlib.Path(__file__).with_name("build_oras5_drake_vertical_view.py")
SPEC = importlib.util.spec_from_file_location("build_oras5_drake_vertical_view", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)
PAYLOAD = json.loads((PATH.parent.parent / "research/osw-m3-oras5-drake-vertical-2018.json").read_text(encoding="utf-8"))


class DrakeVerticalViewTests(unittest.TestCase):
    def test_svg_is_valid_and_declares_depth_contract(self):
        svg = module.build(PAYLOAD)
        ET.fromstring(svg)
        for label in ("0–200 m", "200–700 m", "700–1500 m", "1500–3000 m", "&gt;3000 m"):
            self.assertIn(label, svg)
        self.assertIn("THE WATER IS DEEP / THE HEAT SIGNAL IS SHALLOWER", svg)
        self.assertIn("NOT WATER MASSES", svg)


if __name__ == "__main__":
    unittest.main()
