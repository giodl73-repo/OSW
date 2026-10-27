"""Small source fixtures: no installed packet, native build or browser required."""
import copy
import json
import unittest
import azores_2009_section_projection_v1 as p


class SectionPresentation(unittest.TestCase):
    def fixture(self):
        return {'schema': 'osw.query-bundle.v1', 'manifest': {'input_sha256': {'prior': 'preserved'}, 'history': [1, 2]},
                'collections': {'widths': copy.deepcopy(json.loads((p.ROOT / p.BINDINGS).read_bytes())['records']),
                                'objects': [{'id': 'current:azores'}, {'id': 'current:azores-countercurrent'}],
                                'reference_routes': [{'id': 'unrelated'}]}}

    def test_only_manifest_provenance_is_extended(self):
        before = self.fixture()
        snapshot = copy.deepcopy(before)
        after = p.prepare(before, logical_parent_sha256=p.PARENT)
        self.assertEqual(before, snapshot)
        self.assertIs(after['collections'], before['collections'])
        self.assertEqual(after['manifest']['history'], snapshot['manifest']['history'])
        self.assertEqual(after['manifest']['input_sha256']['prior'], 'preserved')
        self.assertEqual(after['manifest'][p.KEY], p.marker())

    def test_changed_width_layer_period_geometry_and_identity_refused(self):
        for field, value in [('approximate_width_km', 111), ('current_id', 'wrong'),
                             ('observed_period', {'start': '2010-10-26', 'end': '2010-11-01'}),
                             ('layer', 'surface-only'), ('section_geometry', None),
                             ('width_range_km', [100, 120]), ('width_rank_eligible', True)]:
            with self.subTest(field=field):
                data = self.fixture(); data['collections']['widths'][0][field] = value
                with self.assertRaises(ValueError):
                    p.prepare(data, logical_parent_sha256=p.PARENT)

    def test_missing_duplicate_parent_and_source_rebinding_refused(self):
        for edit in [lambda d: d['collections']['widths'].pop(),
                     lambda d: d['collections']['widths'].append(copy.deepcopy(d['collections']['widths'][0])),
                     lambda d: d['manifest']['input_sha256'].update({p.REVIEW: 'wrong'}),
                     lambda d: d['manifest'].update({p.KEY: {}})]:
            data = self.fixture(); edit(data)
            with self.assertRaises(ValueError):
                p.prepare(data, logical_parent_sha256=p.PARENT)
        with self.assertRaises(ValueError):
            p.prepare(self.fixture(), logical_parent_sha256='wrong')

    def test_original_index_strings_survive_extension(self):
        raw = b'{"schema":"old.v1","value":42}\n'
        path = 'research/old.json'
        descriptor = {'path': path, 'source_sha256': p.sha(raw), 'source_bytes': len(raw)}
        catalog = {'schema': 'osw.almanac-index-catalog.v1', 'documents': [descriptor], 'source_count': 1}
        corpus = {'schema': 'osw.almanac-index-bundle.v1', 'documents': {path: raw.decode()}}
        registry = {'schema': 'osw.almanac-index-sources.v1', 'documents': [path]}
        _, after, _, audit = p.extend_source_index(catalog, corpus, registry)
        self.assertEqual(after['documents'][path], raw.decode())
        self.assertEqual(audit['scientific_source_documents_replaced'], 0)
        self.assertEqual(set(audit['added_source_paths']), set(p.documents()))


if __name__ == '__main__':
    unittest.main()
