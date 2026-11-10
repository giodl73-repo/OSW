import copy
import json
import unittest
from unittest.mock import patch
import satellite_core_width_delivery_v1 as m
import satellite_core_width_cases_v1 as cases
import check_satellite_core_width_delivery_v1 as cloud
import test_published_satellite_core_widths_v1 as fixtures


class SatelliteDeliveryTests(unittest.TestCase):
    def test_runtime_archives_and_compiler_inventory_preserve_old_data(self):
        scope=m.scopes();parent=json.loads((m.ROOT/m.INVENTORY).read_bytes())
        updated=m.compile_inventory(parent,scope,catalog_sha='a'*64,logical_sha='b'*64)
        self.assertEqual(len(updated['rust_source_sha256']),104);self.assertEqual(len(updated['compile_time_data_sha256']),154)
        for path,pin in parent['compile_time_data_sha256'].items():
            if path!='almanac/index-catalog.json':self.assertEqual(updated['compile_time_data_sha256'][path],pin)
        self.assertEqual(parent['saved_candidate_logical_sha256'],m.core.PARENT)

    def test_collection_append_and_twelve_case_semantics(self):
        parent=fixtures.SatelliteWidthProjectionTests().parent();child=m.core.prepare(parent,logical_parent_sha256=m.core.PARENT)
        m.verify_collections(parent,child);self.assertEqual(len(cases.main_cases(child['collections'])),12)
        bad=copy.deepcopy(child);bad['collections']['width_samples'].clear()
        with self.assertRaises(ValueError):m.verify_collections(parent,bad)
        bad=copy.deepcopy(child);bad['collections']['objects'][1]['preserve']=False
        with self.assertRaises(ValueError):m.verify_collections(parent,bad)

    def snapshots(self):
        rows=m.core.records();prior={'ok':True,'bundle_sha256':'old','supplemental_widths':[{'id':'old-width'}],'published_speed_scenes':{'preserve':True},'phase_plans':{'agulhas':{'phases':[{'id':'old-state','playback_step_eligible':True}],'eligible_indices':[0],'can_play':True,'range_note':'old'},'other':{'preserve':True}}}
        updated=copy.deepcopy(prior);updated['bundle_sha256']='new';updated['supplemental_widths'].extend(rows);updated['satellite_core_width_scenes']={'agulhas':{'records':rows}}
        updated['phase_plans']['agulhas']['phases'].extend({'id':r['id'],'playback_step_eligible':False} for r in rows)
        return prior,updated

    def test_only_static_phases_and_exact_new_snapshot_fields_allowed(self):
        prior,updated=self.snapshots();m.verify_snapshot('seasons',prior,updated)
        for change in [lambda x:x['published_speed_scenes'].update(preserve=False),
                       lambda x:x['phase_plans']['agulhas']['phases'][1].update(playback_step_eligible=True),
                       lambda x:x['phase_plans']['agulhas']['eligible_indices'].append(1),
                       lambda x:x['supplemental_widths'].pop(0),
                       lambda x:x.update(unrelated='invented')]:
            bad=copy.deepcopy(updated);change(bad)
            with self.assertRaises(ValueError):m.verify_snapshot('seasons',prior,bad)

    def test_cloud_refused_before_any_installed_artifact_read(self):
        with patch.dict(cloud.os.environ,{'GITHUB_ACTIONS':'false'}),patch.object(cloud,'read',side_effect=AssertionError('Unexpected packet read')):
            with self.assertRaisesRegex(ValueError,'Exact cloud'):cloud.controls()

    def test_manifest_preserves_historical_namespaces_and_rejects_rebinding(self):
        scope=m.scopes();parent=json.loads((m.ROOT/scope['parent_engine_manifest_file']).read_bytes())
        inv=m.compile_inventory(json.loads((m.ROOT/m.INVENTORY).read_bytes()),scope,catalog_sha='a'*64,logical_sha='b'*64)
        replacements={**{p:r['candidate_sha256'] for p,r in scope['runtime_source_changes'].items()},**scope['added_source_sha256'],**scope['source_dependencies_sha256'],**inv['rust_source_sha256'],**inv['compile_time_data_sha256']}
        deps=[m.core.SOURCE,'rust/osw-query/src/satellite_core_widths.rs','almanac/index-catalog.json','rust/osw-query/src/index_store.rs']
        proof={'production_dependencies':deps,'production_dependency_count':4,'compiled_catalog_dependency_verified':True,'test_only_fixtures_compiled':0}
        kwargs={'generated_paths':{'almanac/index-catalog.json'},'logical_sha':'b'*64,'wasm_sha':'c'*64,'source_commit':'d'*40,'compiler':'rustc 1.95.0 (test)','inventory':inv,'proof':proof}
        result=m.engine_manifest(parent,replacements,scope,**kwargs)
        for key in parent:
            if key not in {'sha256','rustc'}:self.assertEqual(result[key],parent[key])
        self.assertEqual(result['sha256'][m.WASM],'c'*64)
        for path in ['rust/osw-query/src/abstract_regional_widths.rs',m.core.SOURCE]:
            changed=dict(replacements);changed[path]='0'*64
            with self.assertRaises(ValueError):m.engine_manifest(parent,changed,scope,**kwargs)


if __name__=='__main__':unittest.main()
