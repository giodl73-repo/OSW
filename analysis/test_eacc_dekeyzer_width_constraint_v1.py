import copy
import json
import unittest
import eacc_dekeyzer_width_constraint_v1 as m


class EaccConstraintTests(unittest.TestCase):
    def facts(self):return json.loads((m.ROOT/m.FACTS).read_bytes())

    def test_reviewed_original_supports_only_one_dependent_exclusive_lower_bound(self):
        facts=self.facts();m.validate(facts)
        self.assertEqual(facts['records'][0]['reported_operator'],'gt')
        self.assertIsNone(facts['records'][0]['upper_bound_km'])
        self.assertIsNone(facts['records'][0]['reported_width_km'])

    def test_point_range_depth_date_and_observation_promotions_are_refused(self):
        for key,value in [('reported_operator','gte'),('reported_width_km',160),('width_range_km',[160,200]),
                          ('calendar_months',[6,7,8]),('fixed_layer_bounds_m',[0,400]),
                          ('seasonal_playback_eligible',True),('independent_observational_sample',True)]:
            facts=self.facts();facts['records'][0][key]=value
            with self.assertRaises(ValueError,msg=key):m.validate(facts)

    def test_changed_identity_custody_lineage_or_duplicate_report_is_refused(self):
        for mutate in [lambda f:f.update(original_sha256='0'*64),
                       lambda f:f['records'][0].update(entity_id='current:somali'),
                       lambda f:f['underlying_cited_work'].update(original_full_text_reviewed=True),
                       lambda f:f['records'].append(copy.deepcopy(f['records'][0])),
                       lambda f:f.update(installed_width_records_added=1)]:
            facts=self.facts();mutate(facts)
            with self.assertRaises(ValueError):m.validate(facts)


if __name__=='__main__':unittest.main()
