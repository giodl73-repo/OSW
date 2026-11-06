import copy,json,unittest,hashlib
import load_current_depth_reference_inventory_v33 as loader
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery,numeric_tokens
import compiled_depth_catalog_view_v1 as compiled
from load_current_depth_reference_inventory_v1 import reference_csv_bytes,counts_for

def fixture():
    profiles=[]
    for station in ['002','004','008']:
        cases=[{'threshold_m_s':t,'lower_depth_native_bracket_m':[100.,108.],'refined_bracket_indices':[12,13],
            'coarse_bracket_indices':[10,20],'lower_depth_m':104.,
            'status':'ADJACENT_NATIVE_CROSSING_WITHIN_FIRST_COARSE_DESCENDING_BRACKET',
            'first_native_downcrossing_below_core_verified':False,'continuous_connection_from_core_verified':False,
            'physical_current_bottom_established':False,'volume_eligible':False,
            'local_crossing_is_first_crossing_of_entire_native_profile':False} for t in [.05,.1,.2]]
        if station=='002':
            for c in cases:c.update(lower_depth_m=None,lower_depth_native_bracket_m=None,status='NO_QUALIFYING_FIXED_NATIVE_UV_FRAME')
        profiles.append({'station':station,'entity_context':'current:east-australian',
            'cast_datetime_utc':('2017-07-05' if station=='008' else '2017-07-04')+'T12:00:00Z',
            'source_processing_software':'LDEO LADCP software: Version IX_13beta','exact_solver_equivalence_verified':False,
            'independent_geographic_component_orientation_verified':False,'volume_eligible':False,
            'physical_state_join_eligible':False,'physical_thickness_m':None,'seasonal_range_m':None,
            'selected_native_levels':20,'current_membership_basis':'regional_EAC_candidate_not_independently_validated_current_axis',
            'source_file':'research/source-data/p06-eac-native-casts-v1/'+station+'.nc','source_sha256':'a'*64,
            'native_component_frame':{'qualified':station!='002','independent_geographic_direction_or_current_axis_verified':False,
                'native_uv_unit_vector':None if station=='002' else [1.,0.],'reference_native_index':11,'reference_depth_m':96.,
                'reference_native_u_m_s':1.,'reference_native_v_m_s':0.,'reference_speed_m_s':1.},
            'source_lon_lat':[153.,-30.],'source_processing_warnings':'preserved shallow warning' if station=='002' else '',
            'source_QC_status':'provider_processed_final_QC_not_verified',
            'source_timestamp_role':'provider_nominal_profile_date_not_per_depth_instant','threshold_cases':cases})
    return {'schema':'osw.p06-native-frame-depths.v2','profiles':profiles,'counts':{'source_cast_profiles':3},
        **{k:False for k in loader.FALSE_GATES}}

def addendum(source):
    return {'schema':loader.SCHEMA,'id':'p06-eac-native-uv-depths-v1',
        'evidence':loader.references(source),'source_contexts':{loader.CONTEXT:loader.context()}}

class P06Admission(unittest.TestCase):
    def test_six_resolved_references_three_unresolved_contexts(self):
        source=fixture();rows=loader.references(source);missing=loader.unresolved(source)
        self.assertEqual(len(rows),6);self.assertEqual(len(missing['contexts']),3)
        self.assertEqual(len({r['source_cast_profile_id'] for r in rows}),2)
        self.assertTrue(all(c['lower_depth_m'] is None and not c['canonical_reference_admitted'] for c in missing['contexts']))
        self.assertEqual(missing['source_processing_warnings'],'preserved shallow warning')

    def test_unresolved_cannot_silently_become_zero_or_estimate(self):
        for value in [0.,104.]:
            source=fixture();source['profiles'][0]['threshold_cases'][0]['lower_depth_m']=value
            with self.assertRaises(ValueError):loader.references(source)

    def test_preserve_native_metric_temporal_and_physical_caveats(self):
        for row in loader.references(fixture()):
            self.assertEqual(row['approximate_value_m'],100)
            self.assertEqual(row['source_computed_depth_before_display_rounding_m'],104.)
            self.assertIn('/2017_P06/',row['source_url'])
            self.assertIn('NBP1706',row['source_citation'])
            self.assertFalse(row['source_frame_is_mathematical_instant'])
            for k in ['volume_eligible','physical_state_join_eligible','physical_depth_ranking_eligible','direct_physical_current_depth_measurement']:
                self.assertFalse(row[k])
            for k in ['thickness_m','uncertainty_m','annual_range_m','depth_confidence_interval_m']:self.assertIsNone(row[k])

    def test_every_prior_reference_and_context_preserved(self):
        source=fixture();a=addendum(source)
        before={'records':[{'entity_id':'current:east-australian','depth_reference_ids':['old']}],
            'evidence':[{'id':'old','entity_id':'current:east-australian','metric':'old','unit':'m','notes':[None,False,3.]}],
            'source_contexts':{'old':{'notes':'same'}}}
        original=copy.deepcopy(before);after=loader.assemble(before,a,source)
        self.assertEqual(before,original);self.assertEqual(after['evidence'][:-6],original['evidence'])
        self.assertEqual(after['source_contexts']['old'],original['source_contexts']['old'])

    def test_missing_value_or_canonical_promotion_rejected(self):
        source=fixture();source['profiles'][1]['threshold_cases'][0]['lower_depth_m']=None
        with self.assertRaises(ValueError):loader.references(source)
        source=fixture();a=addendum(source);a['evidence'][0]['volume_eligible']=True
        with self.assertRaises(ValueError):loader.assemble({'records':[],'evidence':[],'source_contexts':{}},a,source)

