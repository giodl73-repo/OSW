import copy,unittest
from unittest.mock import patch
import audit_north_brazil_reference_land_v1 as audit
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery

def svg(path='M0,0 L10,0 L10,10 L0,10 Z',extra='',rule='evenodd'):
    return ('<svg><metadata>Natural Earth 1:110m land SHA256 9e0729ee253ca7d7a5c4ae9395fb1902264c5377c52e224d13dd85010e2835d9</metadata><path class="land-context" fill-rule="'+rule+'" '+extra+' d="'+path+'"/></svg>').encode()

class LandScreenTests(unittest.TestCase):
    def setUp(self):self.query=DescriptorQuery(lambda v:None,prior_numeric=0,prior_bytes=0);self.budget=audit.VectorBudget(self.query)
    def test_full_svg_bytes_and_coordinates_reserved(self):
        raw=svg();rings=audit.read_mask(raw,self.budget)
        self.assertEqual(rings,[[[0,0],[10,0],[10,10],[0,10]]]);self.assertEqual(self.budget.nodes,4);self.assertEqual(self.query.ledger['reserved_numeric_tokens'],8);self.assertEqual(self.query.ledger['unique_json_bytes'],len(raw))
    def test_prospective_cap_before_any_float_conversion(self):
        self.query.numeric_cap=0
        with patch.object(audit,'float',side_effect=AssertionError('No conversion before reservation'),create=True),self.assertRaises(ValueError):audit.read_mask(svg(),self.budget)
        self.assertEqual(self.query.ledger['reserved_numeric_tokens'],0)
        self.budget.nodes=6000
        with self.assertRaises(ValueError):self.budget.reserve(nodes=1)
    def test_curve_transform_non_evenodd_or_open_ring_rejected(self):
        for raw in [svg('M0,0 C1,1 2,2 3,3 Z'),svg(extra='transform="translate(1,2)"'),svg(rule='nonzero'),svg('M0,0 L10,0 L10,10')]:
            with self.subTest(raw=raw),self.assertRaises(ValueError):audit.read_mask(raw,self.budget)
    def test_boundary_crossing_without_contained_vertices(self):
        self.assertTrue(audit.segment_box([-2,.5],[2,.5],[0,0,1,1]));self.assertFalse(audit.segment_box([-2,2],[2,2],[0,0,1,1]));self.assertTrue(audit.segment_box([0,-1],[0,2],[0,0,1,1]))
    def test_land_fill_clear_and_boundary_touch(self):
        rings=audit.read_mask(svg(),self.budget)
        self.assertEqual(audit.contact([2,2,3,3],rings),'reference_cell_corner_in_coarse_land_fill')
        self.assertEqual(audit.contact([11,2,12,3],rings),'no_contact_detected_in_coarse_display_mask')
        self.assertEqual(audit.contact([10,2,11,3],rings),'coarse_land_boundary_meets_reference_cell')
    def test_island_inside_large_cell_detected(self):
        rings=audit.read_mask(svg(),self.budget);self.assertEqual(audit.contact([-1,-1,11,11],rings),'coarse_land_boundary_meets_reference_cell')
    def test_evenodd_hole_keeps_lake_interior_unfilled(self):
        rings=audit.read_mask(svg('M0,0 L10,0 L10,10 L0,10 Z M2,2 L8,2 L8,8 L2,8 Z'),self.budget)
        self.assertFalse(audit.filled([4,4],rings));self.assertTrue(audit.filled([1,1],rings));self.assertEqual(audit.contact([3,3,4,4],rings),'no_contact_detected_in_coarse_display_mask')
    def test_projection_and_cell_nodes_are_bounded(self):
        rect=audit.rectangle([-35,-34],[0,1],self.budget)
        self.assertLess(rect[0],rect[2]);self.assertLess(rect[1],rect[3]);self.assertEqual(self.budget.nodes,4)
        with self.assertRaises(ValueError):audit.rectangle([-34,-35],[0,1],self.budget)
    def test_all_cells_source_values_and_physical_flags_preserved(self):
        source={'schema':'osw.north-brazil-reference-solids.v1','entity_id':'current:north-brazil','physical_volume_eligible':False,'whole_current_volume_km3':None,'original_physical_volume_ineligibility_preserved':True,'counts':{'accepted_reference_solids':1},
            'section_pairs':[{'snapshot_time_utc':'2022-01-15T00:00:00Z','south_section_id':'south','north_section_id':'north','actual_native_latitude_degrees_north':[0,1],'cells':[{'longitude_cell_degrees_east':[-35,-34],'reference_solid_volume_km3':12.5,'sampling_bracket_reference_volume_bounds_km3':[10,15]}]}],
            'by_date':[{'snapshot_time_utc':'2022-01-15T00:00:00Z','accepted_reference_solid_count':1}]}
        before=copy.deepcopy(source);far=[[[0,0],[1,0],[1,1],[0,1]]];report=audit.build(source,far,self.budget)
        self.assertEqual(source,before);self.assertEqual(report['counts']['source_reference_solids'],1);self.assertEqual(report['by_date'][0]['retained_after_coarse_screen_partial_reference_volume_km3'],12.5);self.assertFalse(report['land_free_ocean_support_established']);self.assertFalse(report['cells'][0]['land_free_ocean_support_established'])
        covering=[[[0,0],[1600,0],[1600,1050],[0,1050]]];report=audit.build(source,covering,self.budget)
        self.assertEqual(report['counts']['coarse_land_contact'],1);self.assertIsNone(report['by_date'][0]['retained_after_coarse_screen_partial_reference_volume_km3']);self.assertEqual(report['cells'][0]['original_reference_solid_volume_km3'],12.5)
        source['physical_volume_eligible']=True
        with self.assertRaises(ValueError):audit.build(source,far,self.budget)

if __name__=='__main__':unittest.main()
