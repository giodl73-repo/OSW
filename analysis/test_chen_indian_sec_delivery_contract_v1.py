import copy
import json
import os
import unittest
from unittest.mock import patch
import chen_indian_sec_delivery_contract_v1 as m
import check_chen_indian_sec_delivery_v1 as gate

class DeliveryContract(unittest.TestCase):
    def contract(self):
        return {'prior_records':{'identities':{m.OWNER:{'object':{'id':m.OWNER,'length':None},'length_assessments':[{'id':'length','entity_id':m.OWNER,'value':None}]}}},
                'final_owner':{'id':m.OWNER,'length':None,'series':1},'final_length_assessment':{'id':'length','entity_id':m.OWNER,'value':None,'regional':1},
                'series_record':{'id':'series','scope':'Regional only'},'reading_records':[{'id':'withheld','length_km':None}],
                'sensitivity_records':[{'id':'choice'}],'new_sources':[{'id':'new-source','year':2022}]}
    def test_local_refusal_precedes_data_and_compiler(self):
        with patch.dict(os.environ,{},clear=True),patch.object(gate,'read',side_effect=AssertionError('early read')),patch.object(gate.subprocess,'check_output',side_effect=AssertionError('early compiler')):
            with self.assertRaises(ValueError):gate.controls()
    def test_only_exact_known_rows_project(self):
        c=self.contract();prior=c['prior_records']['identities'][m.OWNER]['object']
        self.assertEqual(m.transform_rows([prior,{'id':'other','length':None}],c),[c['final_owner'],{'id':'other','length':None}])
        self.assertEqual(prior,{'id':m.OWNER,'length':None})
    def test_source_inventory_projection_preserves_pagination_and_filters(self):
        c=self.contract();rows=[{'id':'a','year':2015},{'id':'z','year':2022}]
        query={'collection':'sources','filters':[],'limit':1,'offset':1}
        before={'ok':True,'rows':[rows[1]],'total':2,'chart_scene':None}
        after=m.expected_query(query,before,c,rows)
        self.assertEqual(after['total'],3);self.assertEqual(after['rows'],c['new_sources'])
        bad=copy.deepcopy(before);bad['rows']=[]
        with self.assertRaises(ValueError):m.expected_query(query,bad,c,rows)
    def test_complete_object_scope_and_unrelated_changes_refused(self):
        c=self.contract();old={'ok':True,'id':m.OWNER,'bundle_sha256':'old','collections':{'sources':[]}}
        new=copy.deepcopy(old);new['bundle_sha256']='new';new['collections']['sources']=c['new_sources'];new['regional_model_length_scene']=m.full_scene(c)
        m.verify_object(m.OWNER,old,new,c)
        new['collections']['widths']=[{'width':100}]
        with self.assertRaises(ValueError):m.verify_object(m.OWNER,old,new,c)
    def test_family_cannot_inherit_model_scene(self):
        c=self.contract();owner='current:south-equatorial';old={'ok':True,'id':owner,'bundle_sha256':'old','collections':{'sources':[]}}
        new=copy.deepcopy(old);new['bundle_sha256']='new';new['collections']['sources']=c['new_sources'];m.verify_object(owner,old,new,c)
        new['regional_model_length_scene']=m.full_scene(c)
        with self.assertRaises(ValueError):m.verify_object(owner,old,new,c)
    def test_complete_snapshot_changes_are_bounded(self):
        c=self.contract();old={'ok':True,'bundle_sha256':'old','untouched':{'width':None}}
        new={**old,'bundle_sha256':'new','regional_model_length_scenes':{'indian-south-equatorial':m.full_scene(c)}}
        m.verify_snapshot('seasons',old,new,c)
        new['untouched']={'width':0}
        with self.assertRaises(ValueError):m.verify_snapshot('seasons',old,new,c)
    def test_dashboard_only_declared_owner_and_fingerprint_change(self):
        c=self.contract();prior=c['prior_records']['identities'][m.OWNER]['object']
        doc={'entries':[prior,{'id':'other'}],'snapshot_fingerprint':'a'*64,'counts':{'named_current':111}}
        old={'ok':True,'bundle_sha256':'old','snapshot_json':json.dumps(doc)}
        final=m.dashboard_document(doc,c);new={'ok':True,'bundle_sha256':'new','snapshot_json':json.dumps(final)}
        m.verify_snapshot('dashboard',old,new,c)
        final['counts']['named_current']=112;new['snapshot_json']=json.dumps(final)
        with self.assertRaises(ValueError):m.verify_snapshot('dashboard',old,new,c)

if __name__=='__main__':unittest.main()
