import copy,unittest
import load_current_depth_reference_inventory_v30 as loader

def fixture():
    profiles=[]
    for station in ['046','047','048']:
        cases=[{'threshold_m_s':t,'lower_depth_native_bracket_m':[100.,108.],'refined_bracket_indices':[12,13],
            'coarse_bracket_indices':[10,20],'lower_depth_m':104.,
            'status':'ADJACENT_NATIVE_CROSSING_WITHIN_FIRST_COARSE_DESCENDING_BRACKET',
            'first_native_downcrossing_below_core_verified':False,'continuous_connection_from_core_verified':False,
            'physical_current_bottom_established':False,'volume_eligible':False,
            'local_crossing_is_first_crossing_of_entire_native_profile':False} for t in [.05,.1,.2]]
        profiles.append({'station':station,'entity_context':'current:agulhas','cast_datetime_utc':'2019-05-09T12:00:00Z',
            'source_processing_software':'LDEO LADCP software: Version IX_14beta2','exact_solver_equivalence_verified':False,
            'independent_geographic_component_orientation_verified':False,'volume_eligible':False,
            'physical_state_join_eligible':False,'physical_thickness_m':None,'seasonal_range_m':None,
            'selected_native_levels':20,'current_membership_basis':'regional_Agulhas_candidate_not_independently_validated_current_axis',
            'source_file':'research/source-data/i06s-agulhas-native-casts-v1/'+station+'.nc','source_sha256':'a'*64,
            'native_component_frame':{'qualified':True,'independent_geographic_direction_or_current_axis_verified':False,
                'native_uv_unit_vector':[1.,0.],'reference_native_index':11,'reference_depth_m':96.,
                'reference_native_u_m_s':1.,'reference_native_v_m_s':0.,'reference_speed_m_s':1.},
            'source_lon_lat':[28.,-33.],'source_processing_warnings':'retained synthetic tilt warning' if station=='047' else '',
            'source_QC_status':'provider_processed_final_QC_not_verified',
            'source_timestamp_role':'provider_nominal_profile_date_not_per_depth_instant','threshold_cases':cases})
    return {'schema':'osw.i06s-native-frame-depths.v2','profiles':profiles,'counts':{'source_cast_profiles':3},
        **{k:False for k in loader.FALSE_GATES}}

def addendum(source):
    return {'schema':loader.SCHEMA,'id':'i06s-agulhas-native-uv-depths-v1',
        'evidence':loader.references(source),'source_contexts':{loader.CONTEXT:loader.context()}}

class ConditionalAdmissionChecks(unittest.TestCase):
    def test_three_casts_nine_thresholds_not_independent_observation_claim(self):
        rows=loader.references(fixture())
        self.assertEqual(len(rows),9);self.assertEqual(len({r['source_cast_profile_id'] for r in rows}),3)
        self.assertTrue(all(not r['independent_observation_count_claimed'] for r in rows))

    def test_no_physical_or_uncertainty_promotion(self):
        for row in loader.references(fixture()):
            self.assertEqual(row['approximate_value_m'],100)
            self.assertEqual(row['source_computed_depth_before_display_rounding_m'],104)
            for k in ['annual_range_m','uncertainty_m','thickness_m','upper_boundary_m','lower_boundary_m','depth_confidence_interval_m']:
                self.assertIsNone(row[k])
            for k in ['volume_eligible','physical_state_join_eligible','physical_depth_ranking_eligible','direct_physical_current_depth_measurement','source_bracket_is_uncertainty_interval']:
                self.assertFalse(row[k])

    def test_warnings_beta_native_basis_and_cast_time_preserved(self):
        rows=loader.references(fixture())
        self.assertEqual(rows[3]['source_processing_warnings'],'retained synthetic tilt warning')
        self.assertEqual(rows[3]['metric'],loader.METRIC)
        self.assertFalse(rows[3]['source_frame_is_mathematical_instant'])
        self.assertTrue(rows[3]['metric_frame_is_cast_specific_not_climatology'])
        self.assertIn('IX_14beta2',rows[3]['source_processing_software'])
        self.assertNotIn('east_north_unit_vector',rows[3]['source_fixed_native_uv_frame'])

    def test_missing_value_or_nonadjacent_bracket_rejected(self):
        for field,value in [('lower_depth_m',None),('refined_bracket_indices',[12,14])]:
            source=fixture();source['profiles'][0]['threshold_cases'][0][field]=value
            with self.assertRaises(ValueError):loader.references(source)

    def test_canonical_tampering_or_warning_loss_rejected(self):
        source=fixture();a=addendum(source);a['evidence'][3]['source_processing_warnings']=''
        before={'records':[{'entity_id':'current:agulhas'}],'evidence':[],'source_contexts':{}}
        with self.assertRaises(ValueError):loader.assemble(before,a,source)
        source=fixture();source['exact_solver_equivalence_verified']=True
        with self.assertRaises(ValueError):loader.references(source)

    def test_all_prior_evidence_contexts_and_references_retained(self):
        source=fixture();a=addendum(source)
        before={'records':[{'entity_id':'current:agulhas','depth_reference_ids':['old']}],
            'evidence':[{'id':'old','entity_id':'current:agulhas','metric':'old_metric','unit':'m','note':[None,False,3.]}],
            'source_contexts':{'old_context':{'note':'unchanged'}}}
        old=copy.deepcopy(before);after=loader.assemble(before,a,source)
        self.assertEqual(before,old);self.assertEqual(after['evidence'][:-9],old['evidence'])
        self.assertEqual(after['source_contexts']['old_context'],old['source_contexts']['old_context'])
        self.assertEqual(after['counts']['depth_references'],10)
        self.assertEqual(after['records'][0]['depth_reference_ids'][0],'old')

    def test_repeated_context_or_cutoff_does_not_admit(self):
        source=fixture();source['profiles'][0]['threshold_cases'][1]['threshold_m_s']=.05
        with self.assertRaises(ValueError):loader.references(source)
        source=fixture();a=addendum(source)
        before={'records':[{'entity_id':'current:agulhas'}],'evidence':[],'source_contexts':{loader.CONTEXT:{}}}
        with self.assertRaises(ValueError):loader.assemble(before,a,source)

if __name__=='__main__':unittest.main()
