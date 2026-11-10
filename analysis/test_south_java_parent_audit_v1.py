"""Small publication-identity and pre-read environment refusal checks."""
import copy
import os
import unittest
from unittest.mock import patch

import check_south_java_parent_audit_v1 as audit


class ParentAudit(unittest.TestCase):
    def paper(self):
        row = copy.deepcopy(audit.PAPERS['iskandar_2006'])
        return {key: row[key] for key in ['id', 'doi', 'url']}

    def test_local_execution_refused_before_any_source_or_packet_read(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(audit, 'read', side_effect=AssertionError('early read')):
            with self.assertRaises(ValueError):
                audit.audit()

    def test_existing_normalized_doi_identity_reused(self):
        paper = self.paper()
        paper['doi'] = 'https://doi.org/10.1029/2006JC003486'
        self.assertEqual(audit.publication([paper], 'iskandar_2006'), paper)

    def test_duplicate_doi_requires_reconciliation(self):
        paper = self.paper()
        duplicate = {**paper, 'id': 'source:duplicate-paper'}
        with self.assertRaises(ValueError):
            audit.publication([paper, duplicate], 'iskandar_2006')

    def test_incidental_title_mention_does_not_duplicate_publication(self):
        paper = self.paper()
        method = {'id': 'source:method', 'title': 'Method citing10.1029/2006JC003486', 'url': '../plans/method.md'}
        self.assertEqual(audit.publication([paper, method], 'iskandar_2006'), paper)

    def test_conflicting_doi_and_matching_url_refused(self):
        paper = self.paper()
        paper['doi'] = '10.1029/different-paper'
        with self.assertRaises(ValueError):
            audit.publication([paper], 'iskandar_2006')

    def test_duplicate_source_ids_refused(self):
        paper = self.paper()
        with self.assertRaises(ValueError):
            audit.publication([paper, paper], 'iskandar_2006')


if __name__ == '__main__':
    unittest.main()
