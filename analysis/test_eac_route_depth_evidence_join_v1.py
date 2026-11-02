import copy
import hashlib
import json
import unittest
from build_eac_route_depth_evidence_join_v1 import ROOT, OPERATOR, join, interpolate


class RouteEvidenceJoin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op = json.loads((ROOT / OPERATOR).read_bytes())
        cls.inputs = [json.loads((ROOT / cls.op[name + '_file']).read_bytes())
                      for name in ['model', 'layers', 'surface', 'moorings']]
        cls.result = join(*cls.inputs, cls.op)

    def test_complete_coverage_and_conditional_counts(self):
        self.assertEqual(self.result['counts'], {'dated_route_nodes': 14,
            'adjacent_reference_segments': 12, 'conditional_lower_depth_nodes': 6,
            'conditional_thickness_nodes': 6, 'conditional_linear_reference_segments': 2,
            'gap_segments': 10, 'regional_mooring_context_profiles': 14,
            'whole_route_physical_depth_profiles': 0, 'water_volume_estimates': 0})

    def test_only27_to30S_has_adjacent_eligible_endpoints(self):
        ready = [s for s in self.result['segments'] if s['status'] != 'gap_no_projection']
        self.assertEqual([(s['source_date'], s['route_vertex_interval']) for s in ready],
                         [('2022-01-15', [4, 5]), ('2022-07-15', [4, 5])])
        for s in ready:
            self.assertTrue(s['unsampled_interior_assumed_linear_not_observed'])
            self.assertFalse(s['physical_current_continuity_established'])
            self.assertFalse(s['volume_eligible'])

    def test_gaps_never_supply_projected_values(self):
        for s in self.result['segments']:
            if s['status'] == 'gap_no_projection':
                self.assertIsNone(s['lower_isotach_depth_m_endpoints'])
                self.assertIsNone(s['layer_thickness_m_endpoints'])
                a, b = s['reference_distance_interval_km']
                self.assertIsNone(interpolate(s, (a + b) / 2))

    def test_noncorroboration_and_edge_flags_both_block(self):
        unsupported = {(n['source_date'], n['route_vertex_index']) for n in self.result['nodes']
                       if 'surface_component_not_corroborated_or_missing' in n['projection_block_reasons']}
        self.assertEqual(unsupported, {('2022-01-15', 0), ('2022-01-15', 1),
                                      ('2022-07-15', 0), ('2022-07-15', 2)})
        for n in self.result['nodes']:
            if n['model_horizontal_selection_status'] == 'edge_maximum_axis_unresolved':
                self.assertFalse(n['conditional_lower_depth_projection_node_eligible'])

    def test_vertical_censoring_no_alternate_threshold_substitution(self):
        for n in self.result['nodes']:
            if n['route_vertex_index'] == 6:
                self.assertIsNone(n['model_primary_lower_isotach_depth_m'])
                self.assertIn('lower_boundary_unresolved', n['projection_block_reasons'])
                self.assertFalse(n['conditional_lower_depth_projection_node_eligible'])

    def test_thickness_is_paired_span_not_lower_depth_alias(self):
        for n in self.result['nodes']:
            layer = n['model_primary_connected_layer']
            if layer['layer_thickness_m'] is not None:
                self.assertAlmostEqual(layer['layer_thickness_m'], layer['lower_depth_m'] - layer['upper_depth_m'])
            self.assertFalse(n['current_axis_or_physical_depth_validated'])
        self.assertFalse(any(self.result['eligibility'].values()))

    def test_mooring_context_cannot_fill_model_or_become_colocated(self):
        for c in self.result['regional_mooring_context']:
            self.assertEqual(len(c['records']), 7)
            self.assertFalse(c['model_observation_colocated'])
            self.assertIn('not_colocated_or_used_for_model_depth_filling', c['role'])
        for n in self.result['nodes']:
            self.assertEqual(n['regional_mooring_context_key'] is not None, n['route_vertex_index'] == 4)

    def test_duplicate_or_incomplete_keys_rejected(self):
        for source, field in [(0, 'samples'), (1, 'selected_route_samples'), (2, 'samples')]:
            inputs = copy.deepcopy(self.inputs)
            inputs[source][field].append(copy.deepcopy(inputs[source][field][0]))
            with self.assertRaises(ValueError):
                join(*inputs, self.op)
            inputs[source][field] = inputs[source][field][:-2]
            with self.assertRaises(ValueError):
                join(*inputs, self.op)

    def test_frozen_selection_geometry_time_and_primary_must_match(self):
        mutations = [(1, 'selected_route_samples', 'selected_profile_index', 4),
                     (1, 'selected_route_samples', 'editorial_lon_lat', [0, 0]),
                     (1, 'selected_route_samples', 'snapshot_time_utc', '2022-01-15T06:00:00Z')]
        for source, field, key, value in mutations:
            inputs = copy.deepcopy(self.inputs)
            inputs[source][field][0][key] = value
            with self.assertRaises(ValueError):
                join(*inputs, self.op)
        inputs = copy.deepcopy(self.inputs)
        inputs[1]['selected_route_samples'][0]['layers_at_frozen_selected_node'][0]['lower_depth_m'] = 1
        with self.assertRaises(ValueError):
            join(*inputs, self.op)

    def test_no_identity_promotion_or_corrupted_surface_support(self):
        inputs = copy.deepcopy(self.inputs)
        inputs[2]['samples'][0]['screen']['named_current_axis_validated'] = True
        with self.assertRaises(ValueError):
            join(*inputs, self.op)
        inputs = copy.deepcopy(self.inputs)
        inputs[2]['samples'][0]['screen']['status'] = 'poleward_surface_component_supported_not_current_identity'
        with self.assertRaises(ValueError):
            join(*inputs, self.op)

    def test_conditional_linear_interpolation_and_no_extrapolation(self):
        s = next(s for s in self.result['segments'] if s['status'] != 'gap_no_projection')
        a, b = s['reference_distance_interval_km']
        values = s['lower_isotach_depth_m_endpoints']
        self.assertAlmostEqual(interpolate(s, (a + b) / 2), sum(values) / 2)
        for x in [a - 1, b + 1, float('nan')]:
            with self.assertRaises(ValueError):
                interpolate(s, x)
        with self.assertRaises(ValueError):
            interpolate(s, a, 'water_volume')

    def test_frozen_input_hashes(self):
        for path, pin in self.op['input_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), pin)


if __name__ == '__main__':
    unittest.main()
