import json
import unittest
import numpy as np
import acquire_zonal_current_depth_sections_v1 as s


class NECSubarcticDeclaredRulesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.op=json.loads((s.ROOT/'research/nec-subarctic-depth-sections-operator-v1.json').read_bytes())

    def test_basin_members_and_distinct_eastward_subarctic_scope(self):
        self.assertEqual(set(self.op['currents']),{'current:pacific-north-equatorial','current:atlantic-north-equatorial','current:aleutian'})
        self.assertNotIn('current:north-equatorial',self.op['currents'])
        self.assertNotIn('current:alaskan-stream',self.op['currents'])
        self.assertEqual(len(self.op['sections']),17)
        self.assertEqual(len({(r['entity_id'],r['id']) for r in self.op['sections']}),17)

    def test_declared_longitude_order_preserves_opposite_downstream_directions(self):
        expected={'current:pacific-north-equatorial':[-170,180,170,160,150,140,130],
                  'current:atlantic-north-equatorial':[-27,-35,-45,-55],
                  'current:aleutian':[175,180,-170,-160,-150,-140]}
        for entity,values in expected.items():self.assertEqual([r['longitude_degrees_east'] for r in self.op['sections'] if r['entity_id']==entity],values)

    def test_westward_and_eastward_frames_keep_deep_counterflow_signed(self):
        u=np.array([-.4,.3]);v=np.zeros_like(u)
        np.testing.assert_allclose(s.along_velocity(u,v,270),[.4,-.3],rtol=0,atol=1e-15)
        np.testing.assert_allclose(s.along_velocity(u,v,90),[-.4,.3],rtol=0,atol=1e-15)
        for entity,c in self.op['currents'].items():
            self.assertEqual(c['component_bearing_degrees_true'],90 if entity=='current:aleutian' else 270)
            self.assertEqual(c['primary_threshold_m_s'],.05 if entity=='current:aleutian' else .1)
            self.assertEqual(c['surface_component_gate_m_s'],.02 if entity=='current:aleutian' else .05)

    def test_full34_slice_budget_is_declared_before_any_fields(self):
        plans,pairs=s.preflight(np.arange(-80,90.001,.04),np.arange(0,360,.08),self.op)
        self.assertEqual(len(plans),17);self.assertLessEqual(pairs,250000)
        self.assertEqual(pairs,2*sum(40*len(p['latitude_indices']) for p in plans))
        self.assertLess(pairs*16,7000000)

    def test_no_thermal_seasonal_volume_or_family_inheritance_promotion(self):
        self.assertFalse(any(self.op['eligibility'].values()));self.assertFalse(self.op['full_goal_complete'])
        for c in self.op['currents'].values():self.assertIsNone(c['temperature_gate'])
        self.assertEqual(self.op['snapshot_times_utc'],['2022-01-15T00:00:00Z','2022-07-15T00:00:00Z'])


if __name__=='__main__':unittest.main()
