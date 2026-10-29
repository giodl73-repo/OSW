"""Synthetic operator/refusal tests; no source fields or installed engine reads."""
import math
import unittest
from unittest.mock import patch
import pacific_nec_monthly_dimensions_v1 as diagnostic


class MonthlyDimensionOperators(unittest.TestCase):
    def setUp(self):self.latitude=list(range(4,27))

    def test_uniform_westward_window_centroid_and_vector(self):
        result=diagnostic.axis_profile(self.latitude,[-.2]*23,[.03]*23)
        self.assertIsNone(result['reason'])
        self.assertAlmostEqual(result['latitude'],13)
        self.assertAlmostEqual(result['westward_share'],1)
        self.assertAlmostEqual(result['eastward_m_s'],-.2)
        self.assertAlmostEqual(result['northward_m_s'],.03)

    def test_missing_and_mixed_direction_do_not_create_axis(self):
        for case in ('missing','eastward','weak','mixed','two_lobes'):
            u=[-.2]*23;v=[0]*23
            if case=='missing':v[9]=math.nan
            elif case=='eastward':u=[.2]*23
            elif case=='weak':u=[-.001]*23
            elif case=='mixed':u=[-.2 if y<13 else .2 for y in self.latitude]
            else:
                u=[-.2 if y in (9,10,16,17) else .0001 for y in self.latitude]
            with self.subTest(case=case):
                result=diagnostic.axis_profile(self.latitude,u,v)
                self.assertIsNotNone(result['reason'])
                self.assertIsNone(result['latitude'])

    def test_connected_edges_and_thresholds_are_different_quantities(self):
        u=[(abs(y-13)-3)/10 for y in self.latitude]
        broad=diagnostic.section_span(self.latitude,u)
        core=diagnostic.section_span(self.latitude,u,.05)
        self.assertIsNone(broad['reason']);self.assertIsNone(core['reason'])
        self.assertEqual((broad['south_latitude'],broad['north_latitude']),(10,16))
        self.assertEqual((core['south_latitude'],core['north_latitude']),(10.5,15.5))

    def test_censored_missing_tied_and_weak_spans_withheld(self):
        for case in ('censored','missing','tie','weak'):
            u=[(abs(y-13)-3)/10 for y in self.latitude]
            if case=='censored':u=[-.2]*23;u[9]=-.3
            elif case=='missing':u[11]=math.nan
            elif case=='tie':u[10]=u[9]
            else:u=[.02]*23;u[9]=-.04
            with self.subTest(case=case):
                result=diagnostic.section_span(self.latitude,u)
                self.assertIsNotNone(result['reason'])

    def test_full_gate_requirement_and_no_bridging_rejected_columns(self):
        profiles=[{'latitude':13,'reason':None} for _ in range(3)]
        result=diagnostic.axis_length([179,180,181],profiles,lambda *args:1)
        self.assertEqual(result['length_km'],2)
        profiles[1]={'latitude':None,'reason':'missing_monthly_vector_in_window'}
        result=diagnostic.axis_length([179,180,181],profiles,lambda *args:self.fail('Must not bridge gap'))
        self.assertIsNone(result['length_km'])

    def test_excessive_jumps_withheld_before_distance(self):
        profiles=[{'latitude':13,'reason':None},{'latitude':15,'reason':None}]
        result=diagnostic.axis_length([180,181],profiles,lambda *args:self.fail('Jump must be refused'))
        self.assertIsNone(result['length_km'])
        self.assertEqual(result['reason'],'adjacent_latitude_jump')
        for longitude,rows in (([180,181,182],profiles),([180,180],profiles),([0,180],profiles)):
            with self.assertRaisesRegex(ValueError,'longitude support'):
                diagnostic.axis_length(longitude,rows,lambda *args:self.fail('Incomplete geometry'))

    def test_partial_range_never_becomes_complete_annual_range(self):
        rows=[{'month':month,'length_km':None if month==3 else 10000+month} for month in range(1,13)]
        result=diagnostic.monthly_range(rows,'length_km')
        self.assertEqual(result['missing_months'],[3])
        self.assertFalse(result['complete_2013_monthly_mean_regional_range'])
        self.assertFalse(result['whole_current_annual_range'])
        self.assertFalse(result['physical_uncertainty'])
        self.assertFalse(result['climatology'])

    def test_local_refusal_before_files_or_network(self):
        with patch.dict(diagnostic.os.environ,{},clear=True), \
             patch.object(diagnostic,'read',side_effect=AssertionError('No input reads allowed')):
            with self.assertRaisesRegex(ValueError,'Cloud-only'):diagnostic.guard()


if __name__=='__main__':unittest.main()
