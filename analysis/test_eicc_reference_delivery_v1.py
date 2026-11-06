"""Small delivery-boundary fixtures; never load installed packet/index or compile."""
import copy
import gzip
import json
import unittest
from collections import Counter

import eicc_reference_delivery_v1 as delivery
import eicc_reference_query_v1 as context
import test_eicc_reference_query_v1 as fixtures
from query_packet import PART_LIMIT


class EiccDelivery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = context.build_contract()

    def bundle(self):
        rows = fixtures.EiccReferenceContract().base()
        dashboard = {'schema': 'osw.motion-dashboard.v1', 'fingerprint_version': 2,
                     'entries': copy.deepcopy(rows['objects']),
                     'counts': dict(Counter(r['type'] for r in rows['objects'])),
                     'historical_namespace': {'keep': True}}
        raw = delivery.encoded(dashboard).decode()
        return {'schema': 'osw.query-bundle.v1', 'collections': rows, 'manifest': {
            'input_sha256': {delivery.DASHBOARD: delivery.sha(raw.encode())},
            'dashboard_receipt': {'source_file': delivery.DASHBOARD,
                                  'source_sha256': delivery.sha(raw.encode()), 'source_json': raw},
            'historical_namespace': {'keep': True}}}

    def test_projection_preserves_parent_and_physical_science(self):
        parent = self.bundle()
        original = delivery.encoded(parent)
        child, dashboard, audit = delivery.candidate(parent, self.contract)
        self.assertEqual(delivery.encoded(parent), original)
        self.assertEqual(audit['new_evidence_records'], 15)
        self.assertEqual(audit['new_source_records'], 3)
        self.assertEqual(audit['other_objects_preserved'], 1)
        for name in ['widths', 'width_samples', 'length_assessments', 'geometries', 'state_links']:
            self.assertEqual(child['collections'][name], parent['collections'][name])
        old = parent['collections']['route_decisions'][0]
        self.assertEqual(child['collections']['route_decisions'][0]['prior_route_decision'], old)
        doc = json.loads(dashboard)
        self.assertEqual(doc['historical_namespace'], {'keep': True})
        self.assertEqual(doc['entries'][1], parent['collections']['objects'][1])
        self.assertEqual(doc['entries'][0]['capabilities']['scoped_width'], 1)
        self.assertIsNone(doc['entries'][0]['published_length_km'])
        self.assertEqual(child['manifest']['historical_namespace'], {'keep': True})
        self.assertEqual(child['manifest']['input_sha256'][delivery.DASHBOARD], delivery.sha(dashboard))
        with self.assertRaises(ValueError):
            delivery.candidate(child, self.contract)

    def test_owner_refuses_deleted_null_and_changed_physical_metadata(self):
        parent = self.bundle()
        child, _, _ = delivery.candidate(parent, self.contract)
        before = parent['collections']['objects'][0]
        good = child['collections']['objects'][0]
        for mutation in ['delete_null', 'width_capability', 'prior_feature', 'prior_link', 'prior_source']:
            with self.subTest(mutation=mutation):
                after = copy.deepcopy(good)
                if mutation == 'delete_null': del after['published_length_km']
                elif mutation == 'width_capability': after['capabilities']['scoped_width'] = 2
                elif mutation == 'prior_feature': after['map_features'][0]['role'] = 'physical_axis'
                elif mutation == 'prior_link': after['evidence_links'][0]['url'] = 'different.html'
                else: after['source_ids'].remove('source:prior')
                with self.assertRaises(ValueError):
                    delivery.verify_owner(before, after)

    def test_dashboard_custody_and_other_owner_rejected(self):
        parent = self.bundle()
        child, _, _ = delivery.candidate(parent, self.contract)
        for mutation in ['source_hash', 'other_owner', 'entry_duplicate', 'count']:
            with self.subTest(mutation=mutation):
                manifest = copy.deepcopy(parent['manifest'])
                after = copy.deepcopy(child['collections']['objects'])
                if mutation == 'source_hash': manifest['dashboard_receipt']['source_sha256'] = '0' * 64
                elif mutation == 'other_owner': after[1]['fingerprint'] = 'changed'
                else:
                    doc = json.loads(manifest['dashboard_receipt']['source_json'])
                    if mutation == 'entry_duplicate': doc['entries'].append(doc['entries'][0])
                    else: doc['counts']['named_current'] = 3
                    raw = delivery.encoded(doc)
                    manifest['dashboard_receipt'].update(source_json=raw.decode(), source_sha256=delivery.sha(raw))
                    manifest['input_sha256'][delivery.DASHBOARD] = delivery.sha(raw)
                with self.assertRaises(ValueError):
                    delivery.dashboard_projection(manifest, parent['collections']['objects'], after)

    def test_duplicate_prior_route_decision_is_rejected_without_mutation(self):
        parent = self.bundle()
        parent['collections']['route_decisions'].append(copy.deepcopy(parent['collections']['route_decisions'][1]))
        original = delivery.encoded(parent)
        with self.assertRaises(ValueError): delivery.candidate(parent, self.contract)
        self.assertEqual(delivery.encoded(parent), original)

    def index(self):
        docs = {'research/prior-science.json': '{ "historical": true }\n',
                delivery.DASHBOARD: '{"entries":[]}\n'}
        corpus = {'schema': 'osw.almanac-index-bundle.v1', 'documents': docs}
        raw = delivery.encoded(corpus)
        compressed = gzip.compress(raw, mtime=0)
        catalog = {'schema': 'osw.almanac-index-catalog.v1', 'source_count': 2,
                   'bundle_bytes': len(raw), 'bundle_sha256': delivery.sha(raw),
                   'compressed_bytes': len(compressed), 'compressed_sha256': delivery.sha(compressed),
                   'documents': [{'path': p, 'source_bytes': len(s.encode()),
                                  'source_sha256': delivery.sha(s.encode())} for p, s in docs.items()]}
        registry = {'schema': 'osw.almanac-index-sources.v1', 'documents': sorted(docs)}
        return catalog, compressed, registry

    def test_index_preserves_exact_source_strings_and_extends_eight(self):
        parent = self.index()
        original = copy.deepcopy(parent)
        docs = {p: delivery.encoded({'source': p}) for p in delivery.DOCUMENTS}
        result, audit = delivery.source_index(*parent, docs, b'{"entries":[],"updated":true}\n')
        self.assertEqual(parent, original)
        self.assertEqual(audit['original_source_strings_preserved'], 1)
        self.assertEqual(audit['replaced_source_paths'], [delivery.DASHBOARD])
        self.assertEqual(set(audit['added_source_paths']), delivery.DOCUMENTS)
        corpus = json.loads(gzip.decompress(result['almanac/index-data.json.gz']))
        self.assertEqual(corpus['documents']['research/prior-science.json'], '{ "historical": true }\n')
        for p, raw in docs.items(): self.assertEqual(corpus['documents'][p], raw.decode())
        self.assertEqual(json.loads(result[delivery.CATALOG])['source_count'], 10)
        bad = copy.deepcopy(parent[0]); bad['compressed_bytes'] += 1
        with self.assertRaises(ValueError): delivery.source_index(bad, *parent[1:], docs, b'{}')
        bad = dict(docs); bad.pop(next(iter(bad)))
        with self.assertRaises(ValueError): delivery.source_index(*parent, bad, b'{}')

    def test_index_rejects_collision_with_historical_delivery_document(self):
        catalog, packed, registry = self.index()
        corpus = json.loads(gzip.decompress(packed))
        path = sorted(delivery.DOCUMENTS)[0]
        raw = b'{"already_indexed":true}\n'
        corpus['documents'][path] = raw.decode()
        catalog['documents'].append({'path': path, 'source_bytes': len(raw), 'source_sha256': delivery.sha(raw)})
        catalog['source_count'] += 1
        registry['documents'].append(path)
        body = delivery.encoded(corpus); packed = gzip.compress(body, mtime=0)
        catalog.update(bundle_bytes=len(body), bundle_sha256=delivery.sha(body),
                       compressed_bytes=len(packed), compressed_sha256=delivery.sha(packed))
        docs = {p: delivery.encoded({'new': p}) for p in delivery.DOCUMENTS}
        original = copy.deepcopy((catalog, registry))
        with self.assertRaises(ValueError): delivery.source_index(catalog, packed, registry, docs, b'{}')
        self.assertEqual((catalog, registry), original)

    def compiler(self):
        original = {'rust_source_sha256': {'rust/osw-query/src/index_store.rs': '1' * 64},
                    'compile_time_data_sha256': {delivery.CATALOG: '2' * 64, 'research/prior.json': '3' * 64},
                    'excluded_test_only_data_references': ['test-only.json']}
        parent = {'schema': 'osw.query-engine-manifest.v1', 'abi_version': 1,
                  'sha256': {**original['rust_source_sha256'], **original['compile_time_data_sha256'],
                             delivery.CATALOG: '4' * 64, delivery.WASM: delivery.PARENT_WASM_SHA},
                  'loop_published_metrics_presentation_revision_v1': {'archive_sha256': '5' * 64}}
        return original, parent

    def test_compile_inventory_rebases_only_catalog_and_keeps_history(self):
        original, parent = self.compiler()
        before = copy.deepcopy((original, parent))
        inventory = delivery.compile_inventory(original, parent, '6' * 64, '7' * 64)
        self.assertEqual((original, parent), before)
        self.assertEqual(inventory['parent_catalog_sha256'], '4' * 64)
        self.assertEqual(inventory['compile_time_data_sha256'][delivery.CATALOG], '6' * 64)
        self.assertEqual(inventory['compile_time_data_sha256']['research/prior.json'], '3' * 64)
        for path in ['rust/osw-query/src/index_store.rs', 'research/prior.json']:
            bad = copy.deepcopy(parent); bad['sha256'][path] = '0' * 64
            with self.assertRaises(ValueError): delivery.compile_inventory(original, bad, '6' * 64, '7' * 64)

    def overlay(self):
        original, parent = self.compiler()
        packet = {'schema': 'osw.query-packet.v1', 'logical_schema': 'osw.query-bundle.v1',
                  'hash_algorithm': 'sha256', 'part_byte_limit': PART_LIMIT,
                  'logical_sha256': '7' * 64, 'logical_byte_length': 8,
                  'parts': [{'index': 0, 'path': 'query-parts/000000-' + '8' * 64 + '.bin',
                             'sha256': '8' * 64, 'byte_length': 8}]}
        pins = {**{p: '6' * 64 for p in delivery.DOCUMENTS}, **self.contract['input_sha256'],
                context.FILE: delivery.sha(context.encoded(self.contract))}
        replacements = {p: '6' * 64 for p in delivery.GENERATED | delivery.DOCUMENTS}
        replacements.update(pins)
        replacements['almanac/' + packet['parts'][0]['path']] = '8' * 64
        inventory = delivery.compile_inventory(original, parent, replacements[delivery.CATALOG], packet['logical_sha256'])
        proof = {'compiled_catalog_dependency_verified': True, 'test_only_fixtures_compiled': 0,
                 'production_dependencies': [delivery.CATALOG, 'rust/osw-query/src/index_store.rs'],
                 'production_dependency_count': 2}
        return dict(parent=parent, original_inventory=original, inventory=inventory, replacements=replacements,
                    source_pins=pins, packet=packet, wasm_sha='9' * 64, compiler='rustc 1.95.0 (fixture)',
                    parent_manifest_sha=delivery.PARENT_MANIFEST_SHA, source_commit='a' * 40,
                    dependency_proof=proof)

    def test_engine_overlay_preserves_archives_and_sources(self):
        args = self.overlay(); before = copy.deepcopy(args)
        result = delivery.engine_manifest(**args)
        self.assertEqual(args, before)
        self.assertEqual(result['loop_published_metrics_presentation_revision_v1'],
                         args['parent']['loop_published_metrics_presentation_revision_v1'])
        self.assertEqual(result['sha256'][delivery.WASM], '9' * 64)
        self.assertEqual(result[delivery.RECEIPT]['changed_compile_time_data_paths'], [delivery.CATALOG])
        for p, pin in args['parent']['sha256'].items():
            if p not in {delivery.CATALOG, delivery.WASM}: self.assertEqual(result['sha256'][p], pin)

    def test_engine_refuses_wrong_parent_and_undeclared_dependencies(self):
        for mutation in ['parent_identity', 'binary_identity', 'test_fixture', 'unknown_dependency',
                         'source_pin', 'untracked_document', 'historical_pin', 'missing_output', 'wrong_part', 'inventory']:
            with self.subTest(mutation=mutation):
                args = self.overlay()
                if mutation == 'parent_identity': args['parent_manifest_sha'] = '0' * 64
                elif mutation == 'binary_identity': args['parent']['sha256'][delivery.WASM] = '0' * 64
                elif mutation == 'test_fixture': args['dependency_proof']['test_only_fixtures_compiled'] = 1
                elif mutation == 'unknown_dependency':
                    args['dependency_proof']['production_dependencies'].append('unknown.rs')
                    args['dependency_proof']['production_dependency_count'] += 1
                elif mutation == 'source_pin': args['source_pins'].pop(context.FILE)
                elif mutation == 'untracked_document':
                    args['source_pins'].pop('research/eicc-reference-query-preparation-v1.json')
                elif mutation == 'historical_pin': args['parent']['sha256'][context.FILE] = '0' * 64
                elif mutation == 'missing_output': args['replacements'].pop(delivery.DASHBOARD)
                elif mutation == 'wrong_part':
                    args['replacements']['almanac/' + args['packet']['parts'][0]['path']] = '0' * 64
                else: args['inventory']['compile_time_data_sha256']['research/prior.json'] = '0' * 64
                with self.assertRaises(ValueError): delivery.engine_manifest(**args)


if __name__ == '__main__':
    unittest.main()
