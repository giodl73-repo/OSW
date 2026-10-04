"""Check nominal/scenario distinctions in the state-first route inventory."""
import unittest
from build_reference_route_state_join import crossing_summary


class CrossingSummaryTests(unittest.TestCase):
    def test_semantic_exclusions_preserve_raw_contacts_for_audit(self):
        row={'nominal_atlas_state_crossings':['MEDI'],'scenario_count':1,
             'scenarios':[{'atlas_state_crossings':['MEDI','REDS']}],
             'state_semantic_exclusions':[{'state_code':'MEDI','reason':'Separate Black Sea basin'},{'state_code':'REDS','reason':'Separate Black Sea basin'}]}
        self.assertEqual(crossing_summary(row,{'MEDI','REDS'}),{})
        self.assertEqual(set(crossing_summary(row,{'MEDI','REDS'},False)),{'MEDI','REDS'})
        row['state_semantic_exclusions'][0]['reason']=''
        with self.assertRaises(ValueError):crossing_summary(row,{'MEDI','REDS'})
    def test_nominal_and_scenario_only_crossings_remain_distinct(self):
        record = {'nominal_atlas_state_crossings': ['A'], 'scenario_count': 3,
                  'scenarios': [{'atlas_state_crossings': ['A']},
                                {'atlas_state_crossings': ['A', 'B']},
                                {'atlas_state_crossings': ['A']}]}
        result = crossing_summary(record, {'A', 'B', 'C'})
        self.assertEqual(set(result), {'A', 'B'})
        self.assertTrue(result['A']['crosses_in_all_declared_scenarios'])
        self.assertFalse(result['B']['nominal_crossing'])
        self.assertEqual(result['B']['crossing_scenario_count'], 1)
        self.assertEqual(result['B']['scenario_count'], 3)

    def test_invalid_or_incomplete_crossings_are_rejected(self):
        records = [
            {'nominal_atlas_state_crossings': ['A'], 'scenario_count': 1, 'scenarios': []},
            {'nominal_atlas_state_crossings': ['A'], 'scenario_count': 1, 'scenarios': [{'atlas_state_crossings': ['B']}]},
            {'nominal_atlas_state_crossings': ['A'], 'scenario_count': 1, 'scenarios': [{'atlas_state_crossings': ['A', 'X']}]},
            {'nominal_atlas_state_crossings': ['A'], 'scenario_count': 1, 'scenarios': [{'atlas_state_crossings': ['A', 'A']}]},
        ]
        for record in records:
            with self.subTest(record=record), self.assertRaises(ValueError):
                crossing_summary(record, {'A', 'B'})


if __name__ == '__main__':
    unittest.main()
