import pathlib
import unittest
import xml.etree.ElementTree as ET


ROOT = pathlib.Path(__file__).parents[1]
SVG = ROOT / "figures/osw-m4-nordic-seas-budget-contract.svg"


class NordicSeasBudgetContractViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.svg = SVG.read_text(encoding="utf-8")

    def test_svg_is_valid_and_names_every_boundary_role(self):
        ET.fromstring(self.svg)
        for token in (
            "NORDIC SEAS",
            "FRAM",
            "BARENTS",
            "DENMARK",
            "ICELAND–SCOTLAND RIDGE",
            "NORTH SEA",
        ):
            self.assertIn(token, self.svg)

    def test_readiness_and_nonresult_boundary_are_explicit(self):
        for token in (
            "7 PASS / 1 OPEN",
            "faint orange shows the rejected Faroe split",
            "native tracer-budget terms remain open",
        ):
            self.assertIn(token, self.svg)


if __name__ == "__main__":
    unittest.main()
