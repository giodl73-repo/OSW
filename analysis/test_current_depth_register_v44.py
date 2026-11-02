import copy
import csv
import io
import json
import unittest
from collections import Counter
import build_current_depth_register_v44 as depth
import build_agulhas_individual_depth_distributions_v1 as distributions


class AgulhasDepthAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.rows=cls.data['evidence'][-25:]
        cls.candidate=json.loads((depth.ROOT/'research/source-data/agulhas-chandler-seasonal-depth-v1/candidate.json').read_bytes())
        cls.distribution=json.loads((depth.ROOT/distributions.OUTPUT).read_bytes())

    def test_previous378_references_and_identity_coverage(self):
        old=json.loads((depth.ROOT/'research/current-depth-register-v43.json').read_bytes())
        self.assertEqual(self.data['evidence'][:378],old['evidence'])
        self.assertEqual(self.data['counts']['depth_references'],403)
        self.assertEqual(self.data['counts']['identities_with_scoped_depth_reference'],101)
        self.assertEqual(self.data['counts']['whole_route_depth_profiles'],0);self.assertEqual(self.data['counts']['volume_estimates'],0)

    def test25_descriptors_have12_shared_calendar_input_groups(self):
        self.assertEqual(Counter(r['metric'] for r in self.rows),{'core_depth':12,'derived_median_individual_isotach_depth':12,'derived_current_following_isotach_depth':1})
        self.assertEqual(sorted(Counter(r['source_case_id'] for r in self.rows).values()),[2]*11+[3])
        for row in self.rows:self.assertFalse(row['independent_observation_count_claimed'])

    def test_sampled_mean_profile_cores_and_restricted_axis(self):
        rows=[r for r in self.rows if r['metric']=='core_depth']
        self.assertEqual([r['approximate_value_m'] for r in rows],[40,40,40,40,40,40,30,40,30,40,40,40])
        for row in rows:
            self.assertIn('longitude_less_than34.4E',row['source_horizontal_axis_operator'])
            self.assertLess(row['source_longitude_support_range_degrees_east'][1],34.4)
            self.assertEqual(row['source_derived_metric_role'],'sampled_core_of_calendar_mean_velocity_profile')

    def test_complete_individual_medians_link16_values_and_spread(self):
        rows=[r for r in self.rows if r['metric']=='derived_median_individual_isotach_depth']
        for row in rows:
            group=self.distribution['records'][int(row['source_distribution_pointer'].split('/')[-1])]
            self.assertEqual(group['resolved_year_count'],16);self.assertEqual(row['source_distribution_year_count'],16)
            self.assertEqual(row['source_computed_depth_before_display_rounding_m'],group['statistics']['median_m'])
            self.assertEqual(row['source_interannual_reconstructed_sample_span_m'],[group['statistics']['minimum_m'],group['statistics']['maximum_m']])
            self.assertEqual(row['approximate_value_m'],int(10*round(group['statistics']['median_m']/10)))
            self.assertFalse(row['source_sample_spread_is_confidence_interval']);self.assertIsNone(row['uncertainty_m']);self.assertIsNone(row['range_m'])

    def test_mean_profile_crossing_is_not_individual_depth_median(self):
        mean=next(r for r in self.rows if r['metric']=='derived_current_following_isotach_depth')
        self.assertEqual(mean['calendar_months'],[9]);self.assertEqual(mean['source_native_bracketing_depths_m'],[950,1000])
        self.assertAlmostEqual(mean['source_computed_depth_before_display_rounding_m'],999.192665)
        median=next(r for r in self.rows if r['calendar_months']==[9] and r['metric']=='derived_median_individual_isotach_depth')
        self.assertNotEqual(mean['source_computed_depth_before_display_rounding_m'],median['source_computed_depth_before_display_rounding_m'])
        self.assertIsNone(mean['source_distribution_file'])

    def test_missing5cms_mean_crossings_are_not_filled(self):
        self.assertTrue(all(r['derived']['crossings']['0.05']['status']=='unknown_gap_after_core' for r in self.candidate['monthly_climatologies']))
        self.assertTrue(all(r['source_velocity_threshold_m_s']!=.05 for r in self.rows))
        for row in self.rows:
            self.assertIsNone(row['lower_boundary_m']);self.assertIsNone(row['upper_boundary_m']);self.assertIsNone(row['thickness_m']);self.assertIsNone(row['annual_range_m'])
            self.assertFalse(row['source_product_limit_is_current_bottom']);self.assertFalse(row['source_reference_velocity_standard_error_is_depth_error'])
            self.assertFalse(row['volume_eligible']);self.assertFalse(row['physical_state_join_eligible'])

    def test_mutations_reject_changed_estimand_and_error_promotion(self):
        for row in self.rows:
            for field,value in [('source_derived_metric_role','physical_current_bottom'),('source_sample_spread_is_confidence_interval',True),('source_year_profiles_per_calendar_month',15),('source_velocity_threshold_m_s',.05),('uncertainty_m',50),('volume_eligible',True)]:
                changed=copy.deepcopy(row);changed[field]=value
                with self.subTest(reference=row['id'],field=field),self.assertRaises(ValueError):depth.validate_context(changed)

    def test_exact_outputs_and_prior_csv_cells(self):
        self.assertEqual(self.data,json.loads((depth.ROOT/depth.OUTPUT).read_bytes()))
        raw=depth.csv_bytes(self.data);self.assertEqual(raw,(depth.ROOT/depth.CSV).read_bytes())
        self.assertEqual(distributions.build(),self.distribution)
        rows=list(csv.DictReader(io.StringIO(raw.decode('utf8'))))
        old=list(csv.DictReader(io.StringIO((depth.ROOT/'research/current-depth-register-v43.csv').read_text(encoding='utf8'))))
        for before,after in zip(old,rows):
            for key,value in before.items():self.assertEqual(value,after[key],(before['id'],key))
        for source,out in zip(self.rows,rows[-25:]):
            if source['source_interannual_reconstructed_sample_span_m'] is not None:
                self.assertEqual(json.loads(out['source_interannual_reconstructed_sample_span_m']),source['source_interannual_reconstructed_sample_span_m'])

    def test_source_pins_and_reconstruction_limits(self):
        import hashlib
        for path,digest in self.data['input_sha256'].items():self.assertEqual(hashlib.sha256((depth.ROOT/path).read_bytes()).hexdigest(),digest)
        self.assertIn(distributions.OUTPUT,self.data['input_sha256'])
        for row in self.rows:
            self.assertEqual(row['climatology_years'],[2004,2019]);self.assertEqual(row['source_statistical_deep_extension_below_m'],800)
            self.assertFalse(row['source_reference_velocity_time_varying']);self.assertFalse(row['whole_current_representative'])


if __name__=='__main__':unittest.main()
