import importlib.util
import json
import pathlib
import unittest
import xml.etree.ElementTree as ET


PATH = pathlib.Path(__file__).with_name("build_oras5_drake_seasonal_view.py")
SPEC = importlib.util.spec_from_file_location("build_oras5_drake_seasonal_view", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)
PAYLOAD = json.loads((PATH.parent.parent / "research/osw-m3-oras5-drake-seasons-2018.json").read_text(encoding="utf-8"))


class DrakeSeasonalViewTests(unittest.TestCase):
    def test_svg_is_valid_and_contains_all_months_and_references(self):
        svg = module.build(PAYLOAD)
        ET.fromstring(svg)
        for label in ("FEBRUARY", "MAY", "AUGUST", "NOVEMBER", "Tref −1.9°C", "Tref 0°C", "Tref 5°C"):
            self.assertIn(label, svg)
        self.assertIn("THE NET LOOKS STEADIER THAN ITS BRANCHES", svg)
        self.assertIn("NOT AN ANNUAL MEAN", svg)


if __name__ == "__main__":
    unittest.main()
