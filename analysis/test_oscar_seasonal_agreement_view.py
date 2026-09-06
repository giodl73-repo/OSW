import importlib.util
import pathlib
import sys
import unittest


ANALYSIS = pathlib.Path(__file__).parent
sys.path.insert(0, str(ANALYSIS))
MODULE_PATH = ANALYSIS / "build_oscar_seasonal_agreement_view.py"
SPEC = importlib.util.spec_from_file_location("build_oscar_seasonal_agreement_view", MODULE_PATH)
view = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(view)


class OscarSeasonalAgreementViewTests(unittest.TestCase):
    def test_turn_palette_endpoints(self):
        self.assertEqual("#41cfc2", view.turn_color(0))
        self.assertEqual("#e2507e", view.turn_color(180))

    def test_committed_agreement_artifacts(self):
        root = ANALYSIS.parent
        payload = view.load_payload(root / "atlas" / "data" / "oscar-seasonal-agreement-2018.js")
        svg = (root / "figures" / "osw-motion-seasonal-agreement-2018.svg").read_text(encoding="utf-8")
        self.assertEqual(759, payload["summary"]["valid_cells"])
        self.assertEqual(402, payload["summary"]["aligned_candidate_cells"])
        self.assertEqual(288, payload["summary"]["turning_candidate_cells"])
        self.assertEqual("94716c1dcf21188c1dad651562ae4c57297bc63bae82a929e9b00b42956e4ea0", payload["source_data_sha256"])
        self.assertEqual("bb1aa2d76de6bc6438114561f8d2401b2c88f24c5b00a521bbf324d354c9ec15", payload["source_artifact_sha256"])
        self.assertIn('data-motion-level="cross-season-agreement"', svg)
        self.assertIn('data-zoning="off"', svg)
        self.assertIn("WHAT HOLDS", svg)
        self.assertIn("WHAT TURNS", svg)
        page = (root / "projections" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-motion-view="skeleton"', page)
        self.assertIn("../figures/osw-motion-seasonal-agreement-2018.svg", page)


if __name__ == "__main__":
    unittest.main()
