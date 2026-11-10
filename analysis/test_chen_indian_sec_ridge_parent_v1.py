import copy
import os
import unittest
from unittest.mock import patch
import check_chen_indian_sec_ridge_parent_v1 as subject


class CurrentParentGuards(unittest.TestCase):
    def fixture(self):
        rows={'objects':[],'entities':[],'route_decisions':[],
              'widths':[{'id':'width:'+str(i),'current_id':'other'} for i in range(179)],
              'reference_routes':[{'id':'route:'+str(i),'current_id':'other'} for i in range(83)],
              'sources':[{'id':'source:'+str(i)} for i in range(219)],'length_assessments':[],
              'current_basin_memberships':[{'id':'membership:'+str(i)} for i in range(5)]}
        for owner in [subject.OWNER,'current:south-equatorial']:
            rows['objects'].append({'id':owner,'source_ids':[]});rows['entities'].append({'id':owner})
            rows['route_decisions'].append({'id':'decision:'+owner,'entity_id':owner})
        return {'collections':rows,'manifest':{'equatorial_basin_identities_v3':{},'published_pacific_nec_nominal_width_v1':{}}}

    def test_local_refused_before_any_file_or_packet_read(self):
        with patch.dict(os.environ,{},clear=True),patch.object(subject,'read',side_effect=AssertionError('early read')):
            with self.assertRaises(ValueError):subject.audit()

    def test_empty_dois_do_not_match_unrelated_sources(self):
        selected,resolved=subject.publications([{'id':'unrelated'}])
        self.assertTrue(all(not rows for rows in selected.values()))
        self.assertTrue(all(r['status']=='MISSING' for r in resolved.values()))

    def test_paper_doi_and_publisher_url_resolve_same_identity(self):
        key='chen_indian_sec_2022';paper=subject.PAPERS[key]
        for field,value in [('doi','https://doi.org/'+paper['doi'].upper()),('url',paper['urls'][1]),('title',paper['title'])]:
            selected,resolved=subject.publications([{'id':'existing',field:value}])
            self.assertEqual(resolved[key]['status'],'UNIQUE_EXISTING');self.assertEqual(selected[key][0]['id'],'existing')

    def test_provider_dataset_matches_its_specific_record(self):
        key='chen_indian_sec_model_deposit';paper=subject.PAPERS[key]
        selected,resolved=subject.publications([{'id':'deposit','kind':'dataset','url':paper['urls'][0]}])
        self.assertEqual(resolved[key]['status'],'UNIQUE_EXISTING')
        selected,_=subject.publications([{'id':'different','url':'https://data.scsio.ac.cn/metaData-detail/other'}])
        self.assertEqual(selected[key],[])

    def test_duplicate_ids_or_conflicting_metadata_refused_or_exposed(self):
        with self.assertRaises(ValueError):subject.publications([{'id':'same'},{'id':'same'}])
        paper=subject.PAPERS['chen_indian_sec_2022']
        _,resolved=subject.publications([{'id':'bad','title':paper['title'],'doi':'10.1234/wrong'}])
        self.assertEqual(resolved['chen_indian_sec_2022']['status'],'CONFLICTING_METADATA')

    def test_family_measurements_remain_separate(self):
        fixture=self.fixture();fixture['collections']['widths'][0]['current_id']='south-equatorial'
        selected,_=subject.select_records(fixture)
        self.assertEqual(selected['identities'][subject.OWNER]['widths'],[])
        self.assertEqual(len(selected['identities']['current:south-equatorial']['widths']),1)

    def test_new_prefix_collision_is_exposed_in_any_collection(self):
        fixture=self.fixture();row={'id':subject.PREFIXES[0]+'collision','current_id':'other'}
        fixture['collections']['new_model_collection']=[row]
        selected,_=subject.select_records(fixture)
        self.assertEqual(selected['candidate_prefix_matches'],{'new_model_collection':[row]})

    def test_changed_parent_inventory_or_markers_refused(self):
        for kind in ['count','owner','marker']:
            fixture=self.fixture()
            if kind=='count':fixture['collections']['sources'].pop()
            elif kind=='owner':fixture['collections']['objects'].append(copy.deepcopy(fixture['collections']['objects'][0]))
            else:fixture['manifest'].pop('published_pacific_nec_nominal_width_v1')
            with self.assertRaises(ValueError):subject.select_records(fixture)


if __name__=='__main__':unittest.main()
