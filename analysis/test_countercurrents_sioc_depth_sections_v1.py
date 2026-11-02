import json
import unittest
import numpy as np
import acquire_zonal_current_depth_sections_v1 as s


class CountercurrentSIOCRulesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.op=json.loads((s.ROOT/'research/countercurrents-sioc-depth-sections-operator-v1.json').read_bytes())

    def test_distinct_members_and_studied_reaches_not_family_or_undercurrents(self):
        self.assertEqual(set(self.op['currents']),{'current:pacific-north-equatorial-countercurrent','current:atlantic-north-equatorial-countercurrent','current:south-indian'})
        self.assertEqual(len(self.op['sections']),16)
        self.assertNotIn('current:north-equatorial-countercurrent',self.op['currents'])
        self.assertFalse(any('undercurrent' in key for key in self.op['currents']))

    def test_declared_eastward_orders_and_seasonally_weak110w_section_are_preserved(self):
        expected={'current:pacific-north-equatorial-countercurrent':[-140,-132.5,-125,-117.5,-110,-102.5,-95],
                  'current:atlantic-north-equatorial-countercurrent':[-42,-38,-35,-32],'current:south-indian':[70,75,80,85,90]}
        for entity,values in expected.items():self.assertEqual([r['longitude_degrees_east'] for r in self.op['sections'] if r['entity_id']==entity],values)
        self.assertEqual(self.op['snapshot_times_utc'],['2022-01-15T00:00:00Z','2022-07-15T00:00:00Z'])

    def test_primary_and_surface_gates_are_declared_before_fields(self):
        for entity,c in self.op['currents'].items():
            self.assertEqual(c['component_bearing_degrees_true'],90)
            self.assertEqual(c['primary_threshold_m_s'],.05 if entity=='current:south-indian' else .1)
            self.assertEqual(c['surface_component_gate_m_s'],.02 if entity=='current:south-indian' else .05)

    def test_full32_slice_budget_leaves_bounded_retry_reserve(self):
        plans,pairs=s.preflight(np.arange(-80,90.001,.04),np.arange(0,360,.08),self.op)
        self.assertEqual(len(plans),16);self.assertLess(pairs,250000)
        self.assertEqual(pairs,2*sum(40*len(p['latitude_indices']) for p in plans))
        self.assertLess(pairs*16,self.op['maximum_total_decoded_velocity_bytes'])
        self.assertEqual(self.op['maximum_component_read_attempts'],3)

    def test_no_thermal_annual_physical_or_volume_promotion(self):
        self.assertFalse(any(self.op['eligibility'].values()));self.assertFalse(self.op['full_goal_complete'])
        for c in self.op['currents'].values():self.assertIsNone(c['temperature_gate'])


if __name__=='__main__':unittest.main()
