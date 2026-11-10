"""Independent complete-response and compiled-input rules for Indian SEC delivery."""
import copy
import hashlib
import json

OWNER='current:indian-south-equatorial'
CONTRACT='research/chen-indian-sec-ridge-length-query-contract-v1.json'
CONTRACT_SHA='8a2f105f06ab009fa2a859035ad3f76516aaaf97c6f4608ad413e18758011fc6'

def transform_rows(value,c):
    if isinstance(value,dict):
        if value==c['prior_records']['identities'][OWNER]['object']:return copy.deepcopy(c['final_owner'])
        if value==c['prior_records']['identities'][OWNER]['length_assessments'][0]:return copy.deepcopy(c['final_length_assessment'])
        return {k:transform_rows(v,c) for k,v in value.items()}
    if isinstance(value,list):return [transform_rows(v,c) for v in value]
    return value

def full_scene(c):
    return {'kind':'regional_model_core_length_series','entity_id':OWNER,'title':'Indian SEC: regional model-grid lengths',
            'series':c['series_record'],'readings':c['reading_records'],'sensitivities':c['sensitivity_records'],
            'scope':c['series_record']['scope'],'figure':'figures/chen-indian-sec-regional-ridge-lengths-v1.svg'}

def expected_query(request,parent,c,old_sources):
    result=transform_rows(parent,c)
    if request['collection']=='sources':
        # The retained source-query inventory uses only exact scalar equality.
        if any(f.get('op')!='eq' for f in request.get('filters',[])) or set(request)-{'collection','filters','sort','limit','offset'}:
            raise ValueError('Unsupported historical source-query projection')
        def matches(row):return all(row.get(f['field'])==f['value'] for f in request.get('filters',[]))
        old=[r for r in old_sources if matches(r)]
        order=request.get('sort',{'field':'id','direction':'asc'})
        key=order['field']
        if any(r.get(key) is None for r in old):raise ValueError('Nullable historical source sort requires explicit convention')
        old=sorted(old,key=lambda r:r[key],reverse=order['direction']=='desc')
        offset=request.get('offset',0);limit=request.get('limit',100)
        if parent['total']!=len(old) or parent['rows']!=old[offset:offset+limit]:raise ValueError('Historical source rows do not match the audited collection')
        new=sorted(old+[r for r in c['new_sources'] if matches(r)],key=lambda r:r[key],reverse=order['direction']=='desc')
        result['total']=len(new);result['rows']=new[offset:offset+limit]
    return result

def dashboard_document(value,c):
    result=transform_rows(value,c)
    if sum(r.get('id')==OWNER for r in value['entries'])!=1:raise ValueError('One preceding Indian SEC dashboard row required')
    if 'indian_sec_model_grid_length_projection_v1' in value:raise ValueError('Already projected dashboard')
    result['snapshot_fingerprint']=hashlib.sha256(('osw.indian-sec-model-grid-lengths.v1\n'+value['snapshot_fingerprint']+'\n'+CONTRACT_SHA+'\n').encode()).hexdigest()
    result['indian_sec_model_grid_length_projection_v1']={'contract_file':CONTRACT,'contract_sha256':CONTRACT_SHA,
        'regional_series_added':1,'qualified_grid_lengths':8,'withheld_readings':67,'reported_lengths_added':0}
    return result

def verify_snapshot(name,old,new,c):
    if name not in ['atlas','seasons','dashboard'] or old.get('ok') is not True or new.get('ok') is not True:raise ValueError('Complete snapshot required')
    expected=transform_rows(old,c);expected['bundle_sha256']=new['bundle_sha256']
    if name=='dashboard':
        if json.loads(new['snapshot_json'])!=dashboard_document(json.loads(old['snapshot_json']),c):raise ValueError('Complete dashboard document differs')
        expected['snapshot_json']=new['snapshot_json']
    else:
        expected['regional_model_length_scenes']={'indian-south-equatorial':full_scene(c)}
        if name=='atlas':
            path='research/ocean-motion-dashboard.json'
            if json.loads(new['sources_json'][path])!=dashboard_document(json.loads(old['sources_json'][path]),c):raise ValueError('Complete atlas dashboard differs')
            expected['sources_json'][path]=new['sources_json'][path]
    if expected!=new:raise ValueError('Complete '+name+' changed outside declared regional evidence')

