"""Finer hydrographic failures cannot be hidden between native velocity samples."""
import copy,json,unittest
from unittest.mock import patch
import derive_redsox_observed_depth_sections_v2 as derive
import redsox_native_union_depth_v2 as fine
import redsox_saline_component_depth_v1 as coarse


class NativeUnion(unittest.TestCase):
    def sources(self):return [100,110,120],[.3,.5,.3],list(range(100,121)),[39]*21,1
    def test_hidden_salinity_dip_is_found_while_coarse_grid_misses_it(self):
        vz,q,hz,s,c=self.sources();s[5]=37;grid=fine.union_grid(vz,q,hz,s,c);result=fine.diagnose(grid)
        coarse_s=derive.original.remap_salinity(hz,s,vz)[0];previous=coarse.diagnose(vz,q,coarse_s,c)
        self.assertIsNone(previous['upper']['boundary_depth_m']);self.assertEqual(result['upper']['limiting_criteria'],['salinity']);self.assertAlmostEqual(result['upper']['boundary_depth_m'],105.5);self.assertEqual(result['source_velocity_core_index'],c);self.assertEqual(result['original_core_depth_m'],110)
    def test_hidden_missing_hydrographic_sample_censors_without_bridge(self):
        vz,q,hz,s,c=self.sources();s[5]=None;r=fine.diagnose(fine.union_grid(vz,q,hz,s,c));self.assertIsNone(r['upper']['boundary_depth_m']);self.assertEqual(r['upper']['status'],'censored_before_incomplete_native_source_segment');self.assertEqual(r['upper']['salinity_segment_support'],'missing');self.assertEqual(r['upper']['last_connected_depth_m'],106)
    def test_wide_hydrographic_gap_between_exact_nodes_is_still_a_barrier(self):
        g=fine.union_grid([100,110,120],[.3,.5,.3],[100,110,120],[39,39,39],1);r=fine.diagnose(g);self.assertEqual(r['upper']['salinity_segment_support'],'gap');self.assertIsNone(r['upper']['boundary_depth_m']);self.assertIsNone(r['lower']['boundary_depth_m'])
    def test_dense_hydrography_does_not_repair_wide_velocity_gap(self):
        g=fine.union_grid([100,140],[.5,.3],list(range(100,141)),[39]*41,0);r=fine.diagnose(g);self.assertEqual(r['lower']['velocity_segment_support'],'gap');self.assertIsNone(r['lower']['boundary_depth_m']);self.assertIn(None,g['component_m_s'])
    def test_outside_hydrographic_support_is_unknown_without_extrapolation(self):
        g=fine.union_grid([100,110,120],[.3,.5,.3],list(range(105,116)),[39]*11,1);r=fine.diagnose(g);self.assertEqual(r['upper']['last_connected_depth_m'],105);self.assertEqual(r['lower']['last_connected_depth_m'],115);self.assertIsNone(r['joint_support_span_m'])
    def test_competing_crossings_choose_first_and_retain_native_brackets(self):
        g=fine.union_grid([100,110,120],[0,.5,0],list(range(100,121)),[35 if i==0 or i==20 else 39 for i in range(21)],1);r=fine.diagnose(g);self.assertAlmostEqual(r['upper']['boundary_depth_m'],104);self.assertAlmostEqual(r['lower']['boundary_depth_m'],116);self.assertEqual(r['upper']['limiting_criteria'],['velocity']);self.assertEqual(r['upper']['source_velocity_segment_indices'],[0,1]);self.assertEqual(r['upper']['fine_union_bracket_m'],[104,105])
    def test_frozen_core_failure_never_reselects_another_saltier_or_faster_node(self):
        vz,q,hz,s,c=self.sources();s[10]=37;r=fine.diagnose(fine.union_grid(vz,q,hz,s,c));self.assertEqual(r['status'],'original_velocity_core_not_in_declared_saline_class');self.assertFalse(r['core_reselected'])
        q[c]=.2;r=fine.diagnose(fine.union_grid(vz,q,hz,s,c));self.assertEqual(r['status'],'original_core_not_above_velocity_threshold')
    def test_every_native_knot_including_missing_is_retained_and_not_independent_data(self):
        vz,q,hz,s,c=self.sources();s[5]=None;g=fine.union_grid(vz,q,hz,s,c);self.assertEqual(g['depth_m'],hz);self.assertIsNone(g['salinity_psu'][5]);self.assertFalse(g['interpolated_velocity_is_new_observation']);self.assertFalse(g['union_spacing_is_native_velocity_resolution']);self.assertEqual(g['new_independent_samples'],0)
    def test_native_axes_and_omitted_source_knot_rejected(self):
        for args in [([100,90],[.3,.5],[100,101],[39,39],0),([100,110],[.3,.5],[100,100],[39,39],0),([100,110],[.3,.5],[100,110],[39,99],0)]:
            with self.assertRaises(ValueError):fine.union_grid(*args)
        with self.assertRaises(ValueError):fine.source_segment([0,5,10],[39]*3,0,10,5)


