import importlib.util
import json
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("build_oras5_barents_section_sensitivity_view.py")
SPEC = importlib.util.spec_from_file_location("build_oras5_barents_section_sensitivity_view", PATH)
module = importlib.util.module_from_spec(SPEC); assert SPEC.loader; SPEC.loader.exec_module(module)
ROOT = pathlib.Path(__file__).parents[1]


class BarentsSectionSensitivityViewTests(unittest.TestCase):
    def test_view_keeps_method_sensitivity_out_of_physical_uncertainty(self):
        payload = json.loads((ROOT / "research/osw-m3-oras5-barents-section-sensitivity.json").read_text(encoding="utf-8"))
        svg = module.build(payload)
        self.assertIn("THE COST RULE HOLDS. THE ANCHORS MOVE THE LINE.", svg)
        self.assertIn("9 PATHS · 39–49 FACES", svg)
        self.assertIn("6 PATHS · 73–74 FACES", svg)
        self.assertIn("ALL 9 ENDPOINT CASES SCALE-INVARIANT", svg)
        self.assertIn("NO VELOCITY, TRANSPORT, HEAT", svg)


if __name__ == "__main__":
    unittest.main()
