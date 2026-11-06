"""Dry-run the source-bound append on audited metadata and synthetic peers only."""
import copy
import unittest

import south_java_reference_query_v1 as query


class ReferenceAdmission(unittest.TestCase):
    def fixture(self):
        doc = query.build_contract()
        sources = copy.deepcopy(doc['prior_owner_sources'])
        sources += [{'id': 'fixture:source:' + str(i)} for i in range(210 - len(sources))]
        collections = {
            'sources': sources,
            'objects': [copy.deepcopy(doc['prior_owner']), {'id': 'current:peer', 'payload': ['preserve']}],
            'entities': [copy.deepcopy(doc['prior_entity']), {'id': 'current:peer'}],
            'route_decisions': [copy.deepcopy(doc['prior_decision']),
                {'id': 'route-decision:peer', 'entity_id': 'current:peer', 'payload': ['preserve']}],
            'reference_routes': [{'id': 'fixture:route:' + str(i), 'current_id': 'fixture-peer'} for i in range(81)],
            'widths': [{'id': 'fixture:width', 'value': 123, 'scope': 'unchanged'}],
            'width_samples': [{'id': 'fixture:sample', 'month': 8, 'value': 34}],
            'current_model_analysis_layers': [{'id': 'fixture:layer', 'layer': [0, 150]}]}
        return doc, collections

    def refused_without_mutation(self, doc, collections, parent=query.PARENT):
        before = copy.deepcopy(collections)
        with self.assertRaises(ValueError):
            query.append(collections, doc, parent_logical_sha256=parent)
        self.assertEqual(collections, before)

    def test_append_reuses_publications_and_preserves_all_other_evidence(self):
        doc, collections = self.fixture()
        before = copy.deepcopy(collections)
        result = query.append(collections, doc, parent_logical_sha256=query.PARENT)
        self.assertEqual(result['existing_publications_reused'], 2)
        self.assertFalse(result['installed'])
        self.assertEqual(len(collections['sources']), 211)
        self.assertEqual(collections['sources'][:210], before['sources'])
        self.assertEqual(len(collections['reference_routes']), 82)
        self.assertEqual(collections['reference_routes'][:81], before['reference_routes'])
        for key in ['entities', 'widths', 'width_samples', 'current_model_analysis_layers']:
            self.assertEqual(collections[key], before[key])
        self.assertEqual(collections['objects'][1], before['objects'][1])
        self.assertEqual(collections['route_decisions'][1], before['route_decisions'][1])
        owner = collections['objects'][0]
        for key in ['published_length_km', 'width_ids', 'width_sample_ids', 'model_analysis_layer_ids',
                    'model_depth_context_ids', 'state_codes', 'latest_observation_date']:
            self.assertEqual(owner[key], before['objects'][0][key])
        caps = copy.deepcopy(before['objects'][0]['capabilities'])
        caps['reference_route'] = 1
        self.assertEqual(owner['capabilities'], caps)
        self.assertEqual(owner['route_url'], query.atlas_url())
        self.assertEqual(owner['fingerprint'], query.fingerprint({k: v for k, v in owner.items() if k != 'fingerprint'}))
        self.assertEqual(collections['route_decisions'][0]['prior_route_decision'], doc['prior_decision'])

    def test_repeat_admission_refused_atomically(self):
        doc, collections = self.fixture()
        query.append(collections, doc, parent_logical_sha256=query.PARENT)
        self.refused_without_mutation(doc, collections)

    def test_changed_owner_refused_atomically(self):
        doc, collections = self.fixture()
        collections['objects'][0]['capabilities']['scoped_width'] = 1
        self.refused_without_mutation(doc, collections)

    def test_changed_publication_refused_atomically(self):
        doc, collections = self.fixture()
        paper = next(r for r in collections['sources'] if r['id'] == doc['route']['source_id'])
        paper['label'] = 'changed source'
        self.refused_without_mutation(doc, collections)

    def test_duplicate_publication_refused_atomically(self):
        doc, collections = self.fixture()
        paper = copy.deepcopy(doc['existing_publications']['iskandar_2006'])
        paper['id'] = 'fixture:duplicate-paper'
        collections['sources'][-1] = paper
        self.refused_without_mutation(doc, collections)

    def test_method_collision_refused_atomically(self):
        doc, collections = self.fixture()
        collections['sources'][-1] = copy.deepcopy(doc['method_source'])
        self.refused_without_mutation(doc, collections)

    def test_wrong_parent_and_changed_scientific_scope_refused(self):
        doc, collections = self.fixture()
        self.refused_without_mutation(doc, collections, parent='0' * 64)
        doc['route']['physical_width_km'] = 100
        self.refused_without_mutation(doc, collections)

    def test_prepared_and_delivered_page_keep_distinct_navigation_states(self):
        doc = query.build_contract()
        prepared = query.support_page(doc)
        delivered = query.support_page(doc, installed=True)
        self.assertIn('awaiting query integration', prepared)
        self.assertNotIn('atlas-route=', prepared)
        self.assertIn('atlas-route=', delivered)
        self.assertIn('inspect=', delivered)
        for text in ['editorial', 'not a measurement of the entire', 'not a seasonal range', query.COMPACT, query.FIGURE]:
            self.assertIn(text, prepared)
            self.assertIn(text, delivered)


if __name__ == '__main__':
    unittest.main()
