"""Analytic synthetic surfaces, rejected joins and source preservation."""
import copy,math,unittest
import project_barents_makassar_depth_surfaces_v1 as m

def run(first=1,last=2,up=5.,down=25.):
    return {'status':'FINITE_PAIRED_COMPONENT_CONTOURS','native_depth_indices_inclusive':[first,last],'upper_depth_m':up,'lower_depth_m':down,'thickness_m':down-up,'sampling_thickness_bounds_m':[max(0,down-up-10),down-up+10]}

def case(owner='current:north-cape',slot=0,stamp=None):
    sid,value=m.CUTS[owner][slot];fixed=0 if owner=='current:north-cape' else 1
    columns=[]
    for i in range(3):
        p=[value,71+i*.01] if fixed==0 else [118+i*.01,value]
        columns.append({'native_column_index':i,'sampled_lon_lat':p,'runs':[run()]})
    return {'entity_id':owner,'section_id':sid,'snapshot_time_utc':stamp or m.DATES[0],'branch_scope':'synthetic '+owner,'source_descriptor_pointer':'/synthetic/'+sid,'component_bearing_degrees_true':m.BEARINGS[owner],'velocity_threshold_m_s':.1,'named_current_axis_independently_validated':False,'whole_section_area_established':False,'volume_km3':None,'conditional_partial_area_km2':1.,'status':'CONDITIONAL_PARTIAL_COMPONENT_SECTION_GEOMETRY','columns':columns,'strips':[{'left_column_index':i,'right_column_index':i+1,'patches':[{'left_run_index':0,'right_run_index':0}]} for i in range(2)],'lateral_gate_censored':True}

def corner(x,y,thickness=50.):
    return {'lon_lat':[x,y],'upper_depth_m':10.,'lower_depth_m':10+thickness,'thickness_m':thickness,'sampling_thickness_bounds_m':[thickness-5,thickness+5]}

