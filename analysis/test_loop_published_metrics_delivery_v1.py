"""Tiny preservation, source-index and compiled-overlay fixtures; no live data."""
import copy
import gzip
import json
import unittest

import loop_published_metrics_delivery_v1 as delivery
import loop_published_metrics_query_v1 as query
from query_packet import PART_LIMIT
import test_loop_published_metrics_query_v1 as fixtures


class Delivery(unittest.TestCase):
    def setUp(self): self.contract = query.build_contract()

    def bundle(self):
        collections = fixtures.PublishedContourEvents().base()
        dashboard = {'schema': 'osw.motion-dashboard.v1', 'fingerprint_version': 2,
                     'entries': copy.deepcopy(collections['objects']), 'counts': {'named_current': 2},
                     'model_context_projection': {'keep_prior_proof': True}}
        body = json.dumps(dashboard, ensure_ascii=False, indent=2) + '\n'
        manifest = {'input_sha256': {delivery.DASHBOARD: delivery.sha(body.encode()), 'old-science': 'a' * 64},
                    'dashboard_receipt': {'source_file': delivery.DASHBOARD, 'source_json': body,
                                          'source_sha256': delivery.sha(body.encode())},
                    'south_java_model_context_version': 'keep'}
        return {'schema': 'osw.query-bundle.v1', 'collections': collections, 'manifest': manifest}

    def test_parent_not_mutated_and_every_prior_scientific_row_preserved(self):
        original = self.bundle(); before = copy.deepcopy(original)
        result, dashboard, audit = delivery.candidate(original, self.contract)
        self.assertEqual(delivery.encoded(original), delivery.encoded(before))
        self.assertEqual(audit['new_evidence_records'], 14)
        self.assertEqual(audit['new_source_records'], 2)
        self.assertEqual(result['manifest']['input_sha256']['old-science'], 'a' * 64)
        self.assertEqual(result['collections']['measurements'], original['collections']['measurements'])
        self.assertEqual(result['collections']['geometries'], original['collections']['geometries'])
        self.assertEqual(json.loads(dashboard)['model_context_projection'], {'keep_prior_proof': True})
        self.assertEqual(json.loads(dashboard)['entries'][1], before['collections']['objects'][1])
        self.assertEqual(result['collections']['objects'][0]['latest_observation_date'], '2026-09-25')

    def test_dashboard_or_append_failure_cannot_mutate_parent(self):
        for mode in ['bad-receipt', 'bad-entries', 'already-applied']:
            parent = self.bundle()
            if mode == 'bad-receipt': parent['manifest']['dashboard_receipt']['source_sha256'] = '0' * 64
            elif mode == 'bad-entries':
                doc = json.loads(parent['manifest']['dashboard_receipt']['source_json']); doc['counts'] = {}
                body = json.dumps(doc); pin = delivery.sha(body.encode())
                parent['manifest']['dashboard_receipt'].update(source_json=body, source_sha256=pin)
                parent['manifest']['input_sha256'][delivery.DASHBOARD] = pin
            else: parent['manifest'][delivery.RECEIPT] = {}
            before = delivery.encoded(parent)
            with self.assertRaises(ValueError): delivery.candidate(parent, self.contract)
            self.assertEqual(delivery.encoded(parent), before)

    def test_physical_owner_changes_cannot_be_projected(self):
        before = self.bundle()['collections']['objects'][0]
        for mode in ['latest_observation_date', 'published_length_km', 'prior-capability', 'erase-source']:
            after = copy.deepcopy(before)
            if mode == 'prior-capability': after['capabilities']['scoped_width'] = 99
            elif mode == 'erase-source': after['source_ids'] = []
            else: after[mode] = 999
            with self.subTest(mode=mode):
                with self.assertRaises(ValueError): delivery.verify_owner(before, after)

    def index_fixture(self):
        documents = {'research/prior-science.json': '{"preserve":"original whitespace"}\n',
                     delivery.DASHBOARD: '{"schema":"osw.motion-dashboard.v1","entries":[]}'}
        corpus = {'schema': 'osw.almanac-index-bundle.v1', 'documents': documents}
        raw = delivery.encoded(corpus); packed = gzip.compress(raw, mtime=0)
        catalog = {'schema': 'osw.almanac-index-catalog.v1', 'source_count': len(documents),
                   'bundle_bytes': len(raw), 'bundle_sha256': delivery.sha(raw),
                   'compressed_sha256': delivery.sha(packed), 'input_sha256': {'old-source': 'a' * 64},
                   'documents': [{'path': p, 'source_bytes': len(b.encode()), 'source_sha256': delivery.sha(b.encode())}
                                 for p, b in documents.items()]}
        registry = {'schema': 'osw.almanac-index-sources.v1', 'documents': sorted(documents)}
        additions = {p: b'{"new":"source"}\n' for p in delivery.DOCUMENTS}
        return catalog, packed, registry, additions

    def test_lossless_index_preserves_old_strings_and_adds_exact_four_sources(self):
        catalog, packed, registry, additions = self.index_fixture()
        generated, audit = delivery.source_index(catalog, packed, registry, additions, b'{"new":"dashboard"}')
        corpus = json.loads(gzip.decompress(generated['almanac/index-data.json.gz']))
        self.assertEqual(corpus['documents']['research/prior-science.json'], '{"preserve":"original whitespace"}\n')
        self.assertEqual(set(audit['added_source_paths']), delivery.DOCUMENTS)
        self.assertEqual(audit['replaced_source_paths'], [delivery.DASHBOARD])
        self.assertEqual(audit['scientific_source_documents_replaced'], 0)
        self.assertEqual(json.loads(generated[delivery.CATALOG])['source_count'], 6)

    def test_corrupt_index_or_undeclared_source_inventory_refused(self):
        catalog, packed, registry, additions = self.index_fixture()
        with self.assertRaises(ValueError): delivery.source_index(catalog, packed + b'x', registry, additions, b'{}')
        additions['research/unreviewed.json'] = b'{}'
        with self.assertRaises(ValueError): delivery.source_index(catalog, packed, registry, additions, b'{}')

    def engine_fixture(self):
        original = {'rust_source_sha256': {'rust/osw-query/src/index_store.rs': 'a' * 64},
                    'compile_time_data_sha256': {delivery.CATALOG: 'b' * 64, 'old-science': 'c' * 64},
                    'saved_candidate_catalog_sha256': 'b' * 64,
                    'saved_candidate_logical_sha256': 'd' * 64}
        packet = {'schema': 'osw.query-packet.v1', 'logical_schema': 'osw.query-bundle.v1',
                  'hash_algorithm': 'sha256', 'part_byte_limit': PART_LIMIT,
                  'logical_sha256': 'e' * 64, 'logical_byte_length': 1,
                  'parts': [{'index': 0, 'path': 'query-parts/000000-' + 'f' * 64 + '.bin',
                             'byte_length': 1, 'sha256': 'f' * 64}]}
        inventory = delivery.compile_inventory(original, '1' * 64, 'e' * 64)
        parent = {'schema': 'osw.query-engine-manifest.v1', 'abi_version': 1,
                  'sha256': {**original['rust_source_sha256'], **original['compile_time_data_sha256'], delivery.WASM: '2' * 64},
                  'south_java_compiled_catalog_engine_v1': {'preserve': 'earlier receipt'}}
        required = delivery.GENERATED | delivery.DOCUMENTS | set(self.contract['input_sha256'])
        replacements = {p: '3' * 64 for p in required}
        replacements.update(self.contract['input_sha256'])
        replacements[query.FILE] = delivery.sha(query.encoded(self.contract))
        replacements[delivery.CATALOG] = '1' * 64
        replacements['almanac/' + packet['parts'][0]['path']] = 'f' * 64
        deps = {'production_dependencies': [delivery.CATALOG, 'rust/osw-query/src/index_store.rs'],
                'production_dependency_count': 2, 'compiled_catalog_dependency_verified': True, 'test_only_fixtures_compiled': 0}
        kwargs = {'wasm_sha': '4' * 64, 'compiler': 'rustc 1.95.0 (verified)',
                  'parent_manifest_sha': '5' * 64, 'source_commit': '6' * 40, 'dependency_proof': deps}
        return parent, original, inventory, replacements, packet, kwargs

    def test_matching_overlay_keeps_history_and_changes_only_declared_compile_data(self):
        args = self.engine_fixture(); parent, original, inventory, replacements, packet, kwargs = args
        before = copy.deepcopy(parent)
        result = delivery.engine_manifest(parent, original, inventory, replacements, packet, **kwargs)
        self.assertEqual(parent, before)
        self.assertEqual(result['south_java_compiled_catalog_engine_v1'], before['south_java_compiled_catalog_engine_v1'])
        self.assertEqual(result['sha256']['old-science'], 'c' * 64)
        self.assertEqual(result[delivery.RECEIPT]['changed_compile_time_data_paths'], [delivery.CATALOG])
        self.assertEqual(result[delivery.RECEIPT]['runtime_sources_changed'], [])

    def test_unreviewed_compile_source_catalog_dependency_or_overlay_refused(self):
        for mode in ['runtime', 'data', 'dependency', 'source-hash', 'extra-overlay', 'contract-hash']:
            parent, original, inventory, replacements, packet, kwargs = self.engine_fixture()
            if mode == 'runtime': parent['sha256']['rust/osw-query/src/index_store.rs'] = '0' * 64
            elif mode == 'data': inventory['compile_time_data_sha256']['old-science'] = '0' * 64
            elif mode == 'dependency': kwargs['dependency_proof']['production_dependencies'].append('/outside')
            elif mode == 'source-hash': replacements[query.FACTS] = '0' * 64
            elif mode == 'extra-overlay': replacements['undeclared-path'] = '0' * 64
            else: replacements[query.FILE] = '0' * 64
            with self.subTest(mode=mode):
                with self.assertRaises(ValueError): delivery.engine_manifest(parent, original, inventory, replacements, packet, **kwargs)


if __name__ == '__main__': unittest.main()
