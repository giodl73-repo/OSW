import importlib.util
import json
import pathlib
import unittest
import xml.etree.ElementTree as ET


PATH = pathlib.Path(__file__).with_name("build_oras5_drake_storage_probe_view.py")
SPEC = importlib.util.spec_from_file_location("build_oras5_drake_storage_probe_view", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)
PAYLOAD = json.loads((PATH.parent.parent / "research/osw-m4-oras5-drake-storage-probe-2018.json").read_text(encoding="utf-8"))


class DrakeStorageProbeViewTests(unittest.TestCase):
    def test_svg_is_valid_and_refuses_source_claim(self):
        svg = module.build(PAYLOAD)
        ET.fromstring(svg)
        self.assertIn("STORAGE ENTERS THE BUDGET / IT DOES NOT CLOSE IT", svg)
        self.assertIn("THE REMAINDER IS NOT A DISCOVERED HEAT SOURCE", svg)
        for value in ("−0.0157", "−0.0279", "+0.0031"):
            self.assertIn(value, svg.replace("-", "−"))


if __name__ == "__main__":
    unittest.main()
