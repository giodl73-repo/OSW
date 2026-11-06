"""Keep historical engine namespaces while binding the exact new compiled inputs."""
import copy
import re

KEY='pacific_nec_surface_product_axes_engine_v1'
PRESENTATION={'almanac/dashboard.html','almanac/dashboard.js','almanac/query.html','almanac/query-charts.js',
    'almanac/object.html','almanac/object.js','almanac/reference-routes.html','almanac/reference-route-atlas.js'}
ADDED={'almanac/surface-product-axes.js','almanac/surface-product-axes.css'}
RUST_CHANGED={'rust/osw-query/src/'+p for p in ['lib.rs','object_view.rs','atlas_data.rs','seasons_data.rs','dashboard.rs',
    'equatorial_basin_identities.rs','pacific_secc_reference.rs','south_java_reference.rs','wicc_winter_reference.rs']}
RUST_ADDED={'rust/osw-query/src/pacific_nec_product_axes.rs'}
CONTRACT='research/pacific-nec-product-axis-query-contract-v1.json'

def engine_manifest(parent,replacements,*,inventory,proof,source_commit,logical_sha,wasm_sha,compiler,source_documents):
    if parent.get('schema')!='osw.query-engine-manifest.v1' or KEY in parent:raise ValueError('Exact preceding engine required')
    if not compiler.startswith('rustc 1.95.0 ') or not re.fullmatch('[0-9a-f]{64}',wasm_sha):raise ValueError('Pinned compiler and matching binary required')
    rust=inventory['rust_source_sha256'];data=inventory['compile_time_data_sha256']
    if len(rust)!=114 or len(data)!=168:raise ValueError('Complete 114 Rust/Cargo and 168 production-data inputs required')
    if proof.get('test_only_fixtures_compiled')!=0 or proof.get('compiled_catalog_dependency_verified') is not True or proof.get('production_dependency_count')!=274:raise ValueError('Complete compiler-emitted production proof required')
    if not RUST_ADDED|{CONTRACT,'almanac/index-catalog.json'}<=set(proof['production_dependencies']):raise ValueError('Required new production inputs absent')
    generated={p for p in replacements if p in {'almanac/query-data.json','almanac/query-engine.wasm','almanac/index-catalog.json','almanac/index-data.json.gz','almanac/index-sources.json'} or p.startswith('almanac/query-parts/')}
    allowed=RUST_CHANGED|RUST_ADDED|PRESENTATION|ADDED|{CONTRACT}|set(source_documents)|generated
    if not (PRESENTATION|ADDED|RUST_ADDED|{CONTRACT})<=set(replacements):raise ValueError('Incomplete presentation/compiler receipt')
    for path,digest in {**rust,**data}.items():
        if replacements.get(path)!=digest:raise ValueError('Missing compiled input: '+path)
    for path,digest in replacements.items():
        if not re.fullmatch('[0-9a-f]{64}',digest):raise ValueError('Invalid digest')
        if parent['sha256'].get(path)!=digest and path not in allowed:raise ValueError('Unrelated engine input rebound: '+path)
    if any(p in parent['sha256'] for p in ADDED|RUST_ADDED):raise ValueError('Added input already exists')
    if replacements.get('almanac/query-engine.wasm')!=wasm_sha:raise ValueError('Binary receipt differs')
    result=copy.deepcopy(parent);result['sha256'].update(replacements);result['rustc']=compiler
    result[KEY]={'schema':'osw.pacific-nec-product-axis-engine.v1','source_commit':source_commit,'logical_sha256':logical_sha,
        'matching_binary_sha256':wasm_sha,'previous_binary_sha256':parent['sha256']['almanac/query-engine.wasm'],
        'source_documents_after':656,'publication_source_rows_after':225,'new_reported_lengths':0,'new_reference_routes':0,
        'new_physical_widths':0,'new_annual_physical_ranges':0,'new_independent_observations':0,
        'experimental_monthly_paths':36,'experimental_method_scenarios':1332,'dependency_proof':copy.deepcopy(proof)}
    if any(result[k]!=parent[k] for k in parent if k not in ('sha256','rustc')):raise ValueError('Historical namespace changed')
    return result
