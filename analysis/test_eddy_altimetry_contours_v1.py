import math
import unittest

import numpy as np

from eddy_altimetry_contours_v1 import GEOD, RADIUS_M, contour_candidates, demean


class ContourTests(unittest.TestCase):
    def setUp(self):
        self.lon = np.linspace(-92, -88, 161)
        self.lat = np.linspace(23, 27, 161)
        x, y = np.meshgrid(self.lon, self.lat)
        _, _, distance = GEOD.inv(np.full(x.size, -90.), np.full(y.size, 25.), x.ravel(), y.ravel())
        self.distance = np.asarray(distance).reshape(x.shape)
        self.z = 0.5 - 0.3 * (self.distance / 100000.) ** 2

    def test_known_spherical_circle_area_and_spans(self):
        loops, _ = contour_candidates(self.lon, self.lat, self.z, .2)
        self.assertEqual(len(loops), 1)
        row = loops[0][0]
        exact = 2 * math.pi * (RADIUS_M / 1000) ** 2 * (1 - math.cos(100000 / RADIUS_M))
        self.assertLess(abs(row['area_km2'] / exact - 1), .001)
        self.assertLess(abs(row['north_south_bounding_arc_km'] - 200), .1)
        self.assertLess(abs(row['east_west_bounding_arc_km_at_midlatitude'] - 200), .1)

    def test_open_cut_is_not_closed(self):
        loops, rejected = contour_candidates(self.lon[:85], self.lat, self.z[:, :85], .2)
        self.assertEqual(loops, [])
        self.assertGreater(rejected['open_or_degenerate'], 0)

    def test_missing_interior_is_rejected(self):
        z = self.z.copy(); z[80, 80] = np.nan
        loops, rejected = contour_candidates(self.lon, self.lat, z, .2)
        self.assertEqual(loops, [])
        self.assertGreater(rejected['missing_interior_or_no_sampled_interior'], 0)

    def test_low_interior_is_not_an_anticyclonic_candidate(self):
        loops, rejected = contour_candidates(self.lon, self.lat, -self.z, -.2)
        self.assertEqual(loops, [])
        self.assertGreater(rejected['low_interior'], 0)

    def test_daily_additive_offset_cancels(self):
        a, ma, n = demean(self.lon, self.lat, self.z)
        b, mb, m = demean(self.lon, self.lat, self.z + 4.)
        np.testing.assert_allclose(a, b, atol=1e-14)
        self.assertAlmostEqual(mb - ma, 4.)
        self.assertEqual(n, m)

    def test_weighting_and_domain_are_explicit(self):
        lon = np.linspace(-99.5, -79.5, 161)
        lat = np.linspace(16.5, 31.5, 121)
        z = np.broadcast_to(lat[:, None], (121, 161)).copy()
        _, plain, n = demean(lon, lat, z)
        _, weighted, m = demean(lon, lat, z, weighted=True)
        self.assertAlmostEqual(plain, 24.)
        self.assertLess(weighted, plain)
        self.assertEqual(n, m)

    def test_level_sensitivity_keeps_distinct_loops(self):
        areas = [contour_candidates(self.lon, self.lat, self.z, v)[0][0][0]['area_km2'] for v in [.15, .17, .19]]
        self.assertGreater(areas[0], areas[1]); self.assertGreater(areas[1], areas[2])


if __name__ == '__main__':
    unittest.main()
