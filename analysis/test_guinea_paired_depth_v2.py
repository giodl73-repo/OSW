"""Synthetic semantic checks; no retained scientific data read."""
import copy,math,unittest
import derive_guinea_paired_depth_v2 as m

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
        case={'entity_id':'current:guinea','section_id':'synthetic','snapshot_time_utc':m.DATES[0],'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':'synthetic-fixed-longitude','component_bearing_degrees_true':90,'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'synthetic-interior','original_selected_column_index':1,'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN','depth_levels_m':self.z,'columns':columns,'lateral_gate_censored':True}
        saved=copy.deepcopy(case);out=m.derive_case(case,'/cases/0','synthetic branch')
        self.assertEqual(case,saved);self.assertTrue(out['lateral_gate_censored']);self.assertIsNone(out['volume_km3']);self.assertIsNone(out['physical_current_thickness_m']);self.assertFalse(out['whole_section_area_established']);self.assertAlmostEqual(out['equivalent_paired_component_thickness_m'],20)
        case['columns'][2]['global_latitude_index']=3
        with self.assertRaises(ValueError):m.derive_case(case,'/cases/0','synthetic branch')
        case=copy.deepcopy(saved);case['component_bearing_degrees_true']=45
        with self.assertRaises(ValueError):m.derive_case(case,'/cases/0','synthetic branch')
    def test_unresolved_case_stays_null_and_long_connector_rejected(self):
        case={'entity_id':'current:guinea','section_id':'synthetic','snapshot_time_utc':m.DATES[0],'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':'synthetic','component_bearing_degrees_true':90,'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'unresolved','original_selected_column_index':None,'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN','columns':[]}
        out=m.derive_case(case,'/cases/0','synthetic');self.assertIsNone(out['conditional_partial_area_km2']);self.assertIsNone(out['equivalent_paired_component_thickness_m'])
        with self.assertRaises(ValueError):m.separation([0,0],[0,1])

class OrderedObjectEncoding(unittest.TestCase):
    def report(self,cases):return {'schema':'osw.guinea-paired-depth.v1','header':'unchanged','cases':cases,'tail':False}
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

class GuineaCases(unittest.TestCase):
    def fixture(self):
        method={'snapshot_times_utc':m.DATES[:],'maximum_nearest_longitude_distance_km':5,'core_search_depth_interval_m':[0,200],'surface_component_gate_m_s':.05,'thresholds_m_s':[.05,.1,.2],'maximum_total_temperature_scalars':0,'maximum_total_decoded_temperature_bytes':0,'eligibility':{'physical_volume':False},'currents':{'current:guinea':{'entity_id':'current:guinea','component_bearing_degrees_true':90,'primary_threshold_m_s':.1,'surface_component_gate_m_s':.05,'temperature_gate':None,'branch_scope':'synthetic Guinea regional proxy, not undercurrent'}},'sections':[]}
        cases=[]
        for j,lon in enumerate([-8,-6,-4,-2.5,-1,0,2]):
            d={'id':'section-'+str(j),'entity_id':'current:guinea','fixed_axis':'longitude','longitude_degrees_east':lon,'latitude_gate_degrees_north':[2.5,5]};method['sections'].append(d)
            for stamp in m.DATES:
                cols=[]
                for i in range(3):
                    r=run(1,6,5,350,[0,10],[300,400]);r['contains_original_core']=i==1
                    cols.append({'native_column_index':i,'global_longitude_index':100+j,'global_latitude_index':200+i,'sampled_lon_lat':[lon,3+i*.01],'status':'ORIGINAL_SEED_CONNECTED_SUPPORT','connected_depth_runs':[r]})
                case={'entity_id':'current:guinea','section_id':d['id'],'snapshot_time_utc':stamp,'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':{'section_definition':copy.deepcopy(d),'maximum_nearest_longitude_distance_km':2,'actual_source_longitude_degrees_east':lon%360,'retrieved_hyperslab':{}},'component_bearing_degrees_true':90,'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'synthetic-interior','original_selected_column_index':1,'original_primary_layer':copy.deepcopy(cols[1]['connected_depth_runs'][0]['threshold_layer']),'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN','depth_levels_m':[0,10,20,50,100,200,300,400],'columns':cols,'lateral_gate_censored':True}
                cases.append(case)
        source={'schema':'osw.guinea-velocity-depth-curtains.v1','status':'REGIONAL_MODEL_COMPONENT_THRESHOLD_GEOMETRY_NOT_PHYSICAL_CURRENT_BOTTOM','cases':cases}
        review={'status':'ALL14_ORIGINAL_GUINEA_CASES_REPRODUCED_NATIVE_SPATIAL_DEPTH_CONTOURS_RETAINED'}
        return source,review,[method]
    def test_all_fourteen_dates_sections_original_anchors_and_immutability(self):
        source,review,methods=self.fixture();saved=copy.deepcopy((source,review,methods));out=m.build(source,review,methods)
        self.assertEqual((source,review,methods),saved);self.assertEqual(out['counts']['source_cases'],14);self.assertEqual(out['counts']['original_axis_proxy_anchors'],14)
        self.assertTrue(all(r['source_geometry']==c['source_geometry'] for r,c in zip(out['cases'],source['cases'])))
    def test_selection_window_and_literature_upper_fifty_do_not_cap_layer(self):
        out=m.build(*self.fixture())
        for r in out['cases']:
            p=r['original_axis_proxy_depth_anchor']['paired_component_run'];self.assertEqual(p['upper_depth_m'],5);self.assertEqual(p['lower_depth_m'],350);self.assertEqual(p['thickness_m'],345);self.assertNotEqual(p['thickness_m'],p['lower_depth_m']);self.assertEqual(r['source_selection_depth_interval_m'],[0,200]);self.assertEqual(r['source_selection_window_origin'],'original_global_interval_inherited_not_owner_override')
    def test_surface_gate_applies_to_original_selection_not_every_run(self):
        out=m.build(*self.fixture());self.assertTrue(all(r['source_surface_component_gate_m_s']==.05 for r in out['cases']))
        self.assertTrue(all(r['original_axis_proxy_depth_anchor']['paired_component_run']['upper_depth_m']>0 for r in out['cases']))
    def test_parent_context_stays_undeclared_and_physical_values_unknown(self):
        out=m.build(*self.fixture())
        for r in out['cases']:
            self.assertEqual(r['source_identity_context'],{});self.assertIsNone(r['source_parent_depth_values_inherited']);self.assertIsNone(r['source_parent_current_id']);self.assertIsNone(r['physical_current_thickness_m']);self.assertIsNone(r['volume_km3']);self.assertFalse(r['whole_section_area_established']);self.assertFalse(r['physical_volume_eligible'])
    def test_top_bottom_censoring_retains_minimum_support(self):
        source,review,methods=self.fixture();c=source['cases'][0]
        for col in c['columns']:col['connected_depth_runs'][0]['threshold_layer'].update(lower_status='censored_at_sample_domain_edge',lower_depth_m=None,layer_thickness_m=None)
        c['original_primary_layer']=copy.deepcopy(c['columns'][1]['connected_depth_runs'][0]['threshold_layer']);out=m.build(source,review,methods);a=out['cases'][0]['original_axis_proxy_depth_anchor']['paired_component_run'];self.assertIsNone(a['thickness_m']);self.assertEqual(a['native_supported_minimum_component_span_m'],290);self.assertIsNone(out['cases'][0]['conditional_partial_area_km2'])
    def test_exact_json_and_both_csv_roundtrips(self):
        import csv,io,json
        out=m.build(*self.fixture());restored=m.expand_report(json.loads(m.encode(m.compact_report(out))));self.assertEqual(m.encode(restored),m.encode(out))
        for writer in [m.csv_bytes,m.anchor_csv]:
            self.assertEqual(writer(out['cases']),writer(restored['cases']));rows=list(csv.DictReader(io.StringIO(writer(out['cases']).decode())));self.assertEqual(len(rows),14)
            for r in rows:self.assertEqual(r['source_fixed_axis'],'longitude');self.assertEqual(r['source_surface_component_gate_m_s'],'0.05');self.assertEqual(r['source_parent_depth_values_inherited'],'')
    def test_original_frame_gate_window_scope_and_candidate_mutations_fail(self):
        for change in ['missing','duplicate','owner','frame','cutoff','surface','window','date','promotion','axis','coordinate','indices','temperature','classification','primary','parent','owner_window','definition','tolerance']:
            source,review,methods=self.fixture();c=source['cases'][0];method=methods[0];config=method['currents']['current:guinea']
            if change=='missing':source['cases'].pop()
            elif change=='duplicate':source['cases'][1]=copy.deepcopy(c)
            elif change=='owner':c['entity_id']='current:guinea-undercurrent'
            elif change=='frame':c['component_bearing_degrees_true']=270
            elif change=='cutoff':config['primary_threshold_m_s']=.05
            elif change=='surface':method['surface_component_gate_m_s']=None
            elif change=='window':method['core_search_depth_interval_m']=[0,50]
            elif change=='date':c['snapshot_time_utc']='2022-06-15T00:00:00Z'
            elif change=='promotion':method['eligibility']['physical_volume']=True
            elif change=='axis':c['source_geometry']='longitude'
            elif change=='coordinate':c['columns'][0]['sampled_lon_lat'][0]+=.1
            elif change=='indices':c['columns'][1]['global_latitude_index']+=1
            elif change=='temperature':method['maximum_total_temperature_scalars']=1
            elif change=='classification':c['water_mass_classification_performed']=True
            elif change=='primary':c['original_primary_layer']['lower_depth_m']=349
            elif change=='parent':config['parent_depth_values_inherited']=False
            elif change=='owner_window':config['selection_depth_interval_m']=[0,200]
            elif change=='definition':c['source_geometry']['section_definition']['latitude_gate_degrees_north']=[0,6]
            else:c['source_geometry']['maximum_nearest_longitude_distance_km']=6
            with self.assertRaises((ValueError,KeyError)):m.build(source,review,methods)
    def test_single_level_minimum_zero_is_uninformative(self):
        r=run(1,1,5,15,[0,10],[10,20]);r['threshold_layer'].update(lower_status='censored_at_sample_domain_edge',lower_depth_m=None,layer_thickness_m=None);p=m.run_support(r,[0,10,20]);self.assertEqual(p['native_supported_minimum_component_span_m'],0);self.assertIsNone(p['thickness_m']);self.assertFalse(p['minimum_span_is_physical_current_bound'])

class CoordinateReceipts(unittest.TestCase):
    def test_measured_offset_is_not_operator_tolerance_and_native_longitudes_wrap(self):
        for distance in [0,2,5]:
            source,review,methods=GuineaCases().fixture()
            for c in source['cases']:c['source_geometry']['maximum_nearest_longitude_distance_km']=distance
            out=m.build(source,review,methods);self.assertEqual(len(out['cases']),14)
            self.assertEqual(out['cases'][0]['source_geometry']['actual_source_longitude_degrees_east'],352)
    def test_bad_measurement_and_wrong_native_longitude_fail(self):
        for value in [None,-1,5.01,float('nan')]:
            source,review,methods=GuineaCases().fixture();source['cases'][0]['source_geometry']['maximum_nearest_longitude_distance_km']=value
            with self.assertRaises(ValueError):m.build(source,review,methods)
        source,review,methods=GuineaCases().fixture();source['cases'][0]['source_geometry']['actual_source_longitude_degrees_east']=351
        with self.assertRaises(ValueError):m.build(source,review,methods)

if __name__=='__main__':unittest.main()
