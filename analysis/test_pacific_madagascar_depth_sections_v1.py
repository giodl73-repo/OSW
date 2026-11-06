import json
import unittest
import numpy as np
import acquire_three_current_depth_sections_v1 as s


class PacificMadagascarDeclaredSectionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((s.ROOT/'research/pacific-madagascar-depth-sections-operator-v1.json').read_bytes())

    def test_declared_original_section_date_coverage_and_unique_keys(self):
        self.assertEqual(set(self.op['currents']),{'current:california','current:alaska','current:southern-east-madagascar'})
        sections=self.op['sections'];self.assertEqual(len(sections),20)
        self.assertEqual(len({(r['entity_id'],r['id']) for r in sections}),20)
        self.assertEqual(self.op['snapshot_times_utc'],['2022-01-15T00:00:00Z','2022-07-15T00:00:00Z'])
        self.assertEqual([r['latitude_degrees_north'] for r in sections if r['entity_id']=='current:california'],[43,40,37,34,31,28,25,23])
        self.assertEqual([r['latitude_degrees_north'] for r in sections if r['entity_id']=='current:alaska'],[48,50,52,54,56,57])
        self.assertEqual([r['latitude_degrees_north'] for r in sections if r['entity_id']=='current:southern-east-madagascar'],[-20,-21,-22,-23,-24,-25.5])

    def test_separate_weak_current_and_jet_gates_are_used_by_frozen_selector(self):
        z=[0,100,200,400];columns=[[.025,.03,.025,-.1],[.04,.08,.04,-.1],[.03,.04,.03,-.1]]
        for entity in ['current:california','current:alaska']:
            config={**self.op,**self.op['currents'][entity]}
            self.assertEqual(config['surface_component_gate_m_s'],.02);self.assertEqual(config['primary_threshold_m_s'],.05)
            self.assertEqual(s.selection(z,columns,config)['selected_column_index'],1)
            self.assertIsNone(s.selection(z,columns,{**config,'surface_component_gate_m_s':.05})['selected_column_index'])
        config={**self.op,**self.op['currents']['current:southern-east-madagascar']}
        self.assertEqual(config['surface_component_gate_m_s'],.05);self.assertEqual(config['primary_threshold_m_s'],.1)
        self.assertIsNone(s.selection(z,columns,config)['selected_column_index'])

    def test_fixed_north_and_south_components_preserve_return_flow(self):
        u=np.array([.3,-.3]);v=np.array([.4,-.4])
        np.testing.assert_array_equal(s.along_velocity(u,v,0),v)
        np.testing.assert_allclose(s.along_velocity(u,v,180),-v,rtol=0,atol=1e-15)
        self.assertEqual(self.op['currents']['current:alaska']['component_bearing_degrees_true'],0)
        for entity in ['current:california','current:southern-east-madagascar']:
            self.assertEqual(self.op['currents'][entity]['component_bearing_degrees_true'],180)

    def test_all_declared_gates_fit_bounded_native_slice_budget(self):
        axis=np.arange(0.,360.,.08);used=0
        for stamp in self.op['snapshot_times_utc']:
            for section in self.op['sections']:
                indices=s.longitude_indices(axis,section['longitude_gate_degrees_east'])
                used+=s.check_budget((40,1,len(indices)),used,self.op['maximum_total_cell_pairs'])
        self.assertLess(used,self.op['maximum_total_cell_pairs'])
        self.assertLess(used*16,self.op['maximum_total_decoded_velocity_bytes'])

    def test_no_temperature_or_physical_or_seasonal_admission(self):
        self.assertFalse(any(self.op['eligibility'].values()))
        self.assertEqual(self.op['maximum_total_temperature_scalars'],0)
        self.assertEqual(self.op['maximum_total_decoded_temperature_bytes'],0)
        for config in self.op['currents'].values():self.assertIsNone(config['temperature_gate'])
        self.assertFalse(self.op['full_goal_complete'])


if __name__=='__main__':unittest.main()
