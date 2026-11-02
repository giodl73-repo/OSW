import copy
import math
import unittest
import numpy as np
import acquire_three_current_depth_sections_v1 as s


class ThreeCurrentSectionTests(unittest.TestCase):
    def setUp(self):
        self.op={'entity_id':'current:oyashio','component_bearing_degrees_true':225,
                 'surface_component_gate_m_s':.05,'primary_threshold_m_s':.1,
                 'thresholds_m_s':[.05,.1,.2],'core_search_depth_interval_m':[0,200],
                 'temperature_gate':{'native_depth_m':100,'maximum_temperature_degrees_celsius':5},
                 'eligibility':{'whole_current_volume':False}}
        self.z=[0,100,200,400]
        self.columns=[[.2,.3,.2,-.1],[.4,.5,.4,-.1],[.1,.2,.1,-.1]]

    def test_warm_stronger_column_excluded_before_selection(self):
        result=s.selection(self.z,self.columns,self.op,[5,5.01,4])
        self.assertEqual(result['selected_column_index'],0)
        self.assertTrue(result['candidate_scores'][1]['eligible_before_water_mass_gate'])
        self.assertFalse(result['candidate_scores'][1]['temperature_gate_passed'])
        self.assertEqual(result['horizontal_selection_status'],'section_gate_edge_maximum_axis_unresolved')

    def test_temperature_boundary_inclusive_missing_excluded_and_no_fallback(self):
        self.assertEqual(s.selection(self.z,self.columns,self.op,[None,5,None])['selected_column_index'],1)
        result=s.selection(self.z,self.columns,self.op,[None,5.001,8])
        self.assertIsNone(result['selected_column_index'])
        self.assertEqual(result['horizontal_selection_status'],'no_qualifying_surface_connected_cold_component_column')

    def test_temperature_neighbour_is_not_velocity_support_edge(self):
        result=s.selection(self.z,self.columns,self.op,[8,4,None])
        self.assertIn('interior_section_integral_maximum',result['horizontal_selection_status'])
        columns=copy.deepcopy(self.columns);columns[0][1]=None
        result=s.selection(self.z,columns,self.op,[8,4,4])
        self.assertEqual(result['horizontal_selection_status'],'upper_layer_support_edge_maximum_axis_unresolved')

    def test_invalid_temperature_data_rejected(self):
        for values in [None,[4],[4,math.nan,4],[4,math.inf,4],[4,-6,4],[4,46,4]]:
            with self.assertRaises(ValueError):s.selection(self.z,self.columns,self.op,values)

    def test_nonthermal_currents_reproduce_frozen_selector(self):
        op={**self.op,'temperature_gate':None,'component_bearing_degrees_true':180}
        self.assertEqual(s.selection(self.z,self.columns,op),s.base_selection(self.z,self.columns,op))
        op['primary_threshold_m_s']=.05
        small=[[.06]*4,[.08,.09,.08,-.1],[.06]*4]
        self.assertEqual(s.selection(self.z,small,op)['selected_column_index'],1)
        self.assertIsNone(s.selection(self.z,small,{**op,'primary_threshold_m_s':.1})['selected_column_index'])

    def test_qualifying_ties_and_peaks_retained(self):
        result=s.selection(self.z,[self.columns[0],self.columns[1],self.columns[1],self.columns[0]],self.op,[4]*4)
        self.assertEqual(result['selected_column_index'],1)
        self.assertEqual(result['local_integral_maximum_indices'],[1,2])
        self.assertFalse(result['multiple_peaks_are_independent_currents'])

    def test_signed_directions_and_counterflow_preserved(self):
        np.testing.assert_allclose(s.along_velocity(np.array([0.,0.]),np.array([-1.,1.]),180),[1,-1])
        np.testing.assert_allclose(s.along_velocity(np.array([-1.,1.]),np.array([-1.,1.]),225),[math.sqrt(2),-math.sqrt(2)])

    def test_full_native_eastern_and_wrapped_western_gates(self):
        self.assertEqual(s.longitude_indices(np.arange(120.,141.),[125,130]).tolist(),list(range(5,11)))
        self.assertEqual(s.longitude_indices(np.arange(300.,331.),[-57,-47]).tolist(),list(range(3,14)))
        for axis,gate in [([], [125,130]),([125,127,126],[125,130]),(np.arange(120,141),[130,125]),(np.arange(120,141),[170,-170]),(np.linspace(120,140,1000),[125,130])]:
            with self.assertRaises(ValueError):s.longitude_indices(axis,gate)

    def test_layers_retain_internal_gaps_and_individual_threshold_cores(self):
        columns=copy.deepcopy(self.columns);columns[1]=[.06,.6,.2,-.2]
        primary=s.diagnose(self.z,columns,self.op,[4]*3)['selected_column_threshold_layers'][1]
        self.assertGreater(primary['upper_depth_m'],0)
        self.assertAlmostEqual(primary['lower_depth_m'],250)
        columns[1]=[.4,.8,.4,None]
        primary=s.diagnose(self.z,columns,self.op,[4]*3)['selected_column_threshold_layers'][1]
        self.assertIsNone(primary['lower_depth_m']);self.assertIsNone(primary['layer_thickness_m'])

    def test_retained_owner_time_frame_components_and_diagnosis(self):
        op={**self.op,'component_bearing_degrees_true':180,'temperature_gate':None}
        profiles=[]
        for i,column in enumerate(self.columns):
            u=np.zeros(4);v=-np.asarray(column,dtype=float)
            profiles.append({'native_source_longitude_degrees_east':125.+i,'sampled_lon_lat':[125.+i,8.],
                'eastward_velocity_m_s':s.clean(u),'northward_velocity_m_s':s.clean(v),
                'signed_reference_component_m_s':s.clean(s.along_velocity(u,v,180))})
        cols=[p['signed_reference_component_m_s'] for p in profiles]
        section={'entity_id':op['entity_id'],'source_returned_timestamp_utc':'2022-01-15T00:00:00Z',
                 'snapshot_time_utc':'2022-01-15T00:00:00Z','columns':profiles,'depth_levels_m':self.z,
                 'decoded_columns_sha256':s.canonical_hash(profiles),'diagnosis':s.diagnose(self.z,cols,op),
                 'native100m_temperature_degrees_celsius':None,'component_bearing_degrees_true':180,'eligibility':op['eligibility']}
        s.validate_retained(section,op)
        for key,value in [('entity_id','current:kuroshio'),('source_returned_timestamp_utc','2022-01-15T03:00:00Z'),('component_bearing_degrees_true',225),('decoded_columns_sha256','changed'),('eligibility',{'whole_current_volume':True})]:
            changed=copy.deepcopy(section);changed[key]=value
            with self.assertRaises(ValueError):s.validate_retained(changed,op)
        changed=copy.deepcopy(section);changed['columns'][0]['eastward_velocity_m_s'][0]=1
        changed['decoded_columns_sha256']=s.canonical_hash(changed['columns'])
        with self.assertRaises(ValueError):s.validate_retained(changed,op)

    def test_retained_temperature_pin_and_actual_time_audit(self):
        op={**self.op,'component_bearing_degrees_true':180}
        profiles=[]
        for i,column in enumerate(self.columns):
            u=np.zeros(4);v=-np.asarray(column,dtype=float)
            profiles.append({'native_source_longitude_degrees_east':125.+i,'sampled_lon_lat':[125.+i,8.],
                'eastward_velocity_m_s':s.clean(u),'northward_velocity_m_s':s.clean(v),
                'signed_reference_component_m_s':s.clean(s.along_velocity(u,v,180))})
        cols=[p['signed_reference_component_m_s'] for p in profiles];temps=[4,4,4]
        stamp='2022-01-15T00:00:00Z'
        receipt={'source_returned_timestamp_utc':stamp,'native_depth_m':100,'variable':'water_temp','decoded_values_sha256':s.canonical_hash(temps)}
        section={'entity_id':op['entity_id'],'source_returned_timestamp_utc':stamp,'snapshot_time_utc':stamp,
                 'columns':profiles,'depth_levels_m':self.z,'decoded_columns_sha256':s.canonical_hash(profiles),
                 'diagnosis':s.diagnose(self.z,cols,op,temps),'native100m_temperature_degrees_celsius':temps,
                 'temperature_source':receipt,'component_bearing_degrees_true':180,'eligibility':op['eligibility']}
        s.validate_retained(section,op)
        for key,value in [('source_returned_timestamp_utc','2022-01-15T03:00:00Z'),('native_depth_m',150),('decoded_values_sha256','changed')]:
            changed=copy.deepcopy(section);changed['temperature_source'][key]=value
            with self.assertRaises(ValueError):s.validate_retained(changed,op)


if __name__=='__main__':unittest.main()
