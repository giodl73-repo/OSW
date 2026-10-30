"""Bind the complete new compiler closure and preserve historical namespaces."""
import copy
import re
import current_reference_profile_batch_query_v1 as query

KEY='current_reference_profile_engine_v1'
MODULE='rust/osw-query/src/current_reference_profiles.rs'
RUST_CHANGED={'rust/osw-query/src/'+name+'.rs' for name in ['lib','atlas_data','seasons_data','dashboard','planning','equatorial_basin_identities','atlantic_nsec_reference','object_view']}
PRESENTATION={'almanac/'+name for name in ['core-migration-profiles.js','core-migration-profiles.css','query.html','query.js','query-charts.js','reference-routes.html','atlas-width-evidence.js','object.html','object.js','dashboard.html','dashboard.js','dashboard-evidence-schema.js']}
PRESENTATION|={'figures/'+name for name in ['atlantic-nec-regional-reference-reaches-v1.svg','atlantic-nec-regional-reference-reaches-compact-v1.svg','pacific-sec-sun-2025-core-migration-profile-v1.svg','pacific-sec-sun-2025-core-migration-profile-compact-v1.svg']}


def engine_manifest(parent,replacements,*,inventory,proof,source_commit,logical_sha,wasm_sha,compiler,source_documents):
    if parent.get('schema')!='osw.query-engine-manifest.v1' or KEY in parent:raise ValueError('Exact unapplied installed engine required')
    if not compiler.startswith('rustc 1.95.0 ') or not re.fullmatch('[0-9a-f]{64}',wasm_sha) or not re.fullmatch('[0-9a-f]{64}',logical_sha):raise ValueError('Pinned compiler and matching outputs required')
    rust=inventory['rust_source_sha256'];data=inventory['compile_time_data_sha256']
    if len(rust)!=122 or len(data)!=175 or MODULE not in rust or query.FILE not in data:raise ValueError('Complete122 Rust/Cargo and175 production-data inputs required')
    if proof.get('test_only_fixtures_compiled')!=0 or proof.get('compiled_catalog_dependency_verified') is not True or proof.get('production_dependency_count')!=289:raise ValueError('Complete289 production dependency proof required')
    if not {MODULE,query.FILE,'almanac/index-catalog.json'}<=set(proof['production_dependencies']):raise ValueError('New production dependencies absent')
    c=query.read(query.FILE)
    source_bound={**c['input_sha256'],query.FILE:query.sha(query.FILE)}
    generated={p for p in replacements if p in {'almanac/query-data.json','almanac/query-engine.wasm','almanac/index-catalog.json','almanac/index-data.json.gz','almanac/index-sources.json'} or p.startswith('almanac/query-parts/')}
    allowed=RUST_CHANGED|{MODULE}|PRESENTATION|set(source_bound)|set(source_documents)|generated
    if not PRESENTATION|{MODULE,query.FILE}<=set(replacements):raise ValueError('Missing production or presentation receipt')
    for path,pin in {**rust,**data,**source_bound}.items():
        if replacements.get(path)!=pin:raise ValueError('Missing compiled/scientific input: '+path)
    for path,pin in replacements.items():
        if not re.fullmatch('[0-9a-f]{64}',pin):raise ValueError('Invalid digest')
        if parent['sha256'].get(path)!=pin and path not in allowed:raise ValueError('Unrelated engine input rebound: '+path)
    if MODULE in parent['sha256'] or query.FILE in parent['sha256']:raise ValueError('New production inputs already present')
    if replacements.get('almanac/query-engine.wasm')!=wasm_sha:raise ValueError('Binary receipt differs')
    result=copy.deepcopy(parent);result['sha256'].update(replacements);result['rustc']=compiler
    result[KEY]={'schema':'osw.current-reference-profile-engine.v1','source_commit':source_commit,'parent_logical_sha256':query.PARENT,
        'logical_sha256':logical_sha,'matching_binary_sha256':wasm_sha,'previous_binary_sha256':parent['sha256']['almanac/query-engine.wasm'],
        'source_documents_after':696,'source_collection_rows_after':236,'reference_route_records_after':87,'reference_route_owners_after':78,
        'query_collections_after':79,'query_rows_after':110357,'reference_routes_added':2,'sources_added':3,'source_plot_core_profiles_added':24,
        'whole_current_dimensions_added':0,'annual_ranges_added':0,'new_independent_observations':0,'dependency_proof':copy.deepcopy(proof)}
    if any(result[k]!=parent[k] for k in parent if k not in ('sha256','rustc')):raise ValueError('Historical engine namespace changed')
    return result
