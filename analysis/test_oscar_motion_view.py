import importlib.util
import pathlib
import sys
import unittest


ANALYSIS = pathlib.Path(__file__).parent
sys.path.insert(0, str(ANALYSIS))
MODULE_PATH = ANALYSIS / "build_oscar_motion_view.py"
SPEC = importlib.util.spec_from_file_location("build_oscar_motion_view", MODULE_PATH)
motion = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(motion)


class OscarMotionViewTests(unittest.TestCase):
    def test_render_is_zoning_free_and_declares_limits(self):
        payload = {
            "shape": [2, 2], "latitude_values": [20, 0], "longitude_values": [140, 160],
            "u_mm_s": [100, 300, -500, None], "v_mm_s": [0, 100, 200, None],
            "source": "test source", "source_sha256": "a" * 64, "date": "2018-11-16",
            "query_url": "https://example.test/query",
            "boundary": "Not full-depth velocity or ocean heat transport.",
        }
        svg = motion.render(payload, {"type": "FeatureCollection", "features": []}, "b" * 64)
        self.assertIn('data-zoning="off"', svg)
        self.assertIn("ZONING OFF · WATER PRIMARY", svg)
        self.assertIn("DO NOT READ", svg)
        self.assertIn("Not full-depth velocity or ocean heat transport.", svg)
        self.assertNotIn("data-state-count", svg)

    def test_committed_pilot_has_pinned_provenance(self):
        root = ANALYSIS.parent
        payload = motion.load_payload(root / "atlas" / "data" / "oscar-historical-2018-11-16.js")
        self.assertEqual("2018-11-16", payload["date"])
        self.assertEqual([31, 68], payload["shape"])
        self.assertEqual("08b8d922b60bcf2fe292b5eb1c4f7a826c73710b586b9ae983e3557f18281a1c", payload["source_sha256"])
        self.assertEqual(15, payload["nominal_depth_m"])
        self.assertIn("not OSCAR v2.0", payload["boundary"])

    def test_projection_laboratory_exposes_motion_plate(self):
        root = ANALYSIS.parent
        page = (root / "projections" / "index.html").read_text(encoding="utf-8")
        svg = (root / "figures" / "osw-motion-surface-historical-pilot.svg").read_text(encoding="utf-8")
        self.assertIn('class="motion-study"', page)
        self.assertIn("../figures/osw-motion-surface-historical-pilot.svg", page)
        self.assertIn('data-zoning="off"', svg)
        self.assertIn("Rendered vectors: 1203", svg)
        self.assertNotIn("data-state-count", svg)


if __name__ == "__main__":
    unittest.main()
