import unittest
from acquire_eac_surface_route_screen_v1 import along, screen, check_budget


class SurfaceScreen(unittest.TestCase):
    def profiles(self, values):
        return [{'along_total_m_s': v, 'source_grid_index': [0, i]} for i, v in enumerate(values)]

    def test_true_direction_and_missing_component(self):
        self.assertAlmostEqual(along(.1, -.3, 180), .3)
        self.assertAlmostEqual(along(.1, -.3, 90), .1)
        self.assertIsNone(along(None, -.3, 180))

    def test_supported_flow_not_identity(self):
        r = screen(self.profiles([.1, .3, .2, 0, -.1]), 1, .05)
        self.assertEqual(r['sampled_surface_peak_index'], 1)
        self.assertFalse(r['named_current_axis_validated'])
        self.assertFalse(r['physical_depth_validated'])

    def test_no_switch_to_convenient_node(self):
        r = screen(self.profiles([-.1, .3, .2, .1, -.2]), 4, .05)
        self.assertEqual(r['frozen_model_selected_profile_index'], 4)
        self.assertEqual(r['status'], 'poleward_surface_component_not_corroborated_not_current_absence')

    def test_missing_unknown_not_zero(self):
        r = screen(self.profiles([None] * 5), 0, .05)
        self.assertIsNone(r['surface_component_at_frozen_model_node_m_s'])
        self.assertIsNone(r['sampled_surface_peak_index'])

    def test_ties_edges_and_duplicate_grid_nodes(self):
        profiles = self.profiles([.2, .2, .1, .1, 0])
        profiles[1]['source_grid_index'] = profiles[0]['source_grid_index']
        r = screen(profiles, 1, .05)
        self.assertEqual(r['sampled_surface_peak_index'], 0)
        self.assertTrue(r['sampled_surface_peak_at_window_edge'])
        self.assertEqual(r['unique_surface_grid_nodes'], 4)

    def test_budget_before_field_retrieval(self):
        self.assertEqual(check_budget(5, 5, 0, 10000), 125)
        for args in [(30, 30, 0, 10000), (5, 5, 9950, 10000), (0, 1, 0, 10000)]:
            with self.assertRaises(ValueError):
                check_budget(*args)

    def test_invalid_frozen_index(self):
        with self.assertRaises(ValueError):
            screen(self.profiles([.1] * 5), 5, .05)


if __name__ == '__main__':
    unittest.main()
