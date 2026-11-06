import json
from pathlib import Path
import unittest
import numpy as np
import acquire_zonal_current_depth_sections_v1 as s


class SECBasinDepthRulesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((Path(__file__).resolve().parents[1]/'research/sec-basin-depth-sections-operator-v1.json').read_bytes())

    def test_distinct_basin_members_and_original_partial_reaches(self):
        expected={'current:atlantic-south-equatorial':[-31,-32,-33,-34,-35],
            'current:pacific-south-equatorial':[-100,-110,-120,-130,-140],
            'current:indian-south-equatorial':[90,85,80,75,70]}
        self.assertEqual(set(self.op['currents']),set(expected))
        self.assertNotIn('current:south-equatorial',self.op['currents'])
        for entity,values in expected.items():
            self.assertEqual([r['longitude_degrees_east'] for r in self.op['sections'] if r['entity_id']==entity],values)
        self.assertEqual(self.op['snapshot_times_utc'],['2022-01-15T00:00:00Z','2022-07-15T00:00:00Z'])

    def test_fixed_westward_frames_and_declared_primary_surface_gates(self):
        for c in self.op['currents'].values():
            self.assertEqual(c['component_bearing_degrees_true'],270)
            self.assertEqual(c['primary_threshold_m_s'],.1)
            self.assertEqual(c['surface_component_gate_m_s'],.05)
            self.assertIsNone(c['temperature_gate'])
        self.assertEqual(self.op['thresholds_m_s'],[.05,.1,.2])

    def test_full30_target_preflight_inside_unchanged_caps(self):
        plans,pairs=s.preflight(np.arange(-80,80.001,.04),np.arange(0,360,.08),self.op)
        self.assertEqual(len(plans),15);self.assertEqual(pairs,2*sum(40*len(p['latitude_indices']) for p in plans))
        self.assertLess(pairs,250000);self.assertLess(pairs*16,7000000)
        self.assertEqual(self.op['maximum_component_read_attempts'],3)

    def test_no_thermal_family_physical_or_annual_promotion(self):
        self.assertFalse(any(self.op['eligibility'].values()));self.assertFalse(self.op['full_goal_complete'])
        self.assertEqual(self.op['maximum_total_temperature_scalars'],0)
        expected={'current:atlantic-south-equatorial':[-6.5,-1.5],
            'current:pacific-south-equatorial':[-5.5,-.5],'current:indian-south-equatorial':[-15,-10]}
        for row in self.op['sections']:self.assertEqual(row['latitude_gate_degrees_north'],expected[row['entity_id']])


if __name__=='__main__':unittest.main()
