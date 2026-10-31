import math
import unittest
import chen_indian_sec_regional_ridge_lengths_v1 as subject


class RegionalLengthGuards(unittest.TestCase):
    def test_wgs84_equatorial_reference(self):
        self.assertAlmostEqual(subject.polyline_km([(0,0),(1,0)]),111.319490793,places=8)

    def test_every_resolution_phase_keeps_both_gates(self):
        for count in [2,7,18]:
            for stride in subject.STRIDES:
                for phase in range(stride):
                    indices=subject.selected_indices(count,stride,phase)
                    self.assertEqual(indices[0],0);self.assertEqual(indices[-1],count-1)
                    self.assertEqual(indices,sorted(set(indices)))

    def test_all_native_vertices_and_all_declared_scenarios_retained(self):
        points=[(i,-10+(i%2)*.2) for i in range(10)]
        rows=subject.scenarios(points)
        self.assertEqual(len(rows),15)
        self.assertEqual(rows[0]['retained_vertices'],10)
        self.assertAlmostEqual(rows[0]['length_km'],subject.polyline_km(points))
        self.assertTrue(all(r['length_km']>0 for r in rows))

    def test_coarser_chord_is_not_claimed_as_physical_bound(self):
        points=[(0,0),(.5,1),(1,0)]
        self.assertGreater(subject.polyline_km(points),subject.polyline_km([points[0],points[-1]]))

    def test_invalid_geometry_and_ambiguous_legs_refused(self):
        for points in [[],[(0,0)],[(0,math.nan),(1,0)],[(0,91),(1,0)],[(179,0),(-179,0)]]:
            with self.assertRaises(ValueError):subject.polyline_km(points)

    def test_rounding_and_invalid_resolution(self):
        self.assertEqual(subject.nearest_100(4450),4500)
        with self.assertRaises(ValueError):subject.selected_indices(20,3,0)
        with self.assertRaises(ValueError):subject.selected_indices(20,4,4)


if __name__=='__main__':unittest.main()
