"""Verify original cells, explicit identity/component joins and cruise scope."""
import copy
import json
import unittest
import build_current_depth_register_v4 as previous
import build_current_depth_register_v5 as depth
from build_current_depth_register_v2 import validate_reference
from build_atlantic_cruise_widths import read_cells


class AdditionalAtlanticDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.new=cls.data['evidence'][58:]
        cls.tables={i:{r['row']:r['cells'] for r in read_cells(p)} for i,p in [(1,depth.TABLE1),(2,depth.TABLE2)]}

    def test_prior_evidence_and_full_inventory_preserved(self):
        prior=previous.build()
        self.assertEqual(self.data['evidence'][:58],prior['evidence'])
        self.assertEqual({r['entity_id'] for r in self.data['records']},{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':65,'identities_with_scoped_depth_reference':25,'identities_not_yet_assessed':86,'whole_route_depth_profiles':0,'volume_estimates':0})

    def test_seven_depth_cells_and_three_current_mappings(self):
        self.assertEqual({r['table_2_row']:r['range_m'] for r in self.new},{45:[0,937],47:[0,511],48:[0,566],49:[0,592],86:[0,413],87:[0,418],88:[0,400]})
        self.assertEqual({r['entity_id'] for r in self.new},{'current:north-brazil','current:florida','current:labrador'})
        for row in self.new:depth.validate_section(row,self.tables)

    def test_layer_indices_transport_and_other_groups_are_not_depths(self):
        for field,value in [('range_m',[1,5]),('range_m',[0,17]),('raw_depth_cell','0 to 17'),('table_2_group_row',35),('entity_id','current:guiana')]:
            row=copy.deepcopy(self.new[0]);row[field]=value
            with self.assertRaises(ValueError):depth.validate_section(row,self.tables)

    def test_upper_labrador_is_not_entire_current_or_unrelated_width(self):
        row=next(r for r in self.new if r['entity_id']=='current:labrador')
        self.assertEqual(row['source_component_scope'],'upper_component_only')
        for field,value in [('source_component_scope','entire_current'),('component_promoted_to_entire_system',True),('same_source_width_reference_id','labrador-thompson-2009-regional-width')]:
            changed=copy.deepcopy(row);changed[field]=value
            with self.assertRaises(ValueError):depth.validate_section(changed,self.tables)

    def test_dates_are_whole_section_snapshots_not_decade_means(self):
        for field,value in [('observed_period',{'start':'1990-01-01','end':'1999-12-31'}),('decade_group_is_time_average',True),('section_sampling_window',{'start':'1994-04-02','end':'1994-05-07'}),('table_1_row',4),('cruise_id','different-cruise')]:
            row=copy.deepcopy(self.new[0]);row[field]=value
            with self.assertRaises(ValueError):depth.validate_section(row,self.tables)

    def test_no_rectangles_thickness_volumes_or_temporal_envelopes(self):
        rules=json.loads((depth.ROOT/depth.RULES).read_bytes());ids={r['entity_id'] for r in self.data['records']}
        for field,value in [('volume_eligible',True),('thickness_m',937),('annual_range_m',[400,937]),('uncertainty_m',10)]:
            row=copy.deepcopy(self.new[0]);row[field]=value
            with self.assertRaises(ValueError):validate_reference(row,ids,rules['metric_types'])
        for field in ['rectangle_cross_section_inferred','cross_section_area_eligible','exact_boundary_coordinates_available']:
            row=copy.deepcopy(self.new[0]);row[field]=True
            with self.assertRaises(ValueError):depth.validate_section(row,self.tables)

    def test_source_pointers_and_outputs_reproduce(self):
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        for row in self.new:
            raw=source['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual(raw,{k:row[k] for k in raw})
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),depth.csv_bytes(self.data))


if __name__=='__main__':unittest.main()
