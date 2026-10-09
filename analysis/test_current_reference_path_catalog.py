"""Verify envelope ordering, including ties and excluded study reaches."""
import unittest
import tempfile
import json
import hashlib
from pathlib import Path
from build_current_reference_path_catalog import ordering_sensitivity, validate_generator, validate_strategies, validate_parent_scope
from build_current_reference_path_catalog import validate_source_receipt


def row(name, low, high, group='osw_approximate_reference_routes'):
    return {'id': name, 'scenario_range_km': [low, high], 'comparison_group': group}


class EnvelopeOrderingTests(unittest.TestCase):
    def test_retained_original_receipts_reject_changed_bytes_and_wrong_owner(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'original.pdf').write_bytes(b'pinned original')
            digest=lambda p:hashlib.sha256((root/p).read_bytes()).hexdigest()
            (root/'acquisition.json').write_text(json.dumps({'sha256':digest('original.pdf'),'bytes':15}))
            audit={'current_id':'sample','source_document_file':'original.pdf',
                   'source_document_sha256':digest('original.pdf'),
                   'acquisition_file':'acquisition.json','acquisition_sha256':digest('acquisition.json')}
            (root/'audit.json').write_text(json.dumps(audit))
            receipt={**{k:v for k,v in audit.items() if k!='current_id'},'audit_file':'audit.json','audit_sha256':digest('audit.json')}
            record={'current_id':'sample','source_review_receipt':receipt}
            self.assertEqual(len(validate_source_receipt(record,root)),3)
            with self.assertRaisesRegex(ValueError,'ownership'):
                validate_source_receipt({**record,'current_id':'other'},root)
            (root/'original.pdf').write_bytes(b'changed original')
            with self.assertRaisesRegex(ValueError,'Changed'):
                validate_source_receipt(record,root)
            self.assertEqual(validate_source_receipt({'source_review_receipt':{'retrieved_bytes':100}},root),{})

    def test_parent_scope_requires_ledger_relation_and_note(self):
        ledger={'segment':{'part_of_current_id':'parent'},'parent':{},'other':{}}
        record={'current_id':'segment','parent_current_id':'parent','parent_scope_note':'Overlapping segment, not additive.'}
        validate_parent_scope(record,ledger)
        validate_parent_scope({'current_id':'parent'},ledger)
        for value in [{**record,'parent_current_id':'other'},{**record,'parent_current_id':'missing'},{**record,'parent_current_id':'segment'},{**record,'parent_scope_note':''}]:
            with self.subTest(value=value),self.assertRaises(ValueError):validate_parent_scope(value,ledger)

    def test_planning_inventory_requires_complete_unique_supported_assignments(self):
        document = {'basis_sha256': 'basis', 'strategies': [{'id': 'regional'}], 'assignments': [{'current_id': 'a', 'strategy_id': 'regional'}, {'current_id': 'b', 'strategy_id': 'regional'}]}
        self.assertEqual(validate_strategies(document, {'a', 'b'}, 'basis'), {'a': 'regional', 'b': 'regional'})
        invalid = [
            {**document, 'basis_sha256': 'old'},
            {**document, 'assignments': document['assignments'][:1]},
            {**document, 'assignments': document['assignments'] + [document['assignments'][0]]},
            {**document, 'assignments': [{'current_id': 'a', 'strategy_id': 'regional'}, {'current_id': 'extra', 'strategy_id': 'regional'}]},
            {**document, 'assignments': [{'current_id': 'a', 'strategy_id': 'undefined'}, {'current_id': 'b', 'strategy_id': 'regional'}]},
            {**document, 'strategies': [{'id': 'regional'}, {'id': 'regional'}]},
            *[{**document, 'assignments': [{**document['assignments'][0], 'next_action': value}, document['assignments'][1]]} for value in [None, '', {'instruction': 'invalid'}]],
        ]
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_strategies(value, {'a', 'b'}, 'basis')

    def test_missing_and_changed_generator_fingerprints_are_rejected(self):
        current = {'generator_file': 'analysis/build_current_reference_path_candidate.py', 'generator_sha256': 'current'}
        validate_generator(current, 'current')
        for record in [{}, {**current, 'generator_sha256': 'old'}, {**current, 'generator_file': 'other.py'}]:
            with self.subTest(record=record), self.assertRaisesRegex(ValueError, 'generator fingerprint'):
                validate_generator(record, 'current')

    def test_disjoint_envelopes_have_fixed_positions(self):
        result = ordering_sensitivity([row('short', 100, 200), row('long', 500, 600)])
        self.assertEqual(result['long']['envelope_position_bounds'], [1, 1])
        self.assertEqual(result['short']['envelope_position_bounds'], [2, 2])
        self.assertEqual(result['long']['overlapping_candidate_ids'], [])

    def test_touching_nested_and_equal_envelopes(self):
        result = ordering_sensitivity([row('a', 100, 300), row('b', 300, 400), row('c', 150, 200), row('d', 100, 300)])
        self.assertEqual(result['a']['envelope_position_bounds'], [1, 4])
        self.assertEqual(set(result['a']['overlapping_candidate_ids']), {'b', 'c', 'd'})
        self.assertEqual(result['c']['envelope_position_bounds'], [2, 4])

    def test_studied_reach_is_excluded(self):
        result = ordering_sensitivity([row('route', 100, 200), row('reach', 50, 1000, 'osw_studied_reach_routes')])
        self.assertEqual(set(result), {'route'})
        self.assertEqual(result['route']['envelope_position_bounds'], [1, 1])


if __name__ == '__main__':
    unittest.main()
