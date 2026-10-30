"""Scientific scope and complete-response preservation without loading packets."""
import copy
import unittest
import pacific_sec_jet_widths_query_v1 as query
import pacific_sec_jet_widths_delivery_rules_v1 as rules
from check_pacific_sec_jet_widths_delivery_v1 import new_requests
import pacific_sec_jet_widths_index_v1 as index


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.contract = query.build_contract()

    def test_distinct_components_and_unknowns_survive_scene(self):
        rows = self.contract['width_records']
        scene = rules.scene(rows, query.OWNERS[0], self.contract)
        self.assertEqual(scene['width_records'], rows)
        self.assertIn('17 July–17 October 2005', scene['scope'])
        self.assertIn('0–600 m', scene['scope'])
        self.assertNotIn('2003', scene['scope'])
        self.assertNotIn('27°W', scene['scope'])
        self.assertEqual({r['approximate_width_km'] for r in rows}, {100, 300})
        self.assertEqual(len({r['phase_label'] for r in rows}), 2)
        self.assertTrue(all(r['annual_width_range_km'] is None for r in rows))

    def test_pagination_preserves_matching_context_without_family_inheritance(self):
        request = {'collection': 'widths', 'filters': [
            {'field': 'current_id', 'op': 'eq', 'value': 'pacific-south-equatorial'}],
            'limit': 1, 'offset': 1}
        old = {'total': 0, 'rows': [], 'chart_scene': None, 'map_scene': None}
        result = rules.expected_query(request, old, self.contract, {'widths': []})
        self.assertEqual(result['total'], 2)
        self.assertEqual(len(result['rows']), 1)
        self.assertEqual(len(result['chart_scene']['width_records']), 2)
        request['filters'][0]['value'] = 'south-equatorial'
        self.assertEqual(rules.expected_query(request, old, self.contract, {'widths': []}), old)

    def test_dashboard_updates_only_owner_and_preserves_characteristic_evidence(self):
        entries = [copy.deepcopy(v['objects'][0]) for v in self.contract['prior_owners'].values()]
        old = {'entries': entries, 'snapshot_fingerprint': 'parent',
               'published_characteristic_velocities_v1': {'records': 10}}
        before = copy.deepcopy(old)
        after = rules.dashboard_document(old, self.contract)
        self.assertEqual(old, before)
        self.assertEqual(after['published_characteristic_velocities_v1'], before['published_characteristic_velocities_v1'])
        self.assertEqual(next(r for r in after['entries'] if r['id'] == query.FAMILY),
                         next(r for r in before['entries'] if r['id'] == query.FAMILY))
        owner = next(r for r in after['entries'] if r['id'] == query.OWNERS[0])
        self.assertEqual(owner['capabilities']['scoped_width'], 2)

    def test_extension_preserves_unrelated_measurements_and_sources(self):
        doc = copy.deepcopy(self.contract)
        rows = {name: [] for name in doc['parent_collection_counts']}
        rows['sources'] = copy.deepcopy(doc['prior_source_inventory']) + [{'id': 'source:unrelated', 'note': 'preserve'}]
        for prior in doc['prior_owners'].values():
            for name in ('objects', 'entities', 'widths'):
                rows[name].extend(copy.deepcopy(prior[name]))
        rows['current_speed_statistics'] = [{'id': 'old-speed', 'mean': .83}]
        doc['parent_collection_counts'] = {name: len(values) for name, values in rows.items()}
        parent = {'schema': 'osw.query-bundle.v1', 'collections': rows, 'manifest': {'input_sha256': {}}}
        collections, manifest = query.apply_verified(rows, parent['manifest'], doc,
            parent_logical_sha256=query.PARENT, contract_sha256=query.digest(doc))
        child = {**parent, 'collections': collections, 'manifest': manifest}
        rules.verify_extension(parent, child, doc)
        for name in ('current_speed_statistics', 'sources'):
            broken = copy.deepcopy(child)
            broken['collections'][name][0]['changed'] = True
            with self.assertRaises(ValueError):
                rules.verify_extension(parent, broken, doc)

    def test_complete_historical_cases_are_extended_with_explicit_new_scopes(self):
        cases = new_requests(self.contract)
        self.assertEqual(len(cases), 11)
        self.assertEqual(sum(r['kind'] == 'query' for r in cases), 6)
        self.assertEqual(sum(r['kind'] == 'object' for r in cases), 2)
        self.assertEqual({r['name'] for r in cases if r['kind'] == 'snapshot'}, {'atlas', 'seasons', 'dashboard'})
        self.assertEqual(len(index.DOCUMENTS), 4)
        good = {'original_sources_verified': 668, 'original_source_strings_preserved': 668,
                'replaced_source_paths': [], 'added_source_paths': index.DOCUMENTS,
                'scientific_source_documents_replaced': 0}
        index.verify_audit(good)
        with self.assertRaises(ValueError):
            index.verify_audit({**good, 'original_source_strings_preserved': 667})


if __name__ == '__main__':
    unittest.main()
