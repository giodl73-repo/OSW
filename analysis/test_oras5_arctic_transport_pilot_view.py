import importlib.util
import json
import pathlib
import unittest
import xml.etree.ElementTree as ET


PATH = pathlib.Path(__file__).with_name("build_oras5_arctic_transport_pilot_view.py")
SPEC = importlib.util.spec_from_file_location("build_oras5_arctic_transport_pilot_view", PATH)
module = importlib.util.module_from_spec(SPEC); assert SPEC.loader; SPEC.loader.exec_module(module)
ROOT = pathlib.Path(__file__).parents[1]


class ArcticTransportPilotViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        payload = json.loads((ROOT / "research/osw-m3-oras5-arctic-transport-pilot-201802.json").read_text(encoding="utf-8"))
        cls.svg = module.build(payload)

    def test_svg_is_valid_and_names_all_sections(self):
        ET.fromstring(self.svg)
        for token in ("FRAM STRAIT", "FUGLØYA–BEAR PROXY", "NORWAY–SVALBARD CLOSURE"):
            self.assertIn(token, self.svg)

    def test_view_keeps_heat_and_section_semantics_bounded(self):
        for token in ("REFERENCE-RELATIVE HEAT", "endpoint/domain difference", "not gateway convergence"):
            self.assertIn(token, self.svg)


if __name__ == "__main__":
    unittest.main()
