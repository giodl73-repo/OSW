import copy
import csv
import io
import json
import unittest
from unittest.mock import patch
import audit_norkyst_jutland_depth_v1 as m


class RetainedDepthAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('urllib.request.urlopen', side_effect=AssertionError('No provider retrieval')):
            cls.report, cls.geo = m.build()
        cls.original_op = json.loads((m.ROOT / m.source.OPERATOR).read_bytes())
        cls.plan = m.source.preflight(cls.original_op)['plans'][0]
        cls.raw = (m.ROOT / m.FOLDER / 'case-00.ascii').read_bytes()
        cls.case = json.loads((m.ROOT / m.FOLDER / 'case-00.json').read_bytes())

    def test_every_source_case_and_profile_retained(self):
        self.assertEqual(len(self.report['rows']),12)
        self.assertEqual(self.report['counts']['source_profile_instances'],468)
        self.assertEqual([p['date'] for p in self.report['date_profiles']],self.original_op['dates'])
        self.assertTrue(all(len(p['anchors']) == 3 for p in self.report['date_profiles']))

    def test_full_response_reconstruction_and_core_rules(self):
        row = m.audit_case(self.case,self.raw,self.plan,self.original_op)
        self.assertEqual(row['component_bearing_degrees_true'],45)
        self.assertEqual(row['selection_interval_m'],[0,25])
        self.assertEqual(row['source_vertical_sampling'],'provider_interpolated_fixed_z_not_native_ROMS_s_layers')

    def test_changed_component_coordinate_or_time_rejected(self):
        for change in ['time','position','component']:
            case = copy.deepcopy(self.case)
            if change == 'time': case['time_utc'] = 'invented'
            elif change == 'position': case['columns'][0]['position_lon_lat'][0] += .1
            else: case['columns'][0]['northeast_component_m_s'][0] = 99
            with self.assertRaises(ValueError): m.audit_case(case,self.raw,self.plan,self.original_op)

    def test_changed_selection_or_physical_promotion_rejected(self):
        for key,value in [('physical_current_thickness_m',25),('physical_current_bottom_established',True),('component_bearing_degrees_true',0)]:
            case = copy.deepcopy(self.case); case[key] = value
            with self.assertRaises(ValueError): m.audit_case(case,self.raw,self.plan,self.original_op)
        case = copy.deepcopy(self.case); case['diagnosis']['selected_column_index'] = 999
        with self.assertRaises(ValueError): m.audit_case(case,self.raw,self.plan,self.original_op)

    def test_anchor_qualification_uses_primary_and_interior_only(self):
        for r in self.report['rows']:
            self.assertEqual(r['regional_axis_proxy_lower_contour_anchor_eligible'],
                             r['horizontal_axis_proxy_interior'] and r['primary_lower_component_contour_depth_m'] is not None)
            if r['primary_component_layer']:
                self.assertEqual(r['primary_component_layer']['threshold_m_s'],.1)

    def test_censor_stays_a_bound_without_bottom_or_volume(self):
        for r in self.report['rows']:
            if r['primary_connected_depth_lower_bound_m'] is not None:
                self.assertIsNone(r['primary_lower_component_contour_depth_m'])
                self.assertIsNone(r['conditional_component_span_m'])
            self.assertIsNone(r['physical_thickness_m']); self.assertIsNone(r['volume_m3'])
            self.assertFalse(r['physical_current_bottom_established']); self.assertFalse(r['volume_eligible'])

    def test_geojson_positions_and_no_depth_as_altitude(self):
        by_id = {(r['date'],r['section_id']):r for r in self.report['rows']}
        for f in self.geo['features']:
            p = f['properties']; row = by_id[p['date'],p['section_id']]
            self.assertEqual(f['geometry'],{'type':'Point','coordinates':row['selected_position_lon_lat']})
            self.assertEqual(len(f['geometry']['coordinates']),2)

    def test_tabular_roles_and_all_dates_preserved(self):
        rows = list(csv.DictReader(io.StringIO(m.csv_bytes(self.report).decode())))
        self.assertEqual(len(rows),12)
        for row, source in zip(rows,self.report['rows']):
            self.assertEqual(row['date'],source['date'])
            if source['primary_lower_component_contour_depth_m'] is None:
                self.assertEqual(row['primary_lower_component_contour_depth_m'],'')
        self.assertTrue(all(p['between_anchor_interpolation_performed'] is False and p['seasonal_mean'] is False for p in self.report['date_profiles']))


if __name__ == '__main__': unittest.main()
