"""Small identity and pre-read refusal checks; no installed packet access."""
import os
import unittest
from unittest.mock import patch
import check_wicc_reference_parent_v1 as audit


class WiccParent(unittest.TestCase):
    def test_local_call_refused_before_any_read(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(audit, 'read', side_effect=AssertionError('early read')):
            with self.assertRaises(ValueError):
                audit.audit()

    def test_missing_publication_does_not_create_one(self):
        selected, resolutions = audit.publications([])
        self.assertEqual(selected['shetye_1991'], [])
        self.assertEqual(resolutions['shetye_1991']['status'], 'MISSING')

    def test_normalized_doi_reuses_existing_identity(self):
        row = {'id': 'existing', 'doi': 'https://doi.org/10.1016/0198-0149(91)90087-V'}
        selected, resolutions = audit.publications([row])
        self.assertEqual(selected['shetye_1991'], [row])
        self.assertEqual(resolutions['shetye_1991']['status'], 'UNIQUE_EXISTING')

    def test_duplicate_publications_require_reconciliation(self):
        rows = [{'id': i, 'doi': '10.1029/2008JC004874'} for i in ['one', 'two']]
        _, resolutions = audit.publications(rows)
        self.assertEqual(resolutions['shetye_2008']['status'], 'RECONCILIATION_REQUIRED')

    def test_conflicting_identifier_refused(self):
        row = {'id': 'bad', 'doi': '10.1029/other', 'url': audit.PAPERS['shetye_2008'][1]}
        with self.assertRaises(ValueError):
            audit.publications([row])

    def test_duplicate_source_id_refused(self):
        with self.assertRaises(ValueError):
            audit.publications([{'id': 'one'}, {'id': 'one'}])


if __name__ == '__main__':
    unittest.main()
