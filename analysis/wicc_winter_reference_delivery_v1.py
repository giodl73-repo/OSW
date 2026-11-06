"""Exact source/corpus/API preservation checks; no builds or installed payload reads."""
import copy
import hashlib
import json
import wicc_winter_reference_query_v1 as query
import wicc_winter_reference_runtime_v1 as runtime
import wicc_winter_reference_index_v1 as index

ROOT=query.ROOT
SCOPE='research/wicc-winter-reference-runtime-scope-v2.json'
PARENT_MANIFEST='bfd24fac7c745b3891136fca77a1f6c1ac8a2a55923abc0f74dd30aaa52870e5'
PARENT_WASM='a0c96141734ec124dbd7b0153c412de8ed755cf15357cbb06781f07a4eeab1a0'
MANIFEST='almanac/query-engine.manifest.json'
WASM='almanac/query-engine.wasm'
KEY='wicc_winter_reference_engine_v1'
DASHBOARD='research/ocean-motion-dashboard.json'
sha=lambda raw:hashlib.sha256(raw).hexdigest()


def scopes():
    scope=json.loads((ROOT/SCOPE).read_bytes())
    if sha((ROOT/scope['parent_engine_manifest_file']).read_bytes())!=PARENT_MANIFEST:
        raise ValueError('Parent engine source receipt differs')
    for path,row in scope['runtime_source_changes'].items():
        if sha((ROOT/path).read_bytes())!=row['candidate_sha256'] or sha((ROOT/row['archive_path']).read_bytes())!=row['historical_sha256']:
            raise ValueError('Changed source/history: '+path)
    for path,pin in {**scope['added_source_sha256'],**scope['source_dependencies_sha256']}.items():
        if sha((ROOT/path).read_bytes())!=pin:raise ValueError('Changed frozen source: '+path)
    return scope


def verify_collections(parent,child):
    contract=runtime.build_contract()
    if set(parent['collections'])!=set(child['collections']) or child['schema']!=parent['schema']:
        raise ValueError('Collection/schema inventory differs')
    for name,old in parent['collections'].items():
        new=child['collections'][name]
        if name=='sources':expected=old+contract['query_contract']['new_sources']
        elif name=='reference_routes':expected=old+[contract['query_contract']['route']]
        elif name=='objects':expected=[contract['final_owner'] if r['id']==query.OWNER else r for r in old]
        elif name=='route_decisions':expected=[contract['final_decision'] if r.get('entity_id')==query.OWNER else r for r in old]
        else:expected=old
        if new!=expected:raise ValueError('Unrelated/incorrect collection change: '+name)
    if set(child['manifest'])-set(parent['manifest'])!={runtime.KEY,index.KEY}:
        raise ValueError('Manifest namespace differs')
    for key,value in parent['manifest'].items():
        if key!='input_sha256' and child['manifest'][key]!=value:raise ValueError('Historical manifest differs: '+key)
    before=parent['manifest']['input_sha256'];after=child['manifest']['input_sha256']
    allowed=set(contract['input_sha256'])|{runtime.FILE}|index.INDEX
    if set(after)!=set(before)|allowed:raise ValueError('Source input inventory differs')
    if any(after[p]!=pin for p,pin in before.items() if p not in index.INDEX):
        raise ValueError('Historical source input changed')
    if child['manifest'][runtime.KEY]!=runtime.marker(contract):raise ValueError('Runtime receipt differs')


def projected_dashboard(raw):
    doc=json.loads(raw);contract=runtime.build_contract()
    old=[r for r in doc['entries'] if r['id']==query.OWNER]
    if old!=[contract['dashboard_before']]:raise ValueError('Preceding WICC dashboard differs')
    doc['entries']=[contract['dashboard_after'] if r['id']==query.OWNER else r for r in doc['entries']]
    pin=sha((ROOT/runtime.FILE).read_bytes())
    doc['snapshot_fingerprint']=sha(('osw.wicc-winter-reference.v1\n'+doc['snapshot_fingerprint']+'\n'+pin+'\n').encode())
    doc['wicc_winter_reference_projection_v1']={'contract_file':runtime.FILE,'contract_sha256':pin,
        'scope':'One abstract-supported regional editorial path; no physical length or annual range.'}
    return doc


