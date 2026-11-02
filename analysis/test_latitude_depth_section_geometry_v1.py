import copy
import json
from pathlib import Path
import unittest
import numpy as np
import latitude_depth_section_geometry_v1 as g

ROOT=Path(__file__).resolve().parents[1]


class LatitudeDepthGeometryTests(unittest.TestCase):
    def setUp(self):
        self.op=json.loads((ROOT/'research/greenland-depth-sections-operator-v1.json').read_bytes())

    def fixture(self):
        config={**self.op,**self.op['currents']['current:east-greenland']}
        z=[0,50,100,200,400]
        v=np.array([[-.2,-.5,-.2]]*4+[[0,0,0]])
        columns=g.columns_from_arrays(np.zeros_like(v),v,np.array([310,310.08,310.16]),64,7,np.array([0,1,2]),180)
        section={'entity_id':config['entity_id'],'source_returned_timestamp_utc':'2022-01-15T00:00:00Z','snapshot_time_utc':'2022-01-15T00:00:00Z',
            'columns':columns,'depth_levels_m':z,'decoded_columns_sha256':g.canonical_hash(columns),'native100m_temperature_degrees_celsius':None,'temperature_source':None,
            'diagnosis':g.diagnose(z,[r['signed_reference_component_m_s'] for r in columns],config),'eligibility':config['eligibility'],'component_bearing_degrees_true':180,
            'section_definition':{'entity_id':config['entity_id'],'fixed_axis':'latitude','latitude_degrees_north':64,'longitude_gate_degrees_east':[-50.1,-49.7]},
            'actual_source_latitude_degrees_north':64,'nearest_latitude_distance_km':0,
            'retrieved_hyperslab':{'depth_indices_inclusive':[0,4],'latitude_index':7,'longitude_indices_inclusive':[0,2]}}
        return section,config

    def test_native_wrapped_west_to_east_order_and_no_dateline_gate(self):
        np.testing.assert_array_equal(g.longitude_indices(np.arange(303,312),[-56,-50]),np.arange(1,8))
        for gate in [[170,-170],[-181,-175],[-50,-50],[-50,-49.99]]:
            with self.subTest(gate=gate),self.assertRaises(ValueError):g.longitude_indices(np.arange(0,360,.08),gate)

    def test_all28_original_targets_preflight_inside_caps(self):
        plans,pairs=g.preflight(np.arange(-80,80.001,.04),np.arange(0,360,.08),self.op)
        self.assertEqual(len(plans),14)
        self.assertEqual(pairs,2*sum(40*len(p['longitude_indices']) for p in plans))
        self.assertLess(pairs,250000);self.assertLess(pairs*16,7000000)

    def test_preflight_rejects_bad_axis_duplicate_owner_orientation_and_offset(self):
        lat=np.arange(-80,80.001,.04);lon=np.arange(0,360,.08)
        with self.assertRaises(ValueError):g.preflight(lat[::-1],lon,self.op)
        for change in ['duplicate','owner','orientation','latitude','offset']:
            op=copy.deepcopy(self.op)
            if change=='duplicate':op['sections'].append(op['sections'][0])
            elif change=='owner':op['sections'][0]['entity_id']='current:invented'
            elif change=='orientation':op['sections'][0]['fixed_axis']='longitude'
            elif change=='latitude':op['sections'][0]['latitude_degrees_north']=91
            else:op['maximum_nearest_latitude_distance_km']=-1
            with self.subTest(change=change),self.assertRaises(ValueError):g.preflight(lat,lon,op)

    def test_signed_components_and_missing_profiles_are_preserved(self):
        u=np.zeros((5,3));v=np.ones((5,3))*.3;v[2,1]=np.nan
        for bearing,expected in [(0,.3),(180,-.3)]:
            columns=g.columns_from_arrays(u,v,np.array([310,311,312]),64,7,np.array([0,1,2]),bearing)
            self.assertAlmostEqual(columns[0]['signed_reference_component_m_s'][0],expected)
            self.assertIsNone(columns[1]['signed_reference_component_m_s'][2])
            self.assertEqual(columns[0]['sampled_lon_lat'],[-50,64])

    def test_actual_component_and_geometry_audit_accepts_valid_section(self):
        section,config=self.fixture();g.validate_retained(section,config)
        self.assertEqual(section['diagnosis']['selected_column_index'],1)

    def test_geometry_mutations_rejected_after_rehashing_components(self):
        original,config=self.fixture()
        for change in ['longitude_index','latitude_index','native_latitude','wrapped_latitude','slice_bounds','offset','depth_bounds','orientation','gate']:
            section=copy.deepcopy(original)
            if change=='longitude_index':section['columns'][1]['global_longitude_index']=99
            elif change=='latitude_index':section['columns'][1]['global_latitude_index']=99
            elif change=='native_latitude':section['columns'][1]['native_source_latitude_degrees_north']=65
            elif change=='wrapped_latitude':section['columns'][1]['sampled_lon_lat'][1]=65
            elif change=='slice_bounds':section['retrieved_hyperslab']['longitude_indices_inclusive']=[0,3]
            elif change=='offset':section['nearest_latitude_distance_km']=1
            elif change=='depth_bounds':section['retrieved_hyperslab']['depth_indices_inclusive']=[0,3]
            elif change=='orientation':section['section_definition']['fixed_axis']='longitude'
            else:section['section_definition']['longitude_gate_degrees_east']=[-49.9,-49.7]
            section['decoded_columns_sha256']=g.canonical_hash(section['columns'])
            with self.subTest(change=change),self.assertRaises(ValueError):g.validate_retained(section,config)

    def test_original_members_reaches_and_opposite_frames(self):
        self.assertEqual(set(self.op['currents']),{'current:east-greenland','current:west-greenland'})
        expected={'current:east-greenland':[78.5,76,73,70,67,64,61,59],'current:west-greenland':[59.4,60.5,61.5,63,65,67]}
        for entity,values in expected.items():
            self.assertEqual([s['latitude_degrees_north'] for s in self.op['sections'] if s['entity_id']==entity],values)
            self.assertEqual(self.op['currents'][entity]['component_bearing_degrees_true'],180 if entity=='current:east-greenland' else 0)

    def test_no_watermass_bottom_physical_or_annual_promotion(self):
        self.assertFalse(any(self.op['eligibility'].values()))
        for c in self.op['currents'].values():
            self.assertEqual(c['primary_threshold_m_s'],.1);self.assertEqual(c['surface_component_gate_m_s'],.05)
            self.assertIsNone(c['temperature_gate'])
        self.assertFalse(self.op['full_goal_complete'])


if __name__=='__main__':unittest.main()
