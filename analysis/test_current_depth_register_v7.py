"""Verify inverse deep domains, nonnumeric seafloor terminals and spatial summaries."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v6 as previous
import build_current_depth_register_v7 as depth
from build_atlantic_cruise_widths import read_cells


class DeepDomainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.new=cls.data['evidence'][75:]
        cls.tables=depth.read_deep_tables()
        cls.cruises={r['row']:r['cells'] for r in read_cells(depth.TABLE1)}
        cls.table2={r['row']:r['cells'] for r in read_cells(depth.TABLE2)}
        cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        previous.validate_reference(row,self.ids,self.metrics)
        if row.get('xml_table_id'):depth.validate_section(row,self.tables,self.cruises)
        else:depth.validate_other(row,self.table2)

    def test_inventory_and_prior_75_references_preserved(self):
        prior=previous.build()
        self.assertEqual(self.data['evidence'][:75],prior['evidence'])
        self.assertEqual({r['entity_id'] for r in self.data['records']},{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':95,'identities_with_scoped_depth_reference':33,'identities_not_yet_assessed':78,'whole_route_depth_profiles':0,'volume_estimates':0})

    def test_seventeen_deep_rows_have_explicit_identity_cruise_and_column_joins(self):
        rows=[r for r in self.new if r.get('xml_table_id')]
        self.assertEqual(len(rows),17)
        self.assertEqual({(r['xml_table_id'],r['xml_tbody_row']) for r in rows},set(depth.JOINS))
        dwbc=[r for r in rows if r['entity_id']=='current:deep-western-boundary']
        self.assertEqual(len(dwbc),14)
        self.assertEqual({r['nominal_latitude_degrees_north'] for r in dwbc},{47,36,24.5,-11,-19,-24,-30,-45})
        for row in rows:self.validate(row)

    def test_six_bottom_terminals_do_not_invent_depth_or_thickness(self):
        rows=[r for r in self.new if r.get('lower_domain_boundary_kind')=='seafloor_unspecified_numeric_depth']
        self.assertEqual(len(rows),6)
        row=next(r for r in rows if r['raw_depth_cell']=='2859 to bottom')
        self.assertEqual(row['metric'],'transport_selected_upper_depth');self.assertEqual(row['approximate_value_m'],2859)
        self.assertIsNone(row['range_m']);self.assertIsNone(row['domain_lower_depth_m']);self.assertIsNone(row['thickness_m'])
        for field,value in [('domain_lower_depth_m',5000),('lower_domain_boundary_kind','reported_numeric_depth'),('metric','upper_flow_boundary_depth'),('range_m',[2859,5000]),('thickness_m',2141)]:
            changed=copy.deepcopy(row);changed[field]=value
            with self.assertRaises(ValueError):self.validate(changed)

    def test_finite_domains_reproduce_both_depths_not_layer_indices_or_transport(self):
        rows={(r.get('xml_table_id'),r.get('xml_tbody_row')):r for r in self.new}
        self.assertEqual(rows[('Ch1.T5',27)]['range_m'],[2553,5630])
        self.assertEqual(rows[('Ch1.T6',2)]['range_m'],[1323,2561])
        self.assertEqual(rows[('Ch1.T6',13)]['range_m'],[717,3352])
        for field,value in [('range_m',[6,8]),('raw_depth_cell','17.3 to 22'),('xml_table_id','Ch1.T3'),('neutral_density_layer_indices','7:10'),('domain_lower_depth_m',2561)]:
            row=copy.deepcopy(rows[('Ch1.T6',2)]);row[field]=value
            with self.assertRaises(ValueError):self.validate(row)

    def test_component_and_front_scope_do_not_become_entire_systems(self):
        lab=[r for r in self.new if r['entity_id']=='current:labrador']
        self.assertEqual(len(lab),3)
        self.assertTrue(all(r['source_component_scope']=='deep_component_only' for r in lab))
        front=next(r for r in self.new if r['entity_id']=='current:acc')
        self.assertEqual(front['range_m'],[0,3035]);self.assertEqual(front['source_component_scope'],'front_component_only')
        for original in [lab[0],front]:
            row=copy.deepcopy(original);row['source_component_scope']='whole_current'
            with self.assertRaises(ValueError):self.validate(row)

    def test_cruise_windows_not_decade_means_widths_or_exact_boundary_dates(self):
        row=next(r for r in self.new if r.get('xml_table_id')=='Ch1.T6' and r['xml_tbody_row']==13)
        self.assertEqual(row['section_sampling_window'],{'start':'1992-12-27','end':'1993-01-30'})
        for field,value in [('table_1_row',3),('section_sampling_window',{'start':'1990-01-01','end':'1999-12-31'}),('decade_group_is_time_average',True),('source_horizontal_span_km',163),('horizontal_span_is_cross_stream_width',True),('same_source_width_reference_id','unrelated'),('volume_eligible',True)]:
            changed=copy.deepcopy(row);changed[field]=value
            with self.assertRaises(ValueError):self.validate(changed)

    def test_california_cross_shore_summaries_not_temporal_range(self):
        rows={r['cross_shore_scope']:r for r in self.new if r['entity_id']=='current:california'}
        self.assertEqual(rows['offshore']['approximate_value_m'],500)
        self.assertEqual(rows['within_300km_of_coast']['approximate_value_m'],150)
        for row in rows.values():
            self.assertIsNone(row['range_m']);self.assertIsNone(row['annual_range_m']);self.assertEqual(row['evidence_kind'],'published_literature_synthesis')
            for field,value in [('cross_shore_scope','whole_route'),('climatology_period',{'start_year':2003,'end_year':2009}),('annual_range_m',[150,500])]:
                changed=copy.deepcopy(row);changed[field]=value
                with self.assertRaises(ValueError):self.validate(changed)

    def test_raw_facts_and_json_csv_reproduce_with_seafloor_semantics(self):
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        self.assertEqual(len(self.new),20)
        for row in self.new:
            raw=source['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual(raw,{k:row[k] for k in raw});self.validate(row)
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),depth.csv_bytes(self.data))
        rows=list(csv.DictReader(io.StringIO(depth.csv_bytes(self.data).decode('utf8'))))
        row=next(r for r in rows if r['xml_table_id']=='Ch1.T5' and r['xml_tbody_row']=='22')
        self.assertEqual(row['approximate_value_m'],'2859');self.assertEqual(row['range_m'],'')
        self.assertEqual(row['domain_lower_depth_m'],'');self.assertEqual(row['lower_domain_boundary_kind'],'seafloor_unspecified_numeric_depth')


if __name__=='__main__':unittest.main()
