import unittest
from unittest.mock import patch
import check_pacific_sec_gourdeau_2008_parent_v1 as audit

class AuditTests(unittest.TestCase):
    def test_case_encoded_DOI_and_repository_URL_resolve_same_publication(self):
        rows=[{'id':'paper','doi':'https://doi.org/10.1175%2F2007JPO3780.1'}]
        selected,resolutions=audit.publications(rows)
        self.assertEqual(resolutions['gourdeau_2008']['status'],'UNIQUE_EXISTING')
        self.assertEqual(selected['gourdeau_2008'],rows)
        rows=[{'id':'paper','url':'https://faculty.washington.edu/kessler/abstracts/gourdeau_etal_jpo08_glider.pdf'}]
        self.assertEqual(audit.publications(rows)[1]['gourdeau_2008']['status'],'UNIQUE_EXISTING')

    def test_conflicting_and_duplicate_publications_require_reconciliation(self):
        paper=audit.PAPERS['gourdeau_2008']
        rows=[{'id':'bad','title':paper['title'],'doi':'10.1029/different'}]
        self.assertEqual(audit.publications(rows)[1]['gourdeau_2008']['status'],'CONFLICTING_METADATA')
        rows=[{'id':'a','doi':paper['doi']},{'id':'b','doi':paper['doi']}]
        self.assertEqual(audit.publications(rows)[1]['gourdeau_2008']['status'],'RECONCILIATION_REQUIRED')
        rows[1]['id']='a'
        with self.assertRaises(ValueError):audit.publications(rows)

    def test_local_audit_refuses_before_any_file_read(self):
        with patch.object(audit.os,'name','nt'),patch.object(audit.Path,'read_bytes',side_effect=AssertionError('No packet read')):
            with self.assertRaisesRegex(ValueError,'Exact cloud'):audit.controls()

if __name__=='__main__':unittest.main()
