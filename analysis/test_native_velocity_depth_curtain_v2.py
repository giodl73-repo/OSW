"""Generalized source threshold preserves v1 exact behavior and native graph rules."""
import copy,json,unittest
import native_velocity_depth_curtain_v2 as new
import derive_barents_makassar_velocity_curtains_v1 as old


class ExplicitThreshold(unittest.TestCase):
    def test_diagonal_and_missing_do_not_bridge_at_five_cm(self):
        self.assertEqual(new.component([0,10,20],[[.07,None,0],[None,.08,0],[0,0,0]],0,0,.05),{(0,0)})
    def test_strict_source_threshold_not_equality(self):
        for t in [.05,.1]:self.assertEqual(new.component([0,10],[[t+.01,t],[t,t+.02],[0,0]],0,0,t),{(0,0)})
    def test_threshold_is_not_rescaled_to_old_threshold(self):
        values=[[.06,.05],[.05,.07],[0,0]];self.assertEqual(new.component([0,10],values,0,0,.05),{(0,0)})
        with self.assertRaises(ValueError):new.component([0,10],values,0,0,.1)
    def test_invalid_threshold_and_unqualified_seed_rejected(self):
        for t in [0,-.1,float('nan'),float('inf'),True]:
            with self.assertRaises(ValueError):new.component([0,10],[[.2,0],[0,0],[0,0]],0,0,t)
    def test_native_detour_preserves_separate_vertical_runs(self):
        nodes=new.component([0,10,20],[[.06,0,.08],[.07,.07,.07],[0,0,0]],0,0,.05);self.assertEqual(new.runs(nodes,0),[[0,0],[2,2]])
    def test_frozen_vertical_boundary_and_run_routines_reused(self):
        self.assertIs(new.runs,old.runs);self.assertIs(new.connected_layer,old.connected_layer);self.assertIs(new.validate_retained,old.validate_retained)
    def test_all32_v1_source_cases_and_full_results_exact_at_ten_cm(self):
        op=json.loads((old.ROOT/old.OPERATOR).read_bytes());original=json.loads((old.ROOT/op['source_operator']).read_bytes())
        for file in op['section_files']:
            section=json.loads((old.ROOT/file).read_bytes());config={**original,**original['currents'][section['entity_id']]};self.assertEqual(config['primary_threshold_m_s'],.1);self.assertEqual(new.curtain(section,config,file),old.curtain(section,config,file))
    def test_source_threshold_missing_or_duplicate_rejected(self):
        for config in [{'primary_threshold_m_s':.05,'thresholds_m_s':[.1,.2]},{'primary_threshold_m_s':.05,'thresholds_m_s':[.05,.05,.1]}]:
            with self.assertRaises(ValueError):new.curtain({},config,'synthetic')


if __name__=='__main__':unittest.main()
