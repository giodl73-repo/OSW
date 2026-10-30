import copy
import json
import unittest
from unittest.mock import patch
import check_current_core_gap_followup_parent_v1 as audit


class FollowupAuditTests(unittest.TestCase):
    def test_primary_DOI_normalizes_url_case_encoding(self):
        rows=[{'id':'peters','doi':'https://doi.org/10.1175%2FJPO2679.1'},
              {'id':'nilsen','doi':'doi:10.1175/JPO-D-15-0058.1'}]
        selected,resolved=audit.publications(rows)
        self.assertEqual(selected['peters_2005'],rows[:1])
        self.assertEqual(resolved['nilsen_2016']['status'],'UNIQUE_EXISTING')
        self.assertEqual(audit.doi(None),'')

    def test_no_DOI_report_does_not_match_other_no_DOI_sources(self):
        rows=[{'id':'unrelated','title':'Another report','doi':None}]
        self.assertEqual(audit.publications(rows)[1]['asclme_2008_51pp']['status'],'MISSING')

    def test_report_title_alone_requires_version_review(self):
        paper=audit.PAPERS['asclme_2008_51pp']
        rows=[{'id':'report','title':paper['title']}]
        self.assertEqual(audit.publications(rows)[1]['asclme_2008_51pp']['status'],'VERSION_REVIEW_REQUIRED')
        rows[0]['url']=paper['urls'][0].replace(' ','%20')+'?download=1'
        self.assertEqual(audit.publications(rows)[1]['asclme_2008_51pp']['status'],'UNIQUE_EXISTING')
        rows[0]['url']='https://archive.iwlearn.net/asclme.org/DraftFinalReportMASCARENE_PLATEAU.pdf'
        self.assertEqual(audit.publications(rows)[1]['asclme_2008_51pp']['status'],'VERSION_REVIEW_REQUIRED')

    def test_conflicts_and_duplicate_sources_require_review(self):
        paper=audit.PAPERS['nilsen_2016']
        rows=[{'id':'a','title':paper['title'],'doi':'10.1234/different'}]
        self.assertEqual(audit.publications(rows)[1]['nilsen_2016']['status'],'CONFLICTING_METADATA')
        rows=[{'id':i,'doi':paper['doi']} for i in ['a','b']]
        self.assertEqual(audit.publications(rows)[1]['nilsen_2016']['status'],'RECONCILIATION_REQUIRED')
        rows[1]['id']='a'
        with self.assertRaises(ValueError):audit.publications(rows)

    def test_full_named_feature_in_aliases_but_not_ambiguous_acronym(self):
        self.assertTrue(audit.named_candidate({'aliases':['Spitsbergen Trough Current (STC)']}))
        self.assertTrue(audit.named_candidate({'label':'Spitzbergen Trough Current'}))
        self.assertTrue(audit.named_candidate({'id':audit.CANDIDATE_OWNER}))
        self.assertFalse(audit.named_candidate({'aliases':['STC'],'label':'Subtropical Countercurrent'}))

    def test_large_field_projection_has_exact_hash_and_does_not_mutate(self):
        row={'id':'a','source_json':'x'*17000,'length_km':120}
        before=copy.deepcopy(row);result=audit.projection(row)
        self.assertEqual(row,before)
        self.assertEqual(result['record_projection'],{'id':'a','length_km':120})
        omitted=result['omitted_fields']['source_json']
        self.assertEqual(omitted['canonical_sha256'],audit.sha(audit.canonical(row['source_json'])))
        self.assertEqual(result['canonical_record_sha256'],audit.sha(audit.canonical(row)))
        self.assertEqual(audit.projection({'id':'small'}),{'id':'small'})

    def test_local_audit_refuses_before_file_or_network_reads(self):
        with patch.object(audit.os,'name','nt'),patch.object(audit.Path,'read_bytes',side_effect=AssertionError('No packet read')),patch.object(audit.subprocess,'check_output',side_effect=AssertionError('No network')):
            with self.assertRaisesRegex(ValueError,'Exact cloud'):audit.controls()

    def test_workflow_selector_and_output_match_driver(self):
        workflow=(audit.ROOT/audit.WORKFLOW).read_text(encoding='utf8')
        self.assertEqual(workflow.count(audit.REQUEST),3)
        self.assertIn('test_current_core_gap_followup_parent_v1.py',workflow)
        self.assertIn('analysis/check_current_core_gap_followup_parent_v1.py',workflow)
        self.assertIn(str(audit.OUT.relative_to(audit.ROOT)).replace('\\','/')+'/*.json',workflow)
        self.assertIn('group: osw-current-gap-delivery',workflow)
        self.assertNotIn('test_current_core_gap_followup_widths',workflow)


if __name__=='__main__':unittest.main()
