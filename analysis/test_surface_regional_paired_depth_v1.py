"""Synthetic analytic geometry checks; never read retained ocean data."""
import copy,math,unittest
import derive_surface_regional_paired_depth_v1 as m

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
        for i in range(3):columns.append({'native_column_index':i,'global_longitude_index':i,'global_latitude_index':0,'sampled_lon_lat':[20+i*.01,1],'status':'ORIGINAL_SEED_CONNECTED_SUPPORT','connected_depth_runs':[run(1,2,5,25,[0,10],[20,30])]})
        case={'entity_id':'current:east-adriatic','section_id':'synthetic','snapshot_time_utc':m.DATES[0],'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':'synthetic-fixed-longitude','component_bearing_degrees_true':315,'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'synthetic-interior','original_selected_column_index':1,'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN','depth_levels_m':self.z,'columns':columns,'lateral_gate_censored':True}
        saved=copy.deepcopy(case);out=m.derive_case(case,'/cases/0','synthetic branch')
        self.assertEqual(case,saved);self.assertTrue(out['lateral_gate_censored']);self.assertIsNone(out['volume_km3']);self.assertIsNone(out['physical_current_thickness_m']);self.assertFalse(out['whole_section_area_established']);self.assertAlmostEqual(out['equivalent_paired_component_thickness_m'],20)
        case['columns'][2]['global_longitude_index']=3
        with self.assertRaises(ValueError):m.derive_case(case,'/cases/0','synthetic branch')
        case=copy.deepcopy(saved);case['component_bearing_degrees_true']=45
        with self.assertRaises(ValueError):m.derive_case(case,'/cases/0','synthetic branch')
    def test_unresolved_case_stays_null_and_long_connector_rejected(self):
        case={'entity_id':'current:east-adriatic','section_id':'synthetic','snapshot_time_utc':m.DATES[0],'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':'synthetic','component_bearing_degrees_true':315,'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'unresolved','original_selected_column_index':None,'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN','columns':[]}
        out=m.derive_case(case,'/cases/0','synthetic');self.assertIsNone(out['conditional_partial_area_km2']);self.assertIsNone(out['equivalent_paired_component_thickness_m'])
        with self.assertRaises(ValueError):m.separation([0,0],[0,1])


class SurfaceRegionalCases(unittest.TestCase):
    def fixture(self):
        methods=[];cases=[]
        for mi in range(3):
            group=[o for o in m.OWNERS if m.OWNER_METHOD[o]==mi];window=[0,30] if mi==0 else [0,100] if mi==1 else [0,200]
            method={'snapshot_times_utc':m.DATES[:],'maximum_nearest_latitude_distance_km':5,'core_search_depth_interval_m':window[:],'surface_component_gate_m_s':None,'thresholds_m_s':[.05,.1,.2],'maximum_total_temperature_scalars':0,'maximum_total_decoded_temperature_bytes':0,'eligibility':{'physical_volume':False},'currents':{},'sections':[]}
            for owner in group:
                config={'entity_id':owner,'component_bearing_degrees_true':m.OWNERS[owner],'primary_threshold_m_s':.1,'surface_component_gate_m_s':None,'temperature_gate':None,'core_search_depth_interval_m':window[:],'selection_depth_interval_m':window[:],'branch_scope':'synthetic restricted regional reach '+owner};config.update(copy.deepcopy(m.CONTEXTS[owner]));method['currents'][owner]=config
                for j in range(4):
                    lat=43.5-j*.5 if mi==0 else 57+j*.2 if mi==1 else -15+j if owner=='current:hiri-current' else -40.5-j*.75
                    lon=16 if owner=='current:east-adriatic' else 14 if owner=='current:western-adriatic' else -156 if mi==1 else 146 if owner=='current:hiri-current' else 144
                    definition={'id':'section-'+str(j),'entity_id':owner,'fixed_axis':'latitude','latitude_degrees_north':lat,'longitude_gate_degrees_east':[lon-.5,lon+1]};method['sections'].append(definition)
                    for ti,stamp in enumerate(m.DATES):
                        columns=[]
                        for i in range(3):
                            r=run(2,7,15,175,[10,20],[150,200]);r['contains_original_core']=i==1
                            columns.append({'native_column_index':i,'global_longitude_index':100+i,'global_latitude_index':200+j,'sampled_lon_lat':[lon+i*.01,lat],'status':'ORIGINAL_SEED_CONNECTED_SUPPORT','connected_depth_runs':[r]})
                        case={'entity_id':owner,'section_id':definition['id'],'snapshot_time_utc':stamp,'source_operator':m.METHODS[mi],'cohort_id':m.COHORTS[owner],'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':'latitude','component_bearing_degrees_true':m.OWNERS[owner],'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'synthetic-interior','original_selected_column_index':1,'original_primary_layer':copy.deepcopy(columns[1]['connected_depth_runs'][0]['threshold_layer']),'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN','depth_levels_m':[0,10,20,30,40,50,100,150,200,300],'columns':columns,'lateral_gate_censored':True}
                        if j*4+ti<m.GAPS[owner]:case.update(status='ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN',columns=[],original_selected_column_index=0,original_horizontal_selection_status='original_candidate_unresolved')
                        cases.append(case)
            methods.append(method)
        source={'schema':'osw.surface-regional-velocity-depth-curtains.v1','status':'REGIONAL_MODEL_COMPONENT_THRESHOLD_GEOMETRY_NOT_PHYSICAL_CURRENT_BOTTOM','cases':cases};review={'status':'ALL80_ORIGINAL_CASES_PRESERVED_65_REGIONAL_CURTAINS_15_EXPLICIT_UNRESOLVED'}
        return source,review,methods
    def test_all80_cases65_anchors15_gaps_and_source_immutable(self):
        source,review,methods=self.fixture();saved=copy.deepcopy(source);out=m.build(source,review,methods);self.assertEqual(source,saved)
        self.assertEqual(out['counts']['source_cases'],80);self.assertEqual(out['counts']['original_axis_proxy_anchors'],65);self.assertEqual(out['counts']['original_unresolved_cases'],15)
        for o in m.OWNERS:self.assertEqual(out['counts_by_current'][o]['source_cases'],16);self.assertEqual(out['counts_by_current'][o]['original_unresolved_cases'],m.GAPS[o])
        for r in out['cases']:self.assertIsNone(r['volume_km3']);self.assertIsNone(r['physical_current_thickness_m']);self.assertFalse(r['whole_route_depth_eligible'])
    def test_original_five_frames_strata_and_no_surface_gate(self):
        source,review,methods=self.fixture();out=m.build(source,review,methods)
        for r in out['cases']:
            o=r['entity_id'];self.assertEqual(r['component_bearing_degrees_true'],m.OWNERS[o]);self.assertEqual(r['source_selection_depth_interval_m'],m.WINDOWS[o]);self.assertEqual(r['velocity_threshold_m_s'],.1);self.assertIsNone(r['source_surface_component_gate_m_s']);self.assertEqual(r['surface_gate_policy'],'not_applied_in_original_method');self.assertEqual(r['source_fixed_axis'],'latitude')
    def test_adriatic_thirty_meter_search_is_not_layer_thickness_or_bottom(self):
        source,review,methods=self.fixture();out=m.build(source,review,methods)
        for r in out['cases']:
            if r['entity_id'] in ['current:east-adriatic','current:western-adriatic'] and r['original_axis_proxy_depth_anchor'] is not None:
                p=r['original_axis_proxy_depth_anchor']['paired_component_run'];self.assertEqual(r['source_selection_depth_interval_m'],[0,30]);self.assertEqual(p['upper_depth_m'],15);self.assertEqual(p['lower_depth_m'],175);self.assertEqual(p['thickness_m'],160);self.assertEqual(p['native_supported_minimum_component_span_m'],130)
    def test_historical_strict_zeehan_reach_not_imposed_on_2022_snapshot(self):
        source,review,methods=self.fixture();out=m.build(source,review,methods);r=next(r for r in out['cases'] if r['entity_id']=='current:zeehan' and r['original_axis_proxy_depth_anchor'] is not None);self.assertEqual(r['source_selection_depth_interval_m'],[0,200]);self.assertLess(r['original_axis_proxy_depth_anchor']['paired_component_run']['lower_depth_m'],300);self.assertEqual(r['source_identity_evidence_basis'],m.CONTEXTS['current:zeehan']['identity_evidence_basis'])
    def test_absent_adriatic_parent_fields_stay_undeclared_not_false(self):
        source,review,methods=self.fixture();out=m.build(source,review,methods)
        for r in out['cases']:
            if m.OWNER_METHOD[r['entity_id']]==0:self.assertNotIn('parent_depth_values_inherited',r['source_identity_context']);self.assertIsNone(r['source_parent_depth_values_inherited']);self.assertNotIn('parent_current_id',r['source_identity_context'])
        methods[0]['currents']['current:east-adriatic']['parent_depth_values_inherited']=False
        with self.assertRaises(ValueError):m.build(source,review,methods)
    def test_zeehan_parent_preserved_without_depth_inheritance_or_additivity(self):
        source,review,methods=self.fixture();out=m.build(source,review,methods)
        for r in out['cases']:
            o=r['entity_id'];self.assertEqual(r['source_identity_context'],{k:m.CONTEXTS[o][k] for k in m.CONTEXT_KEYS if k in m.CONTEXTS[o]})
            if o=='current:zeehan':self.assertEqual(r['source_parent_current_id'],'current:australian-west-south-boundary-flow');self.assertFalse(r['source_parent_depth_values_inherited']);self.assertEqual(r['source_identity_relationship'],'regional_component_not_additive_boundary_system')
        for change in ['parent','inherit','zero','alias','basis']:
            source,review,methods=self.fixture();config=methods[2]['currents']['current:zeehan']
            if change=='parent':config['parent_current_id']='current:leeuwin'
            elif change=='inherit':config['parent_depth_values_inherited']=True
            elif change=='zero':config['parent_depth_values_inherited']=0
            elif change=='alias':config['identity_relationship']='whole_parent'
            else:config['identity_evidence_basis']=m.CONTEXTS['current:hiri-current']['identity_evidence_basis']
            with self.assertRaises(ValueError):m.build(source,review,methods)
    def test_shelikof_and_hiri_scopes_do_not_inherit_other_current_identity(self):
        source,review,methods=self.fixture();out=m.build(source,review,methods)
        for r in out['cases']:
            o=r['entity_id']
            if o in ['current:alaska-coastal-gulf','current:hiri-current']:self.assertIsNone(r['source_parent_current_id']);self.assertFalse(r['source_parent_depth_values_inherited']);self.assertEqual(r['source_identity_relationship'],m.CONTEXTS[o]['identity_relationship'])
        methods[1]['currents']['current:alaska-coastal-gulf']['parent_current_id']='current:alaska'
        with self.assertRaises(ValueError):m.build(source,review,methods)
    def test_censored_core_keeps_minimum_without_finite_bottom(self):
        source,review,methods=self.fixture();c=next(c for c in source['cases'] if c['columns']);p=c['columns'][1]['connected_depth_runs'][0]['threshold_layer'];p.update(lower_status='censored_before_missing_or_dry_level',lower_depth_m=None,layer_thickness_m=None);c['original_primary_layer']=copy.deepcopy(p)
        out=m.build(source,review,methods);p=out['cases'][source['cases'].index(c)]['original_axis_proxy_depth_anchor']['paired_component_run'];self.assertIsNone(p['lower_depth_m']);self.assertIsNone(p['thickness_m']);self.assertEqual(p['native_supported_minimum_component_span_m'],130);self.assertFalse(p['minimum_span_is_physical_current_bound'])
    def test_unknown_axis_stays_null_not_zero_or_replacement(self):
        source,review,methods=self.fixture();c=source['cases'][0];c['original_selected_column_index']=None;c['original_primary_layer']=None;out=m.build(source,review,methods);r=out['cases'][0];self.assertIsNone(r['original_axis_proxy_depth_anchor']);self.assertIsNone(r['conditional_partial_area_km2']);self.assertEqual(r['columns'],[]);self.assertIsNone(r['original_primary_layer'])
    def test_original_cohort_axis_frame_window_and_eligibility_mutations(self):
        for change in ['missing_method','missing_case','duplicate','owner','frame','cutoff','surface','window','date','promotion','axis','coordinate','indices','rule','cohort','primary','temperature','classification']:
            source,review,methods=self.fixture();c=next(c for c in source['cases'] if c['columns'])
            if change=='missing_method':methods.pop()
            elif change=='missing_case':source['cases'].pop()
            elif change=='duplicate':source['cases'][1]=copy.deepcopy(source['cases'][0])
            elif change=='owner':c['entity_id']='current:dalmatian'
            elif change=='frame':c['component_bearing_degrees_true']=135
            elif change=='cutoff':methods[1]['currents']['current:alaska-coastal-gulf']['primary_threshold_m_s']=.05
            elif change=='surface':methods[0]['surface_component_gate_m_s']=.05
            elif change=='window':methods[0]['core_search_depth_interval_m']=[0,100]
            elif change=='date':c['snapshot_time_utc']='2022-01-15T00:00:00Z'
            elif change=='promotion':methods[0]['eligibility']['physical_volume']=True
            elif change=='axis':c['source_geometry']='longitude'
            elif change=='coordinate':c['columns'][0]['sampled_lon_lat'][1]+=.1
            elif change=='indices':c['columns'][1]['global_longitude_index']+=1
            elif change=='rule':c['source_operator']=m.METHODS[1]
            elif change=='cohort':c['cohort_id']='hiri-zeehan'
            elif change=='temperature':methods[0]['maximum_total_temperature_scalars']=1
            elif change=='classification':c['water_mass_classification_performed']=True
            else:c['original_primary_layer']['lower_depth_m']=176
            with self.assertRaises((ValueError,KeyError)):m.build(source,review,methods)
    def test_exact_full_json_both_csvs_expose_declared_and_absent_context(self):
        import csv,io,json
        source,review,methods=self.fixture();out=m.build(source,review,methods);restored=m.expand_report(json.loads(m.encode(m.compact_report(out))));self.assertEqual(m.encode(restored),m.encode(out))
        for writer in [m.csv_bytes,m.anchor_csv]:
            self.assertEqual(writer(restored['cases']),writer(out['cases']));rows=list(csv.DictReader(io.StringIO(writer(out['cases']).decode())));self.assertEqual(len(rows),80)
            for r in rows:
                o=r['entity_id'];self.assertEqual(r['source_fixed_axis'],'latitude');self.assertEqual(r['source_identity_evidence_basis'],m.CONTEXTS[o]['identity_evidence_basis']);self.assertEqual(json.loads(r['source_selection_depth_interval_m']),m.WINDOWS[o]);self.assertEqual(r['source_parent_depth_values_inherited'],'' if m.OWNER_METHOD[o]==0 else 'false')
        for r in csv.DictReader(io.StringIO(m.anchor_csv(out['cases']).decode())):
            if r['status']=='ORIGINAL_AXIS_UNRESOLVED_NO_SECTION_GEOMETRY':self.assertEqual(r['paired_component_thickness_m'],'');self.assertEqual(r['lower_component_depth_m'],'')
    def test_single_level_minimum_zero_is_uninformative(self):
        r=run(1,1,5,15,[0,10],[10,20]);r['threshold_layer'].update(lower_status='censored_at_sample_domain_edge',lower_depth_m=None,layer_thickness_m=None);p=m.run_support(r,[0,10,20]);self.assertEqual(p['native_supported_minimum_component_span_m'],0);self.assertIsNone(p['thickness_m']);self.assertFalse(p['minimum_span_is_physical_current_bound'])


class OrderedObjectEncoding(unittest.TestCase):
    def report(self,cases):return {'schema':'osw.surface-regional-paired-depth.v1','header':'unchanged','cases':cases,'tail':False}
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
