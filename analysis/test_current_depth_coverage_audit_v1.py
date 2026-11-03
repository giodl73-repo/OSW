"""Coverage joins reject mismatched provenance and preserve scoped gaps."""
import copy,unittest
from unittest.mock import patch
import audit_current_depth_coverage_v1 as audit


def fixture():
    row={'entity_id':'current:fixture','section_id':'s','snapshot_time_utc':'2022-01-15T00:00:00Z','horizontal_selection_status':audit.INTERIOR,'selected_column_index':1,'primary_threshold_m_s':.1,'primary_lower_status':'adjacent_isotach_crossing','source_file':'source.json','source_sha256':'a'*64}
    case={'entity_id':row['entity_id'],'section_id':'s','snapshot_time_utc':row['snapshot_time_utc'],'original_horizontal_selection_status':audit.INTERIOR,'original_selected_column_index':1,'velocity_threshold_m_s':.1,'source_file':row['source_file'],'source_sha256':row['source_sha256'],'core_reselected':False,'physical_current_bottom_established':False,'volume_m3':None,'status':audit.RESOLVED,'columns':[{'connected_depth_runs':[{'threshold_layer':{'lower_status':'adjacent_isotach_crossing'}}]}],'lateral_gate_censored':False}
    index={};audit.merge_source(index,row,'facts-a.json');return row,case,index


class CoverageAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('urllib.request.urlopen',side_effect=AssertionError('No retrieval in coverage audit')):cls.report,cls.raw=audit.build()

    def test_duplicate_source_mentions_count_once_and_keep_all_provenance(self):
        row,case,index=fixture();audit.merge_source(index,row,'facts-b.json')
        self.assertEqual(len(index),1);self.assertEqual(index[audit.key(row)]['facts_files'],{'facts-a.json','facts-b.json'})
        counts=audit.source_counts(index,index,{})
        self.assertEqual(counts['registered_source_cases'],1);self.assertEqual(counts['unprocessed_interior_cases'],1)

    def test_conflicting_hash_owner_threshold_and_status_cannot_be_coalesced(self):
        row,case,index=fixture()
        for name,value in [('source_sha256','b'*64),('entity_id','current:other'),('primary_threshold_m_s',.05),('horizontal_selection_status','unresolved')]:
            bad=copy.deepcopy(row);bad[name]=value
            with self.subTest(name=name),self.assertRaises(ValueError):audit.merge_source(index,bad,'facts-b.json')

    def test_curtain_requires_matching_owner_time_selection_threshold_and_hash(self):
        row,case,index=fixture()
        for name,value in [('source_sha256','b'*64),('entity_id','current:other'),('snapshot_time_utc','2022-07-15T00:00:00Z'),('original_selected_column_index',2),('velocity_threshold_m_s',.05),('physical_current_bottom_established',True)]:
            bad=copy.deepcopy(case);bad[name]=value
            with self.subTest(name=name),self.assertRaises(ValueError):audit.attach_curtain(index,{},bad,'curtains.json')

    def test_duplicate_curtains_count_once_and_conflicting_results_fail(self):
        row,case,index=fixture();derived={};audit.attach_curtain(index,derived,case,'a.json');audit.attach_curtain(index,derived,case,'b.json')
        self.assertEqual(len(derived),1);self.assertEqual(derived[audit.key(case)]['datasets'],{'a.json','b.json'});self.assertEqual(audit.source_counts(index,index,derived)['seed_connected_profile_date_columns'],1)
        bad=copy.deepcopy(case);bad['lateral_gate_censored']=True
        with self.assertRaises(ValueError):audit.attach_curtain(index,derived,bad,'c.json')

    def test_processed_unresolved_is_distinct_from_unprocessed_and_absence(self):
        row,case,index=fixture();row['horizontal_selection_status']='no_qualifying_interval_component_column';row['selected_column_index']=None;index={};audit.merge_source(index,row,'facts.json')
        before=audit.source_counts(index,index,{})
        self.assertEqual(before['unprocessed_unresolved_cases'],1);self.assertEqual(before['unprocessed_interior_cases'],0)
        case.update(status='ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN',original_horizontal_selection_status=row['horizontal_selection_status'],original_selected_column_index=None,columns=[]);derived={};audit.attach_curtain(index,derived,case,'curtains.json');after=audit.source_counts(index,index,derived)
        self.assertEqual(after['processed_unresolved_cases'],1);self.assertEqual(after['resolved_contours'],0);self.assertEqual(after['unprocessed_source_cases'],0)

    def test_reference_inventory_native_units_and_direct_identity_coverage(self):
        report=self.report;self.assertEqual(report['counts']['reference_identities'],111);self.assertEqual(report['counts']['reference_rows'],808);self.assertEqual(report['reference_unit_counts'],{'m':807,'dbar':1});self.assertEqual(report['counts']['reference_identities_with_direct_rows'],101)
        registered=[r for r in report['currents'] if r['in_reference_identity_register']]
        self.assertEqual(len(registered),111);self.assertEqual(sum(r['direct_reference_rows'] for r in report['currents']),808);self.assertEqual(sum(not r['direct_reference_rows'] for r in registered),10)
        for row in registered:
            if not row['direct_reference_rows']:self.assertIn('NO_DIRECT_REFERENCE_ROWS_DO_NOT_INHERIT_FROM_RELATED_IDENTITIES',row['next_actions'])

    def test_real_backlog_is_case_partition_not_false_completion(self):
        report=self.report;counts=report['registered_model_totals']
        self.assertEqual(counts['registered_source_cases'],counts['cases_with_contour_processing']+counts['unprocessed_source_cases']);self.assertEqual(counts['unprocessed_source_cases'],counts['unprocessed_interior_cases']+counts['unprocessed_unresolved_cases']);self.assertEqual(counts['cases_with_contour_processing'],counts['resolved_contours']+counts['processed_unresolved_cases']);self.assertGreater(counts['unprocessed_interior_cases'],0)
        self.assertEqual(sum(r['registered_model_sections']['registered_source_cases'] for r in report['currents']),counts['registered_source_cases'])
        self.assertEqual(sum(r['registered_model_sections']['resolved_contours'] for r in report['currents']),counts['resolved_contours'])

    def test_fitted_sensitivity_is_separate_from_model_cases_and_annual_ranges(self):
        self.assertEqual(self.report['counts']['fitted_profile_sensitivity_cases'],78);self.assertEqual(self.report['counts']['fitted_finite_sensitivity_cases'],77)
        rows={r['entity_id']:r for r in self.report['currents']};self.assertEqual(rows['current:gulf-stream']['fitted_profile_sensitivity_cases'],65);self.assertEqual(rows['current:florida']['fitted_profile_sensitivity_cases'],13)

    def test_no_physical_depth_volume_reference_or_runtime_promotion(self):
        for row in self.report['currents']:
            for name in ['whole_route_physical_depth_established','annual_depth_extrema_established','volume_estimate_established']:self.assertFalse(row[name])
        for name in ['whole_route_physical_depth_profiles','volume_estimates','new_ocean_field_requests','new_depth_references']:self.assertEqual(self.report['counts'][name],0)
        self.assertFalse(self.report['raw_ocean_field_data_reaudited']);self.assertFalse(self.report['runtime_changed']);self.assertFalse(self.report['full_goal_complete']);self.assertLess(len(self.raw),2400000)

    def test_backlog_ranking_is_explicit_and_all_scoped_inputs_are_listed(self):
        rows=self.report['source_cohort_backlog'];self.assertEqual(rows,sorted(rows,key=lambda r:(-r['unprocessed_interior_cases'],-r['unprocessed_source_cases'],r['facts_file'])))
        self.assertEqual(len(rows),self.report['counts']['registered_model_fact_files']);self.assertGreater(self.report['counts']['curtain_dataset_files'],0);self.assertIn('excluded_source_types',self.report['scope'])


if __name__=='__main__':unittest.main()
