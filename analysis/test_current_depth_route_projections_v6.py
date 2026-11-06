"""Verify paired EAC geometry and explicitly regional reference-volume units."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_route_projections_v5 as previous
import build_current_depth_route_projections_v6 as depth


class EACRegionalDepthAreaVolumeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.p=cls.data['projections'][-1];cls.volumes=depth.build_volume_scenarios(cls.data);cls.volume=cls.volumes['records'][0]
        cls.operator=json.loads((depth.ROOT/depth.OPERATOR).read_bytes());cls.case=cls.operator['case'];cls.source=json.loads((depth.ROOT/cls.operator['depth_register_file']).read_bytes());cls.refs={r['id']:r for r in cls.source['evidence']}

    def test_previous_seven_preserved_and_eighth_regional_profile(self):
        self.assertEqual(self.data['projections'][:7],previous.build()['projections'])
        self.assertEqual(self.data['counts'],{'catalog_identities':111,'identities_with_regional_projection_scenarios':8,'identities_not_yet_projected':103,'regional_projection_scenarios':8,'source_anchor_references':20,'new_depth_measurements':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0,'regional_reference_geometry_volume_scenarios':1})
        for record,source in zip(self.data['records'],self.source['records']):self.assertEqual(record['depth_reference_ids'],source['depth_reference_ids'])

    def test_only_same_source820_1010_depth_and97_104_area_pairs_used(self):
        self.assertEqual([(a['maximum_depth_m'],a['cross_section_area_km2']) for a in self.p['anchors']],[(820,97.1),(1010,104.2)])
        self.assertEqual(self.p['model_simulation_period'],{'start':'1994-01-01','end':'2016-10-01'})
        self.assertEqual(self.p['metric'],'projected_mean_isotach_core_maximum_depth')

    def test_downstream_sections_excluded_and_no_route_extrapolation(self):
        self.assertEqual(len(self.p['excluded_downstream_reference_ids']),3)
        self.assertFalse(set(self.p['source_reference_ids']).intersection(self.p['excluded_downstream_reference_ids']))
        self.assertIsNone(self.p['samples'][0]['projected_depth_descriptor_m']);self.assertIsNone(self.p['samples'][-1]['projected_depth_descriptor_m'])
        self.assertIsNone(self.p['samples'][-1]['projected_core_cross_section_area_km2'])
        self.assertAlmostEqual(self.volume['reference_interval_length_km'],311.085,places=3)

    def test_source_mask_period_and_area_pair_mutations_rejected(self):
        ref_id=self.case['anchors'][0]['reference_id']
        for key,value in [('source_cross_section_area_km2',104.2),('source_signed_alongshore_isotach_m_s',0.05),('reference_route_projection_eligible',False),('model_simulation_period',{'start':'2004-01-01','end':'2015-12-31'}),('source_distance_offshore_is_current_width',True)]:
            refs=copy.deepcopy(self.refs);refs[ref_id][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):depth.validate_case(self.case,refs)

    def test_intermediate_depth_and_area_are_assumed_not_new_observations(self):
        for sample in self.p['samples']:
            if sample['status']=='unsupported_no_extrapolation':self.assertEqual(sample['source_reference_ids'],[])
            else:
                self.assertTrue(820<=sample['projected_depth_descriptor_m']<=1010)
                self.assertTrue(97.1<=sample['projected_core_cross_section_area_km2']<=104.2)
        self.assertEqual(len([s for s in self.p['samples'] if s['status']=='source_mean_mask_section_depth_and_area_anchor']),2)

    def test_area_distance_integral_has_cubic_kilometre_units(self):
        anchors=[{'reference_id':'a','distance_km':0,'cross_section_area_km2':1},{'reference_id':'b','distance_km':1,'cross_section_area_km2':1}]
        self.assertEqual(depth.integrate_area(anchors)[0],1)
        anchors=[{'reference_id':'a','distance_km':0,'cross_section_area_km2':2},{'reference_id':'b','distance_km':10,'cross_section_area_km2':4}]
        self.assertEqual(depth.integrate_area(anchors)[0],30)
        for a in anchors:a['maximum_depth_m']=99999
        self.assertEqual(depth.integrate_area(anchors)[0],30)

    def test_invalid_area_or_distance_order_is_rejected(self):
        anchors=[{'reference_id':'a','distance_km':0,'cross_section_area_km2':2},{'reference_id':'b','distance_km':10,'cross_section_area_km2':4}]
        for key,value in [('cross_section_area_km2',-1),('cross_section_area_km2',float('nan')),('cross_section_area_km2',True),('distance_km',-10)]:
            changed=copy.deepcopy(anchors);changed[1][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):depth.integrate_area(changed)
        with self.assertRaises(ValueError):depth.integrate_area(list(reversed(anchors)))
        with self.assertRaises(ValueError):depth.integrate_area(anchors[:1])

    def test_real_volume_is_area_integral_not_width_depth_box_or_transport(self):
        expected=(97.1+104.2)/2*311.085
        self.assertAlmostEqual(self.volume['computed_integral_km3'],expected,places=3)
        self.assertEqual(self.volume['scenario_volume_km3'],31000)
        self.assertEqual(len(self.volume['computational_terms']),1)
        self.assertIn('no rectangle',self.volume['shape_assumption'])

    def test_regional_mean_geometry_scenario_not_whole_current_observed_volume(self):
        v=self.volume;self.assertTrue(v['regional_scenario_admitted'])
        for key in ['whole_current_volume_estimate','observed_water_volume','mean_of_instantaneous_core_volumes','physical_state_join_eligible','global_total_eligible']:self.assertFalse(v[key])
        self.assertIsNone(v['uncertainty_km3']);self.assertIsNone(v['confidence_interval_km3'])
        self.assertIn('not recovered or applied',v['orientation_assumption'])
        self.assertEqual(self.volumes['counts']['whole_current_volume_estimates'],0)
        self.assertFalse(any(self.p['eligibility'].values()));self.assertIsNone(self.p['volume_km3'])

    def test_json_and_both_csvs_reproduce_with_paired_area_context(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        self.assertEqual(json.loads((depth.ROOT/depth.VOLUME_OUTPUT).read_bytes()),self.volumes)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        self.assertEqual((depth.ROOT/depth.VOLUME_CSV).read_bytes(),depth.volume_csv_bytes(self.volumes))
        rows=[r for r in csv.DictReader(io.StringIO(raw.decode('utf8'))) if r['entity_id']=='current:east-australian']
        self.assertEqual(len(rows),len(self.p['samples']))
        for row in rows:
            self.assertEqual(json.loads(row['model_simulation_period']),self.p['model_simulation_period'])
            self.assertEqual(row['metric'],self.p['metric'])


if __name__=='__main__':unittest.main()
