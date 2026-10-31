import unittest
from unittest.mock import patch
import check_richardson_walsh_1986_velocity_parent_v1 as audit

class AuditTests(unittest.TestCase):
    def test_case_encoded_DOI_and_repository_URL_resolve_same_publication(self):
        rows=[{'id':'paper','doi':'https://doi.org/10.1029%2FJC091iC09p10537'}]
        selected,resolutions=audit.publications(rows)
        self.assertEqual(resolutions['richardson_walsh_1986']['status'],'UNIQUE_EXISTING')
        self.assertEqual(selected['richardson_walsh_1986'],rows)
        rows=[{'id':'paper','url':'https://www2.whoi.edu/staff/prichardson/wp-content/uploads/sites/75/2018/11/Richardson-Walsh-1986-jgr.pdf'}]
        self.assertEqual(audit.publications(rows)[1]['richardson_walsh_1986']['status'],'UNIQUE_EXISTING')

    def test_conflicting_and_duplicate_publications_require_reconciliation(self):
        paper=audit.PAPERS['richardson_walsh_1986']
        rows=[{'id':'bad','title':paper['title'],'doi':'10.1029/different'}]
        self.assertEqual(audit.publications(rows)[1]['richardson_walsh_1986']['status'],'CONFLICTING_METADATA')
        rows=[{'id':'a','doi':paper['doi']},{'id':'b','doi':paper['doi']}]
        self.assertEqual(audit.publications(rows)[1]['richardson_walsh_1986']['status'],'RECONCILIATION_REQUIRED')
        rows[1]['id']='a'
        with self.assertRaises(ValueError):audit.publications(rows)

    def test_local_audit_refuses_before_any_file_read(self):
        with patch.object(audit.os,'name','nt'),patch.object(audit.Path,'read_bytes',side_effect=AssertionError('No packet read')):
            with self.assertRaisesRegex(ValueError,'Exact cloud'):audit.controls()

if __name__=='__main__':unittest.main()
