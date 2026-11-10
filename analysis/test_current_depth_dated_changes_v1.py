import copy,json,unittest
from derive_current_depth_dated_changes_v1 import build,summarize_series,verify_point,FINITE,METRICS

def point(name='a',date='2022-01-15T00:00:00Z',xy=None,**changes):
    row={'id':name,'record_type':'regional_depth_estimate','dataset_id':'dataset','entity_id':'current:a','section_id':'section',
        'snapshot_time_utc':date,'estimate_status':FINITE,'sampled_lon_lat':[10,-20] if xy is None else xy,
        'component_bearing_degrees_true':90,'velocity_threshold_m_s':.1,'source_rule_operator_file':'research/scope.json',
        'upper_depth_m':20,'lower_depth_m':100,'thickness_m':80,'sampling_thickness_bounds_m':[60,100],
        'native_supported_minimum_component_span_m':60,'source_status':'source_diagnostic',
        'original_csv':'research/source.csv','original_csv_sha256':'csv-hash','original_csv_data_row_index':0,
        'source_compiled_descriptor_file':'research/compiled.json','source_compiled_descriptor_sha256':'compiled-hash','source_descriptor_pointer':'/cases/0',
        'physical_current_depth_m':None,'whole_route_interpolation_allowed':False,'independent_current_axis_validated':False,'volume_km3':None}
    row.update(changes);return row

def series(rows):return summarize_series(rows,{r['id']:i for i,r in enumerate(rows)})

