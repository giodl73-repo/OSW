import copy
import unittest
import reconcile_width_record_coverage_v1 as coverage

class WidthCoverageTests(unittest.TestCase):
    def test_all190_retained_source_rows_have93_owners_and111_decisions(self):
        result=coverage.build()
        self.assertEqual(result['counts']['owners_with_admitted_scoped_width_records'],93)
        self.assertEqual(sum(len(g['rows']) for g in result['source_width_groups']),190)
        self.assertEqual(result['capability_only_current_ids'],['gulf-stream-system'])
        gulf=next(r for r in result['current_decisions'] if r['current_id']=='gulf-stream-system')
        self.assertEqual(gulf['measurement_ids'],[])
        self.assertEqual(gulf['width_decision'],'derived_width_candidate_requires_review')

    def test_candidate_capability_does_not_create_a_measurement_or_cover_family(self):
        result=coverage.reconcile([{'id':'width:a','current_id':'a'}],
            [{'current_id':'a'},{'current_id':'family','width_decision':'derived_width_candidate_requires_review'}],
            [{'id':'current:family','type':'named_current','capabilities':{'scoped_width':1}}])
        self.assertEqual(result['counts']['owners_with_admitted_scoped_width_records'],1)
        self.assertEqual(result['counts']['owners_with_broader_dashboard_width_capability'],2)
        self.assertEqual(result['current_decisions'][1]['measurement_ids'],[])

    def test_duplicate_row_or_unknown_owner_refused(self):
        row={'id':'width:a','current_id':'a'}
        for records in [[row,copy.deepcopy(row)],[{**row,'current_id':'unknown'}]]:
            with self.assertRaises(ValueError):coverage.reconcile(records,[{'current_id':'a'}],[])

if __name__=='__main__':unittest.main()
