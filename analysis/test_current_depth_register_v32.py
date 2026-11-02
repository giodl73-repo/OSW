"""Guard regional cSEC attribution, sampling limits and parent ownership."""
import copy
import csv
import hashlib
import io
import json
import unittest
import build_current_depth_register_v31 as previous
import build_current_depth_register_v32 as depth


class AtlanticCentralSECDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.row=cls.data['evidence'][-1]
        cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def reject(self,changes):
        for key,value in changes:
            changed=copy.deepcopy(self.row);changed[key]=value
            with self.subTest(field=key,value=value),self.assertRaises(ValueError):self.validate(changed)

    def test_preserve_prior_evidence_and_add_one_regional_owner(self):
        self.assertEqual(self.data['evidence'][:318],previous.build()['evidence'])
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':319,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0})
        self.assertEqual(self.row['entity_id'],'current:atlantic-south-equatorial')
        self.assertEqual(self.row['approximate_value_m'],100);self.validate(self.row)

    def test_extent_not_boundary_thickness_or_sampling_domain(self):
        self.reject([('metric','reported_vertical_thickness'),('metric','lower_flow_boundary_depth'),('approximate_value_m',500),('approximate_value_m',700),('range_m',[15,100]),('lower_bound_m',100),('upper_boundary_m',0),('lower_boundary_m',100),('thickness_m',100),('uncertainty_m',15)])
        self.assertEqual(self.row['reported_velocity_sampling_domain_m'],[15,700])
        self.assertEqual(self.row['source_displayed_ADCP_limit_m'],500)

    def test_central_westward_branch_separate_from_undercurrents(self):
        self.reject([('entity_id','current:atlantic-south-equatorial-undercurrent'),('entity_id','current:north-brazil'),('source_current_name','South_Equatorial_Undercurrent_SEUC'),('branch_section_scope','coastal_WBCS'),('depth_basis','digitized_signed_velocity_zero_crossing'),('source_figure4_velocity_quantity','signed_zonal_velocity')])

    def test_two_survey_windows_not_annual_depth_range_or_two_repeats(self):
        self.assertEqual(self.row['source_survey_periods'],[{'survey':'ABRACOS1','start_month':'2015-09','end_month':'2015-10','austral_season':'spring'},{'survey':'ABRACOS2','start_month':'2017-04','end_month':'2017-05','austral_season':'autumn'}])
        self.reject([('source_survey_periods',[]),('calendar_months',[4,5,9,10]),('annual_range_m',[0,100]),('observed_period',{'start':'2015-09','end':'2017-05'}),('climatology_years',[2015,2017]),('temporal_operator','annual_climatology'),('independent_observation_count_claimed',True),('phase_label','annual')])

    def test_sampling_and_averaging_context_not_promoted_to_geometry(self):
        self.assertEqual(self.row['source_ADCP_frequency_kHz'],75)
        self.reject([('source_ADCP_frequency_kHz',150),('reported_velocity_sampling_domain_m',[0,100]),('source_displayed_ADCP_limit_m',100),('source_research_vessel','Meteor'),('station_profile_averaging_definition','one_exact_instantaneous_profile'),('section_latitude_degrees_north',-5),('reference_route_projection_eligible',True),('same_source_width_reference_id','unrelated_width'),('whole_current_representative',True),('volume_eligible',True),('physical_state_join_eligible',True),('seasonal_playback_eligible',True),('annual_extrema_eligible',True)])

    def test_member_lookup_refresh_preserves_child_ownership_without_aggregation(self):
        index=depth.build_member_index(self.data)
        self.assertEqual(json.loads((depth.ROOT/depth.MEMBER_OUTPUT).read_bytes()),index)
        self.assertEqual(index['depth_register_file'],depth.OUTPUT)
        self.assertEqual(index['depth_register_sha256'],hashlib.sha256((depth.ROOT/depth.OUTPUT).read_bytes()).hexdigest())
        self.assertEqual(index['counts'],{'parents':9,'families':8,'systems':1,'member_links':23,'distinct_member_identities':20,'distinct_member_depth_references':38,'parents_with_any_member_depth_evidence':9,'parents_with_all_declared_members_referenced':9,'new_measurements':0,'whole_route_profiles':0,'volumes':0})
        refs={r['id']:r for r in self.data['evidence']};linked=[]
        for parent in index['records']:
            self.assertIsNone(parent['parent_depth_m']);self.assertIsNone(parent['aggregation_operator'])
            self.assertFalse(parent['volume_eligible'])
            for member in parent['members']:
                for ref in member['depth_reference_ids']:
                    self.assertEqual(refs[ref]['entity_id'],member['entity_id'])
                    if ref==self.row['id']:linked.append(parent['entity_id'])
        self.assertEqual(linked,['current:south-equatorial'])

    def test_source_review_csv_and_previous_member_index_frozen(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        columns=next(csv.reader(io.StringIO(raw.decode('utf8'))));self.assertEqual(len(columns),len(set(columns)))
        exported=list(csv.DictReader(io.StringIO(raw.decode('utf8'))))[-1]
        self.assertEqual(json.loads(exported['source_survey_periods']),self.row['source_survey_periods'])
        self.assertEqual(exported['source_figure4_velocity_quantity'],'current_speed_magnitude_not_signed_zonal_velocity')
        self.assertEqual(exported['volume_eligible'],'False')
        self.assertEqual(exported['whole_current_representative'],'False')
        self.assertEqual(exported['lower_boundary_m'],'')
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        review=source['source_reviews'][0];self.assertTrue(review['actual_original_pixels_viewed'])
        self.assertEqual(review['actual_reviewed_pages'],[3,4,8])
        original=source['references'][0];self.assertEqual(original,{k:self.row[k] for k in original})
        p='research/current-depth-member-index-v1.json'
        self.assertEqual(hashlib.sha256((depth.ROOT/p).read_bytes()).hexdigest(),source['source_input_sha256'][p])
        self.assertEqual(json.loads((depth.ROOT/p).read_bytes())['depth_register_file'],'research/current-depth-register-v30.json')


if __name__=='__main__':unittest.main()