def verify_snapshot(name,old,new):
    expected=copy.deepcopy(old)
    expected['bundle_sha256']=new['bundle_sha256']
    if name=='dashboard':
        actual=json.loads(new['snapshot_json']);wanted=projected_dashboard(old['snapshot_json'])
        if actual!=wanted:raise ValueError('Complete dashboard projection differs')
        expected['snapshot_json']=new['snapshot_json']
    else:
        expected['working_reference_routes']=runtime.catalog_projection(old['working_reference_routes'],runtime.build_contract())
        if name=='atlas':
            wanted=projected_dashboard(old['sources_json'][DASHBOARD])
            if json.loads(new['sources_json'][DASHBOARD])!=wanted:raise ValueError('Atlas dashboard projection differs')
            expected['sources_json'][DASHBOARD]=new['sources_json'][DASHBOARD]
    if expected!=new:raise ValueError('Complete '+name+' changed outside the declared route/dashboard projection')


def inventory(scope,*,logical_sha,catalog_sha):
    result=json.loads((ROOT/'research/eacc-cited-width-verified-run-v3/compile-inventory.json').read_bytes())
    result['rust_source_sha256']=copy.deepcopy(scope['candidate_rust_source_sha256'])
    result['compile_time_data_sha256']=copy.deepcopy(scope['candidate_compile_time_data_sha256'])
    result['compile_time_data_sha256']['almanac/index-catalog.json']=catalog_sha
    result['excluded_test_only_data_references']=sorted(set(result['excluded_test_only_data_references'])|{'research/wicc-winter-reference-runtime-fixture-v1.json'})
    result.update(schema='osw.wicc-winter-reference-compiled-inputs.v1',parent_logical_sha256=query.PARENT,
                  saved_candidate_logical_sha256=logical_sha,saved_candidate_catalog_sha256=catalog_sha)
    return result


def engine_manifest(parent,replacements,scope,*,generated_paths,logical_sha,wasm_sha,source_commit,compiler,inventory,proof):
    if parent.get('schema')!='osw.query-engine-manifest.v1' or KEY in parent or parent['sha256'][WASM]!=PARENT_WASM or not compiler.startswith('rustc 1.95.0 '):
        raise ValueError('Exact parent/compiler required')
    allowed=set(scope['runtime_source_changes'])|set(generated_paths)|{WASM}
    for p,pin in replacements.items():
        if p in parent['sha256'] and parent['sha256'][p]!=pin and p not in allowed:
            raise ValueError('Unrelated source rebinding: '+p)
    for p,row in scope['runtime_source_changes'].items():
        if parent['sha256'].get(p)!=row['historical_sha256'] or replacements.get(p)!=row['candidate_sha256']:
            raise ValueError('Runtime source rebinding differs: '+p)
    for group in ['rust_source_sha256','compile_time_data_sha256']:
        if any(replacements.get(p)!=pin for p,pin in inventory[group].items()):raise ValueError('Compiler inventory differs')
    required={runtime.FILE,'rust/osw-query/src/wicc_winter_reference.rs','almanac/index-catalog.json','rust/osw-query/src/index_store.rs'}
    if not required<=set(proof['production_dependencies']) or proof['test_only_fixtures_compiled']!=0 or proof['compiled_catalog_dependency_verified'] is not True:
        raise ValueError('Compiler dependency proof differs')
    result=copy.deepcopy(parent);result['sha256'].update(replacements);result['sha256'][WASM]=wasm_sha;result['rustc']=compiler
    result[KEY]={'parent_engine_manifest_sha256':PARENT_MANIFEST,'parent_logical_sha256':query.PARENT,
                 'logical_sha256':logical_sha,'matching_binary_sha256':wasm_sha,'previous_binary_sha256':PARENT_WASM,
                 'source_commit':source_commit,'new_editorial_reference_routes':1,'new_physical_dimensions':0,
                 'source_documents_after':633,'dependency_proof':copy.deepcopy(proof)}
    if any(result[k]!=parent[k] for k in parent if k not in ['sha256','rustc']):raise ValueError('Historical engine namespace changed')
    return result
