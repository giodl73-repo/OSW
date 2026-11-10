"""Pure custody, preservation and manifest rules for one scoped cloud delivery."""
import copy
import hashlib
import json
from pathlib import Path
import re
import published_satellite_core_widths_v1 as core
import published_satellite_core_width_index_v1 as index

ROOT=Path(__file__).resolve().parents[1]
SCOPE='research/agulhas-krug-2012-core-widths-runtime-scope-v1.json'
INVENTORY='research/seasonal-core-velocity-engine-run-v1/compile-inventory.json'
MANIFEST='almanac/query-engine.manifest.json';WASM='almanac/query-engine.wasm'
PARENT_MANIFEST='a3704ee9d03f68fe6dff1fc9737be584ff573998ef99aa997b1505b773edd36e'
PARENT_WASM='6caf567278cb644eed9a45c89028bcadf7d919bb4adba6381503af34fe3e0c16'
KEY='published_satellite_core_width_delivery_v1'
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
    if len(parent['rust_source_sha256'])!=103 or len(parent['compile_time_data_sha256'])!=153 or parent['saved_candidate_logical_sha256']!=core.PARENT or parent['saved_candidate_catalog_sha256']!=index.PARENT_CATALOG_SHA:raise ValueError('Exact installed compiler inventory required')
    result=copy.deepcopy(parent)
    for path,row in scope['runtime_source_changes'].items():
        if path in result['rust_source_sha256']:
            if result['rust_source_sha256'][path]!=row['historical_sha256']:raise ValueError('Historical Rust source differs')
            result['rust_source_sha256'][path]=row['candidate_sha256']
    result['rust_source_sha256']['rust/osw-query/src/satellite_core_widths.rs']=scope['added_source_sha256']['rust/osw-query/src/satellite_core_widths.rs']
    result['compile_time_data_sha256'][core.SOURCE]=scope['source_dependencies_sha256'][core.SOURCE]
    result['compile_time_data_sha256']['almanac/index-catalog.json']=catalog_sha
    result.update(schema='osw.satellite-core-width-compiled-inputs.v1',parent_logical_sha256=core.PARENT,saved_candidate_logical_sha256=logical_sha,saved_candidate_catalog_sha256=catalog_sha)
    return result


def verify_collections(parent,child):
    if set(parent['collections'])!=set(child['collections']):raise ValueError('Collection inventory changed')
    for name,rows in parent['collections'].items():
        actual=copy.deepcopy(child['collections'][name]) if name=='objects' else child['collections'][name]
        if name=='widths':
            if len(rows)!=172 or len(actual)!=174 or actual[172:]!=core.records():raise ValueError('Width append differs')
            actual=actual[:172]
        elif name=='objects':
            owners=[r for r in actual if r['id']==core.OWNER]
            if len(owners)!=1 or owners[0]['width_ids'][-2:]!=[r['id'] for r in core.records()] or owners[0]['capabilities']['scoped_width']!=4:raise ValueError('Agulhas append differs')
            owners[0]['width_ids']=owners[0]['width_ids'][:-2];owners[0]['capabilities']['scoped_width']=2
        if actual!=rows:raise ValueError('Original collection changed: '+name)


def verify_snapshot(name,old,new):
    if new.get('ok') is not True or set(new)!=set(old)|{'satellite_core_width_scenes'}:raise ValueError('Snapshot field inventory differs')
    allowed={'bundle_sha256','satellite_core_width_scenes','supplemental_widths'}|({'phase_plans'} if name=='seasons' else set())
    for key in set(old)-allowed:
        if new[key]!=old[key]:raise ValueError('Prior snapshot field changed: '+key)
    scene=new['satellite_core_width_scenes']
    if set(scene)!= {'agulhas'} or scene['agulhas']['records']!=core.records():raise ValueError('Satellite snapshot scene differs')
    ids={r['id'] for r in core.records()}
    if [r for r in new['supplemental_widths'] if r['id'] not in ids]!=old['supplemental_widths'] or [r for r in new['supplemental_widths'] if r['id'] in ids]!=core.records():raise ValueError('Prior supplemental widths changed')
    if name=='seasons':
        if set(new['phase_plans'])!=set(old['phase_plans']):raise ValueError('Phase owner inventory changed')
        for owner,prior in old['phase_plans'].items():
            after=new['phase_plans'][owner]
            if owner!='agulhas':
                if after!=prior:raise ValueError('Unrelated phase plan changed')
                continue
            for key in set(prior)-{'phases','eligible_indices'}:
                if after[key]!=prior[key]:raise ValueError('Agulhas playback convention changed: '+key)
            phases=after['phases'];added=[p for p in phases if p['id'] in ids]
            if {p['id'] for p in added}!=ids or any(p['playback_step_eligible'] is not False for p in added) or [p for p in phases if p['id'] not in ids]!=prior['phases']:raise ValueError('Static mean phases or prior states differ')
            for plan in [prior,after]:
                if any(i<0 or i>=len(plan['phases']) for i in plan['eligible_indices']):raise ValueError('Invalid playback index')
            if [phases[i]['id'] for i in after['eligible_indices']]!=[prior['phases'][i]['id'] for i in prior['eligible_indices']]:raise ValueError('Prior eligible states changed')


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
    deps=proof.get('production_dependencies',[]);required_deps={core.SOURCE,'rust/osw-query/src/satellite_core_widths.rs','almanac/index-catalog.json','rust/osw-query/src/index_store.rs'}
    if not required_deps<=set(deps) or not set(deps)<=set(inventory['rust_source_sha256'])|set(inventory['compile_time_data_sha256']) or len(deps)!=len(set(deps)) or proof.get('production_dependency_count')!=len(deps) or proof.get('compiled_catalog_dependency_verified') is not True or proof.get('test_only_fixtures_compiled')!=0 or inventory['saved_candidate_logical_sha256']!=logical_sha or inventory['saved_candidate_catalog_sha256']!=replacements['almanac/index-catalog.json']:raise ValueError('Production dependency proof differs')
    result=copy.deepcopy(parent);result['sha256'].update(replacements);result['sha256'][WASM]=wasm_sha;result['rustc']=compiler
    result[KEY]={'parent_engine_manifest_sha256':PARENT_MANIFEST,'parent_logical_sha256':core.PARENT,'logical_sha256':logical_sha,'matching_binary_sha256':wasm_sha,'previous_binary_sha256':PARENT_WASM,'source_commit':source_commit,'new_width_records':2,'new_width_samples':0,'new_length_records':0,'source_documents_after':630,'dependency_proof':copy.deepcopy(proof)}
    if any(result[k]!=parent[k] for k in parent if k not in {'sha256','rustc'}):raise ValueError('Historical engine namespace changed')
    return result
