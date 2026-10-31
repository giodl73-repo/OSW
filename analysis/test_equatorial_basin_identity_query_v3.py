import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import equatorial_basin_identity_query_v3 as m
import test_equatorial_basin_identity_query_v2 as prior_fixtures


def manifest(c):
    receipts = []
    pins = {'older.json': 'unchanged'}
    for path, value in [('research/ocean-current-almanac.json', {'entries': []}),
                        ('research/ocean-motion-taxonomy.json', {'axes': {'identity_level': {}}})]:
        raw = json.dumps(value, indent=2) + '\n'
        digest = hashlib.sha256(raw.encode()).hexdigest()
        receipts.append({'file': path, 'source_json': raw, 'sha256': digest})
        pins[path] = digest
    return {'historical': {'keep': [1, 2]}, 'input_sha256': pins,
            'taxonomy': {'schema': 'osw.query-taxonomy.v1', 'scope': m.TAXONOMY_SCOPE,
                         'complete_physical_taxonomy': False, 'measurement_inheritance_eligible': False,
                         'source_receipts': receipts, 'identity_levels': {'keep': 'unchanged'},
                         **c['taxonomy_counts']['before']}}


class TaxonomyIdentityContract(unittest.TestCase):
    def fixture(self):
        #Reduced selected-family/source rehearsal. It does not load installed data.
        _, rows = prior_fixtures.BasinIdentityContract().small_rehearsal()
        rows['taxonomy_links'] = [{'id': 'fixture:old-taxonomy-link', 'keep': [1, 2]}]
        c = m.build_contract()
        c['prior_collection_counts'] = {k: len(v) for k, v in rows.items()}
        c['after_collection_counts'] = {**c['prior_collection_counts'], **{
            k: c['prior_collection_counts'].get(k, 0) + len(v) for k, v in c['additions'].items()}}
        c['taxonomy_counts'] = {'before': {'node_count': len(rows['objects']), 'link_count': len(rows['taxonomy_links'])},
                               'after': {'node_count': len(rows['objects']) + 5, 'link_count': len(rows['taxonomy_links']) + 5}}
        return c, rows, manifest(c)

    def apply(self, rows, state, c):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / m.FILE
            path.parent.mkdir(parents=True)
            path.write_bytes(m.encoded(c))
            with patch.object(m, 'ROOT', Path(folder)), patch.object(m, 'build_contract', return_value=copy.deepcopy(c)):
                m.prepare(rows, state, c, parent_logical_sha256=m.PARENT)

    def test_actual_contract_rebuilds_and_preserves_all_seven_v2_additions(self):
        c = m.build_contract()
        self.assertEqual(m.encoded(c), (m.ROOT / m.FILE).read_bytes())
        old = m.previous.build_contract()
        for name, rows in old['additions'].items():
            self.assertEqual(c['additions'][name], rows, name)
        self.assertEqual(sum(map(len, c['additions'].values())), 40)
        self.assertEqual(c['taxonomy_counts'], {'before': {'node_count': 246, 'link_count': 20},
                                              'after': {'node_count': 251, 'link_count': 25}})
        self.assertEqual(c['after_collection_counts']['taxonomy_links'], 25)
        for name in ['widths', 'width_samples', 'reference_routes', 'sources']:
            self.assertEqual(c['after_collection_counts'][name], c['prior_collection_counts'][name])

    def test_each_link_resolves_the_exact_member_and_parent_without_physical_claims(self):
        c = m.build_contract()
        links = c['additions']['taxonomy_links']
        self.assertEqual(len({r['id'] for r in links}), 5)
        self.assertEqual({r['child_id'] for r in links}, set(c['expected_entity_ids']))
        for i, link in enumerate(links):
            member = c['additions']['current_basin_memberships'][i]
            self.assertEqual(link['child_id'], member['entity_id'])
            self.assertEqual(link['parent_id'], member['family_entity_id'])
            self.assertEqual(link['source_file'], m.FILE)
            self.assertEqual(link['source_pointer'], f'/additions/current_basin_memberships/{i}')
            self.assertFalse(link['physical_connectivity_eligible'])
            self.assertFalse(link['measurement_inheritance_eligible'])
            self.assertFalse(link['naming_source_is_parent_relation_evidence'])

    def test_atomic_application_appends_links_and_changes_only_two_taxonomy_counts(self):
        c, rows, state = self.fixture()
        oldrows, oldstate = copy.deepcopy(rows), copy.deepcopy(state)
        self.apply(rows, state, c)
        for name, old in oldrows.items():
            self.assertEqual(rows[name], old + c['additions'].get(name, []), name)
        expected = copy.deepcopy(oldstate['taxonomy'])
        expected.update(c['taxonomy_counts']['after'])
        self.assertEqual(state['taxonomy'], expected)
        self.assertEqual(state['taxonomy']['source_receipts'], oldstate['taxonomy']['source_receipts'])
        self.assertEqual(state['historical'], oldstate['historical'])
        self.assertEqual(state['input_sha256']['older.json'], 'unchanged')
        self.assertEqual(state[m.KEY]['new_measurements'], 0)

    def test_wrong_counts_scope_receipts_and_source_hashes_refused_without_mutation(self):
        mutations = [lambda s: s['taxonomy'].update(node_count=999),
                     lambda s: s['taxonomy'].update(link_count=999),
                     lambda s: s['taxonomy'].update(physical=True, complete_physical_taxonomy=True),
                     lambda s: s['taxonomy'].update(scope='changed'),
                     lambda s: s['taxonomy']['source_receipts'].pop(),
                     lambda s: s['taxonomy']['source_receipts'][0].update(source_json='{}'),
                     lambda s: s['input_sha256'].update({'research/ocean-current-almanac.json': 'wrong'})]
        for mutate in mutations:
            c, rows, state = self.fixture()
            mutate(state)
            before = copy.deepcopy((rows, state))
            with self.assertRaises(ValueError):
                self.apply(rows, state, c)
            self.assertEqual((rows, state), before)

    def test_link_id_collision_and_changed_family_refused_atomically(self):
        for kind in ['collision', 'family', 'source']:
            c, rows, state = self.fixture()
            if kind == 'collision':
                rows['taxonomy_links'][0]['id'] = c['additions']['taxonomy_links'][0]['id']
            elif kind == 'family':
                rows['entities'][0]['label'] = 'changed family'
            else:
                rows['sources'][0]['label'] = 'changed historical source'
            before = copy.deepcopy((rows, state))
            with self.assertRaises(ValueError):
                self.apply(rows, state, c)
            self.assertEqual((rows, state), before)

    def test_repeated_and_failed_v2_receipt_refused(self):
        c, rows, state = self.fixture()
        state[m.previous.KEY] = {}
        with self.assertRaises(ValueError):
            self.apply(rows, state, c)
        c, rows, state = self.fixture()
        self.apply(rows, state, c)
        before = copy.deepcopy((rows, state))
        with self.assertRaises(ValueError):
            self.apply(rows, state, c)
        self.assertEqual((rows, state), before)

    def test_wrong_parent_or_modified_frozen_contract_refused(self):
        c = m.build_contract()
        with self.assertRaises(ValueError):
            m.prepare({}, {}, c, parent_logical_sha256='wrong')
        c['additions']['taxonomy_links'][0]['physical_connectivity_eligible'] = True
        with self.assertRaises(ValueError):
            m.prepare({}, {}, c, parent_logical_sha256=m.PARENT)

    def test_coherently_rewritten_file_cannot_promote_a_different_parent_or_measurement(self):
        trusted = m.build_contract()
        for field, value in [('parent_id', 'current:other'), ('measurement_inheritance_eligible', True)]:
            c = copy.deepcopy(trusted)
            c['additions']['taxonomy_links'][0][field] = value
            with tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / m.FILE
                path.parent.mkdir(parents=True)
                path.write_bytes(m.encoded(c))
                with patch.object(m, 'ROOT', Path(folder)), patch.object(m, 'build_contract', return_value=trusted):
                    with self.assertRaises(ValueError):
                        m.prepare({}, {}, c, parent_logical_sha256=m.PARENT)


if __name__ == '__main__':
    unittest.main()
