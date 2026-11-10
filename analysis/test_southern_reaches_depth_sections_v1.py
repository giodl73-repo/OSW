import json
import unittest
import numpy as np
import acquire_zonal_current_depth_sections_v1 as s


class SouthernReachDepthRulesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((s.ROOT/'research/southern-reaches-depth-sections-operator-v1.json').read_bytes())

    def test_distinct_regions_and_all_original_sections(self):
        self.assertEqual(set(self.op['currents']),{'current:south-pacific','current:south-australian'})
        expected={'current:south-pacific':[-103,-100,-96,-92,-88],'current:south-australian':[135.5,138,140,142.5]}
        for owner,values in expected.items():
            self.assertEqual([r['longitude_degrees_east'] for r in self.op['sections'] if r['entity_id']==owner],values)
        self.assertEqual(self.op['snapshot_times_utc'],['2022-01-15T00:00:00Z','2022-07-15T00:00:00Z'])

    def test_weak_and_reversing_flow_does_not_change_declared_frame_or_cutoff(self):
        for c in self.op['currents'].values():
            self.assertEqual(c['component_bearing_degrees_true'],90)
            self.assertEqual(c['primary_threshold_m_s'],.05)
            self.assertEqual(c['surface_component_gate_m_s'],.02)
            self.assertIsNone(c['temperature_gate'])
        self.assertIn('no sign flip',self.op['currents']['current:south-australian']['branch_scope'])
        self.assertIn('not current depth boundaries',self.op['currents']['current:south-pacific']['branch_scope'])

    def test_complete_original_preflight_inside_frozen_caps(self):
        plans,pairs=s.preflight(np.arange(-80,90.001,.04),np.arange(0,360,.08),self.op)
        self.assertEqual(len(plans),9)
        self.assertEqual(pairs,2*sum(40*len(p['latitude_indices']) for p in plans))
        self.assertLess(pairs,250000)
        self.assertLess(pairs*16,7000000)
        self.assertEqual(self.op['maximum_component_read_attempts'],3)

    def test_no_physical_thermal_or_annual_promotion(self):
        self.assertFalse(any(self.op['eligibility'].values()))
        self.assertFalse(self.op['full_goal_complete'])
        self.assertIn('shallow',self.op['geometry_provenance'])


if __name__=='__main__':unittest.main()
