import unittest
from acquire_somali_steady_model_pressures_v1 import extract
TEXT='Wind-driven cross-equatorial flow;2003-2009 Argo steady model. Winter Monsoon shallow (200 dbar). Summer Monsoon and Transitional Periods to (650 dbar).'
class Tests(unittest.TestCase):
    def test_pressure_and_phase_roles(self):
        r=extract(TEXT);self.assertEqual([x['approximate_value'] for x in r],[200,650,650]);self.assertTrue(all(x['unit']=='dbar' for x in r));self.assertEqual([x['source_flow_direction'] for x in r],['southward','northward','southward'])
    def test_no_physical_metres_or_annual_range(self):
        for r in extract(TEXT):
            for k in ['lower_boundary_metres','thickness_metres','annual_extrema_dbar','pressure_uncertainty_dbar','calendar_months']:self.assertIsNone(r[k])
            for k in ['physical_current_bottom_established','independent_direct_observation','whole_current_representative','seasonal_playback_eligible','physical_depth_ranking_eligible','route_state_join_eligible','volume_eligible']:self.assertIs(r[k],False)
    def test_changed_value_rejected(self):
        with self.assertRaises(ValueError):extract(TEXT.replace('200 dbar','250 dbar'))
    def test_unknown_method_rejected(self):
        with self.assertRaises(ValueError):extract(TEXT.replace('steady model','direct observed currents'))
    def test_shared_author_statement_not_independent(self):
        self.assertIn('not two independent observations',extract(TEXT)[2]['qualification'])
if __name__=='__main__':unittest.main()
