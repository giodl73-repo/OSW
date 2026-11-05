"""Atlantic SECC batch adds all16 source cases once without changing identity scope."""
import json,unittest
from unittest.mock import patch
import audit_current_depth_coverage_v14 as audit
import audit_current_depth_coverage_v1 as frozen


class AtlanticSeccContextCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('urllib.request.urlopen',side_effect=AssertionError('No retrieval')):cls.report,cls.raw=audit.build()
        cls.previous=json.loads((audit.ROOT/'research/current-depth-coverage-audit-v13.json').read_bytes());cls.new_rows={r['entity_id']:r for r in cls.report['currents']};cls.old_rows={r['entity_id']:r for r in cls.previous['currents']}
    def test_validated_join_code_and_exact_source_register_unchanged(self):
        self.assertIs(audit.frozen,frozen);op=json.loads((audit.ROOT/audit.OPERATOR).read_bytes());self.assertEqual(op['input_sha256']['analysis/audit_current_depth_coverage_v1.py'],self.previous['input_sha256']['analysis/audit_current_depth_coverage_v1.py']);self.assertEqual(self.report['schema'],'osw.current-depth-coverage-audit.v14');self.assertEqual(self.report['operator_file'],audit.OPERATOR)
    def test_one_canonical_owner_all16_cases_processed_with_original_gaps(self):
        for owner,resolved,unresolved in [('current:atlantic-south-equatorial-countercurrent',10,6)]:
            old=self.old_rows[owner]['registered_model_sections'];new=self.new_rows[owner]['registered_model_sections'];self.assertEqual(old['cases_with_contour_processing'],0);self.assertEqual(new['registered_source_cases'],resolved+unresolved);self.assertEqual(new['cases_with_contour_processing'],resolved+unresolved);self.assertEqual(new['resolved_contours'],resolved);self.assertEqual(new['processed_unresolved_cases'],unresolved);self.assertEqual(new['unprocessed_source_cases'],0)
    def test_16_unique_additions_not_duplicate_or_new_source_cases(self):
        old=self.previous['counts'];new=self.report['counts'];self.assertEqual(new['unique_registered_model_source_cases'],old['unique_registered_model_source_cases']);self.assertEqual(new['curtain_case_mentions'],old['curtain_case_mentions']+16);self.assertEqual(new['unique_cases_with_contour_processing'],old['unique_cases_with_contour_processing']+16);self.assertEqual(new['duplicate_curtain_mentions_removed'],old['duplicate_curtain_mentions_removed']);self.assertEqual(new['unique_source_cases_with_any_threshold_contours'],old['unique_source_cases_with_any_threshold_contours']+16)
    def test_all_other_current_model_case_counts_unchanged(self):
        self.assertEqual(set(self.new_rows),set(self.old_rows))
        for owner in set(self.new_rows)-{'current:atlantic-south-equatorial-countercurrent'}:self.assertEqual(self.new_rows[owner]['registered_model_sections'],self.old_rows[owner]['registered_model_sections'])
    def test_reference_metrics_native_units_fitted_profiles_and_identities_unchanged(self):
        for key in ['reference_identities','reference_rows','reference_identities_with_direct_rows','fitted_profile_sensitivity_cases','fitted_finite_sensitivity_cases']:self.assertEqual(self.report['counts'][key],self.previous['counts'][key])
        self.assertEqual(self.report['reference_unit_counts'],{'m':807,'dbar':1})
        for owner,new in self.new_rows.items():
            for key in ['name','identity_level','direct_reference_rows','reference_metric_counts','reference_unit_counts','reference_evidence_kind_counts']:self.assertEqual(new[key],self.old_rows[owner][key])
    def test_all_registered_default_source_cases_processed(self):
        c=self.report['registered_model_totals'];self.assertEqual(c['registered_source_cases'],1038);self.assertEqual(c['cases_with_contour_processing'],1038);self.assertEqual(c['resolved_contours'],810);self.assertEqual(c['processed_unresolved_cases'],228)
        for key in ['unprocessed_source_cases','unprocessed_interior_cases','unprocessed_unresolved_cases']:self.assertEqual(c[key],0)
        cohort=next(r for r in self.report['source_cohort_backlog'] if r['facts_file']=='research/atlantic-secc-multi-context-depth-sections-source-facts-v1.json');self.assertEqual(cohort['registered_source_cases'],16);self.assertEqual(cohort['resolved_contours'],10);self.assertEqual(cohort['processed_unresolved_cases'],6)
    def test_both_contexts_inventory_preserves_one_owner_and_no_double_count(self):
        self.assertEqual(self.report['counts']['reference_identities'],111);self.assertEqual(self.report['counts']['curtain_dataset_files'],41);v=self.report['non_additive_diagnostic_context_coverage'];self.assertEqual(v['unique_shared_source_cases'],16);self.assertEqual(v['diagnostic_context_cases'],32);self.assertEqual(v['context_datasets'],2);self.assertFalse(v['vertical_contexts_are_additive']);self.assertFalse(v['contexts_are_independent_observations']);self.assertFalse(v['deep_context_added_to_source_case_totals']);self.assertEqual(v['additional_current_identities'],0);self.assertEqual(v['new_independent_observations'],0)
        self.assertEqual(v['contexts']['shallow']['status_counts'],{'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN':10,'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':6});self.assertEqual(v['contexts']['deep']['status_counts'],{'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN':9,'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':7});self.assertEqual(len({(c['source_file'],c['source_sha256']) for c in v['cases']}),16);self.assertEqual(len({(c['source_file'],c['source_sha256'],c['diagnostic_context_id']) for c in v['cases']}),32)
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
    def context_fixture(self):
        op=json.loads((audit.ROOT/audit.OPERATOR).read_bytes());spec=next(s for s in op['non_additive_context_datasets'] if s['context']=='deep');data=json.loads((audit.ROOT/spec['data']).read_bytes());case=data['cases'][0];source=json.loads((audit.ROOT/case['source_file']).read_bytes());original=json.loads((audit.ROOT/audit.SOURCE_OPERATOR).read_bytes());cfg={**original,**original['currents'][audit.OWNER]};return case,source,cfg,op
    def test_deep_context_never_attaches_to_frozen_default_join(self):
        import copy
        case,source,cfg,op=self.context_fixture();bad=copy.deepcopy(op);bad['curtain_datasets'].append(next(s for s in bad['non_additive_context_datasets'] if s['context']=='deep'))
        with self.assertRaises(ValueError):audit.context_inventory(audit.ROOT,bad)
    def test_missing_or_duplicate_context_rejected(self):
        import copy
        case,source,cfg,op=self.context_fixture()
        for specs in [op['non_additive_context_datasets'][:1],[op['non_additive_context_datasets'][0]]*2]:
            bad=copy.deepcopy(op);bad['non_additive_context_datasets']=specs
            with self.assertRaises(ValueError):audit.context_inventory(audit.ROOT,bad)
    def test_own_context_join_rejects_selection_window_status_or_physical_promotion(self):
        import copy
        case,source,cfg,op=self.context_fixture()
        for key,value in [('diagnostic_context_id','shallow'),('original_selected_column_index',-1),('selection_depth_interval_m',[0,100]),('vertical_contexts_are_additive',True),('contexts_are_independent_observations',True),('volume_m3',1),('source_context_diagnosis_sha256','0'*64)]:
            bad=copy.deepcopy(case);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):audit.validate_context_case(bad,source,cfg,'deep')
    def test_source_context_default_flags_frame_and_window_mutations_rejected(self):
        import copy
        case,source,cfg,op=self.context_fixture()
        for key,value in [('default_diagnostic_context_id','deep'),('vertical_contexts_are_additive',True),('contexts_are_independent_observations',True),('entity_id','current:other')]:
            bad=copy.deepcopy(source);bad[key]=value
            with self.assertRaises(ValueError):audit.validate_context_case(case,bad,cfg,'deep')
        bad=copy.deepcopy(cfg);bad['diagnostic_contexts']['deep']['selection_depth_interval_m']=[0,100]
        with self.assertRaises(ValueError):audit.validate_context_case(case,source,bad,'deep')
    def test_context_source_metadata_and_primary_layers_match_original_without_numeric_reanalysis(self):
        v=self.report['non_additive_diagnostic_context_coverage'];self.assertTrue(v['source_metadata_only_no_velocity_calculation']);self.assertEqual(v['default_context_in_source_case_totals'],'shallow')
        for case in v['cases']:self.assertEqual(case['entity_id'],audit.OWNER);self.assertEqual(case['primary_threshold_m_s'],.1);self.assertEqual(case['selection_depth_interval_m'],{'shallow':[0,100],'deep':[150,350]}[case['diagnostic_context_id']])


if __name__=='__main__':unittest.main()
