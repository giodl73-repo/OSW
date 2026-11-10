"""Use exact selected parent rows plus synthetic unrelated registry controls."""
import copy
import unittest
from urllib.parse import parse_qs, urlsplit

import pacific_secc_publication_admission_v1 as admission
from pacific_secc_reference_runtime_v1 import query, ROOT

FIXTURE = 'research/pacific-secc-reference-publication-fixture-v1.json'


def fixture():
    selected = admission.read_selected()
    owner = copy.deepcopy(selected['owner'])
    sources = copy.deepcopy(selected['owner_sources'])
    sources += [{'id': 'source:unrelated-control-' + str(i), 'kind': 'external', 'preserve': i}
                for i in range(208 - len(sources))]
    collections = {'objects': [owner, {'id': 'test:other-owner', 'preserve': True}],
        'entities': [copy.deepcopy(selected['entity'])], 'sources': sources,
        'route_decisions': [copy.deepcopy(selected['planning_decision'])],
        'reference_routes': [{'id': 'unrelated-route-' + str(i), 'current_id': 'unrelated'} for i in range(80)],
        'widths': [{'id': 'physical-width-control', 'width_km': 300}],
        'width_samples': [], 'state_links': [{'id': 'state-control', 'state_code': 'KEEP'}],
        'geometries': [], 'length_assessments': [{'id': 'length-control', 'rank_eligible': False}]}
    inputs = {admission.runtime.PLANNING: admission.runtime.PLANNING_SHA}
    inputs.update({r['note']['audit_file']: r['source_sha256'] for r in selected['planning_decision']['scope_reviews']})
    return {'schema': 'osw.query-bundle.v1', 'collections': collections, 'manifest': {'input_sha256': inputs}}


def applied_fixture(document):
    result = fixture()
    admission.prepare(result['collections'], result['manifest'], document,
                      parent_logical_sha256=admission.runtime.PARENT_LOGICAL)
    return result


class PublicationAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = admission.build_contract()

    def test_exact_audited_parent_gains_one_publication_method_and_reference(self):
        old = fixture()
        before = query.encoded(old)
        after = copy.deepcopy(old)
        result = admission.prepare(after['collections'], after['manifest'], self.document,
                                   parent_logical_sha256=admission.runtime.PARENT_LOGICAL)
        self.assertTrue(result['publication_added'])
        self.assertEqual(query.encoded(old), before)
        self.assertEqual(after['collections']['sources'][:208], old['collections']['sources'])
        self.assertEqual(after['collections']['sources'][208], self.document['publication_source'])
        self.assertEqual(len(after['collections']['sources']), 210)
        self.assertEqual(len(after['collections']['reference_routes']), 81)
        self.assertEqual(after['collections']['reference_routes'][:80], old['collections']['reference_routes'])
        for name in ['entities', 'widths', 'width_samples', 'state_links', 'geometries', 'length_assessments']:
            self.assertEqual(after['collections'][name], old['collections'][name])
        self.assertEqual(after['collections']['objects'][1], old['collections']['objects'][1])
        receipt = after['manifest'][admission.runtime.KEY]
        self.assertEqual(receipt['publication_admission'], self.document)
        self.assertEqual(receipt['prior_owner'], old['collections']['objects'][0])

    def test_atlas_link_selects_the_current_and_route_and_fingerprint_matches(self):
        result = applied_fixture(self.document)
        owner = result['collections']['objects'][0]
        args = parse_qs(urlsplit(owner['route_url']).query)
        self.assertEqual(args['atlas-feature'], [query.TARGET])
        self.assertEqual(args['atlas-route'], [query.ROUTE])
        self.assertEqual(urlsplit(owner['route_url']).fragment, 'route-atlas')
        self.assertEqual(owner['fingerprint'], query.fingerprint({k: v for k, v in owner.items() if k != 'fingerprint'}))
        receipt = result['manifest'][admission.runtime.KEY]
        self.assertEqual(admission.runtime.sha(receipt['owner_fingerprint_json'].encode()), owner['fingerprint'])
        self.assertIsNone(owner['published_length_km'])
        self.assertEqual(owner['capabilities']['geometry'], 0)
        self.assertEqual(owner['capabilities']['width_samples'], 0)

    def test_alias_collision_changed_parent_and_repeat_refused_atomically(self):
        for change in ['title', 'doi', 'id', 'owner', 'source-count', 'owner-source', 'repeat']:
            data = fixture()
            if change == 'title':
                data['collections']['sources'][-1]['title'] = 'Seasonal variability of the South Equatorial Countercurrent'
            elif change == 'doi':
                data['collections']['sources'][-1]['doi'] = query.DOI
            elif change == 'id':
                data['collections']['sources'][-1]['id'] = admission.PAPER
            elif change == 'owner':
                data['collections']['objects'][0]['route_url'] = 'wrong.html'
            elif change == 'source-count':
                data['collections']['sources'].pop()
            elif change == 'owner-source':
                data['collections']['sources'][0]['label'] = 'changed'
            elif change == 'repeat':
                admission.prepare(data['collections'], data['manifest'], self.document,
                                  parent_logical_sha256=admission.runtime.PARENT_LOGICAL)
            before = query.encoded(data)
            with self.assertRaises(ValueError):
                admission.prepare(data['collections'], data['manifest'], self.document,
                                  parent_logical_sha256=admission.runtime.PARENT_LOGICAL)
            self.assertEqual(query.encoded(data), before)

    def test_saved_native_fixture_reproduces_exactly(self):
        self.assertEqual((ROOT / FIXTURE).read_bytes(), query.encoded(applied_fixture(self.document)))


if __name__ == '__main__':
    unittest.main()
