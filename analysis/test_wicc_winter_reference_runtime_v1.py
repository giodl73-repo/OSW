"""Runtime adapter invariants from bounded synthetic lists and audited WICC rows."""
import copy
import unittest
import test_wicc_winter_reference_query_v1 as fixtures
import wicc_winter_reference_runtime_v1 as runtime
import wicc_winter_reference_query_v1 as query


class RuntimeReference(unittest.TestCase):
    def setUp(self):
        fixture = fixtures.WiccReferenceContract()
        fixture.setUp()
        self.parent = fixture.parent
        self.contract = runtime.build_contract()
        self.manifest = {'input_sha256': {runtime.PLANNING: self.contract['input_sha256'][runtime.PLANNING]}}

    def prepare(self):
        runtime.prepare(self.parent, self.manifest, self.contract, parent_logical_sha256=query.PARENT)

    def test_prepare_preserves_large_tables_widths_and_full_planning_mapping(self):
        class MustNotCopy:
            def __deepcopy__(self, memo):
                raise AssertionError('Unrelated large table copied')
        sentinel = MustNotCopy()
        self.parent['unrelated_large_table'] = sentinel
        widths = self.parent['widths']
        entities = self.parent['entities']
        self.prepare()
        self.assertIs(self.parent['unrelated_large_table'], sentinel)
        self.assertIs(self.parent['widths'], widths)
        self.assertIs(self.parent['entities'], entities)
        decision = self.parent['route_decisions'][0]
        for key, source_key in [('current_id', 'current_id'), ('label', 'name'), ('strategy_id', 'route_strategy_id'),
            ('strategy_label', 'route_strategy_label'), ('construction_status', 'reference_path_decision'),
            ('route_ids', 'candidate_ids'), ('next_action', 'next_action'), ('scope', 'existing_scope'),
            ('status', 'planning_status'), ('source_url', 'name_source_url')]:
            self.assertEqual(decision[key], decision['source_decision'][source_key], key)
        self.assertEqual(self.manifest[runtime.KEY], runtime.marker(self.contract))

    def test_changed_planning_receipt_refuses_before_mutation(self):
        self.manifest['input_sha256'][runtime.PLANNING] = '0'*64
        before = copy.deepcopy(self.parent)
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertEqual(self.parent, before)

    def test_repeated_append_refused(self):
        self.prepare()
        with self.assertRaises(ValueError):
            self.prepare()

    def test_dashboard_preserves_measurement_fingerprint(self):
        before, after = self.contract['dashboard_before'], self.contract['dashboard_after']
        self.assertEqual(before['section_fingerprints']['measurements'], after['section_fingerprints']['measurements'])
        self.assertNotEqual(before['fingerprint'], after['fingerprint'])
        self.assertEqual(after['capabilities']['reference_route'], 1)
        self.assertEqual(before['capabilities']['reference_route'], 0)

    def test_catalogue_appends_card_without_rank_or_seasonal_support(self):
        old = {'candidates': [{'id': 'retained', 'current_id': 'other'}],
               'remaining_current_decisions': [self.contract['original_planning_source']],
               'reference_route_length_order': ['retained'],
               'counts': {'route_candidates': 82, 'currents_with_route_candidates': 75,
                          'currents_without_route_candidates': 31, 'currents_without_any_reference_card': 31},
               'planning_taxonomy': {'strategies': [{'id': self.contract['final_decision']['strategy_id'], 'unbuilt_count': 7}]}}
        saved = copy.deepcopy(old)
        result = runtime.catalog_projection(old, self.contract)
        self.assertEqual(old, saved)
        self.assertEqual(result['reference_route_length_order'], old['reference_route_length_order'])
        self.assertIsNone(result['candidates'][-1]['scenario_range_km'])
        self.assertFalse(result['candidates'][-1]['seasonal_playback_eligible'])
        self.assertEqual(result['counts']['route_candidates'], 83)
        self.assertEqual(result['counts']['currents_with_route_candidates'], 76)


if __name__ == '__main__':
    unittest.main()
