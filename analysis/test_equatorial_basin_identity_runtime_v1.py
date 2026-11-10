import copy
import json
import unittest
from unittest.mock import patch
import equatorial_basin_identity_runtime_v1 as m


def audit():
    return {'added_source_paths': m.index.DOCUMENTS, 'replaced_source_paths': [],
            'original_sources_verified': 636, 'original_source_strings_preserved': 636,
            'scientific_source_documents_replaced': 0}


def dashboard():
    #Synthetic entries, not the installed dashboard.
    return {'entries': [{'id': 'fixture:' + str(i), 'keep': [i]} for i in range(246)],
            'counts': {'named_current': 106, 'named_eddy': 23}, 'proposed_current_additions': 23,
            'snapshot_fingerprint': 'a' * 64, 'prior_projection': {'keep': [1, 2]}}


def catalogue():
    return {'remaining_current_decisions': [{'current_id': 'other', 'keep': True}],
            'planning_taxonomy': {'strategies': [{'id': 'source_axis_definition_required', 'current_count': 8, 'unbuilt_count': 8},
                                                {'id': 'other', 'keep': [1, 2]}]},
            'counts': {'accepted_current_names': 106, 'currents_without_any_reference_card': 30,
                       'currents_without_route_candidates': 30, 'currents_without_published_ranked_estimate': 93,
                       'route_decision_records': 1, 'currents_with_route_candidates': 76},
            'candidates': [{'id': 'old:route', 'coordinates': [[1, 2], [3, 4]]}], 'historical': {'keep': True}}


def snapshot_pair(name):
    old = {'ok': True, 'engine': 'rust-osw-query-v1', 'bundle_sha256': 'a' * 64,
           'scientific_sentinel': {'widths': [42], 'dates': ['2020-01-01']}}
    if name == 'dashboard':
        old['snapshot_json'] = json.dumps(dashboard())
        new = copy.deepcopy(old)
        new['snapshot_json'] = json.dumps(m.dashboard_document(dashboard()))
    else:
        old.update(admitted_current_decisions=[{'current_id': 'old', 'measurement_ids': ['keep']}],
                   working_reference_routes=catalogue(), supplemental_widths=[{'id': 'old:width', 'width_km': 42}],
                   current_dimension_evidence_scenes={'old': {'records': [{'keep': True}]}},
                   sources_json={'other': '{ "keep": true }\n'})
        if name == 'atlas':
            old['sources_json']['research/ocean-motion-dashboard.json'] = json.dumps(dashboard())
        else:
            old['phase_plans'] = {'old': {'phases': [{'id': 'old:phase'}], 'can_play': False}}
        new = copy.deepcopy(old)
        new.update(basin_identity_scenes=m.scenes(), basin_identity_contract=m.contract(),
                   basin_identity_planning=m.query.read(m.query.PLANNING))
        new['admitted_current_decisions'] += m.decisions()
        new['working_reference_routes'] = m.catalogue_document(old['working_reference_routes'])
        if name == 'atlas':
            new['sources_json']['research/ocean-motion-dashboard.json'] = json.dumps(m.dashboard_document(dashboard()))
        else:
            new['phase_plans'].update({r['current_id']: m.empty_plan(r['current_id']) for r in m.decisions()})
    new['bundle_sha256'] = 'b' * 64
    return old, new


