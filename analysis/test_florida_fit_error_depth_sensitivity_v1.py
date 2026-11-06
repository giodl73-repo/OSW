import copy,json,unittest
from unittest.mock import patch
import derive_florida_fit_error_depth_sensitivity_v1 as d
import derive_gulf_stream_fit_error_depth_sensitivity_v1 as shared


class FloridaFitSensitivity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('netCDF4.Dataset',side_effect=AssertionError('No retrieval')),patch('urllib.request.urlopen',side_effect=AssertionError('No retrieval')):cls.report,cls.raw=d.build()
        op=json.loads((d.ROOT/d.OPERATOR).read_bytes());cls.source=json.loads((d.ROOT/op['source_file']).read_bytes())
    def test_all13_original_profiles_and_phases_present(self):
        self.assertEqual(self.report['counts']['profile_cases'],13);self.assertEqual(self.report['counts']['mean_cases'],1);self.assertEqual(self.report['counts']['fitted_day15_phase_cases'],12);self.assertEqual({(c['source_product_kind'],c['calendar_month_phase']) for c in self.report['cases']},{('mean',None)}|{('annual_cycle',m) for m in range(1,13)});self.assertLess(len(self.raw),2400000)
    def test_all_nominal_source_selections_and_layers_reproduce(self):
        for row,c in zip(self.source['records'],self.report['cases']):
            self.assertEqual(c['selected_section_column_index'],row['selected_section_column_index']);self.assertEqual(c['horizontal_selection_status'],row['horizontal_selection_status']);self.assertTrue(c['nominal_diagnostics_and_selection_reproduced']);self.assertEqual(c['nominal_source_half_core_descriptor'],row['selected_profile']['half_sampled_core_component_decay']);self.assertFalse(c['horizontal_core_or_direction_reselected'])
    def test_original_censored_nominal_phase_not_made_finite(self):
        self.assertEqual(sum(c['sensitivity']['nominal_layer']['lower_status']=='adjacent_isotach_crossing' for c in self.report['cases']),12)
        for c in self.report['cases']:
            if c['sensitivity']['nominal_layer']['lower_status']!='adjacent_isotach_crossing':self.assertIsNone(c['sensitivity']['lower_depth_sensitivity_range_m'])
    def test_eastward_velocity_and_provider_direction_do_not_enter_northward_metric(self):
        row=copy.deepcopy(self.source['records'][0]);before=d.reproduce(row,[.05,.1,.2]);row['selected_profile']['source_values']['eastward_velocity']=[.7]*100;row['selected_profile']['source_values']['eastward_velocity_uncertainty']=[None]*100;row['selected_profile']['source_fit_support']['downstream_direction']=[210]*100;self.assertEqual(d.reproduce(row,[.05,.1,.2]),before)
    def test_missing_northward_error_cannot_select_another_core(self):
        row=copy.deepcopy(self.source['records'][0]);core=row['selected_profile']['half_sampled_core_component_decay']['core_index'];row['selected_profile']['source_values']['northward_velocity_uncertainty'][core]=None;result=d.reproduce(row,[.05,.1,.2]);self.assertEqual(result['lower_velocity_scenario_layer']['lower_status'],'no_qualifying_core');self.assertIsNone(result['lower_depth_sensitivity_range_m'])
    def test_frozen_shared_sensitivity_function_used_directly(self):self.assertIs(d.shared.sensitivity,shared.sensitivity)
    def test_selection_or_nominal_profile_tampering_rejected(self):
        row=copy.deepcopy(self.source['records'][0]);row['selected_section_column_index']=999
        with self.assertRaises(ValueError):d.reproduce(row,[.05,.1,.2])
        row=copy.deepcopy(self.source['records'][0]);row['selected_profile']['source_values']['northward_velocity'][0]=999
        with self.assertRaises(ValueError):d.reproduce(row,[.05,.1,.2])
    def test_no_confidence_physical_annual_or_volume_promotion(self):
        for c in self.report['cases']:
            s=c['sensitivity'];self.assertEqual(c['depth_levels_m'],list(range(10,1001,10)));self.assertFalse(c['timestamp_is_instantaneous_observation_date']);self.assertIsNone(s['uncertainty_m']);self.assertIsNone(s['annual_range_m'])
            for k in ['confidence_interval_established','component_covariance_used','normal_distribution_assumed','direction_uncertainty_propagated','core_selection_uncertainty_propagated','cutoff_uncertainty_propagated','physical_current_bottom_established','volume_eligible']:self.assertFalse(s[k])
        for k in ['new_ocean_field_requests','new_scalar_depth_references','physical_whole_route_depth_profiles','volume_estimates']:self.assertEqual(self.report['counts'][k],0)


if __name__=='__main__':unittest.main()
