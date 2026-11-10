"""Exact custody and whole-response preservation rules for EACC cloud verification.

This module performs no builds, installed-packet reads or field processing.
"""
import copy
import hashlib
import json
from pathlib import Path
import re
import published_eacc_cited_width_constraint_v1 as core
import published_eacc_cited_width_constraint_index_v1 as index

ROOT=Path(__file__).resolve().parents[1]
SCOPE='research/eacc-dekeyzer-2012-runtime-scope-v1.json'
INVENTORY='research/wicc-review-width-engine-run-v1/compile-inventory.json'
MANIFEST='almanac/query-engine.manifest.json';WASM='almanac/query-engine.wasm'
PARENT_MANIFEST='b03b4c865bb14f8960122a5581ae292e5f8576454ff2f0de460c40813e4846d3'
PARENT_WASM='037b6cfcee4d21bff80443bc77e0ab12c797eccc419e4ff39665cb09441e0ee0'
KEY='published_eacc_cited_width_constraint_delivery_v1'

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
    if len(parent['rust_source_sha256'])!=105 or len(parent['compile_time_data_sha256'])!=155 or parent['saved_candidate_logical_sha256']!=core.PARENT or parent['saved_candidate_catalog_sha256']!=index.PARENT_CATALOG_SHA:raise ValueError('Exact installed compiler inventory required')
    result=copy.deepcopy(parent)
    for path,row in scope['runtime_source_changes'].items():
        if path in result['rust_source_sha256']:
            if result['rust_source_sha256'][path]!=row['historical_sha256']:raise ValueError('Historical Rust source differs')
            result['rust_source_sha256'][path]=row['candidate_sha256']
    result['rust_source_sha256']['rust/osw-query/src/eacc_cited_width.rs']=scope['added_source_sha256']['rust/osw-query/src/eacc_cited_width.rs']
    result['compile_time_data_sha256'][core.SOURCE]=scope['source_dependencies_sha256'][core.SOURCE]
    result['compile_time_data_sha256']['almanac/index-catalog.json']=catalog_sha
    result.update(schema='osw.eacc-cited-width-compiled-inputs.v1',parent_logical_sha256=core.PARENT,saved_candidate_logical_sha256=logical_sha,saved_candidate_catalog_sha256=catalog_sha)
    return result


def verify_collections(parent,child):
    if child.get('schema')!=parent.get('schema') or set(child['collections'])!=set(parent['collections']):
        raise ValueError('Collection or schema inventory changed')
    if not set(child['manifest'])-set(parent['manifest'])<={core.KEY,index.KEY}:
        raise ValueError('Unrelated manifest namespace added')
    old_owners=[r for r in parent['collections']['objects'] if r['id']==core.OWNER]
    if len(old_owners)!=1 or old_owners[0]['width_ids']!=[] or old_owners[0]['capabilities']['scoped_width']!=0:
        raise ValueError('Exact prior EACC width ownership required')
    owner=old_owners[0]
    for name,old in parent['collections'].items():
        new=child['collections'][name]
        if name=='widths':
            if len(old)!=175 or len(new)!=176 or new[:-1]!=old or new[-1]!=core.record():
                raise ValueError('Exact historical175 widths and one bound required')
        elif name=='objects':
            expected=[core.dashboard_row(r,owner['fingerprint'],owner['section_fingerprints']['measurements']) for r in old]
            if new!=expected:raise ValueError('Object fields changed beyond the EACC width join')
        elif new!=old:raise ValueError('Historical collection changed: '+name)
    expected_marker={'logical_parent_sha256':core.PARENT,'source_file':core.SOURCE,'source_file_sha256':core.document()[1],
        'records_added':1,'prior_width_records':175,'prior_owner_width_ids':[],
        'prior_dashboard_fingerprint':owner['fingerprint'],'prior_measurements_fingerprint':owner['section_fingerprints']['measurements'],
        'width_samples_added':0,'length_records_added':0,'independent_observations_added':0,'geometry_added':False}
    if child['manifest'].get(core.KEY)!=expected_marker:raise ValueError('Constraint admission marker differs')
    for key,value in parent['manifest'].items():
        if key!='input_sha256' and child['manifest'].get(key)!=value:raise ValueError('Historical manifest field changed: '+key)
    before=parent['manifest']['input_sha256'];after=child['manifest']['input_sha256']
    if set(after)!=set(before)|{core.SOURCE} or after.get(core.SOURCE)!=core.document()[1]:raise ValueError('Source input inventory differs')
    if any(after[k]!=v for k,v in before.items() if k not in index.INDEX):raise ValueError('Historical source input rebound')