class CompiledQuerySafety(unittest.TestCase):
    def test_prior_failed_query_reservations_are_carried(self):
        q=DescriptorQuery(lambda v:None)
        with q.decoding():json.loads('[7]')
        self.assertEqual(q.ledger['reserved_numeric_tokens'],23445)
        self.assertEqual(q.ledger['prior_failed_numeric_upper_bound'],23444)
        self.assertEqual(q.ledger['new_numeric_tokens'],1)
    def test_numeric_reservation_does_not_count_quoted_numbers(self):
        self.assertEqual(numeric_tokens(json.dumps({'12':'23','escaped':'q"45','v':[-.0012,7,True,None]}).encode()),2)

    def test_cached_values_are_isolated_and_not_decoded_again(self):
        snapshots=[];q=DescriptorQuery(lambda v:snapshots.append(copy.deepcopy(v)),prior_numeric=0,prior_bytes=0)
        original=json.loads
        with q.decoding():
            first=json.loads('{"a":[7]}');first['a'][0]=99
            self.assertEqual(json.loads('{"a":[7]}'),{'a':[7]})
        self.assertIs(json.loads,original)
        self.assertEqual(q.ledger['reserved_numeric_tokens'],1);self.assertEqual(q.ledger['cache_hits'],1)
        self.assertTrue(any(v['packets'] and v['packets'][0]['status']=='reserved_before_decode' for v in snapshots))

    def test_cap_rejects_before_numeric_decode_and_restores_decoder(self):
        q=DescriptorQuery(lambda v:None,numeric_cap=1,prior_numeric=0,prior_bytes=0);original=json.loads
        with self.assertRaises(ValueError):
            with q.decoding():json.loads('[1,2]')
        self.assertIs(json.loads,original);self.assertEqual(q.ledger['reserved_numeric_tokens'],0)

    def test_reader_cannot_open_native_or_archive_targets(self):
        q=DescriptorQuery(lambda v:None,prior_numeric=0,prior_bytes=0);read=q.reader(lambda p:b'{}')
        for path in ['native.nc','raw.zip','field.raw','research/source-data/retained-field.json']:
            with self.assertRaises(ValueError):read(path)
        self.assertEqual(read('compiled.json'),b'{}')

class AlreadyAdmittedDescriptorComposition(unittest.TestCase):
    def parts(self,bad_csv=False):
        encode=lambda v:json.dumps(v,separators=(',',':')).encode()
        files={}
        def part(path,raw):
            files[path]=raw;return {'file':path,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
        old={'id':'old','entity_id':'current:test','metric':'published','unit':'m'}
        new={'id':'new','entity_id':'current:test','metric':'published','unit':'m'}
        records=[{'entity_id':'current:test','depth_reference_ids':['old'],'status':'scoped_depth_reference'}]
        base={'records':records,'evidence':[old],'source_contexts':{},'counts':counts_for(records,[old])}
        bp={'json':part('base.json',encode(base)),'csv':part('base.csv',reference_csv_bytes([old]))}
        a={'schema':'already-validated-source-class','id':'redsox-published-plume-thickness-v1',
            'base_snapshot_sha256':bp['json']['sha256'],'evidence':[new],
            'source_contexts':{'published':{'source_report':{'file':'research/source-data/forbidden.json'}}},
            'derived_source_report':{'file':'never-reopened.nc'},'runtime_changed':False,'full_goal_complete':False}
        cp={'id':a['id'],'json':part('addendum.json',encode(a)),
            'csv':part('addendum.csv',reference_csv_bytes([{**new,'metric':'wrong'}] if bad_csv else [new]))}
        manifest={'schema':'osw.current-depth-reference-inventory.v28','base':bp,'addenda':[cp],
            'counts':counts_for(records,[old,new]),'metric_counts':{'published':2},'coordinate_unit_counts':{'m':2},
            'view_metadata':{'schema':'synthetic-compiled-view','runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}}
        return manifest,files

    def test_compose_only_pinned_canonical_pieces_without_following_source_fields(self):
        manifest,files=self.parts();reads=[]
        def reader(p):reads.append(p);return files[p]
        view=compiled.load_inventory(manifest,reader)
        self.assertEqual([r['id'] for r in view['evidence']],['old','new'])
        self.assertEqual(set(reads),set(files))
        self.assertEqual(view['records'][0]['depth_reference_ids'],['old','new'])

    def test_typed_compiled_csv_mismatch_rejected(self):
        manifest,files=self.parts(True)
        with self.assertRaises(ValueError):compiled.load_inventory(manifest,files.__getitem__)

if __name__=='__main__':unittest.main()
