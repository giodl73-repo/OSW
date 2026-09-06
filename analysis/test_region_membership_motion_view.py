import pathlib
import unittest


class RegionMembershipMotionViewTests(unittest.TestCase):
    def test_committed_view_is_exposed(self):
        root = pathlib.Path(__file__).parent.parent
        svg = (root / "figures" / "osw-motion-region-membership-2018.svg").read_text(encoding="utf-8")
        self.assertIn('data-motion-level="region-membership-audit"', svg)
        self.assertIn("WHAT DISAGREES INSIDE THE 22?", svg)
        page = (root / "projections" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-motion-view="membership"', page)


if __name__ == "__main__":
    unittest.main()
