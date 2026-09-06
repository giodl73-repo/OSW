import importlib.util
import json
import pathlib
import unittest
import xml.etree.ElementTree as ET


PATH = pathlib.Path(__file__).with_name("build_oras5_drake_monthly_budget_view.py")
SPEC = importlib.util.spec_from_file_location("build_oras5_drake_monthly_budget_view", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)
PAYLOAD = json.loads((PATH.parent.parent / "research/osw-m4-oras5-drake-monthly-budget-2018.json").read_text(encoding="utf-8"))


class DrakeMonthlyBudgetViewTests(unittest.TestCase):
    def test_svg_is_valid_and_preserves_unclosed_claim(self):
        svg = module.build(PAYLOAD)
        ET.fromstring(svg)
        self.assertIn("TWELVE MONTHS / THE GAP PERSISTS", svg)
        self.assertIn("+0.0622 PW", svg)
        self.assertIn("every interval retains a positive unclosed remainder", svg)
        for label in module.LABELS:
            self.assertIn(label, svg)


if __name__ == "__main__":
    unittest.main()
