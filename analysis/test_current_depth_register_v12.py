"""Protect reach scales, property cores and selected domains from geometry promotion."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v11 as previous
import build_current_depth_register_v12 as depth


class ReachAndCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.new=cls.data['evidence'][140:]
        cls.rows={r['id']:r for r in cls.new}
        cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def reject(self,original,changes):
        for field,value in changes:
            row=copy.deepcopy(original);row[field]=value
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):self.validate(row)

    def test_all_identities_and_prior_140_references_preserved(self):
        prior=previous.build()
        self.assertEqual(self.data['evidence'][:140],prior['evidence'])
        self.assertEqual({r['entity_id'] for r in self.data['records']},{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':145,'identities_with_scoped_depth_reference':59,'identities_not_yet_assessed':52,'whole_route_depth_profiles':0,'volume_estimates':0})
        gaps={r['entity_id'] for r in self.data['records'] if not r['depth_reference_ids']}
        self.assertIn('current:spitsbergen-atlantic',gaps)

    def test_loop_reach_range_not_subsurface_band_or_bathymetry(self):
        row=self.rows['loop-lopera-2025-literature-reach']
        self.assertEqual(row['range_m'],[1000,1200]);self.assertEqual(row['metric'],'reported_vertical_extent')
        self.reject(row,[('metric','reported_flow_depth_band'),('range_m',[800,1000]),('campaign_window',{'start':'2014-09-01','end':'2016-08-31'}),('climatology_years',[2014,2016])])

    def test_alaska_core_not_eddy_or_coastal_current_extent(self):
        row=self.rows['alaska-tang-2014-sept2008-geostrophic-core']
        self.assertEqual(row['approximate_value_m'],150);self.assertEqual(row['section_sampling_month'],'2008-09')
        self.reject(row,[('entity_id','current:alaska-coastal-gulf'),('metric','reported_vertical_extent'),('approximate_value_m',700),('velocity_reconstruction','direct_ADCP'),('window_role','exact_core_occupation'),('core_definition',{'kind':'salinity_maximum'})])

    def test_ncc_upper_layer_scale_not_layer_top_or_trial_mean(self):
        row=self.rows['ncc-tonani-2019-trench-upper-layer']
        self.assertEqual(row['range_m'],[50,100]);self.assertEqual(row['source_wording_class'],'upper_layer_depth_scale')
        self.reject(row,[('metric','reported_flow_depth_band'),('upper_boundary_m',50),('entity_id','current:norwegian-atlantic-slope'),('section_sampling_month','2018-12'),('climatology_years',[2016,2017])])

    def test_wsc_stream_domain_preserves_selection_branch_and_pressure(self):
        row=self.rows['wsc-kolas-fer-2018-aug2015-stream-tube-depth-domain']
        self.assertEqual(row['range_m'],[50,500]);self.assertEqual(row['metric'],'transport_selected_depth_extent')
        self.assertEqual(row['source_branch'],'svalbard_branch')
        self.reject(row,[('range_m',[45,475]),('metric','reported_flow_depth_band'),('thickness_m',450),('entity_id','current:spitsbergen-atlantic'),('branch_section_scope','whole_current'),('pressure_to_depth_conversion_performed',True),('velocity_reconstruction','unreferenced_geostrophy')])
        for field,value in [('vertical','fixed_50_to_500m'),('tube1_background_speed_m_s',0.02),('tube2_volume_flux_constraint_Sv',2.8)]:
            changed=copy.deepcopy(row);changed['transport_selection'][field]=value
            with self.subTest(selection=field),self.assertRaises(ValueError):self.validate(changed)
        changed=copy.deepcopy(row);changed['transport_selection']['water_mass']['conservative_temperature_operator']='>'
        with self.assertRaises(ValueError):self.validate(changed)

    def test_redsea_product_core_range_not_thickness_or_summer(self):
        row=self.rows['redsea-bower-2005-winter2001-product-core-depths']
        self.assertEqual(row['range_m'],[400,800]);self.assertEqual(row['metric'],'core_depth')
        self.assertEqual(row['campaign_window'],{'start':'2001-02-05','end':'2001-03-15'})
        self.reject(row,[('metric','reported_flow_depth_band'),('core_definition',{'kind':'maximum_velocity'}),('phase_label','summer_REDSOX2001'),('section_sampling_month','2001-02'),('campaign_window',{'start':'2001-08-21','end':'2001-09-12'})])

    def test_no_unreviewed_volume_or_annual_geometry_promotion(self):
        for row in self.new:
            self.validate(row)
            self.reject(row,[('lower_boundary_m',800),('uncertainty_m',20),('annual_range_m',[50,1200]),('volume_eligible',True),('physical_state_join_eligible',True),('seasonal_playback_eligible',True),('whole_current_representative',True),('same_source_width_reference_id','unreviewed-width'),('independent_observation_count_claimed',True)])

    def test_source_facts_json_and_csv_reproduce(self):
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes());self.assertEqual(len(self.new),5)
        for row in self.new:
            raw=source['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual(raw,{k:row[k] for k in raw})
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),depth.csv_bytes(self.data))
        rows={r['id']:r for r in csv.DictReader(io.StringIO(depth.csv_bytes(self.data).decode('utf8')))}
        row=rows['wsc-kolas-fer-2018-aug2015-stream-tube-depth-domain']
        self.assertEqual(json.loads(row['transport_selection'])['water_mass']['absolute_salinity_g_kg'],35.05)
        self.assertEqual(rows['alaska-tang-2014-sept2008-geostrophic-core']['survey_window'],'{"start":"2008-09-17","end":"2008-09-18"}')


if __name__=='__main__':unittest.main()
