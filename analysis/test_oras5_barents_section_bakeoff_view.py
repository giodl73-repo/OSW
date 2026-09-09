import importlib.util
import json
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("build_oras5_barents_section_bakeoff_view.py")
SPEC = importlib.util.spec_from_file_location("build_oras5_barents_section_bakeoff_view", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)
ROOT = pathlib.Path(__file__).parents[1]


class BarentsSectionBakeoffViewTests(unittest.TestCase):
    def test_view_preserves_topology_and_semantic_difference(self):
        payload = json.loads((ROOT / "research/osw-m3-oras5-barents-section-bakeoff.json").read_text(encoding="utf-8"))
        svg = module.build(payload, ROOT / "atlas/data/oras5-arctic-entrances-mesh.nc")
        self.assertIn("TWO VALID LINES. TWO DIFFERENT QUESTIONS.", svg)
        self.assertIn("43 FACES · 23 U + 20 V", svg)
        self.assertIn("73 FACES · 36 U + 37 V", svg)
        self.assertIn("ZERO CORNER DUPLICATION", svg)
        self.assertIn("NOT THE OBSERVATIONAL BSO", svg)
        self.assertIn("NO VELOCITY, VOLUME, HEAT", svg)


if __name__ == "__main__":
    unittest.main()
