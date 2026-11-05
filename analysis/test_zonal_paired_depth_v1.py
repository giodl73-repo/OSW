"""Synthetic analytic geometry checks; never read retained ocean data."""
import copy,math,unittest
import derive_zonal_paired_depth_v1 as m

def run(first,last,upper,lower,ub,lb):
    return {'native_depth_indices_inclusive':[first,last],'contains_original_core':True,'threshold_layer':{'threshold_m_s':.1,'upper_depth_m':upper,'lower_depth_m':lower,'upper_status':'adjacent_isotach_crossing','lower_status':'adjacent_isotach_crossing','upper_bracket_m':ub,'lower_bracket_m':lb,'layer_thickness_m':lower-upper}}

class PairedGeometry(unittest.TestCase):
    def setUp(self):
        self.z=[0,10,20,30,40,50]
        self.a=m.run_geometry(run(1,2,5,25,[0,10],[20,30]),self.z)
        self.b=m.run_geometry(run(1,3,5,35,[0,10],[30,40]),self.z)
    def col(self,index,runs):return {'native_column_index':index,'sampled_lon_lat':[0,index*.01],'runs':runs}
    def test_linear_wedge_area_and_sampling_scenarios_have_correct_units(self):
        s=m.strip(self.col(0,[self.a]),self.col(1,[self.b]));p=s['patches'][0]
        distance=6371008.8*math.radians(.01)
        self.assertAlmostEqual(s['distance_m'],distance)
        self.assertAlmostEqual(p['linear_contour_strip_area_km2'],25*distance/1e6)
        self.assertAlmostEqual(p['sampling_bracket_strip_area_bounds_km2'][0],15*distance/1e6)
        self.assertAlmostEqual(p['sampling_bracket_strip_area_bounds_km2'][1],35*distance/1e6)
    def test_censor_is_unknown_and_never_closed_at_sample_limit(self):
        r=run(1,5,5,55,[0,10],[50,60]);r['threshold_layer'].update(lower_status='censored_at_sample_domain_edge',lower_depth_m=None,layer_thickness_m=None)
        g=m.run_geometry(r,self.z);self.assertIsNone(g['thickness_m']);self.assertIsNone(g['sampling_thickness_bounds_m'])
        s=m.strip(self.col(0,[self.a]),self.col(1,[g]));self.assertEqual(s['patches'],[]);self.assertEqual(s['rejected_links'][0]['reason'],'CENSORED_TOP_OR_BOTTOM')
        self.assertEqual(s['status'],'NO_INTEGRABLE_PAIRED_CONTOURS_UNKNOWN_NOT_ZERO')
    def test_surface_top_allowed_only_at_zero_and_bracket_not_confidence(self):
        r=run(0,2,0,25,[0,10],[20,30]);r['threshold_layer']['upper_status']='surface_bounded_layer'
        g=m.run_geometry(r,self.z);self.assertEqual(g['sampling_thickness_bounds_m'],[20,30])
        r['threshold_layer']['upper_depth_m']=1
        with self.assertRaises(ValueError):m.run_geometry(r,self.z)
    def test_split_or_merge_is_not_turned_into_one_thick_layer(self):
        broad=m.run_geometry(run(1,4,5,45,[0,10],[40,50]),self.z)
        low=m.run_geometry(run(3,4,25,45,[20,30],[40,50]),self.z)
        s=m.strip(self.col(0,[broad]),self.col(1,[self.a,low]))
        self.assertEqual(s['patches'],[]);self.assertEqual(len(s['rejected_links']),2)
        self.assertTrue(all(p['reason']=='AMBIGUOUS_VERTICAL_SPLIT_OR_MERGE' for p in s['rejected_links']))
    def test_disjoint_runs_and_empty_column_do_not_bridge_missing_support(self):
        low=m.run_geometry(run(3,4,25,45,[20,30],[40,50]),self.z)
        s=m.strip(self.col(0,[self.a]),self.col(1,[low]));self.assertEqual(s['patches'],[]);self.assertEqual(s['unmatched_left_runs'],[0]);self.assertEqual(s['unmatched_right_runs'],[0])
        s=m.strip(self.col(0,[self.a]),self.col(1,[]));self.assertEqual(s['patches'],[])
    def test_source_depth_pair_and_cutoff_mutations_rejected(self):
        for key,value in [('layer_thickness_m',100),('threshold_m_s',.05),('lower_depth_m',50),('upper_bracket_m',[9,10])]:
            r=run(1,2,5,25,[0,10],[20,30]);r['threshold_layer'][key]=value
            with self.assertRaises(ValueError):m.run_geometry(r,self.z)
    def test_case_preserves_gap_and_branch_identity_and_forbids_skipping_indices(self):
        columns=[]
        for i in range(3):columns.append({'native_column_index':i,'global_longitude_index':0,'global_latitude_index':i,'sampled_lon_lat':[20,1+i*.01],'status':'ORIGINAL_SEED_CONNECTED_SUPPORT','connected_depth_runs':[run(1,2,5,25,[0,10],[20,30])]})
        case={'entity_id':'current:kuroshio-extension','section_id':'synthetic','snapshot_time_utc':m.DATES[0],'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':'synthetic-fixed-longitude','component_bearing_degrees_true':90,'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'synthetic-interior','original_selected_column_index':1,'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN','depth_levels_m':self.z,'columns':columns,'lateral_gate_censored':True}
        saved=copy.deepcopy(case);out=m.derive_case(case,'/cases/0','synthetic branch')
        self.assertEqual(case,saved);self.assertTrue(out['lateral_gate_censored']);self.assertIsNone(out['volume_km3']);self.assertIsNone(out['physical_current_thickness_m']);self.assertFalse(out['whole_section_area_established']);self.assertAlmostEqual(out['equivalent_paired_component_thickness_m'],20)
        case['columns'][2]['global_latitude_index']=3
        with self.assertRaises(ValueError):m.derive_case(case,'/cases/0','synthetic branch')
        case=copy.deepcopy(saved);case['component_bearing_degrees_true']=45
        with self.assertRaises(ValueError):m.derive_case(case,'/cases/0','synthetic branch')
    def test_unresolved_case_stays_null_and_long_connector_rejected(self):
        case={'entity_id':'current:kuroshio-extension','section_id':'synthetic','snapshot_time_utc':m.DATES[0],'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':'synthetic','component_bearing_degrees_true':90,'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'unresolved','original_selected_column_index':None,'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN','columns':[]}
        out=m.derive_case(case,'/cases/0','synthetic');self.assertIsNone(out['conditional_partial_area_km2']);self.assertIsNone(out['equivalent_paired_component_thickness_m'])
        with self.assertRaises(ValueError):m.separation([0,0],[0,1])


class ZonalCases(unittest.TestCase):
    def fixture(self):
        method={'snapshot_times_utc':m.DATES[:],'maximum_nearest_longitude_distance_km':5,'core_search_depth_interval_m':[0,200],'surface_component_gate_m_s':.05,'eligibility':{'physical_volume':False},'currents':{},'sections':[]};sources=[];reviews=[]
        longs={'current:kuroshio-extension':[145,150,155,160],'current:agulhas-return':[21,25,30,35,40,50,60],'current:north-pacific':[160,170,180,-170,-160,-150,-145]}
        for owner in m.OWNERS:
            method['currents'][owner]={'entity_id':owner,'component_bearing_degrees_true':90,'primary_threshold_m_s':m.THRESHOLDS[owner],'surface_component_gate_m_s':m.SURFACE_GATES[owner],'temperature_gate':None,'branch_scope':'original restricted reach '+owner};cases=[]
            for j,lon in enumerate(longs[owner]):
                definition={'id':'section-'+str(j),'entity_id':owner,'fixed_axis':'longitude','longitude_degrees_east':lon,'latitude_gate_degrees_north':[30,35]};method['sections'].append(definition)
                for stamp in m.DATES:
                    columns=[]
                    for i in range(3):
                        r=run(1,2,5,25,[0,10],[20,30]);r['contains_original_core']=i==1;r['threshold_layer']['threshold_m_s']=m.THRESHOLDS[owner]
                        columns.append({'native_column_index':i,'global_longitude_index':100+j,'global_latitude_index':200+i,'sampled_lon_lat':[(lon+180)%360-180,32+i*.01],'status':'ORIGINAL_SEED_CONNECTED_SUPPORT','connected_depth_runs':[r]})
                    case={'entity_id':owner,'section_id':definition['id'],'snapshot_time_utc':stamp,'source_operator':m.METHODS[0],'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':{'section_definition':copy.deepcopy(definition),'actual_source_longitude_degrees_east':lon%360,'maximum_nearest_longitude_distance_km':0,'retrieved_hyperslab':{'latitude_indices_inclusive':[200,202],'longitude_index':100+j}},'component_bearing_degrees_true':90,'velocity_threshold_m_s':m.THRESHOLDS[owner],'original_horizontal_selection_status':'synthetic-interior','original_selected_column_index':1,'original_primary_layer':copy.deepcopy(columns[1]['connected_depth_runs'][0]['threshold_layer']),'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'native_surface_seed_connected':True,'status':'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN','depth_levels_m':[0,10,20,30,40,50],'columns':columns,'lateral_gate_censored':True}
                    if owner=='current:agulhas-return' and j==0:case.update(status='ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN',columns=[],original_selected_column_index=0,original_horizontal_selection_status='original_candidate_unresolved',native_surface_seed_connected=False)
                    cases.append(case)
            sources.append({'schema':'osw.zonal-current-velocity-depth-curtains.v1','status':'REGIONAL_MODEL_COMPONENT_THRESHOLD_GEOMETRY_NOT_PHYSICAL_CURRENT_BOTTOM','batch_current_id':owner,'source_plan_case_count':36,'cases':cases});reviews.append({'status':'ORIGINAL_SOURCE_PRIMARY_CURRENT_BATCH_RETAINED','entity_id':owner})
        return sources,reviews,[method]
    def test_all36_cases34_anchors2_gaps_and_three_sources_immutable(self):
        sources,reviews,methods=self.fixture();saved=copy.deepcopy(sources);out=m.build(sources,reviews,methods);self.assertEqual(sources,saved)
        self.assertEqual(out['counts']['source_cases'],36);self.assertEqual(out['counts']['original_axis_proxy_anchors'],34);self.assertEqual(out['counts']['original_unresolved_cases'],2)
        for o,n in m.OWNER_CASES.items():self.assertEqual(out['counts_by_current'][o]['source_cases'],n)
        for r in out['cases']:self.assertIsNone(r['volume_km3']);self.assertIsNone(r['physical_current_thickness_m']);self.assertFalse(r['whole_route_depth_eligible'])
    def test_owner_specific_primary_and_surface_cutoffs_preserved(self):
        sources,reviews,methods=self.fixture();out=m.build(sources,reviews,methods)
        for r in out['cases']:
            o=r['entity_id'];self.assertEqual(r['velocity_threshold_m_s'],m.THRESHOLDS[o]);self.assertEqual(r['source_surface_component_gate_m_s'],m.SURFACE_GATES[o]);self.assertEqual(r['component_bearing_degrees_true'],90);self.assertEqual(r['source_selection_depth_interval_m'],[0,200])
        self.assertEqual(out['counts_by_primary_threshold_m_s']['0.05']['source_cases'],14);self.assertEqual(out['counts_by_primary_threshold_m_s']['0.1']['source_cases'],22)
    def test_date_line_and_native_0_360_receipts_are_circular(self):
        sources,reviews,methods=self.fixture();out=m.build(sources,reviews,methods)
        self.assertEqual(m.longitude_delta(-180,180),0);self.assertEqual(m.longitude_delta(-170,190),0);self.assertAlmostEqual(m.longitude_delta(179.99,-179.99),-.02)
        self.assertTrue(any(r['source_geometry']['section_definition']['longitude_degrees_east']==180 and r['columns'][0]['sampled_lon_lat'][0]==-180 for r in out['cases'] if r['columns']))
        sources[2]['cases'][4]['source_geometry']['maximum_nearest_longitude_distance_km']=5.1
        with self.assertRaises(ValueError):m.build(sources,reviews,methods)
    def test_surface_gate_and_graph_connection_do_not_force_primary_top_zero(self):
        sources,reviews,methods=self.fixture();out=m.build(sources,reviews,methods)
        for r in out['cases']:
            a=r['original_axis_proxy_depth_anchor']
            if a is not None:self.assertTrue(r['source_native_surface_seed_connected']);self.assertEqual(a['paired_component_run']['upper_depth_m'],5);self.assertEqual(a['paired_component_run']['thickness_m'],20)
            else:self.assertIn('not constructed',r['source_surface_connectivity_interpretation'])
    def test_each_case_pointer_is_scoped_by_exact_original_compiled_file(self):
        sources,reviews,methods=self.fixture();out=m.build(sources,reviews,methods)
        for owner in m.OWNERS:
            rows=[r for r in out['cases'] if r['entity_id']==owner]
            for i,r in enumerate(rows):self.assertEqual(r['source_compiled_descriptor_file'],m.SOURCES[owner][0]);self.assertEqual(r['source_compiled_descriptor_sha256'],m.SOURCES[owner][1]);self.assertEqual(r['source_descriptor_pointer'],'/cases/'+str(i))
        first=[r for r in out['cases'] if r['source_descriptor_pointer']=='/cases/0'];self.assertEqual(len(first),3);self.assertEqual(len({r['source_compiled_descriptor_file'] for r in first}),3)
    def test_censored_core_keeps_minimum_span_without_finite_bottom(self):
        sources,reviews,methods=self.fixture();c=sources[0]['cases'][0];p=c['columns'][1]['connected_depth_runs'][0]['threshold_layer'];p.update(lower_status='censored_at_sample_domain_edge',lower_depth_m=None,layer_thickness_m=None);c['original_primary_layer']=copy.deepcopy(p)
        out=m.build(sources,reviews,methods);p=out['cases'][0]['original_axis_proxy_depth_anchor']['paired_component_run'];self.assertIsNone(p['thickness_m']);self.assertIsNone(p['lower_depth_m']);self.assertEqual(p['native_supported_minimum_component_span_m'],10);self.assertFalse(p['minimum_span_is_physical_current_bound'])
    def test_all_original_batches_identity_date_axis_and_method_mutations_rejected(self):
        for change in ['missing_batch','swapped','review','batch_owner','plan','missing_case','duplicate','owner','direction','cutoff','gate','window','date','promotion','section','indices','native','rule','primary']:
            sources,reviews,methods=self.fixture();c=sources[0]['cases'][0]
            if change=='missing_batch':sources.pop()
            elif change=='swapped':sources[0],sources[1]=sources[1],sources[0]
            elif change=='review':reviews[0]['entity_id']='wrong'
            elif change=='batch_owner':sources[0]['batch_current_id']='wrong'
            elif change=='plan':sources[0]['source_plan_case_count']=8
            elif change=='missing_case':sources[0]['cases'].pop()
            elif change=='duplicate':sources[0]['cases'][1]=copy.deepcopy(c)
            elif change=='owner':c['entity_id']='current:kuroshio'
            elif change=='direction':c['component_bearing_degrees_true']=270
            elif change=='cutoff':methods[0]['currents']['current:north-pacific']['primary_threshold_m_s']=.1
            elif change=='gate':methods[0]['currents']['current:north-pacific']['surface_component_gate_m_s']=.05
            elif change=='window':methods[0]['core_search_depth_interval_m']=[0,100]
            elif change=='date':c['snapshot_time_utc']='2022-03-15T00:00:00Z'
            elif change=='promotion':methods[0]['eligibility']['physical_volume']=True
            elif change=='section':c['source_geometry']['section_definition']['fixed_axis']='latitude'
            elif change=='indices':c['columns'][1]['global_latitude_index']+=1
            elif change=='native':c['columns'][0]['sampled_lon_lat'][0]+=.1
            elif change=='rule':c['source_operator']='wrong'
            else:c['original_primary_layer']['lower_depth_m']=26
            with self.assertRaises((ValueError,KeyError)):m.build(sources,reviews,methods)
    def test_model_graph_does_not_promote_physical_current_identity(self):
        sources,reviews,methods=self.fixture();sources[0]['cases'][0]['named_current_axis_independently_validated']=True
        with self.assertRaises(ValueError):m.build(sources,reviews,methods)
    def test_exact_full_json_and_both_csv_roundtrips_visible_original_source(self):
        import csv,io,json
        sources,reviews,methods=self.fixture();out=m.build(sources,reviews,methods);restored=m.expand_report(json.loads(m.encode(m.compact_report(out))));self.assertEqual(m.encode(restored),m.encode(out))
        for writer in [m.csv_bytes,m.anchor_csv]:
            self.assertEqual(writer(restored['cases']),writer(out['cases']));rows=list(csv.DictReader(io.StringIO(writer(out['cases']).decode())));self.assertEqual(len(rows),36)
            for r in rows:self.assertEqual(r['source_compiled_descriptor_file'],m.SOURCES[r['entity_id']][0]);self.assertEqual(r['source_compiled_descriptor_sha256'],m.SOURCES[r['entity_id']][1]);self.assertEqual(float(r['source_surface_component_gate_m_s']),m.SURFACE_GATES[r['entity_id']])
        for r in csv.DictReader(io.StringIO(m.anchor_csv(out['cases']).decode())):
            if r['status']=='ORIGINAL_AXIS_UNRESOLVED_NO_SECTION_GEOMETRY':self.assertEqual(r['paired_component_thickness_m'],'');self.assertEqual(r['lower_component_depth_m'],'')
    def test_single_level_minimum_zero_is_uninformative(self):
        r=run(1,1,5,15,[0,10],[10,20]);r['threshold_layer'].update(lower_status='censored_at_sample_domain_edge',lower_depth_m=None,layer_thickness_m=None);p=m.run_support(r,[0,10,20]);self.assertEqual(p['native_supported_minimum_component_span_m'],0);self.assertIsNone(p['thickness_m']);self.assertFalse(p['minimum_span_is_physical_current_bound'])


class OrderedObjectEncoding(unittest.TestCase):
    def report(self,cases):return {'schema':'osw.zonal-paired-depth.v1','header':'unchanged','cases':cases,'tail':False}
    def roundtrip(self,value):
        import json
        before=m.encode(value);packed=m.compact_report(value);restored=m.expand_report(json.loads(m.encode(packed)));self.assertEqual(m.encode(restored),before);self.assertEqual(m.encode(value),before);return packed
    def test_arbitrary_key_order_unicode_null_bool_int_float_and_empty(self):
        self.roundtrip(self.report([{'z':None,'a':[True,False,0,0.0,-0.0,1.2345678901234567,'Δ漂流',[],{}],'empty':'','inner':{'b':2,'a':1}}]))
    def test_original_lists_resembling_tags_stay_original_lists(self):
        self.roundtrip(self.report([{'tags':[[0,[]],[1,0,[]],[2,0],['o',1,[2,3]],[]]}]))
    def test_same_fields_different_order_have_distinct_schemas(self):
        p=self.roundtrip(self.report([{'a':1,'b':2},{'b':2,'a':1}]))
        self.assertIn(['a','b'],p['cases']['object_key_schemas']);self.assertIn(['b','a'],p['cases']['object_key_schemas'])
    def test_repeated_exact_strings_interned_without_rounding(self):
        p=self.roundtrip(self.report([{'text':'same','number':1.2345678901234567},{'text':'same','number':1.2345678901234567}]))
        self.assertEqual(p['cases']['string_values'],['same']);self.assertLess(len(m.encode(p)),1000)
    def test_bad_tags_indices_and_value_counts_rejected(self):
        for node in [[3,[]],[1,-1,[]],[1,99,[]],[1,True,[]],[True,0,[]],[1,0,[]],[2,99],[2,False],[0,{}],'untagged string',{}]:
            p=m.compact_report(self.report([{'a':1}]))
            p['cases']['node']=node
            with self.assertRaises(ValueError):m.expand_report(p)
    def test_duplicate_schemas_keys_and_string_values_rejected(self):
        for change in ['schema_duplicate','key_duplicate','schema_type','string_duplicate','string_type','extra']:
            p=m.compact_report(self.report([{'a':'same'}]));b=p['cases']
            if change=='schema_duplicate':b['object_key_schemas'].append(b['object_key_schemas'][0][:])
            elif change=='key_duplicate':b['object_key_schemas'][0]=['a','a']
            elif change=='schema_type':b['object_key_schemas'][0]=[1]
            elif change=='string_duplicate':b['string_values'].append('same')
            elif change=='string_type':b['string_values']=[1]
            else:b['extra']='discarded?'
            with self.assertRaises(ValueError):m.expand_report(p)
    def test_wrong_versions_and_nonobject_case_list_rejected(self):
        with self.assertRaises(ValueError):m.compact_report({'schema':'wrong','cases':[]})
        p=m.compact_report(self.report([{'a':1}]))
        p['schema']='wrong'
        with self.assertRaises(ValueError):m.expand_report(p)
        p=m.compact_report(self.report([{'a':1}]))
        p['cases']['node']=[0,[42]]
        with self.assertRaises(ValueError):m.expand_report(p)
    def test_fresh_calls_have_no_cross_report_state(self):
        a=m.compact_report(self.report([{'x':'alpha'}]));b=m.compact_report(self.report([{'y':'beta'}]));self.assertEqual(a['cases']['string_values'],['alpha']);self.assertEqual(b['cases']['string_values'],['beta']);self.assertEqual(m.expand_report(a)['cases'],[{'x':'alpha'}])

if __name__=='__main__':unittest.main()
