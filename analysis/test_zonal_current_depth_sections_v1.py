import copy
import json
import unittest
import numpy as np
import acquire_zonal_current_depth_sections_v1 as s


class ZonalSectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.op=json.loads((s.ROOT/s.OPERATOR).read_bytes())

    def test_native_latitude_slices_inclusive_increasing_bounded(self):
        self.assertEqual(s.latitude_indices([-3,-2,-1,0,1,2,3],[-1,1]).tolist(),[2,3,4])
        for axis,gate in [([],[-1,1]),([[0,1]],[-1,1]),([0,float('nan'),1],[-1,1]),([1,0,-1],[-1,1]),([-2,0,-1,1],[-1,1]),([-1,0,1],[1,-1]),([-1,0,1],[-91,1]),(np.linspace(-5,5,1000),[-1,1])]:
            with self.assertRaises(ValueError):s.latitude_indices(axis,gate)

    def test_circular_longitudes_and_native_first_ties_include_date_line(self):
        axis=[0,90,180,270]
        self.assertEqual(s.nearest_longitude_index(axis,-180),2)
        self.assertEqual(s.nearest_longitude_index(axis,180),2)
        self.assertEqual(s.nearest_longitude_index(axis,-90),3)
        self.assertEqual(s.nearest_longitude_index([179,181],180),0)
        self.assertEqual(s.wrapped_longitude(180),-180)

    def test_full_declared_plan_has36_bounded_slices_before_field_reads(self):
        plans,pairs=s.preflight(np.arange(-80,90.001,.04),np.arange(0,360,.08),self.op)
        self.assertEqual(len(plans),18);self.assertGreater(pairs,0);self.assertLessEqual(pairs,250000)
        self.assertEqual(pairs,2*sum(40*len(r['latitude_indices']) for r in plans))
        self.assertLess(pairs*16,7000000)
        self.assertEqual(len({(r['definition']['entity_id'],r['definition']['id']) for r in plans}),18)

    def test_budget_gate_width_duplicate_and_native_offset_fail_in_preflight(self):
        lats=np.arange(-80,90.001,.04);lons=np.arange(0,360,.08)
        for key,value in [('maximum_total_cell_pairs',1),('maximum_total_decoded_velocity_bytes',1),('maximum_nearest_longitude_distance_km',.000001)]:
            op=copy.deepcopy(self.op);op[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):s.preflight(lats,lons,op)
        op=copy.deepcopy(self.op);op['sections'][0]['latitude_gate_degrees_north']=[20,60]
        with self.assertRaises(ValueError):s.preflight(lats,lons,op)
        op=copy.deepcopy(self.op);op['sections'].append(op['sections'][0])
        with self.assertRaises(ValueError):s.preflight(lats,lons,op)

    def test_depth_latitude_matrix_extraction_keeps_signed_return_and_indices(self):
        u=np.array([[.2,.3,.4],[.3,.6,.3],[.2,.4,.2],[-.2,-.3,-.4]])
        v=np.zeros_like(u);columns=s.columns_from_arrays(u,v,[-1,0,1],180.,7,[0,1,2],90)
        self.assertEqual([r['sampled_lon_lat'] for r in columns],[[-180.,-1.],[-180.,0.],[-180.,1.]])
        self.assertEqual(columns[1]['signed_reference_component_m_s'],[.3,.6,.4,-.3])
        self.assertEqual([r['global_latitude_index'] for r in columns],[0,1,2])
        self.assertTrue(all(r['global_longitude_index']==7 for r in columns))
        with self.assertRaises(ValueError):s.columns_from_arrays(u.T,v,[-1,0,1],180.,7,[0,1,2],90)

    def test_retained_native_geometry_owner_time_frame_and_component_audit(self):
        config={**self.op,**self.op['currents']['current:kuroshio-extension']}
        z=[0,100,200,400];u=np.array([[.2,.3,.2],[.3,.6,.3],[.2,.4,.2],[-.2,-.3,-.2]]);v=np.zeros_like(u)
        columns=s.columns_from_arrays(u,v,[-1,0,1],180.,7,[0,1,2],90)
        section={'entity_id':config['entity_id'],'snapshot_time_utc':'2022-01-15T00:00:00Z','source_returned_timestamp_utc':'2022-01-15T00:00:00Z',
            'section_definition':{'entity_id':config['entity_id'],'fixed_axis':'longitude','longitude_degrees_east':180,'latitude_gate_degrees_north':[-1,1]},
            'depth_levels_m':z,'columns':columns,'decoded_columns_sha256':s.canonical_hash(columns),
            'diagnosis':s.diagnose(z,[r['signed_reference_component_m_s'] for r in columns],config),
            'component_bearing_degrees_true':90,'actual_source_longitude_degrees_east':180.,'maximum_nearest_longitude_distance_km':0.,
            'native100m_temperature_degrees_celsius':None,'temperature_source':None,'eligibility':config['eligibility'],
            'retrieved_hyperslab':{'depth_indices_inclusive':[0,3],'latitude_indices_inclusive':[0,2],'longitude_index':7}}
        s.validate_retained(section,config)
        for key,value in [('source_returned_timestamp_utc','2022-01-15T03:00:00Z'),('component_bearing_degrees_true',0),('actual_source_longitude_degrees_east',179),('maximum_nearest_longitude_distance_km',1),('entity_id','current:kuroshio')]:
            bad=copy.deepcopy(section);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):s.validate_retained(bad,config)
        bad=copy.deepcopy(section);bad['columns'][1]['global_latitude_index']=7;bad['decoded_columns_sha256']=s.canonical_hash(bad['columns'])
        with self.assertRaises(ValueError):s.validate_retained(bad,config)
        bad=copy.deepcopy(section);bad['retrieved_hyperslab']['longitude_index']=8
        with self.assertRaises(ValueError):s.validate_retained(bad,config)

    def test_frozen_selector_uses_first_southern_tie_and_retains_censored_depth(self):
        config={**self.op,**self.op['currents']['current:kuroshio-extension']}
        z=[0,100,200,400];columns=[[.2,.3,.2,-.1],[.4,.8,.4,None],[.4,.8,.4,None],[.2,.3,.2,-.1]]
        result=s.diagnose(z,columns,config)
        self.assertEqual(result['selected_column_index'],1);self.assertEqual(result['local_integral_maximum_indices'],[1,2])
        primary=next(r for r in result['selected_column_threshold_layers'] if r['threshold_m_s']==.1)
        self.assertIsNone(primary['lower_depth_m']);self.assertIsNone(primary['layer_thickness_m'])

    def test_declared_currents_frames_primary_gates_and_no_promotions(self):
        self.assertEqual(set(self.op['currents']),{'current:kuroshio-extension','current:agulhas-return','current:north-pacific'})
        self.assertFalse(any(self.op['eligibility'].values()))
        for entity,config in self.op['currents'].items():
            self.assertEqual(config['component_bearing_degrees_true'],90);self.assertIsNone(config['temperature_gate'])
            self.assertEqual(config['primary_threshold_m_s'],.05 if entity=='current:north-pacific' else .1)
            self.assertEqual(config['surface_component_gate_m_s'],.02 if entity=='current:north-pacific' else .05)
        npc=[r['longitude_degrees_east'] for r in self.op['sections'] if r['entity_id']=='current:north-pacific']
        self.assertEqual(npc,[160,170,180,-170,-160,-150,-145])


if __name__=='__main__':unittest.main()
