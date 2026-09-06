import importlib.util
import json
import pathlib
import sys
import unittest


ANALYSIS = pathlib.Path(__file__).parent
sys.path.insert(0, str(ANALYSIS))
MODULE_PATH = ANALYSIS / "build_motion_region_audit_view.py"
SPEC = importlib.util.spec_from_file_location("build_motion_region_audit_view", MODULE_PATH)
view = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(view)


class MotionRegionAuditViewTests(unittest.TestCase):
    def test_score_bands_respect_support_floor(self):
        self.assertEqual(0, view.score_band(.9, 2))
        self.assertEqual(1, view.score_band(.30, 3))
        self.assertEqual(2, view.score_band(.45, 3))
        self.assertEqual(3, view.score_band(.55, 3))

    def test_committed_audit_artifacts(self):
        root = ANALYSIS.parent
        payload = json.loads((root / "research" / "osw-motion-region-audit-2018.json").read_text(encoding="utf-8"))
        svg = (root / "figures" / "osw-motion-region-audit-2018.svg").read_text(encoding="utf-8")
        self.assertEqual(759, payload["summary"]["supported_cells"])
        self.assertEqual(44, payload["summary"]["supported_boundary_pairs"])
        self.assertEqual(22, payload["summary"]["regions_with_supported_cells"])
        self.assertEqual("diagnostic audit; frozen zoning; no boundary revision", payload["status"])
        self.assertEqual("oceanlines.osw.motion-boundary-audit.v3", payload["schema"])
        for season in ("DJF", "MAM", "JJA", "SON"):
            self.assertIn(f"cut_through_{season}", payload["boundary_pairs"][0])
        self.assertIn('data-motion-level="boundary-audit"', svg)
        self.assertIn('data-zoning="frozen-audit"', svg)
        self.assertIn("DO THESE BORDERS HOLD?", svg)
        page = (root / "projections" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-motion-view="audit"', page)
        self.assertIn("../figures/osw-motion-region-audit-2018.svg", page)


if __name__ == "__main__":
    unittest.main()
