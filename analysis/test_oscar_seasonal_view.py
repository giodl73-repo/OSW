import importlib.util
import pathlib
import sys
import unittest


ANALYSIS = pathlib.Path(__file__).parent
sys.path.insert(0, str(ANALYSIS))
MODULE_PATH = ANALYSIS / "build_oscar_seasonal_view.py"
SPEC = importlib.util.spec_from_file_location("build_oscar_seasonal_view", MODULE_PATH)
view = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(view)


class OscarSeasonalViewTests(unittest.TestCase):
    def test_committed_seasonal_artifacts(self):
        root = ANALYSIS.parent
        payload = view.load_payload(root / "atlas" / "data" / "oscar-seasons-2018.js")
        svg = (root / "figures" / "osw-motion-seasons-2018.svg").read_text(encoding="utf-8")
        self.assertEqual(["DJF", "MAM", "JJA", "SON"], payload["season_order"])
        self.assertEqual([18, 18, 18, 17], [len(payload["seasons"][item]["sample_times"]) for item in payload["season_order"]])
        self.assertEqual("94716c1dcf21188c1dad651562ae4c57297bc63bae82a929e9b00b42956e4ea0", payload["source_sha256"])
        self.assertIn('data-motion-level="seasonal-persistence"', svg)
        self.assertIn('data-zoning="off"', svg)
        for season in payload["season_order"]:
            self.assertIn(f'aria-label="{season} surface motion"', svg)
        page = (root / "projections" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-motion-view="seasons"', page)
        self.assertIn("../figures/osw-motion-seasons-2018.svg", page)


if __name__ == "__main__":
    unittest.main()
