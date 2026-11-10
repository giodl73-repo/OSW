import copy
import unittest
import pacific_nec_nominal_width_delivery_v1 as m


class EngineReceipts(unittest.TestCase):
    def fixture(self):
        scope=m.scopes();parent=m.query.read(scope['parent_engine_manifest_file']);inv=m.inventory(scope,logical_sha='a'*64,catalog_sha='b'*64)
        generated={'almanac/index-catalog.json','almanac/index-data.json.gz','almanac/index-sources.json','almanac/query-data.json'}
        replacements={**scope['added_source_sha256'],**scope['source_dependencies_sha256'],**inv['rust_source_sha256'],**inv['compile_time_data_sha256'],
            **{p:row['candidate_sha256'] for p,row in scope['runtime_source_changes'].items()},
            **{p:'b'*64 for p in generated}}
        proof={'production_dependencies':[m.query.FILE,'rust/osw-query/src/pacific_nec_nominal_width.rs','rust/osw-query/src/equatorial_basin_identities.rs',
            'rust/osw-query/src/current_catalogue.rs','rust/osw-query/src/seasons_data.rs','almanac/index-catalog.json','rust/osw-query/src/index_store.rs'],
            'test_only_fixtures_compiled':0,'compiled_catalog_dependency_verified':True}
        args={'generated_paths':generated,'logical_sha':'a'*64,'wasm_sha':'c'*64,'source_commit':'d'*40,'compiler':'rustc 1.95.0 (test fixture)',
            'inventory':inv,'proof':proof}
        return parent,replacements,scope,args

    def test_complete_metadata_inventory_and_historical_namespace_preservation(self):
        parent,replacements,scope,args=self.fixture();before=copy.deepcopy(parent)
        result=m.engine_manifest(parent,replacements,scope,**args);self.assertEqual(parent,before)
        for key in parent:
            if key not in ['sha256','rustc']:self.assertEqual(result[key],parent[key],key)
        self.assertEqual(result[m.KEY]['new_independent_observations'],0);self.assertEqual(result[m.KEY]['new_width_records'],1)
        self.assertEqual(len(args['inventory']['rust_source_sha256']),112);self.assertEqual(len(args['inventory']['compile_time_data_sha256']),165)

    def test_unrelated_scientific_source_rebinding_is_refused(self):
        parent,replacements,scope,args=self.fixture();candidate=next(p for p in parent['sha256'] if p not in replacements and p!=m.WASM)
        replacements[candidate]='0'*64
        with self.assertRaises(ValueError):m.engine_manifest(parent,replacements,scope,**args)

    def test_missing_compiler_input_dependency_or_archived_source_binding_is_refused(self):
        for mutation in ['inventory','dependency','archive']:
            parent,replacements,scope,args=self.fixture()
            if mutation=='inventory':args['inventory']['rust_source_sha256'].pop('rust/osw-query/src/pacific_nec_nominal_width.rs')
            elif mutation=='dependency':args['proof']['production_dependencies'].remove(m.query.FILE)
            else:replacements[next(iter(scope['runtime_source_changes']))]='0'*64
            with self.assertRaises(ValueError,msg=mutation):m.engine_manifest(parent,replacements,scope,**args)


if __name__=='__main__':unittest.main()
