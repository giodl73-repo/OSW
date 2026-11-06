"""Check publisher metre cells, identity joins and inverse-section scope."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v2 as previous
import build_current_depth_register_v3 as depth
from build_atlantic_cruise_widths import read_cells


class InverseSectionDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.new=cls.data['evidence'][17:]
        cls.widths={r['id']:r for r in json.loads((depth.ROOT/depth.WIDTHS).read_bytes())['measurements']}
        cls.tables={1:{r['row']:r['cells'] for r in read_cells(depth.TABLE1)},2:{r['row']:r['cells'] for r in read_cells(depth.TABLE2)}}

    def test_complete_inventory_and_all_previous_references_preserved(self):
        prior=previous.build()
        self.assertEqual(self.data['evidence'][:17],prior['evidence'])
        self.assertEqual({r['entity_id'] for r in self.data['records']},{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':52,'identities_with_scoped_depth_reference':18,'identities_not_yet_assessed':93,'whole_route_depth_profiles':0,'volume_estimates':0})

    def test_all_35_source_rows_and_ten_identity_joins_verified(self):
        expected=[r for r in self.widths.values() if r.get('hydrographic_section_context')]
        self.assertEqual({r['same_source_width_reference_id'] for r in self.new},{r['id'] for r in expected})
        self.assertEqual(len(self.new),35);self.assertEqual(len({r['entity_id'] for r in self.new}),10)
        self.assertEqual(len({r['table_2_row'] for r in self.new}),35)
        for row in self.new:depth.validate_section(row,self.widths,self.tables)

    def test_depths_come_from_metre_column_not_density_or_transport(self):
        rows={r['table_2_row']:r for r in self.new}
        self.assertEqual(rows[5]['range_m'],[0,678]);self.assertEqual(rows[13]['range_m'],[0,476]);self.assertEqual(rows[19]['range_m'],[0,1514])
        self.assertEqual(rows[59]['range_m'],[0,891]);self.assertEqual(rows[83]['range_m'],[0,1232])
        for field,value in [('range_m',[1,4]),('raw_depth_cell','0 to 26.7'),('range_m',[0,26.7])]:
            row=copy.deepcopy(rows[5]);row[field]=value
            with self.assertRaises(ValueError):depth.validate_section(row,self.widths,self.tables)

    def test_cruise_windows_are_not_decade_means_or_exact_boundary_dates(self):
        row=next(r for r in self.new if r['table_2_row']==5)
        self.assertEqual(row['section_sampling_window'],{'start':'1992-12-30','end':'1993-01-28'})
        self.assertEqual(row['inverse_model_decade_group'],'1990–1999');self.assertIsNone(row['observed_period'])
        for field,value in [('observed_period',row['section_sampling_window']),('decade_group_is_time_average',True),('cruise_id','invented'),('table_1_row',2)]:
            changed=copy.deepcopy(row);changed[field]=value
            with self.assertRaises(ValueError):depth.validate_section(changed,self.widths,self.tables)

    def test_latitude_layer_and_source_identity_mismatches_are_rejected(self):
        for field,value in [('nominal_latitude_degrees_north',30),('neutral_density_layer_indices','1:6'),('source_group','Brazil recirculation'),('entity_id','current:atlantic-south-equatorial')]:
            row=copy.deepcopy(self.new[1]);row[field]=value
            with self.assertRaises(ValueError):depth.validate_section(row,self.widths,self.tables)

    def test_extent_pair_is_not_a_uniform_rectangle_or_volume(self):
        for field in ['depth_extent_is_uniform_fixed_layer','rectangle_cross_section_inferred','cross_section_area_eligible','exact_boundary_coordinates_available']:
            row=copy.deepcopy(self.new[0]);row[field]=True
            with self.assertRaises(ValueError):depth.validate_section(row,self.widths,self.tables)
        for row in self.new:
            self.assertFalse(row['volume_eligible']);self.assertFalse(row['physical_state_join_eligible'])
            self.assertIsNone(row['thickness_m']);self.assertIsNone(row['uncertainty_m']);self.assertIsNone(row['annual_range_m'])

    def test_each_added_raw_source_reference_is_retained(self):
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        for row in self.new:
            raw=source['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual(raw,{k:row[k] for k in raw})

    def test_json_and_csv_reproduce_with_source_units_and_windows(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),depth.csv_bytes(self.data))
        rows=list(csv.DictReader(io.StringIO(depth.csv_bytes(self.data).decode('utf8'))))
        row=next(r for r in rows if r['table_2_row']=='5')
        self.assertEqual(row['range_m'],'[0,678]');self.assertEqual(row['unit'],'m')
        self.assertEqual(row['section_window_start'],'1992-12-30');self.assertEqual(row['cruise_id'],'06MT19921227')


if __name__=='__main__':unittest.main()
