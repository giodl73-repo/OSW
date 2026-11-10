"""Packet and source-index preservation checks with small synthetic controls."""
import copy
import gzip
import json
import unittest
from collections import Counter

import pacific_secc_reference_delivery_v1 as delivery
import pacific_secc_publication_admission_v1 as admission
from test_pacific_secc_publication_admission_v1 import fixture


class PacificDelivery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = admission.build_contract()

    def parent(self):
        bundle = fixture()
        bundle['collections']['objects'][1]['type'] = 'test_control'
        owners = bundle['collections']['objects']
        doc = {'schema': 'osw.motion-dashboard.v1', 'fingerprint_version': 2,
               'entries': copy.deepcopy(owners), 'counts': dict(Counter(r['type'] for r in owners)),
               'prior_delivery_marker': {'preserve': True}}
        raw = delivery.encoded(doc)
        sha = admission.runtime.sha(raw)
        bundle['manifest']['dashboard_receipt'] = {'source_file': delivery.DASHBOARD,
            'source_json': raw.decode(), 'source_sha256': sha}
        bundle['manifest']['input_sha256'][delivery.DASHBOARD] = sha
        return bundle

    def test_candidate_preserves_all_other_tables_and_refreshes_direct_dashboard_link(self):
        parent = self.parent()
        original = delivery.encoded(parent)
        child, raw, audit = delivery.candidate(parent, self.document,
            parent_logical_sha256=admission.runtime.PARENT_LOGICAL)
        self.assertEqual(delivery.encoded(parent), original)
        for name in set(parent['collections']) - {'objects', 'route_decisions', 'sources', 'reference_routes'}:
            self.assertEqual(child['collections'][name], parent['collections'][name])
        self.assertEqual(child['collections']['sources'][:208], parent['collections']['sources'])
        doc = json.loads(raw)
        self.assertEqual(doc['entries'][1], parent['collections']['objects'][1])
        self.assertEqual(doc['entries'][0]['route_url'], self.document['atlas_route_url'])
        self.assertEqual(doc['prior_delivery_marker'], {'preserve': True})
        self.assertEqual(audit['candidate_collection_counts']['reference_routes'], 81)
        self.assertEqual(audit['candidate_collection_counts']['sources'], 210)
        self.assertEqual(audit['new_physical_dimensions'], 0)

    def test_corrupt_dashboard_and_forbidden_physical_owner_change_are_refused(self):
        parent = self.parent()
        parent['manifest']['dashboard_receipt']['source_sha256'] = 'wrong'
        raw = delivery.encoded(parent)
        with self.assertRaises(ValueError):
            delivery.candidate(parent, self.document, parent_logical_sha256=admission.runtime.PARENT_LOGICAL)
        self.assertEqual(delivery.encoded(parent), raw)
        before = admission.read_selected()['owner']
        after = copy.deepcopy(before)
        after['state_codes'] = ['invented-physical-passage']
        with self.assertRaises(ValueError):
            delivery.verify_owner(before, after)

    def test_index_preserves_old_scientific_source_strings_and_admits_only_declared_documents(self):
        old_path = 'research/unchanged-source.json'
        old_raw = b'{"schema":"test.original","value":42}\n'
        dash = b'{"schema":"osw.motion-dashboard.v1","entries":[]}\n'
        old = {old_path: old_raw.decode(), delivery.DASHBOARD: dash.decode()}
        corpus = delivery.encoded({'schema': 'osw.almanac-index-bundle.v1', 'documents': old})
        packed = gzip.compress(corpus, mtime=0)
        catalog = {'schema': 'osw.almanac-index-catalog.v1', 'source_count': 2,
            'documents': [{'path': path, 'source_sha256': admission.runtime.sha(raw.encode()),
                'source_bytes': len(raw.encode()), 'optional': False} for path, raw in old.items()],
            'bundle_sha256': admission.runtime.sha(corpus), 'bundle_bytes': len(corpus),
            'compressed_sha256': admission.runtime.sha(packed), 'compressed_bytes': len(packed)}
        registry = {'schema': 'osw.almanac-index-sources.v1', 'documents': sorted(old)}
        additions = {p: delivery.encoded({'schema': 'test.addition', 'path': p}) for p in delivery.DOCUMENTS}
        generated, audit = delivery.source_index(catalog, packed, registry, additions, dash)
        child = json.loads(gzip.decompress(generated['almanac/index-data.json.gz']))
        self.assertEqual(child['documents'][old_path], old_raw.decode())
        self.assertEqual(set(audit['added_source_paths']), delivery.DOCUMENTS)
        self.assertEqual(audit['scientific_source_documents_replaced'], 0)
        with self.assertRaises(ValueError):
            delivery.source_index(catalog, packed + b'changed', registry, additions, dash)


if __name__ == '__main__':
    unittest.main()
