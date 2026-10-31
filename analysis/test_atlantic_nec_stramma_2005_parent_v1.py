import unittest
from unittest.mock import patch
import check_atlantic_nec_stramma_2005_parent_v1 as audit

class AuditTests(unittest.TestCase):
    def test_case_encoded_DOI_and_repository_URL_resolve_same_publication(self):
        rows=[{'id':'paper','doi':'https://doi.org/10.1029%2F2005JC002939'}]
        selected,resolutions=audit.publications(rows)
        self.assertEqual(resolutions['stramma_2005']['status'],'UNIQUE_EXISTING')
        self.assertEqual(selected['stramma_2005'],rows)
        rows=[{'id':'paper','url':'https://oceanrep.geomar.de/5767/1/2005JC002939.pdf'}]
        self.assertEqual(audit.publications(rows)[1]['stramma_2005']['status'],'UNIQUE_EXISTING')

    def test_conflicting_and_duplicate_publications_require_reconciliation(self):
        paper=audit.PAPERS['stramma_2005']
        rows=[{'id':'bad','title':paper['title'],'doi':'10.1029/different'}]
        self.assertEqual(audit.publications(rows)[1]['stramma_2005']['status'],'CONFLICTING_METADATA')
        rows=[{'id':'a','doi':paper['doi']},{'id':'b','doi':paper['doi']}]
        self.assertEqual(audit.publications(rows)[1]['stramma_2005']['status'],'RECONCILIATION_REQUIRED')
        rows[1]['id']='a'
        with self.assertRaises(ValueError):audit.publications(rows)

    def test_local_audit_refuses_before_any_file_read(self):
        with patch.object(audit.os,'name','nt'),patch.object(audit.Path,'read_bytes',side_effect=AssertionError('No packet read')):
            with self.assertRaisesRegex(ValueError,'Exact cloud'):audit.controls()

if __name__=='__main__':unittest.main()
