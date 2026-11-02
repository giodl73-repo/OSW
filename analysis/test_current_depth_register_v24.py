"""Verify Adriatic sample-group depth and conservative figure-presence support."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v23 as previous
import build_current_depth_register_v24 as depth


class AdriaticDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.new=cls.data['evidence'][305:];cls.wac,cls.eac=cls.new
        cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def reject(self,row,changes):
        for k,v in changes:
            changed=copy.deepcopy(row);changed[k]=v
            with self.subTest(field=k),self.assertRaises(ValueError):self.validate(changed)

    def test_prior_evidence_and_identity_inventory_preserved(self):
        prior=previous.build();self.assertEqual(self.data['evidence'][:305],prior['evidence'])
        self.assertEqual(self.ids,{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':307,'identities_with_scoped_depth_reference':92,'identities_not_yet_assessed':19,'whole_route_depth_profiles':0,'volume_estimates':0})

    def test_sample_group_not_continuous_layer_or_detected_bottom(self):
        self.validate(self.wac);self.assertEqual(self.wac['range_m'],[0.5,15])
        self.reject(self.wac,[('metric','reported_flow_depth_band'),('metric','reported_vertical_thickness'),('range_m',[0,15]),('range_m',[15,26]),('range_m',[113,141]),('upper_endpoint_is_physical_flow_boundary',True),('lower_endpoint_is_physical_flow_boundary',True),('continuous_velocity_layer_established',True),('water_mass_component','Northern_Adriatic_Dense_Water'),('classification_properties',['velocity'])])

    def test_sample_campaign_not_publication_or_model_dates(self):
        self.assertEqual(self.wac['campaign_window'],{'start_date':'2012-03-23','end_date':'2012-04-02'})
        self.reject(self.wac,[('campaign_window',{'start_date':'2018-03-14','end_date':'2018-03-14'}),('window_role','exact_current_boundary_occupation'),('sample_collection','ADCP_velocity_profile'),('evidence_kind','published_model_climatology')])

    def test_eac_conservative_reach_not_station_depth_or_terminal_depth(self):
        self.validate(self.eac);self.assertEqual(self.eac['lower_bound_m'],30)
        self.reject(self.eac,[('lower_bound_m',56),('lower_bound_m',50),('lower_bound_operator','>'),('lower_bound_exclusive',True),('metric','lower_flow_boundary_depth'),('graphical_read_depth_m',56),('source_station_id','A2'),('source_station_water_depth_m',83)])

    def test_observed_vector_not_model_or_variability_ellipse(self):
        for key,value in [('series','blue_model_vectors'),('panel','A1'),('depth_tick_m',45),('read_kind','ellipse_vertical_extent'),('velocity_digitized',True),('statistical_significance_established',True),('excluded_graphics',[])]:
            changed=copy.deepcopy(self.eac);changed['graphical_read_operator'][key]=value
            with self.subTest(operator=key),self.assertRaises(ValueError):self.validate(changed)
        self.reject(self.eac,[('source_depth_axis_convention','pressure_in_dbar'),('evidence_kind','published_model_climatology'),('sampling_limit_is_flow_boundary',True)])

    def test_two_month_mean_not_deployment_or_annual_envelope(self):
        self.assertEqual(self.eac['averaging_period'],{'start_date':'2015-02-01','end_date':'2015-04-01'})
        self.reject(self.eac,[('averaging_period',{'start_date':'2014-11-01','end_date':'2015-07-01'}),('deployment_window_description','February_to_April_2015')])
        for row in self.new:
            self.reject(row,[('section_sampling_month','2015-03'),('phase_label','winter'),('calendar_months',[2,3]),('climatology_years',[2014,2015])])

    def test_no_whole_geometry_volume_or_unreviewed_joins(self):
        for row in self.new:
            self.reject(row,[('thickness_m',14.5),('upper_boundary_m',0.5),('lower_boundary_m',15),('uncertainty_m',2),('annual_range_m',[15,30]),('whole_current_representative',True),('volume_eligible',True),('physical_state_join_eligible',True),('seasonal_playback_eligible',True),('annual_extrema_eligible',True),('same_source_width_reference_id','unreviewed'),('independent_observation_count_claimed',True)])

    def test_json_csv_and_source_access_reproduce(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        columns=next(csv.reader(io.StringIO(raw.decode('utf8'))));self.assertEqual(len(columns),len(set(columns)))
        rows={r['id']:r for r in csv.DictReader(io.StringIO(raw.decode('utf8')))}
        self.assertEqual(json.loads(rows[self.wac['id']]['classification_properties']),['temperature','salinity','dissolved_oxygen'])
        self.assertEqual(json.loads(rows[self.eac['id']]['graphical_read_operator'])['series'],'observed_ADCP_mean_vectors_left_set')
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        self.assertEqual([r['actual_original_pixels_viewed'] for r in source['source_reviews']],[False,True])
        for row in self.new:
            original=source['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual(original,{k:row[k] for k in original})


if __name__=='__main__':unittest.main()
