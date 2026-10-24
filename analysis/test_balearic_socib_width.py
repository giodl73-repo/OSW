import copy
import json
import unittest
from check_balearic_socib_width import ROOT, ID, load, record, validate_row, validate_inventory, svg


class BalearicProviderWidthTests(unittest.TestCase):
    def test_exact_table_range_is_not_an_occupation_or_representative_scalar(self):
        row = record()
        validate_row(row)
        self.assertEqual(row['width_range_km'], [20, 35])
        self.assertIsNone(row['approximate_width_km'])
        self.assertIsNone(row['observed_period'])
        self.assertIn('not an edge cutoff', svg())

    def test_rejects_midpoint_calendar_cutoff_and_alias_promotions(self):
        row = record()
        for key, value in [('approximate_width_km', 27.5), ('width_range_km', [10, 20]),
                           ('calendar_months', [9,10,11]), ('width_rank_eligible', True),
                           ('annual_extrema_eligible', True), ('current_id', 'northern-mediterranean'),
                           ('boundary_rule', 'GV > 0.2 m/s'), ('fixed_layer_bounds_m', [0,150]),
                           ('observed_period', {'start':'2023-11-13','end':'2023-11-13'})]:
            invalid = copy.deepcopy(row)
            invalid[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_row(invalid)
        invalid = copy.deepcopy(row)
        invalid['original_regional_context']['numeric_endpoints_assigned_to_seasons'] = True
        with self.assertRaises(ValueError):
            validate_row(invalid)

    def test_missing_reviewed_range_or_coherent_audit_rewrite_is_rejected(self):
        inventory = json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
        inventory['measurements'] = [r for r in inventory['measurements'] if r['id'] != ID]
        with self.assertRaises(ValueError):
            validate_inventory(inventory)
        audit = load()
        audit['measurement']['width_range_km'] = [20,40]
        invalid = record()
        invalid['width_range_km'] = [20,40]
        with self.assertRaises(ValueError):
            validate_row(invalid, audit)


if __name__ == '__main__':
    unittest.main()
