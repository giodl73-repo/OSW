import copy
import inspect
import json
from pathlib import Path
import unittest
import numpy as np
import latitude_depth_section_geometry_v1 as geometry
import latitude_interval_section_audit_v1 as audit
from interval_depth_diagnostic_v1 import diagnose


class MauritaniaBaffinIntervalSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((Path(__file__).resolve().parents[1]/'research/mauritania-baffin-interval-depth-sections-operator-v1.json').read_bytes())

    def fixture(self,entity='current:mauritanian',edge=False,censored=False):
        config={**self.op,**self.op['currents'][entity]};z=[0,50,100,200,300,500,700]
        signed=np.array([[0,-.1,0],[.01,.02,.01],[.01,.2,.01],[.01,.3,.01],[.01,.2,.01],[.01,.02,.01],[0,-.1,0]])
        if edge:signed[:,0]=signed[:,1]
        if censored:signed[-2:,0]=np.nan
        baffin=entity=='current:baffin';v=-signed if baffin else signed
        lat=70 if baffin else 18;lons=np.array([293.2,293.28,293.36]) if baffin else np.array([342.8,342.88,342.96])
        columns=geometry.columns_from_arrays(np.zeros_like(v),v,lons,lat,7,np.array([0,1,2]),config['component_bearing_degrees_true'])
        section={'entity_id':entity,'snapshot_time_utc':'2022-03-15T00:00:00Z','source_returned_timestamp_utc':'2022-03-15T00:00:00Z',
            'section_definition':{'entity_id':entity,'fixed_axis':'latitude','latitude_degrees_north':lat,'longitude_gate_degrees_east':[-70,-63] if baffin else [-18.5,-16]},
            'depth_levels_m':z,'columns':columns,'decoded_columns_sha256':geometry.canonical_hash(columns),
            'diagnosis':diagnose(z,[r['signed_reference_component_m_s'] for r in columns],config),
            'component_bearing_degrees_true':config['component_bearing_degrees_true'],'actual_source_latitude_degrees_north':lat,'nearest_latitude_distance_km':0.,
            'native100m_temperature_degrees_celsius':None,'temperature_source':None,'eligibility':config['eligibility'],
            'retrieved_hyperslab':{'depth_indices_inclusive':[0,6],'longitude_indices_inclusive':[0,2],'latitude_index':7}}
        return section,config

    def test_distinct_currents_frames_partial_reaches_intervals_and_cutoffs(self):
        expected={'current:mauritanian':([17,17.5,18,18.5,19],[[-18.5,-16]]*5,[50,300],.1,0),
            'current:baffin':([74.5,73,71.5,70,68.5],[[-78,-71],[-76,-68],[-73,-66],[-70,-63],[-67,-60]],[100,300],.05,180)}
        self.assertEqual(set(self.op['currents']),set(expected))
        for entity,(latitudes,gates,interval,threshold,frame) in expected.items():
            c=self.op['currents'][entity];sections=[s for s in self.op['sections'] if s['entity_id']==entity]
            self.assertEqual([s['latitude_degrees_north'] for s in sections],latitudes)
            self.assertEqual([s['longitude_gate_degrees_east'] for s in sections],gates)
            self.assertEqual(c['core_search_depth_interval_m'],interval);self.assertEqual(c['selection_depth_interval_m'],interval)
            self.assertEqual(c['primary_threshold_m_s'],threshold);self.assertEqual(c['component_bearing_degrees_true'],frame)
            self.assertIsNone(c['surface_component_gate_m_s']);self.assertIsNone(c['temperature_gate'])

    def test_all40_quarterly_targets_preflight_under_unchanged_caps(self):
        plans,pairs=geometry.preflight(np.arange(-80,80.001,.04),np.arange(0,360,.08),self.op)
        self.assertEqual(len(plans),10);self.assertEqual(pairs,4*sum(40*len(p['longitude_indices']) for p in plans))
        self.assertLess(pairs,250000);self.assertLess(pairs*16,7000000)
        self.assertEqual(self.op['snapshot_times_utc'],['2022-03-15T00:00:00Z','2022-06-15T00:00:00Z','2022-09-15T00:00:00Z','2022-12-15T00:00:00Z'])
        self.assertEqual(self.op['maximum_component_read_attempts'],3)
        self.assertFalse(any(self.op['eligibility'].values()));self.assertFalse(self.op['full_goal_complete'])
        self.assertEqual(self.op['maximum_total_temperature_scalars'],0)

    def test_latitude_audit_body_unchanged_and_both_source_frames_pass(self):
        self.assertEqual(inspect.getsource(audit.validate_retained).strip(),inspect.getsource(geometry.validate_retained).strip())
        for entity in self.op['currents']:
            section,config=self.fixture(entity);audit.validate_retained(section,config)
            self.assertEqual(section['diagnosis']['selected_column_index'],1)

    def test_opposing_surface_does_not_remove_subsurface_layer_or_clip_window(self):
        for entity,top,bottom in [('current:mauritanian',50+(.1-.02)/(.2-.02)*50,300+(.2-.1)/(.2-.02)*200),
                                  ('current:baffin',50+(.05-.02)/(.2-.02)*50,300+(.2-.05)/(.2-.02)*200)]:
            section,config=self.fixture(entity);audit.validate_retained(section,config)
            self.assertFalse(section['diagnosis']['surface_velocity_qualification_applied'])
            layer=next(r for r in section['diagnosis']['selected_column_threshold_layers'] if r['threshold_m_s']==config['primary_threshold_m_s'])
            self.assertAlmostEqual(layer['upper_depth_m'],top);self.assertAlmostEqual(layer['lower_depth_m'],bottom)
            self.assertGreater(layer['lower_depth_m'],config['selection_depth_interval_m'][1])

    def test_raw_hash_component_time_frame_and_diagnosis_mutations_rejected(self):
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
        for key,value in [('actual_source_latitude_degrees_north',18.1),('nearest_latitude_distance_km',1)]:
            bad=copy.deepcopy(section);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):audit.validate_retained(bad,config)
        for field,value in [('global_longitude_index',7),('global_latitude_index',8),('native_source_latitude_degrees_north',18.1)]:
            bad=copy.deepcopy(section);bad['columns'][1][field]=value;bad['decoded_columns_sha256']=geometry.canonical_hash(bad['columns'])
            with self.subTest(field=field),self.assertRaises(ValueError):audit.validate_retained(bad,config)
        bad=copy.deepcopy(section);bad['retrieved_hyperslab']['longitude_indices_inclusive']=[0,3]
        with self.assertRaises(ValueError):audit.validate_retained(bad,config)

    def test_first_western_tie_gate_edge_and_censored_lower_remain_unresolved(self):
        section,config=self.fixture(edge=True,censored=True);audit.validate_retained(section,config)
        self.assertEqual(section['diagnosis']['selected_column_index'],0)
        self.assertEqual(section['diagnosis']['horizontal_selection_status'],'section_gate_edge_maximum_axis_unresolved')
        layer=next(r for r in section['diagnosis']['selected_column_threshold_layers'] if r['threshold_m_s']==.1)
        self.assertIsNone(layer['lower_depth_m']);self.assertIsNone(layer['layer_thickness_m'])
        self.assertEqual(layer['lower_last_connected_depth_m'],300)

    def test_no_positive_surface_or_unequal_interval_substitution(self):
        section,config=self.fixture();audit.validate_retained(section,config)
        self.assertEqual(section['diagnosis']['selection_depth_interval_m'],[50,300])
        for field,value in [('surface_component_gate_m_s',.05),('selection_depth_interval_m',[100,300])]:
            changed=copy.deepcopy(config);changed[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):audit.validate_retained(section,changed)

    def test_baffin_southward_frame_preserves_raw_sign_and_rejects_northward_substitution(self):
        section,config=self.fixture('current:baffin');audit.validate_retained(section,config)
        column=section['columns'][1]
        self.assertLess(column['northward_velocity_m_s'][3],0)
        self.assertGreater(column['signed_reference_component_m_s'][3],0)
        self.assertGreater(column['northward_velocity_m_s'][0],0)
        changed={**config,'component_bearing_degrees_true':0}
        with self.assertRaises(ValueError):audit.validate_retained(section,changed)


if __name__=='__main__':unittest.main()