class ConditionalSurfaces(unittest.TestCase):
    def test_constant_prism_volume_units_and_sampling_range(self):
        p=m.integrate_corners([corner(0,0),corner(1,0),corner(1,1),corner(0,1)])
        expected_area=m.RADIUS**2*math.radians(1)*math.sin(math.radians(1))
        self.assertAlmostEqual(p['surface_footprint_km2'],expected_area/1e6)
        self.assertAlmostEqual(p['conditional_partial_component_volume_km3'],expected_area*50/1e9)
        self.assertAlmostEqual(p['sampling_bracket_volume_scenarios_km3'][0],expected_area*45/1e9)
        self.assertAlmostEqual(p['sampling_bracket_volume_scenarios_km3'][1],expected_area*55/1e9)
    def test_affine_latitude_field_matches_independent_simpson_integral(self):
        p=m.integrate_corners([corner(20,70,30),corner(22,70,50),corner(22,71,90),corner(20,71,70)])
        lo,hi=map(math.radians,[70,71]);n=1000;step=(hi-lo)/n
        # Longitude mean thickness increases linearly40->80m; integrate against
        # cos(latitude) independently of the implementation's analytic weights.
        f=lambda phi:(40+40*(phi-lo)/(hi-lo))*math.cos(phi)
        integral=step/3*(f(lo)+f(hi)+sum((4 if i%2 else 2)*f(lo+i*step) for i in range(1,n)))
        expected=m.RADIUS**2*math.radians(2)*integral/1e9
        self.assertAlmostEqual(p['conditional_partial_component_volume_km3'],expected,places=8)
        self.assertLess(p['spherical_latitude_weights_south_north'][1],.5)
    def test_missing_endpoint_stays_null_and_unresolved_cut_cannot_be_skipped(self):
        a,b=case(),case(slot=1);b.update(status='ORIGINAL_AXIS_UNRESOLVED_NO_SECTION_GEOMETRY',columns=[],strips=[],conditional_partial_area_km2=None)
        r=m.segment(a,b,20,22);self.assertIsNone(r['conditional_partial_component_volume_km3']);self.assertEqual(r['cells'],[])
        with self.assertRaises(ValueError):m.segment(a,case(slot=2),20,24)
    def test_owner_time_branch_and_component_frame_must_match(self):
        for key,value in [('snapshot_time_utc',m.DATES[1]),('branch_scope','other'),('entity_id','current:indonesian-throughflow'),('component_bearing_degrees_true',45),('velocity_threshold_m_s',.05)]:
            a,b=case(),case(slot=1);b[key]=value
            with self.assertRaises(ValueError):m.segment(a,b,20,22)
    def test_no_common_native_level_means_no_quad_surface(self):
        a,b=case(),case(slot=1)
        for c in b['columns']:c['runs'][0]['native_depth_indices_inclusive']=[3,4]
        r=m.segment(a,b,20,22);self.assertIsNone(r['conditional_partial_component_volume_km3']);self.assertTrue(all(not c['patches'] for c in r['cells']))
    def test_between_section_split_merge_is_explicit_gap(self):
        a,b=case(),case(slot=1)
        for c in a['columns']:c['runs']=[run(1,5,5,55)]
        for c in b['columns']:c['runs']=[run(1,2,5,25),run(4,5,35,55)]
        for s in b['strips']:s['patches'].append({'left_run_index':1,'right_run_index':1})
        r=m.segment(a,b,20,22);self.assertIsNone(r['conditional_partial_component_volume_km3']);self.assertTrue(all(len(c['rejected_links'])==2 for c in r['cells']))
    def test_native_coordinates_indices_and_paired_depths_cannot_change(self):
        a,b=case(),case(slot=1);b['columns'][1]['sampled_lon_lat'][1]+=.001
        with self.assertRaises(ValueError):m.segment(a,b,20,22)
        a,b=case(),case(slot=1);b['strips'][0]['right_column_index']=2
        with self.assertRaises(ValueError):m.segment(a,b,20,22)
        a,b=case(),case(slot=1);b['columns'][0]['runs'][0]['thickness_m']=100
        with self.assertRaises(ValueError):m.segment(a,b,20,22)
    def test_full_cohort_preserved_24_slots_geojson_depth_not_altitude(self):
        cases=[case(o,i,t) for o in m.CUTS for t in m.DATES for i in range(4)]
        for c in cases[:14]:c.update(status='ORIGINAL_AXIS_UNRESOLVED_NO_SECTION_GEOMETRY',columns=[],strips=[],conditional_partial_area_km2=None)
        source={'schema':'osw.barents-makassar-conditional-section-geometry.v1','cases':cases,'source_credit':'synthetic'}
        review={'status':'PASS_EIGHTEEN_PARTIAL_COMPONENT_SECTIONS_WITH_PAIRED_DEPTHS_AND_SAMPLING_SCENARIOS','actual_complete_32_case_json_csv_roundtrip_passed':True}
        before=copy.deepcopy(source);r=m.build(source,review);g=m.geojson(r)
        self.assertEqual(source,before);self.assertEqual(len(r['segments']),24);self.assertEqual(r['counts']['source_unresolved_cases_preserved'],14)
        self.assertEqual(len(g['features']),r['counts']['conditional_depth_surface_patches']);self.assertTrue(g['features'])
        for f in g['features']:
            self.assertTrue(all(len(p)==2 for p in f['geometry']['coordinates'][0]));self.assertEqual(len(f['properties']['upper_depth_m']),4);self.assertFalse(f['properties']['physical_volume_eligible'])
        for s in r['segments']:
            self.assertIsNone(s['physical_volume_km3']);self.assertIsNone(s['annual_range_m']);self.assertFalse(s['whole_segment_volume_established']);self.assertFalse(s['global_total_eligible'])

if __name__=='__main__':unittest.main()
