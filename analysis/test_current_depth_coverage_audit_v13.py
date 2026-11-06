"""Spitsbergen Atlantic batch adds all16 source cases once without changing identity scope."""
import json,unittest
from unittest.mock import patch
import audit_current_depth_coverage_v13 as audit
import audit_current_depth_coverage_v1 as frozen


class SpitsbergenAtlanticCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('urllib.request.urlopen',side_effect=AssertionError('No retrieval')):cls.report,cls.raw=audit.build()
        cls.previous=json.loads((audit.ROOT/'research/current-depth-coverage-audit-v12.json').read_bytes());cls.new_rows={r['entity_id']:r for r in cls.report['currents']};cls.old_rows={r['entity_id']:r for r in cls.previous['currents']}
    def test_validated_join_code_and_exact_source_register_unchanged(self):
        self.assertIs(audit.frozen,frozen);op=json.loads((audit.ROOT/audit.OPERATOR).read_bytes());self.assertEqual(op['input_sha256']['analysis/audit_current_depth_coverage_v1.py'],self.previous['input_sha256']['analysis/audit_current_depth_coverage_v1.py']);self.assertEqual(self.report['schema'],'osw.current-depth-coverage-audit.v13');self.assertEqual(self.report['operator_file'],audit.OPERATOR)
    def test_one_canonical_owner_all16_cases_processed_with_original_gaps(self):
        for owner,resolved,unresolved in [('current:spitsbergen-atlantic',7,9)]:
            old=self.old_rows[owner]['registered_model_sections'];new=self.new_rows[owner]['registered_model_sections'];self.assertEqual(old['cases_with_contour_processing'],0);self.assertEqual(new['registered_source_cases'],resolved+unresolved);self.assertEqual(new['cases_with_contour_processing'],resolved+unresolved);self.assertEqual(new['resolved_contours'],resolved);self.assertEqual(new['processed_unresolved_cases'],unresolved);self.assertEqual(new['unprocessed_source_cases'],0)
    def test_16_unique_additions_not_duplicate_or_new_source_cases(self):
        old=self.previous['counts'];new=self.report['counts'];self.assertEqual(new['unique_registered_model_source_cases'],old['unique_registered_model_source_cases']);self.assertEqual(new['curtain_case_mentions'],old['curtain_case_mentions']+16);self.assertEqual(new['unique_cases_with_contour_processing'],old['unique_cases_with_contour_processing']+16);self.assertEqual(new['duplicate_curtain_mentions_removed'],old['duplicate_curtain_mentions_removed']);self.assertEqual(new['unique_source_cases_with_any_threshold_contours'],old['unique_source_cases_with_any_threshold_contours']+16)
    def test_all_other_current_model_case_counts_unchanged(self):
        self.assertEqual(set(self.new_rows),set(self.old_rows))
        for owner in set(self.new_rows)-{'current:spitsbergen-atlantic'}:self.assertEqual(self.new_rows[owner]['registered_model_sections'],self.old_rows[owner]['registered_model_sections'])
    def test_reference_metrics_native_units_fitted_profiles_and_identities_unchanged(self):
        for key in ['reference_identities','reference_rows','reference_identities_with_direct_rows','fitted_profile_sensitivity_cases','fitted_finite_sensitivity_cases']:self.assertEqual(self.report['counts'][key],self.previous['counts'][key])
        self.assertEqual(self.report['reference_unit_counts'],{'m':807,'dbar':1})
        for owner,new in self.new_rows.items():
            for key in ['name','identity_level','direct_reference_rows','reference_metric_counts','reference_unit_counts','reference_evidence_kind_counts']:self.assertEqual(new[key],self.old_rows[owner][key])
    def test_updated_backlog_and_original_spitsbergen_cohort_exact_counts(self):
        c=self.report['registered_model_totals'];self.assertEqual(c['registered_source_cases'],1038);self.assertEqual(c['cases_with_contour_processing'],1022);self.assertEqual(c['resolved_contours'],800);self.assertEqual(c['processed_unresolved_cases'],222);self.assertEqual(c['unprocessed_source_cases'],16);self.assertEqual(c['unprocessed_interior_cases'],10);self.assertEqual(c['unprocessed_unresolved_cases'],6)
        cohort=next(r for r in self.report['source_cohort_backlog'] if r['facts_file']=='research/spitsbergen-atlantic-interval-depth-sections-source-facts-v1.json');self.assertEqual(cohort['registered_source_cases'],16);self.assertEqual(cohort['resolved_contours'],7);self.assertEqual(cohort['processed_unresolved_cases'],9);self.assertEqual(cohort['unprocessed_source_cases'],0)
    def test_original_owner_frame_interval_and_quarterly_dates_preserved(self):
        self.assertEqual(self.report['counts']['reference_identities'],111);self.assertEqual(self.report['counts']['identity_rows_including_any_extra_direct_owners'],111);self.assertEqual(self.report['counts']['curtain_dataset_files'],40)
        op=json.loads((audit.ROOT/audit.OPERATOR).read_bytes());new=[spec for spec in op['curtain_datasets'] if 'spitsbergen-atlantic-spitsbergen-atlantic-' in spec['data']];self.assertEqual(len(new),1)
        original=json.loads((audit.ROOT/'research/spitsbergen-atlantic-interval-depth-sections-operator-v1.json').read_bytes());data=json.loads((audit.ROOT/new[0]['data']).read_bytes());owner='current:spitsbergen-atlantic';self.assertEqual(data['batch_current_id'],owner);self.assertEqual(data['source_plan_case_count'],16);self.assertEqual(set(data['counts_by_current']),{owner});config=original['currents'][owner];self.assertEqual(config['selection_depth_interval_m'],[50,300]);self.assertEqual(config['core_search_depth_interval_m'],[50,300]);self.assertIsNone(config['surface_component_gate_m_s']);self.assertFalse(original['full_wsc_name_equivalence_admitted']);self.assertIsNone(config['parent_current_id']);self.assertFalse(config['parent_depth_values_inherited']);self.assertEqual({case['snapshot_time_utc'] for case in data['cases']},set(original['snapshot_times_utc']))
        for case in data['cases']:self.assertEqual(case['velocity_threshold_m_s'],.1);self.assertEqual(case['component_bearing_degrees_true'],315);self.assertEqual(case['source_geometry'],'latitude');self.assertNotIn('geometry_adapter',case);self.assertFalse(case['named_current_axis_independently_validated'])
    def test_configuration_restores_after_success_or_failure(self):
        prior=frozen.OPERATOR
        with patch.object(frozen,'build',return_value=({},b'')):audit.build()
        self.assertEqual(frozen.OPERATOR,prior)
        with patch.object(frozen,'build',side_effect=ValueError('fixture')):
            with self.assertRaises(ValueError):audit.build()
        self.assertEqual(frozen.OPERATOR,prior)
    def test_no_physical_volume_reference_or_runtime_promotion(self):
        for key in ['whole_route_physical_depth_profiles','volume_estimates','new_depth_references','new_ocean_field_requests']:self.assertEqual(self.report['counts'][key],0)
        for row in self.report['currents']:
            for key in ['whole_route_physical_depth_established','annual_depth_extrema_established','volume_estimate_established']:self.assertFalse(row[key])
        self.assertEqual(self.report['alternate_threshold_cases'],self.previous['alternate_threshold_cases']);self.assertFalse(self.report['runtime_changed']);self.assertFalse(self.report['raw_ocean_field_data_reaudited']);self.assertFalse(self.report['full_goal_complete']);self.assertLess(len(self.raw),2400000)


if __name__=='__main__':unittest.main()
