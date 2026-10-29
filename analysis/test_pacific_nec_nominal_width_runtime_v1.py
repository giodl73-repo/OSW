import copy
import json
import unittest
from unittest.mock import patch
import pacific_nec_nominal_width_runtime_v1 as m


def packet_fixture():
    # Small synthetic packet: only its test contract's counts are substituted.
    # Real source/owner/width records are retained; no installed packet is loaded.
    c=copy.deepcopy(m.contract());identities=c['prior_records']['identities'];sources={s['id']:s for r in identities.values() for s in r['owner_sources']}
    old={'schema':'osw.query-bundle.v1','manifest':{'input_sha256':{'old':'keep'},'historical_basin_receipt':{'keep':True}},'collections':{
        'objects':[copy.deepcopy(r['object']) for r in identities.values()]+[{'id':'other','keep':True}],
        'entities':[copy.deepcopy(r['entity']) for r in identities.values()],
        'widths':[{'id':'old-width','current_id':'other','value':1}],
        'sources':list(copy.deepcopy(sources).values())+[{'id':'other-source','value':2}],
        'reference_routes':[{'id':'old-route','current_id':'other'}],
        'unrelated_physics':[{'id':'physical-row','values':[None,0,7]}]}}
    c['parent_collection_counts']={k:len(v) for k,v in old['collections'].items()}
    new=copy.deepcopy(old);new['collections']['widths'].append(copy.deepcopy(c['width_record']));new['collections']['sources']+=copy.deepcopy(c['new_sources'])
    new['collections']['objects']=[copy.deepcopy(c['final_owner']) if r['id']==m.query.OWNER else r for r in new['collections']['objects']]
    new['manifest']['input_sha256'].update(c['input_sha256']);new['manifest']['input_sha256'][m.query.FILE]=m.query.sha(m.query.FILE)
    new['manifest']['input_sha256'].update({p:'2'*64 for p in m.index.INDEX})
    new['manifest'][m.query.KEY]=m.query.marker(c)
    new['manifest'][m.index.KEY]={'added_source_paths':m.index.DOCUMENTS,'replaced_source_paths':[],
        'original_sources_verified':639,'original_source_strings_preserved':639,'scientific_source_documents_replaced':0}
    return old,new,c


def dashboard_fixture():
    return {'entries':[m.contract()['dashboard_before']]+[{'id':f'fixture:{i}','keep':i} for i in range(250)],
        'counts':{'named_current':111,'other':12},'snapshot_fingerprint':'old','historical':{'keep':True}}


def snapshot_fixture(name):
    if name=='dashboard':
        old={'ok':True,'bundle_sha256':'1'*64,'snapshot_json':json.dumps(dashboard_fixture())}
        new=copy.deepcopy(old);new['bundle_sha256']='2'*64;new['snapshot_json']=json.dumps(m.dashboard_document(dashboard_fixture()))
        return old,new
    old={'ok':True,'bundle_sha256':'1'*64,'basin_identity_scenes':m.basin.scenes(),
        'admitted_current_decisions':[{'current_id':m.query.CURRENT,'measurement_ids':[],'status':'identity_admitted_width_not_admitted','admission_id':'keep'}],
        'current_dimension_evidence_scenes':{'other':{'keep':True}},'supplemental_widths':[{'id':'old'}],
        'sources_json':{'unrelated':'keep'},'historical':{'keep':True}}
    if name=='atlas':old['sources_json']['research/ocean-motion-dashboard.json']=json.dumps(dashboard_fixture())
    else:old['phase_plans']={m.query.CURRENT:m.basin.empty_plan(m.query.CURRENT),'other':{'keep':True}}
    new=copy.deepcopy(old);new['bundle_sha256']='2'*64;new['basin_identity_scenes']=m.scenes()
    decision=new['admitted_current_decisions'][0];decision['measurement_ids']=[m.query.WIDTH_ID];decision['status']='nominal_regional_width_admitted'
    new['current_dimension_evidence_scenes'][m.query.CURRENT]=m.width_scene([m.contract()['width_record']]);new['supplemental_widths'].append(m.contract()['width_record'])
    if name=='atlas':new['sources_json']['research/ocean-motion-dashboard.json']=json.dumps(m.dashboard_document(dashboard_fixture()))
    else:
        new['phase_plans'][m.query.CURRENT]['range_note']='Nominal regional width about 1,000 km; sampling dates, annual ranges and numerical uncertainty remain unknown.'
        new['phase_plans'][m.query.CURRENT]['playback_scope']='Static nominal summary; no comparable dated states for seasonal animation.'
    return old,new


