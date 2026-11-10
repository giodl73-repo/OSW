import copy,csv,io,socket,unittest
from unittest.mock import patch
import summarize_kuroshio_calendar_depth_distributions_v1 as summary

def case(year,value=None,status=summary.RESOLVED):
    d={'status':status,'depth_m':value}
    if status==summary.RESOLVED:d['bracketing_native_depths_m']=[value-1,value+1]
    if status=='right_censored_at_native_domain_end':d['last_supported_depth_m']=1975
    return {'source_year':year,'source_date':str(year)+'-01-15','descriptor':d}

class KuroshioCalendarDistributions(unittest.TestCase):
    def test_kuroshio_gate_and_derived_depths_preserved_without_velocity_reprocessing(self):
        r={'status':'axis_within_KUROSHIO_gate','native_velocity_profile_m_s':object(),'derived':{'status':'derived_native_sampled_core','crossings':{'0.1':{'status':summary.RESOLVED,'depth_m':100,'bracketing_native_depths_m':[75,125]}}}}
        self.assertEqual(summary.descriptor(r,0.1)['depth_m'],100)
        for status in ['axis_within_EAC_gate','axis_within_KE_gate','unknown_axis_outside_EAC_gate']:
            changed=copy.deepcopy(r);changed['status']=status
            with self.assertRaises(ValueError):summary.descriptor(changed,0.1)
        changed=copy.deepcopy(r);changed['derived']['crossings']['0.1']['depth_m']=float('nan')
        with self.assertRaises(ValueError):summary.descriptor(changed,0.1)

    def test_shared_arithmetic_and_noncommuting_operator_rule(self):
        cases=[case(2004,100),case(2005,200)]
        r=summary.summarize(cases,{'status':summary.RESOLVED,'depth_m':155},[2004,2005])
        self.assertEqual(r['resolved_subset_arithmetic_mean_depth_m'],150);self.assertEqual(r['resolved_subset_median_depth_m'],150)
        self.assertEqual(r['resolved_subset_depth_min_max_m'],[100,200]);self.assertEqual(r['same_cohort_mean_of_crossing_depths_minus_crossing_of_mean_profile_m'],-5)

    def test_current_specific_unknown_axis_not_renamed_or_lost(self):
        cases=[case(2004,100),case(2005,None,'unknown_axis_outside_KUROSHIO_gate')]
        r=summary.summarize(cases,{'status':'no_core','depth_m':None},[2004,2005])
        self.assertEqual(r['gap_or_no_core_or_axis_unknown_count'],1)
        self.assertEqual(r['status_counts']['unknown_axis_outside_KUROSHIO_gate'],1)
        self.assertNotIn('unknown_axis_outside_EAC_gate',r['status_counts'])
        self.assertIsNone(r['complete_cohort_calendar_month_reconstructed_depth_range_m'])
        with self.assertRaises(ValueError):summary.summarize([case(2004,None,'unknown_axis_outside_EAC_gate')],{'status':'no_core','depth_m':None},[2004])

    def test_observation_era_is_explicit_year_context_not_direct_sample_proof(self):
        self.assertEqual(summary.source_era(2011),'BEFORE_LOCAL_PX40_HRXBT_OCCUPATIONS')
        self.assertEqual(summary.source_era(2012),'LOCAL_PX40_HRXBT_ERA_CONTEXT_NOT_PER_MONTH_OBSERVATION_PROOF')
        for year in [2003,2020,True]:
            with self.assertRaises(ValueError):summary.source_era(year)

    def test_censoring_incomplete_cohort_and_no_8year_mean_profile_substitution(self):
        r=summary.summarize([case(2004,100),case(2005,None,'right_censored_at_native_domain_end')],{'status':summary.RESOLVED,'depth_m':150},[2004,2005])
        self.assertEqual(r['right_censored_count'],1);self.assertIsNone(r['same_cohort_mean_of_crossing_depths_minus_crossing_of_mean_profile_m'])
        self.assertIsNone(r['complete_cohort_calendar_month_reconstructed_depth_range_m'])
        r=summary.summarize([case(2012+i,100+i) for i in range(8)],{'status':'cohort_specific_mean_velocity_profile_not_available','depth_m':None},list(range(2012,2020)))
        self.assertTrue(r['all_cohort_year_crossings_resolved']);self.assertIsNone(r['same_cohort_mean_of_crossing_depths_minus_crossing_of_mean_profile_m'])
        with self.assertRaises(ValueError):summary.summarize([case(2004,100),case(2004,200)],{'status':'no_core','depth_m':None},[2004,2005])

    def test_actual_full192_descriptor_cases_and_overlapping108_summary_cells(self):
        raw=(summary.ROOT/summary.SOURCE).read_bytes();r=summary.build()
        self.assertEqual((summary.ROOT/summary.SOURCE).read_bytes(),raw)
        self.assertEqual(len(r['individual_cases']),576);self.assertEqual(len(r['calendar_month_summaries']),108)
        self.assertEqual(r['counts']['full_period_month_threshold_summaries'],36);self.assertEqual(r['counts']['era_month_threshold_summaries'],72)
        self.assertEqual(r['counts']['before_local_HRXBT_threshold_cases'],288);self.assertEqual(r['counts']['later_HRXBT_era_threshold_cases'],288)
        self.assertTrue(r['era_summaries_overlap_full_period_summaries']);self.assertTrue(r['era_subcohorts_disjoint_with_each_other'])
        self.assertEqual(sum(s['expected_monthly_estimates'] for s in r['calendar_month_summaries']),1152)
        self.assertEqual(r['current_entity_id'],'current:kuroshio');self.assertEqual(r['positive_poleward_component'],'source_northward_positive_cross_transect_velocity')
        for c in r['individual_cases']:
            self.assertFalse(c['individual_month_is_direct_PX40_HRXBT_measurement_verified'])
            self.assertEqual(c['source_reconstruction_era'],summary.source_era(c['source_year']))

    def test_actual_era_comparators_use_only_matched_mean_profile_cohort(self):
        r=summary.build()
        for s in r['calendar_month_summaries']:
            self.assertEqual(sum(s['status_counts'].values()),s['expected_monthly_estimates'])
            if s['source_cohort_id']!='reconstructed2004_2019':
                self.assertEqual(s['expected_monthly_estimates'],8);self.assertIsNone(s['original_mean_profile_descriptor_pointer'])
                self.assertFalse(s['source_mean_velocity_profile_available_for_exact_cohort'])
                self.assertIsNone(s['same_cohort_mean_of_crossing_depths_minus_crossing_of_mean_profile_m'])
            else:self.assertEqual(s['expected_monthly_estimates'],16)
            if not s['all_cohort_year_crossings_resolved']:self.assertIsNone(s['complete_cohort_calendar_month_reconstructed_depth_range_m'])
            self.assertFalse(s['source_support_era_split_is_climate_or_significance_test'])

    def test_network_free_csv_era_labels_and_physical_scope(self):
        def denied(*a,**k):raise RuntimeError('No provider/archive replay')
        with patch.object(socket,'socket',denied),patch.object(socket,'create_connection',denied):r=summary.build()
        rows=list(csv.DictReader(io.StringIO(summary.csv_bytes(r['calendar_month_summaries']).decode())))
        self.assertEqual(len(rows),108);self.assertTrue(all(row['source_cohort_id'] for row in rows))
        self.assertEqual(r['counts']['new_native_profiles_selected'],0);self.assertEqual(r['counts']['provider_requests'],0);self.assertEqual(r['counts']['new_reference_inventory_rows'],0)
        self.assertLessEqual(r['counts']['retained_typed_numeric_scalars'],50000)
        for s in r['calendar_month_summaries']:
            for k in ['range_is_confidence_interval','range_is_instantaneous_annual_extrema','monthly_estimates_assumed_independent','physical_current_bottom_established','volume_eligible','physical_state_join_eligible','reference_route_projection_eligible','seasonal_playback_eligible']:self.assertFalse(s[k])
            for k in ['physical_depth_uncertainty_m','physical_thickness_m','annual_depth_range_m','whole_current_depth_m']:self.assertIsNone(s[k])

if __name__=='__main__':unittest.main()
