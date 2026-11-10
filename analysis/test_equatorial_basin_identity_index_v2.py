import copy
import json
import os
import unittest
from unittest.mock import patch
import equatorial_basin_identity_index_v2 as m


def tiny_parent():
    #636 synthetic tiny source strings; this does not read the installed index.
    documents = {f'research/fixture-{i}.json': '{ "fixture": ' + str(i) + ' }\n' for i in range(636)}
    catalog = {'schema': 'osw.almanac-index-catalog.v1', 'source_count': 636, 'documents': [
        {'path': p, 'source_sha256': m.sha(text.encode()), 'source_bytes': len(text.encode()), 'optional': False}
        for p, text in documents.items()]}
    return catalog, {'schema': 'osw.almanac-index-bundle.v1', 'documents': documents}, {
        'schema': 'osw.almanac-index-sources.v1', 'documents': list(documents)}


class SourceIndex(unittest.TestCase):
    def test_local_access_refused_before_decompression(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(m.gzip, 'decompress', side_effect=AssertionError('early read')):
            with self.assertRaises(ValueError):
                m.source_index(None, None, None)

    def test_three_actual_identity_documents_append_and_all_synthetic_strings_survive(self):
        parent = tiny_parent()
        before = copy.deepcopy(parent)
        added = {p: (m.query.ROOT / p).read_bytes() for p in m.DOCUMENTS}
        catalog, corpus, registry, audit = m.extend(*parent, added)
        m.verify_audit(audit)
        self.assertEqual(parent, before)
        self.assertEqual(catalog['source_count'], 639)
        self.assertEqual(len(registry['documents']), 639)
        for p, text in before[1]['documents'].items():
            self.assertEqual(corpus['documents'][p], text)
        contract = json.loads(corpus['documents'][m.query.FILE])
        self.assertEqual(len(contract['additions']['current_basin_memberships']), 5)
        self.assertTrue(all(row['measurements_inherited'] is False for row in contract['additions']['current_basin_memberships']))

    def test_corrupt_parent_text_or_historical_replacement_refused(self):
        parent = tiny_parent()
        parent[1]['documents']['research/fixture-0.json'] = '{}'
        with self.assertRaises(ValueError):
            m.extend(*parent, {})
        with self.assertRaises(ValueError):
            m.extend(*tiny_parent(), {'research/fixture-0.json': b'{}'})

    def test_strict_audit_rejects_count_drift_replacement_and_extra_source(self):
        _, _, _, audit = m.extend(*tiny_parent(), {p: (m.query.ROOT / p).read_bytes() for p in m.DOCUMENTS})
        for key, value in [('original_sources_verified', 635), ('original_source_strings_preserved', 635),
                           ('replaced_source_paths', ['research/fixture-0.json']),
                           ('added_source_paths', m.DOCUMENTS + ['research/extra.json'])]:
            bad = copy.deepcopy(audit)
            bad[key] = value
            with self.assertRaises(ValueError):
                m.verify_audit(bad)

    def test_attach_preserves_prior_manifest_and_collections_and_rejects_repeat(self):
        _, _, _, audit = m.extend(*tiny_parent(), {p: (m.query.ROOT / p).read_bytes() for p in m.DOCUMENTS})
        bundle = {'manifest': {'historical': {'keep': True}, m.query.KEY: {}, 'input_sha256': {'old': 'unchanged'}},
                  'collections': {'current_basin_memberships': m.query.build_contract()['additions']['current_basin_memberships']}}
        old = copy.deepcopy(bundle)
        generated = {p: b'{}' for p in m.INDEX}
        generated['almanac/index-catalog.json'] = b'{"source_count":639}'
        child = m.attach(bundle, generated, audit)
        self.assertEqual(bundle, old)
        self.assertIs(child['collections'], bundle['collections'])
        self.assertEqual(child['manifest']['historical'], old['manifest']['historical'])
        self.assertEqual(child['manifest']['input_sha256']['old'], 'unchanged')
        with self.assertRaises(ValueError):
            m.attach(child, generated, audit)
        generated['almanac/index-catalog.json'] = b'{"source_count":638}'
        with self.assertRaises(ValueError):
            m.attach(bundle, generated, audit)


if __name__ == '__main__':
    unittest.main()
