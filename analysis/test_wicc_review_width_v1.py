import copy
import json
import unittest
import build_wicc_review_width_v1 as m

class ReviewWidthTests(unittest.TestCase):
    def facts(self):return json.loads((m.ROOT/m.FACTS).read_bytes())

    def test_one_dependent_review_report_preserves_unknown_support(self):
        report=m.prepare(self.facts());self.assertEqual(len(report['records']),1)
        self.assertEqual(report['records'][0]['reported_width_km'],150)
        self.assertEqual(report['independent_observations_added'],0)
        self.assertIsNone(report['records'][0]['fixed_layer_bounds_m'])
        self.assertFalse(report['underlying_cited_work']['original_full_text_reviewed'])

    def test_value_owner_depth_dates_and_eligibility_mutations_fail(self):
        for key,value in [('reported_width_km',400),('current_id','east-india-coastal'),('fixed_layer_bounds_m',[0,100]),('calendar_months',[6,7,8]),('reported_width_uncertainty_km',10),('annual_width_range_km',[100,400]),('geometry',{'invented':True}),('independent_observational_sample',True),('seasonal_playback_eligible',True)]:
            facts=self.facts();facts['records'][0][key]=value
            with self.assertRaises(ValueError,msg=key):m.prepare(facts)

    def test_original_lineage_duplication_and_installation_promotion_fail(self):
        facts=self.facts();facts['underlying_cited_work']['original_full_text_reviewed']=True
        with self.assertRaises(ValueError):m.prepare(facts)
        facts=self.facts();facts['records'].append(copy.deepcopy(facts['records'][0]))
        with self.assertRaises(ValueError):m.prepare(facts)
        facts=self.facts();facts['installed_width_records_added']=1
        with self.assertRaises(ValueError):m.prepare(facts)

if __name__=='__main__':unittest.main()
