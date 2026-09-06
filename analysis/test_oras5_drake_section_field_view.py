import importlib.util
import json
import pathlib
import unittest
import xml.etree.ElementTree as ET


PATH = pathlib.Path(__file__).with_name("build_oras5_drake_section_field_view.py")
SPEC = importlib.util.spec_from_file_location("build_oras5_drake_section_field_view", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)
PAYLOAD = json.loads((PATH.parent.parent / "research/osw-m3-oras5-drake-section-field-2018.json").read_text(encoding="utf-8"))


class DrakeSectionFieldViewTests(unittest.TestCase):
    def test_svg_is_valid_and_preserves_section_orientation(self):
        svg = module.build(PAYLOAD)
        root = ET.fromstring(svg)
        self.assertEqual(4662, len(root.findall(".//{http://www.w3.org/2000/svg}rect[@data-cell]")))
        for label in ("ANTARCTIC PENINSULA / SOUTH", "SOUTH AMERICA / NORTH", "EASTWARD · OUT OF SECTION", "WESTWARD · INTO SECTION"):
            self.assertIn(label, svg)
        self.assertIn("NONLINEAR DEPTH DISPLAY", svg)


if __name__ == "__main__":
    unittest.main()