class RuntimePreservation(unittest.TestCase):
    def collection_pair(self):
        c = m.contract()
        #Reduced synthetic inventory; only count expectations are adapted below.
        collections = {name: [{'id': 'fixture:' + name, 'keep': {'values': [1, 2]}}]
                       for name in c['prior_collection_counts']}
        c['prior_collection_counts'] = {name: len(rows) for name, rows in collections.items()}
        manifest = {'historical': {'keep': [1, 2]}, 'input_sha256': {'old': 'c' * 64}}
        parent = {'schema': 'osw.query-bundle.v1', 'collections': collections, 'manifest': manifest}
        child = copy.deepcopy(parent)
        for name, rows in c['additions'].items():
            child['collections'].setdefault(name, []).extend(copy.deepcopy(rows))
        child['manifest'][m.query.KEY] = m.marker(c)
        child['manifest'][m.index.KEY] = audit()
        child['manifest']['input_sha256'].update({**c['input_sha256'], m.query.FILE: m.query.sha(m.query.FILE),
                                                **{p: 'd' * 64 for p in m.index.INDEX}})
        return c, parent, child

    def test_exact_append_only_collections_and_historical_rows(self):
        c, parent, child = self.collection_pair()
        with patch.object(m, 'contract', return_value=c):
            m.verify_collections(parent, child)
            for name in ['widths', 'reference_routes', 'sources', 'hydrography_samples', 'entities', 'objects']:
                bad = copy.deepcopy(child)
                bad['collections'][name][0]['keep']['values'].append(3)
                with self.assertRaises(ValueError, msg=name):
                    m.verify_collections(parent, bad)
            bad = copy.deepcopy(child)
            bad['collections']['names'].reverse()
            with self.assertRaises(ValueError):
                m.verify_collections(parent, bad)

    def test_manifest_envelope_receipt_and_pin_rebinding_refused(self):
        c, parent, child = self.collection_pair()
        mutations = [lambda b: b.update(unknown=True),
                     lambda b: b['manifest']['historical']['keep'].append(3),
                     lambda b: b['manifest']['input_sha256'].update(old='e' * 64),
                     lambda b: b['manifest'][m.query.KEY].update(new_measurements=1),
                     lambda b: b['manifest'][m.index.KEY].update(original_source_strings_preserved=635),
                     lambda b: b['manifest']['input_sha256'].update({'almanac/index-data.json.gz': 'bad'})]
        with patch.object(m, 'contract', return_value=c):
            for mutate in mutations:
                bad = copy.deepcopy(child)
                mutate(bad)
                with self.assertRaises(ValueError):
                    m.verify_collections(parent, bad)

    def test_dashboard_preserves_all_prior_entries_and_reduces_proposals(self):
        old = dashboard()
        before = copy.deepcopy(old)
        new = m.dashboard_document(old)
        self.assertEqual(old, before)
        self.assertEqual(new['entries'][:246], old['entries'])
        self.assertEqual(new['entries'][246:], m.contract()['additions']['objects'])
        self.assertEqual(new['counts'], {'named_current': 111, 'named_eddy': 23})
        self.assertEqual(new['proposed_current_additions'], 18)
        self.assertEqual(new['prior_projection'], old['prior_projection'])
        with self.assertRaises(ValueError):
            m.dashboard_document(new)

    def test_route_planning_adds_no_route_or_scientific_dimensions(self):
        old = catalogue()
        new = m.catalogue_document(old)
        self.assertEqual(new['remaining_current_decisions'][0], old['remaining_current_decisions'][0])
        self.assertEqual(new['candidates'], old['candidates'])
        self.assertEqual(new['counts']['accepted_current_names'], 111)
        self.assertEqual(new['counts']['currents_with_route_candidates'], 76)
        self.assertEqual(new['counts']['currents_without_route_candidates'], 35)
        self.assertEqual(new['planning_taxonomy']['strategies'][1], old['planning_taxonomy']['strategies'][1])
        self.assertTrue(all(r['candidate_ids'] == [] for r in new['remaining_current_decisions'][1:]))
        with self.assertRaises(ValueError):
            m.catalogue_document(new)

    def test_seven_owner_scenes_and_filtered_memberships_do_not_inherit_dimensions(self):
        scenes = m.scenes()
        self.assertEqual(len(scenes), 7)
        self.assertEqual(len(scenes['current:north-equatorial']['members']), 2)
        self.assertEqual(len(scenes['current:south-equatorial']['members']), 3)
        row = m.contract()['additions']['current_basin_memberships'][0]
        self.assertEqual(len(m.membership_scene([row])['members']), 1)
        self.assertIsNone(m.membership_scene([]))
        for scene in scenes.values():
            self.assertIn('unmeasured', scene['dimension_status'])
            self.assertTrue(all(r['membership_record']['measurements_inherited'] is False for r in scene['members']))

    def test_complete_apis_reject_undeclared_scientific_and_source_text_changes(self):
        for name in ['dashboard', 'atlas', 'seasons']:
            old, new = snapshot_pair(name)
            m.verify_snapshot(name, old, new)
            bad = copy.deepcopy(new)
            bad['scientific_sentinel']['widths'].append(99)
            with self.assertRaises(ValueError, msg=name):
                m.verify_snapshot(name, old, bad)
            if name != 'dashboard':
                for key, value in [('supplemental_widths', []), ('sources_json', {'other': 'changed'}),
                                   ('current_dimension_evidence_scenes', {}), ('new_undeclared_field', True)]:
                    bad = copy.deepcopy(new)
                    bad[key] = value
                    with self.assertRaises((ValueError, KeyError), msg=name + ':' + key):
                        m.verify_snapshot(name, old, bad)

    def test_empty_seasonal_plans_cannot_gain_playback_or_measurements(self):
        old, new = snapshot_pair('seasons')
        for row in m.decisions():
            plan = new['phase_plans'][row['current_id']]
            self.assertFalse(plan['can_play'])
            self.assertEqual(plan['phases'], [])
            self.assertEqual(plan['eligible_indices'], [])
            for key, value in [('can_play', True), ('phases', [{'width_id': 'fabricated'}])]:
                bad = copy.deepcopy(new)
                bad['phase_plans'][row['current_id']][key] = value
                with self.assertRaises(ValueError):
                    m.verify_snapshot('seasons', old, bad)

    def test_snapshot_rejects_missing_bundle_identity_and_wrong_api(self):
        old, new = snapshot_pair('dashboard')
        for value in [None, 'x' * 64, 'a' * 63]:
            new['bundle_sha256'] = value
            with self.assertRaises(ValueError):
                m.verify_snapshot('dashboard', old, new)
        with self.assertRaises(ValueError):
            m.verify_snapshot('other', old, new)


if __name__ == '__main__':
    unittest.main()
