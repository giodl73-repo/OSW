import importlib.util
import json
import pathlib
import unittest
import xml.etree.ElementTree as ET


PATH = pathlib.Path(__file__).with_name("build_oras5_drake_transport_field_view.py")
SPEC = importlib.util.spec_from_file_location("build_oras5_drake_transport_field_view", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)
PAYLOAD = json.loads((PATH.parent.parent / "research/osw-m3-oras5-drake-section-field-2018.json").read_text(encoding="utf-8"))


class DrakeTransportFieldViewTests(unittest.TestCase):
    def test_svg_maps_both_contribution_fields_and_warns_about_resolution(self):
        svg = module.build(PAYLOAD)
        root = ET.fromstring(svg)
        self.assertEqual(9324, len(root.findall(".//{http://www.w3.org/2000/svg}rect[@data-transport-cell]")))
        self.assertIn("WHERE DOES THE TRANSPORT CROSS?", svg)
        self.assertIn("Per-cell intensity is resolution-dependent", svg)
        self.assertIn("124.185 SV", svg)
        self.assertIn("1.300 PW", svg)


if __name__ == "__main__":
    unittest.main()
