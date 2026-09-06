import importlib.util
import json
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("build_agulhas_motion_view.py")
SPEC = importlib.util.spec_from_file_location("build_agulhas_motion_view", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class AgulhasMotionViewTests(unittest.TestCase):
    def test_role_palette_is_complete(self):
        self.assertEqual(
            {"boundary-current", "retroflection", "return-current", "cape-basin"},
            set(module.ROLE_COLORS),
        )

    def test_shipped_svg_exposes_contract_and_roles(self):
        path = pathlib.Path(__file__).parents[1] / "figures" / "osw-motion-agulhas-junction-2018.svg"
        if not path.exists():
            self.skipTest("generated figure not built")
        svg = path.read_text(encoding="utf-8")
        self.assertIn("PATHWAYS · NOT HEAT TRANSPORT", svg)
        self.assertIn("CURRENT TURNS", svg)
        self.assertIn("LEAKAGE FIELD", svg)
        self.assertIn("10.1038/nature09983", svg)


if __name__ == "__main__":
    unittest.main()
