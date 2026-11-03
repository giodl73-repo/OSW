"""Check native topology and exact reproduction on the complete retained cohort."""
import unittest
import derive_barents_makassar_velocity_curtains_v1 as derive


class Curtains(unittest.TestCase):
    def test_diagonal_and_missing_do_not_bridge(self):
        self.assertEqual(derive.component([0,10,20],[[.2,None,0],[None,.3,0],[0,0,0]],0,0),{(0,0)})
    def test_detour_preserves_separate_vertical_runs(self):
        nodes=derive.component([0,10,20],[[.2,0,.3],[.2,.2,.2],[0,0,0]],0,0)
        self.assertEqual(derive.runs(nodes,0),[[0,0],[2,2]])
    def test_strict_threshold_excludes_equality(self):
        self.assertEqual(derive.component([0,10],[[.2,.1],[.1,.3],[0,0]],0,0),{(0,0)})
    def test_invalid_and_unqualified_original_core_rejected(self):
        for values in [[[0,0],[0,0],[0,0]],[[float('nan'),0],[0,0],[0,0]]]:
            with self.assertRaises(ValueError):derive.component([0,10],values,0,0)
    def test_full32cases_geometry_rotation_selection_and_original_boundaries(self):
        report,raw=derive.build();self.assertEqual(report['counts']['cases'],32);self.assertLess(len(raw),2400000)
        self.assertEqual({c['entity_id'] for c in report['cases']},{'current:north-cape','current:indonesian-throughflow'})
        self.assertEqual(report['counts']['new_ocean_field_requests'],0)
        for case in report['cases']:
            self.assertFalse(case['core_reselected']);self.assertFalse(case['physical_current_bottom_established']);self.assertIsNone(case['volume_m3'])
            if case['columns']:self.assertEqual(sum(r['contains_original_core'] for col in case['columns'] for r in col['connected_depth_runs']),1)


if __name__=='__main__':unittest.main()
