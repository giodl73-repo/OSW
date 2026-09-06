import importlib.util
import json
import pathlib
import unittest
import xml.etree.ElementTree as ET


PATH = pathlib.Path(__file__).with_name("build_arctic_entrances_motion_view.py")
SPEC = importlib.util.spec_from_file_location("build_arctic_entrances_motion_view", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)
ROOT = PATH.parent.parent


class ArcticEntrancesMotionViewTests(unittest.TestCase):
    def test_generated_artifact_is_valid_and_keeps_two_way_fram_claim(self):
        svg = (ROOT / "figures/osw-motion-arctic-entrances-2018.svg").read_text(encoding="utf-8")
        ET.fromstring(svg)
        self.assertIn("ONE ARCTIC ENTRANCE IS REALLY TWO", svg)
        self.assertIn("FRAM WEST · SOUTHWARD EXPORT", svg)
        self.assertIn("FRAM EAST · NORTHWARD INFLOW", svg)
        self.assertIn("SURFACE MOTION · NOT HEAT TRANSPORT", svg)


if __name__ == "__main__":
    unittest.main()
