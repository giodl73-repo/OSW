import json
import os
import unittest
from unittest.mock import patch
import test_current_gap_index_extension as fixtures
import current_gap_index_extension as extension
import wicc_winter_reference_index_v1 as index
import wicc_winter_reference_query_v1 as query


class ReferenceIndex(unittest.TestCase):
    def test_local_index_access_refused_before_read_or_decompression(self):
        with patch.dict(os.environ,{},clear=True),patch.object(index.gzip,'decompress',side_effect=AssertionError('early decompression')):
            with self.assertRaises(ValueError):index.source_index(None,None,None)

    def test_new_source_preserves_exact_old_text_and_unknown_ranges(self):
        catalog,corpus,registry,_=fixtures.fixture()
        before=dict(corpus['documents'])
        source=(query.ROOT/query.CANDIDATE).read_bytes()
        _,child,_,audit=extension.extend(catalog,corpus,registry,{query.CANDIDATE:source})
        self.assertEqual({p:child['documents'][p] for p in before},before)
        candidate=json.loads(child['documents'][query.CANDIDATE])
        self.assertIsNone(candidate['reported_scenario_range_km'])
        self.assertIsNone(candidate['annual_length_range_km'])
        self.assertEqual(audit['replaced_source_paths'],[])

    def test_unapplied_route_cannot_attach_source_index(self):
        with self.assertRaises(ValueError):index.attach({'manifest':{},'collections':{}},{},{})


if __name__=='__main__':unittest.main()
