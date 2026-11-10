"""Synthetic analytic geometry checks; never read retained ocean data."""
import copy,math,unittest
import derive_north_brazil_paired_depth_geometry_v1 as m

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
        case={'entity_id':'current:north-brazil','section_id':'synthetic','snapshot_time_utc':m.DATES[0],'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':'synthetic-fixed-longitude','component_bearing_degrees_true':315,'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'synthetic-interior','original_selected_column_index':1,'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN','depth_levels_m':self.z,'columns':columns,'lateral_gate_censored':True}
        saved=copy.deepcopy(case);out=m.derive_case(case,'/cases/0','synthetic branch')
        self.assertEqual(case,saved);self.assertTrue(out['lateral_gate_censored']);self.assertIsNone(out['volume_km3']);self.assertIsNone(out['physical_current_thickness_m']);self.assertFalse(out['whole_section_area_established']);self.assertAlmostEqual(out['equivalent_paired_component_thickness_m'],20)
        case['columns'][2]['global_longitude_index']=3
        with self.assertRaises(ValueError):m.derive_case(case,'/cases/0','synthetic branch')
        case=copy.deepcopy(saved);case['component_bearing_degrees_true']=45
        with self.assertRaises(ValueError):m.derive_case(case,'/cases/0','synthetic branch')
    def test_unresolved_case_stays_null_and_long_connector_rejected(self):
        case={'entity_id':'current:north-brazil','section_id':'synthetic','snapshot_time_utc':m.DATES[0],'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':'synthetic','component_bearing_degrees_true':315,'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'unresolved','original_selected_column_index':None,'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN','columns':[]}
        out=m.derive_case(case,'/cases/0','synthetic');self.assertIsNone(out['conditional_partial_area_km2']);self.assertIsNone(out['equivalent_paired_component_thickness_m'])
        with self.assertRaises(ValueError):m.separation([0,0],[0,1])

class CompleteNBCAnchors(unittest.TestCase):
    def fixture(self):
        method={'entity_id':'current:north-brazil','component_bearing_degrees_true':315,'primary_threshold_m_s':.1,'snapshot_times_utc':m.DATES,'eligibility':{'physical_volume':False},'branch_scope':'synthetic surface branch','sections':[{'id':'section-'+str(i),'latitude_degrees_north':i} for i in range(7)]}
        cases=[]
        for stamp in m.DATES:
            for definition in method['sections']:
                columns=[]
                for i in range(3):
                    r=run(1,2,5,25,[0,10],[20,30]);r['contains_original_core']=i==1
                    columns.append({'native_column_index':i,'global_longitude_index':i,'global_latitude_index':0,'sampled_lon_lat':[-45+i*.01,definition['latitude_degrees_north']],'status':'ORIGINAL_SEED_CONNECTED_SUPPORT','connected_depth_runs':[r]})
                cases.append({'entity_id':'current:north-brazil','section_id':definition['id'],'snapshot_time_utc':stamp,'source_file':'synthetic','source_sha256':'0'*64,'source_geometry':'synthetic-fixed-latitude','component_bearing_degrees_true':315,'velocity_threshold_m_s':.1,'original_horizontal_selection_status':'synthetic-interior','original_selected_column_index':1,'original_primary_layer':copy.deepcopy(columns[1]['connected_depth_runs'][0]['threshold_layer']),'native_input_column_count':3,'core_reselected':False,'named_current_axis_independently_validated':False,'water_mass_classification_performed':False,'status':'REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN','depth_levels_m':[0,10,20,30,40,50],'columns':columns,'lateral_gate_censored':True})
        source={'schema':'osw.north-brazil-velocity-depth-curtains.v1','status':'REGIONAL_MODEL_COMPONENT_THRESHOLD_GEOMETRY_NOT_PHYSICAL_CURRENT_BOTTOM','cases':cases}
        review={'status':'ORIGINAL_SOURCE_PRIMARY_CURRENT_BATCH_RETAINED'}
        return source,review,method
    def test_fourteen_original_anchors_and_source_immutable_csv_complete(self):
        source,review,method=self.fixture();saved=copy.deepcopy(source)
        out=m.build(source,review,method);self.assertEqual(source,saved);self.assertEqual(len(out['cases']),14)
        for c in out['cases']:
            anchor=c['original_axis_proxy_depth_anchor'];self.assertEqual(anchor['native_column_index'],1);self.assertEqual(anchor['paired_component_run']['thickness_m'],20)
            self.assertIsNone(anchor['physical_current_depth_m']);self.assertFalse(anchor['whole_route_interpolation_allowed'])
        self.assertEqual(m.csv_bytes(out['cases']),m.csv_bytes(__import__('json').loads(m.encode(out))['cases']))
    def test_censored_original_anchor_never_reselected(self):
        source,review,method=self.fixture();case=source['cases'][0]
        layer=case['columns'][1]['connected_depth_runs'][0]['threshold_layer']
        layer.update(lower_status='censored_before_missing_or_dry_level',lower_depth_m=None,layer_thickness_m=None)
        case['original_primary_layer']=copy.deepcopy(layer)
        out=m.build(source,review,method)['cases'][0]
        self.assertIsNone(out['original_axis_proxy_depth_anchor']['paired_component_run']['thickness_m'])
        self.assertEqual(out['original_axis_proxy_depth_anchor']['native_column_index'],1)
    def test_missing_date_duplicate_owner_frame_or_changed_primary_rejected(self):
        for mutation in ['missing','duplicate','owner','frame','primary','promote','latitude']:
            source,review,method=self.fixture()
            if mutation=='missing':source['cases'].pop()
            elif mutation=='duplicate':source['cases'][1]=copy.deepcopy(source['cases'][0])
            elif mutation=='owner':source['cases'][0]['entity_id']='current:guiana'
            elif mutation=='frame':source['cases'][0]['component_bearing_degrees_true']=0
            elif mutation=='primary':source['cases'][0]['original_primary_layer']['lower_depth_m']=26
            elif mutation=='promote':method['eligibility']['physical_volume']=True
            else:source['cases'][0]['columns'][0]['sampled_lon_lat'][1]=.1
            with self.assertRaises(ValueError):m.build(source,review,method)

if __name__=='__main__':unittest.main()
