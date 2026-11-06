import copy
import os
import unittest
from unittest.mock import patch
import azcc_onken_query_v1 as query
import azcc_onken_runtime_v1 as runtime
import azcc_onken_delivery_v1 as delivery
import azcc_onken_cases_v1 as cases
import check_azcc_onken_delivery_v1 as controller

class Delivery(unittest.TestCase):
    def test_local_controller_and_browser_refuse_before_payload_access(self):
        with patch.dict(os.environ,{},clear=True),patch.object(controller,'sha',side_effect=AssertionError('early read')):
            with self.assertRaises(ValueError):controller.controls()
        from check_azcc_onken_browser_v1 import browser_review
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaises(ValueError):browser_review(None,None)

    def test_twelve_cases_keep_filtered_comparison_scope_before_pagination(self):
        contract=query.build_contract();collections={'reference_routes':[],
            'widths':contract['prior_records']['widths']+[contract['width_record']],
            'objects':[contract['final_owner']],'sources':[contract['new_source']]}
        entries=cases.main_cases(collections);self.assertEqual(len(entries),12)
        for request,expected in entries:
            sort=request.get('sort',{'field':'id','direction':'asc'})
            ordered=sorted(expected,key=lambda r:r[sort['field']],reverse=sort['direction']=='desc')
            start=request.get('offset',0);selected=ordered[start:start+request['limit']]
            scene=None
            if expected and request['collection']=='widths':
                scene={'kind':'published_current_dimension_evidence','entity_id':query.OWNER,'width_records':expected,'event_records':[]}
            response={'ok':True,'total':len(expected),'rows':selected,'map_scene':None,'chart_scene':scene}
            cases.verify(request,expected,response)
            if scene and len(expected)>request['limit']:
                bad=copy.deepcopy(response);bad['chart_scene']['width_records']=selected
                with self.assertRaises(ValueError):cases.verify(request,expected,bad)
                compound={**response,'chart_scene':{'kind':'scoped_width_comparisons','scenes':[scene,{'kind':'azores_2009_section_review'}]}}
                cases.verify(request,expected,compound)

    def test_inventory_is_pinned_and_fixture_is_test_only(self):
        scope=runtime.scopes();inventory=delivery.inventory(scope,logical_sha='logical',catalog_sha='new-catalog')
        self.assertEqual(len(inventory['rust_source_sha256']),110)
        self.assertEqual(len(inventory['compile_time_data_sha256']),162)
        self.assertEqual(inventory['compile_time_data_sha256']['almanac/index-catalog.json'],'new-catalog')
        self.assertIn('research/azcc-onken-query-fixture-v1.json',inventory['excluded_test_only_data_references'])

    def test_manifest_keeps_prior_namespaces_and_requires_production_contract(self):
        scope=runtime.scopes();parent=query.read(scope['parent_engine_manifest_file'])
        inventory=delivery.inventory(scope,logical_sha='logical',catalog_sha='new-catalog')
        replacements={**inventory['rust_source_sha256'],**inventory['compile_time_data_sha256']}
        replacements.update({p:r['candidate_sha256'] for p,r in scope['runtime_source_changes'].items()})
        proof={'production_dependencies':[query.FILE,'rust/osw-query/src/azcc_onken_width.rs',
            'almanac/index-catalog.json','rust/osw-query/src/index_store.rs'],
            'test_only_fixtures_compiled':0,'compiled_catalog_dependency_verified':True}
        kwargs={'generated_paths':{'almanac/index-catalog.json'},'logical_sha':'logical','wasm_sha':'new-binary',
            'source_commit':'source','compiler':'rustc 1.95.0 test','inventory':inventory,'proof':proof}
        after=delivery.engine_manifest(parent,replacements,scope,**kwargs)
        self.assertEqual(after[delivery.KEY]['new_flow_event_references'],0)
        self.assertEqual(after[delivery.KEY]['new_width_records'],1)
        for key in parent:
            if key not in ['sha256','rustc']:self.assertEqual(after[key],parent[key])
        bad=copy.deepcopy(proof);bad['production_dependencies'].remove(query.FILE)
        with self.assertRaises(ValueError):delivery.engine_manifest(parent,replacements,scope,**{**kwargs,'proof':bad})
        bad=copy.deepcopy(replacements);bad['rust/osw-query/src/index_store.rs']='unrelated'
        with self.assertRaises(ValueError):delivery.engine_manifest(parent,bad,scope,**kwargs)

    def test_resource_scope_and_case_counts_agree(self):
        workflow=(query.ROOT/controller.WORKFLOW).read_text()
        self.assertIn('OSW_AZCC_ONKEN_DELIVERY_V1: "1"',workflow)
        self.assertIn('group: osw-current-gap-delivery',workflow);self.assertIn('cancel-in-progress: false',workflow)
        self.assertEqual(controller.REQUEST,'research/azcc-onken-delivery-request-v1.json')
        self.assertEqual(controller.PREFLIGHT,'research/azcc-onken-delivery-preflight-v1.json')
        self.assertIn('azcc-onken-delivery-evidence-v1',workflow)
        self.assertNotIn('madagascar-dimensions-delivery-request-v1.json',workflow)
        for kind in ['parity','snapshots']:
            body=(query.ROOT/f'analysis/check_azcc_onken_{kind}_v1.mjs').read_text()
            self.assertIn('OSW_AZCC_ONKEN_DELIVERY_V1',body)
            self.assertNotIn('OSW_MADAGASCAR_DIMENSIONS_DELIVERY_V1',body)
        self.assertIn("mode==='main'?129:50",(query.ROOT/'analysis/check_azcc_onken_parity_v1.mjs').read_text())
        self.assertEqual(controller.sha(query.ROOT/query.FILE),query.sha(query.FILE))
        self.assertIn("rust_tests_passed':261",(query.ROOT/'analysis/check_azcc_onken_delivery_v1.py').read_text())

if __name__=='__main__':unittest.main()
