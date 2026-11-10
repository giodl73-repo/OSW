"""Pure assembly/preservation rules for indexed regional speed delivery."""
import copy
import hashlib
import json
import re
from pathlib import Path
import published_current_speed_statistics_v1 as speeds
import published_current_speed_source_index_v1 as index

ROOT = Path(__file__).resolve().parents[1]
KEY = 'published_current_speed_delivery_v1'
BASE_SCOPE = 'research/published-current-speed-runtime-scope-v1.json'
SCOPE = 'research/published-current-speed-source-index-delivery-scope-v1.json'
PARENT_MANIFEST = 'dd85f3264d13539b3219b17c5dd30ab675494b46e53653b3c12fe6f3a3856546'
PARENT_WASM = '2c25aad90ef489b9129d004b5efb5ff1309fd58ac08b33e7af16d897fe970ef5'
VERIFIED_SPEED_BUNDLE = 'ebf8ea83b97a62dad76acf341db6754e9d2122c0e66bb1920a61ac6461c85a77'
WASM = 'almanac/query-engine.wasm'
MANIFEST = 'almanac/query-engine.manifest.json'
GENERATED = index.INDEX | {'almanac/query-data.json'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def scopes():
    base = json.loads((ROOT / BASE_SCOPE).read_bytes())
    scope = json.loads((ROOT / SCOPE).read_bytes())
    if sha((ROOT / BASE_SCOPE).read_bytes()) != scope['base_runtime_scope_sha256']:
        raise ValueError('Verified runtime scope changed')
    changes = copy.deepcopy(base['runtime_source_changes'])
    additions = dict(base['added_runtime_source'])
    expected_ui = {'almanac/published-current-speeds.js','almanac/query.html',
                   'almanac/reference-routes.html','almanac/seasons.html'}
    if set(scope['verified_ui_revisions']) != expected_ui:
        raise ValueError('Unexpected UI source revision scope')
    for path, row in scope['verified_ui_revisions'].items():
        old = changes[path]['candidate_sha256'] if path in changes else additions[path]
        archive = (ROOT / row['archive_path']).read_bytes()
        if (old != row['verified_sha256'] or sha(archive) != old or len(archive) != row['bytes']
                or sha((ROOT / path).read_bytes()) != row['candidate_sha256']):
            raise ValueError('Verified/current UI custody differs: ' + path)
        if path in changes:
            changes[path]['candidate_sha256'] = row['candidate_sha256']
        else:
            additions[path] = row['candidate_sha256']
    for path,row in changes.items():
        archive=(ROOT/row['archive_path']).read_bytes()
        if (sha(archive)!=row['historical_sha256'] or len(archive)!=row['bytes']
                or sha((ROOT/path).read_bytes())!=row['candidate_sha256']):
            raise ValueError('Installed/runtime source custody differs: '+path)
    contracts=dict(base['additional_compiled_source_contracts'])
    for path,pin in {**additions,**contracts}.items():
        if sha((ROOT/path).read_bytes())!=pin:
            raise ValueError('Added runtime or scientific source differs: '+path)
    return changes, additions, contracts


def assemble(parent, catalog_raw, compressed, registry_raw):
    child = speeds.prepare(parent,logical_parent_sha256=speeds.PARENT)
    if sha(index.encode(child)) != VERIFIED_SPEED_BUNDLE:
        raise ValueError('Reproduced speed collection differs from verified engine candidate')
    generated, audit = index.source_index(catalog_raw,compressed,registry_raw)
    result = index.attach(child,generated,audit)
    if result['collections'] is not child['collections']:
        raise ValueError('Index extension replaced measurement collections')
    return result,generated,audit


def compile_inventory(original, *, catalog_sha, logical_sha):
    result = copy.deepcopy(original)
    if len(result['rust_source_sha256']) != 102 or len(result['compile_time_data_sha256']) != 152:
        raise ValueError('Exact previously verified compiler inventory required')
    result['compile_time_data_sha256']['almanac/index-catalog.json'] = catalog_sha
    result.update(schema='osw.published-current-speed-compiled-inputs.v1',
                  parent_logical_sha256=speeds.PARENT,saved_candidate_logical_sha256=logical_sha,
                  saved_candidate_catalog_sha256=catalog_sha)
    return result


def engine_manifest(parent, replacements, *, logical_sha, wasm_sha, source_commit,
                    compiler, inventory, proof, changed_sources, added_sources, contracts):
    if (parent.get('schema') != 'osw.query-engine-manifest.v1'
            or parent['sha256'].get(WASM) != PARENT_WASM or KEY in parent
            or not compiler.startswith('rustc 1.95.0 ')
            or not re.fullmatch('[0-9a-f]{40}',source_commit)
            or not all(re.fullmatch('[0-9a-f]{64}',x) for x in [logical_sha,wasm_sha])
            or inventory['saved_candidate_logical_sha256'] != logical_sha):
        raise ValueError('Exact matching delivery identities required')
    required = GENERATED | set(changed_sources) | set(added_sources) | set(contracts)
    if not required <= set(replacements):
        raise ValueError('Incomplete candidate source/artifact inventory')
    allowed = GENERATED | set(changed_sources) | {WASM}
    for path, digest in replacements.items():
        if not re.fullmatch('[0-9a-f]{64}',digest):
            raise ValueError('Malformed candidate digest')
        if path in parent['sha256'] and parent['sha256'][path] != digest and path not in allowed:
            raise ValueError('Unrelated installed source pin would change: ' + path)
    for path, row in changed_sources.items():
        if (parent['sha256'].get(path) != row['historical_sha256']
                or replacements[path] != row['candidate_sha256']):
            raise ValueError('Scoped runtime source differs: ' + path)
    for path, digest in {**added_sources,**contracts}.items():
        if replacements[path] != digest:
            raise ValueError('New source contract differs: ' + path)
    if inventory.get('saved_candidate_catalog_sha256')!=replacements['almanac/index-catalog.json']:
        raise ValueError('Compiled catalog identity differs from delivery metadata')
    for group in ['rust_source_sha256','compile_time_data_sha256']:
        for path,pin in inventory[group].items():
            if replacements.get(path)!=pin:
                raise ValueError('Compiler input hash differs from delivery metadata: '+path)
    actual = proof.get('production_dependencies',[])
    allowed_compile = set(inventory['rust_source_sha256']) | set(inventory['compile_time_data_sha256'])
    needed = {'rust/osw-query/src/published_current_speeds.rs',speeds.SOURCE,
              'rust/osw-query/src/index_store.rs','almanac/index-catalog.json'}
    if (not needed <= set(actual) or not set(actual) <= allowed_compile
            or len(actual) != len(set(actual)) or proof.get('production_dependency_count') != len(actual)
            or proof.get('compiled_catalog_dependency_verified') is not True
            or proof.get('test_only_fixtures_compiled') != 0):
        raise ValueError('Actual production compiler dependencies differ')
    result = copy.deepcopy(parent)
    result['sha256'].update(replacements)
    result['sha256'][WASM] = wasm_sha
    result['rustc'] = compiler
    result[KEY] = {'schema':'osw.published-current-speed-engine-delivery.v1',
        'parent_engine_manifest_sha256':PARENT_MANIFEST,'parent_logical_sha256':speeds.PARENT,
        'previous_binary_sha256':PARENT_WASM,'matching_binary_sha256':wasm_sha,
        'logical_sha256':logical_sha,'source_commit':source_commit,
        'source_documents_added':[speeds.SOURCE],'regional_speed_summary_records':15,
        'new_length_records':0,'new_width_records':0,'dependency_proof':copy.deepcopy(proof)}
    if any(result[k] != parent[k] for k in parent if k not in {'sha256','rustc'}):
        raise ValueError('Inherited complete engine namespace changed')
    return result
