import json,unittest
from derive_pratt2000_mean_interfaces_v1 import derive
RAW=b'ranges from 35 m in winter to 110 m in\\nsummer.'
class Tests(unittest.TestCase):
    def test_reported_season_labels_not_calendar(self):
        r=derive(RAW);self.assertEqual([(x['source_season_label'],x['approximate_value_m']) for x in r],[('winter',35),('summer',110)]);self.assertTrue(all(x['calendar_month'] is None for x in r))
    def test_changed_source_values_rejected(self):
        for raw in [RAW.replace(b'35',b'30'),RAW.replace(b'110',b'100')]:
            with self.assertRaises(ValueError):derive(raw)
    def test_no_physical_or_range_promotion(self):
        for r in derive(RAW):
            for k in ['physical_current_bottom_m','thickness_m','range_m','annual_range_m','uncertainty_m','paired_lower_boundary_m']:self.assertIsNone(r[k])
            for k in ['whole_current_representative','physical_depth_ranking_eligible','seasonal_playback_eligible','reference_route_projection_eligible','volume_eligible']:self.assertIs(r[k],False)
    def test_oversize_rejected(self):
        with self.assertRaises(ValueError):derive(b'x'*1001)
    def test_scope_and_method_preserved(self):
        r=derive(RAW)[0];self.assertIn('monthly_mean',r['metric']);self.assertIn('zero_crossing',r['metric']);self.assertIn('Hanish',r['geographic_scope']);self.assertIn('not mean individual',r['source_qualifications'][0])
if __name__=='__main__':unittest.main()
