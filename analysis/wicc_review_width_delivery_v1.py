"""Exact custody and whole-response preservation rules for WICC cloud verification.

This module performs no builds, installed-packet reads or field processing.
"""
import copy
import hashlib
import json
from pathlib import Path
import re
import published_wicc_review_width_v1 as core
import published_wicc_review_width_index_v1 as index

ROOT=Path(__file__).resolve().parents[1]
SCOPE='research/wicc-vinayachandran-2021-runtime-scope-v1.json'
INVENTORY='research/satellite-core-width-engine-run-v1/compile-inventory.json'
MANIFEST='almanac/query-engine.manifest.json';WASM='almanac/query-engine.wasm'
PARENT_MANIFEST='924a379214df55974f9fbc1dfba6f080c8a8ab5ad80a5c129b2f8044f9101a29'
PARENT_WASM='ac809aadc3bc5b2a2b1e6bdc1d71207535b3383efa391f656c4623a27cd5f668'
KEY='published_wicc_review_width_delivery_v1'

def digest(raw):return hashlib.sha256(raw).hexdigest()

def scopes():
    scope=json.loads((ROOT/SCOPE).read_bytes())
    parent_raw=(ROOT/scope['parent_engine_manifest_file']).read_bytes()
    if digest(parent_raw)!=PARENT_MANIFEST or scope['parent_engine_manifest_sha256']!=PARENT_MANIFEST:raise ValueError('Parent engine custody differs')
    parent=json.loads(parent_raw)
    for path,row in scope['runtime_source_changes'].items():
        original=(ROOT/row['archive_path']).read_bytes()
        if digest(original)!=row['historical_sha256'] or len(original)!=row['historical_bytes'] or parent['sha256'].get(path)!=row['historical_sha256'] or digest((ROOT/path).read_bytes())!=row['candidate_sha256']:raise ValueError('Runtime source custody differs: '+path)
    for path,pin in {**scope['added_source_sha256'],**scope['source_dependencies_sha256']}.items():
        if digest((ROOT/path).read_bytes())!=pin:raise ValueError('Frozen source differs: '+path)
    return scope

def compile_inventory(parent,scope,*,catalog_sha,logical_sha):
    if len(parent['rust_source_sha256'])!=104 or len(parent['compile_time_data_sha256'])!=154 or parent['saved_candidate_logical_sha256']!=core.PARENT or parent['saved_candidate_catalog_sha256']!=index.PARENT_CATALOG_SHA:raise ValueError('Exact installed compiler inventory required')
    result=copy.deepcopy(parent)
    for path,row in scope['runtime_source_changes'].items():
        if path in result['rust_source_sha256']:
            if result['rust_source_sha256'][path]!=row['historical_sha256']:raise ValueError('Historical Rust source differs')
            result['rust_source_sha256'][path]=row['candidate_sha256']
    result['rust_source_sha256']['rust/osw-query/src/wicc_review_width.rs']=scope['added_source_sha256']['rust/osw-query/src/wicc_review_width.rs']
    result['compile_time_data_sha256'][core.SOURCE]=scope['source_dependencies_sha256'][core.SOURCE]
    result['compile_time_data_sha256']['almanac/index-catalog.json']=catalog_sha
    result.update(schema='osw.wicc-review-width-compiled-inputs.v1',parent_logical_sha256=core.PARENT,saved_candidate_logical_sha256=logical_sha,saved_candidate_catalog_sha256=catalog_sha)
    return result


def verify_collections(parent,child):
    expected=core.prepare(parent,logical_parent_sha256=core.PARENT)
    if child['collections']!=expected['collections']:
        raise ValueError('Collections differ from the exact one-width append')
    for key,value in parent['manifest'].items():
        if key!='input_sha256' and child['manifest'].get(key)!=value:
            raise ValueError('Historical manifest field changed: '+key)
    if child['manifest'].get(core.KEY)!=expected['manifest'][core.KEY]:
        raise ValueError('Review width admission marker differs')


def scene():
    return {'kind':'published_review_cited_widths','title':'West India Coastal Current: review-cited width',
        'scope':'Surface current in the west-coast-of-India summer-monsoon discussion; exact sampling dates and numerical width depth unspecified.',
        'records':[core.record()],'source_file':core.SOURCE,'full_context_figure':core.FIGURE}


def projected_dashboard(raw):
    original=json.loads(raw)
    # The parent snapshot already includes the Agulhas projection. Its marker
    # retains the hash of the original dashboard source, not this derived string.
    source_pin=original.get('published_satellite_core_width_projection_v1',{}).get('source_dashboard_sha256')
    if not isinstance(source_pin,str) or not re.fullmatch('[0-9a-f]{64}',source_pin):
        raise ValueError('Installed parent dashboard provenance required')
    return core.dashboard_document(original,source_pin)


def verify_decisions(old,new):
    expected=copy.deepcopy(old)
    rows=[r for r in expected if r['current_id']=='west-india-coastal']
    if len(rows)!=1 or rows[0]['measurement_ids']!=[] or rows[0]['status']!='identity_admitted_width_not_admitted':
        raise ValueError('One prior unmeasured WICC decision required')
    rows[0]['measurement_ids']=[core.ID];rows[0]['status']='review_cited_scoped_width_admitted'
    if new!=expected:raise ValueError('Admitted decisions changed beyond the exact WICC width')


