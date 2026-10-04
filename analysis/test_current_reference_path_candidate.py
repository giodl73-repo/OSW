"""Numerical and geometry checks for editorial reference-route measurement."""
import math
import unittest
from shapely.geometry import LineString, box

from build_current_reference_path_candidate import display_coordinates, length_km, periodic_geometry


class ReferencePathTests(unittest.TestCase):
    def test_equatorial_degree_and_round_trip(self):
        expected = 6378137 * math.pi / 180 / 1000
        self.assertAlmostEqual(length_km([[0, 0], [1, 0]]), expected, places=8)
        self.assertAlmostEqual(length_km([[0, 0], [1, 0], [0, 0]]), 2 * expected, places=8)

    def test_waypoint_changes_length(self):
        direct = length_km([[0, 0], [2, 0]])
        route = [[0, 0], [1, 1], [2, 0]]
        self.assertGreater(length_km(route), direct)
        self.assertAlmostEqual(length_km(route), length_km(route[::-1]), places=8)

    def test_geodesic_display_bends_poleward(self):
        points = display_coordinates([[-20, 60], [20, 60]])
        self.assertGreater(len(points), 100)
        # North is smaller display y in the OSW equirectangular projection.
        self.assertLess(min(y for _, y in points), points[0][1] - 1)

    def test_invalid_or_ambiguous_geometry(self):
        for path in [[], [[0, 0]], [[0, 91], [1, 0]], [[float('nan'), 0], [1, 0]], [[179, 0], [-179, 0]]]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                length_km(path)

    def test_date_line_short_arc_and_continuous_display(self):
        path = [[179, 0], [-179, 0]]
        expected = 2 * 6378137 * math.pi / 180 / 1000
        self.assertAlmostEqual(length_km(path, allow_seam=True), expected, places=8)
        points = display_coordinates(path, allow_seam=True)
        self.assertAlmostEqual(points[-1][0] - points[0][0], 1480 * 2 / 360, places=8)
        self.assertTrue(all(abs(b[0] - a[0]) < 1 for a, b in zip(points, points[1:])))
        reverse = display_coordinates(path[::-1], allow_seam=True)
        self.assertAlmostEqual(reverse[-1][0] - reverse[0][0], -1480 * 2 / 360, places=8)

    def test_periodic_join_does_not_cross_unrelated_world(self):
        line = LineString(display_coordinates([[179, 0], [-179, 0]], allow_seam=True))
        east_edge = box(1535, 455, 1540, 465)
        west_edge = box(60, 455, 65, 465)
        atlantic = box(700, 455, 800, 465)
        self.assertGreater(line.intersection(periodic_geometry(east_edge)).length, 0)
        self.assertGreater(line.intersection(periodic_geometry(west_edge)).length, 0)
        self.assertEqual(line.intersection(periodic_geometry(atlantic)).length, 0)

    def test_ambiguous_half_world_leg_stays_rejected(self):
        with self.assertRaises(ValueError):
            length_km([[0, 10], [180, 10]], allow_seam=True)


if __name__ == "__main__":
    unittest.main()
