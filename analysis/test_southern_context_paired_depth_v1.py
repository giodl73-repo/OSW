"""Synthetic semantics only; no retained scientific data read."""
import copy,math,unittest
import derive_southern_context_paired_depth_v1 as m

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
        case={'entity_id':'current:indian-south-equatorial-countercurrent','section_id':'synthetic','snapshot_time_utc':m.DATES[0],'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':'synthetic-fixed-longitude','component_bearing_degrees_true':90,'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'synthetic-interior','original_selected_column_index':1,'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN','depth_levels_m':self.z,'columns':columns,'lateral_gate_censored':True}
        saved=copy.deepcopy(case);out=m.derive_case(case,'/cases/0','synthetic branch')
        self.assertEqual(case,saved);self.assertTrue(out['lateral_gate_censored']);self.assertIsNone(out['volume_km3']);self.assertIsNone(out['physical_current_thickness_m']);self.assertFalse(out['whole_section_area_established']);self.assertAlmostEqual(out['equivalent_paired_component_thickness_m'],20)
        case['columns'][2]['global_latitude_index']=3
        with self.assertRaises(ValueError):m.derive_case(case,'/cases/0','synthetic branch')
        case=copy.deepcopy(saved);case['component_bearing_degrees_true']=45
        with self.assertRaises(ValueError):m.derive_case(case,'/cases/0','synthetic branch')
    def test_unresolved_case_stays_null_and_long_connector_rejected(self):
        case={'entity_id':'current:indian-south-equatorial-countercurrent','section_id':'synthetic','snapshot_time_utc':m.DATES[0],'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':'synthetic','component_bearing_degrees_true':90,'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'unresolved','original_selected_column_index':None,'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN','columns':[]}
        out=m.derive_case(case,'/cases/0','synthetic');self.assertIsNone(out['conditional_partial_area_km2']);self.assertIsNone(out['equivalent_paired_component_thickness_m'])
        with self.assertRaises(ValueError):m.separation([0,0],[0,1])

class OrderedObjectEncoding(unittest.TestCase):
    def report(self,cases):return {'schema':'osw.southern-context-paired-depth.v1','header':'unchanged','cases':cases,'tail':False}
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

class SouthernCases(unittest.TestCase):
    def fixture(self):
        methods=[];sources={};reviews={}
        for mi in range(2):
            method={'snapshot_times_utc':m.METHOD_DATES[mi][:],'maximum_nearest_longitude_distance_km':5,'core_search_depth_interval_m':[0,200],'surface_component_gate_m_s':.02 if mi==0 else None,'thresholds_m_s':[.05,.1,.2],'maximum_total_temperature_scalars':0,'maximum_total_decoded_temperature_bytes':0,'eligibility':{'physical_volume':False},'currents':{},'sections':[]}
            if mi:method['selection_depth_interval_m']=[0,200]
            methods.append(method)
        for owner in m.OWNERS:
            mi=m.OWNER_METHOD[owner];method=methods[mi];config={'entity_id':owner,'component_bearing_degrees_true':90,'primary_threshold_m_s':m.THRESHOLDS[owner],'surface_component_gate_m_s':.02 if mi==0 else None,'temperature_gate':None,'branch_scope':'synthetic partial '+owner}
            if mi:config.update(core_search_depth_interval_m=[0,200],selection_depth_interval_m=[0,200])
            method['currents'][owner]=config;cases=[]
            for j in range(m.CASE_COUNTS[owner]//len(m.METHOD_DATES[mi])):
                lon=-103+j*3.75 if owner=='current:south-pacific' else 135.5+j*2 if owner=='current:south-australian' else 93+j if owner=='current:indian-south-equatorial-countercurrent' else 168+j;lat=-34 if mi==0 else -6 if owner=='current:indian-south-equatorial-countercurrent' else -10
                d={'id':'section-'+str(j),'entity_id':owner,'fixed_axis':'longitude','longitude_degrees_east':lon,'latitude_gate_degrees_north':[lat-2.5,lat+2.5]};method['sections'].append(d)
                for ti,stamp in enumerate(m.METHOD_DATES[mi]):
                    cols=[]
                    for i in range(3):
                        r=run(1,6,5,350,[0,10],[300,400]);r['contains_original_core']=i==1;r['threshold_layer']['threshold_m_s']=m.THRESHOLDS[owner]
                        cols.append({'native_column_index':i,'global_longitude_index':100+j,'global_latitude_index':200+i,'sampled_lon_lat':[lon,lat+i*.01],'status':'ORIGINAL_SEED_CONNECTED_SUPPORT','connected_depth_runs':[r]})
                    g={'section_definition':copy.deepcopy(d),'retrieved_hyperslab':{},'maximum_nearest_longitude_distance_km':2,'actual_source_longitude_degrees_east':lon%360} if mi==0 else 'longitude'
                    c={'entity_id':owner,'section_id':d['id'],'snapshot_time_utc':stamp,'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':g,'cohort_id':m.COHORTS[mi],'source_operator':m.METHODS[mi],'component_bearing_degrees_true':90,'velocity_threshold_m_s':m.THRESHOLDS[owner],'original_horizontal_selection_status':'synthetic-interior','original_selected_column_index':1,'original_primary_layer':copy.deepcopy(cols[1]['connected_depth_runs'][0]['threshold_layer']),'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN','depth_levels_m':[0,10,20,50,100,200,300,400],'columns':cols,'lateral_gate_censored':True}
                    if mi==0:c['native_surface_seed_connected']=False
                    else:c['geometry_adapter']='ORIGINAL_LONGITUDE_INTERVAL_VALIDATED_THEN_IN_MEMORY_TAG_ONLY'
                    if j*len(m.METHOD_DATES[mi])+ti<m.GAPS[owner]:c.update(status='ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN',columns=[],original_selected_column_index=0,original_horizontal_selection_status='original_candidate_unresolved')
                    cases.append(c)
            sources[owner]={'schema':'osw.'+m.COHORTS[mi]+'-velocity-depth-curtains.v1','status':'REGIONAL_MODEL_COMPONENT_THRESHOLD_GEOMETRY_NOT_PHYSICAL_CURRENT_BOTTOM','batch_current_id':owner,'source_plan_case_count':m.SOURCE_PLANS[mi],'cases':cases};reviews[owner]={'entity_id':owner,'status':'ORIGINAL_SOURCE_PRIMARY_CURRENT_BATCH_RETAINED'}
        return sources,reviews,methods
    def test_all_fifty_eight_cases_forty_one_axes_seventeen_gaps_immutable(self):
        sources,reviews,methods=self.fixture();saved=copy.deepcopy((sources,reviews,methods));out=m.build(sources,reviews,methods);self.assertEqual((sources,reviews,methods),saved);self.assertEqual(out['counts']['source_cases'],58);self.assertEqual(out['counts']['original_axis_proxy_anchors'],41);self.assertEqual(out['counts']['original_unresolved_cases'],17)
        for o in m.OWNERS:self.assertEqual(out['counts_by_current'][o]['original_unresolved_cases'],m.GAPS[o])
    def test_five_and_ten_cm_primary_cutoffs_and_surface_gates_stay_distinct(self):
        out=m.build(*self.fixture())
        for r in out['cases']:
            o=r['entity_id'];mi=m.OWNER_METHOD[o];self.assertEqual(r['velocity_threshold_m_s'],.05 if mi==0 else .1);self.assertEqual(r['source_surface_component_gate_m_s'],.02 if mi==0 else None);a=r['original_axis_proxy_depth_anchor']
            if a is not None:self.assertEqual(a['paired_component_run']['thickness_m'],345)
    def test_original_two_vs_four_dates_are_not_relabelled(self):
        out=m.build(*self.fixture())
        for o in m.OWNERS:self.assertEqual({r['snapshot_time_utc'] for r in out['cases'] if r['entity_id']==o},set(m.METHOD_DATES[m.OWNER_METHOD[o]]))
        self.assertIn('40-case',out['temporal_scope'])
    def test_global_classic_or_owner_interval_not_depth_cap_or_surface_top(self):
        out=m.build(*self.fixture())
        for r in out['cases']:
            mi=m.OWNER_METHOD[r['entity_id']];self.assertEqual(r['source_selection_window_origin'],'original_classic_global_upper200m_inherited' if mi==0 else 'original_explicit_owner_interval');a=r['original_axis_proxy_depth_anchor']
            if a is not None:self.assertEqual(a['paired_component_run']['upper_depth_m'],5);self.assertEqual(a['paired_component_run']['lower_depth_m'],350);self.assertGreater(a['paired_component_run']['thickness_m'],200)
    def test_classic_dictionary_native_wrap_and_interval_enum_adapter_preserved(self):
        out=m.build(*self.fixture())
        for r in out['cases']:
            if m.OWNER_METHOD[r['entity_id']]==0:self.assertIsInstance(r['source_geometry'],dict);self.assertFalse(r['original_native_surface_seed_connected']);self.assertNotIn('geometry_adapter',r)
            else:self.assertEqual(r['source_geometry'],'longitude');self.assertEqual(r['geometry_adapter'],'ORIGINAL_LONGITUDE_INTERVAL_VALIDATED_THEN_IN_MEMORY_TAG_ONLY');self.assertNotIn('original_native_surface_seed_connected',r)
        self.assertEqual(out['cases'][0]['source_geometry']['actual_source_longitude_degrees_east'],257)
    def test_censored_reach_bottom_and_original_gap_stay_unknown(self):
        sources,reviews,methods=self.fixture();c=sources['current:south-australian']['cases'][-1]
        for col in c['columns']:col['connected_depth_runs'][0]['threshold_layer'].update(lower_status='censored_before_missing_or_dry_level',lower_depth_m=None,layer_thickness_m=None)
        c['original_primary_layer']=copy.deepcopy(c['columns'][1]['connected_depth_runs'][0]['threshold_layer']);r=m.build(sources,reviews,methods)['cases'][17];p=r['original_axis_proxy_depth_anchor']['paired_component_run'];self.assertIsNone(p['thickness_m']);self.assertEqual(p['native_supported_minimum_component_span_m'],290);self.assertIsNone(r['conditional_partial_area_km2'])
    def test_undeclared_parent_context_and_physical_unknowns_preserved(self):
        for r in m.build(*self.fixture())['cases']:self.assertEqual(r['source_identity_context'],{});self.assertIsNone(r['source_parent_depth_values_inherited']);self.assertIsNone(r['source_parent_current_id']);self.assertIsNone(r['physical_current_thickness_m']);self.assertIsNone(r['volume_km3']);self.assertFalse(r['whole_section_area_established'])
    def test_full_json_both_context_csv_roundtrips_and_censor_gap_cells(self):
        import csv,io,json
        out=m.build(*self.fixture());restored=m.expand_report(json.loads(m.encode(m.compact_report(out))));self.assertEqual(m.encode(restored),m.encode(out))
        for writer in [m.csv_bytes,m.anchor_csv]:
            a=m.contextual_csv(writer,out['cases']);self.assertEqual(a,m.contextual_csv(writer,restored['cases']));rows=list(csv.DictReader(io.StringIO(a.decode())));self.assertEqual(len(rows),58)
            for r in rows:
                self.assertEqual(r['source_parent_depth_values_inherited'],'')
                if m.OWNER_METHOD[r['entity_id']]==0:self.assertEqual(r['original_native_surface_seed_connected'],'false');self.assertEqual(r['geometry_adapter'],'')
                else:self.assertEqual(r['original_native_surface_seed_connected'],'');self.assertNotEqual(r['geometry_adapter'],'')
        rows=list(csv.DictReader(io.StringIO(m.contextual_csv(m.anchor_csv,out['cases']).decode())));self.assertEqual(rows[0]['paired_component_thickness_m'],'')
    def test_original_thresholds_dates_surface_strata_geometry_and_pair_mutations_fail(self):
        reach='current:south-pacific';counter='current:indian-south-equatorial-countercurrent'
        for change in ['date','cutoff','cutoffrun','surface','surfacecounter','window','interval','ownerwindow','parent','relative','thermal','topology','adapter','extraadapter','extraitopology','offset','native','coordinate','indices','primary','rule','cohort','plan','missingowner','promotion']:
            sources,reviews,methods=self.fixture();c=sources[reach]['cases'][-1];ic=sources[counter]['cases'][-1]
            if change=='date':c['snapshot_time_utc']=m.METHOD_DATES[1][0]
            elif change=='cutoff':methods[0]['currents'][reach]['primary_threshold_m_s']=.1
            elif change=='cutoffrun':c['columns'][0]['connected_depth_runs'][0]['threshold_layer']['threshold_m_s']=.1
            elif change=='surface':methods[0]['surface_component_gate_m_s']=.05
            elif change=='surfacecounter':methods[1]['surface_component_gate_m_s']=.02
            elif change=='window':methods[0]['core_search_depth_interval_m']=[0,100]
            elif change=='interval':methods[0]['selection_depth_interval_m']=[0,200]
            elif change=='ownerwindow':methods[0]['currents'][reach]['selection_depth_interval_m']=[0,200]
            elif change=='parent':methods[1]['currents'][counter]['parent_depth_values_inherited']=False
            elif change=='relative':methods[1]['currents'][counter]['require_core_stronger_than_surface']=True
            elif change=='thermal':methods[0]['maximum_total_temperature_scalars']=1
            elif change=='topology':c['native_surface_seed_connected']=0
            elif change=='adapter':ic['geometry_adapter']='other'
            elif change=='extraadapter':c['geometry_adapter']='other'
            elif change=='extraitopology':ic['native_surface_seed_connected']=False
            elif change=='offset':c['source_geometry']['maximum_nearest_longitude_distance_km']=6
            elif change=='native':c['source_geometry']['actual_source_longitude_degrees_east']+=1
            elif change=='coordinate':ic['columns'][0]['sampled_lon_lat'][0]+=.1
            elif change=='indices':c['columns'][1]['global_latitude_index']+=1
            elif change=='primary':c['original_primary_layer']['lower_depth_m']=349
            elif change=='rule':c['source_operator']=m.METHODS[1]
            elif change=='cohort':c['cohort_id']='southern-countercurrent'
            elif change=='plan':sources[counter]['source_plan_case_count']=20
            elif change=='missingowner':del sources[counter]
            else:methods[0]['eligibility']['physical_volume']=True
            with self.assertRaises((ValueError,KeyError)):m.build(sources,reviews,methods)
    def test_context_wrapper_preserves_all_original_csv_field_values(self):
        import csv,io
        out=m.build(*self.fixture())
        for writer in [m.csv_bytes,m.anchor_csv]:
            before=list(csv.DictReader(io.StringIO(writer(out['cases']).decode())));after=list(csv.DictReader(io.StringIO(m.contextual_csv(writer,out['cases']).decode())))
            for a,b in zip(before,after):self.assertEqual(a,{k:b[k] for k in a})

if __name__=='__main__':unittest.main()
