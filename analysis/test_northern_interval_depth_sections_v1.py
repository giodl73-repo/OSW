import copy
import json
from pathlib import Path
import unittest
import numpy as np
import acquire_zonal_current_depth_sections_v1 as g
import interval_transverse_section_audit_v1 as audit
from interval_depth_diagnostic_v1 import diagnose


class NorthernIntervalSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((Path(__file__).resolve().parents[1]/'research/northern-interval-depth-sections-operator-v1.json').read_bytes())

    def fixture(self,edge=False,censored=False):
        config={**self.op,**self.op['currents']['current:pacific-north-subsurface-countercurrent']}
        z=[0,100,200,300,400,700]
        u=np.array([[-.1,-.1,-.1],[.05,.2,.05],[.07,.3,.07],[.05,.2,.05],[.03,.15,.03],[0,0,0]])
        if edge:u[:,0]=u[:,1]*2
        if censored:u[-1,0]=np.nan
        columns=g.columns_from_arrays(u,np.zeros_like(u),[3.9,4,4.1],220.,7,[0,1,2],90)
        section={'entity_id':config['entity_id'],'snapshot_time_utc':'2022-01-15T00:00:00Z','source_returned_timestamp_utc':'2022-01-15T00:00:00Z',
            'section_definition':{'entity_id':config['entity_id'],'fixed_axis':'longitude','longitude_degrees_east':-140,'latitude_gate_degrees_north':[3.8,4.2]},
            'depth_levels_m':z,'columns':columns,'decoded_columns_sha256':g.canonical_hash(columns),
            'diagnosis':diagnose(z,[r['signed_reference_component_m_s'] for r in columns],config),
            'component_bearing_degrees_true':90,'actual_source_longitude_degrees_east':220.,'maximum_nearest_longitude_distance_km':0.,
            'native100m_temperature_degrees_celsius':None,'temperature_source':None,'eligibility':config['eligibility'],
            'retrieved_hyperslab':{'depth_indices_inclusive':[0,5],'latitude_indices_inclusive':[0,2],'longitude_index':7}}
        return section,config

    def test_two_distinct_currents_and_ten_ordered_partial_sections(self):
        expected={'current:pacific-north-subsurface-countercurrent':[-155,-147.5,-140,-132.5,-125],
            'current:atlantic-north-equatorial-undercurrent':[-40,-37.5,-35,-32.5,-30]}
        self.assertEqual(set(self.op['currents']),set(expected));self.assertEqual(len(self.op['sections']),10)
        for entity,values in expected.items():
            self.assertEqual([s['longitude_degrees_east'] for s in self.op['sections'] if s['entity_id']==entity],values)
        self.assertTrue(all(s['latitude_gate_degrees_north']==([2.5,6] if s['entity_id'].startswith('current:pacific') else [2,5]) for s in self.op['sections']))

    def test_all20_native_targets_preflight_under_original_caps_before_fields(self):
        plans,pairs=g.preflight(np.arange(-80,80.001,.04),np.arange(0,360,.08),self.op)
        self.assertEqual(len(plans),10);self.assertEqual(pairs,2*sum(40*len(p['latitude_indices']) for p in plans))
        self.assertLess(pairs,250000);self.assertLess(pairs*16,7000000)
        self.assertEqual(self.op['snapshot_times_utc'],['2022-01-15T00:00:00Z','2022-07-15T00:00:00Z'])
        self.assertEqual(self.op['maximum_component_read_attempts'],3)

    def test_declared_interval_without_surface_or_thermal_gate_and_no_promotion(self):
        self.assertEqual(self.op['selection_depth_interval_m'],[100,400]);self.assertEqual(self.op['core_search_depth_interval_m'],[100,400])
        self.assertIsNone(self.op['surface_component_gate_m_s']);self.assertEqual(self.op['thresholds_m_s'],[.05,.1,.2])
        for c in self.op['currents'].values():
            self.assertEqual(c['component_bearing_degrees_true'],90);self.assertEqual(c['primary_threshold_m_s'],.1)
            self.assertIsNone(c['surface_component_gate_m_s']);self.assertIsNone(c['temperature_gate'])
        self.assertFalse(any(self.op['eligibility'].values()));self.assertFalse(self.op['full_goal_complete'])
        self.assertEqual(self.op['maximum_total_temperature_scalars'],0)

    def test_subsurface_selection_audits_with_nonzero_upper_and_lower_beyond_interval(self):
        section,config=self.fixture();audit.validate_retained(section,config)
        self.assertEqual(section['diagnosis']['selected_column_index'],1)
        self.assertFalse(section['diagnosis']['surface_velocity_qualification_applied'])
        layer=next(r for r in section['diagnosis']['selected_column_threshold_layers'] if r['threshold_m_s']==.1)
        self.assertAlmostEqual(layer['upper_depth_m'],200/3);self.assertAlmostEqual(layer['lower_depth_m'],500)

    def test_identity_time_frame_interval_diagnosis_and_thermal_mutations_rejected(self):
        section,config=self.fixture()
        for key,value in [('entity_id','invented'),('source_returned_timestamp_utc','2022-01-15T03:00:00Z'),('component_bearing_degrees_true',270),('native100m_temperature_degrees_celsius',[1,2,3])]:
            bad=copy.deepcopy(section);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):audit.validate_retained(bad,config)
        bad=copy.deepcopy(section);bad['diagnosis']['selected_column_index']=0
        with self.assertRaises(ValueError):audit.validate_retained(bad,config)
        for field,value in [('surface_component_gate_m_s',.05),('selection_depth_interval_m',[100,300])]:
            changed=copy.deepcopy(config);changed[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):audit.validate_retained(section,changed)

    def test_raw_component_hash_and_signed_recalculation_mutations_rejected(self):
        section,config=self.fixture()
        bad=copy.deepcopy(section);bad['columns'][1]['eastward_velocity_m_s'][2]=.9
        with self.assertRaises(ValueError):audit.validate_retained(bad,config)
        bad['decoded_columns_sha256']=g.canonical_hash(bad['columns'])
        with self.assertRaises(ValueError):audit.validate_retained(bad,config)

    def test_native_geometry_indices_hyperslab_and_offset_mutations_rejected(self):
        section,config=self.fixture()
        for key,value in [('actual_source_longitude_degrees_east',219),('maximum_nearest_longitude_distance_km',1)]:
            bad=copy.deepcopy(section);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):audit.validate_retained(bad,config)
        bad=copy.deepcopy(section);bad['columns'][1]['global_latitude_index']=7;bad['decoded_columns_sha256']=g.canonical_hash(bad['columns'])
        with self.assertRaises(ValueError):audit.validate_retained(bad,config)
        bad=copy.deepcopy(section);bad['retrieved_hyperslab']['longitude_index']=8
        with self.assertRaises(ValueError):audit.validate_retained(bad,config)
        bad=copy.deepcopy(section);bad['columns'][1]['native_source_latitude_degrees_north']=4.01;bad['decoded_columns_sha256']=g.canonical_hash(bad['columns'])
        with self.assertRaises(ValueError):audit.validate_retained(bad,config)

    def test_selected_gate_edge_and_missing_lower_support_retained_without_substitution(self):
        section,config=self.fixture(edge=True,censored=True);audit.validate_retained(section,config)
        self.assertEqual(section['diagnosis']['selected_column_index'],0)
        self.assertEqual(section['diagnosis']['horizontal_selection_status'],'section_gate_edge_maximum_axis_unresolved')
        layer=next(r for r in section['diagnosis']['selected_column_threshold_layers'] if r['threshold_m_s']==.1)
        self.assertIsNone(layer['lower_depth_m']);self.assertIsNone(layer['layer_thickness_m'])
        self.assertEqual(layer['lower_last_connected_depth_m'],400)


if __name__=='__main__':unittest.main()