def verify_object(owner,old,new,c):
    if old.get('ok') is not True or old.get('id')!=owner or new.get('ok') is not True:raise ValueError('Complete object API required')
    expected=transform_rows(old,c);expected['bundle_sha256']=new['bundle_sha256']
    expected['collections']['sources']+=copy.deepcopy(c['new_sources'])
    if owner==OWNER:expected['regional_model_length_scene']=full_scene(c)
    if expected!=new:raise ValueError('Complete object changed outside declared regional evidence: '+owner)

def verify_inventory(inventory,parent_engine,allowed_changes):
    rust=inventory['rust_source_sha256'];data=inventory['compile_time_data_sha256']
    if len(rust)!=113 or len(data)!=167:raise ValueError('Exact113 Rust/Cargo and167 production data inputs required')
    for path,h in {**rust,**data}.items():
        prior=parent_engine['sha256'].get(path)
        if prior is not None and prior!=h and path not in allowed_changes:raise ValueError('Undeclared production source/data rebinding: '+path)
    if data['almanac/index-catalog.json']!=inventory['saved_candidate_catalog_sha256']:raise ValueError('Compiled catalog not bound to candidate')
    if CONTRACT not in data or 'rust/osw-query/src/indian_sec_model_grid_lengths.rs' not in rust:raise ValueError('Regional source/contract missing from production compile')

def engine_manifest(parent,replacements,*,inventory,allowed_changes,proof,compiler,source_commit,logical_sha,wasm_sha):
    verify_inventory(inventory,parent,allowed_changes)
    if not compiler.startswith('rustc 1.95.0 ') or proof.get('compiled_catalog_dependency_verified') is not True or proof.get('test_only_fixtures_compiled')!=0:
        raise ValueError('Matching compiler and production dependency proof required')
    required={CONTRACT,'research/chen-indian-sec-regional-ridge-lengths-v1.json','rust/osw-query/src/indian_sec_model_grid_lengths.rs','rust/osw-query/src/atlas_data.rs','rust/osw-query/src/seasons_data.rs'}
    if not required<=set(proof['production_dependencies']):raise ValueError('Missing regional production dependencies')
    key='indian_sec_regional_model_lengths_engine_v1'
    if key in parent:raise ValueError('Engine extension already applied')
    for p,h in replacements.items():
        if p in parent['sha256'] and parent['sha256'][p]!=h and p not in allowed_changes:raise ValueError('Unrelated engine input rebound: '+p)
    for group in ['rust_source_sha256','compile_time_data_sha256']:
        if any(replacements.get(p)!=h for p,h in inventory[group].items()):raise ValueError('Incomplete compiled-input receipt')
    result=copy.deepcopy(parent);result['sha256'].update(replacements);result['sha256']['almanac/query-engine.wasm']=wasm_sha;result['rustc']=compiler
    result[key]={'schema':'osw.indian-sec-regional-model-lengths-engine.v1','source_commit':source_commit,'logical_sha256':logical_sha,
        'matching_binary_sha256':wasm_sha,'previous_binary_sha256':parent['sha256']['almanac/query-engine.wasm'],
        'source_documents_after':649,'new_reported_lengths':0,'new_reference_routes':0,'new_widths':0,'new_independent_observations':0,
        'regional_model_series':1,'qualified_grid_lengths':8,'withheld_cases':67,'sensitivity_scenarios':120,'dependency_proof':copy.deepcopy(proof)}
    if any(result[k]!=parent[k] for k in parent if k not in ['sha256','rustc']):raise ValueError('Historical engine namespace changed')
    return result
