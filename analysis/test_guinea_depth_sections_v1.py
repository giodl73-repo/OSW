import json
import unittest
import numpy as np
import acquire_zonal_current_depth_sections_v1 as s


class GuineaDepthRulesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((s.ROOT/'research/guinea-depth-sections-operator-v1.json').read_bytes())

    def test_regional_identity_and_original_sections(self):
        self.assertEqual(set(self.op['currents']), {'current:guinea'})
        self.assertEqual([r['longitude_degrees_east'] for r in self.op['sections']],[-8,-6,-4,-2.5,-1,0,2])
        self.assertTrue(all(r['entity_id']=='current:guinea' for r in self.op['sections']))
        self.assertEqual(self.op['snapshot_times_utc'],['2022-01-15T00:00:00Z','2022-07-15T00:00:00Z'])

    def test_surface_qualification_does_not_target_undercurrent(self):
        c=self.op['currents']['current:guinea']
        self.assertEqual(c['component_bearing_degrees_true'],90)
        self.assertEqual(c['primary_threshold_m_s'],.1)
        self.assertEqual(c['surface_component_gate_m_s'],.05)
        self.assertIsNone(c['temperature_gate'])
        self.assertEqual(self.op['core_search_depth_interval_m'],[0,200])

    def test_preflight_all_dates_inside_original_caps(self):
        plans,pairs=s.preflight(np.arange(-80,90.001,.04),np.arange(0,360,.08),self.op)
        self.assertEqual(len(plans),7)
        self.assertEqual(pairs,2*sum(40*len(p['latitude_indices']) for p in plans))
        self.assertLess(pairs,250000)
        self.assertLess(pairs*16,7000000)
        self.assertEqual(self.op['maximum_component_read_attempts'],3)

    def test_no_physical_or_annual_promotion(self):
        self.assertFalse(any(self.op['eligibility'].values()))
        self.assertFalse(self.op['full_goal_complete'])
        self.assertIn('shallow',self.op['geometry_provenance'])


if __name__=='__main__':unittest.main()
