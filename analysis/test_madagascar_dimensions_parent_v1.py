import os
import unittest
from unittest.mock import patch
import check_madagascar_dimensions_parent_v1 as m

class ParentAudit(unittest.TestCase):
    def test_local_refusal_before_read(self):
        with patch.dict(os.environ,{},clear=True),patch.object(m,'read',side_effect=AssertionError('early read')):
            with self.assertRaises(ValueError):m.audit()

    def test_missing_does_not_create_publication(self):
        rows,resolutions=m.publications([])
        self.assertEqual(rows['ponsoni_2016'],[])
        self.assertEqual(resolutions['ponsoni_2016']['status'],'MISSING')

    def test_normalized_doi_and_full_publisher_url(self):
        for row in [{'id':'existing','doi':'https://doi.org/10.1175/JPO-D-15-0154.1'},
                    {'id':'existing','url':'https://doi.org/10.1175/JPO-D-15-0154.1?utm=example'}]:
            rows,resolutions=m.publications([row]);self.assertEqual(rows['ponsoni_2016'],[row])
            self.assertEqual(resolutions['ponsoni_2016']['status'],'UNIQUE_EXISTING')

    def test_exact_title_without_doi_is_detected(self):
        row={'id':'by-title','title':m.PAPERS['ponsoni_2016']['title'].upper().replace('Intra-annual','Intra annual')}
        rows,resolutions=m.publications([row]);self.assertEqual(rows['ponsoni_2016'],[row])
        self.assertEqual(resolutions['ponsoni_2016']['status'],'UNIQUE_EXISTING')

    def test_conflicting_doi_is_reported_for_reconciliation(self):
        row={'id':'conflict','title':m.PAPERS['ponsoni_2016']['title'],'doi':'10.1029/another-paper'}
        _,resolutions=m.publications([row])
        self.assertEqual(resolutions['ponsoni_2016']['status'],'CONFLICTING_METADATA')
        self.assertEqual(resolutions['ponsoni_2016']['conflicting_source_ids'],['conflict'])

    def test_two_publication_rows_do_not_become_new_identity(self):
        rows=[{'id':i,'doi':m.PAPERS['ponsoni_2016']['doi']} for i in ['one','two']]
        _,resolutions=m.publications(rows)
        self.assertEqual(resolutions['ponsoni_2016']['status'],'RECONCILIATION_REQUIRED')

    def test_duplicate_source_ids_are_invalid(self):
        with self.assertRaises(ValueError):m.publications([{'id':'same'},{'id':'same'}])

if __name__=='__main__':unittest.main()
