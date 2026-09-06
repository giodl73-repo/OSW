import importlib.util
import json
import pathlib
import unittest
import xml.etree.ElementTree as ET


PATH = pathlib.Path(__file__).with_name("build_oras5_arctic_seasons_view.py")
SPEC = importlib.util.spec_from_file_location("build_oras5_arctic_seasons_view", PATH)
module = importlib.util.module_from_spec(SPEC); assert SPEC.loader; SPEC.loader.exec_module(module)
ROOT = pathlib.Path(__file__).parents[1]


class ArcticSeasonsViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        payload = json.loads((ROOT / "research/osw-m3-oras5-arctic-seasons-2018.json").read_text(encoding="utf-8"))
        cls.svg = module.build(payload)

    def test_svg_is_valid_and_contains_all_sections_and_months(self):
        ET.fromstring(self.svg)
        for token in ("FRAM STRAIT", "FUGLØYA–BEAR PROXY", "NORWAY–SVALBARD CLOSURE", "FEB", "MAY", "AUG", "NOV"):
            self.assertIn(token, self.svg)

    def test_central_sign_result_and_boundary_are_explicit(self):
        for token in ("Net volume is southward", "heat signal positive", "not an annual mean", "not convergence"):
            self.assertIn(token, self.svg)


if __name__ == "__main__":
    unittest.main()
