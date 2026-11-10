"""Synthetic presentation gates; no pixels or scientific source files read."""
import copy,unittest
import join_makassar_terrain_status_v1 as m

def feature(fid,sid):return {'type':'Feature','id':fid,'geometry':{'type':'Polygon','coordinates':[[[0,0],[1,0],[1,1],[0,1],[0,0]]]},'properties':{'segment_id':sid,'upper_depth_m':[10]*4,'lower_depth_m':[50]*4,'conditional_partial_component_volume_km3':3.,'physical_volume_eligible':False}}
def segment(sid,status='PARTIAL_ASSUMED_DEPTH_SURFACE_SCENARIO'):return {'id':sid,'entity_id':'synthetic','snapshot_time_utc':'synthetic-time','status':status}

class TerrainPresentationGates(unittest.TestCase):
    def test_one_conflict_withholds_entire_segment_without_hiding_patches(self):
        g={'type':'FeatureCollection','features':[feature('a','s'),feature('b','s')]};a,r=m.join(g,[{'id':'a','status':m.CLEAR},{'id':'b','status':m.CONFLICT}],[segment('s')],'synthetic-sha')
        self.assertEqual(len(a['features']),2);self.assertTrue(all(f['properties']['conditional_volume_after_terrain_gate_km3'] is None for f in a['features']));self.assertEqual(r['segments'][0]['terrain_gate_status'],'WITHHELD_SAMPLED_TERRAIN_CONFLICT')
    def test_clear_is_conditional_not_physical_validation(self):
        a,r=m.join({'type':'FeatureCollection','features':[feature('a','s')]},[{'id':'a','status':m.CLEAR}],[segment('s')],'sha')
        p=a['features'][0]['properties'];self.assertEqual(p['conditional_volume_after_terrain_gate_km3'],3.);self.assertFalse(p['physical_volume_eligible']);self.assertFalse(p['terrain_clearance_established']);self.assertEqual(r['segments'][0]['terrain_gate_status'],m.CONDITIONAL)
    def test_offset_sensitive_and_missing_terrain_withheld(self):
        for status in [m.SENSITIVE,m.UNKNOWN]:
            a,r=m.join({'type':'FeatureCollection','features':[feature('a','s')]},[{'id':'a','status':status}],[segment('s')],'sha')
            self.assertIsNone(a['features'][0]['properties']['conditional_volume_after_terrain_gate_km3']);self.assertFalse(r['segments'][0]['conditional_segment_volume_presentation_eligible'])
    def test_source_gap_stays_explicit_without_invented_features(self):
        a,r=m.join({'type':'FeatureCollection','features':[]},[],[segment('gap','UNRESOLVED_ENDPOINT_NO_DEPTH_SURFACE_SCENARIO')],'sha')
        self.assertEqual(a['features'],[]);self.assertEqual(r['segments'][0]['terrain_gate_status'],'SOURCE_GAP_NO_DEPTH_SURFACE');self.assertEqual(r['segments'][0]['source_patch_count'],0)
    def test_missing_duplicate_unknown_status_and_cross_segment_ids_rejected(self):
        g={'type':'FeatureCollection','features':[feature('a','s')]}
        for rows in [[],[{'id':'a','status':m.CLEAR},{'id':'a','status':m.CLEAR}],[{'id':'a','status':'invented'}],[{'id':'other','status':m.CLEAR}]]:
            with self.assertRaises(ValueError):m.join(g,rows,[segment('s')],'sha')
        with self.assertRaises(ValueError):m.join(g,[{'id':'a','status':m.CLEAR}],[segment('wrong')],'sha')
    def test_original_geometry_properties_and_input_objects_preserved(self):
        g={'type':'FeatureCollection','features':[feature('a','s')]};before=copy.deepcopy(g);a,r=m.join(g,[{'id':'a','status':m.CONFLICT}],[segment('s')],'sha')
        self.assertEqual(g,before);self.assertEqual(a['features'][0]['geometry'],before['features'][0]['geometry'])
        self.assertTrue(all(a['features'][0]['properties'][k]==v for k,v in before['features'][0]['properties'].items()))
        self.assertEqual(r['counts']['physical_volumes_admitted'],0)
    def test_csv_numeric_and_scenario_cells_remain_unparsed_strings(self):
        rows=m.strings_csv(b'id,status,sample_count,scenarios\na,NO_SAMPLED_CONFLICT_NOT_TERRAIN_VALIDATION,do-not-parse,{not-json}\n')
        self.assertEqual(rows[0]['sample_count'],'do-not-parse');self.assertEqual(rows[0]['scenarios'],'{not-json}')
        a,r=m.join({'type':'FeatureCollection','features':[feature('a','s')]},rows,[segment('s')],'sha');self.assertEqual(a['features'][0]['properties']['terrain_screen_status'],m.CLEAR)

if __name__=='__main__':unittest.main()
