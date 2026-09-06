import importlib.util
import json
import pathlib
import sys
import unittest


ANALYSIS = pathlib.Path(__file__).parent
sys.path.insert(0, str(ANALYSIS))
MODULE_PATH = ANALYSIS / "audit_region_membership_motion.py"
SPEC = importlib.util.spec_from_file_location("audit_region_membership_motion", MODULE_PATH)
membership = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(membership)


class RegionMembershipMotionTests(unittest.TestCase):
    def test_identical_signatures_agree(self):
        signature = {"seasonal_mean_vectors": [(1.0, 0.0, 1.0)] * 4}
        self.assertAlmostEqual(1.0, membership.signature_similarity(signature, signature))

    def test_committed_audit_covers_membership(self):
        root = ANALYSIS.parent
        payload = json.loads((root / "research" / "osw-motion-region-membership-2018.json").read_text(encoding="utf-8"))
        self.assertEqual(22, payload["summary"]["regions"])
        self.assertEqual(56, payload["summary"]["states"])
        self.assertIn("sampled_state_adjacencies", payload)
        for season in ("DJF", "MAM", "JJA", "SON"):
            self.assertIn(f"direction_similarity_{season}", payload["sampled_state_adjacencies"][0])


if __name__ == "__main__":
    unittest.main()
