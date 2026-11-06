"""Planning projection, receipt and atlas checks using small synthetic records."""
import copy
import json
import unittest

import pacific_secc_reference_runtime_v1 as runtime
import pacific_secc_reference_query_v1 as query
from test_pacific_secc_reference_query_v1 import PacificReference

FIXTURE = 'research/pacific-secc-reference-runtime-fixture-v1.json'


def fixture(contract):
    data = PacificReference().base()
    source = copy.deepcopy(contract['original_planning_source'])
    decision = data['route_decisions'][0]
    decision.update(id='route-decision:' + query.CURRENT, source_decision=source,
                    source_catalog_file=runtime.PLANNING, source_catalog_sha256=runtime.PLANNING_SHA,
                    scope_reviews=[])
    for target, origin in [('current_id', 'current_id'), ('label', 'name'), ('strategy_id', 'route_strategy_id'),
                           ('strategy_label', 'route_strategy_label'), ('construction_status', 'reference_path_decision'),
                           ('next_action', 'next_action'), ('scope', 'existing_scope'), ('status', 'planning_status'),
                           ('source_url', 'name_source_url')]:
        decision[target] = source[origin]
    data['objects'][0]['route_decision_ids'] = [decision['id']]
    data['objects'][0]['scope_notes'] = []
    data['route_decisions'] = [decision]
    manifest = {'input_sha256': {runtime.PLANNING: runtime.PLANNING_SHA}}
    return {'schema': 'osw.query-bundle.v1', 'collections': data, 'manifest': manifest}


def applied_fixture(contract):
    result = fixture(contract)
    runtime.prepare(result['collections'], result['manifest'], contract,
                    parent_logical_sha256=runtime.PARENT_LOGICAL)
    return result


class PacificRuntime(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = runtime.build_contract()

    def test_fixed_planning_projection_preserves_original_source_and_physical_owner(self):
        before = fixture(self.contract)
        after = applied_fixture(self.contract)
        decision = after['collections']['route_decisions'][0]
        self.assertEqual(decision['source_url'], decision['source_decision']['name_source_url'])
        self.assertEqual(decision['prior_route_decision'], before['collections']['route_decisions'][0])
        for target, origin in [('route_ids', 'candidate_ids'), ('next_action', 'next_action'),
                               ('construction_status', 'reference_path_decision'), ('source_url', 'name_source_url')]:
            self.assertEqual(decision[target], decision['source_decision'][origin])
        receipt = after['manifest'][runtime.KEY]
        self.assertEqual(receipt['prior_owner'], before['collections']['objects'][0])
        owner = after['collections']['objects'][0]
        self.assertEqual(runtime.sha(receipt['owner_fingerprint_json'].encode()), owner['fingerprint'])
        self.assertEqual(runtime.sha(receipt['section_fingerprint_json'].encode()),
                         owner['section_fingerprints']['pacific_secc_western_reference'])
        self.assertEqual(json.loads(receipt['section_fingerprint_json']), after['collections']['reference_routes'][-1])

    def test_changed_source_parent_and_repeat_are_atomic_across_both_containers(self):
        for change in ['source', 'parent', 'repeat', 'publication']:
            data = fixture(self.contract)
            parent = runtime.PARENT_LOGICAL
            if change == 'source':
                data['collections']['route_decisions'][0]['source_decision']['candidate_ids'] = ['fabricated']
            elif change == 'parent':
                parent = '0' * 64
            elif change == 'repeat':
                runtime.prepare(data['collections'], data['manifest'], self.contract, parent_logical_sha256=parent)
            elif change == 'publication':
                data['collections']['sources'][0]['url'] = 'https://example.org/unrelated'
            before = query.encoded(data)
            with self.assertRaises(ValueError):
                runtime.prepare(data['collections'], data['manifest'], self.contract, parent_logical_sha256=parent)
            self.assertEqual(query.encoded(data), before)

    def test_saved_fixture_reproduces_exactly_and_native_inputs_are_small(self):
        saved = query.ROOT / FIXTURE
        self.assertEqual(saved.read_bytes(), query.encoded(applied_fixture(self.contract)))
        self.assertLess(saved.stat().st_size, 60000)

    def test_atlas_uses_exact_original_plan_and_saved_report(self):
        data = applied_fixture(self.contract)
        source = self.contract['original_planning_source']
        catalog = {'candidates': [], 'remaining_current_decisions': [copy.deepcopy(source)],
                   'counts': {'route_candidates': 80, 'currents_with_route_candidates': 73,
                              'currents_without_route_candidates': 22, 'currents_without_any_reference_card': 22},
                   'planning_taxonomy': {'strategies': [{'id': source['route_strategy_id'], 'unbuilt_count': 9}]}}
        result = runtime.catalog_projection(catalog, data['collections'], self.contract)
        self.assertEqual(result['candidates'][0]['report_inline'], self.contract['atlas_report'])
        self.assertEqual(result['counts']['route_candidates'], 81)
        self.assertEqual(result['remaining_current_decisions'][0]['name_source_url'], query.URL)
        self.assertEqual(result['candidates'][0]['nominal_atlas_state_crossings'], [])
        catalog['remaining_current_decisions'][0]['name_source_url'] = 'https://example.org/wrong'
        with self.assertRaises(ValueError):
            runtime.catalog_projection(catalog, data['collections'], self.contract)


if __name__ == '__main__':
    unittest.main()
