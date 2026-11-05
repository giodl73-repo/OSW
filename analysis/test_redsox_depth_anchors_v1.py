import copy
import json
import tempfile
import unittest
from pathlib import Path
import build_redsox_depth_anchors_v1 as m


class DepthAnchors(unittest.TestCase):
    def setUp(self):
        self.facts = json.loads((m.ROOT / m.FACTS).read_bytes())
        self.row = copy.deepcopy(self.facts['records'][0])

    def test_cloud_source_build_and_positions(self):
        result = m.build()
        self.assertEqual(len(result['features']), 4)
        for feature, row in zip(result['features'], self.facts['records']):
            self.assertEqual(feature['geometry'], {'type': 'Point', 'coordinates': row['position_lon_lat']})
            for key, value in row.items():
                self.assertEqual(feature['properties'][key], value)

    def test_support_lower_bound_arithmetic(self):
        for row in self.facts['records']:
            p = m.anchor(row)['properties']
            self.assertEqual(p['minimum_connected_vertical_support_m'],
                             row['supported_penetration_lower_bound_m'] - row['upper_crossing_context']['boundary_depth_m'])
            self.assertGreater(p['minimum_connected_vertical_support_m'], 0)
            self.assertIsNone(p['conditional_lower_boundary_depth_m'])
            self.assertFalse(p['minimum_support_is_physical_current_thickness'])

    def test_no_bottom_or_surface_substitution(self):
        for key, value in [('lower_status', 'physical_bottom'), ('surface_connection_established', True),
                           ('physical_layer_thickness_m', 50), ('physical_current_bottom_established', True)]:
            row = copy.deepcopy(self.row); row[key] = value
            with self.assertRaises(ValueError): m.anchor(row)

    def test_invalid_upper_crossing_or_disconnected_core(self):
        for key, value in [('boundary_depth_m', 0), ('status', 'sampling_end')]:
            row = copy.deepcopy(self.row); row['upper_crossing_context'][key] = value
            with self.assertRaises(ValueError): m.anchor(row)
        row = copy.deepcopy(self.row); row['native_union_path_from_core_to_sampling_end_verified'] = False
        with self.assertRaises(ValueError): m.anchor(row)

    def test_no_temporal_identity_or_volume_upgrade(self):
        for key in ['volume_eligible', 'annual_extrema_established', 'reference_route_projection_eligible',
                    'physical_cast_identity_independently_verified', 'sample_level_synchronization_verified']:
            row = copy.deepcopy(self.row); row[key] = True
            with self.assertRaises(ValueError): m.anchor(row)

    def test_source_byte_change_blocks(self):
        op = json.loads((m.ROOT / m.OPERATOR).read_bytes())
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for path in [m.OPERATOR, *op['input_sha256']]:
                target = root / path; target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((m.ROOT / path).read_bytes())
            with (root / m.FACTS).open('ab') as stream: stream.write(b' ')
            with self.assertRaises(ValueError): m.build(root)

    def test_frames_times_and_no_interpolation(self):
        features = m.build()['features']
        self.assertEqual(len({f['properties']['comparison_group'] for f in features}), 2)
        for f in features:
            p = f['properties']
            self.assertNotEqual(p['source_velocity_header_time_utc'], p['source_ctd_start_time_utc'])
            self.assertFalse(p['between_anchor_interpolation_performed'])
            self.assertIsNone(p['volume_m3'])
            self.assertIsNone(p['annual_range_m'])


if __name__ == '__main__': unittest.main()
