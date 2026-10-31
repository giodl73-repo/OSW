import hashlib
import json
import unittest
from pathlib import Path
import build_current_length_register_v1 as register
import estimate_current_reference_extents_v1 as extents


class LengthRegister(unittest.TestCase):
    def test_complete_inventory_and_honest_remaining_work(self):
        document=register.build();rows=document['records']
        self.assertEqual(len(rows),111)
        self.assertEqual(len({r['entity_id'] for r in rows}),111)
        self.assertEqual(sum(r['length_estimate_km'] is not None for r in rows),111)
        self.assertEqual(sum(r['needs_full_extent_estimate'] for r in rows),0)
        self.assertEqual(document['full_goal_complete'],(register.ROOT/register.COMPLETION_PATH).exists())
        for row in rows:
            self.assertIsNone(row['annual_length_range_km'])
            if row['length_estimate_km'] is not None:
                self.assertGreater(row['length_estimate_km'],0)
                self.assertTrue(row['scope']);self.assertTrue(row['method']);self.assertTrue(row['record_file'])

    def test_regional_reach_not_promoted_and_reported_extent_not_overwritten(self):
        rows={r['entity_id']:r for r in register.build()['records']}
        self.assertEqual(rows['current:baffin']['length_estimate_km'],1500)
        self.assertEqual(rows['current:baffin']['available_regional_reach_km'],1200)
        self.assertEqual(rows['current:aleutian']['length_estimate_km'],4800)
        self.assertEqual(rows['current:aleutian']['available_regional_reach_km'],3300)
        self.assertEqual(rows['current:southern-east-madagascar']['length_estimate_km'],650)
        self.assertEqual(rows['current:southern-east-madagascar']['status'],'reported')
        self.assertEqual(rows['current:north-equatorial']['selected_member_id'],'current:pacific-north-equatorial')

    def test_two_estimates_reproduce_all_scenarios_and_source_bindings(self):
        document=extents.build();retained=json.loads((extents.ROOT/extents.OUTPUT).read_bytes())
        self.assertEqual(document,retained)
        for row in document['records']:
            self.assertEqual(len(row['scenarios']),36)
            self.assertAlmostEqual(extents.length(row['coordinates_lon_lat']),row['computed_reference_length_km'],places=5)
            low,high=row['scenario_range_km']
            self.assertTrue(all(low<=s['length_km']<=high for s in row['scenarios']))
            self.assertIsNone(row['uncertainty_km']);self.assertFalse(row['physical_axis_admitted'])
        for path,pin in register.build()['input_sha256'].items():
            self.assertEqual(hashlib.sha256((register.ROOT/path).read_bytes()).hexdigest(),pin)


if __name__=='__main__':unittest.main()
