"""Synthetic analytic geometry checks; never read retained ocean data."""
import copy,math,unittest
import derive_caribbean_azores_paired_depth_v1 as m

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
        case={'entity_id':'current:azores','section_id':'synthetic','snapshot_time_utc':m.DATES[0],'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':'synthetic-fixed-longitude','component_bearing_degrees_true':90,'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'synthetic-interior','original_selected_column_index':1,'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN','depth_levels_m':self.z,'columns':columns,'lateral_gate_censored':True}
        saved=copy.deepcopy(case);out=m.derive_case(case,'/cases/0','synthetic branch')
        self.assertEqual(case,saved);self.assertTrue(out['lateral_gate_censored']);self.assertIsNone(out['volume_km3']);self.assertIsNone(out['physical_current_thickness_m']);self.assertFalse(out['whole_section_area_established']);self.assertAlmostEqual(out['equivalent_paired_component_thickness_m'],20)
        case['columns'][2]['global_latitude_index']=3
        with self.assertRaises(ValueError):m.derive_case(case,'/cases/0','synthetic branch')
        case=copy.deepcopy(saved);case['component_bearing_degrees_true']=45
        with self.assertRaises(ValueError):m.derive_case(case,'/cases/0','synthetic branch')
    def test_unresolved_case_stays_null_and_long_connector_rejected(self):
        case={'entity_id':'current:azores','section_id':'synthetic','snapshot_time_utc':m.DATES[0],'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':'synthetic','component_bearing_degrees_true':90,'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'unresolved','original_selected_column_index':None,'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN','columns':[]}
        out=m.derive_case(case,'/cases/0','synthetic');self.assertIsNone(out['conditional_partial_area_km2']);self.assertIsNone(out['equivalent_paired_component_thickness_m'])
        with self.assertRaises(ValueError):m.separation([0,0],[0,1])


class FullLegacyLongitudeCases(unittest.TestCase):
    def fixture(self):
        method={'snapshot_times_utc':m.DATES,'maximum_nearest_longitude_distance_km':5,'core_search_depth_interval_m':[0,200],'surface_component_gate_m_s':.05,'eligibility':{'physical_volume':False},'currents':{},'sections':[]};cases=[]
        for owner in m.OWNERS:
            method['currents'][owner]={'entity_id':owner,'component_bearing_degrees_true':m.OWNERS[owner],'primary_threshold_m_s':.1,'surface_component_gate_m_s':.05,'temperature_gate':None,'branch_scope':'synthetic partial reach '+owner}
            for j in range(5):
                definition={'id':'section-'+str(j),'entity_id':owner,'fixed_axis':'longitude','longitude_degrees_east':-60+j,'latitude_gate_degrees_north':[12,16.5]};method['sections'].append(definition)
                for stamp in m.DATES:
                    columns=[]
                    for i in range(3):
                        r=run(1,2,5,25,[0,10],[20,30]);r['contains_original_core']=i==1
                        columns.append({'native_column_index':i,'global_longitude_index':100+j,'global_latitude_index':200+i,'sampled_lon_lat':[-60+j,12+i*.01],'status':'ORIGINAL_SEED_CONNECTED_SUPPORT','connected_depth_runs':[r]})
                    case={'entity_id':owner,'section_id':definition['id'],'snapshot_time_utc':stamp,'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':{'section_definition':definition.copy(),'actual_source_longitude_degrees_east':300+j,'maximum_nearest_longitude_distance_km':0,'retrieved_hyperslab':{'synthetic':'retained'}},'component_bearing_degrees_true':m.OWNERS[owner],'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'synthetic-interior','original_selected_column_index':1,'original_primary_layer':copy.deepcopy(columns[1]['connected_depth_runs'][0]['threshold_layer']),'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'native_surface_seed_connected':False,'status':'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN','depth_levels_m':[0,10,20,30,40,50],'columns':columns,'lateral_gate_censored':True}
                    if owner=='current:caribbean' and j==0 and stamp==m.DATES[0]:case.update(status='ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN',columns=[],original_selected_column_index=0,original_horizontal_selection_status='synthetic_gate_edge')
                    cases.append(case)
        source={'schema':'osw.caribbean-azores-velocity-depth-curtains.v1','status':'REGIONAL_MODEL_COMPONENT_THRESHOLD_GEOMETRY_NOT_PHYSICAL_CURRENT_BOTTOM','cases':cases};review={'status':'ALL20_ORIGINAL_CASES_PRESERVED_19_REGIONAL_CURTAINS_1_EXPLICIT_UNRESOLVED'}
        return source,review,[method]
    def test_twenty_cases_nineteen_original_anchors_and_one_null_gap_without_mutation(self):
        source,review,methods=self.fixture();saved=copy.deepcopy(source);out=m.build(source,review,methods)
        self.assertEqual(source,saved);self.assertEqual(out['counts']['source_cases'],20);self.assertEqual(out['counts']['original_axis_proxy_anchors'],19);self.assertEqual(out['counts']['original_unresolved_cases'],1)
        for owner in m.OWNERS:self.assertEqual(out['counts_by_current'][owner]['source_cases'],10)
        gap=out['cases'][0];self.assertIsNone(gap['original_axis_proxy_depth_anchor']);self.assertIsNotNone(gap['original_primary_layer']);self.assertEqual(gap['columns'],[]);self.assertIn('not constructed',gap['source_surface_connectivity_interpretation'])
    def test_surface_selection_gate_never_forces_primary_top_to_zero(self):
        source,review,methods=self.fixture();out=m.build(source,review,methods)
        for row in out['cases']:
            self.assertEqual(row['source_surface_component_gate_m_s'],.05);self.assertEqual(row['source_selection_depth_interval_m'],[0,200]);self.assertIsNone(row['physical_current_thickness_m']);self.assertIsNone(row['volume_km3'])
            a=row['original_axis_proxy_depth_anchor']
            if a is not None:self.assertEqual(a['paired_component_run']['upper_depth_m'],5);self.assertFalse(row['source_native_surface_seed_connected'])
    def test_censored_selected_anchor_keeps_native_minimum_without_replacement(self):
        source,review,methods=self.fixture();case=next(c for c in source['cases'] if c['columns']);layer=case['columns'][1]['connected_depth_runs'][0]['threshold_layer']
        layer.update(lower_status='censored_at_sample_domain_edge',lower_depth_m=None,layer_thickness_m=None);case['original_primary_layer']=copy.deepcopy(layer)
        out=m.build(source,review,methods);row=next(r for r in out['cases'] if r['source_descriptor_pointer']=='/cases/'+str(source['cases'].index(case)))
        a=row['original_axis_proxy_depth_anchor'];self.assertEqual(a['native_column_index'],1);self.assertIsNone(a['paired_component_run']['thickness_m']);self.assertIsNone(a['paired_component_run']['lower_depth_m']);self.assertEqual(a['paired_component_run']['native_supported_minimum_component_span_m'],10)
    def test_native_minimum_is_not_surface_depth_or_zero_absence(self):
        r=run(2,2,5,25,[0,10],[20,30]);r['threshold_layer'].update(upper_status='censored_before_missing_or_dry_level',lower_status='censored_at_sample_domain_edge',upper_depth_m=None,lower_depth_m=None,layer_thickness_m=None)
        p=m.run_support(r,[0,10,20,30,40]);self.assertEqual(p['native_supported_depth_interval_m'],[20,20]);self.assertEqual(p['native_supported_minimum_component_span_m'],0);self.assertIsNone(p['thickness_m']);self.assertFalse(p['minimum_span_is_physical_current_bound']);self.assertIn('not absence',p['minimum_span_interpretation'])
    def test_source_owner_gates_time_case_and_primary_mutations_rejected(self):
        for change in ['missing','duplicate','owner','frame','cutoff','gate','window','promotion','date','primary']:
            source,review,methods=self.fixture();case=next(c for c in source['cases'] if c['columns'])
            if change=='missing':source['cases'].pop()
            elif change=='duplicate':source['cases'][1]=copy.deepcopy(source['cases'][0])
            elif change=='owner':case['entity_id']='current:antilles'
            elif change=='frame':case['component_bearing_degrees_true']=0
            elif change=='cutoff':case['columns'][1]['connected_depth_runs'][0]['threshold_layer']['threshold_m_s']=.05
            elif change=='gate':methods[0]['surface_component_gate_m_s']=0
            elif change=='window':methods[0]['core_search_depth_interval_m']=[0,500]
            elif change=='promotion':methods[0]['eligibility']['physical_volume']=True
            elif change=='date':case['snapshot_time_utc']='2022-06-15T00:00:00Z'
            else:case['original_primary_layer']['lower_depth_m']=26
            with self.assertRaises((ValueError,KeyError)):m.build(source,review,methods)
    def test_longitude_receipt_wrapping_definition_and_native_adjacency_mutations(self):
        for change in ['tag','definition','native','receipt','target','indices','missing_column']:
            source,review,methods=self.fixture();case=next(c for c in source['cases'] if c['columns'])
            if change=='tag':case['source_geometry']='longitude'
            elif change=='definition':case['source_geometry']['section_definition']['fixed_axis']='latitude'
            elif change=='native':case['source_geometry']['actual_source_longitude_degrees_east']+=1
            elif change=='receipt':case['source_geometry']['maximum_nearest_longitude_distance_km']=6
            elif change=='target':case['columns'][0]['sampled_lon_lat'][0]+=.1
            elif change=='indices':case['columns'][1]['global_latitude_index']+=1
            else:case['columns'].pop()
            with self.assertRaises(ValueError):m.build(source,review,methods)
    def test_lossless_shared_note_preserves_full_dictionary_and_both_csv_bytes(self):
        import csv,io,json
        source,review,methods=self.fixture();report=m.build(source,review,methods);compact=m.compact_report(report);restored=m.expand_report(json.loads(m.encode(compact)))
        self.assertEqual(restored,report);self.assertLess(len(m.encode(compact)),len(m.encode(report)))
        for writer in [m.csv_bytes,m.anchor_csv]:self.assertEqual(writer(restored['cases']),writer(report['cases']));self.assertEqual(len(list(csv.DictReader(io.StringIO(writer(report['cases']).decode())))),20)
    def test_flat_csv_exposes_original_direction_and_gates_and_blank_unresolved_depths(self):
        import csv,io
        source,review,methods=self.fixture();report=m.build(source,review,methods);table=list(csv.DictReader(io.StringIO(m.anchor_csv(report['cases']).decode())))
        self.assertEqual(table[0]['upper_component_depth_m'],'');self.assertEqual(table[0]['native_supported_minimum_component_span_m'],'')
        for row in table:self.assertEqual(float(row['velocity_threshold_m_s']),.1);self.assertEqual(float(row['source_surface_component_gate_m_s']),.05);self.assertEqual(float(row['component_bearing_degrees_true']),m.OWNERS[row['entity_id']])

if __name__=='__main__':unittest.main()
