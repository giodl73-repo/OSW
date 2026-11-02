import copy
import inspect
import json
from pathlib import Path
import unittest
import numpy as np
import latitude_depth_section_geometry_v1 as geometry
import latitude_interval_section_audit_v1 as audit
from interval_depth_diagnostic_v1 import diagnose


class LoopAntillesIntervalSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((Path(__file__).resolve().parents[1]/'research/loop-antilles-interval-depth-sections-operator-v1.json').read_bytes())

    def fixture(self,entity='current:antilles',edge=False,censored=False):
        config={**self.op,**self.op['currents'][entity]};z=[0,100,200,400,700,1000]
        v=np.array([[0,-.1,0],[.01,.1,.01],[.02,.3,.02],[.02,.4,.02],[.01,.1,.01],[0,-.1,0]])
        if edge:v[:,0]=v[:,1]
        if censored:v[-1,0]=np.nan
        columns=geometry.columns_from_arrays(np.zeros_like(v),v,np.array([283.2,283.28,283.36]),26.5,7,np.array([0,1,2]),0)
        section={'entity_id':entity,'snapshot_time_utc':'2022-03-15T00:00:00Z','source_returned_timestamp_utc':'2022-03-15T00:00:00Z',
            'section_definition':{'entity_id':entity,'fixed_axis':'latitude','latitude_degrees_north':26.5,'longitude_gate_degrees_east':[-77.5,-73]},
            'depth_levels_m':z,'columns':columns,'decoded_columns_sha256':geometry.canonical_hash(columns),
            'diagnosis':diagnose(z,[r['signed_reference_component_m_s'] for r in columns],config),
            'component_bearing_degrees_true':0,'actual_source_latitude_degrees_north':26.5,'nearest_latitude_distance_km':0.,
            'native100m_temperature_degrees_celsius':None,'temperature_source':None,'eligibility':config['eligibility'],
            'retrieved_hyperslab':{'depth_indices_inclusive':[0,5],'longitude_indices_inclusive':[0,2],'latitude_index':7}}
        return section,config

    def test_distinct_currents_partial_reaches_intervals_and_cutoffs(self):
        expected={'current:loop':([23,24,25,26,27],[-89,-83],[0,200],.1),
            'current:antilles':([26,26.25,26.5,26.75,27],[-77.5,-73],[100,700],.05)}
        self.assertEqual(set(self.op['currents']),set(expected))
        for entity,(latitudes,gate,interval,threshold) in expected.items():
            c=self.op['currents'][entity];sections=[s for s in self.op['sections'] if s['entity_id']==entity]
            self.assertEqual([s['latitude_degrees_north'] for s in sections],latitudes)
            self.assertTrue(all(s['longitude_gate_degrees_east']==gate for s in sections))
            self.assertEqual(c['core_search_depth_interval_m'],interval);self.assertEqual(c['selection_depth_interval_m'],interval)
            self.assertEqual(c['primary_threshold_m_s'],threshold);self.assertEqual(c['component_bearing_degrees_true'],0)
            self.assertIsNone(c['surface_component_gate_m_s']);self.assertIsNone(c['temperature_gate'])

    def test_all40_quarterly_targets_preflight_under_unchanged_caps(self):
        plans,pairs=geometry.preflight(np.arange(-80,80.001,.04),np.arange(0,360,.08),self.op)
        self.assertEqual(len(plans),10);self.assertEqual(pairs,4*sum(40*len(p['longitude_indices']) for p in plans))
        self.assertLess(pairs,250000);self.assertLess(pairs*16,7000000)
        self.assertEqual(self.op['snapshot_times_utc'],['2022-03-15T00:00:00Z','2022-06-15T00:00:00Z','2022-09-15T00:00:00Z','2022-12-15T00:00:00Z'])
        self.assertEqual(self.op['maximum_component_read_attempts'],3)
        self.assertFalse(any(self.op['eligibility'].values()));self.assertFalse(self.op['full_goal_complete'])
        self.assertEqual(self.op['maximum_total_temperature_scalars'],0)

    def test_latitude_geometry_audit_body_is_unchanged_and_interval_source_passes(self):
        self.assertEqual(inspect.getsource(audit.validate_retained).strip(),inspect.getsource(geometry.validate_retained).strip())
        section,config=self.fixture();audit.validate_retained(section,config)
        self.assertEqual(section['diagnosis']['selected_column_index'],1)

    def test_antilles_subsurface_layer_has_nonzero_top_and_lower_beyond_seed(self):
        section,config=self.fixture();audit.validate_retained(section,config)
        self.assertFalse(section['diagnosis']['surface_velocity_qualification_applied'])
        layer=next(r for r in section['diagnosis']['selected_column_threshold_layers'] if r['threshold_m_s']==.05)
        self.assertAlmostEqual(layer['upper_depth_m'],75);self.assertAlmostEqual(layer['lower_depth_m'],775)

    def test_raw_hash_component_time_frame_and_interval_diagnosis_mutations_rejected(self):
        section,config=self.fixture()
        for key,value in [('entity_id','invented'),('source_returned_timestamp_utc','2022-03-15T03:00:00Z'),('component_bearing_degrees_true',180),('native100m_temperature_degrees_celsius',[1,2,3])]:
            bad=copy.deepcopy(section);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):audit.validate_retained(bad,config)
        bad=copy.deepcopy(section);bad['columns'][1]['northward_velocity_m_s'][2]=.9
        with self.assertRaises(ValueError):audit.validate_retained(bad,config)
        bad['decoded_columns_sha256']=geometry.canonical_hash(bad['columns'])
        with self.assertRaises(ValueError):audit.validate_retained(bad,config)
        bad=copy.deepcopy(section);bad['diagnosis']['selected_column_index']=0
        with self.assertRaises(ValueError):audit.validate_retained(bad,config)

    def test_native_latitude_longitude_hyperslab_and_offset_mutations_rejected(self):
        section,config=self.fixture()
        for key,value in [('actual_source_latitude_degrees_north',26.6),('nearest_latitude_distance_km',1)]:
            bad=copy.deepcopy(section);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):audit.validate_retained(bad,config)
        for field,value in [('global_longitude_index',7),('global_latitude_index',8),('native_source_latitude_degrees_north',26.6)]:
            bad=copy.deepcopy(section);bad['columns'][1][field]=value;bad['decoded_columns_sha256']=geometry.canonical_hash(bad['columns'])
            with self.subTest(field=field),self.assertRaises(ValueError):audit.validate_retained(bad,config)
        bad=copy.deepcopy(section);bad['retrieved_hyperslab']['longitude_indices_inclusive']=[0,3]
        with self.assertRaises(ValueError):audit.validate_retained(bad,config)

    def test_first_western_tie_gate_edge_and_censored_lower_remain_unresolved(self):
        section,config=self.fixture(edge=True,censored=True);audit.validate_retained(section,config)
        self.assertEqual(section['diagnosis']['selected_column_index'],0)
        self.assertEqual(section['diagnosis']['horizontal_selection_status'],'section_gate_edge_maximum_axis_unresolved')
        layer=next(r for r in section['diagnosis']['selected_column_threshold_layers'] if r['threshold_m_s']==.05)
        self.assertIsNone(layer['lower_depth_m']);self.assertIsNone(layer['layer_thickness_m'])
        self.assertEqual(layer['lower_last_connected_depth_m'],700)

    def test_loop_current_window_is_distinct_and_no_surface_or_unequal_interval_substitution(self):
        section,config=self.fixture(entity='current:loop');audit.validate_retained(section,config)
        self.assertEqual(section['diagnosis']['selection_depth_interval_m'],[0,200])
        self.assertEqual(config['primary_threshold_m_s'],.1)
        for field,value in [('surface_component_gate_m_s',.05),('selection_depth_interval_m',[100,700])]:
            changed=copy.deepcopy(config);changed[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):audit.validate_retained(section,changed)


if __name__=='__main__':unittest.main()
