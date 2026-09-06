import importlib.util
import pathlib
import sys
import unittest


ANALYSIS = pathlib.Path(__file__).parent
sys.path.insert(0, str(ANALYSIS))
MODULE_PATH = ANALYSIS / "build_motion_border_orientation_view.py"
SPEC = importlib.util.spec_from_file_location("build_motion_border_orientation_view", MODULE_PATH)
view = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(view)


class MotionBorderOrientationViewTests(unittest.TestCase):
    def test_margin_bands_are_diverging(self):
        self.assertEqual(0, view.margin_band(-.2))
        self.assertEqual(2, view.margin_band(0))
        self.assertEqual(4, view.margin_band(.2))

    def test_committed_view_is_exposed(self):
        root = ANALYSIS.parent
        svg = (root / "figures" / "osw-motion-border-orientation-2018.svg").read_text(encoding="utf-8")
        self.assertIn('data-motion-level="border-orientation"', svg)
        self.assertIn("WHERE FLOW LEANS ALONG / LEANS ACROSS", svg)
        page = (root / "projections" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-motion-view="orientation"', page)


if __name__ == "__main__":
    unittest.main()
