"""Synthetic terrain comparisons; no real provider requests or ocean files."""
import copy,json,unittest,urllib.parse
import numpy as np
import screen_makassar_depth_surfaces_etopo_v1 as m

def patch():
    points=[[118.,-2.],[118.08,-2.],[118.08,-1.92],[118.,-1.92]]
    return {'id':'synthetic','segment_id':'synthetic-segment','snapshot_time_utc':'synthetic-time','source_pointer':'/synthetic','bbox':[118.,-2.,118.08,-1.92],'corners':[{'lon_lat':p,'upper_depth_m':10.,'lower_depth_m':50.} for p in points],'original_conditional_volume_km3':3.,'original_sampling_volume_scenarios_km3':[2.,4.]}

class CoarseTerrainSemantics(unittest.TestCase):
    def setUp(self):
        self.p=patch();self.grid={'bbox':[118.,-2.,118.08,-1.92],'width':2,'height':2};self.nodes=[[(0,0),(0,1),(1,0),(1,1)]]
    def assess(self,value,mask=False):return m.assess([self.p],self.grid,self.nodes,np.full((2,2),value,dtype='float32'),np.full((2,2),mask,dtype=bool))[0]
    def test_bilinear_surface_and_no_extrapolation(self):
        for c,lower in zip(self.p['corners'],[30.,50.,70.,50.]):c['lower_depth_m']=lower
        self.assertAlmostEqual(m.interpolated_depth(self.p,118.04,-1.96,'lower_depth_m'),50.)
        with self.assertRaises(ValueError):m.interpolated_depth(self.p,119.,-1.96,'lower_depth_m')
    def test_persistent_bed_conflict_is_not_clipped_or_promoted(self):
        before=copy.deepcopy(self.p);r=self.assess(-10)
        self.assertEqual(r['status'],'SAMPLED_CONFLICT_AT_ALL_TESTED_OFFSETS');self.assertTrue(all(s['lower_surface_below_grid_bed_samples']==4 for s in r['scenarios']))
        self.assertEqual(self.p,before);self.assertEqual(r['original_conditional_volume_km3'],3.);self.assertFalse(r['current_boundary_clipped_to_bed']);self.assertFalse(r['physical_volume_eligible']);self.assertFalse(r['terrain_clearance_established'])
    def test_offset_sign_and_sensitivity_are_not_uncertainty(self):
        r=self.assess(-40)
        self.assertEqual(r['status'],'OFFSET_SENSITIVE_SAMPLED_CONFLICT')
        self.assertEqual([s['lower_surface_below_grid_bed_samples'] for s in r['scenarios']],[4,4,0])
        self.assertGreater(r['scenarios'][0]['maximum_lower_surface_minus_grid_water_depth_m'],r['scenarios'][2]['maximum_lower_surface_minus_grid_water_depth_m'])
    def test_no_sampled_conflict_does_not_validate_between_sample_terrain(self):
        r=self.assess(-200);self.assertEqual(r['status'],'NO_SAMPLED_CONFLICT_NOT_TERRAIN_VALIDATION');self.assertFalse(r['terrain_clearance_established']);self.assertFalse(r['physical_volume_eligible'])
    def test_nodata_is_unknown_and_nonnegative_elevation_explicit(self):
        r=self.assess(-200,True);self.assertEqual(r['status'],'NO_FINITE_TERRAIN_SAMPLES_UNKNOWN');self.assertEqual(r['finite_sample_count'],0);self.assertTrue(all(s['maximum_lower_surface_minus_grid_water_depth_m'] is None for s in r['scenarios']))
        r=self.assess(10);self.assertEqual(r['nonnegative_elevation_samples'],4);self.assertEqual([s['nonpositive_water_column_samples'] for s in r['scenarios']],[4,4,0])
    def test_grid_and_comparison_caps_are_prospective_without_resolution_retuning(self):
        grid,nodes=m.plan_grid([self.p]);self.assertEqual(grid['step_degrees'],.04);self.assertGreater(grid['reserved_terrain_values'],0);self.assertEqual(grid['comparison_node_occurrences'],sum(map(len,nodes)))
        p=patch();p['bbox']=[110.,-20.,130.,0.]
        with self.assertRaises(ValueError):m.plan_grid([p])
        with self.assertRaises(ValueError):m.plan_grid([patch() for _ in range(2000)])
    def test_exact_etopo_metadata_selection_and_truncation_fail_closed(self):
        a={'OBJECTID':1,'Name':'ETOPO_2022_v1_15s_bed_elev','ProductName':'ETOPO2022','CellsizeArcseconds':15};b=dict(a,OBJECTID=2,Name='ETOPO_2022_v1_15s_surface_elev')
        self.assertEqual(m.selected_rasters({'features':[{'attributes':b},{'attributes':a}]}),[a])
        for metadata in [{'features':[]},{'features':[{'attributes':a}],'exceededTransferLimit':True},{'features':[{'attributes':dict(a,Name='other',ProductName='GEBCO2024',CellsizeArcseconds=30)}]}]:
            with self.assertRaises(ValueError):m.selected_rasters(metadata)
    def test_export_url_locks_rasters_numeric_pixels_and_no_rendering(self):
        grid={'bbox':[118.,-2.,118.08,-1.92],'width':2,'height':2};url=m.image_url(grid,[{'OBJECTID':42}]);p=urllib.parse.urlsplit(url);q=urllib.parse.parse_qs(p.query)
        self.assertEqual(p.scheme,'https');self.assertEqual(q['pixelType'],['F32']);self.assertEqual(q['format'],['tiff']);self.assertEqual(q['interpolation'],['RSP_NearestNeighbor']);self.assertEqual(json.loads(q['mosaicRule'][0])['lockRasterIds'],[42]);self.assertEqual(json.loads(q['renderingRule'][0]),{'rasterFunction':'None'})

if __name__=='__main__':unittest.main()
