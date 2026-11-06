import copy,json,unittest
from build_current_depth_almanac_v1 import CSVQuery,normalize,assemble,compact_report,expand_report,table
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery

class AlmanacTests(unittest.TestCase):
    def setUp(self):
        self.q=DescriptorQuery(lambda v:None,prior_numeric=0,prior_bytes=0);self.adapter=CSVQuery(self.q)
        self.d={'id':'example','scope_operators':['research/scope.json'],'csv':'research/admitted.csv','csv_sha256':'csvhash','fallback_compiled_descriptor_file':'research/compiled.json','fallback_compiled_descriptor_sha256':'sourcehash'}
        self.scopes={'research/scope.json':{'snapshot_times_utc':['2022-01-15T00:00:00Z'],'currents':{'current:a':{'entity_id':'current:a','component_bearing_degrees_true':90,'primary_threshold_m_s':.1,'branch_scope':'Local only; membership not validated.'}}}}
        self.pairing={'input_sha256':{'research/compiled.json':'sourcehash'}}
        self.anchor={'sampled_lon_lat':[12,-10],'physical_current_depth_m':None,'whole_route_interpolation_allowed':False,'independent_current_axis_validated':False,
            'paired_component_run':{'upper_depth_m':20,'lower_depth_m':100,'thickness_m':80,'sampling_thickness_bounds_m':[60,100],'upper_status':'adjacent_isotach_crossing','lower_status':'adjacent_isotach_crossing'}}
        self.row={'entity_id':'current:a','section_id':'section-a','snapshot_time_utc':'2022-01-15T00:00:00Z','status':'original_status','source_descriptor_pointer':'/cases/0','original_axis_proxy_depth_anchor':json.dumps(self.anchor)}
    def runrow(self,row=None):return normalize(self.row if row is None else row,self.d,0,self.scopes,self.pairing,self.adapter)
    def test_finite_pair_and_original_scope_are_preserved(self):
        before=copy.deepcopy(self.row);r=self.runrow()
        self.assertEqual(r['thickness_m'],80);self.assertEqual(r['sampling_thickness_bounds_m'],[60,100]);self.assertEqual(r['original_axis_proxy_depth_anchor'],self.anchor)
        self.assertEqual(r['estimate_status'],'finite_component_depth_pair');self.assertEqual(self.row,before);self.assertIsNone(r['volume_km3']);self.assertFalse(r['independent_current_axis_validated'])
    def test_censor_keeps_unknown_bottom_and_support_separate(self):
        self.anchor['paired_component_run'].update(lower_depth_m=None,thickness_m=None,sampling_thickness_bounds_m=None,native_supported_minimum_component_span_m=400,lower_status='sampled_domain_limit')
        self.row['original_axis_proxy_depth_anchor']=json.dumps(self.anchor);r=self.runrow()
        self.assertEqual(r['estimate_status'],'censored_component_depth_pair');self.assertIsNone(r['lower_depth_m']);self.assertIsNone(r['thickness_m']);self.assertEqual(r['native_supported_minimum_component_span_m'],400)
    def test_gap_is_null_not_zero(self):
        self.row['original_axis_proxy_depth_anchor']='null';r=self.runrow()
        self.assertEqual(r['estimate_status'],'unresolved_original_axis');self.assertIsNone(r['sampled_lon_lat']);self.assertIsNone(r['upper_depth_m'])
    def test_mismatched_frame_date_and_provenance_rejected(self):
        for change in [{'component_bearing_degrees_true':'180'},{'velocity_threshold_m_s':'0.05'},{'snapshot_time_utc':'2022-07-15T00:00:00Z'},{'source_compiled_descriptor_sha256':'changed'},{'source_descriptor_pointer':'/invented/0'}]:
            with self.subTest(change=change),self.assertRaises(ValueError):self.runrow(dict(self.row,**change))
    def test_invalid_pairs_and_physical_promotion_rejected(self):
        for change in [{'thickness_m':90},{'sampling_thickness_bounds_m':[90,100]},{'upper_depth_m':-1},{'lower_depth_m':None}]:
            a=copy.deepcopy(self.anchor);a['paired_component_run'].update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):self.runrow(dict(self.row,original_axis_proxy_depth_anchor=json.dumps(a)))
        a=copy.deepcopy(self.anchor);a['whole_route_interpolation_allowed']=True
        with self.assertRaises(ValueError):self.runrow(dict(self.row,original_axis_proxy_depth_anchor=json.dumps(a)))
    def test_root_operator_binding_and_ambiguous_owner_rejection(self):
        m=self.scopes['research/scope.json'];m.update(m.pop('currents')['current:a']);self.assertEqual(self.runrow()['velocity_threshold_m_s'],.1)
        self.scopes['research/other.json']=copy.deepcopy(m);self.d['scope_operators'].append('research/other.json')
        with self.assertRaises(ValueError):self.runrow()
    def test_csv_reserves_before_numeric_conversion(self):
        self.adapter.rows(b'value,opaque\n3,hash123\n');before=self.q.ledger['unique_json_bytes'];self.adapter.rows(b'value,opaque\n3,hash123\n')
        self.assertEqual(self.q.ledger['unique_json_bytes'],before);self.assertEqual(self.q.ledger['reserved_numeric_tokens'],0)
        self.assertEqual(self.adapter.scalar('3'),3);self.assertEqual(self.q.ledger['reserved_numeric_tokens'],1)
        self.q.numeric_cap=1
        with self.assertRaises(ValueError):self.adapter.scalar('4')
        self.assertEqual(self.q.ledger['reserved_numeric_tokens'],1)
    def test_csv_packet_cap_and_json_anchor_charges(self):
        self.q.byte_cap=2
        with self.assertRaises(ValueError):self.adapter.rows(b'value\n3\n')
        self.assertEqual(self.q.ledger['unique_json_bytes'],0)
        self.q.byte_cap=32000000
        with self.q.decoding():self.runrow()
        self.assertGreater(self.q.ledger['reserved_numeric_tokens'],5)
    def test_complete_join_and_distinct_quantities(self):
        view={'records':[{'entity_id':'current:a','name':'A'},{'entity_id':'current:family','name':'Family'}],
            'evidence':[{'id':'core','entity_id':'current:a','metric':'core_depth','unit':'m','value_m':30,'qualifier':'core is not bottom'},{'id':'pressure','entity_id':'current:a','metric':'reach_pressure','unit':'dbar','value_dbar':200}],
            'source_contexts':{'source':{'caveat':'No observed physical bottom.'}}}
        ready={'records':[{'entity_id':'current:a','identity_level':'current','canonical_reference_ids':['core','pressure'],'direct_current_without_supported_regional_case':False},
            {'entity_id':'current:family','identity_level':'family','canonical_reference_ids':[],'direct_current_without_supported_regional_case':False}]}
        report=assemble(view,ready,[],[self.runrow()],self.scopes)
        self.assertEqual(report['counts']['currents'],2);self.assertEqual(report['counts']['owners_with_paired_rows'],1)
        self.assertEqual([e['reference'] for e in report['entries'] if e['record_type']=='canonical_reference'],view['evidence'])
        family=report['entries'][1];self.assertEqual(family['regional_estimate_ids'],[]);self.assertIsNone(family['whole_route_physical_depth_m'])
        self.assertEqual(expand_report(json.loads(json.dumps(compact_report(report)))),report)
        with self.assertRaises(ValueError):assemble(view,ready,[],[self.runrow(),self.runrow()],self.scopes)
    def test_lossless_codec_null_bool_pressure_unicode_and_bad_schema(self):
        report={'schema':'osw.current-depth-almanac.expanded.v1','entries':[{'a':[None,False,0,3.14,'é'],'unit':'dbar'},{'a':[],'unit':'m'}]}
        packed=compact_report(report);self.assertEqual(expand_report(packed),report)
        packed['entries']['object_key_schemas'].append(packed['entries']['object_key_schemas'][0])
        with self.assertRaises(ValueError):expand_report(packed)
    def test_csv_all_cells_roundtrip_without_rounding(self):
        raw=table([{'a':None,'b':[1.234567890123,2],'c':'quoted,"\ntext'}],['a','b','c'])
        self.assertIn(b'1.234567890123',raw)

if __name__=='__main__':unittest.main()
