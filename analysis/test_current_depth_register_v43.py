import copy
import csv
import io
import json
import unittest
from collections import Counter
import build_current_depth_register_v43 as depth


class EACCalendarDepthRegisterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.rows=cls.data['evidence'][-24:]
        cls.candidate=json.loads((depth.ROOT/'research/source-data/eac-chandler-seasonal-depth-v1/candidate.json').read_bytes())

    def test_previous354_references_and_identity_coverage_preserved(self):
        old=json.loads((depth.ROOT/'research/current-depth-register-v42.json').read_bytes())
        self.assertEqual(self.data['evidence'][:354],old['evidence'])
        self.assertEqual(self.data['counts']['depth_references'],378)
        self.assertEqual(self.data['counts']['identities_with_scoped_depth_reference'],101)
        self.assertEqual(self.data['counts']['whole_route_depth_profiles'],0)
        self.assertEqual(self.data['counts']['volume_estimates'],0)

    def test24_descriptors_are12_paired_mean_profiles_not_independent_sections(self):
        self.assertEqual(Counter(r['source_case_id'] for r in self.rows).most_common()[0][1],2)
        self.assertEqual(len(set(r['source_case_id'] for r in self.rows)),12)
        self.assertEqual(Counter(r['metric'] for r in self.rows),{'core_depth':12,'derived_current_following_isotach_depth':12})
        self.assertEqual(sorted({r['calendar_months'][0] for r in self.rows}),list(range(1,13)))
        for row in self.rows:
            self.assertFalse(row['independent_observation_count_claimed'])
            self.assertEqual(row['climatology_years'],[2004,2019]);self.assertEqual(row['source_year_profiles_per_calendar_month'],16)
            self.assertEqual(row['source_calendar_mean_frame'],'moving_monthly_depth_integrated_axis_current_following_not_one_fixed_point')

    def test_core_values_and_shallow_edge_limit(self):
        rows=[r for r in self.rows if r['metric']=='core_depth']
        self.assertEqual([r['approximate_value_m'] for r in rows],[2.5,2.5,60,60,70,70,60,50,2.5,2.5,2.5,2.5])
        for row in rows:
            self.assertEqual(row['source_sampled_core_at_shallowest_valid_level'],row['approximate_value_m']==2.5)
            self.assertIsNone(row['upper_boundary_m']);self.assertIsNone(row['thickness_m'])

    def test_isotach_native_brackets_and_mean_velocity_support(self):
        z=self.candidate['native_depths_m']
        rows=[r for r in self.rows if r['metric']=='derived_current_following_isotach_depth']
        for row,profile in zip(rows,self.candidate['monthly_climatologies']):
            a,b=row['source_native_bracketing_depths_m'];value=row['source_computed_depth_before_display_rounding_m']
            self.assertLessEqual(a,value);self.assertLessEqual(value,b)
            v=profile['native_mean_velocity_profile_m_s'];self.assertGreater(-v[z.index(a)],.05);self.assertLessEqual(-v[z.index(b)],.05)
            self.assertEqual(profile['finite_profile_counts_per_depth'][z.index(a)],16)
            self.assertEqual(profile['finite_profile_counts_per_depth'][z.index(b)],16)
            self.assertEqual(row['source_velocity_threshold_m_s'],.05)
            self.assertEqual(row['approximate_value_m'],int(10*round(value/10)))

    def test_product_limit_is_not_an_invented_terminal_depth(self):
        profiles=self.candidate['monthly_climatologies']
        self.assertEqual(sum(r['derived']['crossings']['0.0']['status']=='right_censored_at_native_domain_end' for r in profiles),10)
        for row in self.rows:
            self.assertFalse(row['source_product_limit_is_current_bottom']);self.assertEqual(row['source_product_deep_limit_m'],1975)
            self.assertIsNone(row['lower_boundary_m']);self.assertIsNone(row['annual_range_m'])
            self.assertNotEqual(row['approximate_value_m'],1975)

    def test_uncertainty_reconstruction_and_join_limits(self):
        for row in self.rows:
            self.assertEqual(row['evidence_kind'],'derived_published_observation_reconstruction_climatology')
            self.assertEqual(row['source_statistical_deep_extension_below_m'],800)
            self.assertFalse(row['source_reference_velocity_time_varying']);self.assertFalse(row['source_reference_velocity_standard_error_is_depth_error'])
            self.assertIsNone(row['uncertainty_m']);self.assertIsNone(row['same_source_width_reference_id'])
            for field in ['volume_eligible','whole_current_representative','physical_state_join_eligible','seasonal_playback_eligible','reference_route_projection_eligible']:
                self.assertFalse(row[field])

    def test_mutations_reject_source_and_calendar_promotion(self):
        for row in self.rows:
            for field,value in [('calendar_months',[13]),('source_year_profiles_per_calendar_month',15),('source_calendar_mean_requires_all16_years_per_depth',False),('source_velocity_threshold_m_s',.1),('evidence_kind','published_observed_section'),('source_product_limit_is_current_bottom',True),('uncertainty_m',50),('volume_eligible',True)]:
                changed=copy.deepcopy(row);changed[field]=value
                with self.subTest(reference=row['id'],field=field),self.assertRaises(ValueError):depth.validate_context(changed)

    def test_exact_json_csv_and_old_cells(self):
        self.assertEqual(self.data,json.loads((depth.ROOT/depth.OUTPUT).read_bytes()))
        raw=depth.csv_bytes(self.data);self.assertEqual(raw,(depth.ROOT/depth.CSV).read_bytes())
        rows=list(csv.DictReader(io.StringIO(raw.decode('utf8'))))
        old=list(csv.DictReader(io.StringIO((depth.ROOT/'research/current-depth-register-v42.csv').read_text(encoding='utf8'))))
        for before,after in zip(old,rows):
            for key,value in before.items():self.assertEqual(value,after[key],(before['id'],key))
        self.assertEqual(json.loads(rows[-1]['calendar_months']),[12])
        self.assertEqual(json.loads(rows[-1]['source_native_bracketing_depths_m']),[950,1000])

    def test_input_pins_include_derived_product_and_cloud_review(self):
        import hashlib
        for path,digest in self.data['input_sha256'].items():self.assertEqual(hashlib.sha256((depth.ROOT/path).read_bytes()).hexdigest(),digest)
        for path in ['research/source-data/eac-chandler-seasonal-depth-v1/candidate.json','research/eac-chandler-seasonal-depth-source-review-v1.json']:
            self.assertIn(path,self.data['input_sha256'])


if __name__=='__main__':unittest.main()
