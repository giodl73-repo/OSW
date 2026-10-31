"""Small source-contract and atomic admission checks; no packet, browser or WASM."""
import copy
from html.parser import HTMLParser
import json
import unittest
from urllib.parse import parse_qs, urlsplit

import eicc_reference_query_v1 as query
from render_eicc_reference_page_v1 import page


class EiccReferenceContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = query.build_contract()

    def base(self):
        return {'objects': [
            {'id': query.TARGET, 'type': 'named_current', 'source_ids': ['source:prior'],
             'linked_source_count': 1, 'route_ids': ['prior-route'],
             'route_decision_ids': ['route-decision:east-india-coastal'],
             'capabilities': {'reference_route': 1, 'scoped_width': 1, 'geometry': 0, 'width_samples': 0},
             'map_features': [{'geometry': {'type': 'Point', 'coordinates': [83, 15]}, 'role': 'prior-context'}],
             'evidence_links': [{'label': 'Prior evidence', 'url': 'prior.html'}],
             'section_fingerprints': {'physical_width': 'prior-width'}, 'fingerprint': 'prior-object',
             'published_length_km': None, 'width_ids': ['prior-width'], 'width_sample_ids': [],
             'geometry_ids': [], 'state_codes': ['KEEP'], 'latest_observation_date': None},
            {'id': 'current:other', 'type': 'named_current', 'fingerprint': 'other'}],
            'entities': [{'id': query.TARGET, 'type': 'named_current'}],
            'sources': [{'id': 'source:prior', 'kind': 'external'}],
            query.ROUTES: [{'id': 'prior-route', 'current_id': query.CURRENT, 'source_ids': ['source:prior'],
                            'rank_eligible': False}],
            'route_decisions': [{'id': 'route-decision:east-india-coastal', 'entity_id': query.TARGET,
                'route_ids': ['prior-route'], 'candidate_count': 1, 'rank_eligible': False,
                'construction_status': 'prior-plan', 'source_decision': {'candidate_ids': ['prior-route'],
                'reference_path_decision': 'prior-plan'}, 'scope_reviews': [{'preserve': True}]},
                {'id': 'route-decision:other', 'entity_id': 'current:other', 'untouched': True}],
            'widths': [{'id': 'prior-width', 'value': 100}],
            'width_samples': [{'id': 'other-sample', 'value': None}],
            'length_assessments': [{'id': 'prior-length', 'rank_eligible': False}],
            'geometries': [], 'state_links': [{'id': 'prior-state-link', 'kind': 'context'}]}

    def refused(self, data, document=None):
        before = query.encoded(data)
        with self.assertRaises(ValueError):
            query.append(data, self.contract if document is None else document)
        self.assertEqual(query.encoded(data), before)

    def test_two_reference_conventions_remain_separate_and_nonphysical(self):
        rows = self.contract['collections'][query.ROUTES]
        self.assertEqual([r['approximate_reference_path_km'] for r in rows], [590, 630])
        self.assertEqual([r['computed_nominal_reference_length_km'] for r in rows], [592.240153, 629.734849])
        self.assertEqual([r['coordinates_lon_lat'][-1][1] for r in rows], [18, 18.5])
        for row in rows:
            self.assertEqual(row['scenario_count'], 9)
            self.assertFalse(row['rank_eligible'])
            self.assertFalse(row['physical_current_axis_admitted'])
            self.assertFalse(row['seasonal_playback_eligible'])
            self.assertIsNone(row['annual_length_range_km'])
            self.assertIsNone(row['whole_current_length_km'])
            self.assertIsNone(row['sample_date'])
            self.assertNotIn('working_dataset_admitted', row)

    def test_exact_sampling_points_keep_g_outlet_and_depth_meaning(self):
        rows = self.contract['collections'][query.POINTS]
        self.assertEqual([r['source_track'] for r in rows], [14, 192, 116, 40, 155, 218, 142])
        self.assertEqual([r['reported_bathymetry_m'] for r in rows], [63, 1199, 615, 288, 289, 4252, 4202])
        self.assertTrue(all(r['is_strict_eicc_path_reference'] for r in rows[:6]))
        self.assertFalse(rows[-1]['is_strict_eicc_path_reference'])
        for row in rows:
            self.assertIsNone(row['geometry'])
            self.assertIsNone(row['current_thickness_m'])
            self.assertFalse(row['route_vertex_eligible'])
            self.assertFalse(row['physical_state_join_eligible'])

    def test_spectral_scales_and_theory_never_become_widths(self):
        rows = self.contract['collections'][query.SCALES]
        self.assertEqual([r['value'] for r in rows], [23, 60, 57, 27, 67, 178])
        self.assertEqual([r['reported_theoretical_ro_over_2_km'] for r in rows], [25, 30, 35, 35, 50, 95])
        for row in rows:
            self.assertIsNone(row['paired_current_width_km'])
            self.assertIsNone(row['uncertainty_km'])
            self.assertIsNone(row['annual_width_range_km'])
            self.assertEqual(row['independent_observation_count'], 0)

    def test_map_features_are_only_two_undated_editorial_connections(self):
        features = self.contract['owner_map_features']
        self.assertEqual(len(features), 2)
        self.assertEqual([f['candidate_id'] for f in features], [r['id'] for r in self.contract['collections'][query.ROUTES]])
        for feature in features:
            self.assertEqual(feature['role'], 'editorial_reference_route')
            self.assertIsNone(feature['observation_date'])
            self.assertGreater(len(feature['geometry']['coordinates']), 500)
            self.assertFalse(feature['physical_current_axis_admitted'])

    def test_append_preserves_physical_collections_prior_routes_and_other_owner(self):
        data = self.base(); before = copy.deepcopy(data)
        query.append(data, self.contract)
        for name in set(before) - {'objects', 'sources', query.ROUTES, 'route_decisions'}:
            self.assertEqual(data[name], before[name])
        self.assertEqual(data[query.ROUTES][0], before[query.ROUTES][0])
        self.assertEqual(data['sources'][0], before['sources'][0])
        self.assertEqual(data['objects'][1], before['objects'][1])
        owner = data['objects'][0]
        for key in ['published_length_km', 'width_ids', 'width_sample_ids', 'geometry_ids', 'state_codes', 'latest_observation_date']:
            self.assertEqual(owner[key], before['objects'][0][key])
        self.assertEqual(owner['capabilities']['geometry'], 0)
        self.assertEqual(owner['capabilities']['scoped_width'], 1)
        self.assertEqual(owner['capabilities']['reference_route'], 3)
        self.assertEqual(owner['capabilities']['sampling_reference_points'], 7)
        self.assertEqual(owner['capabilities']['spectral_cross_shore_scales'], 6)
        self.assertEqual(owner['map_features'][:1], before['objects'][0]['map_features'])

    def test_only_owned_editorial_planning_projection_changes_with_exact_history(self):
        data = self.base(); before = copy.deepcopy(data['route_decisions'])
        query.append(data, self.contract)
        decision = data['route_decisions'][0]
        self.assertEqual(decision['prior_route_decision'], before[0])
        self.assertEqual(data['route_decisions'][1], before[1])
        self.assertEqual(decision['candidate_count'], 3)
        self.assertEqual(decision['route_ids'], data['objects'][0]['route_ids'])
        self.assertEqual(decision['source_decision']['candidate_ids'], decision['route_ids'])
        self.assertFalse(decision['rank_eligible'])

    def test_duplicate_and_late_collisions_refused_without_partial_update(self):
        data = self.base(); query.append(data, self.contract); self.refused(data)
        for collection in query.OWNER_FIELDS:
            data = self.base()
            data.setdefault(collection, []).append(copy.deepcopy(self.contract['collections'][collection][-1]))
            self.refused(data)

    def test_prohibited_quantities_dates_geography_and_numeric_false_refused(self):
        mutations = [
            lambda d: d['collections'][query.ROUTES][0].update(whole_current_length_km=590),
            lambda d: d['collections'][query.ROUTES][0].update(annual_length_range_km=[590, 630]),
            lambda d: d['collections'][query.ROUTES][0].update(sample_date='1987-03-22'),
            lambda d: d['collections'][query.ROUTES][0].update(rank_eligible=0),
            lambda d: d['collections'][query.POINTS][-1].update(is_strict_eicc_path_reference=True),
            lambda d: d['collections'][query.POINTS][0].update(current_thickness_m=63),
            lambda d: d['collections'][query.SCALES][0].update(paired_current_width_km=23),
            lambda d: d['collections'][query.SCALES][0].update(uncertainty_km=25),
            lambda d: d['owner_map_features'][0].update(observation_date='1987-03-22'),
        ]
        for mutate in mutations:
            changed = copy.deepcopy(self.contract); mutate(changed)
            self.refused(self.base(), changed)

    def test_source_alias_or_id_conflict_requires_reconciliation(self):
        data = self.base()
        data['sources'].append({'id': 'source:another-durand', 'doi': 'https://doi.org/10.1029/2008JC004807/'})
        self.refused(data)
        data = self.base()
        data['sources'].append({'id': query.GANG, 'label': 'Different source record'})
        self.refused(data)

    def test_bad_prior_references_counts_and_missing_identity_refused(self):
        for mutate in [lambda d: d['objects'][0].update(linked_source_count=True),
                       lambda d: d['objects'][0].update(route_ids=[]),
                       lambda d: d['route_decisions'][0].update(candidate_count=0),
                       lambda d: d['route_decisions'][0].update(rank_eligible=True),
                       lambda d: d['route_decisions'][0]['source_decision'].update(candidate_ids=[]),
                       lambda d: d['entities'].clear(),
                       lambda d: d[query.ROUTES][0].update(source_ids=[{'invalid': True}])]:
            data = self.base(); mutate(data); self.refused(data)

    def test_source_pointers_and_queries_are_explicit(self):
        rows = [r for name in query.OWNER_FIELDS for r in self.contract['collections'][name]]
        self.assertEqual(len(rows), 15)
        for row in rows:
            self.assertTrue(row['source_pointer'].startswith('/'))
            self.assertTrue(row['source_query_url'].startswith('query.html?source-q='))
            self.assertEqual(row['diagnostic_page'], query.PAGE)
            self.assertIn(row['source_id'], row['source_ids'])
            self.assertIn(query.METHOD, row['source_ids'])

    def test_evidence_page_has_all_records_and_own_reviewed_figures(self):
        html = page(self.contract).decode()
        parser = HTMLParser(); parser.feed(html); parser.close()
        self.assertEqual(html.count('class="panel point"'), 7)
        self.assertEqual(html.count('data-label="Reported scale"'), 6)
        self.assertEqual(html.count('class="number"'), 2)
        self.assertIn('About 590 km', html); self.assertIn('About 630 km', html)
        self.assertIn('not strictly on the EICC path', html)
        self.assertIn('not current depth or thickness', html)
        self.assertNotIn('<script', html)
        self.assertIn(query.FIGURE, html); self.assertIn(query.SUPPORT_FIGURE, html)

    def test_each_reference_link_selects_its_exact_record_and_existing_map_anchor(self):
        for row in self.contract['collections'][query.ROUTES]:
            url = urlsplit(query.route_record_query_url(row['id']))
            params = parse_qs(url.query)
            self.assertEqual(params['inspect'], [row['id']])
            self.assertEqual(json.loads(params['q'][0]), {'collection': query.ROUTES,
                'filters': [{'field': 'id', 'op': 'eq', 'value': row['id']}], 'limit': 1})
            self.assertEqual(url.fragment, 'query-map-section')


if __name__ == '__main__':
    unittest.main()
