import copy
import unittest
from unittest.mock import patch
import published_current_speed_delivery_v1 as m


class DeliveryPolicyTests(unittest.TestCase):
    def test_local_execution_and_unverified_reproduction_refused(self):
        import check_published_current_speed_delivery_v1 as runner
        with patch.dict(runner.os.environ,{'GITHUB_ACTIONS':'false'}):
            with self.assertRaisesRegex(ValueError,'Exact cloud'):
                runner.controls()
        parent={'schema':'osw.query-bundle.v1','manifest':{},'collections':{'objects':[{'id':m.speeds.OWNER}]}}
        original=copy.deepcopy(parent)
        with self.assertRaisesRegex(ValueError,'verified engine candidate'):
            m.assemble(parent,b'not opened',b'not opened',b'not opened')
        self.assertEqual(parent,original)

    def fixture(self):
        changes, additions, contracts=m.scopes()
        parent={'schema':'osw.query-engine-manifest.v1','engine':'rust-osw-query-v1',
                'old_namespace':{'records':'preserve'},'sha256':{m.WASM:m.PARENT_WASM,'research/unrelated.json':'9'*64}}
        parent['sha256'].update({p:r['historical_sha256'] for p,r in changes.items()})
        replacements={p:'a'*64 for p in m.GENERATED}
        replacements.update({p:r['candidate_sha256'] for p,r in changes.items()})
        replacements.update(additions);replacements.update(contracts)
        replacements['rust/osw-query/src/index_store.rs']='a'*64
        deps=['rust/osw-query/src/published_current_speeds.rs',m.speeds.SOURCE,'rust/osw-query/src/index_store.rs','almanac/index-catalog.json']
        inventory={'saved_candidate_logical_sha256':'b'*64,'saved_candidate_catalog_sha256':'a'*64,'rust_source_sha256':{p:replacements[p] for p in deps if p.endswith('.rs')},'compile_time_data_sha256':{p:replacements[p] for p in deps if p.endswith('.json')}}
        proof={'production_dependencies':deps,'production_dependency_count':4,'compiled_catalog_dependency_verified':True,'test_only_fixtures_compiled':0}
        kwargs=dict(logical_sha='b'*64,wasm_sha='c'*64,source_commit='d'*40,compiler='rustc 1.95.0 fixture',inventory=inventory,proof=proof,changed_sources=changes,added_sources=additions,contracts=contracts)
        return parent,replacements,kwargs

    def test_preserve_namespaces_and_parent_without_mutation(self):
        parent,replacements,kwargs=self.fixture();original=copy.deepcopy(parent)
        out=m.engine_manifest(parent,replacements,**kwargs)
        self.assertEqual(parent,original)
        self.assertEqual(out['old_namespace'],original['old_namespace'])
        self.assertEqual(out['sha256']['research/unrelated.json'],'9'*64)
        self.assertEqual(out['sha256'][m.WASM],'c'*64)

    def test_reject_unrelated_pin_change_and_missing_index_guard(self):
        parent,replacements,kwargs=self.fixture();replacements['research/unrelated.json']='0'*64
        with self.assertRaisesRegex(ValueError,'Unrelated'):
            m.engine_manifest(parent,replacements,**kwargs)
        del replacements['research/unrelated.json'];kwargs['proof']['production_dependencies'].remove('rust/osw-query/src/index_store.rs')
        with self.assertRaisesRegex(ValueError,'compiler dependencies'):
            m.engine_manifest(parent,replacements,**kwargs)

    def test_reject_inconsistent_compiler_catalog_metadata(self):
        parent,replacements,kwargs=self.fixture()
        kwargs['inventory']['saved_candidate_catalog_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'catalog identity'):
            m.engine_manifest(parent,replacements,**kwargs)


if __name__=='__main__':unittest.main()
