import json
from pathlib import Path
import unittest
import audit_current_depth_north_cape_selection_v1 as a
from interval_depth_diagnostic_v1 import selection


class NorthCapeSelectionAuditTests(unittest.TestCase):
    def result(self,column):
        z=[0,50,100,200,350,500];config={'selection_depth_interval_m':[50,350],'core_search_depth_interval_m':[50,350],'surface_component_gate_m_s':None,'primary_threshold_m_s':.1}
        scores=selection(z,[column,column,column],config)['candidate_scores']
        return a.classify(z,column,scores[0],config,[[0,200],[50,200],[50,350]])

    def test_incomplete_original_interval_can_have_complete_upper_support_without_reselection(self):
        result=self.result([0,.2,.2,.2,None,None])
        self.assertEqual(result['category'],'incomplete_original_selection_interval')
        self.assertIsNone(result['original_core_peak_component_m_s'])
        self.assertTrue(result['native_support_by_window']['50_200']);self.assertFalse(result['native_support_by_window']['50_350'])

    def test_positive_but_subthreshold_is_distinct_from_incomplete_support(self):
        result=self.result([0,.05,.05,.05,.05,0])
        self.assertEqual(result['category'],'positive_integral_but_subthreshold_core')
        self.assertTrue(result['native_support_by_window']['50_350'])

    def test_nonpositive_integrals_with_and_without_qualifying_core_are_distinct(self):
        self.assertEqual(self.result([0,-.4,.2,-.4,-.4,0])['category'],'qualifying_core_but_nonpositive_integral')
        self.assertEqual(self.result([0,-.2,-.2,-.2,-.2,0])['category'],'subthreshold_core_and_nonpositive_integral')

    def test_original_eligible_category_and_native_endpoint_validation(self):
        self.assertEqual(self.result([0,.2,.2,.2,.2,0])['category'],'eligible_original_diagnostic')
        with self.assertRaises(ValueError):a.support([0,50,200],[0,.2,.2],[50,350])

    def test_actual_audit_preserves_all16_cases_and_only_one_published_eligible_node(self):
        report=a.build();counts=report['counts']
        self.assertEqual(counts['section_date_cases'],16);self.assertEqual(counts['native_velocity_profiles'],1200)
        self.assertEqual(sum(counts['category_counts'].values()),1200);self.assertEqual(counts['original_lower_projectable_nodes'],1)
        self.assertFalse(report['alternative_selection_evaluated']);self.assertFalse(report['current_absence_established'])
        self.assertFalse(report['seabed_inferred_from_missing_support']);self.assertEqual(report['new_projected_depths'],0)
        self.assertEqual(len({(s['snapshot_time_utc'],s['section_id']) for s in report['sections']}),16)

    def test_pinned_source_byte_mutation_rejected_before_analysis(self):
        op=json.loads((a.ROOT/a.OPERATOR).read_bytes());target=op['section_files'][0]
        def reader(f):return (a.ROOT/f).read_bytes()+(b' ' if f==target else b'')
        with self.assertRaises(ValueError):a.build(reader)


if __name__=='__main__':unittest.main()