class DatedDepthTests(unittest.TestCase):
    def test_exact_signed_fixed_grid_change_and_original_values(self):
        a=point();b=point('b','2022-07-15T00:00:00Z',upper_depth_m=10,lower_depth_m=130,thickness_m=120,sampling_thickness_bounds_m=[100,140]);before=copy.deepcopy([a,b]);r=series([b,a]);c=r['adjacent_declared_date_comparisons'][0]
        self.assertEqual(c['selected_profile_depth_change_m'],{'upper_depth_m':-10,'lower_depth_m':30,'thickness_m':40});self.assertEqual(c['fixed_grid_depth_change_m'],c['selected_profile_depth_change_m']);self.assertEqual(c['elapsed_days'],181)
        self.assertEqual(r['finite_pair_dated_sample_ranges_m']['thickness_m'],[80,120]);self.assertEqual(r['smallest_enclosing_finite_pair_sampling_thickness_bracket_m'],[60,140]);self.assertEqual([a,b],before)
    def test_moved_selection_cannot_claim_fixed_grid_change(self):
        r=series([point(),point('b','2022-07-15T00:00:00Z',xy=[10,-20.08])]);c=r['adjacent_declared_date_comparisons'][0]
        self.assertEqual(c['status'],'selected_profile_changed_location_finite_diagnostic_change');self.assertFalse(c['sampled_location_unchanged']);self.assertIsNone(c['fixed_grid_depth_change_m']);self.assertFalse(r['finite_pair_ranges_use_one_native_grid_location'])
    def test_censored_case_is_not_finite_minimum_or_zero(self):
        c=point('c','2022-07-15T00:00:00Z',estimate_status='censored_component_depth_pair',lower_depth_m=None,thickness_m=None,sampling_thickness_bounds_m=None,native_supported_minimum_component_span_m=475)
        r=series([point(),c]);self.assertEqual(r['finite_pair_dated_sample_count'],1);self.assertIsNone(r['finite_pair_dated_sample_ranges_m']['thickness_m']);self.assertEqual(r['points'][1]['native_supported_minimum_component_span_m'],475);self.assertIsNone(r['points'][1]['lower_depth_m']);self.assertIsNone(r['adjacent_declared_date_comparisons'][0]['selected_profile_depth_change_m']['thickness_m'])
    def test_no_comparison_bridges_a_retained_gap(self):
        gap=point('gap','2022-06-15T00:00:00Z',estimate_status='unresolved_original_axis',upper_depth_m=None,lower_depth_m=None,thickness_m=None,sampling_thickness_bounds_m=None,native_supported_minimum_component_span_m=None);gap['sampled_lon_lat']=None
        r=series([point(),gap,point('c','2022-09-15T00:00:00Z')]);self.assertEqual(len(r['points']),3);self.assertEqual(len(r['adjacent_declared_date_comparisons']),2)
        self.assertTrue(all(c['status']=='not_comparable_unresolved_or_censored' for c in r['adjacent_declared_date_comparisons']));self.assertIsNone(r['points'][1]['sampled_lon_lat'])
    def test_frame_threshold_owner_operator_cohort_and_section_separate(self):
        for change in [{'component_bearing_degrees_true':180},{'velocity_threshold_m_s':.05},{'entity_id':'current:b'},{'source_rule_operator_file':'research/other.json'},{'dataset_id':'other'},{'section_id':'other'}]:
            with self.subTest(change=change),self.assertRaises(ValueError):series([point(),point('b','2022-07-15T00:00:00Z',**change)])
    def test_duplicate_time_and_non_utc_timestamp_rejected(self):
        with self.assertRaises(ValueError):series([point(),point('b')])
        for date in ['2022-07-15T00:00:00','2022-07-15T00:00:00+01:00']:
            with self.subTest(date=date),self.assertRaises(ValueError):series([point(date=date)])
    def test_censor_or_gap_cannot_be_promoted_to_finite_thickness(self):
        for state in ['censored_component_depth_pair','unresolved_original_axis']:
            with self.subTest(state=state),self.assertRaises(ValueError):verify_point(point(estimate_status=state))
    def test_physical_or_interpolation_promotion_invalid(self):
        for change in [{'physical_current_depth_m':100},{'whole_route_interpolation_allowed':True},{'independent_current_axis_validated':True},{'volume_km3':5}]:
            with self.subTest(change=change),self.assertRaises(ValueError):verify_point(point(**change))
    def test_invalid_pair_or_sampling_bracket_invalid(self):
        for change in [{'lower_depth_m':110},{'thickness_m':float('nan')},{'upper_depth_m':-1},{'sampling_thickness_bounds_m':[90,100]},{'sampled_lon_lat':[400,10]}]:
            with self.subTest(change=change),self.assertRaises(ValueError):verify_point(point(**change))
    def test_single_sample_and_two_equal_samples_have_distinct_ranges(self):
        self.assertTrue(all(v is None for v in series([point()])['finite_pair_dated_sample_ranges_m'].values()))
        r=series([point(),point('b','2022-07-15T00:00:00Z')]);self.assertEqual(r['finite_pair_dated_sample_ranges_m']['thickness_m'],[80,80]);self.assertFalse(r['annual_extrema_established']);self.assertIsNone(r['physical_annual_depth_range_m'])
    def test_complete_identity_case_accounting_and_roundtrip(self):
        source={'schema':'osw.current-depth-almanac.expanded.v1','runtime_changed':False,'full_goal_complete':False,'counts':{'regional_estimates':2},'entries':[
            {'record_type':'current','entity_id':'current:a','name':'A','identity_level':'current'},
            {'record_type':'current','entity_id':'current:family','name':'Family','identity_level':'family'},point(),point('b','2022-07-15T00:00:00Z')]}
        before=copy.deepcopy(source);r=build(source);self.assertEqual(r['counts']['source_regional_cases'],2);self.assertEqual(r['counts']['canonical_identities'],2);self.assertEqual(r['current_index'][1]['series_ids'],[]);self.assertEqual(r['series'][0]['points'][0]['source_expanded_entry_index'],2);self.assertEqual(source,before);self.assertEqual(json.loads(json.dumps(r)),r)
        source['entries'][-1]['id']='a'
        with self.assertRaises(ValueError):build(source)
    def test_source_cannot_promote_runtime_or_add_unknown_owner(self):
        source={'schema':'osw.current-depth-almanac.expanded.v1','runtime_changed':False,'full_goal_complete':False,'counts':{},'entries':[point()]}
        with self.assertRaises(ValueError):build(source)
        source['runtime_changed']=True
        with self.assertRaises(ValueError):build(source)

if __name__=='__main__':unittest.main()
