"""Exercise admission boundaries against synthetic metadata, never installed packets."""
import unittest
from unittest.mock import patch
import audit_dimoune_2023_width_parent_v1 as audit

class ParentAuditTests(unittest.TestCase):
    def setUp(self):
        self.prepared=audit.read(audit.PREPARED)
        self.bundle={'collections':{'sources':[{'id':'source:registered','doi':self.prepared['doi']}],
            'objects':[{'id':v} for v in audit.OWNERS],'entities':[{'id':v} for v in audit.OWNERS],
            'widths':[{'id':r['matched_existing_inventory_record_id'],'entity_id':r['candidate_entity_id']}
                      for r in self.prepared['records'] if r['matched_existing_inventory_record_id']]}}

    def test_duplicate_partition_and_unplaced_surface_flow(self):
        result=audit.summarize(self.bundle,self.prepared)
        self.assertEqual(len(result['existing_duplicate_rows']),5)
        self.assertEqual(len(result['additional_candidates']),6)
        self.assertTrue(all(r['candidate_entity_id'] is None for r in result['unplaced_surface_current_rows']))
        self.assertFalse(result['admission_performed'])

    def test_missing_duplicate_rejected(self):
        self.bundle['collections']['widths'].pop()
        with self.assertRaisesRegex(ValueError,'Known duplicate missing'):audit.summarize(self.bundle,self.prepared)

    def test_missing_publication_is_reported_without_admission(self):
        self.bundle['collections']['sources']=[{'id':'source:unrelated'}]
        result=audit.summarize(self.bundle,self.prepared)
        self.assertEqual(result['publication_resolution'],'MISSING')
        self.assertFalse(result['admission_performed'])

    def test_candidate_id_collision_rejected(self):
        self.bundle['collections']['widths'].append({'id':self.prepared['records'][2]['id']})
        with self.assertRaisesRegex(ValueError,'already installed'):audit.summarize(self.bundle,self.prepared)

    def test_no_family_inheritance(self):
        self.prepared['records'][2]['candidate_entity_id']='current:south-equatorial'
        with self.assertRaisesRegex(ValueError,'basin/component'):audit.summarize(self.bundle,self.prepared)

    def test_no_surface_to_undercurrent_assignment(self):
        row=next(r for r in self.prepared['records'] if r['source_flow_label']=='ESC4')
        row['candidate_entity_id']='current:equatorial-undercurrent'
        with self.assertRaisesRegex(ValueError,'not be assigned'):audit.summarize(self.bundle,self.prepared)

    def test_local_installed_access_refused(self):
        with patch.dict(audit.os.environ,{'GITHUB_ACTIONS':'false'}):
            with self.assertRaisesRegex(ValueError,'Cloud-only'):audit.guard()

if __name__=='__main__':unittest.main()
