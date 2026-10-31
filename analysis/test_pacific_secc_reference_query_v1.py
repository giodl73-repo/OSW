"""Admission integrity and scientific scope; synthetic collections only."""
import copy
from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest

import pacific_secc_reference_query_v1 as query


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        self.urls.extend(v for k, v in attrs if k in ('href', 'src'))


class PacificReference(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = query.build_contract()

    def base(self):
        return {
            'objects': [{'id': query.TARGET, 'type': 'named_current',
                'source_ids': ['source:existing-paper'], 'linked_source_count': 1,
                'route_ids': [], 'route_decision_ids': ['decision:pacific'],
                'capabilities': {'reference_route': 0, 'geometry': 1, 'scoped_width': 1},
                'map_features': [{'role': 'editorial_locator', 'geometry': {'type': 'Point', 'coordinates': [165, -9]}}],
                'evidence_links': [], 'section_fingerprints': {'width': 'preserve'},
                'published_length_km': None, 'state_codes': ['EXISTING'], 'width_ids': ['old-width'],
                'latest_observation_date': None}, {'id': 'current:other', 'preserve': True}],
            'entities': [{'id': query.TARGET, 'type': 'named_current'}],
            'sources': [{'id': 'source:existing-paper', 'url': query.URL + '#page=2',
                         'kind': 'external', 'rights': 'preserve exact record'}],
            'reference_routes': [{'id': 'other-route', 'current_id': 'other'}],
            'route_decisions': [{'id': 'decision:pacific', 'entity_id': query.TARGET,
                'route_ids': [], 'candidate_count': 0, 'rank_eligible': False,
                'strategy_id': 'reference-after-source-review',
                'construction_status': 'pending', 'scope_review': 'preserve',
                'source_decision': {'candidate_ids': [], 'next_action': 'pending', 'identity': 'preserve'}},
                {'id': 'decision:other', 'entity_id': 'current:other'}],
            'widths': [{'id': 'old-width', 'width_km': 300}],
            'width_samples': [], 'geometries': [{'id': 'old-geometry'}],
            'state_links': [{'id': 'old-link'}], 'length_assessments': [{'id': 'old-length'}]}

    def refused(self, data, contract=None):
        before = query.encoded(data)
        with self.assertRaises(ValueError):
            query.append(data, self.contract if contract is None else contract)
        self.assertEqual(query.encoded(data), before)

    def test_patch_reuses_publication_and_preserves_scientific_data(self):
        data = self.base()
        before = copy.deepcopy(data)
        receipt = query.append(data, self.contract)
        self.assertTrue(receipt['publication_record_reused'])
        self.assertEqual(data['sources'][0], before['sources'][0])
        self.assertEqual(len(data['sources']), 2)  # Only the method is new.
        for name in set(before) - {'objects', 'sources', 'reference_routes', 'route_decisions'}:
            self.assertEqual(data[name], before[name])
        self.assertEqual(data['objects'][1], before['objects'][1])
        self.assertEqual(data['reference_routes'][:-1], before['reference_routes'])
        self.assertEqual(data['route_decisions'][1], before['route_decisions'][1])
        owner = data['objects'][0]
        for key in ['published_length_km', 'state_codes', 'width_ids', 'latest_observation_date']:
            self.assertEqual(owner[key], before['objects'][0][key])
        self.assertEqual(owner['capabilities']['geometry'], 1)
        self.assertEqual(owner['route_ids'], [query.ROUTE])
        self.assertEqual(owner['linked_source_count'], 2)
        self.assertEqual(owner['map_features'][:-1], before['objects'][0]['map_features'])
        self.assertEqual(data['route_decisions'][0]['prior_route_decision'], before['route_decisions'][0])

    def test_published_length_seasons_and_display_context_remain_distinct(self):
        row = self.contract['route']
        self.assertEqual(row['approximate_reference_path_km'], 1800)
        self.assertEqual(row['public_editorial_probe_span_km'], [1700, 1800])
        self.assertEqual(row['scenario_count'], 27)
        self.assertEqual(row['coordinates_lon_lat'][-1], [180, -9.5])
        self.assertEqual(row['display_context']['state_codes'], ['AUSE'])
        self.assertEqual(row['display_context']['recommended_nasa_tile_id'], 'level2_G_4')
        for key in ['whole_current_length_km', 'annual_length_range_km', 'annual_width_range_km',
                    'physical_width_km', 'current_thickness_m', 'uncertainty_km', 'sample_date',
                    'nominal_atlas_state_crossings', 'recommended_nasa_tile_id']:
            self.assertIsNone(row[key])
        for key in ['rank_eligible', 'physical_current_axis_admitted', 'physical_current_edges_admitted',
                    'physical_state_join_eligible', 'seasonal_playback_eligible', 'nasa_identity_verified']:
            self.assertIs(row[key], False)

    def test_doi_alias_is_reused_and_ambiguous_registry_refused(self):
        data = self.base()
        data['sources'][0]['url'] = 'https://doi.org/' + query.DOI
        query.append(data, self.contract)
        data = self.base()
        data['sources'].append({'id': 'source:duplicate', 'doi': query.DOI})
        self.refused(data)

    def test_missing_or_conflicting_publication_refused(self):
        data = self.base()
        data['sources'][0]['url'] = 'https://example.org/unrelated'
        self.refused(data)
        data = self.base()
        data['sources'][0]['doi'] = '10.1029/wrong'
        self.refused(data)

    def test_bad_provenance_and_planning_fail_atomically(self):
        for mutate in [
            lambda d: d['objects'][0].update(linked_source_count=3),
            lambda d: d['objects'][0].update(source_ids=['missing']),
            lambda d: d['route_decisions'][0].update(candidate_count=1),
            lambda d: d['objects'][0].update(route_ids=['missing']),
            lambda d: d['sources'].append({'id': query.METHOD, 'title': 'wrong method'}),
            lambda d: d['reference_routes'].append({'id': 'unexpected', 'current_id': query.CURRENT}),
        ]:
            with self.subTest(mutate=mutate):
                data = self.base()
                mutate(data)
                self.refused(data)

    def test_reapplication_and_promoted_contract_fail_atomically(self):
        data = self.base()
        query.append(data, self.contract)
        self.refused(data)
        changed = copy.deepcopy(self.contract)
        changed['route']['annual_length_range_km'] = [1700, 1800]
        self.refused(self.base(), changed)

    def test_changed_reviewed_evidence_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for path in query.PINS:
                destination = root / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((query.ROOT / path).read_bytes())
            (root / query.CANDIDATE).write_bytes(b'{}')
            with self.assertRaisesRegex(ValueError, 'Changed reviewed'):
                query.build_contract(root)

    def test_support_page_local_links_and_pending_installation(self):
        rendered = query.page(self.contract).decode()
        parser = Links()
        parser.feed(rendered)
        for url in parser.urls:
            if '://' not in url and not url.startswith('#'):
                self.assertTrue((query.ROOT / 'almanac' / url).resolve().is_file(), url)
        self.assertIn('awaiting native/WASM and atlas installation', rendered)
        self.assertNotIn(self.contract['query_url_after_installation'], rendered)

    def test_atlas_projection_preserves_prior_routes_and_separates_state_context(self):
        data = self.base()
        query.append(data, self.contract)
        catalog = {'candidates': [{'id': 'old-card', 'current_id': 'other'}],
                   'remaining_current_decisions': [{'current_id': query.CURRENT, 'candidate_ids': []}],
                   'counts': {'route_candidates': 80, 'currents_with_route_candidates': 73,
                              'currents_without_route_candidates': 22, 'currents_without_any_reference_card': 22},
                   'planning_taxonomy': {'strategies': [{'id': 'reference-after-source-review', 'unbuilt_count': 9}]}}
        before = copy.deepcopy(catalog)
        result = query.catalog_projection(catalog, data, self.contract)
        self.assertEqual(catalog, before)
        self.assertEqual(result['candidates'][0], before['candidates'][0])
        self.assertEqual(result['counts']['route_candidates'], 81)
        self.assertEqual(result['counts']['currents_with_route_candidates'], 74)
        entry = result['candidates'][-1]
        self.assertEqual(entry['nominal_atlas_state_crossings'], [])
        self.assertFalse(entry['physical_state_join_eligible'])
        report = entry['report_inline']
        self.assertEqual(report['nominal_atlas_state_crossings'], ['AUSE'])
        self.assertEqual(report['recommended_nasa_tile_id'], 'level2_G_4')
        self.assertIsNone(report['annual_length_range_km'])
        self.assertEqual(report['reported_approximate_reference_path_km'], 1800)
        self.assertEqual(result['planning_taxonomy']['strategies'][0]['unbuilt_count'], 8)
        catalog['counts']['currents_without_any_reference_card'] = 0
        before = copy.deepcopy(catalog)
        with self.assertRaises(ValueError):
            query.catalog_projection(catalog, data, self.contract)
        self.assertEqual(catalog, before)


if __name__ == '__main__':
    unittest.main()
