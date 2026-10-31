"""Bind the complete compiler closure without rebinding unrelated engine inputs."""
import copy
import re

KEY='published_atlantic_nec_band_spans_engine_v1'
PRESENTATION={'almanac/current-dimension-evidence.js','almanac/query.html','almanac/object.html',
              'almanac/reference-routes.html','almanac/seasons.html'}
RUST_CHANGED={'rust/osw-query/src/'+name for name in ('lib.rs','object_view.rs','seasons_data.rs','dashboard.rs',
    'equatorial_basin_identities.rs','pacific_secc_reference.rs','south_java_reference.rs','wicc_winter_reference.rs',
    'aleutian_onishi_width.rs','hansen_asar_widths.rs','neuc_glider_widths.rs')}
RUST_ADDED={'rust/osw-query/src/atlantic_nec_band_spans.rs'}
CONTRACT='research/atlantic-nec-stramma-2005-query-contract-v1.json'

def engine_manifest(parent,replacements,*,inventory,proof,source_commit,logical_sha,wasm_sha,compiler,source_documents):
    if parent.get('schema')!='osw.query-engine-manifest.v1' or KEY in parent:raise ValueError('Exact unapplied engine required')
    if not compiler.startswith('rustc 1.95.0 ') or not re.fullmatch('[0-9a-f]{64}',wasm_sha):raise ValueError('Pinned compiler and binary required')
    rust=inventory['rust_source_sha256'];data=inventory['compile_time_data_sha256']
    if len(rust)!=116 or len(data)!=170:raise ValueError('Complete 116 Rust/Cargo and 170 production-data inputs required')
    if proof.get('test_only_fixtures_compiled')!=0 or proof.get('compiled_catalog_dependency_verified') is not True or proof.get('production_dependency_count')!=278:raise ValueError('Complete production compiler dependency proof required')
    if not RUST_ADDED|{CONTRACT,'almanac/index-catalog.json'}<=set(proof['production_dependencies']):raise ValueError('New production dependencies absent')
    generated={p for p in replacements if p in {'almanac/query-data.json','almanac/query-engine.wasm','almanac/index-catalog.json','almanac/index-data.json.gz','almanac/index-sources.json'} or p.startswith('almanac/query-parts/')}
    allowed=RUST_CHANGED|RUST_ADDED|PRESENTATION|{CONTRACT}|set(source_documents)|generated
    if not PRESENTATION|RUST_ADDED|{CONTRACT}<=set(replacements):raise ValueError('Missing compiler or presentation receipt')
    for path,pin in {**rust,**data}.items():
        if replacements.get(path)!=pin:raise ValueError('Missing compiled input: '+path)
    for path,pin in replacements.items():
        if not re.fullmatch('[0-9a-f]{64}',pin):raise ValueError('Invalid digest')
        if parent['sha256'].get(path)!=pin and path not in allowed:raise ValueError('Unrelated engine input rebound: '+path)
    if any(p in parent['sha256'] for p in RUST_ADDED):raise ValueError('New Rust module already present')
    if replacements.get('almanac/query-engine.wasm')!=wasm_sha:raise ValueError('Binary receipt differs')
    result=copy.deepcopy(parent);result['sha256'].update(replacements);result['rustc']=compiler
    result[KEY]={'schema':'osw.atlantic-nec-band-spans-engine.v1','source_commit':source_commit,
        'logical_sha256':logical_sha,'matching_binary_sha256':wasm_sha,
        'previous_binary_sha256':parent['sha256']['almanac/query-engine.wasm'],
        'source_documents_after':664,'publication_source_rows_after':227,'scoped_width_records_after':187,
        'width_records_added':2,'whole_current_dimensions_added':0,'annual_ranges_added':0,
        'new_independent_observations':0,'dependency_proof':copy.deepcopy(proof)}
    if any(result[k]!=parent[k] for k in parent if k not in ('sha256','rustc')):raise ValueError('Historical engine namespace changed')
    return result
