"""Synthetic semantics only; no retained scientific data read."""
import copy,math,unittest
import derive_spitsbergen_indian_paired_depth_v1 as m

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
        case={'entity_id':'current:spitsbergen-atlantic','section_id':'synthetic','snapshot_time_utc':m.DATES[0],'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':'synthetic-fixed-longitude','component_bearing_degrees_true':315,'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'synthetic-interior','original_selected_column_index':1,'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN','depth_levels_m':self.z,'columns':columns,'lateral_gate_censored':True}
        saved=copy.deepcopy(case);out=m.derive_case(case,'/cases/0','synthetic branch')
        self.assertEqual(case,saved);self.assertTrue(out['lateral_gate_censored']);self.assertIsNone(out['volume_km3']);self.assertIsNone(out['physical_current_thickness_m']);self.assertFalse(out['whole_section_area_established']);self.assertAlmostEqual(out['equivalent_paired_component_thickness_m'],20)
        case['columns'][2]['global_longitude_index']=3
        with self.assertRaises(ValueError):m.derive_case(case,'/cases/0','synthetic branch')
        case=copy.deepcopy(saved);case['component_bearing_degrees_true']=45
        with self.assertRaises(ValueError):m.derive_case(case,'/cases/0','synthetic branch')
    def test_unresolved_case_stays_null_and_long_connector_rejected(self):
        case={'entity_id':'current:spitsbergen-atlantic','section_id':'synthetic','snapshot_time_utc':m.DATES[0],'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':'synthetic','component_bearing_degrees_true':315,'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'unresolved','original_selected_column_index':None,'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN','columns':[]}
        out=m.derive_case(case,'/cases/0','synthetic');self.assertIsNone(out['conditional_partial_area_km2']);self.assertIsNone(out['equivalent_paired_component_thickness_m'])
        with self.assertRaises(ValueError):m.separation([0,0],[0,1])

class OrderedObjectEncoding(unittest.TestCase):
    def report(self,cases):return {'schema':'osw.spitsbergen-indian-paired-depth.v1','header':'unchanged','cases':cases,'tail':False}
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

class ScopedIntervalRelativeCases(unittest.TestCase):
    def fixture(self):
        methods=[];sources={};reviews={}
        for owner in m.OWNERS:
            mi=m.OWNER_METHOD[owner];win=m.WINDOWS[owner];axis=m.AXES[owner]
            method={'snapshot_times_utc':m.DATES[:],'maximum_nearest_latitude_distance_km':5,'maximum_nearest_longitude_distance_km':5,'core_search_depth_interval_m':win[:],'selection_depth_interval_m':win[:],'surface_component_gate_m_s':None,'thresholds_m_s':[.05,.1,.2],'maximum_total_temperature_scalars':0,'maximum_total_decoded_temperature_bytes':0,'eligibility':{'physical_volume':False},'currents':{},'sections':[],'time_scope':'stale January/July prose' if mi else 'quarterly2022'}
            config={'entity_id':owner,'component_bearing_degrees_true':m.OWNERS[owner],'primary_threshold_m_s':.1,'surface_component_gate_m_s':None,'temperature_gate':None,'branch_scope':'synthetic original restricted '+owner}
            if mi==0:config.update(copy.deepcopy(m.SPITS_CONTEXT));config.update(core_search_depth_interval_m=win[:],selection_depth_interval_m=win[:])
            else:method['require_core_stronger_than_surface']=True;config['require_core_stronger_than_surface']=True
            method['currents'][owner]=config;methods.append(method);cases=[]
            for j in range(m.CASE_COUNTS[owner]//4):
                lat=76.3+j*.1 if mi==0 else 0;lon=13.5 if mi==0 else 70+j*5
                d={'id':'section-'+str(j),'entity_id':owner,'fixed_axis':axis};d.update({'latitude_degrees_north':lat,'longitude_gate_degrees_east':[13,15]} if mi==0 else {'longitude_degrees_east':lon,'latitude_gate_degrees_north':[-2,2]});method['sections'].append(d)
                for ti,stamp in enumerate(m.DATES):
                    cols=[]
                    for i in range(3):
                        r=run(3,8,25,550,[20,50],[500,600]);r['contains_original_core']=i==1
                        cols.append({'native_column_index':i,'global_longitude_index':100+i if mi==0 else 100+j,'global_latitude_index':200+j if mi==0 else 200+i,'sampled_lon_lat':[lon+i*.01,lat] if mi==0 else [lon,lat+i*.01],'status':'ORIGINAL_SEED_CONNECTED_SUPPORT','connected_depth_runs':[r]})
                    c={'entity_id':owner,'section_id':d['id'],'snapshot_time_utc':stamp,'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':axis,'cohort_id':m.COHORTS[owner],'source_operator':m.METHODS[mi],'component_bearing_degrees_true':m.OWNERS[owner],'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'synthetic-interior','original_selected_column_index':1,'original_primary_layer':copy.deepcopy(cols[1]['connected_depth_runs'][0]['threshold_layer']),'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN','depth_levels_m':[0,10,20,50,100,200,300,400,500,600],'columns':cols,'lateral_gate_censored':True}
                    if j*4+ti<m.GAPS[owner]:c.update(status='ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN',columns=[],original_selected_column_index=None,original_horizontal_selection_status='original_no_qualification',original_primary_layer=None)
                    if mi==1:c.update(geometry_adapter='ORIGINAL_RELATIVE_LONGITUDE_VALIDATED_THEN_IN_MEMORY_TAG_ONLY',original_subsurface_core_surface_comparison_applied=True,original_positive_surface_speed_gate_applied=False,original_minimum_core_minus_surface_m_s=0,original_contrast_is_uncertainty_or_physical_accuracy=False,original_selected_relative_candidate=None if c['original_selected_column_index'] is None else {'surface_reference_available':True,'surface_component_m_s':-.1,'subsurface_interval_peak_m_s':.5,'core_minus_surface_m_s':.6,'core_stronger_than_surface':True,'eligible':True,'opaque_source_note':'retain exact original candidate'})
                    cases.append(c)
            sources[owner]={'schema':'osw.'+m.COHORTS[owner]+'-velocity-depth-curtains.v1','status':'REGIONAL_MODEL_COMPONENT_THRESHOLD_GEOMETRY_NOT_PHYSICAL_CURRENT_BOTTOM','batch_current_id':owner,'source_plan_case_count':m.CASE_COUNTS[owner],'cases':cases};reviews[owner]={'entity_id':owner,'status':'ORIGINAL_SOURCE_PRIMARY_CURRENT_BATCH_RETAINED'}
        return sources,reviews,methods
    def test_all_thirty_six_cases_twenty_two_anchors_fourteen_gaps_and_immutability(self):
        sources,reviews,methods=self.fixture();saved=copy.deepcopy((sources,reviews,methods));out=m.build(sources,reviews,methods);self.assertEqual((sources,reviews,methods),saved);self.assertEqual(out['counts']['source_cases'],36);self.assertEqual(out['counts']['original_axis_proxy_anchors'],22);self.assertEqual(out['counts']['original_unresolved_cases'],14)
        self.assertEqual(out['counts_by_current']['current:spitsbergen-atlantic']['original_unresolved_cases'],9);self.assertEqual(out['counts_by_current']['current:indian-equatorial-undercurrent']['original_unresolved_cases'],5)
    def test_different_windows_choose_cores_but_do_not_cap_depth_or_thickness(self):
        out=m.build(*self.fixture())
        for r in out['cases']:
            self.assertEqual(r['source_selection_depth_interval_m'],m.WINDOWS[r['entity_id']]);a=r['original_axis_proxy_depth_anchor']
            if a is not None:self.assertEqual(a['paired_component_run']['lower_depth_m'],550);self.assertEqual(a['paired_component_run']['upper_depth_m'],25);self.assertEqual(a['paired_component_run']['thickness_m'],525);self.assertIsNone(r['physical_current_thickness_m']);self.assertIsNone(r['volume_km3'])
    def test_relative_candidate_negative_zero_and_positive_surface_copied_without_reselection(self):
        owner='current:indian-equatorial-undercurrent'
        for surface,contrast in [(-.1,.6),(0,.5),(.1,.4)]:
            sources,reviews,methods=self.fixture();c=sources[owner]['cases'][-1];candidate=c['original_selected_relative_candidate'];candidate.update(surface_component_m_s=surface,core_minus_surface_m_s=contrast);before=copy.deepcopy(candidate);r=m.build(sources,reviews,methods)['cases'][-1]
            self.assertEqual(r['original_selected_relative_candidate'],before);self.assertEqual(c['original_selected_relative_candidate'],before);self.assertIsNone(r['source_surface_component_gate_m_s']);self.assertFalse(r['original_positive_surface_speed_gate_applied']);self.assertFalse(r['original_contrast_is_uncertainty_or_physical_accuracy'])
    def test_owner_explicit_vs_global_inherited_window_and_parent_absence(self):
        out=m.build(*self.fixture())
        for r in out['cases']:
            if r['entity_id']=='current:spitsbergen-atlantic':
                self.assertEqual(r['source_identity_context'],m.SPITS_CONTEXT);self.assertIs(r['source_parent_depth_values_inherited'],False);self.assertEqual(r['source_selection_window_origin'],'original_explicit_owner_interval');self.assertTrue(all(k not in r for k in m.RELATIVE_KEYS))
            else:self.assertEqual(r['source_identity_context'],{});self.assertIsNone(r['source_parent_depth_values_inherited']);self.assertEqual(r['source_selection_window_origin'],'original_global_interval_inherited_not_owner_override')
    def test_censored_spitsbergen_bottom_retains_minimum_support_and_unknown_area(self):
        sources,reviews,methods=self.fixture();c=sources['current:spitsbergen-atlantic']['cases'][-1]
        for col in c['columns']:col['connected_depth_runs'][0]['threshold_layer'].update(lower_status='censored_before_missing_or_dry_level',lower_depth_m=None,layer_thickness_m=None)
        c['original_primary_layer']=copy.deepcopy(c['columns'][1]['connected_depth_runs'][0]['threshold_layer']);r=m.build(sources,reviews,methods)['cases'][15];p=r['original_axis_proxy_depth_anchor']['paired_component_run'];self.assertIsNone(p['thickness_m']);self.assertEqual(p['native_supported_minimum_component_span_m'],450);self.assertIsNone(r['conditional_partial_area_km2'])
    def test_exact_full_json_and_both_contextual_csv_roundtrips(self):
        import csv,io,json
        out=m.build(*self.fixture());restored=m.expand_report(json.loads(m.encode(m.compact_report(out))));self.assertEqual(m.encode(restored),m.encode(out))
        for writer in [m.csv_bytes,m.anchor_csv]:
            a=m.contextual_csv(writer,out['cases']);self.assertEqual(a,m.contextual_csv(writer,restored['cases']));rows=list(csv.DictReader(io.StringIO(a.decode())));self.assertEqual(len(rows),36)
            for r in rows:
                if r['entity_id']=='current:spitsbergen-atlantic':self.assertEqual(r['original_subsurface_core_surface_comparison_applied'],'');self.assertEqual(r['source_parent_depth_values_inherited'],'false')
                else:self.assertEqual(r['original_subsurface_core_surface_comparison_applied'],'true');self.assertEqual(r['original_positive_surface_speed_gate_applied'],'false');self.assertEqual(r['source_parent_depth_values_inherited'],'')
        rows=list(csv.DictReader(io.StringIO(m.contextual_csv(m.anchor_csv,out['cases']).decode())));self.assertEqual(rows[0]['paired_component_thickness_m'],'');self.assertIn('core_minus_surface_m_s',rows[-1]['original_selected_relative_candidate'])
    def test_rule_context_gate_date_axis_window_and_primary_mutations_rejected(self):
        indian='current:indian-equatorial-undercurrent';spits='current:spitsbergen-atlantic'
        for change in ['owner','date','frame','axis','coordinate','indices','window','ownerwindow','relative','positive','thermal','parentzero','parentinvented','metadataflag','metadatanumber','uncertainty','adapter','candidate','relativeinvented','primary','cohort','promotion']:
            sources,reviews,methods=self.fixture();c=sources[indian]['cases'][-1];sc=sources[spits]['cases'][-1]
            if change=='owner':sources[indian]['batch_current_id']=spits
            elif change=='date':c['snapshot_time_utc']='2022-01-15T00:00:00Z'
            elif change=='frame':c['component_bearing_degrees_true']=315
            elif change=='axis':c['source_geometry']='latitude'
            elif change=='coordinate':c['columns'][0]['sampled_lon_lat'][0]+=.1
            elif change=='indices':c['columns'][1]['global_latitude_index']+=1
            elif change=='window':methods[1]['selection_depth_interval_m']=[0,200]
            elif change=='ownerwindow':methods[1]['currents'][indian]['selection_depth_interval_m']=[50,200]
            elif change=='relative':methods[1]['require_core_stronger_than_surface']=False
            elif change=='positive':methods[1]['surface_component_gate_m_s']=.05
            elif change=='thermal':methods[1]['maximum_total_temperature_scalars']=1
            elif change=='parentzero':methods[0]['currents'][spits]['parent_depth_values_inherited']=0
            elif change=='parentinvented':methods[1]['currents'][indian]['parent_current_id']=None
            elif change=='metadataflag':c['original_subsurface_core_surface_comparison_applied']=False
            elif change=='metadatanumber':c['original_minimum_core_minus_surface_m_s']=False
            elif change=='uncertainty':c['original_contrast_is_uncertainty_or_physical_accuracy']=True
            elif change=='adapter':c['geometry_adapter']='different_geometry'
            elif change=='candidate':c['original_selected_relative_candidate']=None
            elif change=='relativeinvented':sc['original_subsurface_core_surface_comparison_applied']=False
            elif change=='primary':c['original_primary_layer']['lower_depth_m']=549
            elif change=='cohort':c['cohort_id']='spitsbergen-atlantic'
            else:methods[1]['eligibility']['physical_volume']=True
            with self.assertRaises((ValueError,KeyError)):m.build(sources,reviews,methods)
    def test_quarterly_dates_override_frozen_stale_january_july_prose(self):
        out=m.build(*self.fixture());self.assertEqual({r['snapshot_time_utc'] for r in out['cases']},set(m.DATES));self.assertIn('January/July',out['frozen_indian_time_scope_conflict']);self.assertTrue(all('stale' in r['source_temporal_scope_note'] for r in out['cases'] if r['entity_id']=='current:indian-equatorial-undercurrent'))
    def test_unresolved_edge_preserves_selected_relative_candidate_without_derived_axis(self):
        sources,reviews,methods=self.fixture();cases=sources['current:indian-equatorial-undercurrent']['cases'];cases[0]['original_selected_column_index']=0;cases[0]['original_horizontal_selection_status']='original_gate_edge';cases[0]['original_selected_relative_candidate']=copy.deepcopy(cases[-1]['original_selected_relative_candidate']);r=m.build(sources,reviews,methods)['cases'][16];self.assertIsNone(r['original_axis_proxy_depth_anchor']);self.assertEqual(r['original_selected_column_index'],0);self.assertEqual(r['original_selected_relative_candidate'],cases[0]['original_selected_relative_candidate']);self.assertIsNone(r['conditional_partial_area_km2'])
    def test_contextual_wrapper_preserves_every_original_csv_field_exactly(self):
        import csv,io
        out=m.build(*self.fixture())
        for writer in [m.csv_bytes,m.anchor_csv]:
            before=list(csv.DictReader(io.StringIO(writer(out['cases']).decode())));after=list(csv.DictReader(io.StringIO(m.contextual_csv(writer,out['cases']).decode())))
            for a,b in zip(before,after):self.assertEqual(a,{k:b[k] for k in a})

if __name__=='__main__':unittest.main()
