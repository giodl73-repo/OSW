import copy
import unittest
from unittest.mock import patch
import pacific_nec_product_axis_index_v1 as index

class SourceRegistrationScope(unittest.TestCase):
    def test_local_registration_is_refused_before_any_file_or_index_access(self):
        with patch.object(index.os,'name','nt'),patch.object(index.Path,'read_bytes',side_effect=AssertionError('No source access before cloud gate')):
            with self.assertRaisesRegex(ValueError,'Scoped cloud'):index.source_index(None,None,None)
    def test_audit_refuses_any_original_source_loss_or_replacement(self):
        audit={'original_sources_verified':649,'original_source_strings_preserved':649,'replaced_source_paths':[],
            'added_source_paths':index.DOCUMENTS,'scientific_source_documents_replaced':0}
        index.verify_audit(audit)
        for field,value in [('original_source_strings_preserved',648),('replaced_source_paths',['research/historical.json']),('added_source_paths',index.DOCUMENTS[:-1]),('scientific_source_documents_replaced',1)]:
            bad=copy.deepcopy(audit);bad[field]=value
            with self.assertRaises(ValueError):index.verify_audit(bad)

if __name__=='__main__':unittest.main()
