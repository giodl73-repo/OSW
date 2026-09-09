import importlib.util
import pathlib
import sys
import unittest


ANALYSIS = pathlib.Path(__file__).parent
sys.path.insert(0, str(ANALYSIS))
MODULE_PATH = ANALYSIS / "build_oscar_persistence_view.py"
SPEC = importlib.util.spec_from_file_location("build_oscar_persistence_view", MODULE_PATH)
view = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(view)


class OscarPersistenceViewTests(unittest.TestCase):
    def test_band_thresholds(self):
        self.assertEqual(0, view.persistence_band(0.1))
        self.assertEqual(1, view.persistence_band(0.5))
        self.assertEqual(2, view.persistence_band(0.9))

    def test_committed_persistence_receipt_and_svg(self):
        root = ANALYSIS.parent
        payload = view.load_payload(root / "atlas" / "data" / "oscar-persistence-2018.js")
        svg = (root / "figures" / "osw-motion-persistence-2018.svg").read_text(encoding="utf-8")
        self.assertEqual(11, len(payload["sample_times"]))
        self.assertEqual([31, 68], payload["shape"])
        self.assertEqual("45f38936174ce1c7ef8b79396512a3d27d53a77a3df40d25a761ea73211f2b54", payload["source_sha256"])
        self.assertIn('data-motion-level="sampled-persistence"', svg)
        self.assertIn('data-zoning="off"', svg)
        self.assertIn("DIRECTIONAL PERSISTENCE", svg)
        self.assertIn("Rendered vectors: 1180", svg)
        page = (root / "projections" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-motion-view="persistence"', page)
        self.assertIn("../figures/osw-motion-persistence-2018.svg", page)


if __name__ == "__main__":
    unittest.main()
