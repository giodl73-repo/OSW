import copy
import os
import unittest
from unittest.mock import patch
import check_pacific_nec_nominal_width_parent_v1 as m


class ParentAudit(unittest.TestCase):
    def fixture(self):
        rows={'objects':[],'entities':[],'route_decisions':[],
            'widths':[{'id':f'width:{i}','current_id':'other'} for i in range(178)],
            'reference_routes':[{'id':f'route:{i}','current_id':'other'} for i in range(83)],
            'sources':[{'id':f'source:{i}'} for i in range(217)],'length_assessments':[],
            'current_basin_memberships':[{'id':f'member:{i}'} for i in range(5)]}
        for owner in [m.OWNER,'current:north-equatorial']:
            rows['objects'].append({'id':owner,'source_ids':[]});rows['entities'].append({'id':owner})
            rows['route_decisions'].append({'id':'decision:'+owner,'entity_id':owner})
        return {'collections':rows,'manifest':{'equatorial_basin_identities_v3':{}}}

    def test_local_refusal_before_any_file_read(self):
        with patch.dict(os.environ,{},clear=True),patch.object(m,'read',side_effect=AssertionError('early read')):
            with self.assertRaises(ValueError):m.audit()

    def test_all_three_publications_can_be_missing(self):
        selected,resolutions=m.publications([])
        self.assertEqual(set(selected),set(m.PAPERS))
        self.assertTrue(all(r['status']=='MISSING' for r in resolutions.values()))

    def test_doi_publisher_url_and_author_url_are_same_publication(self):
        for key,paper in m.PAPERS.items():
            for field,value in [('doi','https://doi.org/'+paper['doi'].upper()),('url',paper['urls'][0]),('title',paper['title'].upper())]:
                row={'id':'source:existing',field:value};selected,resolutions=m.publications([row])
                self.assertEqual(selected[key],[row]);self.assertEqual(resolutions[key]['status'],'UNIQUE_EXISTING')

    def test_conflicting_doi_and_multiple_ids_require_reconciliation(self):
        key=next(iter(m.PAPERS));paper=m.PAPERS[key]
        _,resolved=m.publications([{'id':'one','title':paper['title'],'doi':'10.1234/wrong'}])
        self.assertEqual(resolved[key]['status'],'CONFLICTING_METADATA')
        _,resolved=m.publications([{'id':i,'doi':paper['doi']} for i in ['one','two']])
        self.assertEqual(resolved[key]['status'],'RECONCILIATION_REQUIRED')

    def test_repeated_source_ids_refused(self):
        with self.assertRaises(ValueError):m.publications([{'id':'same'},{'id':'same'}])

    def test_family_width_is_not_inherited_by_member(self):
        data=self.fixture();data['collections']['widths'][0].update(current_id='north-equatorial')
        selected,_=m.select_records(data)
        self.assertEqual(selected['identities'][m.OWNER]['widths'],[])
        self.assertEqual(len(selected['identities']['current:north-equatorial']['widths']),1)

    def test_other_owner_publication_width_is_exposed_for_duplicate_audit(self):
        data=self.fixture();doi=m.PAPERS['qiu_okmc_2015']['doi'];data['collections']['sources'][0]['doi']=doi
        data['collections']['widths'][0]['source_id']='source:0'
        selected,_=m.select_records(data)
        self.assertEqual(selected['publication_linked_width_records'],[data['collections']['widths'][0]])

    def test_inventory_changes_or_duplicate_owner_refused(self):
        for change in ['widths','owner','marker']:
            data=self.fixture()
            if change=='widths':data['collections']['widths'].pop()
            elif change=='owner':data['collections']['objects'].append(copy.deepcopy(data['collections']['objects'][0]))
            else:data['manifest'].clear()
            with self.assertRaises(ValueError,msg=change):m.select_records(data)


if __name__=='__main__':unittest.main()
