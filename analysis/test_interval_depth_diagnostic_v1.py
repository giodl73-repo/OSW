import copy
import unittest
from interval_depth_diagnostic_v1 import diagnose,selection,INTERIOR
from acquire_north_brazil_depth_sections_v1 import selection as surface_selection
from derive_eac_connected_layer_thickness_v1 import connected_layer


class IntervalDepthDiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.z=[0,20,100,200,500,800]
        self.op={'selection_depth_interval_m':[20,500],'core_search_depth_interval_m':[20,500],
            'surface_component_gate_m_s':None,'primary_threshold_m_s':.1,'thresholds_m_s':[.05,.1,.2]}
        self.weak=[0,.02,.03,.02,.01,0];self.strong=[-.1,.15,.4,.3,.2,0]

    def test_subsurface_profile_has_nonzero_top_and_bottom_beyond_search_window(self):
        result=diagnose(self.z,[self.weak,self.strong,self.weak],self.op)
        self.assertEqual(result['selected_column_index'],1);self.assertEqual(result['horizontal_selection_status'],INTERIOR)
        layer=result['selected_column_threshold_layers'][1]
        self.assertAlmostEqual(layer['upper_depth_m'],16);self.assertAlmostEqual(layer['lower_depth_m'],650)
        self.assertAlmostEqual(layer['layer_thickness_m'],634)
        self.assertEqual(layer['core_depth_m'],100)

    def test_separate_surface_method_keeps_its_original_failure(self):
        columns=[self.weak,self.strong,self.weak]
        old=surface_selection(self.z,columns,{'primary_threshold_m_s':.1,'surface_component_gate_m_s':.05})
        self.assertIsNone(old['selected_column_index'])
        self.assertEqual(selection(self.z,columns,self.op)['selected_column_index'],1)

    def test_missing_surface_does_not_invent_a_zero_top(self):
        column=self.strong[:];column[0]=None
        result=diagnose(self.z,[self.weak,column,self.weak],self.op)
        layer=result['selected_column_threshold_layers'][1]
        self.assertIsNone(layer['upper_depth_m']);self.assertEqual(layer['lower_depth_m'],650)
        self.assertIsNone(layer['layer_thickness_m']);self.assertIn('censored',layer['upper_status'])

    def test_missing_interval_sample_is_not_bridged(self):
        column=self.strong[:];column[2]=None
        result=diagnose(self.z,[self.weak,column,self.weak],self.op)
        self.assertIsNone(result['selected_column_index']);self.assertEqual(result['selected_column_threshold_layers'],[])
        self.assertIsNone(result['candidate_scores'][1]['signed_selection_interval_integral_m2_s'])

    def test_missing_lower_support_is_not_a_500m_bottom(self):
        column=self.strong[:];column[-1]=None
        layer=diagnose(self.z,[self.weak,column,self.weak],self.op)['selected_column_threshold_layers'][1]
        self.assertIsNone(layer['lower_depth_m']);self.assertEqual(layer['lower_last_connected_depth_m'],500)

    def test_support_edge_winner_is_retained_instead_of_weaker_interior(self):
        missing=self.weak[:];missing[2]=None;weaker=[0,.12,.2,.18,.15,0]
        result=selection(self.z,[missing,self.strong,weaker,self.weak],self.op)
        self.assertEqual(result['selected_column_index'],1)
        self.assertEqual(result['horizontal_selection_status'],'selection_interval_support_edge_maximum_axis_unresolved')

    def test_ties_keep_first_western_native_column_even_at_gate_edge(self):
        result=selection(self.z,[self.strong,self.strong,self.weak],self.op)
        self.assertEqual(result['selected_column_index'],0)
        self.assertEqual(result['horizontal_selection_status'],'section_gate_edge_maximum_axis_unresolved')

    def test_signed_integral_and_interval_core_reject_unrepresentative_peaks(self):
        spike=[10,.02,.9,-.5,-.5,0];broad=[0,.2,.3,.2,.15,0]
        result=selection(self.z,[self.weak,spike,broad,self.weak],self.op)
        self.assertEqual(result['selected_column_index'],2)
        surface_only=[10,.02,.03,.02,.01,0]
        self.assertIsNone(selection(self.z,[surface_only]*3,self.op)['selected_column_index'])

    def test_invalid_support_and_method_declarations_fail_closed(self):
        for z,col in [([0,25,100,200,500,800],self.strong),(self.z[::-1],self.strong),(self.z,[float('nan')]+self.strong[1:]),(self.z,self.strong[:-1])]:
            with self.subTest(z=z,col=col),self.assertRaises(ValueError):selection(z,[col]*3,self.op)
        for key,value in [('surface_component_gate_m_s',.05),('core_search_depth_interval_m',[0,200]),('primary_threshold_m_s',0)]:
            op=copy.deepcopy(self.op);op[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):selection(self.z,[self.strong]*3,op)

    def test_sensitivity_layers_reuse_frozen_contours_at_same_selected_column(self):
        result=diagnose(self.z,[self.weak,self.strong,self.weak],self.op)
        self.assertEqual(result['selected_column_threshold_layers'],[connected_layer(self.z,self.strong,t,[20,500]) for t in [.05,.1,.2]])


if __name__=='__main__':unittest.main()
