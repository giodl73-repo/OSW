import copy
import csv
import io
import json
import unittest
from collections import Counter
import build_current_depth_register_v45 as depth


class KuroshioDepthAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.rows=cls.data['evidence'][-36:]
        cls.old=json.loads((depth.ROOT/'research/current-depth-register-v44.json').read_bytes())
        cls.candidate=json.loads((depth.ROOT/'research/source-data/kuroshio-chandler-seasonal-depth-v1/candidate.json').read_bytes())

    def test_previous403_references_and_identity_coverage(self):
        self.assertEqual(self.data['evidence'][:403],self.old['evidence'])
        self.assertEqual(self.data['counts']['depth_references'],439)
        self.assertEqual(self.data['counts']['identities_with_scoped_depth_reference'],101)
        self.assertEqual(self.data['counts']['whole_route_depth_profiles'],0);self.assertEqual(self.data['counts']['volume_estimates'],0)

    def test36_descriptors_share12_calendar_input_groups(self):
        self.assertEqual(Counter(r['metric'] for r in self.rows),{'core_depth':12,'derived_current_following_isotach_depth':24})
        self.assertEqual(list(Counter(r['source_case_id'] for r in self.rows).values()),[3]*12)
        self.assertEqual(Counter(r['source_velocity_threshold_m_s'] for r in self.rows),{None:12,.05:12,.1:12})
        self.assertTrue(all(not r['independent_observation_count_claimed'] for r in self.rows))

    def test_sampled_shallow_edges_not_surface_measurements(self):
        rows=[r for r in self.rows if r['metric']=='core_depth']
        self.assertTrue(all(r['approximate_value_m']==2.5 for r in rows))
        for row in self.rows:
            self.assertTrue(row['source_sampled_core_at_shallowest_valid_level'])
            self.assertIsNone(row['upper_boundary_m']);self.assertIsNone(row['thickness_m'])

    def test_northern_component_crossings_and_native_brackets(self):
        z=self.candidate['native_depths_m']
        for row in self.rows:
            threshold=row['source_velocity_threshold_m_s']
            if threshold is None:continue
            profile=self.candidate['monthly_climatologies'][row['calendar_months'][0]-1]
            a,b=row['source_native_bracketing_depths_m'];v=profile['native_mean_velocity_profile_m_s']
            self.assertGreater(v[z.index(a)],threshold);self.assertLessEqual(v[z.index(b)],threshold)
            self.assertEqual(profile['finite_profile_counts_per_depth'][z.index(a)],16)
            self.assertEqual(profile['finite_profile_counts_per_depth'][z.index(b)],16)
            computed=row['source_computed_depth_before_display_rounding_m']
            self.assertLessEqual(a,computed);self.assertLessEqual(computed,b)
            self.assertEqual(row['approximate_value_m'],int(10*round(computed/10)))
            self.assertIn('not_horizontal_speed_magnitude',row['source_velocity_quantity'])

    def test_source_identity_separates_kuroshio_from_ke(self):
        self.assertTrue(all(r['entity_id']=='current:kuroshio' for r in self.rows))
        before=next(r for r in self.old['records'] if r['entity_id']=='current:kuroshio-extension')
        after=next(r for r in self.data['records'] if r['entity_id']=='current:kuroshio-extension')
        self.assertEqual(before,after)
        for row in self.rows:
            self.assertIn('west_of_minimum_west150E',row['source_horizontal_axis_operator'])
            self.assertLessEqual(row['source_longitude_support_range_degrees_east'][1],145)

    def test_source_period_extension_and_censored_limits(self):
        for row in self.rows:
            self.assertEqual(row['source_direct_HRXBT_occupation_years'],[2012,2019])
            self.assertEqual(row['source_reconstructed_product_years'],[2004,2019]);self.assertTrue(row['source_pre2012_months_are_reconstructed'])
            self.assertEqual(row['source_statistical_deep_extension_below_m'],600)
            self.assertEqual(row['source_zero_crossing_status'],'right_censored_at_native_domain_end')
            self.assertFalse(row['source_product_limit_is_current_bottom']);self.assertIsNone(row['lower_boundary_m'])
            self.assertIsNone(row['uncertainty_m']);self.assertFalse(row['volume_eligible']);self.assertFalse(row['physical_state_join_eligible'])

    def test_mutations_reject_sign_identity_and_reconstruction_loss(self):
        for row in self.rows:
            for field,value in [('entity_id','current:kuroshio-extension'),('source_velocity_quantity','horizontal_speed_magnitude'),('source_pre2012_months_are_reconstructed',False),('source_statistical_deep_extension_below_m',800),('source_product_limit_is_current_bottom',True),('source_year_profiles_per_calendar_month',15),('uncertainty_m',50),('volume_eligible',True)]:
                changed=copy.deepcopy(row);changed[field]=value
                with self.subTest(reference=row['id'],field=field),self.assertRaises(ValueError):depth.validate_context(changed)

    def test_exact_outputs_and_previous_csv_cells(self):
        self.assertEqual(self.data,json.loads((depth.ROOT/depth.OUTPUT).read_bytes()))
        raw=depth.csv_bytes(self.data);self.assertEqual(raw,(depth.ROOT/depth.CSV).read_bytes())
        rows=list(csv.DictReader(io.StringIO(raw.decode('utf8'))))
        old=list(csv.DictReader(io.StringIO((depth.ROOT/'research/current-depth-register-v44.csv').read_text(encoding='utf8'))))
        for before,after in zip(old,rows):
            for key,value in before.items():self.assertEqual(value,after[key],(before['id'],key))
        self.assertEqual(json.loads(rows[-1]['source_direct_HRXBT_occupation_years']),[2012,2019])

    def test_source_pins_and_product_limit_semantics(self):
        import hashlib
        for path,digest in self.data['input_sha256'].items():self.assertEqual(hashlib.sha256((depth.ROOT/path).read_bytes()).hexdigest(),digest)
        self.assertIn('research/source-data/kuroshio-chandler-seasonal-depth-v1/candidate.json',self.data['input_sha256'])
        self.assertTrue(all(r['derived']['crossings']['0.0']['depth_m'] is None for r in self.candidate['monthly_climatologies']))


if __name__=='__main__':unittest.main()
