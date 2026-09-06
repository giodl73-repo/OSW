import pathlib
import unittest


class RegionMembershipSeamsViewTests(unittest.TestCase):
    def test_committed_view_is_exposed(self):
        root = pathlib.Path(__file__).parent.parent
        svg = (root / "figures" / "osw-motion-region-membership-seams-2018.svg").read_text(encoding="utf-8")
        self.assertIn('data-motion-level="membership-seams"', svg)
        self.assertIn("WHICH INTERNAL SEAMS DISAGREE?", svg)
        page = (root / "projections" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-motion-view="seams"', page)


if __name__ == "__main__":
    unittest.main()
