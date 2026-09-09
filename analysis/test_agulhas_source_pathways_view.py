import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("build_agulhas_source_pathways_view.py")
SPEC = importlib.util.spec_from_file_location("build_agulhas_source_pathways_view", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class AgulhasSourcePathwayViewTests(unittest.TestCase):
    def test_palette_keeps_unresolved_distinct(self):
        self.assertNotEqual(module.FATE_COLORS["unresolved"], module.FATE_COLORS["terminated"])
        self.assertEqual(5, len(set(module.FATE_COLORS.values())))

    def test_shipped_svg_states_count_boundary(self):
        path = pathlib.Path(__file__).parents[1] / "figures" / "osw-motion-agulhas-source-pathways-2018.svg"
        if not path.exists():
            self.skipTest("generated figure not built")
        svg = path.read_text(encoding="utf-8")
        self.assertIn("COUNTS · NOT LEAKAGE PERCENT", svg)
        self.assertIn("14 · 24 · 62 · 8", svg)
        self.assertIn("NINE DIFFERENT CENSUSES", svg)


if __name__ == "__main__":
    unittest.main()
