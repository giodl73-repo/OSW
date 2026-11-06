"""Synthetic semantics only; no retained scientific data read."""
import copy,math,unittest
import derive_sec_basin_paired_depth_v1 as m

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
        case={'entity_id':'current:atlantic-south-equatorial','section_id':'synthetic','snapshot_time_utc':m.DATES[0],'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':'synthetic-fixed-longitude','component_bearing_degrees_true':270,'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'synthetic-interior','original_selected_column_index':1,'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN','depth_levels_m':self.z,'columns':columns,'lateral_gate_censored':True}
        saved=copy.deepcopy(case);out=m.derive_case(case,'/cases/0','synthetic branch')
        self.assertEqual(case,saved);self.assertTrue(out['lateral_gate_censored']);self.assertIsNone(out['volume_km3']);self.assertIsNone(out['physical_current_thickness_m']);self.assertFalse(out['whole_section_area_established']);self.assertAlmostEqual(out['equivalent_paired_component_thickness_m'],20)
        case['columns'][2]['global_latitude_index']=3
        with self.assertRaises(ValueError):m.derive_case(case,'/cases/0','synthetic branch')
        case=copy.deepcopy(saved);case['component_bearing_degrees_true']=45
        with self.assertRaises(ValueError):m.derive_case(case,'/cases/0','synthetic branch')
    def test_unresolved_case_stays_null_and_long_connector_rejected(self):
        case={'entity_id':'current:atlantic-south-equatorial','section_id':'synthetic','snapshot_time_utc':m.DATES[0],'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':'synthetic','component_bearing_degrees_true':270,'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'unresolved','original_selected_column_index':None,'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN','columns':[]}
        out=m.derive_case(case,'/cases/0','synthetic');self.assertIsNone(out['conditional_partial_area_km2']);self.assertIsNone(out['equivalent_paired_component_thickness_m'])
        with self.assertRaises(ValueError):m.separation([0,0],[0,1])

class OrderedObjectEncoding(unittest.TestCase):
    def report(self,cases):return {'schema':'osw.sec-basin-paired-depth.v1','header':'unchanged','cases':cases,'tail':False}
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

class BasinCases(unittest.TestCase):
    def fixture(self):
        method={'snapshot_times_utc':m.DATES[:],'maximum_nearest_longitude_distance_km':5,'core_search_depth_interval_m':[0,200],'surface_component_gate_m_s':.05,'thresholds_m_s':[.05,.1,.2],'maximum_total_temperature_scalars':0,'maximum_total_decoded_temperature_bytes':0,'eligibility':{'physical_volume':False},'currents':{},'sections':[]};sources={};reviews={}
        for owner in m.OWNERS:
            config={'entity_id':owner,'component_bearing_degrees_true':270,'primary_threshold_m_s':.1,'surface_component_gate_m_s':.05,'temperature_gate':None,'branch_scope':'synthetic restricted basin reach '+owner};method['currents'][owner]=config;cases=[]
            for j in range(5):
                lon=-31-j if owner=='current:atlantic-south-equatorial' else -100-j*10 if owner=='current:pacific-south-equatorial' else 90-j*5;lat=-4 if owner=='current:atlantic-south-equatorial' else -3 if owner=='current:pacific-south-equatorial' else -12
                d={'id':'section-'+str(j),'entity_id':owner,'fixed_axis':'longitude','longitude_degrees_east':lon,'latitude_gate_degrees_north':[lat-2.5,lat+2.5]};method['sections'].append(d)
                for ti,stamp in enumerate(m.DATES):
                    cols=[]
                    for i in range(3):
                        r=run(1,6,5,350,[0,10],[300,400]);r['contains_original_core']=i==1
                        cols.append({'native_column_index':i,'global_longitude_index':100+j,'global_latitude_index':200+i,'sampled_lon_lat':[lon,lat+i*.01],'status':'ORIGINAL_SEED_CONNECTED_SUPPORT','connected_depth_runs':[r]})
                    c={'entity_id':owner,'section_id':d['id'],'snapshot_time_utc':stamp,'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':{'section_definition':copy.deepcopy(d),'retrieved_hyperslab':{},'maximum_nearest_longitude_distance_km':2,'actual_source_longitude_degrees_east':lon%360},'cohort_id':'sec-basin','source_operator':m.METHODS[0],'component_bearing_degrees_true':270,'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'synthetic-interior','original_selected_column_index':1,'original_primary_layer':copy.deepcopy(cols[1]['connected_depth_runs'][0]['threshold_layer']),'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN','depth_levels_m':[0,10,20,50,100,200,300,400],'columns':cols,'lateral_gate_censored':True,'native_surface_seed_connected':False}
                    if j*2+ti<m.GAPS[owner]:c.update(status='ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN',columns=[],original_selected_column_index=0,original_horizontal_selection_status='original_gate_edge')
                    cases.append(c)
            sources[owner]={'schema':'osw.sec-basin-velocity-depth-curtains.v1','status':'REGIONAL_MODEL_COMPONENT_THRESHOLD_GEOMETRY_NOT_PHYSICAL_CURRENT_BOTTOM','batch_current_id':owner,'source_plan_case_count':30,'cases':cases};reviews[owner]={'entity_id':owner,'status':'ORIGINAL_SOURCE_PRIMARY_CURRENT_BATCH_RETAINED'}
        return sources,reviews,[method]
    def test_all_thirty_cases_twenty_seven_axes_three_original_gaps_immutable(self):
        sources,reviews,methods=self.fixture();saved=copy.deepcopy((sources,reviews,methods));out=m.build(sources,reviews,methods);self.assertEqual((sources,reviews,methods),saved);self.assertEqual(out['counts']['source_cases'],30);self.assertEqual(out['counts']['original_axis_proxy_anchors'],27);self.assertEqual(out['counts']['original_unresolved_cases'],3)
        for o in m.OWNERS:self.assertEqual(out['counts_by_current'][o]['original_unresolved_cases'],m.GAPS[o])
    def test_global_classic_window_and_source_depth_context_do_not_cap_thickness(self):
        out=m.build(*self.fixture())
        for row in out['cases']:
            self.assertEqual(row['source_selection_depth_interval_m'],[0,200]);self.assertEqual(row['source_selection_window_origin'],'original_classic_global_upper200m_inherited_not_interval_owner_override');a=row['original_axis_proxy_depth_anchor']
            if a is not None:self.assertEqual(a['paired_component_run']['upper_depth_m'],5);self.assertEqual(a['paired_component_run']['lower_depth_m'],350);self.assertEqual(a['paired_component_run']['thickness_m'],345)
    def test_surface_selection_not_every_run_or_topology_or_current_presence(self):
        out=m.build(*self.fixture())
        for row in out['cases']:
            self.assertEqual(row['source_surface_component_gate_m_s'],.05);self.assertFalse(row['original_native_surface_seed_connected']);a=row['original_axis_proxy_depth_anchor']
            if a is not None:self.assertGreater(a['paired_component_run']['upper_depth_m'],0)
            else:self.assertEqual(row['original_selected_column_index'],0);self.assertIsNone(row['conditional_partial_area_km2']);self.assertEqual(row['original_horizontal_selection_status'],'original_gate_edge')
    def test_dictionary_measured_offset_and_wrapped_native_longitude_preserved(self):
        for offset in [0,2,5]:
            sources,reviews,methods=self.fixture()
            for source in sources.values():
                for c in source['cases']:c['source_geometry']['maximum_nearest_longitude_distance_km']=offset
            out=m.build(sources,reviews,methods);self.assertEqual(out['cases'][0]['source_geometry']['actual_source_longitude_degrees_east'],329);self.assertEqual(out['cases'][0]['source_compiled_descriptor_file'],m.SOURCES['current:atlantic-south-equatorial'][0])
    def test_censored_depth_is_unknown_with_native_minimum_not_invented_area(self):
        sources,reviews,methods=self.fixture();c=sources['current:indian-south-equatorial']['cases'][-1]
        for col in c['columns']:col['connected_depth_runs'][0]['threshold_layer'].update(lower_status='censored_at_sample_domain_edge',lower_depth_m=None,layer_thickness_m=None)
        c['original_primary_layer']=copy.deepcopy(c['columns'][1]['connected_depth_runs'][0]['threshold_layer']);row=m.build(sources,reviews,methods)['cases'][-1];p=row['original_axis_proxy_depth_anchor']['paired_component_run'];self.assertIsNone(p['thickness_m']);self.assertEqual(p['native_supported_minimum_component_span_m'],290);self.assertIsNone(row['conditional_partial_area_km2'])
    def test_exact_json_both_csv_roundtrips_and_null_parent_gap_fields(self):
        import json,csv,io
        out=m.build(*self.fixture());restored=m.expand_report(json.loads(m.encode(m.compact_report(out))));self.assertEqual(m.encode(restored),m.encode(out))
        for writer in [m.csv_bytes,m.anchor_csv]:
            self.assertEqual(writer(out['cases']),writer(restored['cases']));rows=list(csv.DictReader(io.StringIO(writer(out['cases']).decode())));self.assertEqual(len(rows),30)
            for row in rows:self.assertEqual(row['source_parent_depth_values_inherited'],'');self.assertEqual(row['source_surface_component_gate_m_s'],'0.05')
        rows=list(csv.DictReader(io.StringIO(m.anchor_csv(out['cases']).decode())));self.assertEqual(rows[20]['paired_component_thickness_m'],'');self.assertEqual(rows[20]['lower_component_depth_m'],'')
    def test_no_parent_family_current_body_or_physical_volume_promotions(self):
        out=m.build(*self.fixture())
        for row in out['cases']:
            self.assertEqual(row['source_identity_context'],{});self.assertIsNone(row['source_parent_depth_values_inherited']);self.assertIsNone(row['source_parent_current_id']);self.assertIsNone(row['physical_current_thickness_m']);self.assertIsNone(row['volume_km3']);self.assertFalse(row['whole_route_depth_eligible']);self.assertFalse(row['whole_section_area_established']);self.assertEqual(row['source_fixed_axis'],'longitude')
    def test_original_basin_date_frame_gate_window_geometry_and_pair_mutations_fail(self):
        owner='current:atlantic-south-equatorial'
        for change in ['family','missingbasin','duplicate','date','frame','surface','window','interval','ownerwindow','parent','thermal','topology','axis','definition','offset','native','coordinate','indices','primary','rule','cohort','promotion']:
            sources,reviews,methods=self.fixture();c=sources[owner]['cases'][-1];method=methods[0];config=method['currents'][owner]
            if change=='family':sources[owner]['batch_current_id']='current:south-equatorial'
            elif change=='missingbasin':del sources['current:indian-south-equatorial']
            elif change=='duplicate':sources[owner]['cases'][-2]=copy.deepcopy(c)
            elif change=='date':c['snapshot_time_utc']='2022-03-15T00:00:00Z'
            elif change=='frame':c['component_bearing_degrees_true']=90
            elif change=='surface':method['surface_component_gate_m_s']=None
            elif change=='window':method['core_search_depth_interval_m']=[0,100]
            elif change=='interval':method['selection_depth_interval_m']=[0,200]
            elif change=='ownerwindow':config['core_search_depth_interval_m']=[0,200]
            elif change=='parent':config['parent_depth_values_inherited']=False
            elif change=='thermal':method['maximum_total_temperature_scalars']=1
            elif change=='topology':c['native_surface_seed_connected']=0
            elif change=='axis':c['source_geometry']='longitude'
            elif change=='definition':c['source_geometry']['section_definition']['latitude_gate_degrees_north']=[-2,2]
            elif change=='offset':c['source_geometry']['maximum_nearest_longitude_distance_km']=6
            elif change=='native':c['source_geometry']['actual_source_longitude_degrees_east']+=1
            elif change=='coordinate':c['columns'][0]['sampled_lon_lat'][0]+=.1
            elif change=='indices':c['columns'][1]['global_latitude_index']+=1
            elif change=='primary':c['original_primary_layer']['lower_depth_m']=349
            elif change=='rule':c['source_operator']='synthetic-other'
            elif change=='cohort':c['cohort_id']='synthetic-other'
            else:method['eligibility']['physical_volume']=True
            with self.assertRaises((ValueError,KeyError)):m.build(sources,reviews,methods)

if __name__=='__main__':unittest.main()
