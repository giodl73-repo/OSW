import json
from pathlib import Path
import unittest
import numpy as np
import latitude_depth_section_geometry_v1 as g


class MalvinasEACCRulesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((Path(__file__).resolve().parents[1]/'research/malvinas-eacc-depth-sections-operator-v1.json').read_bytes())

    def test_distinct_currents_and_all_declared_regional_sections(self):
        expected={'current:falkland':[-49,-47,-45,-43,-41],'current:east-african-coastal':[-10,-8.5,-7,-5.5,-4]}
        self.assertEqual(set(self.op['currents']),set(expected))
        for entity,values in expected.items():
            self.assertEqual([r['latitude_degrees_north'] for r in self.op['sections'] if r['entity_id']==entity],values)
        self.assertEqual(self.op['snapshot_times_utc'],['2022-01-15T00:00:00Z','2022-07-15T00:00:00Z'])

    def test_current_specific_frames_cutoffs_and_all_sensitivity_layers(self):
        expected={'current:falkland':(0,.1,.05),'current:east-african-coastal':(0,.1,.05)}
        for entity,(frame,primary,surface) in expected.items():
            c=self.op['currents'][entity]
            self.assertEqual((c['component_bearing_degrees_true'],c['primary_threshold_m_s'],c['surface_component_gate_m_s']),(frame,primary,surface))
            self.assertIsNone(c['temperature_gate']);self.assertIn(primary,self.op['thresholds_m_s'])
        self.assertEqual(self.op['thresholds_m_s'],[.05,.1,.2])

    def test_full20_target_preflight_under_frozen_caps(self):
        plans,pairs=g.preflight(np.arange(-80,80.001,.04),np.arange(0,360,.08),self.op)
        self.assertEqual(len(plans),10);self.assertEqual(pairs,2*sum(40*len(p['longitude_indices']) for p in plans))
        self.assertLess(pairs,250000);self.assertLess(pairs*16,7000000)
        self.assertEqual(self.op['maximum_component_read_attempts'],3)

    def test_no_bed_observational_annual_or_volume_promotion(self):
        self.assertFalse(any(self.op['eligibility'].values()));self.assertFalse(self.op['full_goal_complete'])
        self.assertEqual(self.op['maximum_total_temperature_scalars'],0)
        self.assertEqual([s['longitude_gate_degrees_east'] for s in self.op['sections'] if s['entity_id']=='current:falkland'],[[-62,-55],[-61,-54],[-61,-54],[-60,-53],[-59,-52]])
        self.assertTrue(all(s['longitude_gate_degrees_east']==[38.5,43.5] for s in self.op['sections'] if s['entity_id']=='current:east-african-coastal'))


if __name__=='__main__':unittest.main()
