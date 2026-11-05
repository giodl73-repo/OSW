import copy,csv,io,itertools,json,socket,unittest
from unittest.mock import patch
import audit_eac_mooring_window_depth_sensitivity_v2 as audit

class EACWindowSensitivity(unittest.TestCase):
    def test_fixed34_level_window_anchor_priority_and_cumulative40(self):
        rows=[{'source_threshold_m_s':t,'endpoint_source_indices':pair} for t,pair in [(0.05,[30,31]),(0.1,[45,46]),(0.2,[60,61])]]
        old={30,31,45,46,60,61};w=audit.select_window(100,rows,old)
        self.assertEqual(w['anchor_threshold_m_s'],0.1);self.assertEqual(w['window_source_indices'],list(range(29,63)))
        self.assertLessEqual(len(w['combined_selected_indices']),40);self.assertFalse(w['selection_uses_error_values'])
        rows[1]['endpoint_source_indices']=None;self.assertEqual(audit.select_window(100,rows,old)['anchor_threshold_m_s'],0.05)
        rows[0]['endpoint_source_indices']=None;self.assertEqual(audit.select_window(100,rows,old)['anchor_threshold_m_s'],0.2)
        rows[2]['endpoint_source_indices']=None;self.assertIsNone(audit.select_window(100,rows,set()))
        with self.assertRaises(ValueError):audit.select_window(100,rows,set(range(7)))

    def test_clipped_window_not_shifted_or_padded_for_success(self):
        rows=[{'source_threshold_m_s':t,'endpoint_source_indices':[1,2] if t==0.1 else None} for t in [0.05,0.1,0.2]]
        w=audit.select_window(100,rows,{1,2});self.assertEqual(w['window_source_indices'],list(range(19)))
        self.assertFalse(w['clipped_window_shifted_or_extended'])

    def test_all32_corner_profiles_bounded_by_componentwise_extreme_responses(self):
        z=[0,10,20,30,40];v=[0.5,0.4,0.2,0,-0.1];se=[0.02]*5
        nominal=audit.first_crossing(z,v,0.1)['depth_m'];r=audit.sensitivity(z,v,se,0.1,nominal)
        self.assertEqual(r['status'],'COMPLETE_CONDITIONAL_WINDOW_RESPONSE')
        low,high=r['complete_conditional_depth_response_range_m']
        for signs in itertools.product([-1,1],repeat=5):
            perturbed=[a+b*e for a,b,e in zip(v,signs,se)];x=audit.first_crossing(z,perturbed,0.1)['depth_m']
            self.assertIsNotNone(x);self.assertLessEqual(low,x);self.assertLessEqual(x,high)
        self.assertFalse(r['source_error_independence_assumed']);self.assertFalse(r['confidence_interval_established'])

    def test_gap_and_bottom_censor_not_interpolated_or_extended(self):
        self.assertEqual(audit.first_crossing([0,10,20],[0.5,None,0],0.1)['status'],'CENSORED_BEFORE_MISSING_WINDOW_LEVEL')
        self.assertEqual(audit.first_crossing([0,10,20],[0.5,0.4,0.3],0.1)['status'],'CENSORED_AT_WINDOW_BOTTOM')
        r=audit.sensitivity([0,10,20],[0.5,0.2,0],[0.01,0.01,0.2],0.1,15)
        self.assertIsNone(r['complete_conditional_depth_response_range_m']);self.assertIsNone(r['upper_component_scenario']['depth_m'])

    def test_fixed_entry_and_original_nominal_component_not_replaced(self):
        r=audit.sensitivity([0,10,20],[0.15,0.3,0],[0.1,0.01,0.01],0.1,10+20/3)
        self.assertEqual(r['lower_component_scenario']['status'],'WINDOW_ENTRY_NOT_QUALIFYING')
        self.assertIsNone(r['complete_conditional_depth_response_range_m'])
        r=audit.sensitivity([0,10,20],[0.5,0.2,0],[0.01]*3,0.1,99)
        self.assertFalse(r['original_nominal_crossing_reproduced']);self.assertIsNone(r['complete_conditional_depth_response_range_m'])
        first=audit.first_crossing([0,10,20,30],[0.4,0,0.4,0],0.1)
        self.assertAlmostEqual(first['depth_m'],7.5);self.assertEqual(first['window_bracket_indices'],[0,1])

    def test_missing_error_unknown_and_negative_error_rejected(self):
        r=audit.sensitivity([0,10,20],[0.5,0.2,0],[0.01,None,0.01],0.1,15)
        self.assertIsNone(r['complete_conditional_depth_response_range_m'])
        with self.assertRaises(ValueError):audit.sensitivity([0,10,20],[0.5,0.2,0],[0.01,-0.01,0.01],0.1,15)

    def test_actual_all_profiles_contexts_selected_union_and_no_native_source_mutation(self):
        raw=(audit.ROOT/audit.SOURCE).read_bytes();prior=(audit.ROOT/audit.PRIOR).read_bytes();r=audit.build()
        self.assertEqual((audit.ROOT/audit.SOURCE).read_bytes(),raw);self.assertEqual((audit.ROOT/audit.PRIOR).read_bytes(),prior)
        self.assertEqual(len(r['profiles']),14);self.assertEqual(len(r['outcomes']),42)
        self.assertEqual(r['counts']['nominal_resolved_lower_boundaries'],16);self.assertEqual(r['counts']['original_nominal_boundary_unresolved'],26)
        self.assertLessEqual(r['counts']['maximum_cumulative_selected_levels_per_profile'],40)
        self.assertLessEqual(r['counts']['selected_source_scalar_touches'],1680)
        self.assertLessEqual(r['counts']['cumulative_support_and_derived_node_bound'],6000)
        for p in r['profiles']:
            w=p['window_selection']
            if w:self.assertEqual(w['window_source_indices'],list(range(w['window_source_indices'][0],w['window_source_indices'][-1]+1)))
        self.assertEqual(r['conservative_combined_case_scalar_reservation'],82214)

    def test_actual_output_network_free_csv_nulls_and_physical_gates(self):
        def denied(*a,**k):raise RuntimeError('No source replay')
        with patch.object(socket,'socket',denied),patch.object(socket,'create_connection',denied):r=audit.build()
        table=list(csv.DictReader(io.StringIO(audit.csv_bytes(r['outcomes']).decode())))
        self.assertEqual(len(table),42)
        for row,original in zip(table,r['outcomes']):
            a=original['sensitivity']
            if a is None or a['complete_conditional_depth_response_range_m'] is None:
                self.assertEqual(row['complete_response_min_m'],'');self.assertEqual(row['complete_response_max_m'],'')
            if a:
                self.assertIsNone(a['physical_depth_uncertainty_m']);self.assertIsNone(a['annual_depth_range_m']);self.assertIsNone(a['physical_thickness_m'])
                for key in ['full_profile_or_original_core_connection_reassessed','confidence_interval_established','physical_current_bottom_established','volume_eligible','physical_state_join_eligible','reference_route_projection_eligible','seasonal_playback_eligible']:self.assertFalse(a[key])

if __name__=='__main__':unittest.main()
