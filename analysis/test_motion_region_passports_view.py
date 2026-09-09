import pathlib
import unittest


class MotionRegionPassportViewTests(unittest.TestCase):
    def test_committed_view_is_exposed(self):
        root = pathlib.Path(__file__).parent.parent
        svg = (root / "figures" / "osw-motion-region-passports-2018.svg").read_text(encoding="utf-8")
        self.assertIn('data-motion-level="region-passports"', svg)
        self.assertIn("22 REGIONS / FIVE MOTION QUESTIONS", svg)
        page = (root / "projections" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-motion-view="passports"', page)


if __name__ == "__main__":
    unittest.main()
