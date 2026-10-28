import os
import unittest
from unittest.mock import patch
import check_eac_mean_core_parent_v1 as m

class ParentAudit(unittest.TestCase):
    def test_local_refusal_before_read(self):
        with patch.dict(os.environ,{},clear=True),patch.object(m,'read',side_effect=AssertionError('early read')):
            with self.assertRaises(ValueError):m.audit()

    def test_missing_does_not_create_publication(self):
        rows,resolutions=m.publications([])
        self.assertEqual(rows['kerry_2020'],[])
        self.assertEqual(resolutions['kerry_2020']['status'],'MISSING')

    def test_normalized_doi_and_full_publisher_url(self):
        for row in [{'id':'existing','doi':'https://doi.org/10.1029/2019JC015227'},
                    {'id':'existing','url':'https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/2019JC015227?utm=example'}]:
            rows,resolutions=m.publications([row]);self.assertEqual(rows['kerry_2020'],[row])
            self.assertEqual(resolutions['kerry_2020']['status'],'UNIQUE_EXISTING')

    def test_exact_title_without_doi_is_detected(self):
        row={'id':'by-title','title':m.PAPERS['kerry_2020']['title'].upper().replace('Intra-annual','Intra annual')}
        rows,resolutions=m.publications([row]);self.assertEqual(rows['kerry_2020'],[row])
        self.assertEqual(resolutions['kerry_2020']['status'],'UNIQUE_EXISTING')

    def test_conflicting_doi_is_reported_for_reconciliation(self):
        row={'id':'conflict','title':m.PAPERS['kerry_2020']['title'],'doi':'10.1029/another-paper'}
        _,resolutions=m.publications([row])
        self.assertEqual(resolutions['kerry_2020']['status'],'CONFLICTING_METADATA')
        self.assertEqual(resolutions['kerry_2020']['conflicting_source_ids'],['conflict'])

    def test_two_publication_rows_do_not_become_new_identity(self):
        rows=[{'id':i,'doi':m.PAPERS['kerry_2020']['doi']} for i in ['one','two']]
        _,resolutions=m.publications(rows)
        self.assertEqual(resolutions['kerry_2020']['status'],'RECONCILIATION_REQUIRED')

    def test_duplicate_source_ids_are_invalid(self):
        with self.assertRaises(ValueError):m.publications([{'id':'same'},{'id':'same'}])

if __name__=='__main__':unittest.main()
