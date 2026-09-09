import importlib.util
import json
import pathlib
import unittest
import xml.etree.ElementTree as ET


PATH = pathlib.Path(__file__).with_name("build_oras5_drake_surface_budget_view.py")
SPEC = importlib.util.spec_from_file_location("build_oras5_drake_surface_budget_view", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)
PAYLOAD = json.loads((PATH.parent.parent / "research/osw-m4-oras5-drake-surface-budget-2018.json").read_text(encoding="utf-8"))


class DrakeSurfaceBudgetViewTests(unittest.TestCase):
    def test_svg_is_valid_and_keeps_partial_closure_honest(self):
        svg = module.build(PAYLOAD)
        ET.fromstring(svg)
        self.assertIn("THE SURFACE EXPLAINS PART — NOT ALL", svg)
        self.assertIn("+0.0427 PW", svg)
        self.assertIn("31%", svg)
        self.assertIn("Every interval remains positive", svg)
        for label in module.LABELS:
            self.assertIn(label, svg)


if __name__ == "__main__":
    unittest.main()
