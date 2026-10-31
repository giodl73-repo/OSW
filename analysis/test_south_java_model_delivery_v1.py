"""Tiny generated-custody fixtures, never the real atlas/index or engine."""
import copy
import gzip
import json
import unittest

import south_java_model_delivery_v1 as delivery


class Delivery(unittest.TestCase):
    def index(self):
        documents = {'research/legacy.json': '{}\n', delivery.DASHBOARD: '{}\n'}
        raw = delivery.encoded({'schema': 'osw.almanac-index-bundle.v1', 'documents': documents})
        compressed = gzip.compress(raw, mtime=0)
        catalog = {'schema': 'osw.almanac-index-catalog.v1', 'source_count': 2,
                   'documents': [{'path': path, 'source_sha256': delivery.sha(body.encode()),
                                  'source_bytes': len(body)} for path, body in documents.items()],
                   'input_sha256': {'research/legacy.json': delivery.sha(b'{}\n')},
                   'bundle_sha256': delivery.sha(raw), 'compressed_sha256': delivery.sha(compressed),
                   'bundle_bytes': len(raw)}
        return catalog, compressed, {'schema': 'osw.almanac-index-sources.v1', 'documents': sorted(documents)}

    def test_extend_preserves_original_text_and_refreshes_custody(self):
        catalog, compressed, registry = self.index()
        docs = {path: b'{"new":true}\n' for path in delivery.DOCUMENTS}
        generated, audit = delivery.source_index(catalog, compressed, registry, docs, b'{"dashboard":true}\n')
        corpus_raw = gzip.decompress(generated['almanac/index-data.json.gz'])
        corpus = json.loads(corpus_raw)
        updated = json.loads(generated['almanac/index-catalog.json'])
        self.assertEqual(corpus['documents']['research/legacy.json'], '{}\n')
        self.assertEqual(audit['replaced_source_paths'], [delivery.DASHBOARD])
        self.assertEqual(updated['bundle_sha256'], delivery.sha(corpus_raw))
        self.assertEqual(updated['source_count'], 5)
        self.assertEqual(catalog['source_count'], 2)

    def test_changed_parent_index_refused(self):
        catalog, compressed, registry = self.index()
        with self.assertRaisesRegex(ValueError, 'compressed parent'):
            delivery.source_index(catalog, compressed + b'x', registry,
                                  {path: b'{}' for path in delivery.DOCUMENTS}, b'{}')

    def test_packet_manifest_preserves_scientific_fields(self):
        original = {'input_sha256': {'science': 'old', 'almanac/index-catalog.json': 'old'},
                    'generator': {'original': True}, 'dashboard_receipt': {'unchanged': True}}
        updated = delivery.packet_manifest(original, {path: b'new' for path in delivery.INDEX},
                                           {path: b'{}' for path in delivery.DOCUMENTS},
                                           verified_candidate_sha='a' * 64, index_audit={'preserved': 2})
        self.assertEqual(updated['input_sha256']['science'], 'old')
        self.assertEqual(updated['generator'], original['generator'])
        self.assertEqual(updated['dashboard_receipt'], original['dashboard_receipt'])
        self.assertNotIn(delivery.PROVENANCE, original)

    def overlay(self):
        pin = 'a' * 64
        part = {'index': 0, 'path': 'query-parts/000000-' + pin + '.bin', 'sha256': pin, 'byte_length': 1}
        packet = {'schema': 'osw.query-packet.v1', 'logical_schema': 'osw.query-bundle.v1',
                  'hash_algorithm': 'sha256', 'part_byte_limit': 16777216,
                  'logical_byte_length': 1, 'logical_sha256': pin, 'parts': [part]}
        replacements = {path: 'b' * 64 for path in delivery.GENERATED | delivery.UI | delivery.DOCUMENTS | {delivery.FIGURE}}
        replacements['almanac/' + part['path']] = pin
        parent = {'schema': 'osw.query-engine-manifest.v1', 'abi_version': 1,
                  'sha256': {delivery.WASM: delivery.WASM_SHA, 'rust/science.rs': 'c' * 64},
                  'historical_receipt': {'retained': True}}
        return parent, replacements, packet

    def test_overlay_preserves_binary_compiled_sources_and_prior_receipts(self):
        parent, replacements, packet = self.overlay()
        updated = delivery.engine_manifest(parent, replacements, packet, source_commit='d' * 40)
        self.assertEqual(updated['sha256'][delivery.WASM], delivery.WASM_SHA)
        self.assertEqual(updated['sha256']['rust/science.rs'], 'c' * 64)
        self.assertEqual(updated['historical_receipt'], parent['historical_receipt'])
        self.assertNotIn(delivery.PROVENANCE, parent)

    def test_overlay_rejects_hidden_runtime_change_or_wrong_part(self):
        parent, replacements, packet = self.overlay()
        for bad in [{**replacements, 'rust/science.rs': 'd' * 64},
                    {**replacements, 'almanac/' + packet['parts'][0]['path']: 'd' * 64}]:
            with self.assertRaises(ValueError):
                delivery.engine_manifest(parent, bad, packet, source_commit='d' * 40)

    def test_existing_content_addressed_part_cannot_be_replaced(self):
        parent, replacements, packet = self.overlay()
        parent['sha256']['almanac/' + packet['parts'][0]['path']] = 'e' * 64
        with self.assertRaisesRegex(ValueError, 'would change'):
            delivery.engine_manifest(parent, replacements, packet, source_commit='d' * 40)


if __name__ == '__main__':
    unittest.main()
