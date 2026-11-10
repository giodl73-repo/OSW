"""Synthetic analytic geometry checks; never read retained ocean data."""
import copy,math,unittest
import derive_atlantic_latitude_paired_depth_v1 as m

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
        case={'entity_id':'current:florida','section_id':'synthetic','snapshot_time_utc':m.DATES[0],'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':'synthetic-fixed-longitude','component_bearing_degrees_true':0,'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'synthetic-interior','original_selected_column_index':1,'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN','depth_levels_m':self.z,'columns':columns,'lateral_gate_censored':True}
        saved=copy.deepcopy(case);out=m.derive_case(case,'/cases/0','synthetic branch')
        self.assertEqual(case,saved);self.assertTrue(out['lateral_gate_censored']);self.assertIsNone(out['volume_km3']);self.assertIsNone(out['physical_current_thickness_m']);self.assertFalse(out['whole_section_area_established']);self.assertAlmostEqual(out['equivalent_paired_component_thickness_m'],20)
        case['columns'][2]['global_longitude_index']=3
        with self.assertRaises(ValueError):m.derive_case(case,'/cases/0','synthetic branch')
        case=copy.deepcopy(saved);case['component_bearing_degrees_true']=45
        with self.assertRaises(ValueError):m.derive_case(case,'/cases/0','synthetic branch')
    def test_unresolved_case_stays_null_and_long_connector_rejected(self):
        case={'entity_id':'current:florida','section_id':'synthetic','snapshot_time_utc':m.DATES[0],'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':'synthetic','component_bearing_degrees_true':0,'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'unresolved','original_selected_column_index':None,'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN','columns':[]}
        out=m.derive_case(case,'/cases/0','synthetic');self.assertIsNone(out['conditional_partial_area_km2']);self.assertIsNone(out['equivalent_paired_component_thickness_m'])
        with self.assertRaises(ValueError):m.separation([0,0],[0,1])


class FourCurrentDepths(unittest.TestCase):
    def fixture(self):
        methods=[];cases=[]
        unresolved={'current:florida':0,'current:portugal':1,'current:irminger':0,'current:west-spitsbergen':5}
        for owners in [('current:florida','current:portugal'),('current:irminger','current:west-spitsbergen')]:
            method={'snapshot_times_utc':m.DATES,'maximum_nearest_latitude_distance_km':5,'eligibility':{'physical_volume':False},'thresholds_m_s':[.02,.05,.1,.2],'currents':{},'sections':[]}
            for owner in owners:
                method['currents'][owner]={'entity_id':owner,'component_bearing_degrees_true':m.OWNERS[owner],'primary_threshold_m_s':m.THRESHOLDS[owner],'surface_component_gate_m_s':m.SURFACE_GATES[owner],'temperature_gate':None,'branch_scope':'synthetic branch '+owner}
                for j in range(m.OWNER_CASES[owner]//2):
                    definition={'id':'section-'+str(j),'entity_id':owner,'fixed_axis':'latitude','latitude_degrees_north':20+j};method['sections'].append(definition)
                    for stamp in m.DATES:
                        columns=[]
                        for i in range(3):
                            r=run(1,2,5,25,[0,10],[20,30]);r['contains_original_core']=i==1;r['threshold_layer']['threshold_m_s']=m.THRESHOLDS[owner]
                            columns.append({'native_column_index':i,'global_longitude_index':i,'global_latitude_index':0,'sampled_lon_lat':[-45+i*.01,20+j],'status':'ORIGINAL_SEED_CONNECTED_SUPPORT','connected_depth_runs':[r]})
                        case={'entity_id':owner,'section_id':definition['id'],'snapshot_time_utc':stamp,'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':{'section_definition':definition.copy()},'component_bearing_degrees_true':m.OWNERS[owner],'velocity_threshold_m_s':m.THRESHOLDS[owner],'original_horizontal_selection_status':'synthetic-interior','original_selected_column_index':1,'original_primary_layer':copy.deepcopy(columns[1]['connected_depth_runs'][0]['threshold_layer']),'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN','depth_levels_m':[0,10,20,30,40,50],'columns':columns,'lateral_gate_censored':True}
                        if (owner=='current:west-spitsbergen' and j<5) or (owner=='current:portugal' and stamp==m.DATES[0] and j==0):case.update(status='ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN',columns=[],original_selected_column_index=0,original_horizontal_selection_status='synthetic_edge_candidate')
                        cases.append(case)
            methods.append(method)
        source={'schema':'osw.atlantic-latitude-velocity-depth-curtains.v1','status':'REGIONAL_MODEL_COMPONENT_THRESHOLD_GEOMETRY_NOT_PHYSICAL_CURRENT_BOTTOM','cases':cases}
        review={'status':'ALL48_ORIGINAL_CASES_PRESERVED_37_REGIONAL_CURTAINS_11_EXPLICIT_UNRESOLVED'}
        return source,review,methods
    def test_all_four_owners_48_cases_37_original_anchors_and_eleven_null_gaps(self):
        source,review,methods=self.fixture();saved=copy.deepcopy(source);out=m.build(source,review,methods)
        self.assertEqual(source,saved);self.assertEqual(out['counts']['source_cases'],48);self.assertEqual(out['counts']['original_unresolved_cases'],11);self.assertEqual(out['counts']['original_axis_proxy_anchors'],37)
        for owner,total in m.OWNER_CASES.items():self.assertEqual(out['counts_by_current'][owner]['source_cases'],total)
        for row in out['cases']:
            self.assertIsNone(row['physical_current_thickness_m']);self.assertIsNone(row['volume_km3']);self.assertFalse(row['physical_volume_eligible'])
            if row['original_axis_proxy_depth_anchor'] is None:self.assertEqual(row['columns'],[]);self.assertIsNotNone(row['original_primary_layer'])
            else:self.assertEqual(row['original_axis_proxy_depth_anchor']['native_column_index'],1)
    def test_censored_anchor_retains_native_minimum_span_without_a_bottom(self):
        source,review,methods=self.fixture();case=next(c for c in source['cases'] if c['columns'])
        p=case['columns'][1]['connected_depth_runs'][0]['threshold_layer'];p.update(lower_status='censored_before_missing_or_dry_level',lower_depth_m=None,layer_thickness_m=None)
        case['original_primary_layer']=copy.deepcopy(p);out=m.build(source,review,methods)
        row=next(r for r in out['cases'] if r['source_descriptor_pointer']=='/cases/'+str(source['cases'].index(case)))
        a=row['original_axis_proxy_depth_anchor']['paired_component_run']
        self.assertEqual(a['native_supported_depth_interval_m'],[10,20]);self.assertEqual(a['native_supported_minimum_component_span_m'],10)
        self.assertIsNone(a['lower_depth_m']);self.assertIsNone(a['thickness_m']);self.assertFalse(a['minimum_span_is_physical_current_bound'])
    def test_single_sample_zero_bound_is_uninformative_and_depth_not_thickness(self):
        r=run(2,2,5,25,[0,10],[20,30]);r['threshold_layer'].update(upper_status='censored_before_missing_or_dry_level',lower_status='censored_at_sample_domain_edge',upper_depth_m=None,lower_depth_m=None,layer_thickness_m=None)
        p=m.run_support(r,[0,10,20,30,40]);self.assertEqual(p['native_supported_depth_interval_m'],[20,20]);self.assertEqual(p['native_supported_minimum_component_span_m'],0);self.assertIsNone(p['thickness_m']);self.assertIn('not absence',p['minimum_span_interpretation'])
    def test_sampling_support_remains_inside_finite_pair_and_invalid_levels_rejected(self):
        r=run(1,2,5,25,[0,10],[20,30]);p=m.run_support(r,[0,10,20,30,40]);self.assertEqual(p['thickness_m'],20);self.assertEqual(p['native_supported_minimum_component_span_m'],10)
        for z in [[0,20,10,30,40],[0,10,float('nan'),30,40]]:
            with self.assertRaises(ValueError):m.run_support(r,z)
    def test_owner_frame_primary_scope_case_and_provenance_mutations_rejected(self):
        for mutation in ['missing','duplicate','owner','frame','primary','promotion','latitude','definition','wrong_cohort','date']:
            source,review,methods=self.fixture();case=next(c for c in source['cases'] if c['columns'])
            if mutation=='missing':source['cases'].pop()
            elif mutation=='duplicate':source['cases'][1]=copy.deepcopy(source['cases'][0])
            elif mutation=='owner':case['entity_id']='current:guiana'
            elif mutation=='frame':case['component_bearing_degrees_true']=315
            elif mutation=='primary':case['original_primary_layer']['lower_depth_m']=26
            elif mutation=='promotion':methods[0]['eligibility']['physical_volume']=True
            elif mutation=='latitude':case['columns'][0]['sampled_lon_lat'][1]+=.1
            elif mutation=='definition':case['source_geometry']['section_definition']['fixed_axis']='longitude'
            elif mutation=='wrong_cohort':methods.reverse()
            else:case['snapshot_time_utc']='2022-02-15T00:00:00Z'
            with self.assertRaises((ValueError,KeyError)):m.build(source,review,methods)
    def test_both_csv_tables_preserve_all_cases_and_missing_is_blank(self):
        import csv,io,json
        source,review,methods=self.fixture();out=m.build(source,review,methods);restored=json.loads(m.encode(out))
        for writer in [m.csv_bytes,m.anchor_csv]:self.assertEqual(writer(out['cases']),writer(restored['cases']));self.assertEqual(len(list(csv.DictReader(io.StringIO(writer(out['cases']).decode())))),48)
        table=list(csv.DictReader(io.StringIO(m.anchor_csv(out['cases']).decode())))
        self.assertEqual(next(r for r in table if r['status']=='ORIGINAL_AXIS_UNRESOLVED_NO_SECTION_GEOMETRY')['lower_component_depth_m'],'');self.assertEqual(next(r for r in table if r['status']=='ORIGINAL_AXIS_UNRESOLVED_NO_SECTION_GEOMETRY')['native_supported_minimum_component_span_m'],'')


    def test_shared_metadata_serialization_is_lossless_and_preserves_all_runs(self):
        source,review,methods=self.fixture();report=m.build(source,review,methods);saved=copy.deepcopy(report)
        compact=m.compact_report(report);self.assertEqual(report,saved)
        self.assertLess(len(m.encode(compact)),len(m.encode(report)));self.assertEqual(m.expand_report(__import__('json').loads(m.encode(compact))),report)
        self.assertEqual(m.csv_bytes(report['cases']),m.csv_bytes(m.expand_report(compact)['cases']))
    def test_shared_note_or_reference_mutation_rejected(self):
        source,review,methods=self.fixture();report=m.build(source,review,methods)
        compact=m.compact_report(report);compact['run_note']='different'
        with self.assertRaises(ValueError):m.expand_report(compact)
        compact=m.compact_report(report);next(m.all_report_runs(compact))['minimum_span_definition_ref']='/other'
        with self.assertRaises(ValueError):m.expand_report(compact)


    def test_portugal_two_centimeter_definition_preserved_and_cutoff_substitution_rejected(self):
        source,review,methods=self.fixture();report=m.build(source,review,methods)
        self.assertEqual(report['counts_by_primary_threshold_m_s']['0.02']['source_cases'],10)
        self.assertEqual(report['counts_by_primary_threshold_m_s']['0.1']['source_cases'],38)
        portugal=next(c for c in source['cases'] if c['entity_id']=='current:portugal' and c['columns'])
        row=next(r for r in report['cases'] if r['entity_id']=='current:portugal' and r['original_axis_proxy_depth_anchor'] is not None)
        self.assertEqual(row['velocity_threshold_m_s'],.02);self.assertEqual(row['component_bearing_degrees_true'],180)
        portugal['columns'][1]['connected_depth_runs'][0]['threshold_layer']['threshold_m_s']=.1
        with self.assertRaises(ValueError):m.build(source,review,methods)
    def test_flat_csv_carries_threshold_and_direction_for_every_owner(self):
        import csv,io
        source,review,methods=self.fixture();report=m.build(source,review,methods)
        rows=list(csv.DictReader(io.StringIO(m.anchor_csv(report['cases']).decode())))
        for row in rows:
            self.assertEqual(float(row['velocity_threshold_m_s']),m.THRESHOLDS[row['entity_id']])
            self.assertEqual(float(row['component_bearing_degrees_true']),m.OWNERS[row['entity_id']])

if __name__=='__main__':unittest.main()
