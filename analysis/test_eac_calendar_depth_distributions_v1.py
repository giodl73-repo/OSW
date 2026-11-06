import copy,csv,io,math,socket,unittest
from unittest.mock import patch
import summarize_eac_calendar_depth_distributions_v1 as summary

def case(year,value=None,status=summary.RESOLVED):
    d={'status':status,'depth_m':value}
    if status==summary.RESOLVED:d['bracketing_native_depths_m']=[value-1,value+1]
    if status=='right_censored_at_native_domain_end':d['last_supported_depth_m']=1975
    return {'source_year':year,'source_date':str(year)+'-01-15','descriptor':d}

class EACCalendarDepthDistributions(unittest.TestCase):
    def test_complete_same_cohort_distribution_and_distinct_operators(self):
        years=list(range(2004,2020));cases=[case(y,100+10*i) for i,y in enumerate(years)]
        r=summary.summarize(cases,{'status':summary.RESOLVED,'depth_m':150},years)
        self.assertEqual(r['resolved_crossing_count'],16);self.assertEqual(r['resolved_subset_depth_min_max_m'],[100,250])
        self.assertEqual(r['resolved_subset_arithmetic_mean_depth_m'],175);self.assertEqual(r['resolved_subset_median_depth_m'],175)
        self.assertEqual(r['same_cohort_mean_of_crossing_depths_minus_crossing_of_mean_profile_m'],25)
        self.assertTrue(r['all_cohort_year_crossings_resolved']);self.assertFalse(r['resolved_subset_statistics_are_conditional'])

    def test_censor_limit_not_depth_and_no_complete_envelope_or_operator_comparison(self):
        cases=[case(2004,100),case(2005,None,'right_censored_at_native_domain_end')]
        r=summary.summarize(cases,{'status':summary.RESOLVED,'depth_m':150},[2004,2005])
        self.assertEqual(r['right_censored_count'],1);self.assertEqual(r['resolved_subset_depth_min_max_m'],[100,100])
        self.assertEqual(r['resolved_subset_arithmetic_mean_depth_m'],100);self.assertTrue(r['resolved_subset_statistics_are_conditional'])
        self.assertIsNone(r['complete_cohort_calendar_month_reconstructed_depth_range_m'])
        self.assertIsNone(r['same_cohort_mean_of_crossing_depths_minus_crossing_of_mean_profile_m'])
        self.assertEqual(r['unresolved_cases'][0]['descriptor']['last_supported_depth_m'],1975)

    def test_no_core_gap_and_threshold_not_exceeded_remain_distinct_unknowns(self):
        cases=[case(2004,None,'no_core'),case(2005,None,'unknown_gap_after_core'),case(2006,None,'threshold_not_exceeded')]
        r=summary.summarize(cases,{'status':'no_core','depth_m':None},[2004,2005,2006])
        self.assertEqual(r['gap_or_no_core_or_axis_unknown_count'],2);self.assertEqual(r['threshold_not_exceeded_count'],1)
        self.assertEqual(r['resolved_crossing_count'],0)
        for k in ['resolved_subset_depth_min_max_m','resolved_subset_arithmetic_mean_depth_m','resolved_subset_median_depth_m','complete_cohort_calendar_month_reconstructed_depth_range_m']:self.assertIsNone(r[k])

    def test_missing_duplicate_or_replaced_year_cohort_rejected(self):
        cases=[case(2004,100),case(2005,200)]
        for incoming in [cases[:1],cases+[cases[0]],[cases[0],case(2004,200)]]:
            with self.assertRaises(ValueError):summary.summarize(incoming,{'status':'no_core','depth_m':None},[2004,2005])

    def test_descriptor_validation_never_uses_retained_velocity_array(self):
        record={'status':'axis_within_EAC_gate','native_velocity_profile_m_s':object(),
          'derived':{'status':'derived_native_sampled_core','crossings':{'0.1':{'status':summary.RESOLVED,'depth_m':100,'bracketing_native_depths_m':[75,125]}}}}
        self.assertEqual(summary.descriptor(record,0.1)['depth_m'],100)
        for update in [{'depth_m':float('nan')},{'depth_m':1975.1},{'bracketing_native_depths_m':[110,125]},{'status':'unreviewed_status'}]:
            r=copy.deepcopy(record);r['derived']['crossings']['0.1'].update(update)
            with self.assertRaises(ValueError):summary.descriptor(r,0.1)
        r=copy.deepcopy(record);r['derived']['crossings']['0.1']={'status':'right_censored_at_native_domain_end','depth_m':1975,'last_supported_depth_m':1975}
        with self.assertRaises(ValueError):summary.descriptor(r,0.1)

    def test_nonlinear_depth_of_mean_not_substituted_for_mean_of_depths(self):
        # Two linear velocity profiles crossing zero at50m and80m; mean profile crosses at500/7m.
        a=50;b=80;mean_of_depths=(a+b)/2;depth_of_mean=500/7
        r=summary.summarize([case(2004,a),case(2005,b)],{'status':summary.RESOLVED,'depth_m':depth_of_mean},[2004,2005])
        self.assertEqual(r['resolved_subset_arithmetic_mean_depth_m'],mean_of_depths)
        self.assertAlmostEqual(r['same_cohort_mean_of_crossing_depths_minus_crossing_of_mean_profile_m'],mean_of_depths-depth_of_mean,places=6)
        self.assertNotEqual(r['resolved_subset_arithmetic_mean_depth_m'],r['original_mean_velocity_profile_crossing']['depth_m'])

    def test_actual192_descriptors36_summaries_status_reconciliation_and_source_immutability(self):
        raw=(summary.ROOT/summary.SOURCE).read_bytes();r=summary.build()
        self.assertEqual((summary.ROOT/summary.SOURCE).read_bytes(),raw)
        self.assertEqual(len(r['individual_cases']),576);self.assertEqual(len(r['calendar_month_summaries']),36)
        self.assertEqual(r['counts']['original_monthly_depth_descriptor_records'],192)
        self.assertEqual(sum(s['expected_monthly_estimates'] for s in r['calendar_month_summaries']),576)
        self.assertLessEqual(r['counts']['retained_typed_numeric_scalars'],50000)
        for s in r['calendar_month_summaries']:
            self.assertEqual(s['expected_years'],list(range(2004,2020)));self.assertEqual(sum(s['status_counts'].values()),16)
            if not s['all_cohort_year_crossings_resolved']:
                self.assertIsNone(s['complete_cohort_calendar_month_reconstructed_depth_range_m']);self.assertIsNone(s['same_cohort_mean_of_crossing_depths_minus_crossing_of_mean_profile_m'])
        self.assertEqual(r['counts']['new_native_profiles_selected'],0);self.assertEqual(r['counts']['new_reference_inventory_rows'],0)

    def test_actual_network_free_output_csv_nulls_and_physical_scope(self):
        def denied(*a,**k):raise RuntimeError('No provider/archive replay')
        with patch.object(socket,'socket',denied),patch.object(socket,'create_connection',denied):r=summary.build()
        rows=list(csv.DictReader(io.StringIO(summary.csv_bytes(r['calendar_month_summaries']).decode())))
        self.assertEqual(len(rows),36)
        for s in r['calendar_month_summaries']:
            for k in ['range_is_confidence_interval','range_is_instantaneous_annual_extrema','monthly_estimates_assumed_independent','physical_current_bottom_established','volume_eligible','physical_state_join_eligible','reference_route_projection_eligible','seasonal_playback_eligible']:self.assertFalse(s[k])
            for k in ['physical_depth_uncertainty_m','physical_thickness_m','annual_depth_range_m','whole_current_depth_m']:self.assertIsNone(s[k])

if __name__=='__main__':unittest.main()
