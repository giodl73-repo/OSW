import copy
import hashlib
import json
import unittest
import south_java_model_context_projection_v1 as projection


class DashboardProjectionTests(unittest.TestCase):
    def fixture(self):
        objects=[{'id':projection.TARGET,'type':'named_current','evidence_links':[],
            'source_ids':['source:old'],'linked_source_count':1,'capabilities':{'scoped_width':0},
            'section_fingerprints':{'width':'old-width'},'fingerprint':'old-owner','map_features':[]},
            {'id':'current:other','type':'named_current','fingerprint':'other','map_features':[]}]
        doc={'schema':'osw.motion-dashboard.v1','fingerprint_version':2,'entries':copy.deepcopy(objects),
             'counts':{'named_current':2},'snapshot_fingerprint':projection.fingerprint(objects)}
        raw=json.dumps(doc);sha=hashlib.sha256(raw.encode()).hexdigest()
        manifest={'input_sha256':{projection.DASHBOARD:sha,'prior-source':'keep'},
                  'dashboard_receipt':{'source_file':projection.DASHBOARD,'source_sha256':sha,'source_json':raw},
                  'prior-generator':'keep'}
        updated=copy.deepcopy(objects);owner=updated[0]
        owner.update(evidence_links=[{'label':'Model context','url':'query.html?q=test'}],
                     source_ids=['source:old','source:model'],linked_source_count=2,
                     model_analysis_layer_ids=['layer'],fingerprint='new-owner')
        owner['capabilities']['model_analysis_layers']=1
        owner['section_fingerprints']['model_layer_context']='new-model-context'
        return manifest,objects,updated

    def test_refreshes_receipt_and_only_declared_owner_projection(self):
        manifest,old,new=self.fixture();original=copy.deepcopy(manifest)
        updated,proof=projection.refresh(manifest,old,new)
        doc=json.loads(updated['dashboard_receipt']['source_json'])
        self.assertEqual(manifest,original)
        self.assertEqual(doc['entries'][1],old[1])
        self.assertEqual(doc['entries'][0]['evidence_links'],new[0]['evidence_links'])
        self.assertEqual(updated['input_sha256'][projection.DASHBOARD],hashlib.sha256(updated['dashboard_receipt']['source_json'].encode()).hexdigest())
        self.assertEqual(updated['input_sha256']['prior-source'],'keep')
        self.assertEqual(proof['changed_dashboard_entry_ids'],[projection.TARGET])

    def test_rejects_invalid_parent_receipt_without_mutation(self):
        manifest,old,new=self.fixture();manifest['dashboard_receipt']['source_sha256']='wrong'
        before=copy.deepcopy(manifest)
        with self.assertRaises(ValueError):projection.refresh(manifest,old,new)
        self.assertEqual(manifest,before)

    def test_rejects_other_object_change(self):
        manifest,old,new=self.fixture();new[1]['fingerprint']='changed'
        with self.assertRaises(ValueError):projection.refresh(manifest,old,new)

    def test_rejects_physical_owner_field_or_width_capability_change(self):
        for mode in ['field','capability','scientific_fingerprint','new_physical_capability','new_scientific_fingerprint']:
            with self.subTest(mode=mode):
                manifest,old,new=self.fixture()
                if mode=='field':new[0]['whole_current_width_km']=100
                elif mode=='capability':new[0]['capabilities']['scoped_width']=1
                elif mode=='scientific_fingerprint':new[0]['section_fingerprints']['width']='changed'
                elif mode=='new_physical_capability':new[0]['capabilities']['invented_width']=1
                else:new[0]['section_fingerprints']['invented_dimension']='changed'
                with self.assertRaises(ValueError):projection.refresh(manifest,old,new)

    def test_rejects_inconsistent_parent_projection(self):
        manifest,old,new=self.fixture();old[0]['evidence_links']=[{'url':'missing'}]
        with self.assertRaises(ValueError):projection.refresh(manifest,old,new)

    def test_keeps_unchanged_map_feature_projection(self):
        manifest,old,new=self.fixture()
        new[0]['map_features']=[{'kind':'invented-geometry'}]
        with self.assertRaises(ValueError):projection.refresh(manifest,old,new)


if __name__=='__main__':unittest.main()
