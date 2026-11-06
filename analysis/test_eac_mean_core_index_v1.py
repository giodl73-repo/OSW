import copy
import json
import os
import unittest
from unittest.mock import patch
import current_gap_index_extension as extension
import eac_mean_core_index_v1 as m

class SourceIndex(unittest.TestCase):
    def test_local_access_refused_before_any_decompression(self):
        with patch.dict(os.environ,{},clear=True),patch.object(m.gzip,'decompress',side_effect=AssertionError('early read')):
            with self.assertRaises(ValueError):m.source_index(None,None,None)

    def test_exact_historical_text_preserved_and_active_source_has_unknown_ranges(self):
        documents={'research/original.json':'{ "value": 42 }\n'}
        catalog={'schema':'osw.almanac-index-catalog.v1','source_count':1,'documents':[
            {'path':p,'source_sha256':m.sha(raw.encode()),'source_bytes':len(raw.encode()),'optional':False} for p,raw in documents.items()]}
        corpus={'schema':'osw.almanac-index-bundle.v1','documents':documents};registry={'schema':'osw.almanac-index-sources.v1','documents':list(documents)}
        before=copy.deepcopy((catalog,corpus,registry));source=(m.query.ROOT/m.query.facts.FACTS).read_bytes()
        _,child,_,audit=extension.extend(catalog,corpus,registry,{m.query.facts.FACTS:source})
        self.assertEqual((catalog,corpus,registry),before);self.assertEqual(child['documents']['research/original.json'],documents['research/original.json'])
        self.assertEqual(audit['replaced_source_paths'],[])
        for row in json.loads(child['documents'][m.query.facts.FACTS])['records']:
            self.assertIsNone(row['annual_width_range_km']);self.assertIsNone(row['paired_edge_width_km'])

    def test_unapplied_collection_and_historical_replacement_refused(self):
        with self.assertRaises(ValueError):m.attach({'manifest':{},'collections':{}},{},{})
        audit={'added_source_paths':[m.query.facts.FACTS],'replaced_source_paths':[],'original_sources_verified':633,
            'original_source_strings_preserved':633,'scientific_source_documents_replaced':0}
        m.verify_audit(audit);audit['replaced_source_paths']=['research/original.json']
        with self.assertRaises(ValueError):m.verify_audit(audit)

if __name__=='__main__':unittest.main()
