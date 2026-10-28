"""Bounded append/refusal checks from selected metadata; no installed packet load."""
import copy
import unittest
import wicc_winter_reference_query_v1 as query


class WiccReferenceContract(unittest.TestCase):
    def setUp(self):
        self.contract = query.build_contract()
        selected = self.contract['prior_records']
        starts = {'sources': selected['owner_sources'], 'reference_routes': [],
                  'objects': [selected['owner']], 'entities': [selected['entity']],
                  'route_decisions': [selected['planning_decision']], 'widths': selected['widths']}
        self.parent = {}
        for name, rows in starts.items():
            count = self.contract['parent_collection_counts'][name]
            self.parent[name] = copy.deepcopy(rows) + [{'id': f'fixture:{name}:{i}'} for i in range(count-len(rows))]
        self.parent['direction_and_regime_sentinel'] = [{'id': 'retain', 'content': [None, 'unchanged']}]

    def append(self):
        return query.append(self.parent, self.contract, parent_logical_sha256=query.PARENT)

    def test_exact_regional_append_preserves_width_and_every_prior_record(self):
        before = copy.deepcopy(self.parent)
        result = self.append()
        self.assertEqual(self.parent, before)
        self.assertEqual(result['widths'], before['widths'])
        self.assertEqual(result['entities'], before['entities'])
        self.assertEqual(result['sources'][:-3], before['sources'])
        self.assertEqual(result['reference_routes'][:-1], before['reference_routes'])
        for name in ['objects', 'route_decisions']:
            self.assertEqual(result[name][1:], before[name][1:])
        self.assertEqual(result['direction_and_regime_sentinel'], before['direction_and_regime_sentinel'])
        owner = result['objects'][0]
        self.assertEqual(owner['width_ids'], before['objects'][0]['width_ids'])
        self.assertEqual(owner['section_fingerprints']['measurements'], before['objects'][0]['section_fingerprints']['measurements'])
        self.assertEqual(owner['route_ids'], [query.ROUTE])
        self.assertEqual(owner['capabilities']['reference_route'], 1)
        route = result['reference_routes'][-1]
        for key in ['scenario_range_km', 'uncertainty_km', 'annual_length_range_km', 'whole_current_length_km', 'physical_width_km']:
            self.assertIsNone(route[key])
        self.assertFalse(route['physical_state_join_eligible'])
        self.assertFalse(route['seasonal_playback_eligible'])

    def test_wrong_parent_refused(self):
        with self.assertRaises(ValueError):
            query.append(self.parent, self.contract, parent_logical_sha256='0'*64)

    def test_fabricated_sensitivity_refused(self):
        self.contract['route']['scenario_range_km'] = [1500, 1600]
        with self.assertRaises(ValueError):
            self.append()

    def test_existing_publication_requires_reconciliation(self):
        self.parent['sources'][-1] = {'id': 'fixture:publication', 'doi': '10.1016/0198-0149(91)90087-V'}
        with self.assertRaises(ValueError):
            self.append()

    def test_exact_title_without_identifier_requires_reconciliation(self):
        self.parent['sources'][-1] = {'id': 'fixture:title', 'title': self.contract['new_sources'][0]['title'].upper()}
        with self.assertRaises(ValueError):
            self.append()

    def test_changed_installed_width_refused(self):
        self.parent['widths'][0]['reported_width_km'] = 151
        with self.assertRaises(ValueError):
            self.append()

    def test_duplicate_id_refused(self):
        self.parent['sources'][-1]['id'] = self.parent['sources'][0]['id']
        with self.assertRaises(ValueError):
            self.append()

    def test_existing_route_refused(self):
        self.parent['reference_routes'][0]['current_id'] = query.CURRENT
        with self.assertRaises(ValueError):
            self.append()


if __name__ == '__main__':
    unittest.main()
