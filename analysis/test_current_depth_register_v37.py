"""Guard deep flow presence against invented boundaries, volumes and ownership."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v36 as previous
import build_current_depth_register_v37 as depth


class GulfStreamDeepPresenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.row=cls.data['evidence'][-1]
        cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def reject(self,changes):
        for field,value in changes:
            row=copy.deepcopy(self.row);row[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):
                depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def test_prior_evidence_and_unknown_whole_route_profiles_preserved(self):
        self.assertEqual(self.data['evidence'][:-1],previous.build()['evidence'])
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':333,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0})
        self.assertEqual(self.data['metadata_correction_count'],3)

    def test_presence_is_inclusive_minimum_not_a_bottom_or_thickness(self):
        self.assertEqual((self.row['metric'],self.row['lower_bound_m'],self.row['lower_bound_operator'],self.row['lower_bound_exclusive']),('reported_vertical_extent',3500,'>=',False))
        self.reject([('approximate_value_m',3500),('lower_boundary_m',3500),('thickness_m',3500),('lower_bound_exclusive',True),('lower_bound_operator','>'),('upper_bound_m',3500),('metric','lower_flow_boundary_depth')])

    def test_deployment_and_averaging_frame_not_seasonal_or_exact_position(self):
        self.assertEqual(self.row['source_deployment_month_bounds'],['1988-06','1990-08'])
        self.assertEqual(self.row['source_mooring_count'],13)
        self.assertEqual(self.row['temporal_operator'],'source_stream_coordinate_mean')
        self.reject([('temporal_operator','Eulerian_mean'),('section_latitude_degrees_north',38),('calendar_months',[6,7,8]),('observed_period',{'start':'1988-06-01','end':'1990-08-31'}),('annual_extrema_eligible',True)])

    def test_deep_width_context_cannot_supply_whole_current_area_or_volume(self):
        self.assertEqual(self.row['source_deep_level_width_km'],130)
        self.assertEqual(self.row['source_deep_level_context_depth_m'],3500)
        self.reject([('source_deep_level_width_is_whole_current_width',True),('source_cross_section_area_km2',455),('volume_eligible',True),('whole_current_representative',True),('reference_route_projection_eligible',True),('physical_state_join_eligible',True),('same_source_width_reference_id','surface-width')])

    def test_abstract_review_not_claimed_as_original_figure_or_full_methods(self):
        self.assertEqual(self.row['source_access_scope'],'primary_publisher_abstract')
        self.reject([('source_access_scope','original_PDF_pixels'),('evidence_kind','original_observed_section_figure_presence')])

    def test_parent_lookup_adds_member_reference_without_inheriting_scalar(self):
        index=depth.build_member_index(self.data)
        self.assertEqual(index,json.loads((depth.ROOT/depth.MEMBER_OUTPUT).read_bytes()))
        self.assertEqual(index['counts']['distinct_member_depth_references'],47)
        parent=next(r for r in index['records'] if r['entity_id']=='current:gulf-stream-system')
        member=next(r for r in parent['members'] if r['entity_id']=='current:gulf-stream')
        self.assertIn(self.row['id'],member['depth_reference_ids'])
        self.assertIsNone(parent['parent_depth_m']);self.assertIsNone(parent['parent_volume_km3'])
        self.assertEqual(parent['new_measurement_count'],0)
        own=next(r for r in self.data['records'] if r['entity_id']==parent['entity_id'])
        self.assertEqual(own['depth_reference_ids'],[])

    def test_json_csv_reproduce_with_qualified_bound_and_context(self):
        self.assertEqual(self.data,json.loads((depth.ROOT/depth.OUTPUT).read_bytes()))
        raw=depth.csv_bytes(self.data);self.assertEqual(raw,(depth.ROOT/depth.CSV).read_bytes())
        row=list(csv.DictReader(io.StringIO(raw.decode('utf8'))))[-1]
        self.assertEqual(float(row['lower_bound_m']),3500)
        self.assertEqual(row['lower_bound_operator'],'>=')
        self.assertEqual(json.loads(row['source_deployment_month_bounds']),['1988-06','1990-08'])
        self.assertEqual(float(row['source_deep_level_width_km']),130)


if __name__=='__main__':unittest.main()
