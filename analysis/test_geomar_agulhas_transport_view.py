import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("build_geomar_agulhas_transport_view.py")
SPEC = importlib.util.spec_from_file_location("build_geomar_agulhas_transport_view", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class GeomarAgulhasTransportViewTests(unittest.TestCase):
    def test_shipped_svg_preserves_attribution_and_values(self):
        path = pathlib.Path(__file__).parents[1] / "figures" / "osw-m3-geomar-agulhas-published-replication.svg"
        if not path.exists():
            self.skipTest("generated figure not built")
        svg = path.read_text(encoding="utf-8")
        self.assertIn("ATTRIBUTED MODEL OUTPUT · CC BY 4.0", svg)
        self.assertIn("9.894 Sv", svg)
        self.assertIn("40.02 Sv", svg)
        self.assertIn("WEST + NORTHWEST = LEAKAGE", svg)
        self.assertIn("AN OSW MODEL RUN", svg)


if __name__ == "__main__":
    unittest.main()
