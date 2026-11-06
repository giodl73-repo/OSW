import copy,json,math,unittest
from derive_north_brazil_reference_solids_v1 import integrate,links,possible_overlap,between,build,DATES,RADIUS_M

def run(upper=0,lower=100,indices=None):
    return {'upper_depth_m':upper,'lower_depth_m':lower,'thickness_m':lower-upper if upper is not None and lower is not None else None,
        'sampling_thickness_bounds_m':[max(0,lower-upper-20),lower-upper+20] if upper is not None and lower is not None else None,
        'native_depth_indices_inclusive':[0,1] if indices is None else indices,'contains_original_core':True,'upper_status':'surface_bounded_layer' if upper==0 else 'adjacent_isotach_crossing','lower_status':'adjacent_isotach_crossing' if lower is not None else 'censored'}

def row(name,lat,date=DATES[0],runs=None,patches=None,lons=None):
    runs=[run()] if runs is None else runs;lons=[10,10.08] if lons is None else lons
    patches=[{'left_run_index':i,'right_run_index':i} for i,r in enumerate(runs) if r['thickness_m'] is not None] if patches is None else patches
    return {'entity_id':'current:north-brazil','section_id':name,'snapshot_time_utc':date,'component_bearing_degrees_true':315,'velocity_threshold_m_s':.1,
        'whole_section_area_established':False,'physical_volume_eligible':False,'whole_route_depth_eligible':False,'named_current_axis_independently_validated':False,'physical_current_thickness_m':None,'volume_km3':None,
        'columns':[{'native_column_index':i,'sampled_lon_lat':[lon,lat],'runs':copy.deepcopy(runs)} for i,lon in enumerate(lons)],
        'strips':[{'left_column_index':i,'right_column_index':i+1,'distance_m':9000,'patches':copy.deepcopy(patches)} for i in range(len(lons)-1)]}