def verify_snapshot(name,old,new):
    if name=='dashboard':
        if set(old)!=set(new) or new.get('ok') is not True or any(new[k]!=old[k] for k in set(old)-{'snapshot_json','bundle_sha256'}):
            raise ValueError('Dashboard snapshot shape changed')
        if json.loads(new['snapshot_json'])!=projected_dashboard(old['snapshot_json']):
            raise ValueError('Dashboard projection or prior evidence changed')
        return
    if name not in {'atlas','seasons'}:raise ValueError('Unknown complete API')
    if new.get('ok') is not True or set(new)!=set(old)|{'review_cited_width_scenes'}:
        raise ValueError('Snapshot field inventory differs')
    allowed={'bundle_sha256','review_cited_width_scenes','supplemental_widths','admitted_current_decisions'}|({'phase_plans'} if name=='seasons' else {'sources_json'})
    for key in set(old)-allowed:
        if new[key]!=old[key]:raise ValueError('Prior snapshot field changed: '+key)
    verify_decisions(old['admitted_current_decisions'],new['admitted_current_decisions'])
    if new['review_cited_width_scenes']!={'west-india-coastal':scene()}:
        raise ValueError('Review scene or retained support differs')
    added=[r for r in new['supplemental_widths'] if r['id']==core.ID]
    retained=[r for r in new['supplemental_widths'] if r['id']!=core.ID]
    if added!=[core.record()] or retained!=old['supplemental_widths']:
        raise ValueError('Supplemental width preservation differs')
    if name=='atlas':
        before=old['sources_json'];after=new['sources_json']
        if set(before)!=set(after) or core.DASHBOARD not in before:raise ValueError('Atlas source inventory changed')
        for path,raw in before.items():
            if path==core.DASHBOARD:
                if json.loads(after[path])!=projected_dashboard(raw):raise ValueError('Atlas dashboard projection differs')
            elif after[path]!=raw:raise ValueError('Historical atlas source bytes changed: '+path)
    else:
        expected=copy.deepcopy(old['phase_plans'])
        if 'west-india-coastal' not in expected:raise ValueError('Prior WICC phase owner required')
        expected['west-india-coastal']=core.phase_plan()
        if new['phase_plans']!=expected:raise ValueError('Static WICC plan or unrelated playback changed')


def engine_manifest(parent,replacements,scope,*,generated_paths,logical_sha,wasm_sha,source_commit,compiler,inventory,proof):
    if parent.get('schema')!='osw.query-engine-manifest.v1' or KEY in parent or parent['sha256'].get(WASM)!=PARENT_WASM or not re.fullmatch('[0-9a-f]{40}',source_commit) or not compiler.startswith('rustc 1.95.0 ') or not all(re.fullmatch('[0-9a-f]{64}',v) for v in [logical_sha,wasm_sha]):raise ValueError('Exact parent engine or compiler required')
    required=set(scope['runtime_source_changes'])|set(scope['added_source_sha256'])|set(scope['source_dependencies_sha256'])
    if not required<=set(replacements):raise ValueError('Required source pins missing')
    allowed=set(generated_paths)|set(scope['runtime_source_changes'])|{WASM}
    for path,pin in replacements.items():
        if not re.fullmatch('[0-9a-f]{64}',pin) or path in parent['sha256'] and parent['sha256'][path]!=pin and path not in allowed:raise ValueError('Unrelated source rebinding: '+path)
    for path,row in scope['runtime_source_changes'].items():
        if parent['sha256'].get(path)!=row['historical_sha256'] or replacements[path]!=row['candidate_sha256']:raise ValueError('Runtime source rebinding')
    for path,pin in {**scope['added_source_sha256'],**scope['source_dependencies_sha256']}.items():
        if replacements[path]!=pin:raise ValueError('Added source rebinding')
    for group in ['rust_source_sha256','compile_time_data_sha256']:
        if any(replacements.get(p)!=pin for p,pin in inventory[group].items()):raise ValueError('Compiler inventory differs')
    deps=proof.get('production_dependencies',[]);required_deps={core.SOURCE,'rust/osw-query/src/wicc_review_width.rs','almanac/index-catalog.json','rust/osw-query/src/index_store.rs'}
    if not required_deps<=set(deps) or not set(deps)<=set(inventory['rust_source_sha256'])|set(inventory['compile_time_data_sha256']) or len(deps)!=len(set(deps)) or proof.get('production_dependency_count')!=len(deps) or proof.get('compiled_catalog_dependency_verified') is not True or proof.get('test_only_fixtures_compiled')!=0 or inventory['saved_candidate_logical_sha256']!=logical_sha or inventory['saved_candidate_catalog_sha256']!=replacements['almanac/index-catalog.json']:raise ValueError('Production dependency proof differs')
    result=copy.deepcopy(parent);result['sha256'].update(replacements);result['sha256'][WASM]=wasm_sha;result['rustc']=compiler
    result[KEY]={'parent_engine_manifest_sha256':PARENT_MANIFEST,'parent_logical_sha256':core.PARENT,'logical_sha256':logical_sha,'matching_binary_sha256':wasm_sha,'previous_binary_sha256':PARENT_WASM,'source_commit':source_commit,'new_width_records':1,'new_width_samples':0,'new_length_records':0,'source_documents_after':631,'dependency_proof':copy.deepcopy(proof)}
    if any(result[k]!=parent[k] for k in parent if k not in {'sha256','rustc'}):raise ValueError('Historical engine namespace changed')
    return result
