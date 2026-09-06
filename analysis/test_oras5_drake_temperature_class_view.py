import importlib.util
import json
import pathlib
import unittest
import xml.etree.ElementTree as ET


PATH = pathlib.Path(__file__).with_name("build_oras5_drake_temperature_class_view.py")
SPEC = importlib.util.spec_from_file_location("build_oras5_drake_temperature_class_view", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)
PAYLOAD = json.loads((PATH.parent.parent / "research/osw-m3-oras5-drake-temperature-classes-2018.json").read_text(encoding="utf-8"))


class DrakeTemperatureClassViewTests(unittest.TestCase):
    def test_svg_is_valid_and_refuses_water_mass_claim(self):
        svg = module.build(PAYLOAD)
        ET.fromstring(svg)
        for label in ("&lt;0°C", "0–1°C", "1–2°C", "2–3°C", "3–5°C", "&gt;5°C"):
            self.assertIn(label, svg)
        self.assertIn("THE RETURN FLOW IS COLDER", svg)
        self.assertIn("TEMPERATURE CLASSES ARE NOT WATER MASSES", svg)


if __name__ == "__main__":
    unittest.main()
