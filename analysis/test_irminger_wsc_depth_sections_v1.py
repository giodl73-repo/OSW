import json
from pathlib import Path
import unittest
import numpy as np
import latitude_depth_section_geometry_v1 as g


class IrmingerWSCRulesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((Path(__file__).resolve().parents[1]/'research/irminger-wsc-depth-sections-operator-v1.json').read_bytes())

    def test_original_members_and_regional_sections(self):
        expected={'current:irminger':[56,58,60,62,64,65],'current:west-spitsbergen':[73,74,75,76,77.25,78,79,79.6]}
        self.assertEqual(set(self.op['currents']),set(expected))
        for entity,values in expected.items():
            self.assertEqual([r['latitude_degrees_north'] for r in self.op['sections'] if r['entity_id']==entity],values)
        self.assertEqual(self.op['snapshot_times_utc'],['2022-01-15T00:00:00Z','2022-07-15T00:00:00Z'])

    def test_fixed_northward_upper_component_gates_do_not_claim_watermass_identity(self):
        for c in self.op['currents'].values():
            self.assertEqual(c['component_bearing_degrees_true'],0)
            self.assertEqual(c['primary_threshold_m_s'],.1)
            self.assertEqual(c['surface_component_gate_m_s'],.05)
            self.assertIsNone(c['temperature_gate'])
        self.assertIn('two cores',self.op['currents']['current:irminger']['branch_scope'])
        self.assertIn('not a current bottom',self.op['currents']['current:west-spitsbergen']['branch_scope'])

    def test_full28_target_preflight_inside_unchanged_caps(self):
        plans,pairs=g.preflight(np.arange(-80,80.001,.04),np.arange(0,360,.08),self.op)
        self.assertEqual(len(plans),14)
        self.assertEqual(pairs,2*sum(40*len(p['longitude_indices']) for p in plans))
        self.assertLess(pairs,250000);self.assertLess(pairs*16,7000000)
        self.assertEqual(self.op['maximum_component_read_attempts'],3)

    def test_no_thermal_observational_annual_or_physical_promotion(self):
        self.assertFalse(any(self.op['eligibility'].values()))
        self.assertEqual(self.op['maximum_total_temperature_scalars'],0)
        self.assertFalse(self.op['full_goal_complete'])


if __name__=='__main__':unittest.main()
