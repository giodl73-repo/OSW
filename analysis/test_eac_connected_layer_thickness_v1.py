import unittest
from derive_eac_connected_layer_thickness_v1 import connected_layer, derive


class ConnectedLayers(unittest.TestCase):
    def test_surface_layer(self):
        r = connected_layer([0, 100, 200], [.3, .2, 0], .1)
        self.assertEqual(r['upper_depth_m'], 0)
        self.assertEqual(r['lower_depth_m'], 150)
        self.assertEqual(r['layer_thickness_m'], 150)

    def test_subsurface_layer_not_lower_depth(self):
        r = connected_layer([0, 100, 200], [0, .2, 0], .1)
        self.assertEqual((r['upper_depth_m'], r['lower_depth_m'], r['layer_thickness_m']), (50, 150, 100))

    def test_missing_above(self):
        r = connected_layer([0, 50, 100, 200], [None, .2, .3, 0], .1)
        self.assertIsNone(r['layer_thickness_m'])
        self.assertIsNotNone(r['lower_depth_m'])

    def test_missing_below_not_bridged(self):
        r = connected_layer([0, 100, 200, 300], [.3, .2, None, 0], .1)
        self.assertIsNone(r['lower_depth_m'])
        self.assertIsNone(r['layer_thickness_m'])

    def test_domain_top_not_surface(self):
        r = connected_layer([2.5, 100, 200], [.3, .2, 0], .1)
        self.assertIsNone(r['upper_depth_m'])
        self.assertIsNone(r['layer_thickness_m'])

    def test_deepest_above_threshold_not_bottom(self):
        r = connected_layer([0, 100, 200], [.3, .2, .15], .1)
        self.assertIsNone(r['lower_depth_m'])

    def test_first_connected_component_only(self):
        r = connected_layer([0, 50, 100, 200, 300, 400], [0, .4, 0, 0, .8, 0], .1)
        self.assertEqual(r['core_depth_m'], 50)
        self.assertLess(r['lower_depth_m'], 100)

    def test_exact_threshold_and_tied_core(self):
        r = connected_layer([0, 50, 100, 200], [.1, .3, .3, .1], .1)
        self.assertEqual(r['core_depth_m'], 50)
        self.assertEqual(r['layer_thickness_m'], 200)

    def test_opposing_or_equal_flow(self):
        for v in [[-.3, -.2], [.1, .1]]:
            self.assertEqual(connected_layer([0, 100], v, .1)['status'], 'no_qualifying_core')

    def test_invalid_input(self):
        for z, v, t in [([0, 0], [.3, 0], .1), ([-1, 100], [.3, 0], .1),
                        ([0, 100], [float('nan'), 0], .1), ([0, 100], [.3, 0], 0),
                        ([0, 100], [.3], .1)]:
            with self.assertRaises(ValueError):
                connected_layer(z, v, t)

    def test_missing_core_interval_rejected(self):
        with self.assertRaises(ValueError):
            connected_layer([0, 100], [.3, 0], .1, (200, 0))

    def test_frozen_selection_and_axis_flags(self):
        profile = {'normal_offset_km': 0, 'sampled_lon_lat': [153, -27],
                   'along_velocity_m_s': [.3, .2, 0]}
        row = {'sampled_profiles': [profile] * 5, 'depth_levels_m': [0, 100, 200],
               'snapshot_time_utc': '2022-01-15T00:00:00Z', 'route_vertex_index': 0,
               'reference_distance_km': 0, 'editorial_lon_lat': [153, -27],
               'selected_profile_index': 0, 'horizontal_selection_status': 'edge_maximum_axis_unresolved',
               'primary_core_lower_descriptor': {'core_depth_m': 0, 'lower_isotach_depth_m': 175}}
        src = {'counts': {'sampled_cases': 14}, 'samples': [row] * 14,
               'entity_id': 'current:east-australian', 'source_product': 'synthetic'}
        op = {'thresholds_m_s': [.05, .1, .2], 'core_search_depth_interval_m': [0, 200],
              'eligibility': {'whole_current_volume': False}}
        result = derive(src, op)
        self.assertEqual(result['counts']['threshold_descriptors'], 210)
        self.assertFalse(result['selected_route_samples'][0]['named_current_axis_validated'])
        self.assertEqual(result['selected_route_samples'][0]['selected_profile_index'], 0)
        row['primary_core_lower_descriptor']['lower_isotach_depth_m'] = 180
        with self.assertRaises(ValueError):
            derive(src, op)


if __name__ == '__main__':
    unittest.main()