def scene():
    return {'kind':'published_cited_width_constraints','title':'East African Coastal Current: cited width lower bound',
        'scope':'Historical width constraint cited in a doctoral thesis; no width occupation, fixed depth or boundary geometry supplied.',
        'records':[core.record()],'source_file':core.SOURCE,'full_context_figure':core.FIGURE}


def projected_dashboard(raw):
    original=json.loads(raw)
    # Both installed projections retain the original source hash. Neither
    # derived snapshot string becomes a new dashboard source document.
    source_pin=original.get('published_wicc_review_width_projection_v1',{}).get('source_dashboard_sha256')
    if not isinstance(source_pin,str) or not re.fullmatch('[0-9a-f]{64}',source_pin):
        raise ValueError('Installed parent dashboard provenance required')
    if source_pin!=original.get('published_satellite_core_width_projection_v1',{}).get('source_dashboard_sha256'):
        raise ValueError('Historical dashboard projections disagree on source custody')
    return core.dashboard_document(original,source_pin)


def verify_decisions(old,new):
    expected=copy.deepcopy(old)
    rows=[r for r in expected if r['current_id']=='east-african-coastal']
    if len(rows)!=1 or rows[0]['measurement_ids']!=[] or rows[0]['status']!='identity_admitted_width_not_admitted':
        raise ValueError('One prior unmeasured EACC decision required')
    rows[0]['measurement_ids']=[core.ID];rows[0]['status']='review_cited_width_constraint_admitted'
    if new!=expected:raise ValueError('Admitted decisions changed beyond the exact EACC width')


def verify_snapshot(name,old,new):
    if name=='dashboard':
        if set(old)!=set(new) or new.get('ok') is not True or any(new[k]!=old[k] for k in set(old)-{'snapshot_json','bundle_sha256'}):
            raise ValueError('Dashboard snapshot shape changed')
        if json.loads(new['snapshot_json'])!=projected_dashboard(old['snapshot_json']):
            raise ValueError('Dashboard projection or prior evidence changed')
        return
    if name not in {'atlas','seasons'}:raise ValueError('Unknown complete API')
    if new.get('ok') is not True or set(new)!=set(old)|{'cited_width_constraint_scenes'}:
        raise ValueError('Snapshot field inventory differs')
    allowed={'bundle_sha256','cited_width_constraint_scenes','supplemental_widths','admitted_current_decisions'}|({'phase_plans'} if name=='seasons' else {'sources_json'})
    for key in set(old)-allowed:
        if new[key]!=old[key]:raise ValueError('Prior snapshot field changed: '+key)
    verify_decisions(old['admitted_current_decisions'],new['admitted_current_decisions'])
    if new['cited_width_constraint_scenes']!={'east-african-coastal':scene()}:
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
        if 'east-african-coastal' not in expected:raise ValueError('Prior EACC phase owner required')
        expected['east-african-coastal']=core.phase_plan(old['phase_plans']['east-african-coastal'])
        if new['phase_plans']!=expected:raise ValueError('Static EACC plan or unrelated playback changed')


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
    deps=proof.get('production_dependencies',[]);required_deps={core.SOURCE,'rust/osw-query/src/eacc_cited_width.rs','almanac/index-catalog.json','rust/osw-query/src/index_store.rs'}
    if not required_deps<=set(deps) or not set(deps)<=set(inventory['rust_source_sha256'])|set(inventory['compile_time_data_sha256']) or len(deps)!=len(set(deps)) or proof.get('production_dependency_count')!=len(deps) or proof.get('compiled_catalog_dependency_verified') is not True or proof.get('test_only_fixtures_compiled')!=0 or inventory['saved_candidate_logical_sha256']!=logical_sha or inventory['saved_candidate_catalog_sha256']!=replacements['almanac/index-catalog.json']:raise ValueError('Production dependency proof differs')
    result=copy.deepcopy(parent);result['sha256'].update(replacements);result['sha256'][WASM]=wasm_sha;result['rustc']=compiler
    result[KEY]={'parent_engine_manifest_sha256':PARENT_MANIFEST,'parent_logical_sha256':core.PARENT,'logical_sha256':logical_sha,'matching_binary_sha256':wasm_sha,'previous_binary_sha256':PARENT_WASM,'source_commit':source_commit,'new_width_records':1,'new_width_samples':0,'new_length_records':0,'source_documents_after':632,'dependency_proof':copy.deepcopy(proof)}
    if any(result[k]!=parent[k] for k in parent if k not in {'sha256','rustc'}):raise ValueError('Historical engine namespace changed')
    return result