class ReferenceSolidTests(unittest.TestCase):
    def test_constant_depth_spherical_integral_and_units(self):
        r=integrate(10,10.08,-1,1,[run() for _ in range(4)])
        expected=RADIUS_M**2*math.radians(.08)*(math.sin(math.radians(1))-math.sin(math.radians(-1)))*100/1e9
        self.assertAlmostEqual(r['reference_solid_volume_km3'],expected,places=8);self.assertEqual(r['mean_reference_component_thickness_m'],100)
        self.assertAlmostEqual(r['sampling_bracket_reference_volume_bounds_km3'][0],expected*.8,places=8)
    def test_bilinear_depth_and_latitude_metric_quadrature(self):
        runs=[run(20,v+20) for v in [20,40,60,80]];r=integrate(10,10.08,0,1,runs)
        self.assertEqual(r['mean_reference_component_thickness_m'],50);self.assertAlmostEqual(r['reference_solid_volume_km3'],r['horizontal_reference_cell_area_km2']*.05)
    def test_coordinate_or_censor_rejection_before_volume(self):
        for args in [(10.08,10,0,1),(10,11,0,1),(10,10.08,1,0),(10,10.08,0,4)]:
            with self.subTest(args=args),self.assertRaises(ValueError):integrate(*args,[run() for _ in range(4)])
        with self.assertRaises(ValueError):integrate(10,10.08,0,1,[run(),run(),run(),run(0,None)])
    def test_unique_interval_links_and_conservative_unknown_boundary(self):
        self.assertEqual(links([run(0,50)],[run(10,60)]),{0:0})
        self.assertEqual(links([run(0,50)],[run(0,30),run(35,60,indices=[2,3])]),{})
        self.assertTrue(possible_overlap(run(0,None),run(200,300)))
        self.assertFalse(possible_overlap(run(0,50),run(50,100)))
    def test_matching_four_corners_produce_partial_reference_only(self):
        a,b=row('a',0),row('b',1);before=copy.deepcopy([a,b]);r=between(a,b,0,1)
        self.assertEqual(len(r['cells']),1);self.assertGreater(r['partial_reference_solid_volume_km3'],0);self.assertIsNone(r['physical_water_volume_km3']);self.assertIsNone(r['whole_current_volume_km3']);self.assertFalse(r['partial_reference_volume_is_bound_on_physical_current_volume']);self.assertEqual([a,b],before)
    def test_unmatched_longitude_faces_stay_unknown_not_zero(self):
        r=between(row('a',0),row('b',1,lons=[10.08,10.16]),0,1)
        self.assertEqual(len(r['cells']),0);self.assertIsNone(r['partial_reference_solid_volume_km3']);self.assertTrue(all(c['reference_volume_km3'] is None for c in r['unknown_reference_cells']))
    def test_ambiguous_or_censored_cross_section_link_not_filled(self):
        for runs in [[run(0,30),run(35,100,indices=[2,3])],[run(0,None)]]:
            r=between(row('a',0),row('b',1,runs=runs),0,1);self.assertFalse(r['cells']);self.assertIsNone(r['partial_reference_solid_volume_km3'])
    def test_dates_owner_frame_and_physical_flags_cannot_mix(self):
        for changes in [{'snapshot_time_utc':DATES[1]},{'entity_id':'current:guiana'},{'component_bearing_degrees_true':0},{'velocity_threshold_m_s':.05},{'physical_volume_eligible':True},{'whole_section_area_established':True}]:
            b=row('b',1);b.update(changes)
            with self.subTest(changes=changes),self.assertRaises(ValueError):between(row('a',0),b,0,1)
    def test_source_native_adjacency_and_duplicate_patch_rejected(self):
        b=row('b',1);b['strips'][0]['right_column_index']=2
        with self.assertRaises(ValueError):between(row('a',0),b,0,1)
        b=row('b',1);b['strips'][0]['patches']*=2
        with self.assertRaises(ValueError):between(row('a',0),b,0,1)
    def test_all_fourteen_source_cases_and_two_dates_preserved(self):
        latitudes=[-5,-3,-1,.5,2,4,7];sections=[{'id':'s'+str(i),'latitude_degrees_north':lat} for i,lat in enumerate(latitudes)]
        source={'schema':'osw.north-brazil-paired-depth-geometry.v1','runtime_changed':False,'full_goal_complete':False,'cases':[row(s['id'],s['latitude_degrees_north'],t) for t in DATES for s in sections]}
        method={'entity_id':'current:north-brazil','component_bearing_degrees_true':315,'primary_threshold_m_s':.1,'snapshot_times_utc':DATES,'eligibility':{'physical_volume':False},'sections':sections}
        review={'status':'PASS_ALL14_PAIRED_COMPONENT_SECTIONS_AND_ORIGINAL_DEPTH_ANCHORS_RETAINED'};before=copy.deepcopy(source);r=build(source,method,review)
        self.assertEqual(r['counts']['source_cases'],14);self.assertEqual(r['counts']['declared_neighbor_section_date_pairs'],12);self.assertEqual(r['counts']['accepted_reference_solids'],12);self.assertEqual([v['snapshot_time_utc'] for v in r['by_date']],DATES);self.assertFalse(r['physical_volume_eligible']);self.assertEqual(source,before);self.assertEqual(json.loads(json.dumps(r)),r)
        source['cases'].pop()
        with self.assertRaises(ValueError):build(source,method,review)
    def test_no_face_support_yields_unknown_no_solid(self):
        r=between(row('a',0,patches=[]),row('b',1,patches=[]),0,1);self.assertFalse(r['cells']);self.assertIsNone(r['partial_reference_solid_volume_km3']);self.assertEqual(r['unknown_reference_cells'][0]['reason'],'NO_FINITE_PAIRED_FACE_PATCHES_UNKNOWN_NOT_ZERO')

if __name__=='__main__':unittest.main()
