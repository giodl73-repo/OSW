"""Small scientific-scope and atomic-append checks; no packet or index opened."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import loop_published_metrics_query_v1 as query


class PublishedContourEvents(unittest.TestCase):
    def setUp(self): self.contract = query.build_contract()

    def base(self):
        return {'objects': [
                    {'id': query.TARGET, 'type': 'named_current', 'source_ids': ['source:prior'],
                     'linked_source_count': 1, 'capabilities': {'scoped_width': 3, 'width_samples': 17},
                     'evidence_links': [{'label': 'Existing source', 'url': 'existing.html'}],
                     'section_fingerprints': {'physical_width': 'keep-this'}, 'fingerprint': 'old',
                     'published_length_km': None, 'width_ids': ['old-width'],
                     'width_sample_ids': ['old-sample'], 'latest_observation_date': '2026-09-25',
                     'geometry_ids': ['old-geometry']},
                    {'id': 'current:other', 'type': 'named_current', 'fingerprint': 'other-stays'}],
                'entities': [{'id': query.TARGET, 'type': 'named_current'}, {'id': 'current:other', 'type': 'named_current'}],
                'sources': [{'id': 'source:prior', 'kind': 'external', 'title': 'Earlier evidence'}],
                'measurements': [{'id': 'old-measurement', 'value': 2500}],
                'length_assessments': [{'id': 'old-length', 'current_id': 'loop', 'rank_eligible': False}],
                'width_measurements': [{'id': 'old-width', 'current_id': 'loop', 'width_km': 80}],
                'width_samples': [{'id': 'old-sample', 'entity_id': query.TARGET, 'value_km': 31}],
                'geometries': [{'id': 'old-geometry', 'coordinates': [[-85, 22], [-82, 24]]}],
                'named_eddy_source_observations': [{'id': 'prior-named-eddy', 'name': 'Do not crosswalk'}]}

    def refused(self, data, document=None):
        before = copy.deepcopy(data)
        with self.assertRaises(ValueError): query.append(data, document or self.contract)
        self.assertEqual(query.encoded(data), query.encoded(before))

    def test_contour_mean_and_spread_keep_their_source_semantics(self):
        rows = self.contract['collections'][query.SUMMARIES]
        self.assertEqual([(r['mean_km'], r['temporal_standard_deviation_km']) for r in rows], [(1449, 487), (1495, 466)])
        for row in rows:
            self.assertFalse(row['statistical_spread_is_uncertainty'])
            self.assertIsNone(row['uncertainty_km'])
            self.assertIsNone(row['length_of_temporal_mean_path_km'])
            self.assertEqual(row['gate_labels'], ['Yucatan Channel', 'Florida Straits'])
            self.assertEqual((row['reported_period_start_year'], row['reported_period_end_year']), (1993, 2021))

    def test_twelve_days_are_a_subset_with_no_name_or_spatial_inference(self):
        rows = self.contract['collections'][query.EVENTS]
        self.assertEqual(len(rows), 12)
        november = [r['date'] for r in rows if r['date'].startswith('2017-11')]
        self.assertEqual(november, ['2017-11-10', '2017-11-21'])
        for row in rows:
            self.assertEqual(row['entity_id'], query.TARGET)
            self.assertFalse(row['is_initial_detachment_date'])
            self.assertFalse(row['is_ring_birth_date'])
            self.assertFalse(row['complete_full_period_event_inventory'])
            self.assertEqual(row['listed_subset_count'], 12)
            self.assertEqual(row['reported_full_period_event_count'], 48)
            for key in ['eddy_id', 'eddy_name', 'geometry', 'timezone', 'clock_time',
                        'latitude_degrees_north', 'longitude_degrees_east']:
                self.assertIsNone(row[key])
            self.assertNotIn('timeline_file', row)

    def test_success_preserves_all_prior_science_and_other_objects(self):
        data = self.base(); before = copy.deepcopy(data)
        query.append(data, self.contract)
        for name in set(before) - {'objects', 'sources'}: self.assertEqual(data[name], before[name])
        self.assertEqual(data['objects'][1], before['objects'][1])
        old, new = before['objects'][0], data['objects'][0]
        changed = {k for k in set(old) | set(new) if old.get(k) != new.get(k)}
        self.assertEqual(changed, {'source_ids', 'linked_source_count', 'capabilities', 'evidence_links',
                                   'section_fingerprints', 'fingerprint', 'reported_contour_length_summary_ids',
                                   'reported_separation_event_ids'})
        self.assertEqual(new['latest_observation_date'], '2026-09-25')
        self.assertEqual(new['capabilities']['scoped_width'], 3)
        self.assertEqual(new['capabilities']['width_samples'], 17)
        self.assertEqual(new['capabilities']['reported_contour_length_summaries'], 2)
        self.assertEqual(new['capabilities']['reported_separation_events'], 12)
        self.assertEqual(new['section_fingerprints']['physical_width'], 'keep-this')
        self.assertEqual(data['sources'][0], before['sources'][0])

    def test_duplicate_or_partial_application_is_atomic_refusal(self):
        data = self.base(); query.append(data, self.contract); self.refused(data)
        for name in query.OWNER_FIELDS:
            data = self.base(); data[name] = [copy.deepcopy(self.contract['collections'][name][0])]
            self.refused(data)

    def test_changed_quantities_dates_ownership_or_promotions_refused(self):
        mutations = [
            lambda d: d['collections'][query.SUMMARIES][0].update(mean_km=1495),
            lambda d: d['collections'][query.SUMMARIES][0].update(uncertainty_km=487),
            lambda d: d['collections'][query.SUMMARIES][0].update(annual_maximum_km=1936),
            lambda d: d['collections'][query.EVENTS][0].update(date='2013-05-29'),
            lambda d: d['collections'][query.EVENTS][0].update(eddy_name='Kraken'),
            lambda d: d['collections'][query.EVENTS][0].update(entity_id='eddy:kraken'),
            lambda d: d['collections'][query.EVENTS][0].update(source_id='source:prior'),
            lambda d: d['collections'][query.EVENTS][0].update(complete_full_period_event_inventory=True),
            lambda d: d['collections'][query.EVENTS][0].update(clock_time='00:00:00', timezone='UTC'),
            lambda d: d['collections'][query.EVENTS][0].update(timeline_file='invented-track.json'),
            lambda d: d['collections'][query.EVENTS][0].update(physical_state_join_eligible=True),
            lambda d: d['collections'][query.SUMMARIES][0].update(rank_eligible=True),
        ]
        for change in mutations:
            with self.subTest(change=change):
                document = copy.deepcopy(self.contract); change(document); self.refused(self.base(), document)

    def test_boolean_numeric_and_null_type_changes_are_not_equal_contracts(self):
        for key, value in [('rank_eligible', 0), ('independent_observation_count', False), ('geometry', False)]:
            with self.subTest(field=key):
                doc = copy.deepcopy(self.contract); doc['collections'][query.EVENTS][0][key] = value
                self.refused(self.base(), doc)

    def test_missing_wrong_or_duplicate_owner_is_not_identity_admission(self):
        for name in ['objects', 'entities']:
            for mode in ['missing', 'wrong-type', 'duplicate']:
                data = self.base()
                if mode == 'missing': data[name] = data[name][1:]
                elif mode == 'wrong-type': data[name][0]['type'] = 'named_eddy'
                else: data[name].append(copy.deepcopy(data[name][0]))
                with self.subTest(collection=name, mode=mode): self.refused(data)

    def test_invalid_prior_source_counts_refs_and_containers_not_repaired(self):
        for mode in ['unresolved', 'incoming-source', 'duplicate-source', 'wrong-count', 'bool-count', 'bad-links']:
            data = self.base(); owner = data['objects'][0]
            if mode == 'unresolved': owner['source_ids'] = ['source:missing']
            elif mode == 'incoming-source': owner['source_ids'] = [query.PAPER]
            elif mode == 'duplicate-source': owner['source_ids'] *= 2; owner['linked_source_count'] = 2
            elif mode == 'wrong-count': owner['linked_source_count'] = 9
            elif mode == 'bool-count': owner['linked_source_count'] = True
            else: owner['evidence_links'] = {}
            with self.subTest(mode=mode): self.refused(data)

    def test_existing_source_is_reused_only_when_exact(self):
        data = self.base(); paper = copy.deepcopy(self.contract['collections']['sources'][0])
        data['sources'].append(paper); data['objects'][0]['source_ids'].append(query.PAPER)
        data['objects'][0]['linked_source_count'] = 2
        query.append(data, self.contract)
        self.assertEqual(sum(r['id'] == query.PAPER for r in data['sources']), 1)
        self.assertEqual(data['sources'][1], paper)
        changed = self.base(); changed['sources'].append({**paper, 'publication_year': 2026})
        self.refused(changed)

    def test_publication_doi_or_url_alias_needs_reconciliation(self):
        for extra in [{'doi': 'https://doi.org/10.3389/FMARS.2023.1156159'},
                      {'url': 'https://www.frontiersin.org/articles/10.3389/fmars.2023.1156159/full'}]:
            data = self.base(); data['sources'].append({'id': 'source:older-alias', **extra})
            with self.subTest(alias=extra): self.refused(data)

    def test_prior_owned_records_are_preserved_and_counted(self):
        for name, (field, capability) in query.OWNER_FIELDS.items():
            data = self.base(); old = {'id': 'prior-row', 'entity_id': query.TARGET,
                 'source_ids': ['source:prior'], 'source_id': 'source:prior', 'method_source_id': 'source:prior'}
            data[name] = [copy.deepcopy(old)]; data['objects'][0][field] = ['prior-row']
            data['objects'][0]['capabilities'][capability] = 1
            query.append(data, self.contract)
            self.assertEqual(data[name][0], old)
            self.assertEqual(data['objects'][0]['capabilities'][capability], 1 + len(self.contract['collections'][name]))

    def test_prior_orphan_wrong_owner_bad_provenance_and_counts_refused(self):
        for name, (field, capability) in query.OWNER_FIELDS.items():
            for mode in ['orphan', 'missing-row', 'wrong-owner', 'bad-source', 'wrong-count', 'missing-count', 'bool-count']:
                data = self.base(); old = {'id': 'prior-row', 'entity_id': query.TARGET,
                     'source_ids': ['source:prior'], 'source_id': 'source:prior', 'method_source_id': 'source:prior'}
                data[name] = [old]; owner = data['objects'][0]; owner[field] = ['prior-row']; owner['capabilities'][capability] = 1
                if mode == 'orphan': owner[field] = []; owner['capabilities'][capability] = 0
                elif mode == 'missing-row': data[name] = []
                elif mode == 'wrong-owner': old['entity_id'] = 'current:other'
                elif mode == 'bad-source': old['source_ids'] = ['source:missing']
                elif mode == 'wrong-count': owner['capabilities'][capability] = 17
                elif mode == 'missing-count': del owner['capabilities'][capability]
                else: owner['capabilities'][capability] = True
                with self.subTest(collection=name, mode=mode): self.refused(data)

    def test_duplicate_existing_ids_and_changed_method_source_are_refused(self):
        for name in ['objects', 'entities', 'sources']:
            data = self.base(); data[name].append(copy.deepcopy(data[name][0])); self.refused(data)
        data = self.base(); data['sources'].append({'id': query.METHOD, 'kind': 'external'})
        self.refused(data)

    def test_source_pointer_exactly_selects_each_projected_record(self):
        source = json.loads((query.ROOT / query.FACTS).read_bytes())
        for name in query.OWNER_FIELDS:
            for row in self.contract['collections'][name]:
                key, index = row['source_pointer'].strip('/').split('/')
                original = source[key][int(index)]
                self.assertEqual(original['id'], row['id'])
                for field in original: self.assertEqual(original[field], row[field])

    def test_month_example_uses_supported_text_filter_and_selects_both_events(self):
        request = self.contract['example_queries'][2]
        self.assertEqual(request['filters'], [{'field': 'date', 'op': 'contains', 'value': '2017-11'}])
        rows = self.contract['collections'][query.EVENTS]
        self.assertEqual([r['date'] for r in rows if '2017-11' in r['date']], ['2017-11-10', '2017-11-21'])

    def test_actual_shipped_ui_formatters_present_all_fourteen_records(self):
        raw = subprocess.check_output(['node', 'analysis/check_loop_published_query_formatters_v1.mjs', '--stdin'],
                                      input=query.encoded(self.contract), cwd=query.ROOT, timeout=15)
        result = json.loads(raw)
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['shipped_formatter_records_checked'], 14)
        self.assertFalse(result['browser_or_dom_started'])
        self.assertFalse(result['wasm_loaded'])

    def test_changed_preparation_or_input_bytes_refused_before_projection(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            preparation = root / query.PREPARATION; preparation.parent.mkdir(parents=True)
            preparation.write_bytes(b'{}')
            with self.assertRaisesRegex(ValueError, 'source preparation'): query.build_contract(root)
            preparation.write_bytes((query.ROOT / query.PREPARATION).read_bytes())
            document = json.loads(preparation.read_bytes())
            for path in document['input_sha256']:
                target = root / path; target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((query.ROOT / path).read_bytes())
            (root / query.FACTS).write_bytes((root / query.FACTS).read_bytes() + b' ')
            with self.assertRaisesRegex(ValueError, 'source input'): query.build_contract(root)


if __name__ == '__main__': unittest.main()
