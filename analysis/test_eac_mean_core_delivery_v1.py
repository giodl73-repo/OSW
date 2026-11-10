import copy
import json
import os
import unittest
from unittest.mock import patch
import eac_mean_core_query_v1 as query
import eac_mean_core_runtime_v1 as runtime
import eac_mean_core_delivery_v1 as delivery
import eac_mean_core_cases_v1 as cases
import check_eac_mean_core_delivery_v1 as controller


class Delivery(unittest.TestCase):
    def test_local_controller_and_browser_refuse_before_payload_or_browser_access(self):
        with patch.dict(os.environ,{},clear=True),patch.object(controller,'sha',side_effect=AssertionError('early payload read')):
            with self.assertRaises(ValueError):controller.controls()
        from check_eac_mean_core_browser_v1 import browser_review
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaises(ValueError):browser_review(None,None)

    def test_query_case_inventory_and_all_matching_scene_before_pagination(self):
        contract=query.build_contract()
        collections={query.COLLECTION:contract['records'],'objects':[contract['final_owner']],'sources':[contract['new_source']]}
        entries=cases.main_cases(collections);self.assertEqual(len(entries),16)
        for request,expected in entries:
            sort=request.get('sort',{'field':'id','direction':'asc'})
            ordered=sorted(expected,key=lambda r:r[sort['field']],reverse=sort['direction']=='desc')
            start=request.get('offset',0)
            response={'ok':True,'total':len(expected),'rows':ordered[start:start+request['limit']],
                'map_scene':None,'chart_scene':({'kind':'published_mean_core_sections','records':expected} if expected and request['collection']==query.COLLECTION else None)}
            cases.verify(request,expected,response)
            if request['collection']==query.COLLECTION and len(expected)>request['limit']:
                bad=copy.deepcopy(response);bad['chart_scene']['records']=bad['rows']
                with self.assertRaises(ValueError):cases.verify(request,expected,bad)

    def test_compiler_inventory_preserves_parent_and_marks_fixture_test_only(self):
        scope=runtime.scopes();inventory=delivery.inventory(scope,logical_sha='logical',catalog_sha='new-catalog')
        self.assertEqual(len(inventory['rust_source_sha256']),108)
        self.assertEqual(len(inventory['compile_time_data_sha256']),160)
        self.assertEqual(inventory['compile_time_data_sha256']['almanac/index-catalog.json'],'new-catalog')
        self.assertIn('research/eac-mean-core-query-fixture-v1.json',inventory['excluded_test_only_data_references'])

    def test_engine_manifest_protects_old_namespaces_and_rejects_missing_production_contract(self):
        scope=runtime.scopes();parent=query.read(scope['parent_engine_manifest_file'])
        inventory=delivery.inventory(scope,logical_sha='logical',catalog_sha='new-catalog')
        replacements={**inventory['rust_source_sha256'],**inventory['compile_time_data_sha256']}
        replacements.update({p:r['candidate_sha256'] for p,r in scope['runtime_source_changes'].items()})
        proof={'production_dependencies':[query.FILE,'rust/osw-query/src/mean_core_sections.rs',
            'almanac/index-catalog.json','rust/osw-query/src/index_store.rs'],
            'test_only_fixtures_compiled':0,'compiled_catalog_dependency_verified':True}
        kwargs={'generated_paths':{'almanac/index-catalog.json'},'logical_sha':'logical','wasm_sha':'new-binary',
            'source_commit':'source','compiler':'rustc 1.95.0 test','inventory':inventory,'proof':proof}
        after=delivery.engine_manifest(parent,replacements,scope,**kwargs)
        self.assertEqual(after[delivery.KEY]['new_mean_core_section_records'],5)
        for key in parent:
            if key not in ['sha256','rustc']:self.assertEqual(parent[key],after[key])
        bad=copy.deepcopy(proof);bad['production_dependencies'].remove(query.FILE)
        with self.assertRaises(ValueError):delivery.engine_manifest(parent,replacements,scope,**{**kwargs,'proof':bad})
        bad=copy.deepcopy(replacements);bad['rust/osw-query/src/index_store.rs']='unrelated'
        with self.assertRaises(ValueError):delivery.engine_manifest(parent,bad,scope,**kwargs)

    def test_cloud_case_counts_flags_and_resource_limits_agree(self):
        workflow=(query.ROOT/controller.WORKFLOW).read_text()
        self.assertIn('OSW_EAC_MEAN_CORE_DELIVERY_V1: "1"',workflow)
        self.assertIn('group: osw-current-gap-delivery',workflow)
        self.assertIn('cancel-in-progress: false',workflow)
        for kind in ['parity','snapshots']:
            body=(query.ROOT/f'analysis/check_eac_mean_core_{kind}_v1.mjs').read_text()
            self.assertIn('OSW_EAC_MEAN_CORE_DELIVERY_V1',body)
            self.assertNotIn('OSW_WICC_REFERENCE_DELIVERY_V1',body)
        self.assertIn("mode==='main'?99:35",(query.ROOT/'analysis/check_eac_mean_core_parity_v1.mjs').read_text())


if __name__=='__main__':unittest.main()
