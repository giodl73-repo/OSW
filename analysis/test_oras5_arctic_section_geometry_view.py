import importlib.util
import json
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("build_oras5_arctic_section_geometry_view.py")
SPEC = importlib.util.spec_from_file_location("build_oras5_arctic_section_geometry_view", PATH)
module = importlib.util.module_from_spec(SPEC); assert SPEC.loader; SPEC.loader.exec_module(module)
ROOT = pathlib.Path(__file__).parents[1]


class ArcticSectionGeometryViewTests(unittest.TestCase):
    def test_view_keeps_area_separate_from_transport(self):
        payload = json.loads((ROOT / "research/osw-m3-oras5-arctic-section-geometry-audit.json").read_text(encoding="utf-8"))
        svg = module.build(payload)
        self.assertIn("SAME GRID. THREE DIFFERENT CROSS-SECTIONS.", svg)
        self.assertIn("814 km²", svg)
        self.assertIn("161 km²", svg)
        self.assertIn("224 km²", svg)
        self.assertIn("LONGER DOES NOT MEAN DEEPER", svg)
        self.assertIn("NO VELOCITY OR HEAT", svg)


if __name__ == "__main__":
    unittest.main()
