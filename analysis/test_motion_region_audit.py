import importlib.util
import pathlib
import sys
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("audit_regions_against_motion.py")
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("audit_regions_against_motion", MODULE_PATH)
audit = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(audit)


class MotionRegionAuditTests(unittest.TestCase):
    def test_nearest_state_wraps_longitude(self):
        self.assertEqual(audit.nearest_state(-170, 30), audit.nearest_state(190, 30))

    def test_pair_diagnostics_aligned_crossing(self):
        left = [(1.0, 0.0, 1.0)] * 4
        right = [(1.0, 0.0, 1.0)] * 4
        crossing, similarity, contrast = audit.pair_diagnostics(left, right, "east-west")
        self.assertAlmostEqual(1.0, crossing)
        self.assertAlmostEqual(1.0, similarity)
        self.assertAlmostEqual(0.0, contrast)

    def test_pair_diagnostics_tangent(self):
        left = [(0.0, 1.0, 1.0)] * 4
        right = [(0.0, 1.0, 1.0)] * 4
        crossing, similarity, _ = audit.pair_diagnostics(left, right, "east-west")
        self.assertAlmostEqual(0.0, crossing)
        self.assertAlmostEqual(1.0, similarity)

    def test_pair_diagnostics_uses_declared_boundary_normal(self):
        vectors = [(1.0, 0.0, 1.0)] * 4
        crossing, _, _ = audit.pair_diagnostics(vectors, vectors, (0.0, 1.0))
        self.assertAlmostEqual(0.0, crossing)

    def test_boundary_normal_wraps_seed_longitude(self):
        normal = audit.boundary_normal("ALSK", "KURO")
        self.assertAlmostEqual(1.0, sum(value * value for value in normal), places=12)

    def test_seasonal_pair_diagnostics_preserves_seasons(self):
        left = [(1.0, 0.0, 1.0), (0.0, 1.0, 1.0)]
        right = list(left)
        values = audit.seasonal_pair_diagnostics(left, right, (1.0, 0.0))
        self.assertEqual(2, len(values))
        self.assertAlmostEqual(1.0, values[0][0])
        self.assertAlmostEqual(0.0, values[1][0])

    def test_orientation_diagnostics_separates_crossing_and_following(self):
        eastward = [(1.0, 0.0, 1.0)] * 4
        crossing = audit.pair_orientation_diagnostics(eastward, eastward, (1.0, 0.0))
        following = audit.pair_orientation_diagnostics(eastward, eastward, (0.0, 1.0))
        self.assertAlmostEqual(1.0, crossing[0])
        self.assertAlmostEqual(0.0, crossing[1])
        self.assertAlmostEqual(0.0, following[0])
        self.assertAlmostEqual(1.0, following[1])


if __name__ == "__main__":
    unittest.main()
