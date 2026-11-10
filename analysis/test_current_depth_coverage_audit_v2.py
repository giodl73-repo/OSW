"""New primary coverage counts once while historical variants remain explicit."""
import copy,json,unittest
from unittest.mock import patch
import audit_current_depth_coverage_v2 as audit
import audit_current_depth_coverage_v1 as frozen


class UpdatedCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('urllib.request.urlopen',side_effect=AssertionError('No retrieval')):cls.report,cls.raw=audit.build()
        cls.previous=json.loads((audit.ROOT/'research/current-depth-coverage-audit-v1.json').read_bytes());cls.new_rows={r['entity_id']:r for r in cls.report['currents']};cls.old_rows={r['entity_id']:r for r in cls.previous['currents']}
    def test_frozen_join_implementation_and_input_metadata_preserved(self):
        self.assertIs(audit.frozen,frozen);op=json.loads((audit.ROOT/audit.OPERATOR).read_bytes());self.assertEqual(op['input_sha256']['analysis/audit_current_depth_coverage_v1.py'],self.previous['input_sha256']['analysis/audit_current_depth_coverage_v1.py'])
        self.assertEqual(self.report['schema'],'osw.current-depth-coverage-audit.v2');self.assertEqual(self.report['operator_file'],audit.OPERATOR)
    def test_balearic_all16_primary_cases_processed_12_resolved_4_unresolved(self):
        old=self.old_rows['current:balearic']['registered_model_sections'];new=self.new_rows['current:balearic']['registered_model_sections'];self.assertEqual(old['cases_with_contour_processing'],0);self.assertEqual(new['cases_with_contour_processing'],16);self.assertEqual(new['resolved_contours'],12);self.assertEqual(new['processed_unresolved_cases'],4);self.assertEqual(new['unprocessed_source_cases'],0);self.assertEqual(new['cases_with_declared_alternate_threshold_contours'],16)
    def test_56_duplicate_non_balearic_cases_do_not_inflate_primary_or_source_counts(self):
        old=self.previous['counts'];new=self.report['counts'];self.assertEqual(new['unique_registered_model_source_cases'],old['unique_registered_model_source_cases']);self.assertEqual(new['curtain_case_mentions'],old['curtain_case_mentions']+72);self.assertEqual(new['duplicate_curtain_mentions_removed'],old['duplicate_curtain_mentions_removed']+56);self.assertEqual(new['unique_cases_with_contour_processing'],old['unique_cases_with_contour_processing']+16);self.assertEqual(new['unique_source_cases_with_any_threshold_contours'],old['unique_source_cases_with_any_threshold_contours'])
    def test_ligurian_northern_and_algerian_unique_case_counts_unchanged(self):
        for owner in ['current:ligurian','current:northern-mediterranean','current:algerian']:self.assertEqual(self.new_rows[owner]['registered_model_sections'],self.old_rows[owner]['registered_model_sections'])
    def test_reference_native_units_fitted_profiles_and_identity_rows_unchanged(self):
        for key in ['reference_identities','reference_rows','reference_identities_with_direct_rows','fitted_profile_sensitivity_cases','fitted_finite_sensitivity_cases']:self.assertEqual(self.report['counts'][key],self.previous['counts'][key])
        self.assertEqual(self.report['reference_unit_counts'],{'m':807,'dbar':1});self.assertEqual(set(self.new_rows),set(self.old_rows))
        for owner,new in self.new_rows.items():
            old=self.old_rows[owner]
            for key in ['name','identity_level','direct_reference_rows','reference_metric_counts','reference_unit_counts','reference_evidence_kind_counts','fitted_profile_sensitivity_cases','fitted_finite_sensitivity_cases']:self.assertEqual(new[key],old[key])
    def test_updated_case_partitions_keep_all_remaining_gaps(self):
        c=self.report['registered_model_totals'];self.assertEqual(c['registered_source_cases'],1038);self.assertEqual(c['cases_with_contour_processing'],672);self.assertEqual(c['resolved_contours'],515);self.assertEqual(c['processed_unresolved_cases'],157);self.assertEqual(c['unprocessed_source_cases'],366);self.assertEqual(c['unprocessed_interior_cases'],295);self.assertEqual(c['unprocessed_unresolved_cases'],71)
    def test_configuration_restored_on_success_and_failure(self):
        previous=frozen.OPERATOR
        with patch.object(frozen,'build',return_value=({},b'')):audit.build()
        self.assertEqual(frozen.OPERATOR,previous)
        with patch.object(frozen,'build',side_effect=ValueError('fixture')):
            with self.assertRaises(ValueError):audit.build()
        self.assertEqual(frozen.OPERATOR,previous)
    def test_historical_alternate_cases_and_primary_only_policy_remain_explicit(self):
        self.assertEqual(self.report['alternate_threshold_cases'],self.previous['alternate_threshold_cases']);self.assertTrue(self.report['scope']['source_primary_contour_completion_only']);self.assertEqual(self.report['counts']['curtain_dataset_files'],15)
    def test_no_new_physical_depth_volume_reference_or_runtime_claim(self):
        for key in ['whole_route_physical_depth_profiles','volume_estimates','new_depth_references','new_ocean_field_requests']:self.assertEqual(self.report['counts'][key],0)
        for row in self.report['currents']:
            for key in ['whole_route_physical_depth_established','annual_depth_extrema_established','volume_estimate_established']:self.assertFalse(row[key])
        self.assertFalse(self.report['runtime_changed']);self.assertFalse(self.report['raw_ocean_field_data_reaudited']);self.assertFalse(self.report['full_goal_complete']);self.assertLess(len(self.raw),2400000)


if __name__=='__main__':unittest.main()
