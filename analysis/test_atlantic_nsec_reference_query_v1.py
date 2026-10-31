import copy
import unittest
from unittest.mock import patch
import atlantic_nsec_reference_query_v1 as query


class QueryContractTests(unittest.TestCase):
    def test_unrelated_owner_evidence_and_identity_are_preserved(self):
        doc=query.build_contract();old=doc['prior_owner'];new=doc['final_owner']
        changed={'route_ids','route_url','capabilities','map_features','evidence_links','source_ids','linked_source_count','section_fingerprints','fingerprint'}
        self.assertEqual({k:v for k,v in old.items() if k not in changed},{k:v for k,v in new.items() if k not in changed})
        self.assertEqual({k:v for k,v in old['capabilities'].items() if k!='reference_route'},{k:v for k,v in new['capabilities'].items() if k!='reference_route'})
        self.assertEqual(new['width_ids'],old['width_ids'])
        self.assertIsNone(new['published_length_km'])
        self.assertEqual(doc['final_decision']['prior_route_decision'],doc['prior_decision'])

    def test_all_references_retain_editorial_scope_and_distinct_source_pointers(self):
        doc=query.build_contract()
        self.assertEqual(len({r['source_pointer'] for r in doc['routes']}),2)
        for row in doc['routes']:
            self.assertEqual(row['scenario_count'],27)
            self.assertEqual(row['geometry']['coordinates'][-1][0],-35)
            for key in ['rank_eligible','physical_current_axis_admitted','physical_state_join_eligible','seasonal_playback_eligible']:
                self.assertIs(row[key],False)
            self.assertIsNone(row['annual_length_range_km'])
            self.assertIsNone(row['whole_current_length_km'])
        self.assertEqual({r['id'] for r in doc['new_sources']},{query.PUBLICATION,query.METHOD})

    def test_duplicate_or_unreviewed_evidence_refused(self):
        original=query.read
        for mode in ['duplicate','unreviewed']:
            def changed(path):
                value=copy.deepcopy(original(path))
                if mode=='duplicate' and path==query.PARENT_FOLDER+'selected-records.json':value['reference_routes']=[{'id':'existing'}]
                if mode=='unreviewed' and path==query.REVIEW:value['actual_maps_viewed'][0]['actually_viewed']=False
                return value
            with patch.object(query,'read',changed):
                with self.assertRaises(ValueError):query.build_contract()


if __name__=='__main__':unittest.main()
