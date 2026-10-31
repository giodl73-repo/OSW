import copy
import json
import unittest
import build_current_length_register_v1 as register


class FamilyLengthConventions(unittest.TestCase):
    def test_all_eight_family_conventions_are_visible_and_reproducible(self):
        rows = register.build()['records']
        families = [r for r in rows if r['identity_level'] == 'family']
        self.assertEqual(len(families), 8)
        for r in families:
            self.assertEqual(r['status'], 'family_principal_member')
            self.assertEqual(r['method'], 'longest_catalogued_member')
            self.assertEqual(r['length_estimate_km'], max(c['length_estimate_km'] for c in r['length_components']))
            selected = next(c for c in r['length_components'] if c['entity_id'] == r['selected_member_id'])
            self.assertEqual(r['length_estimate_km'], selected['length_estimate_km'])
            self.assertEqual(r['conditional_extent'], selected['conditional_extent'])
            self.assertTrue(all(c['scope'] and c['record_file'] for c in r['length_components']))
            self.assertIn('not a continuous', r['scope'])
            self.assertIsNone(r['annual_length_range_km'])

    def test_strict_gulf_stream_segments_sum_without_broader_name_aliases(self):
        row = next(r for r in register.build()['records'] if r['entity_id'] == 'current:gulf-stream-system')
        self.assertEqual(row['status'], 'system_segment_sum')
        self.assertEqual([c['entity_id'] for c in row['length_components']], ['current:florida','current:gulf-stream','current:north-atlantic'])
        self.assertEqual(row['length_estimate_km'], 7000)
        self.assertIn('no common along-route segment', row['scope'])
        self.assertIsNone(row['route_sensitivity_km'])
        self.assertIsNone(row['annual_length_range_km'])

    def test_duplicate_and_recursive_component_lists_are_rejected(self):
        document = json.loads((register.ROOT/'research/current-length-family-conventions-v1.json').read_bytes())
        rows = register.build()['records']
        for row in rows:
            if row['status'] in ['family_principal_member','system_segment_sum']:
                row['length_estimate_km'] = None
        for members in [['current:pacific-north-equatorial']*2, ['current:north-equatorial']]:
            broken = copy.deepcopy(document)
            broken['conventions'] = [next(c for c in broken['conventions'] if c['entity_id']=='current:north-equatorial')]
            broken['conventions'][0]['members'] = members
            with self.assertRaises(ValueError):register.apply_family_conventions(copy.deepcopy(rows), broken)


if __name__ == '__main__':
    unittest.main()
