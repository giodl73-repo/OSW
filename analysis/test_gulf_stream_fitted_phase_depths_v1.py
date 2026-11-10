import copy,csv,io,json,socket,unittest
from unittest.mock import patch
import summarize_gulf_stream_fitted_phase_depths_v1 as summary

def row(month,value,kind='annual_cycle'):
    m=month or 0
    return {'case_id':'coastal-30n:'+kind+':'+str(month),'section_id':'coastal-30n','source_product_kind':kind,'calendar_month_phase':month,
      'nominal_half_core_lower_depth_m':value,'conditional_one_reported_SE_depth_response_m':None,
      'source_lon_lat':[-80+0.01*m,30],'fixed_nominal_cutoff_m_s':1+0.01*m,'locked_reference_direction_at100m_degrees':20+m}

def matrix():return [row(None,999,'mean')]+[row(m,90+10*m) for m in range(1,13)]

class GulfStreamFittedPhaseSummary(unittest.TestCase):
    def test_mean_fit_excluded_from_complete_twelve_sampled_phase_span(self):
        r=summary.summarize_section(matrix(),{'id':'coastal-30n'})
        self.assertEqual(r['complete_twelve_sampled_phase_nominal_depth_span_m'],[100,210])
        self.assertEqual(r['mean_fit_case']['nominal_half_core_lower_depth_m'],999)
        self.assertEqual(r['phase_months_at_sampled_min_depth'],[1]);self.assertEqual(r['phase_months_at_sampled_max_depth'],[12])
        self.assertFalse(r['mean_fit_is_a_thirteenth_seasonal_phase']);self.assertFalse(r['mean_of_phase_depths_compared_to_mean_fit'])

    def test_missing_phase_depth_suppresses_complete_range_not_replaced_by_mean_or_limit(self):
        rows=matrix();rows[1]['nominal_half_core_lower_depth_m']=None
        r=summary.summarize_section(rows,{'id':'coastal-30n'})
        self.assertEqual(r['resolved_nominal_phase_depths'],11);self.assertEqual(r['unresolved_nominal_phase_months'],[1])
        self.assertIsNone(r['complete_twelve_sampled_phase_nominal_depth_span_m'])
        self.assertEqual(r['resolved_phase_subset_nominal_depth_span_m'],[110,210]);self.assertTrue(r['phase_subset_span_is_conditional'])

    def test_missing_duplicate_phase_and_section_mixture_rejected(self):
        rows=matrix()
        for bad in [rows[:-1],rows[:-1]+[copy.deepcopy(rows[1])],rows[1:]+[copy.deepcopy(rows[1])]]:
            with self.assertRaises(ValueError):summary.summarize_section(bad,{'id':'coastal-30n'})
        with self.assertRaises(ValueError):summary.summarize_section(rows,{'id':'offshore-70w'})

    def test_phase_positions_cutoffs_and_directions_not_silently_locked_together(self):
        r=summary.summarize_section(matrix(),{'id':'coastal-30n'})
        self.assertTrue(r['phase_selected_source_positions_vary']);self.assertTrue(r['phase_nominal_cutoffs_vary']);self.assertTrue(r['phase_locked_100m_directions_vary'])
        self.assertFalse(r['cross_current_fixed_cutoff_depth_ranking_eligible'])
        self.assertFalse(r['sampled_phase_span_is_continuous_annual_fit_extrema']);self.assertFalse(r['sampled_phase_span_is_observed_annual_extrema'])
        self.assertFalse(r['sampled_phase_span_is_measurement_error_or_confidence_interval'])
        rows=matrix()
        for c in rows:c['locked_reference_direction_at100m_degrees']=-5 if c['calendar_month_phase'] in [1,3,5,7,9,11] else 355
        self.assertFalse(summary.summarize_section(rows,{'id':'coastal-30n'})['phase_locked_100m_directions_vary'])

    def test_actual_scalar_reader_rejects_metric_identity_timestamp_and_confidence_promotions(self):
        source=json.loads((summary.ROOT/summary.SOURCE).read_bytes());original=source['cases'][0]
        for target,key,value in [('root','entity_id','current:florida'),('root','timestamp_is_instantaneous_observation_date',True),('descriptor','relative_sampled_core_fraction',0.4),('descriptor','quantity_role','absolute10cm_per_second_depth'),('descriptor','threshold_m_s',0.1),('sensitivity','confidence_interval_established',True)]:
            bad=copy.deepcopy(original);where=bad if target=='root' else bad['nominal_source_half_core_descriptor' if target=='descriptor' else 'sensitivity'];where[key]=value
            with self.assertRaises(ValueError):summary.thin_case(bad,0)
        # The scalar reader must never use stored native grids/scenario velocity vectors.
        metadata=copy.deepcopy(original);metadata['depth_levels_m']=object();metadata['sensitivity']['lower_velocity_scenario_m_s']=object()
        self.assertEqual(summary.thin_case(metadata,0),summary.thin_case(original,0))

    def test_actual65_cases_five_sections_and_source_bytes_preserved(self):
        raw=(summary.ROOT/summary.SOURCE).read_bytes();r=summary.build()
        self.assertEqual((summary.ROOT/summary.SOURCE).read_bytes(),raw)
        self.assertEqual(len(r['cases']),65);self.assertEqual(len(r['section_summaries']),5)
        self.assertEqual(r['counts']['mean_fit_cases'],5);self.assertEqual(r['counts']['fitted_day15_phase_cases'],60)
        self.assertEqual(r['counts']['resolved_nominal_half_core_depths'],65);self.assertEqual(r['counts']['conditional_fit_error_responses_retained'],65)
        self.assertEqual(r['counts']['complete_twelve_sampled_phase_spans'],5)
        self.assertLessEqual(r['counts']['retained_typed_numeric_scalars'],50000)
        self.assertEqual(r['documented_fit_observation_period'],['2015-07-16','2023-05-30'])

    def test_phase_section_matrix_references_exact_cases_without_route_distance_claim(self):
        r=summary.build();ids={c['case_id']:c for c in r['cases']}
        self.assertEqual(len(r['sampled_phase_section_matrix']),12)
        for phase in r['sampled_phase_section_matrix']:
            self.assertEqual(len(phase['section_cases']),5);self.assertFalse(phase['section_order_is_physical_along_route_distance'])
            for item in phase['section_cases']:
                c=ids[item['case_id']];self.assertEqual(c['section_id'],item['section_id']);self.assertEqual(c['calendar_month_phase'],phase['calendar_month_phase'])
                self.assertEqual(c['source_product_kind'],'annual_cycle')

    def test_network_disabled_csv_and_separate_error_variation_physical_scopes(self):
        def denied(*a,**k):raise RuntimeError('Provider/source replay prohibited')
        with patch.object(socket,'socket',denied),patch.object(socket,'create_connection',denied):r=summary.build()
        table=list(csv.DictReader(io.StringIO(summary.csv_bytes(r['cases']).decode())));self.assertEqual(len(table),65)
        self.assertEqual(r['counts']['new_native_profiles_selected'],0);self.assertEqual(r['counts']['new_reference_inventory_rows'],0);self.assertEqual(r['counts']['provider_requests'],0)
        for c in r['cases']:
            self.assertFalse(c['timestamp_is_instantaneous_observation_date']);self.assertFalse(c['source_date_is_independent_observation'])
            for k in ['physical_current_bottom_established','confidence_interval_established','volume_eligible','physical_state_join_eligible','reference_route_projection_eligible','seasonal_playback_eligible']:self.assertFalse(c[k])
        for s in r['section_summaries']:
            for k in ['physical_depth_uncertainty_m','physical_thickness_m','annual_depth_range_m']:self.assertIsNone(s[k])
            self.assertFalse(s['full_reference_route_depth_profile_established'])

if __name__=='__main__':unittest.main()
