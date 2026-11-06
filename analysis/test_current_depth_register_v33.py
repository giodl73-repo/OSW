"""Guard site-specific EUC core comparison levels and distinct record periods."""
import copy
import csv
import hashlib
import io
import json
import unittest
import build_current_depth_register_v32 as previous
import build_current_depth_register_v33 as depth


class PacificEUCCoreLevelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.rows=cls.data['evidence'][319:]
        cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def reject(self,row,changes):
        for key,value in changes:
            changed=copy.deepcopy(row);changed[key]=value
            with self.subTest(id=row['id'],field=key),self.assertRaises(ValueError):self.validate(changed)

    def test_prior319_and_owner_inventory_preserved(self):
        self.assertEqual(self.data['evidence'][:319],previous.build()['evidence'])
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':323,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0})
        for row in self.rows:self.validate(row)

    def test_four_located_depths_and_site_specific_windows(self):
        self.assertEqual([(r['section_longitude_degrees_east'],r['approximate_value_m']) for r in self.rows],[(165,190),(-170,155),(-140,105),(-110,75)])
        self.assertEqual([r['source_record_period'] for r in self.rows],[{'start':'1996-01-01','end':'2007-12-31'},{'start':'1995-01-01','end':'2005-12-31'},{'start':'1997-01-01','end':'2010-12-31'},{'start':'1996-01-01','end':'2005-12-31'}])
        for row in self.rows:
            self.assertEqual(row['section_latitude_degrees_north'],0)
            self.reject(row,[('source_record_period',{'start':'1995-01-01','end':'2010-12-31'}),('source_record_period_has_gaps',False),('calendar_months',[1,2,3]),('phase_label','annual_extrema'),('annual_range_m',[75,190])])

    def test_comparison_selected_core_not_instantaneous_observed_argmax(self):
        for row in self.rows:
            definition=row['core_definition']
            self.assertEqual(definition['kind'],'author_comparison_selected_record_mean_core_level')
            self.assertEqual(definition['selection'],'minimize_ADCP_ECCOv4r4_record_mean_speed_difference_among_near_equivalent_core_levels')
            self.assertFalse(row['ADCP_velocities_assimilated_in_ECCOv4r4'])
            self.reject(row,[('core_definition',{'kind':'instantaneous_observed_argmax'}),('evidence_kind','pure_observed_instantaneous_core'),('ADCP_velocities_assimilated_in_ECCOv4r4',True),('comparison_products',['moored_ADCP']),('temporal_operator','common_period_climatology')])

    def test_raw_bin_processed_level_and_hourly_average_are_distinct(self):
        for row in self.rows:
            self.assertEqual(row['source_raw_ADCP_bin_size_m'],8.68)
            self.assertEqual(row['source_processed_ADCP_level_spacing_m'],5)
            self.assertEqual(row['source_study_velocity_averaging_hours'],1)
            self.reject(row,[('source_raw_ADCP_bin_size_m',5),('source_processed_ADCP_level_spacing_m',8.68),('source_raw_ADCP_sampling_seconds',60),('source_ADCP_frequency_kHz',75),('uncertainty_m',5),('uncertainty_m',1)])

    def test_analysis_limits_mooring_depth_and_historical_context_not_boundaries(self):
        self.assertEqual([r['reported_velocity_sampling_domain_m'] for r in self.rows],[[40,260],[40,260],[40,235],[35,195]])
        self.assertEqual(self.rows[0]['approximate_value_m']-self.rows[-1]['approximate_value_m'],115)
        for row in self.rows:
            self.reject(row,[('metric','reported_vertical_thickness'),('metric','lower_flow_boundary_depth'),('upper_boundary_m',40),('lower_boundary_m',260),('approximate_value_m',400),('thickness_m',100),('source_site_id','common_basin'),('section_longitude_degrees_east',0)])

    def test_no_incompatible_geometry_or_annual_profile_admission(self):
        for row in self.rows:
            self.reject(row,[('entity_id','current:atlantic-equatorial-undercurrent'),('whole_current_representative',True),('volume_eligible',True),('physical_state_join_eligible',True),('seasonal_playback_eligible',True),('annual_extrema_eligible',True),('same_source_width_reference_id','unrelated_width'),('independent_observation_count_claimed',True)])

    def test_source_csv_member_refresh_and_frozen_prior_index(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        columns=next(csv.reader(io.StringIO(raw.decode('utf8'))));self.assertEqual(len(columns),len(set(columns)))
        exported=list(csv.DictReader(io.StringIO(raw.decode('utf8'))))[-4:]
        for row,out in zip(self.rows,exported):
            self.assertEqual(json.loads(out['source_record_period']),row['source_record_period'])
            self.assertEqual(json.loads(out['core_definition']),row['core_definition'])
            self.assertEqual(out['volume_eligible'],'False')
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes());review=source['source_reviews'][0]
        self.assertTrue(review['actual_original_pixels_viewed']);self.assertEqual(review['actual_reviewed_pages'],[3,5])
        index=depth.build_member_index(self.data);self.assertEqual(json.loads((depth.ROOT/depth.MEMBER_OUTPUT).read_bytes()),index)
        self.assertEqual(index['depth_register_file'],depth.OUTPUT)
        self.assertEqual(index['counts']['distinct_member_depth_references'],42)
        self.assertEqual(index['counts']['new_measurements'],0)
        ids={r['id'] for r in self.rows}
        linked=[p['entity_id'] for p in index['records'] if ids.intersection(p['unique_linked_reference_ids'])]
        self.assertEqual(linked,['current:equatorial-undercurrent'])
        path='research/current-depth-member-index-v2.json'
        self.assertEqual(hashlib.sha256((depth.ROOT/path).read_bytes()).hexdigest(),source['source_input_sha256'][path])
        self.assertEqual(json.loads((depth.ROOT/path).read_bytes())['depth_register_file'],'research/current-depth-register-v32.json')


if __name__=='__main__':unittest.main()
