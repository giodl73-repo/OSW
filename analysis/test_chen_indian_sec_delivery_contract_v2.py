import copy
import json
import unittest
import chen_indian_sec_delivery_contract_v1 as old_rules
import chen_indian_sec_delivery_contract_v2 as rules


class HistoricalBoundary(unittest.TestCase):
    def fixture(self):
        source=rules.historical_contract()
        owner=next(r for r in source['additions']['objects'] if r['id']==rules.OWNER)
        assessment=next(r for r in source['additions']['length_assessments'] if r['entity_id']==rules.OWNER)
        final={**owner,'regional_length_series_ids':['regional-test']}
        final_assessment={**assessment,'evidence_status':'regional_model_core_grid_series'}
        c={'prior_records':{'identities':{rules.OWNER:{'object':owner,'length_assessments':[assessment]}}},
           'final_owner':final,'final_length_assessment':final_assessment,
           'series_record':{'id':'regional-test','scope':'Regional only'},'reading_records':[],
           'sensitivity_records':[]}
        parent={'ok':True,'bundle_sha256':'old','basin_identity_contract':source,
                'live_rows':[owner,assessment],'unrelated':{'width':None}}
        candidate=copy.deepcopy(parent)
        candidate.update(bundle_sha256='new',live_rows=[final,final_assessment],
                         regional_model_length_scenes={'indian-south-equatorial':rules.full_scene(c)})
        return parent,candidate,c

    def test_regression_source_contract_stays_historical_live_records_project(self):
        old,new,c=self.fixture()
        with self.assertRaises(ValueError):old_rules.verify_snapshot('seasons',old,new,c)
        rules.verify_snapshot('seasons',old,new,c)
        self.assertEqual(old['basin_identity_contract'],new['basin_identity_contract'])
        self.assertNotEqual(old['live_rows'],new['live_rows'])

    def test_rejects_historical_source_mutation_even_if_both_sides_match(self):
        old,new,c=self.fixture()
        old['basin_identity_contract']['unexpected']='changed'
        new['basin_identity_contract']['unexpected']='changed'
        with self.assertRaisesRegex(ValueError,'Parent historical basin contract differs'):
            rules.verify_snapshot('seasons',old,new,c)

    def test_rejects_candidate_source_and_live_or_unrelated_mutations(self):
        for target in ('historical','live','unrelated','scene'):
            old,new,c=self.fixture()
            if target=='historical':new['basin_identity_contract']['unexpected']='changed'
            elif target=='live':new['live_rows']=old['live_rows']
            elif target=='unrelated':new['unrelated']['width']=0
            else:new['regional_model_length_scenes']={}
            with self.subTest(target=target),self.assertRaises(ValueError):
                rules.verify_snapshot('seasons',old,new,c)

    def test_atlas_and_dashboard_keep_existing_document_projection(self):
        for name in ('atlas','dashboard'):
            old,new,c=self.fixture()
            document={'entries':[old['live_rows'][0]],'snapshot_fingerprint':'a'*64,'counts':{'named_current':111}}
            projected=rules.dashboard_document(document,c)
            if name=='atlas':
                path='research/ocean-motion-dashboard.json'
                old['sources_json']={path:json.dumps(document),'historical':'{"keep":1000.0}'}
                new['sources_json']={path:json.dumps(projected),'historical':'{"keep":1000.0}'}
            else:
                old.pop('basin_identity_contract');new.pop('basin_identity_contract')
                new.pop('regional_model_length_scenes')
                old['snapshot_json']=json.dumps(document);new['snapshot_json']=json.dumps(projected)
            rules.verify_snapshot(name,old,new,c)
            if name=='atlas':new['sources_json']['historical']='{"keep":1000}'
            else:
                projected['counts']['named_current']=112
                new['snapshot_json']=json.dumps(projected)
            with self.subTest(name=name),self.assertRaises(ValueError):
                rules.verify_snapshot(name,old,new,c)


if __name__=='__main__':unittest.main()
