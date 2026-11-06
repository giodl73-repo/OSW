"""Lossless packet/dashboard/source-index checks using small synthetic peers."""
import copy
import gzip
import json
import unittest

import south_java_reference_delivery_v1 as delivery
import south_java_reference_fixture_v1 as fixture

runtime = delivery.runtime
query = runtime.query


def parent_fixture():
    contract, collections, manifest, _ = fixture.unprepared()
    peer = {'id': 'fixture:other-current', 'type': 'named_current', 'width_km': 123,
            'fingerprint': 'fixture:unchanged'}
    collections['objects'].append(peer)
    dashboard = {'schema': 'osw.motion-dashboard.v1', 'fingerprint_version': 2,
        'counts': {'named_current': 2}, 'entries': copy.deepcopy(collections['objects']),
        'historical_namespace': {'must': 'survive'}}
    raw = json.dumps(dashboard, indent=2) + '\n'
    manifest['dashboard_receipt'] = {'source_file': delivery.DASHBOARD,
        'source_sha256': runtime.sha(raw.encode()), 'source_json': raw}
    manifest['input_sha256'][delivery.DASHBOARD] = runtime.sha(raw.encode())
    return contract, {'schema': 'osw.query-bundle.v1', 'manifest': manifest, 'collections': collections}


def index_fixture():
    documents = {'research/fixture-historical.json': '{ "value": 2, "notes": "preserve whitespace" }\n',
                 delivery.DASHBOARD: '{"schema":"fixture-old-dashboard"}\n'}
    corpus = {'schema': 'osw.almanac-index-bundle.v1', 'documents': documents}
    raw = delivery.encoded(corpus)
    packed = gzip.compress(raw, mtime=0)
    catalog = {'schema': 'osw.almanac-index-catalog.v1', 'source_count': len(documents),
        'documents': [{'path': p, 'source_sha256': runtime.sha(t.encode()), 'source_bytes': len(t.encode())}
                      for p, t in documents.items()], 'bundle_bytes': len(raw),
        'bundle_sha256': runtime.sha(raw), 'compressed_bytes': len(packed),
        'compressed_sha256': runtime.sha(packed)}
    registry = {'schema': 'osw.almanac-index-sources.v1', 'documents': list(documents)}
    additions = {p: (runtime.ROOT / p).read_bytes() for p in delivery.DOCUMENTS}
    return catalog, packed, registry, additions


class ReferenceDelivery(unittest.TestCase):
    def test_packet_keeps_science_and_peers_and_refreshes_only_selected_dashboard(self):
        contract, bundle = parent_fixture()
        before = copy.deepcopy(bundle)
        child, dashboard_raw, audit = delivery.candidate(bundle, contract, parent_logical_sha256=query.PARENT)
        self.assertEqual(bundle, before)
        for name in ['widths', 'width_samples', 'entities']:
            self.assertIs(child['collections'][name], bundle['collections'][name])
        self.assertEqual(child['collections']['sources'][:210], bundle['collections']['sources'])
        self.assertEqual(child['collections']['reference_routes'][:81], bundle['collections']['reference_routes'])
        self.assertEqual(len(child['collections']['sources']), 211)
        self.assertEqual(len(child['collections']['reference_routes']), 82)
        self.assertEqual(child['collections']['objects'][1], bundle['collections']['objects'][1])
        old = json.loads(bundle['manifest']['dashboard_receipt']['source_json'])
        new = json.loads(dashboard_raw)
        self.assertEqual(new['entries'][1], old['entries'][1])
        self.assertEqual(new['historical_namespace'], old['historical_namespace'])
        self.assertEqual(new['counts'], old['counts'])
        self.assertEqual(new['entries'][0]['route_ids'], [query.ROUTE])
        self.assertEqual(new[runtime.KEY]['new_physical_dimensions'], 0)
        self.assertTrue(audit['unrelated_scientific_collections_preserved'])

    def test_stale_dashboard_and_unrelated_owner_changes_are_refused(self):
        contract, bundle = parent_fixture()
        bundle['manifest']['dashboard_receipt']['source_sha256'] = '0' * 64
        before = copy.deepcopy(bundle)
        with self.assertRaises(ValueError):
            delivery.candidate(bundle, contract, parent_logical_sha256=query.PARENT)
        self.assertEqual(bundle, before)
        owner = contract['query_contract']['prior_owner']
        changed = copy.deepcopy(owner)
        changed['unrelated_physical_length_km'] = 1100
        with self.assertRaises(ValueError):
            delivery.verify_owner(owner, changed)

    def test_index_keeps_historical_source_strings_and_manifest_pins(self):
        catalog, packed, registry, documents = index_fixture()
        before = copy.deepcopy((catalog, registry))
        generated, audit = delivery.source_index(catalog, packed, registry, documents, b'{"refreshed":true}\n')
        self.assertEqual((catalog, registry), before)
        corpus = json.loads(gzip.decompress(generated['almanac/index-data.json.gz']))
        self.assertEqual(corpus['documents']['research/fixture-historical.json'],
                         '{ "value": 2, "notes": "preserve whitespace" }\n')
        self.assertEqual(audit['replaced_source_paths'], [delivery.DASHBOARD])
        self.assertEqual(set(audit['added_source_paths']), delivery.DOCUMENTS)
        manifest = {'input_sha256': {}, runtime.KEY: {'existing_receipt': True}}
        result = delivery.packet_manifest(manifest, generated, documents, audit)
        self.assertEqual(result[runtime.KEY]['existing_receipt'], True)
        for p, raw in {**generated, **documents}.items():
            self.assertEqual(result['input_sha256'][p], runtime.sha(raw))
        self.assertEqual(manifest['input_sha256'], {})

    def test_corrupted_index_and_historical_overwrite_are_refused(self):
        catalog, packed, registry, documents = index_fixture()
        with self.assertRaises(ValueError):
            delivery.source_index(catalog, packed + b'x', registry, documents, b'{}')
        # Even a correctly rehashed parent must not allow replacement of a historical source.
        corpus = json.loads(gzip.decompress(packed))
        target = sorted(delivery.DOCUMENTS)[0]
        corpus['documents'][target] = '{"historical":true}\n'
        text = corpus['documents'][target]
        catalog['documents'].append({'path': target, 'source_sha256': runtime.sha(text.encode()),
                                     'source_bytes': len(text.encode())})
        catalog['source_count'] += 1
        registry['documents'].append(target)
        raw = delivery.encoded(corpus);packed = gzip.compress(raw, mtime=0)
        catalog.update(bundle_sha256=runtime.sha(raw), bundle_bytes=len(raw),
                       compressed_sha256=runtime.sha(packed), compressed_bytes=len(packed))
        with self.assertRaises(ValueError):
            delivery.source_index(catalog, packed, registry, documents, b'{}')


if __name__ == '__main__':
    unittest.main()
