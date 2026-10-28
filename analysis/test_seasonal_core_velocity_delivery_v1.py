import copy
import json
import unittest
from unittest.mock import patch
import seasonal_core_velocity_delivery_v1 as m


class DeliveryPolicyTests(unittest.TestCase):
    def fixture(self):
        scope = m.scopes()
        parent = json.loads((m.ROOT/'research/published-current-speed-installation-saved-engine-manifest-v1.json').read_bytes())
        inventory = m.compile_inventory(json.loads((m.ROOT/m.INVENTORY).read_bytes()),scope,catalog_sha='a'*64,logical_sha='b'*64)
        replacements = {**scope['added_source_sha256'],**scope['scientific_source_sha256']}
        replacements.update({p:r['candidate_sha256'] for p,r in scope['runtime_source_changes'].items()})
        for group in ['rust_source_sha256','compile_time_data_sha256']: replacements.update(inventory[group])
        deps = [m.core.SOURCE,'rust/osw-query/src/published_seasonal_core_velocities.rs','almanac/index-catalog.json','rust/osw-query/src/index_store.rs']
        proof = {'production_dependencies':deps,'production_dependency_count':4,'compiled_catalog_dependency_verified':True,'test_only_fixtures_compiled':0}
        kwargs = dict(generated_paths={'almanac/index-catalog.json'},logical_sha='b'*64,wasm_sha='c'*64,source_commit='d'*40,compiler='rustc 1.95.0 fixture',inventory=inventory,proof=proof)
        return parent,replacements,scope,kwargs

    def test_local_execution_refused_before_artifact_access(self):
        import check_seasonal_core_velocity_delivery_v1 as runner
        with patch.dict(runner.os.environ,{'GITHUB_ACTIONS':'false'}):
            with self.assertRaisesRegex(ValueError,'Exact cloud'): runner.controls()

    def test_preserve_all_installed_namespaces_and_add_one_compiled_source(self):
        parent,replacements,scope,kwargs = self.fixture(); before=copy.deepcopy(parent)
        result = m.engine_manifest(parent,replacements,scope,**kwargs)
        self.assertEqual(parent,before)
        for key,value in parent.items():
            if key not in {'sha256','rustc'}: self.assertEqual(result[key],value)
        self.assertEqual(len(kwargs['inventory']['rust_source_sha256']),103)
        self.assertEqual(len(kwargs['inventory']['compile_time_data_sha256']),153)
        self.assertEqual(result[m.KEY]['record_count'],6)
        self.assertEqual(result[m.KEY]['new_length_records'],0)

    def test_reject_unrelated_pin_source_rebinding_and_missing_production_input(self):
        parent,replacements,scope,kwargs=self.fixture()
        unrelated=next(p for p in parent['sha256'] if p not in replacements and p!=m.WASM)
        wrong=dict(replacements);wrong[unrelated]='0'*64
        with self.assertRaisesRegex(ValueError,'Unrelated'): m.engine_manifest(parent,wrong,scope,**kwargs)
        wrong=dict(replacements);wrong[m.core.SOURCE]='0'*64
        with self.assertRaises(ValueError): m.engine_manifest(parent,wrong,scope,**kwargs)
        wrong=copy.deepcopy(kwargs);wrong['proof']['production_dependencies'].remove(m.core.SOURCE)
        with self.assertRaisesRegex(ValueError,'dependency'): m.engine_manifest(parent,replacements,scope,**wrong)

    def test_workflow_is_read_only_serial_and_request_disabled(self):
        import yaml
        workflow=yaml.safe_load((m.ROOT/'.github/workflows/seasonal-core-velocity-delivery-v1.yml').read_bytes())
        self.assertEqual(workflow['concurrency'],{'group':'osw-current-gap-delivery','cancel-in-progress':False})
        self.assertEqual(workflow['permissions'],{'contents':'read','actions':'read'})
        self.assertEqual(workflow['env']['CARGO_BUILD_JOBS'],'1')
        request=json.loads((m.ROOT/'research/seasonal-core-velocity-delivery-request-v1.json').read_bytes())
        for key in ['installation_permitted','source_field_processing_permitted','main_merge_permitted','local_bulk_sync_permitted']:
            self.assertIs(request[key],False)
        # execute may be enabled only by the later separately pinned activation.
        self.assertIsInstance(request['execute'],bool)


if __name__=='__main__': unittest.main()
