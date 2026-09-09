import pathlib
import unittest


class RegionMembershipSeasonsViewTests(unittest.TestCase):
    def test_committed_view_is_exposed(self):
        root = pathlib.Path(__file__).parent.parent
        svg = (root / "figures" / "osw-motion-region-membership-seasons-2018.svg").read_text(encoding="utf-8")
        self.assertIn('data-motion-level="membership-seasons"', svg)
        self.assertIn("DO THE INTERNAL SEAMS PERSIST?", svg)
        self.assertIn("0 PERSISTENTLY OPPOSED", svg)
        page = (root / "projections" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-motion-view="seam-seasons"', page)


if __name__ == "__main__":
    unittest.main()