class Preservation(unittest.TestCase):
    def object_fixture(self,owner):
        old={'ok':True,'id':owner,'bundle_sha256':'1'*64,'collections':{'sources':[{'id':f'old:{i}'} for i in range(217)],'widths':[],'entities':[{'id':owner,'keep':True}],'geometries':[]},'basin_identity_context_scene':m.basin.scenes()[owner],'historical':{'keep':True}}
        new=copy.deepcopy(old);new['bundle_sha256']='2'*64;new['collections']['sources']+=m.contract()['new_sources'];new['basin_identity_context_scene']=m.scenes()[owner]
        if owner==m.query.OWNER:
            new['collections']['widths']=[m.contract()['width_record']];new['current_dimension_evidence_scene']=m.width_scene([m.contract()['width_record']])
        return old,new

    def test_all_seven_complete_object_models_preserve_other_fields(self):
        for owner in m.scenes():
            old,new=self.object_fixture(owner);before=copy.deepcopy(old);m.verify_object(owner,old,new);self.assertEqual(old,before)

    def test_object_model_rejects_family_inheritance_and_source_or_entity_changes(self):
        for mutation in ['family-width','source-order','entity']:
            owner='current:north-equatorial';old,new=self.object_fixture(owner)
            if mutation=='family-width':new['collections']['widths']=[m.contract()['width_record']]
            elif mutation=='source-order':new['collections']['sources'].reverse()
            else:new['collections']['entities'][0]['keep']=False
            with self.assertRaises(ValueError,msg=mutation):m.verify_object(owner,old,new)

    def test_complete_packet_envelope_and_declared_append_order(self):
        old,new,c=packet_fixture();before=copy.deepcopy(old)
        with patch.object(m,'contract',return_value=c):m.verify_collections(old,new)
        self.assertEqual(old,before)

    def test_changed_other_physics_history_width_or_namespace_refused(self):
        for mutation in ['physics','source-order','family','width-range','history','extra-namespace','missing-pin']:
            old,new,c=packet_fixture()
            if mutation=='physics':new['collections']['unrelated_physics'][0]['values'][0]=99
            elif mutation=='source-order':new['collections']['sources'].reverse()
            elif mutation=='family':new['collections']['objects'][1]['width_ids']=['inherited']
            elif mutation=='width-range':new['collections']['widths'][-1]['annual_width_range_km']=[900,1100]
            elif mutation=='history':new['manifest']['historical_basin_receipt']['keep']=False
            elif mutation=='extra-namespace':new['manifest']['unexpected']={}
            else:new['manifest']['input_sha256'].pop(m.query.FILE)
            with patch.object(m,'contract',return_value=c),self.assertRaises(ValueError,msg=mutation):m.verify_collections(old,new)

    def test_dashboard_only_target_changes_and_repeat_is_refused(self):
        old=dashboard_fixture();before=copy.deepcopy(old);new=m.dashboard_document(old)
        self.assertEqual(old,before);self.assertEqual(new['entries'][1:],old['entries'][1:])
        self.assertEqual(new['counts'],old['counts']);self.assertEqual(new['historical'],old['historical'])
        self.assertIsNone(new['entries'][0]['latest_observation_date'])
        with self.assertRaises(ValueError):m.dashboard_document(new)

    def test_all_three_complete_api_models_accept_exact_projection(self):
        for name in ['atlas','seasons','dashboard']:
            old,new=snapshot_fixture(name);before=copy.deepcopy(old);m.verify_snapshot(name,old,new);self.assertEqual(old,before)

    def test_unrelated_api_or_seasonal_promotion_is_refused(self):
        for mutation in ['unrelated','can-play','decision','other-scene','source-json']:
            old,new=snapshot_fixture('seasons')
            if mutation=='unrelated':new['historical']['keep']=False
            elif mutation=='can-play':new['phase_plans'][m.query.CURRENT]['can_play']=True
            elif mutation=='decision':new['admitted_current_decisions'][0]['status']='identity_admitted_width_not_admitted'
            elif mutation=='other-scene':new['current_dimension_evidence_scenes']['other']['keep']=False
            else:new['sources_json']['unrelated']='changed'
            with self.assertRaises(ValueError,msg=mutation):m.verify_snapshot('seasons',old,new)

    def test_only_pacific_member_gets_width_context_and_scenes_filter_exactly(self):
        scene=m.scenes()['current:north-equatorial'];width_members=[r for r in scene['members'] if 'nominal_width_evidence' in r]
        self.assertEqual([r['entity_id'] for r in width_members],[m.query.OWNER]);self.assertIn('not inherited',scene['dimension_status'])
        self.assertIsNone(m.width_scene([]));self.assertEqual(m.width_scene([m.contract()['width_record']])['event_records'],[])
        changed=copy.deepcopy(m.contract()['width_record']);changed['approximate_width_km']=900
        with self.assertRaises(ValueError):m.width_scene([changed])


if __name__=='__main__':unittest.main()