class ObservedUnion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('urllib.request.urlopen',side_effect=AssertionError('No retrieval')):cls.batches={name:derive.build(section=name) for name in derive.SECTIONS}
        cls.cases=[c for report,raw in cls.batches.values() for c in report['cases']];cls.previous=json.loads((derive.ROOT/derive.PREVIOUS).read_bytes());cls.old={c['station']:c for c in cls.previous['cases']}
    def test_both_original_batches_cover_every17_case_once_without_source_scope_change(self):
        self.assertEqual(len(self.cases),17);self.assertEqual(len({c['station'] for c in self.cases}),17)
        for name,(report,raw) in self.batches.items():self.assertEqual([c['station'] for c in report['cases']],derive.SECTIONS[name]);self.assertEqual(report['source_plan_case_count'],17);self.assertEqual(report['batch_case_count'],len(derive.SECTIONS[name]));self.assertLess(len(raw),2400000)
    def test_all_frozen_case_metadata_native_values_selection_and_old_diagnoses_preserved(self):
        for case in self.cases:
            old=self.old[case['station']]
            for key,value in old.items():
                if key!='joint_diagnosis':self.assertEqual(case[key],value,(case['station'],key))
            self.assertEqual(case['previous_velocity_grid_joint_diagnosis'],old['joint_diagnosis'])
    def test_all_four_supported_core_points_and_weak_core_outcomes_unchanged(self):
        supported=[]
        for c in self.cases:
            if not c['joint_diagnosis']:continue
            self.assertEqual(c['joint_diagnosis']['status'],self.old[c['station']]['joint_diagnosis']['status'])
            if c['joint_diagnosis']['status']=='conditional_saline_component_core_supported':supported.append(c['station']);self.assertEqual(c['joint_diagnosis']['original_core_depth_m'],self.old[c['station']]['core_depth_m']);self.assertTrue(c['frozen_velocity_core_and_point_salinity_reproduced_exactly'])
        self.assertEqual(set(supported),{8,9,73,62})
    def test_every_fine_hydrographic_knot_and_exact_velocity_seed_preserved(self):
        for c in self.cases:
            g=c['fine_source_union_grid']
            if not g:continue
            vz=c['native_velocity_depth_m'];expected=sorted(set(vz)|{z for z in c['native_hydrographic_depth_m'] if vz[0]<=z<=vz[-1]});self.assertEqual(g['depth_m'],expected);self.assertEqual(g['depth_m'][g['seed_union_index']],c['core_depth_m']);self.assertEqual(g['component_m_s'][g['seed_union_index']],c['core_component_m_s']);self.assertEqual(g['salinity_psu'][g['seed_union_index']],c['core_remapped_salinity_psu']);self.assertLessEqual(g['union_node_count'],6000)
    def test_selected_source_decoding_and_derived_grids_stay_in_joint_caps(self):
        actual=0
        for report,raw in self.batches.values():actual+=report['counts']['decoded_native_scalar_values_in_batch'];self.assertEqual(report['counts']['whole_cohort_native_scalar_reservation'],44726);self.assertLessEqual(report['counts']['maximum_conservative_input_and_derived_grid_bytes'],7000000)
        self.assertLessEqual(actual,44726)
    def test_original_quality_missing_and_provider_association_limits_unchanged(self):
        for c in self.cases:
            self.assertEqual(c['exclusion_reasons'],self.old[c['station']]['exclusion_reasons']);self.assertFalse(c['physical_cast_identity_independently_verified']);self.assertFalse(c['sample_level_synchronization_verified'])
            if c['exclusion_reasons']:self.assertIsNone(c['joint_diagnosis']);self.assertIsNone(c['fine_source_union_grid'])
    def test_no_native_resolution_error_bars_physical_geometry_volume_or_reference_promotion(self):
        for report,raw in self.batches.values():
            for key in ['new_ocean_field_requests','new_reference_inventory_rows','whole_route_physical_depth_profiles','volume_estimates']:self.assertEqual(report[key],0)
            self.assertFalse(report['runtime_changed']);self.assertFalse(report['full_goal_complete'])
        for c in self.cases:self.assertFalse(c['physical_current_bottom_established']);self.assertIsNone(c['physical_layer_thickness_m']);self.assertIsNone(c['volume_m3'])
    def test_explicit_section_required_and_source_helpers_frozen(self):
        with self.assertRaises(ValueError):derive.build()
        import derive_redsox_observed_depth_sections_v1 as v1
        self.assertIs(derive.original,v1)


if __name__=='__main__':unittest.main()
