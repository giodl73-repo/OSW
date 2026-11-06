"""Synthetic semantics only; no retained scientific data read."""
import copy,math,unittest
import derive_partitioned_paired_depth_v1 as m

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
        case={'entity_id':'current:tasman-front','section_id':'synthetic','snapshot_time_utc':m.DATES[0],'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':'synthetic-fixed-longitude','component_bearing_degrees_true':90,'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'synthetic-interior','original_selected_column_index':1,'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN','depth_levels_m':self.z,'columns':columns,'lateral_gate_censored':True}
        saved=copy.deepcopy(case);out=m.derive_case(case,'/cases/0','synthetic branch')
        self.assertEqual(case,saved);self.assertTrue(out['lateral_gate_censored']);self.assertIsNone(out['volume_km3']);self.assertIsNone(out['physical_current_thickness_m']);self.assertFalse(out['whole_section_area_established']);self.assertAlmostEqual(out['equivalent_paired_component_thickness_m'],20)
        case['columns'][2]['global_latitude_index']=3
        with self.assertRaises(ValueError):m.derive_case(case,'/cases/0','synthetic branch')
        case=copy.deepcopy(saved);case['component_bearing_degrees_true']=45
        with self.assertRaises(ValueError):m.derive_case(case,'/cases/0','synthetic branch')
    def test_unresolved_case_stays_null_and_long_connector_rejected(self):
        case={'entity_id':'current:tasman-front','section_id':'synthetic','snapshot_time_utc':m.DATES[0],'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':'synthetic','component_bearing_degrees_true':90,'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'unresolved','original_selected_column_index':None,'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN','columns':[]}
        out=m.derive_case(case,'/cases/0','synthetic');self.assertIsNone(out['conditional_partial_area_km2']);self.assertIsNone(out['equivalent_paired_component_thickness_m'])
        with self.assertRaises(ValueError):m.separation([0,0],[0,1])

class OrderedObjectEncoding(unittest.TestCase):
    def report(self,cases):return {'schema':'osw.partitioned-paired-depth.v1','header':'unchanged','cases':cases,'tail':False}
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

class PartitionCases(unittest.TestCase):
    def fixture(self):
        method={'snapshot_times_utc':m.DATES[:],'maximum_nearest_longitude_distance_km':5,'core_search_depth_interval_m':[0,200],'selection_depth_interval_m':[0,200],'surface_component_gate_m_s':None,'thresholds_m_s':[.05,.1,.2],'maximum_total_temperature_scalars':0,'maximum_total_decoded_temperature_bytes':0,'eligibility':{'physical_volume':False},'currents':{},'sections':[],'search_partitions':{}};sources={};reviews={}
        for owner in m.OWNERS:method['currents'][owner]={'entity_id':owner,'component_bearing_degrees_true':90,'primary_threshold_m_s':m.THRESHOLDS[owner],'surface_component_gate_m_s':None,'temperature_gate':None,'core_search_depth_interval_m':[0,200],'selection_depth_interval_m':[0,200],'branch_scope':'synthetic partial original '+owner}
        for part,(owner,gate,gaps) in m.PARTITIONS.items():
            context={'id':part,'entity_id':owner,'kind':'editorial_latitude_search_context','latitude_gate_degrees_north':gate[:],'scope':'synthetic editorial search,not identified front','front_or_water_mass_classification_performed':False,'persistent_jet_identity_validated':False,'cross_partition_interpolation_permitted':False,'canonical_current_ownership_changed':False};method['search_partitions'][part]=context;cases=[]
            for j in range(4):
                lon=-13+j*4 if owner=='current:south-atlantic' else 167+j*.5;lat=-35 if part=='sac-northern-search' else -39 if part=='sac-southern-search' else -30.5 if part=='tasman-north-bank-search' else -33
                d={'id':part+'-section-'+str(j),'entity_id':owner,'fixed_axis':'longitude','longitude_degrees_east':lon,'latitude_gate_degrees_north':gate[:],'search_partition_id':part};method['sections'].append(d)
                for ti,stamp in enumerate(m.DATES):
                    cols=[]
                    for i in range(3):
                        r=run(1,7,5,1150,[0,10],[1100,1200]);r['contains_original_core']=i==1;r['threshold_layer']['threshold_m_s']=m.THRESHOLDS[owner]
                        cols.append({'native_column_index':i,'global_longitude_index':100+j,'global_latitude_index':200+i,'sampled_lon_lat':[lon,lat+(i-1)*.01],'status':'ORIGINAL_SEED_CONNECTED_SUPPORT','connected_depth_runs':[r]})
                    c={'entity_id':owner,'section_id':d['id'],'snapshot_time_utc':stamp,'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':'longitude','cohort_id':'partitioned-ocean','source_operator':m.METHODS[0],'component_bearing_degrees_true':90,'velocity_threshold_m_s':m.THRESHOLDS[owner],'original_horizontal_selection_status':'synthetic-interior','original_selected_column_index':1,'original_primary_layer':copy.deepcopy(cols[1]['connected_depth_runs'][0]['threshold_layer']),'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN','depth_levels_m':[0,10,20,50,100,200,500,1100,1200],'columns':cols,'lateral_gate_censored':True,'geometry_adapter':'ORIGINAL_PARTITION_AND_LONGITUDE_INTERVAL_VALIDATED_THEN_IN_MEMORY_TAG_ONLY','search_partition_id':part,'search_partition_kind':'editorial_latitude_search_context','partition_is_current_identity':False,'cross_partition_join_performed':False,'front_or_water_mass_classification_performed':False}
                    if j*4+ti<gaps:c.update(status='ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN',columns=[],original_selected_column_index=0,original_horizontal_selection_status='original_candidate_unresolved')
                    cases.append(c)
            sources[part]={'schema':'osw.partitioned-ocean-velocity-depth-curtains.v1','status':'REGIONAL_MODEL_COMPONENT_THRESHOLD_GEOMETRY_NOT_PHYSICAL_CURRENT_BOTTOM','batch_partition_id':part,'source_plan_case_count':64,'cases':cases};reviews[part]={'batch_partition_id':part,'entity_id':owner,'status':'EXACT_ORIGINAL_16_CASE_PARTITION_BATCH_RETAINED'}
        return sources,reviews,[method]
    def test_all_sixty_four_cases_fifty_three_proxies_eleven_gaps_two_current_owners(self):
        sources,reviews,methods=self.fixture();saved=copy.deepcopy((sources,reviews,methods));out=m.build(sources,reviews,methods);self.assertEqual((sources,reviews,methods),saved);self.assertEqual(out['counts']['source_cases'],64);self.assertEqual(out['counts']['original_axis_proxy_anchors'],53);self.assertEqual(out['counts']['original_unresolved_cases'],11);self.assertEqual(set(out['counts_by_current']),set(m.OWNERS));self.assertEqual(len(out['counts_by_partition']),4)
        for p in m.PARTITIONS:self.assertEqual(out['counts_by_partition'][p]['original_unresolved_cases'],m.PARTITIONS[p][2])
    def test_partition_metadata_is_not_new_current_front_or_independent_observation(self):
        out=m.build(*self.fixture());self.assertFalse(out['partition_case_counts_are_independent_observation_counts']);self.assertFalse(out['cross_partition_physical_area_or_volume_added'])
        for row in out['cases']:
            self.assertEqual(row['entity_id'],m.PARTITIONS[row['search_partition_id']][0]);self.assertEqual(row['source_search_partition']['id'],row['search_partition_id']);self.assertTrue(all(row[k] is False for k in m.PARTITION_FLAGS));self.assertEqual(row['source_identity_context'],{});self.assertIsNone(row['source_parent_depth_values_inherited']);self.assertIsNone(row['volume_km3'])
    def test_own_cutoffs_selection_and_historical_depth_context_do_not_cap_layer(self):
        for r in m.build(*self.fixture())['cases']:
            self.assertEqual(r['velocity_threshold_m_s'],m.THRESHOLDS[r['entity_id']]);self.assertIsNone(r['source_surface_component_gate_m_s']);a=r['original_axis_proxy_depth_anchor']
            if a is not None:self.assertEqual(a['paired_component_run']['lower_depth_m'],1150);self.assertEqual(a['paired_component_run']['upper_depth_m'],5);self.assertEqual(a['paired_component_run']['thickness_m'],1145);self.assertIsNone(r['physical_current_thickness_m'])
    def test_partition_shared_boundary_allowed_but_interior_overlap_rejected(self):
        sources,reviews,methods=self.fixture();self.assertEqual(len(m.validate_partitions(methods[0])),4);methods[0]['search_partitions']['sac-northern-search']['latitude_gate_degrees_north'][0]=-38
        for d in methods[0]['sections']:
            if d['search_partition_id']=='sac-northern-search':d['latitude_gate_degrees_north'][0]=-38
        with self.assertRaises(ValueError):m.validate_partitions(methods[0])
    def test_shared_boundary_and_duplicate_promoted_native_axis_rejected(self):
        rows=m.build(*self.fixture())['cases'];r=copy.deepcopy(rows[0]);r['source_search_partition']['latitude_gate_degrees_north']=[-35,-33]
        with self.assertRaises(ValueError):m.validate_anchor_ownership([r])
        a=copy.deepcopy(rows[0]);b=copy.deepcopy(a);b['search_partition_id']='sac-southern-search'
        with self.assertRaises(ValueError):m.validate_anchor_ownership([a,b])
    def test_original_gate_edge_stays_null_without_weaker_axis_replacement(self):
        rows=m.build(*self.fixture())['cases'];r=rows[32];self.assertEqual(r['original_selected_column_index'],0);self.assertIsNone(r['original_axis_proxy_depth_anchor']);self.assertIsNone(r['conditional_partial_area_km2']);self.assertEqual(r['original_horizontal_selection_status'],'original_candidate_unresolved')
        sources,reviews,methods=self.fixture();c=sources['sac-northern-search']['cases'][0];c['original_selected_column_index']=0
        with self.assertRaises(ValueError):m.build(sources,reviews,methods)
    def test_censored_sac_axis_retains_minimum_support_without_finite_bottom_area(self):
        sources,reviews,methods=self.fixture();c=sources['sac-northern-search']['cases'][-1]
        for col in c['columns']:col['connected_depth_runs'][0]['threshold_layer'].update(lower_status='censored_before_missing_or_dry_level',lower_depth_m=None,layer_thickness_m=None)
        c['original_primary_layer']=copy.deepcopy(c['columns'][1]['connected_depth_runs'][0]['threshold_layer']);r=m.build(sources,reviews,methods)['cases'][15];p=r['original_axis_proxy_depth_anchor']['paired_component_run'];self.assertIsNone(p['thickness_m']);self.assertEqual(p['native_supported_minimum_component_span_m'],1090);self.assertIsNone(r['conditional_partial_area_km2'])
    def test_exact_json_both_context_csv_roundtrips_and_partition_gap_cells(self):
        import csv,io,json
        out=m.build(*self.fixture());restored=m.expand_report(json.loads(m.encode(m.compact_report(out))));self.assertEqual(m.encode(restored),m.encode(out))
        for writer in [m.csv_bytes,m.anchor_csv]:
            raw=m.contextual_csv(writer,out['cases']);self.assertEqual(raw,m.contextual_csv(writer,restored['cases']));rows=list(csv.DictReader(io.StringIO(raw.decode())));self.assertEqual(len(rows),64)
            for r in rows:self.assertEqual(r['partition_is_current_identity'],'false');self.assertEqual(r['cross_partition_join_performed'],'false');self.assertEqual(json.loads(r['source_search_partition'])['entity_id'],r['entity_id']);self.assertEqual(r['source_parent_depth_values_inherited'],'')
        rows=list(csv.DictReader(io.StringIO(m.contextual_csv(m.anchor_csv,out['cases']).decode())));self.assertEqual(rows[32]['paired_component_thickness_m'],'')
    def test_owner_partition_gates_cutoff_flags_geometry_and_primary_mutations_fail(self):
        for change in ['owner','part','kind','cutoff','surface','window','parent','thermal','identity','join','front','boolzero','adapter','coordinate','indices','primary','date','duplicate','plan','promote','partitionfront','partitionowner','partitiongate','missingpart']:
            sources,reviews,methods=self.fixture();c=sources['sac-northern-search']['cases'][-1];method=methods[0]
            if change=='owner':c['entity_id']='current:tasman-front'
            elif change=='part':c['search_partition_id']='sac-southern-search'
            elif change=='kind':c['search_partition_kind']='identified_front'
            elif change=='cutoff':method['currents']['current:south-atlantic']['primary_threshold_m_s']=.1
            elif change=='surface':method['surface_component_gate_m_s']=.05
            elif change=='window':method['selection_depth_interval_m']=[0,100]
            elif change=='parent':method['currents']['current:south-atlantic']['parent_depth_values_inherited']=False
            elif change=='thermal':method['maximum_total_temperature_scalars']=1
            elif change=='identity':c['partition_is_current_identity']=True
            elif change=='join':c['cross_partition_join_performed']=True
            elif change=='front':c['front_or_water_mass_classification_performed']=True
            elif change=='boolzero':c['partition_is_current_identity']=0
            elif change=='adapter':c['geometry_adapter']='other'
            elif change=='coordinate':c['columns'][0]['sampled_lon_lat'][1]=-42
            elif change=='indices':c['columns'][1]['global_latitude_index']+=1
            elif change=='primary':c['original_primary_layer']['lower_depth_m']=1149
            elif change=='date':c['snapshot_time_utc']='2022-01-15T00:00:00Z'
            elif change=='duplicate':sources['sac-northern-search']['cases'][-2]=copy.deepcopy(c)
            elif change=='plan':sources['sac-northern-search']['source_plan_case_count']=16
            elif change=='promote':method['eligibility']['physical_volume']=True
            elif change=='partitionfront':method['search_partitions']['sac-northern-search']['persistent_jet_identity_validated']=True
            elif change=='partitionowner':method['search_partitions']['sac-northern-search']['entity_id']='current:tasman-front'
            elif change=='partitiongate':method['search_partitions']['sac-northern-search']['latitude_gate_degrees_north']=[-36,-33]
            else:del sources['tasman-south-bank-search']
            with self.assertRaises((ValueError,KeyError)):m.build(sources,reviews,methods)
    def test_context_wrapper_preserves_every_original_csv_field(self):
        import csv,io
        out=m.build(*self.fixture())
        for writer in [m.csv_bytes,m.anchor_csv]:
            before=list(csv.DictReader(io.StringIO(writer(out['cases']).decode())));after=list(csv.DictReader(io.StringIO(m.contextual_csv(writer,out['cases']).decode())))
            for a,b in zip(before,after):self.assertEqual(a,{k:b[k] for k in a})

if __name__=='__main__':unittest.main()
