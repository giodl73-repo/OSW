"""Synthetic analytic geometry checks; never read retained ocean data."""
import copy,math,unittest
import derive_boundary_subsurface_paired_depth_v1 as m

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
        case={'entity_id':'current:pacific-north-subsurface-countercurrent','section_id':'synthetic','snapshot_time_utc':m.SEMI[0],'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':'synthetic-fixed-longitude','component_bearing_degrees_true':90,'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'synthetic-interior','original_selected_column_index':1,'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN','depth_levels_m':self.z,'columns':columns,'lateral_gate_censored':True}
        saved=copy.deepcopy(case);out=m.derive_case(case,'/cases/0','synthetic branch')
        self.assertEqual(case,saved);self.assertTrue(out['lateral_gate_censored']);self.assertIsNone(out['volume_km3']);self.assertIsNone(out['physical_current_thickness_m']);self.assertFalse(out['whole_section_area_established']);self.assertAlmostEqual(out['equivalent_paired_component_thickness_m'],20)
        case['columns'][2]['global_latitude_index']=3
        with self.assertRaises(ValueError):m.derive_case(case,'/cases/0','synthetic branch')
        case=copy.deepcopy(saved);case['component_bearing_degrees_true']=45
        with self.assertRaises(ValueError):m.derive_case(case,'/cases/0','synthetic branch')
    def test_unresolved_case_stays_null_and_long_connector_rejected(self):
        case={'entity_id':'current:pacific-north-subsurface-countercurrent','section_id':'synthetic','snapshot_time_utc':m.SEMI[0],'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':'synthetic','component_bearing_degrees_true':90,'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'unresolved','original_selected_column_index':None,'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN','columns':[]}
        out=m.derive_case(case,'/cases/0','synthetic');self.assertIsNone(out['conditional_partial_area_km2']);self.assertIsNone(out['equivalent_paired_component_thickness_m'])
        with self.assertRaises(ValueError):m.separation([0,0],[0,1])


class MixedStratumCases(unittest.TestCase):
    def fixture(self):
        groups=[('current:mauritanian','current:baffin'),('current:pacific-north-subsurface-countercurrent','current:atlantic-north-equatorial-undercurrent')]
        gaps={'current:mauritanian':6,'current:baffin':0,'current:pacific-north-subsurface-countercurrent':5,'current:atlantic-north-equatorial-undercurrent':8};methods=[];cases=[]
        for mi,owners in enumerate(groups):
            method={'snapshot_times_utc':m.QUARTERS if mi==0 else m.SEMI,'core_search_depth_interval_m':[0,200] if mi==0 else [100,400],'selection_depth_interval_m':[0,200] if mi==0 else [100,400],'eligibility':{'physical_volume':False},'maximum_nearest_latitude_distance_km':5,'maximum_nearest_longitude_distance_km':5,'currents':{},'sections':[]}
            for owner in owners:
                config={'entity_id':owner,'component_bearing_degrees_true':m.OWNERS[owner],'primary_threshold_m_s':m.THRESHOLDS[owner],'surface_component_gate_m_s':None,'temperature_gate':None,'branch_scope':'synthetic partial reach '+owner}
                if mi==0:config.update(core_search_depth_interval_m=m.WINDOWS[owner][:],selection_depth_interval_m=m.WINDOWS[owner][:])
                method['currents'][owner]=config
                for j in range(5):
                    axis=m.AXES[owner];definition={'id':'section-'+str(j),'entity_id':owner,'fixed_axis':axis,('longitude_degrees_east' if axis=='longitude' else 'latitude_degrees_north'):30+j};method['sections'].append(definition)
                    for ti,stamp in enumerate(m.OWNER_DATES[owner]):
                        columns=[]
                        for i in range(3):
                            r=run(3,5,125,350,[100,150],[300,400]);r['contains_original_core']=i==1;r['threshold_layer']['threshold_m_s']=m.THRESHOLDS[owner]
                            columns.append({'native_column_index':i,'global_longitude_index':100+j if axis=='longitude' else 100+i,'global_latitude_index':200+i if axis=='longitude' else 200+j,'sampled_lon_lat':[30+j,12+i*.01] if axis=='longitude' else [-45+i*.01,30+j],'status':'ORIGINAL_SEED_CONNECTED_SUPPORT','connected_depth_runs':[r]})
                        case={'entity_id':owner,'section_id':definition['id'],'snapshot_time_utc':stamp,'source_operator':m.METHODS[mi],'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':axis,'component_bearing_degrees_true':m.OWNERS[owner],'velocity_threshold_m_s':m.THRESHOLDS[owner],'original_horizontal_selection_status':'synthetic-interior','original_selected_column_index':1,'original_primary_layer':copy.deepcopy(columns[1]['connected_depth_runs'][0]['threshold_layer']),'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN','depth_levels_m':[0,50,100,150,200,300,400,500],'columns':columns,'lateral_gate_censored':True}
                        if j*len(m.OWNER_DATES[owner])+ti<gaps[owner]:case.update(status='ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN',columns=[],original_selected_column_index=0,original_horizontal_selection_status='synthetic_unresolved_candidate')
                        cases.append(case)
            methods.append(method)
        source={'schema':'osw.boundary-subsurface-velocity-depth-curtains.v1','status':'REGIONAL_MODEL_COMPONENT_THRESHOLD_GEOMETRY_NOT_PHYSICAL_CURRENT_BOTTOM','cases':cases};review={'status':'ALL60_ORIGINAL_CASES_PRESERVED_41_REGIONAL_CURTAINS_19_EXPLICIT_UNRESOLVED'}
        return source,review,methods
    def test_sixty_cases_four_owners_41_anchors19_gaps_source_immutable(self):
        source,review,methods=self.fixture();saved=copy.deepcopy(source);out=m.build(source,review,methods)
        self.assertEqual(source,saved);self.assertEqual(out['counts']['source_cases'],60);self.assertEqual(out['counts']['original_axis_proxy_anchors'],41);self.assertEqual(out['counts']['original_unresolved_cases'],19)
        for owner,total in m.OWNER_CASES.items():self.assertEqual(out['counts_by_current'][owner]['source_cases'],total)
        for row in out['cases']:
            self.assertIsNone(row['physical_current_thickness_m']);self.assertIsNone(row['volume_km3'])
            if row['original_axis_proxy_depth_anchor'] is None:self.assertEqual(row['columns'],[])
    def test_original_mixed_dates_and_effective_window_provenance(self):
        source,review,methods=self.fixture();out=m.build(source,review,methods)
        for row in out['cases']:
            owner=row['entity_id'];self.assertIn(row['snapshot_time_utc'],m.OWNER_DATES[owner]);self.assertEqual(row['source_selection_depth_interval_m'],m.WINDOWS[owner]);self.assertEqual(row['section_fixed_axis'],m.AXES[owner])
            self.assertEqual(row['source_selection_window_origin'],'original_owner_override' if m.AXES[owner]=='latitude' else 'original_explicit_method_default')
    def test_paired_thickness_is_lower_minus_upper_not_lower_depth(self):
        source,review,methods=self.fixture();out=m.build(source,review,methods)
        for row in out['cases']:
            if row['original_axis_proxy_depth_anchor'] is not None:
                p=row['original_axis_proxy_depth_anchor']['paired_component_run'];self.assertEqual(p['upper_depth_m'],125);self.assertEqual(p['lower_depth_m'],350);self.assertEqual(p['thickness_m'],225);self.assertEqual(p['native_supported_minimum_component_span_m'],150)
    def test_subsurface_selection_window_does_not_force_detached_primary_top(self):
        source,review,methods=self.fixture();case=next(c for c in source['cases'] if c['entity_id']=='current:pacific-north-subsurface-countercurrent' and c['columns'])
        for col in case['columns']:
            r=run(0,5,0,350,[0,50],[300,400]);r['contains_original_core']=col['native_column_index']==1;r['threshold_layer']['upper_status']='surface_bounded_layer';col['connected_depth_runs']=[r]
        case['original_primary_layer']=copy.deepcopy(case['columns'][1]['connected_depth_runs'][0]['threshold_layer'])
        out=m.build(source,review,methods);row=next(r for r in out['cases'] if r['source_descriptor_pointer']=='/cases/'+str(source['cases'].index(case)))
        self.assertEqual(row['source_selection_depth_interval_m'],[100,400]);self.assertEqual(row['original_axis_proxy_depth_anchor']['paired_component_run']['upper_depth_m'],0);self.assertEqual(row['original_axis_proxy_depth_anchor']['paired_component_run']['thickness_m'],350)
    def test_baffin_five_centimeter_cutoff_not_replaced_with_ten(self):
        source,review,methods=self.fixture();out=m.build(source,review,methods)
        self.assertEqual(out['counts_by_primary_threshold_m_s']['0.05']['source_cases'],20);self.assertEqual(out['counts_by_primary_threshold_m_s']['0.1']['source_cases'],40)
        case=next(c for c in source['cases'] if c['entity_id']=='current:baffin');case['columns'][1]['connected_depth_runs'][0]['threshold_layer']['threshold_m_s']=.1
        with self.assertRaises(ValueError):m.build(source,review,methods)
    def test_censored_anchor_retains_native_support_and_null_lower_boundary(self):
        source,review,methods=self.fixture();case=next(c for c in source['cases'] if c['entity_id']=='current:baffin');p=case['columns'][1]['connected_depth_runs'][0]['threshold_layer']
        p.update(lower_status='censored_before_missing_or_dry_level',lower_depth_m=None,layer_thickness_m=None);case['original_primary_layer']=copy.deepcopy(p)
        out=m.build(source,review,methods);row=next(r for r in out['cases'] if r['source_descriptor_pointer']=='/cases/'+str(source['cases'].index(case)));p=row['original_axis_proxy_depth_anchor']['paired_component_run']
        self.assertIsNone(p['lower_depth_m']);self.assertIsNone(p['thickness_m']);self.assertEqual(p['native_supported_minimum_component_span_m'],150);self.assertFalse(p['minimum_span_is_physical_current_bound'])
    def test_owner_overrides_are_explicit_and_missing_common_defaults_not_invented(self):
        source,review,methods=self.fixture();methods[0]['selection_depth_interval_m']=[0,400];out=m.build(source,review,methods)
        self.assertEqual(next(r for r in out['cases'] if r['entity_id']=='current:mauritanian')['source_selection_depth_interval_m'],[50,300])
        source,review,methods=self.fixture();methods[1].pop('selection_depth_interval_m')
        with self.assertRaises(ValueError):m.build(source,review,methods)
    def test_date_owner_gate_window_rule_file_and_primary_mutations(self):
        for change in ['missing','duplicate','owner','frame','surface','window','promotion','mixed_date','method_dates','rule','primary']:
            source,review,methods=self.fixture();case=next(c for c in source['cases'] if c['entity_id']=='current:mauritanian' and c['columns'])
            if change=='missing':source['cases'].pop()
            elif change=='duplicate':source['cases'][1]=copy.deepcopy(source['cases'][0])
            elif change=='owner':case['entity_id']='current:canary'
            elif change=='frame':case['component_bearing_degrees_true']=180
            elif change=='surface':methods[0]['currents']['current:mauritanian']['surface_component_gate_m_s']=.05
            elif change=='window':methods[1]['selection_depth_interval_m']=[0,400]
            elif change=='promotion':methods[0]['eligibility']['physical_volume']=True
            elif change=='mixed_date':case['snapshot_time_utc']=m.SEMI[0]
            elif change=='method_dates':methods[0]['snapshot_times_utc']=m.SEMI
            elif change=='rule':case['source_operator']=m.METHODS[1]
            else:case['original_primary_layer']['lower_depth_m']=351
            with self.assertRaises((ValueError,KeyError)):m.build(source,review,methods)
    def test_mixed_axis_and_native_transverse_indices_preserved(self):
        for owner in ['current:mauritanian','current:pacific-north-subsurface-countercurrent']:
            for change in ['enum','coordinate','indices']:
                source,review,methods=self.fixture();case=next(c for c in source['cases'] if c['entity_id']==owner and c['columns']);fixed=0 if m.AXES[owner]=='longitude' else 1
                if change=='enum':case['source_geometry']='latitude' if fixed==0 else 'longitude'
                elif change=='coordinate':case['columns'][0]['sampled_lon_lat'][fixed]+=.1
                else:case['columns'][1]['global_latitude_index' if fixed==0 else 'global_longitude_index']+=1
                with self.assertRaises(ValueError):m.build(source,review,methods)
    def test_lossless_expansion_both_csv_and_explicit_cutoff_window_rule_context(self):
        import csv,io,json
        source,review,methods=self.fixture();out=m.build(source,review,methods);compact=m.compact_report(out);restored=m.expand_report(json.loads(m.encode(compact)));self.assertEqual(restored,out)
        for writer in [m.csv_bytes,m.anchor_csv]:self.assertEqual(writer(restored['cases']),writer(out['cases']));self.assertEqual(len(list(csv.DictReader(io.StringIO(writer(out['cases']).decode())))),60)
        for row in csv.DictReader(io.StringIO(m.anchor_csv(out['cases']).decode())):
            self.assertEqual(float(row['velocity_threshold_m_s']),m.THRESHOLDS[row['entity_id']]);self.assertEqual(json.loads(row['source_selection_depth_interval_m']),m.WINDOWS[row['entity_id']]);self.assertIn(row['snapshot_time_utc'],m.OWNER_DATES[row['entity_id']]);self.assertIn(row['source_rule_operator_file'],m.METHODS)
            if row['status']=='ORIGINAL_AXIS_UNRESOLVED_NO_SECTION_GEOMETRY':self.assertEqual(row['lower_component_depth_m'],'');self.assertEqual(row['paired_component_thickness_m'],'')

if __name__=='__main__':unittest.main()
