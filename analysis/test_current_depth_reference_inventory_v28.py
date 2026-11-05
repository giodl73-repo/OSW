import copy,csv,io,unittest
import load_current_depth_reference_inventory_v28 as loader


def fixture():
    rows=[]
    for i,station in enumerate(['014','015','016']):
        for j,t in enumerate([.05,.1,.2]):
            rows.append({'entity_id':'current:gulf-stream','station':station,'threshold_m_s':t,'computed_depth_m':104.,
                'native_depth_bracket_m':[100.,108.],'refined_native_indices':[12,13],'original_coarse_bracket_indices':[10,20],
                'fixed_reference_frame':{'qualified':True,'reference_native_index':11,'reference_depth_m':96.,
                    'reference_eastward_u_m_s':1.,'reference_northward_v_m_s':0.,'reference_speed_m_s':1.,
                    'east_north_unit_vector':[1.,0.],'reference_direction_is_independently_validated_current_axis':False},
                'cast_datetime_utc':'2021-03-'+('23' if station in ['014','015'] else '24')+'T12:00:00',
                'source_lon_lat':[-52.,41.],'raw_native_file':'research/source-data/a20-gulf-stream-native-casts-v1/'+station+'.nc',
                'raw_native_sha256':'a'*64,'source_case_pointer':'/profiles/'+str(i)+'/threshold_cases/'+str(j),
                'current_membership_basis':'primary_cruise_QC_stations14_to21_candidate_not_independent_axis_validation'})
    return {'schema':'osw.a20-local-component-depth-reference-facts.v1','source_file':loader.SOURCE,'source_sha256':loader.SOURCE_SHA,
        'metric':loader.METRIC,'source_cast_profiles':3,'records':rows,'source_uncertainty_semantics':'provider_velocity_uncertainty_estimate_not_SE_or_depth_CI',
        'independent_observation_count_claimed':False,**{k:False for k in loader.FALSE_GATES}}


class LocalNativeProxyCatalogChecks(unittest.TestCase):
    def facts(self):return fixture()
    def addendum(self):
        f=self.facts();piece={'file':loader.FACTS,'sha256':'a'*64,'bytes':0}
        return f,{'reviewed_source_facts':piece,'source_contexts':{loader.CONTEXT:f},'evidence':loader.references(f,piece)}

    def test_three_casts_nine_definitions_are_not_independent_observations(self):
        f,a=self.addendum();loader.validate_addendum(a,f)
        self.assertEqual(len(a['evidence']),9)
        self.assertEqual(len({r['source_cast_profile_id'] for r in a['evidence']}),3)
        self.assertTrue(all(not r['independent_observation_count_claimed'] for r in a['evidence']))

    def test_brackets_are_not_error_or_physical_depth_intervals(self):
        f,a=self.addendum()
        for r in a['evidence']:
            self.assertEqual(r['approximate_value_m'],100)
            self.assertEqual(r['source_computed_depth_before_display_rounding_m'],104)
            for k in ['uncertainty_m','annual_range_m','thickness_m','lower_boundary_m','upper_boundary_m','depth_confidence_interval_m']:
                self.assertIsNone(r[k])
            for k in ['physical_current_bottom_established','physical_depth_ranking_eligible','volume_eligible','physical_state_join_eligible',
                      'reference_route_projection_eligible','global_first_native_crossing_verified','continuous_core_connection_verified']:
                self.assertFalse(r[k])

    def test_local_proxy_cannot_silently_be_promoted(self):
        f,a=self.addendum()
        for k,v in [('metric','velocity_layer_lower_boundary_depth'),('volume_eligible',True),('thickness_m',104),
                    ('global_first_native_crossing_verified',True),('source_bracket_is_uncertainty_interval',True)]:
            b=copy.deepcopy(a);b['evidence'][0][k]=v
            with self.assertRaises(ValueError):loader.validate_addendum(b,f)
        f['continuous_core_connection_verified']=True
        with self.assertRaises(ValueError):loader.validate_facts(f)

    def test_source_owner_date_cutoff_and_provenance_are_fixed(self):
        for k,v in [('entity_id','current:florida'),('station','017'),('threshold_m_s',.07),
                    ('cast_datetime_utc','2022-03-23T12:00:00'),('source_case_pointer','/profiles/2/threshold_cases/2'),
                    ('raw_native_file','other.nc')]:
            f=self.facts();f['records'][0][k]=v
            with self.assertRaises(ValueError):loader.validate_facts(f)
        f=self.facts();f['source_sha256']='b'*64
        with self.assertRaises(ValueError):loader.validate_facts(f)

    def test_nonadjacent_or_outside_bracket_depth_and_duplicate_cases_rejected(self):
        for k,v in [('computed_depth_m',200),('refined_native_indices',[12,14]),('original_coarse_bracket_indices',[15,20])]:
            f=self.facts();f['records'][0][k]=v
            with self.assertRaises(ValueError):loader.validate_facts(f)
        f=self.facts();f['records'][1]=copy.deepcopy(f['records'][0])
        with self.assertRaises(ValueError):loader.validate_facts(f)

    def test_actual_reference_direction_cannot_become_climatological_axis(self):
        for k,v in [('reference_depth_m',100),('reference_direction_is_independently_validated_current_axis',True),('qualified',False)]:
            f=self.facts();f['records'][0]['fixed_reference_frame'][k]=v
            with self.assertRaises(ValueError):loader.validate_facts(f)
        f,a=self.addendum()
        self.assertTrue(all(r['metric_frame_is_instantaneous_sample_not_climatology'] for r in a['evidence']))
        self.assertTrue(all(not r['fitted_mean_direction_metric_equivalent'] for r in a['evidence']))

    def test_typed_csv_preserves_nested_frames_and_nulls(self):
        f,a=self.addendum();raw=loader.reference_csv_bytes(a['evidence'])
        incoming=csv.DictReader(io.StringIO(raw.decode()));rows=list(incoming);fields=incoming.fieldnames
        self.assertEqual(len(rows),9)
        self.assertEqual(rows,[{k:loader.base.cell(r.get(k)) for k in fields} for r in a['evidence']])


if __name__=='__main__':unittest.main()
