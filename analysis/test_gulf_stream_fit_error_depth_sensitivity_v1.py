import copy,itertools,json,math,unittest
from unittest.mock import patch
import derive_gulf_stream_fit_error_depth_sensitivity_v1 as d


class AnalyticSensitivity(unittest.TestCase):
    def test_component_rectangle_projection_extrema(self):
        for angle in [0,35,90,210]:
            radius=d.rectangle_radius(.1,.2,angle);mean=d.source.project(.4,.7,angle);corners=[d.source.project(.4+a*.1,.7+b*.2,angle) for a,b in itertools.product([-1,1],repeat=2)];self.assertAlmostEqual(min(corners),mean-radius);self.assertAlmostEqual(max(corners),mean+radius)
    def test_analytic_crossings_at_fixed_nominal_cutoff(self):
        r=d.sensitivity([10,20,30,40],[1,.8,.3,.1],[.1]*4,0,.5);self.assertEqual(r['lower_depth_sensitivity_range_m'],[24.,28.]);self.assertEqual(r['nominal_layer']['lower_depth_m'],26.)
    def test_all_finite_rectangle_corners_stay_inside_sensitivity_range(self):
        z=[10,20,30,40];mean=[1,.8,.3,.1];r=d.sensitivity(z,mean,[.1]*4,0,.5)
        for signs in itertools.product([-1,1],repeat=4):
            layer=d.fitted_layer(z,[v+s*.1 for v,s in zip(mean,signs)],.5,0);self.assertGreaterEqual(layer['lower_depth_m'],r['lower_depth_sensitivity_range_m'][0]);self.assertLessEqual(layer['lower_depth_m'],r['lower_depth_sensitivity_range_m'][1])
    def test_zero_errors_reproduce_nominal_without_confidence_claim(self):
        r=d.sensitivity([10,20,30],[1,.8,.1],[0,0,0],0,.5);self.assertEqual(r['lower_velocity_scenario_layer'],r['nominal_layer']);self.assertEqual(r['upper_velocity_scenario_layer'],r['nominal_layer']);self.assertFalse(r['confidence_interval_established'])
    def test_weak_locked_core_not_replaced_by_deeper_qualifier(self):
        r=d.sensitivity([10,20,30],[1,.8,.1],[.6,0,0],0,.5);self.assertEqual(r['lower_velocity_scenario_layer']['lower_status'],'no_qualifying_core');self.assertIsNone(r['lower_depth_sensitivity_range_m'])
    def test_missing_error_censors_not_zero_or_bottom(self):
        r=d.sensitivity([10,20,30],[1,.8,.1],[.1,None,.1],0,.5);self.assertEqual(r['lower_velocity_scenario_layer']['lower_status'],'censored_before_missing_or_dry_level');self.assertIsNone(r['lower_depth_sensitivity_range_m']);self.assertIsNone(d.rectangle_radius(None,.1,0))
    def test_invalid_errors_and_profile_shapes_rejected(self):
        for error in [-1,float('nan'),float('inf'),True]:
            with self.assertRaises(ValueError):d.rectangle_radius(error,.1,45)
        with self.assertRaises(ValueError):d.sensitivity([10,20],[1,.1],[.1],0,.5)
    def test_native_shallow_and_deep_limits_remain_censored(self):
        r=d.sensitivity([10,20,30],[1,.9,.8],[0,0,0],0,.5);self.assertEqual(r['nominal_layer']['upper_status'],'censored_at_sample_domain_edge');self.assertEqual(r['nominal_layer']['lower_status'],'censored_at_sample_domain_edge');self.assertIsNone(r['lower_depth_sensitivity_range_m'])


class RetainedProfiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('netCDF4.Dataset',side_effect=AssertionError('No retrieval')),patch('urllib.request.urlopen',side_effect=AssertionError('No retrieval')):cls.report,cls.raw=d.build()
    def test_all65_source_cases_and_phases_preserved(self):
        self.assertEqual(self.report['counts']['profile_cases'],65);self.assertEqual(self.report['counts']['mean_cases'],5);self.assertEqual(self.report['counts']['fitted_day15_phase_cases'],60);self.assertEqual(len({(c['section_id'],c['source_product_kind'],c['calendar_month_phase']) for c in self.report['cases']}),65);self.assertLess(len(self.raw),2400000)
    def test_nominal_selection_direction_core_and_cutoff_unchanged(self):
        for c in self.report['cases']:
            self.assertTrue(c['nominal_diagnostics_and_selection_reproduced']);self.assertFalse(c['horizontal_core_or_direction_reselected']);s=c['sensitivity'];self.assertEqual(s['fixed_nominal_core_index'],c['nominal_source_half_core_descriptor']['core_index']);self.assertEqual(s['fixed_nominal_cutoff_m_s'],c['nominal_source_half_core_descriptor']['threshold_m_s'])
    def test_source_audit_and_projection_tampering_rejected(self):
        c=self.report['cases'][0];section=json.loads((d.ROOT/c['source_file']).read_bytes());row=section['records'][0]
        bad=copy.deepcopy(row);bad['selected_section_column_index']=999
        with self.assertRaises(ValueError):d.reproduce(bad,[.05,.1,.2])
        bad=copy.deepcopy(row);bad['selected_profile']['along_locked_mean_direction_m_s'][0]=999
        with self.assertRaises(ValueError):d.reproduce(bad,[.05,.1,.2])
    def test_no_confidence_physical_annual_or_volume_promotion(self):
        for c in self.report['cases']:
            s=c['sensitivity'];self.assertIsNone(s['uncertainty_m']);self.assertIsNone(s['annual_range_m'])
            for k in ['confidence_interval_established','component_covariance_used','normal_distribution_assumed','direction_uncertainty_propagated','core_selection_uncertainty_propagated','cutoff_uncertainty_propagated','physical_current_bottom_established','volume_eligible']:self.assertFalse(s[k])
            self.assertFalse(c['timestamp_is_instantaneous_observation_date']);self.assertFalse(c['whole_route_representative']);self.assertFalse(c['seasonal_extrema_eligible'])
    def test_source_grid_not_truncated_or_extrapolated(self):
        for c in self.report['cases']:self.assertEqual(c['depth_levels_m'],list(range(10,1001,10)));self.assertEqual(len(c['sensitivity']['projected_component_error_rectangle_radius_m_s']),100)
    def test_finite_sensitivity_ranges_order_nominal_crossings(self):
        for c in self.report['cases']:
            s=c['sensitivity'];pair=s['lower_depth_sensitivity_range_m']
            if pair is not None:self.assertLessEqual(pair[0],s['nominal_layer']['lower_depth_m']);self.assertLessEqual(s['nominal_layer']['lower_depth_m'],pair[1])
    def test_no_retrieval_or_scalar_reference_admission(self):
        for k in ['new_ocean_field_requests','new_scalar_depth_references','physical_whole_route_depth_profiles','volume_estimates']:self.assertEqual(self.report['counts'][k],0)


if __name__=='__main__':unittest.main()
