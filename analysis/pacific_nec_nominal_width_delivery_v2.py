"""Pure matching-build receipt checks; installed payloads are never read here."""
import copy
import hashlib
import pacific_nec_nominal_width_query_v1 as query
import pacific_nec_nominal_width_runtime_v2 as runtime
import pacific_nec_nominal_width_index_v1 as index

ROOT=query.ROOT
MANIFEST='almanac/query-engine.manifest.json'
WASM='almanac/query-engine.wasm'
PARENT_MANIFEST=runtime.PARENT_MANIFEST
PARENT_WASM=runtime.PARENT_WASM
KEY='pacific_nec_nominal_width_engine_v1'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
scopes=runtime.scopes
verify_collections=runtime.verify_collections
verify_snapshot=runtime.verify_snapshot
verify_object=runtime.verify_object


def inventory(scope,*,logical_sha,catalog_sha):
    return {'schema':'osw.pacific-nec-nominal-width-compiled-inputs.v1','parent_logical_sha256':query.PARENT,
        'saved_candidate_logical_sha256':logical_sha,'saved_candidate_catalog_sha256':catalog_sha,
        'rust_source_sha256':copy.deepcopy(scope['candidate_rust_source_sha256']),
        'compile_time_data_sha256':{**scope['compile_time_data_sha256'],'almanac/index-catalog.json':catalog_sha},
        'excluded_test_only_data_references':copy.deepcopy(scope['excluded_test_only_data_references'])}


def engine_manifest(parent,replacements,scope,*,generated_paths,logical_sha,wasm_sha,source_commit,compiler,inventory,proof):
    if (parent.get('schema')!='osw.query-engine-manifest.v1' or KEY in parent
            or parent['sha256'][WASM]!=PARENT_WASM or not compiler.startswith('rustc 1.95.0 ')
            or len(inventory['rust_source_sha256'])!=112 or len(inventory['compile_time_data_sha256'])!=165):
        raise ValueError('Exact parent, compiler and complete input inventory required')
    allowed=set(scope['runtime_source_changes'])|set(generated_paths)|{WASM}
    for p,h in replacements.items():
        if p in parent['sha256'] and parent['sha256'][p]!=h and p not in allowed:raise ValueError('Unrelated source rebinding: '+p)
    for p,row in scope['runtime_source_changes'].items():
        if parent['sha256'].get(p)!=row['historical_sha256'] or replacements.get(p)!=row['candidate_sha256']:
            raise ValueError('Runtime source rebinding differs: '+p)
    for group in ['rust_source_sha256','compile_time_data_sha256']:
        if any(replacements.get(p)!=h for p,h in inventory[group].items()):raise ValueError('Compiler input differs')
    required={query.FILE,'rust/osw-query/src/pacific_nec_nominal_width.rs','rust/osw-query/src/equatorial_basin_identities.rs',
        'rust/osw-query/src/current_catalogue.rs','rust/osw-query/src/seasons_data.rs','almanac/index-catalog.json','rust/osw-query/src/index_store.rs'}
    if (not required<=set(proof['production_dependencies']) or proof['test_only_fixtures_compiled']!=0
            or proof['compiled_catalog_dependency_verified'] is not True):raise ValueError('Compiler dependency proof differs')
    result=copy.deepcopy(parent);result['sha256'].update(replacements);result['sha256'][WASM]=wasm_sha;result['rustc']=compiler
    result[KEY]={'parent_engine_manifest_sha256':PARENT_MANIFEST,'parent_logical_sha256':query.PARENT,
        'logical_sha256':logical_sha,'matching_binary_sha256':wasm_sha,'previous_binary_sha256':PARENT_WASM,
        'source_commit':source_commit,'new_width_records':1,'new_publication_sources':2,'new_length_records':0,
        'new_independent_observations':0,'physical_geometry_added':False,'source_documents_after':642,
        'dependency_proof':copy.deepcopy(proof)}
    if any(result[k]!=parent[k] for k in parent if k not in ['sha256','rustc']):raise ValueError('Historical engine namespace changed')
    return result
