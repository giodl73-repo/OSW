import copy
import math
import unittest
import numpy as np
import acquire_north_brazil_depth_sections_v1 as s


class NorthBrazilFullSectionTests(unittest.TestCase):
    def setUp(self):
        self.op={'surface_component_gate_m_s':.05,'primary_threshold_m_s':.1,'thresholds_m_s':[.05,.1,.2],
                 'core_search_depth_interval_m':[0,200],'eligibility':{'physical_current_depth':False}}
        self.z=[0,100,200,400]
        self.columns=[[.2,.3,.2,-.1],[.4,.5,.4,-.1],[.1,.2,.1,-.1]]

    def test_integrated_column_selection_not_largest_single_depth_spike(self):
        columns=[[.051,2.,.051,-.1],[1.2,1.2,1.2,-.1],[.1,.2,.1,-.1]]
        result=s.selection(self.z,columns,self.op)
        self.assertEqual(result['selected_column_index'],1)
        self.assertIn('interior_section_integral_maximum',result['horizontal_selection_status'])
        self.assertGreater(result['candidate_scores'][1]['signed_upper200m_integral_m2_s'],result['candidate_scores'][0]['signed_upper200m_integral_m2_s'])

    def test_first_native_longitude_breaks_ties_and_peaks_remain_visible(self):
        columns=[self.columns[0],self.columns[1],self.columns[1],self.columns[0]]
        result=s.selection(self.z,columns,self.op)
        self.assertEqual(result['selected_column_index'],1)
        self.assertEqual(result['local_integral_maximum_indices'],[1,2])
        self.assertFalse(result['multiple_peaks_are_independent_currents'])

    def test_complete_surface_connected_and_positive_integral_required(self):
        for column in [[None,.5,.2,-.1],[.04,2,1,-.1],[.05,2,1,-.1],[.1,.1,.1,-.1],[.051,.2,-4,-4]]:
            result=s.selection(self.z,[column]*3,self.op)
            self.assertIsNone(result['selected_column_index'])
            self.assertEqual(result['horizontal_selection_status'],'no_qualifying_surface_connected_component_column')

    def test_gate_edge_maximum_not_replaced_with_an_interior_candidate(self):
        columns=[self.columns[1],self.columns[0],self.columns[2]]
        result=s.selection(self.z,columns,self.op)
        self.assertEqual(result['selected_column_index'],0)
        self.assertEqual(result['horizontal_selection_status'],'section_gate_edge_maximum_axis_unresolved')

    def test_finite_support_edge_flag_is_separate_from_gate_edge(self):
        columns=[[None,.3,.2,-.1],self.columns[1],self.columns[2]]
        result=s.selection(self.z,columns,self.op)
        self.assertEqual(result['selected_column_index'],1)
        self.assertEqual(result['horizontal_selection_status'],'upper_layer_support_edge_maximum_axis_unresolved')

    def test_fixed_northwest_component_preserves_signed_deep_return(self):
        value=s.along_velocity(np.array([-1.,1.]),np.array([1.,-1.]),315)
        self.assertAlmostEqual(value[0],math.sqrt(2));self.assertAlmostEqual(value[1],-math.sqrt(2))

    def test_threshold_layers_keep_unknown_depth_gaps_and_nonzero_upper_boundary(self):
        columns=[self.columns[0],[.06,.6,.2,-.2],self.columns[2]]
        result=s.diagnose(self.z,columns,self.op);primary=result['selected_column_threshold_layers'][1]
        self.assertEqual(result['selected_column_index'],1)
        self.assertGreater(primary['upper_depth_m'],0);self.assertAlmostEqual(primary['lower_depth_m'],250)
        self.assertAlmostEqual(primary['layer_thickness_m'],primary['lower_depth_m']-primary['upper_depth_m'])
        columns[1]=[.4,.8,.4,None]
        primary=s.diagnose(self.z,columns,self.op)['selected_column_threshold_layers'][1]
        self.assertIsNone(primary['lower_depth_m']);self.assertIsNone(primary['layer_thickness_m'])
        self.assertEqual(primary['lower_last_connected_depth_m'],200)

    def test_western_gate_uses_full_contiguous_native_longitudes(self):
        axis=np.arange(300.,330.)
        indices=s.longitude_indices(axis,[-57,-47])
        self.assertEqual(indices.tolist(),list(range(3,14)))
        self.assertEqual([s.wrapped_longitude(float(axis[i])) for i in indices],list(range(-57,-46)))

    def test_invalid_or_large_or_noncontiguous_sections_rejected_before_read(self):
        for axis,gate in [([],[-57,-47]),([[303,304]],[-57,-47]),([303,math.nan,305],[-57,-47]),([303,305,304],[-57,-47]),(np.arange(300,330),[-47,-57]),(np.arange(300,330),[0,10]),(np.linspace(300,330,1000),[-57,-47])]:
            with self.assertRaises(ValueError):s.longitude_indices(axis,gate)
        with self.assertRaises(ValueError):s.check_budget((40,4251,4500),0,250000)
        self.assertEqual(s.check_budget((40,1,125),0,250000),5000)

    def test_scoring_depth_support_and_profile_size_mismatch_rejected(self):
        with self.assertRaises(ValueError):s.selection([10,100,200,400],self.columns,self.op)
        with self.assertRaises(ValueError):s.selection([0,100,50,200],self.columns,self.op)
        with self.assertRaises(ValueError):s.selection(self.z,[self.columns[0][:-1]],self.op)

    def test_retained_actual_time_owner_hash_and_diagnosis_audit(self):
        profiles=[{'native_source_longitude_degrees_east':320+i,'sampled_lon_lat':[-40+i,0],
                   'signed_northwest_component_m_s':column} for i,column in enumerate(self.columns)]
        section={'entity_id':'current:north-brazil','snapshot_time_utc':'2022-01-15T00:00:00Z',
                 'source_returned_timestamp_utc':'2022-01-15T00:00:00Z','columns':profiles,'depth_levels_m':self.z,
                 'decoded_columns_sha256':s.canonical_hash(profiles),'diagnosis':s.diagnose(self.z,self.columns,self.op),
                 'eligibility':self.op['eligibility']}
        s.validate_retained(section,self.op)
        for key,value in [('entity_id','current:guiana'),('source_returned_timestamp_utc','2022-01-15T03:00:00Z'),('decoded_columns_sha256','changed')]:
            changed=copy.deepcopy(section);changed[key]=value
            with self.assertRaises(ValueError):s.validate_retained(changed,self.op)
        changed=copy.deepcopy(section);changed['diagnosis']['selected_column_index']=0
        with self.assertRaises(ValueError):s.validate_retained(changed,self.op)


if __name__=='__main__':unittest.main()
