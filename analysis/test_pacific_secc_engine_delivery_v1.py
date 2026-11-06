"""Small metadata-only checks for engine custody and complete map-card projection."""
import copy
import json
import unittest
from urllib.parse import parse_qs, urlsplit
from html.parser import HTMLParser

import pacific_secc_engine_delivery_v1 as engine
import pacific_secc_reference_delivery_v2 as presentation
import pacific_secc_runtime_scope_v3 as scope_source
import pacific_secc_publication_admission_v1 as admission
from test_pacific_secc_publication_admission_v1 import applied_fixture
from query_packet import PART_LIMIT


class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.urls = []
    def handle_starttag(self, tag, attrs):
        self.urls.extend(value for key, value in attrs if key == 'href')


class PacificEngineDelivery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scope = scope_source.build()
        cls.parent = json.loads((admission.ROOT / 'research/eacc-connection-presentation-saved-engine-manifest-v4.json').read_bytes())
        cls.original = json.loads((admission.ROOT / 'research/south-java-compiled-catalog-build-inputs-v1.json').read_bytes())
        cls.bindings = json.loads((admission.ROOT / 'research/eacc-connection-presentation-parent-source-bindings-v3.json').read_bytes())['bindings']

    def inventory(self):
        return engine.compile_inventory(self.original, self.parent, self.scope, 'c' * 64, 'b' * 64)

    def packet(self):
        length = 190500000
        parts = []
        for i, offset in enumerate(range(0, length, PART_LIMIT)):
            sha = admission.runtime.sha(('synthetic descriptor ' + str(i)).encode())
            parts.append({'index': i, 'path': f'query-parts/{i:06d}-{sha}.bin',
                          'byte_length': min(PART_LIMIT, length - offset), 'sha256': sha})
        return {'schema': 'osw.query-packet.v1', 'logical_schema': 'osw.query-bundle.v1',
                'hash_algorithm': 'sha256', 'part_byte_limit': PART_LIMIT, 'parts': parts,
                'logical_sha256': 'b' * 64, 'logical_byte_length': length}

    def overlay_args(self):
        inventory = self.inventory()
        sources = {p: row['candidate_sha256'] for p, row in self.scope['runtime_source_changes'].items()}
        sources.update(self.scope['added_runtime_source'])
        sources.update(self.scope['compiled_source_contract_sha256'])
        packet = self.packet()
        parts = {'almanac/' + p['path']: p['sha256'] for p in packet['parts']}
        paths = engine.GENERATED | engine.delivery.DOCUMENTS | set(sources) | set(parts)
        replacements = {p: 'd' * 64 for p in paths}
        replacements.update(parts); replacements.update(sources)
        replacements[engine.delivery.CATALOG] = 'c' * 64
        actual = sorted(set(inventory['rust_source_sha256']) | set(inventory['compile_time_data_sha256']))
        proof = {'production_dependencies': actual, 'production_dependency_count': len(actual),
                 'test_only_fixtures_compiled': 0, 'compiled_catalog_dependency_verified': True}
        return inventory, packet, sources, replacements, proof

    def overlay(self, inventory, packet, sources, replacements, proof):
        return engine.engine_manifest(self.parent, inventory, self.scope, packet, replacements, sources, proof,
            wasm_sha='e' * 64, compiler='rustc 1.95.0 (test fixture)',
            parent_manifest_sha=engine.PARENT_MANIFEST_SHA, source_commit='a' * 40)

    def test_compiler_inventory_preserves_every_inherited_data_path_except_catalog(self):
        inventory = self.inventory()
        self.assertEqual(len(inventory['rust_source_sha256']), 99)
        self.assertEqual(len(inventory['compile_time_data_sha256']), 146)
        self.assertEqual(len(inventory['excluded_test_only_data_references']), 8)
        for path, references in self.original['excluded_test_only_data_references'].items():
            self.assertEqual(inventory['excluded_test_only_data_references'][path], references)
        for path in self.original['compile_time_data_sha256']:
            if path != engine.delivery.CATALOG:
                self.assertEqual(inventory['compile_time_data_sha256'][path], self.parent['sha256'][path])
        bad = copy.deepcopy(self.scope)
        next(iter(bad['runtime_source_changes'].values()))['parent_sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            engine.compile_inventory(self.original, self.parent, bad, 'c' * 64, 'b' * 64)

    def test_overlay_preserves_all_parent_namespaces_and_complete_eacc_metadata(self):
        args = self.overlay_args()
        inventory, packet, sources, replacements, proof = args
        result = self.overlay(*args)
        self.assertEqual(result[engine.PRESENTATION], self.parent[engine.PRESENTATION])
        for key in set(self.parent) - {'sha256', 'rustc'}:
            self.assertEqual(result[key], self.parent[key])
        allowed = engine.GENERATED | set(self.scope['runtime_source_changes']) | {engine.WASM}
        for path, sha in self.parent['sha256'].items():
            if path not in allowed:
                self.assertEqual(result['sha256'][path], sha)
        self.assertEqual(result[engine.KEY]['logical_sha256'], packet['logical_sha256'])

    def test_overlay_refuses_missing_compiler_dependency_or_unrelated_pin_change(self):
        inventory, packet, sources, replacements, proof = self.overlay_args()
        proof['production_dependencies'].remove(admission.FILE)
        proof['production_dependency_count'] -= 1
        with self.assertRaises(ValueError):
            self.overlay(inventory, packet, sources, replacements, proof)
        inventory, packet, sources, replacements, proof = self.overlay_args()
        unrelated = 'rust/osw-query/src/asca_calendar.rs'
        sources[unrelated] = replacements[unrelated] = '0' * 64
        with self.assertRaises(ValueError):
            self.overlay(inventory, packet, sources, replacements, proof)

    def test_parent_custody_requires_both_historical_and_current_byte_versions(self):
        metadata = {p: (sha, 1) for p, sha in self.parent['sha256'].items()}
        for path, row in self.scope['runtime_source_changes'].items():
            metadata[path] = (row['candidate_sha256'], row['candidate_bytes'])
            metadata[row['archive_path']] = (row['parent_sha256'], row['parent_bytes'])
        for row in self.bindings:
            metadata[row['manifest_path']] = (row['installed_path_sha256'], row['installed_path_bytes'])
            metadata[row['archive_path']] = (row['historical_sha256'], row['historical_bytes'])
        result = engine.verify_parent(self.parent, metadata.__getitem__, self.bindings, self.scope)
        self.assertEqual(result['manifest_paths_verified'], len(self.parent['sha256']))
        self.assertEqual(len(result['scoped_runtime_paths']), 6)
        archive = next(iter(self.scope['runtime_source_changes'].values()))['archive_path']
        metadata[archive] = ('0' * 64, 1)
        with self.assertRaises(ValueError):
            engine.verify_parent(self.parent, metadata.__getitem__, self.bindings, self.scope)

    def test_complete_atlas_card_has_existing_renderer_figure_alias_and_correct_reach_role(self):
        supplement = admission.build_contract()
        data = applied_fixture(supplement)
        source = supplement['audited_prior_decision']['source_decision']
        catalog = {'candidates': [], 'remaining_current_decisions': [copy.deepcopy(source)],
                   'counts': {'route_candidates': 80, 'currents_with_route_candidates': 73,
                              'currents_without_route_candidates': 22, 'currents_without_any_reference_card': 22},
                   'planning_taxonomy': {'strategies': [{'id': source['route_strategy_id'], 'unbuilt_count': 9}]}}
        result = presentation.catalog_projection(catalog, data['collections'])
        entry = result['candidates'][0]
        self.assertTrue((admission.ROOT / entry['figure']).is_file())
        self.assertEqual(entry['figure'], entry['figure_file'])
        self.assertEqual(entry['report_inline']['rendering_role'], presentation.RENDERING_ROLE)
        self.assertEqual(entry['comparison_group'], 'osw_studied_reach_routes')

    def test_candidate_support_page_has_exact_current_route_links_and_no_pending_installation_text(self):
        raw = presentation.support_page()
        text = raw.decode()
        self.assertNotIn('awaiting native/WASM', text)
        links = Links(); links.feed(text)
        atlas = next(url for url in links.urls if 'atlas-route=' in url)
        self.assertEqual(parse_qs(urlsplit(atlas).query)['atlas-route'], [admission.query.ROUTE])
        self.assertTrue(any('inspect=' in url for url in links.urls))
        self.assertIn('Whole-current length and seasonal dimensions remain unresolved', text)


if __name__ == '__main__':
    unittest.main()
