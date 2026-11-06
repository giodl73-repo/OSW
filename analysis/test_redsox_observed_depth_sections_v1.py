"""Joint boundary limits, original source support and exclusion fidelity."""
import copy,json,unittest
from unittest.mock import patch
import derive_redsox_observed_depth_sections_v1 as build
import redsox_saline_component_depth_v1 as kernel


class SalineBoundary(unittest.TestCase):
    def fixture(self):return [100,110,120,130,140],[0,.3,.5,.3,0],[37,39,39,39,37],2
    def test_velocity_limits_first_and_both_candidates_preserved(self):
        r=kernel.diagnose(*self.fixture());self.assertEqual(r['status'],'conditional_saline_component_core_supported');self.assertEqual(r['upper']['limiting_criteria'],['velocity']);self.assertAlmostEqual(r['upper']['boundary_depth_m'],106.6666666667);self.assertAlmostEqual(r['lower']['boundary_depth_m'],133.3333333333);self.assertEqual(set(r['upper']['candidate_crossings_m']),{'velocity','salinity'})
    def test_salinity_limits_first_not_velocity_only_extension(self):
        z,q,s,c=self.fixture();s[0]=s[-1]=35;r=kernel.diagnose(z,q,s,c);self.assertEqual(r['upper']['limiting_criteria'],['salinity']);self.assertAlmostEqual(r['upper']['boundary_depth_m'],107.5);self.assertAlmostEqual(r['lower']['boundary_depth_m'],132.5)
    def test_inclusive_salinity_strict_velocity_and_no_core_replacement(self):
        z,q,s,c=self.fixture();s[c]=38;self.assertEqual(kernel.diagnose(z,q,s,c)['status'],'conditional_saline_component_core_supported');s[c]=37.99;self.assertEqual(kernel.diagnose(z,q,s,c)['status'],'original_velocity_core_not_in_declared_saline_class');q[c]=.2;self.assertEqual(kernel.diagnose(z,q,s,c)['status'],'original_core_not_above_velocity_threshold')
    def test_missing_gap_and_sampling_end_are_unknown_not_bed(self):
        z,q,s,c=self.fixture();s[1]=None;r=kernel.diagnose(z,q,s,c);self.assertIsNone(r['upper']['boundary_depth_m']);self.assertEqual(r['upper']['status'],'censored_before_missing_input');self.assertIsNone(r['joint_support_span_m'])
        r=kernel.diagnose([0,10,50],[.3,.4,.3],[39]*3,1);self.assertEqual(r['upper']['status'],'censored_at_native_sampling_end');self.assertEqual(r['lower']['status'],'censored_before_native_depth_gap')
    def test_invalid_axes_units_masks_and_core_rejected(self):
        for args in [([100,90],[.3,.4],[39,39],0),([0,10],[.3,.4],[39,99],0),([0,10],[.3,None],[39,39],2)]:
            with self.assertRaises(ValueError):kernel.diagnose(*args)
    def test_remapping_exact_finite_brackets_and_no_extrapolation(self):
        v,r=build.remap_salinity([0,1,2,3],[37,38,None,40],[-1,0,.5,1.5,3,4]);self.assertEqual(v,[None,37,37.5,None,40,None]);self.assertEqual(r[2]['hydrographic_indices'],[0,1]);self.assertEqual(r[3]['status'],'missing_or_over5m_hydrographic_bracket')
        v,r=build.remap_salinity([0,10],[37,39],[5]);self.assertEqual(v,[None])
    def test_pressure_conversion_is_derived_not_pressure_renaming(self):
        rows=[[0,38,20,25,0,1500],[1000,38,20,25,0,1500]];z,s,method=build.hydro_depths({'_p_data_units':'dbar','_S_data_units':'psu','lat':'12'},['p','S','T','sigma','o2','c'],rows)
        self.assertLess(z[1],1000);self.assertGreater(z[1],980);self.assertIn('gsw',method);self.assertEqual(s,[38,38])
    def test_explicit_depth_and_documented_unit_key_preserved(self):
        z,s,method=build.hydro_depths({'_p_data_units':'dbar','_S_data_units':'psu','_z_dat_units':'m'},['z','p','S','T','theta','sigma'],[[0,0,38,20,20,25],[10,10,38,20,20,25]]);self.assertEqual(z,[0,10]);self.assertIn('explicit_depth',method)


class ObservedCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('urllib.request.urlopen',side_effect=AssertionError('No retrieval')):cls.report,cls.raw=build.build()
    def test_all17_original_profiles_and_both_source_orders_retained(self):
        self.assertEqual(len(self.report['cases']),17);self.assertEqual(len({p['station'] for p in self.report['cases']}),17)
        for section,stations in build.SECTIONS.items():self.assertEqual([p['station'] for p in self.report['cases'] if p['section_id']==section],stations)
    def test_original_quality_and_missing_companion_are_not_replaced(self):
        by={p['station']:p for p in self.report['cases']}
        for station in [10,61,63,74]:self.assertEqual(by[station]['status'],'EXCLUDED_OR_UNRESOLVED_SOURCE_SUPPORT');self.assertIsNone(by[station]['joint_diagnosis'])
        self.assertIn('missing_hydrographic_companion',by[74]['exclusion_reasons']);self.assertIn('unverified_rejected_downcast_treatment',by[10]['exclusion_reasons'])
    def test_exact_parser_geometry_and_layer_functions_reused(self):
        import build_redsox_ladcp_source_inventory as lv
        import build_redsox_ctd_companion_inventory as cv
        import build_redsox_section3_spans as section
        import build_redsox_lower_nc_section as layer
        self.assertIs(build.parse_gpl,lv.parse_gpl);self.assertIs(build.parse_ctd,cv.parse_ctd);self.assertIs(build.section_geometry,section.geometry);self.assertIs(build.velocity_layer,layer.velocity_layer);self.assertIs(build.interpolate_complete,layer.interpolate_complete)
    def test_source_location_times_cast_and_clock_limits_are_explicit(self):
        for p in self.report['cases']:
            self.assertEqual(p['campaign'],'RSX1');self.assertEqual(p['entity_id'],'current:red-sea-saline-overflow');self.assertEqual(len(p['position_lon_lat']),2);self.assertFalse(p['physical_cast_identity_independently_verified']);self.assertFalse(p['sample_level_synchronization_verified']);self.assertFalse(p['tidal_correction_applied'])
    def test_core_selection_and_remapping_preserve_native_axis_and_no_saline_reselection(self):
        for p in self.report['cases']:
            if 'native_velocity_depth_m' not in p:continue
            c=p['core_index'];self.assertEqual(p['core_depth_m'],p['native_velocity_depth_m'][c]);self.assertEqual(p['selection_height_above_bottom_interval_m'],[20,200]);self.assertTrue(20<=p['core_height_above_bottom_m']<=200);self.assertFalse(p['core_reselected']);self.assertFalse(p['pressure_equals_depth']);self.assertEqual(len(p['salinity_remapping']),len(p['native_velocity_depth_m']));self.assertEqual(p['joint_diagnosis']['original_core_index'],c)
    def test_native_reservation_caps_and_output_caps(self):
        c=self.report['counts'];self.assertLessEqual(c['decoded_native_scalar_values'],c['planned_native_scalar_values']);self.assertLessEqual(c['planned_native_scalar_values'],250000);self.assertLessEqual(c['maximum_conservative_decoded_bytes'],7000000);self.assertLess(len(self.raw),2400000)
    def test_no_physical_volume_whole_route_annual_or_new_scalar_reference_promotion(self):
        for p in self.report['cases']:self.assertFalse(p['physical_current_bottom_established']);self.assertIsNone(p['physical_layer_thickness_m']);self.assertIsNone(p['volume_m3']);self.assertFalse(p['annual_extrema_established'])
        for key in ['new_ocean_field_requests','new_reference_inventory_rows','whole_route_physical_depth_profiles','volume_estimates']:self.assertEqual(self.report[key],0)
        self.assertFalse(self.report['runtime_changed']);self.assertFalse(self.report['full_goal_complete'])


if __name__=='__main__':unittest.main()
