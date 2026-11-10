import csv
import io
import json
import tempfile
import unittest
from pathlib import Path
import project_pgw_relative_core_depth_v1 as m


class RelativeCoreDepth(unittest.TestCase):
    def test_source_bound_build(self):
        r = m.build()
        self.assertEqual(r['entity_id'], 'current:persian-gulf-saline-overflow')
        self.assertEqual(len(r['profiles']), 3)
        self.assertIsNone(r['source_constraint']['absolute_endpoint_depths_m'])
        self.assertIsNone(r['coordinate']['geographic_geometry'])

    def test_endpoint_and_direction(self):
        for shoaling in [5, 15, 25]:
            self.assertEqual(m.depth_at(0, shoaling)['relative_core_depth_change_m'], 0)
            self.assertEqual(m.depth_at(300, shoaling)['relative_core_depth_change_m'], -shoaling)
            self.assertEqual(m.depth_at(150, shoaling)['relative_core_depth_change_m'], -shoaling / 2)

    def test_arbitrary_interior_query(self):
        r = m.depth_at(120, 25)
        self.assertEqual(r['relative_core_depth_change_m'], -10)
        self.assertIsNone(r['scenario_core_depth_m'])

    def test_strict_shoaling_limit(self):
        for value in [0, 30, -1, 31, float('nan'), float('inf'), True]:
            with self.assertRaises(ValueError): m.depth_at(100, value)

    def test_no_extrapolation(self):
        for value in [-1, 301, float('nan'), float('inf'), True]:
            with self.assertRaises(ValueError): m.depth_at(value, 15)

    def test_datum_is_explicit_optional_assumption(self):
        r = m.depth_at(300, 25, 200)
        self.assertEqual(r['scenario_core_depth_m'], 175)
        self.assertEqual(r['assumed_r14_core_depth_m'], 200)
        self.assertEqual(m.depth_at(300, 25, 220)['scenario_core_depth_m'], 195)
        for value in [0, 25, -10, True, float('nan')]:
            with self.assertRaises(ValueError): m.depth_at(300, 25, value)

    def test_open_family_bounds_not_uncertainty(self):
        r = m.depth_at(150, 15)
        self.assertEqual(r['linear_scenario_depth_change_open_lower_bound_m'], -15)
        self.assertEqual(r['linear_scenario_depth_change_open_upper_bound_m'], 0)
        self.assertTrue(r['bounds_exclusive'])
        self.assertFalse(m.depth_at(0, 15)['bounds_exclusive'])
        self.assertFalse(m.build()['scenario_family_range_is_uncertainty'])

    def test_no_thickness_volume_or_whole_current_promotion(self):
        r = m.build()
        for key in ['physical_layer_thickness_m', 'volume_m3', 'annual_range_m', 'exact_common_occupation_time']:
            self.assertIsNone(r[key])
        self.assertFalse(r['whole_current_profile'])
        self.assertFalse(r['old_projection_inventory_modified'])
        self.assertEqual(r['new_primary_measurements'], 0)

    def test_source_byte_mutation_rejected(self):
        op = json.loads((m.ROOT / m.OPERATOR).read_bytes())
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for path in [m.OPERATOR, *op['input_sha256']]:
                p = root / path; p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes((m.ROOT / path).read_bytes())
            with (root / m.FACTS).open('ab') as f: f.write(b' ')
            with self.assertRaises(ValueError): m.build(root)

    def test_tabular_values_preserve_relative_and_assumed_roles(self):
        report = m.build(); rows = list(csv.DictReader(io.StringIO(m.csv_bytes(report).decode())))
        self.assertEqual(len(rows), 42)
        relative = [r for r in rows if r['datum_role'] == 'relative_samples']
        self.assertEqual(len(relative), 21)
        self.assertTrue(all(r['scenario_core_depth_m'] == '' for r in relative))
        self.assertTrue(all(r['bounds_role'] == 'linear_family_only_not_observed_pointwise_limits' for r in rows))


if __name__ == '__main__': unittest.main()
