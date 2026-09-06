import pathlib
import unittest


class MotionPartitionRobustnessViewTests(unittest.TestCase):
    def test_committed_view_is_exposed(self):
        root = pathlib.Path(__file__).parent.parent
        svg = (root / "figures" / "osw-motion-partition-robustness-2018.svg").read_text(encoding="utf-8")
        self.assertIn('data-motion-level="partition-robustness"', svg)
        self.assertIn("THE COUNT DOES NOT SURVIVE THE METHOD", svg)
        page = (root / "projections" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-motion-view="robustness"', page)


if __name__ == "__main__":
    unittest.main()
