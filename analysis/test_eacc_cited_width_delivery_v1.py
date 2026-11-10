import copy
import json
import unittest
import eacc_cited_width_delivery_v1 as m
import eacc_cited_width_cases_v1 as cases
import test_published_eacc_cited_width_constraint_v1 as fixtures


class EaccConstraintDeliveryTests(unittest.TestCase):
    def test_query_inventory_filters_and_pagination_require_exact_support(self):
        old=[({'collection':'widths','limit':1},175),({'collection':'objects','limit':1},106)]
        self.assertEqual(cases.adapt_legacy_cases(old),[(old[0][0],176),old[1]])
        for bad in [old[1:],old+[old[0]],[(old[0][0],172)],[(old[0][0],True)]]:
            with self.assertRaises(ValueError):cases.adapt_legacy_cases(bad)
        parent=fixtures.EaccConstraintProjectionTests().parent();child=m.core.prepare(parent,logical_parent_sha256=m.core.PARENT)
        self.assertEqual(len(cases.main_cases(child['collections'])),10)
        for query,expected in cases.main_cases(child['collections']):
            ordered=sorted(expected,key=lambda r:r['id'],reverse=query.get('sort',{}).get('direction')=='desc')
            offset=query.get('offset',0)
            response={'ok':True,'total':len(expected),'rows':ordered[offset:offset+query['limit']],
                'chart_scene':m.scene() if expected and query['collection']=='widths' else None,'map_scene':None}
            cases.verify_response(query,expected,response)
            bad=copy.deepcopy(response);bad['total']+=1
            with self.assertRaises(ValueError):cases.verify_response(query,expected,bad)

    def test_complete_collection_preservation_rejects_unrelated_changes(self):
        parent=fixtures.EaccConstraintProjectionTests().parent()
        child=m.core.prepare(parent,logical_parent_sha256=m.core.PARENT)
        m.verify_collections(parent,child)
        for change in [lambda b:b['collections']['width_samples'].clear(),
                       lambda b:b['collections']['widths'].reverse(),
                       lambda b:b['collections']['objects'][1].update(preserve=False),
                       lambda b:b['manifest']['dashboard_receipt'].update(source_json='{}')]:
            bad=copy.deepcopy(child);change(bad)
            with self.assertRaises(ValueError):m.verify_collections(parent,bad)

    def dashboard(self):
        parent=fixtures.EaccConstraintProjectionTests().parent()
        receipt=parent['manifest']['dashboard_receipt']
        doc=json.loads(receipt['source_json'])
        doc['published_satellite_core_width_projection_v1']={'source_dashboard_sha256':receipt['source_sha256'],'preserve':'prior Agulhas projection'}
        doc['published_wicc_review_width_projection_v1']={'source_dashboard_sha256':receipt['source_sha256'],'preserve':'prior WICC projection'}
        return json.dumps(doc),receipt['source_sha256']

    def snapshots(self,name):
        raw,pin=self.dashboard()
        old={'ok':True,'bundle_sha256':'old','supplemental_widths':[{'id':'old-width'}],
             'satellite_core_width_scenes':{'agulhas':{'preserve':True}},'review_cited_width_scenes':{'west-india-coastal':{'preserve':True}},
             'sources_json':{m.core.DASHBOARD:raw,'old-source':'{ "spacing": true }'},
             'admitted_current_decisions':[{'current_id':'east-african-coastal','measurement_ids':[],
                'status':'identity_admitted_width_not_admitted','whole_current_width_km':None},
                {'current_id':'east-india-coastal','preserve':True}]}
        if name=='seasons':old['phase_plans']={'east-african-coastal':{'current_id':'east-african-coastal','phases':[{'id':'old-season','playback_step_eligible':True}],'eligible_indices':[0],'can_play':True,'range_note':'prior scope'},'other':{'can_play':True}}
        new=copy.deepcopy(old);new['bundle_sha256']='new'
        new['cited_width_constraint_scenes']={'east-african-coastal':m.scene()}
        new['supplemental_widths'].append(m.core.record())
        new['admitted_current_decisions'][0].update(measurement_ids=[m.core.ID],status='review_cited_width_constraint_admitted')
        if name=='atlas':new['sources_json'][m.core.DASHBOARD]=json.dumps(m.core.dashboard_document(json.loads(raw),pin))
        else:new['phase_plans']['east-african-coastal']=m.core.phase_plan(old['phase_plans']['east-african-coastal'])
        return old,new

    def test_all_three_complete_apis_preserve_prior_evidence(self):
        for name in ['atlas','seasons']:
            old,new=self.snapshots(name);m.verify_snapshot(name,old,new)
            for change in [lambda d:d['satellite_core_width_scenes']['agulhas'].update(preserve=False),
                           lambda d:d['supplemental_widths'].pop(0),
                           lambda d:d['admitted_current_decisions'][1].update(preserve=False),
                           lambda d:d['cited_width_constraint_scenes']['east-african-coastal']['records'][0].update(independent_observational_sample=True),
                           lambda d:d.update(extra='invented')]:
                bad=copy.deepcopy(new);change(bad)
                with self.assertRaises(ValueError):m.verify_snapshot(name,old,bad)
        raw,_=self.dashboard()
        old={'ok':True,'engine':'rust-osw-query-v1','bundle_sha256':'old','snapshot_json':raw}
        new={**old,'bundle_sha256':'new','snapshot_json':json.dumps(m.projected_dashboard(raw))}
        m.verify_snapshot('dashboard',old,new)
        doc=json.loads(new['snapshot_json']);doc['entries'][1]['preserve']=False
        with self.assertRaises(ValueError):m.verify_snapshot('dashboard',old,{**new,'snapshot_json':json.dumps(doc)})

    def test_dashboard_uses_retained_source_hash_and_preserves_old_projection(self):
        raw,pin=self.dashboard();projected=m.projected_dashboard(raw)
        self.assertEqual(projected['published_eacc_cited_width_constraint_projection_v1']['source_dashboard_sha256'],pin)
        self.assertNotEqual(pin,m.digest(raw.encode()))
        self.assertEqual(projected['published_satellite_core_width_projection_v1'],json.loads(raw)['published_satellite_core_width_projection_v1'])
        bad=json.loads(raw);del bad['published_satellite_core_width_projection_v1']
        with self.assertRaises(ValueError):m.projected_dashboard(json.dumps(bad))

    def test_exact_static_plan_and_source_strings_are_enforced(self):
        old,new=self.snapshots('seasons')
        for change in [lambda d:d['phase_plans']['east-african-coastal'].update(can_play=False),
                       lambda d:d['phase_plans']['other'].update(can_play=False),
                       lambda d:d['sources_json'].update({'old-source':'{"spacing":true}'})]:
            bad=copy.deepcopy(new);change(bad)
            with self.assertRaises(ValueError):m.verify_snapshot('seasons',old,bad)
        old,new=self.snapshots('atlas');new['sources_json']['old-source']='{"spacing":true}'
        with self.assertRaises(ValueError):m.verify_snapshot('atlas',old,new)

    def test_compiler_inventory_and_engine_namespaces_preserved(self):
        scope=m.scopes();parent=json.loads((m.ROOT/scope['parent_engine_manifest_file']).read_bytes())
        prior=json.loads((m.ROOT/m.INVENTORY).read_bytes())
        inv=m.compile_inventory(prior,scope,catalog_sha='a'*64,logical_sha='b'*64)
        self.assertEqual(len(inv['rust_source_sha256']),106)
        self.assertEqual(len(inv['compile_time_data_sha256']),156)
        for path,pin in prior['compile_time_data_sha256'].items():
            if path!='almanac/index-catalog.json':self.assertEqual(inv['compile_time_data_sha256'][path],pin)
        replacements={**{p:r['candidate_sha256'] for p,r in scope['runtime_source_changes'].items()},
            **scope['added_source_sha256'],**scope['source_dependencies_sha256'],
            **inv['rust_source_sha256'],**inv['compile_time_data_sha256']}
        deps=[m.core.SOURCE,'rust/osw-query/src/eacc_cited_width.rs','almanac/index-catalog.json','rust/osw-query/src/index_store.rs']
        proof={'production_dependencies':deps,'production_dependency_count':4,'compiled_catalog_dependency_verified':True,'test_only_fixtures_compiled':0}
        kwargs={'generated_paths':{'almanac/index-catalog.json'},'logical_sha':'b'*64,'wasm_sha':'c'*64,
            'source_commit':'d'*40,'compiler':'rustc 1.95.0 (test)','inventory':inv,'proof':proof}
        result=m.engine_manifest(parent,replacements,scope,**kwargs)
        for key in parent:
            if key not in {'sha256','rustc'}:self.assertEqual(result[key],parent[key])
        for path in ['rust/osw-query/src/abstract_regional_widths.rs',m.core.SOURCE]:
            bad=dict(replacements);bad[path]='0'*64
            with self.assertRaises(ValueError):m.engine_manifest(parent,bad,scope,**kwargs)


if __name__=='__main__':unittest.main()
