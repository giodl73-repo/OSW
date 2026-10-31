import copy
import os
import unittest
from unittest.mock import patch
import check_equatorial_basin_parent_v1 as m


class ParentIdentityAudit(unittest.TestCase):
    def proposals(self):return copy.deepcopy(m.read(m.FACTS)['proposals'])

    def collections(self):
        parents=['current:north-equatorial','current:south-equatorial']
        return {'entities':[{'id':p,'label':p,'type':'named_current'} for p in parents],
            'objects':[{'id':p,'label':p,'record_type':'named_current','source_ids':['source:noaa']} for p in parents],
            'names':[],'sources':[{'id':'source:noaa','url':'https://www.tidesandcurrents.noaa.gov/glossary.html#N'}],
            'widths':[],'reference_routes':[]}

    def test_local_access_refused_before_any_file_read(self):
        with patch.dict(os.environ,{},clear=True),patch.object(m,'read',side_effect=AssertionError('early read')):
            with self.assertRaises(ValueError):m.controls()

    def test_five_qualified_members_and_indian_nec_hold_are_explicit(self):
        p=self.proposals()
        self.assertEqual({r['proposed_id'] for r in p},{'atlantic-north-equatorial','pacific-north-equatorial',
            'atlantic-south-equatorial','pacific-south-equatorial','indian-south-equatorial'})
        source=m.read(m.FACTS)
        self.assertFalse(source['identity_admitted']);self.assertFalse(source['measurements_admitted'])
        self.assertIn('no separate Indian NEC identity',source['source_facts']['monsoon'])

    def test_missing_exact_identities_do_not_modify_parent_or_inherit_widths(self):
        rows=self.collections();rows['widths']=[{'id':'family-context','current_id':'north-equatorial','value':99}]
        before=copy.deepcopy(rows);selected=m.select(rows,self.proposals())
        self.assertEqual(selected['identity_resolution_counts'],{'MISSING_EXACT_IDENTITY':5})
        self.assertEqual(selected['families']['current:north-equatorial']['widths'],rows['widths'])
        self.assertTrue(all('widths' not in r['linked_inventory'] for r in selected['proposals'].values()))
        self.assertEqual(rows,before)
        self.assertEqual(selected['existing_glossary_sources'],rows['sources'])

    def test_exact_existing_identity_and_partial_records_stay_distinct(self):
        rows=self.collections();p=self.proposals();short=p[0]['proposed_id'];ident='current:'+short
        rows['entities'].append({'id':ident,'label':p[0]['proposed_label'],'type':'named_current'})
        result=m.select(rows,p)['proposals'][short]
        self.assertEqual(result['status'],'PARTIAL_EXISTING_RECORDS')
        rows['objects'].append({'id':ident,'label':p[0]['proposed_label']})
        self.assertEqual(m.select(rows,p)['proposals'][short]['status'],'EXACT_EXISTING_IDENTITY')
        rows['names'].append({'id':'name:own','entity_id':ident,'label':p[0]['proposed_label']})
        self.assertEqual(m.select(rows,p)['proposals'][short]['status'],'EXACT_EXISTING_IDENTITY')

    def test_qualified_name_alias_and_label_collision_require_reconciliation(self):
        for collection in ['entities','objects','names']:
            rows=self.collections();p=self.proposals();r={'id':'other','label':p[0]['proposed_label']}
            if collection=='names':r['entity_id']='current:other'
            rows[collection].append(r)
            self.assertEqual(m.select(rows,p)['proposals'][p[0]['proposed_id']]['status'],'RECONCILIATION_REQUIRED')

    def test_proposal_row_is_not_canonical_but_owned_measurements_cannot_be_missed(self):
        rows=self.collections();p=self.proposals();short=p[0]['proposed_id']
        rows['proposed_currents']=[{'id':'proposal:one','proposal_id':short,'geometry':None}]
        r=m.select(rows,p)['proposals'][short]
        self.assertEqual(r['status'],'MISSING_EXACT_IDENTITY')
        self.assertEqual(r['existing_proposal_rows']['proposed_currents'],rows['proposed_currents'])
        rows['widths'].append({'id':'orphan-width','current_id':short,'approximate_width_km':42})
        r=m.select(rows,p)['proposals'][short]
        self.assertEqual(r['status'],'MISSING_IDENTITY_WITH_LINKED_RECORDS')
        self.assertEqual(r['linked_inventory']['widths'],{'count':1,'ids':['orphan-width']})

    def test_duplicate_ids_changed_proposal_count_and_missing_parent_refused(self):
        for collection in ['entities','objects','names','sources']:
            rows=self.collections()
            if not rows[collection]:rows[collection]=[{'id':'duplicate','label':'unrelated'}]
            rows[collection].append(copy.deepcopy(rows[collection][0]))
            with self.assertRaises(ValueError):m.select(rows,self.proposals())
        with self.assertRaises(ValueError):m.select(self.collections(),self.proposals()[:-1])
        p=self.proposals();p[-1]=copy.deepcopy(p[0])
        with self.assertRaises(ValueError):m.select(self.collections(),p)
        rows=self.collections();rows['objects']=[]
        with self.assertRaises(ValueError):m.select(rows,self.proposals())

    def test_workflow_preserves_sequential_read_only_scope(self):
        workflow=(m.ROOT/m.WORKFLOW).read_text(encoding='utf8')
        self.assertIn('group: osw-current-gap-delivery',workflow)
        self.assertIn('cancel-in-progress: false',workflow)
        self.assertIn('check_equatorial_basin_parent_v1.py',workflow)
        for command in ['cargo ','rustup ','playwright','cloud-install']:
            self.assertNotIn(command,workflow)
        self.assertEqual(m.source_url('http://tidesandcurrents.noaa.gov/glossary/'),
            m.source_url('https://www.tidesandcurrents.noaa.gov/glossary.html#North'))


if __name__=='__main__':unittest.main()
