"""Pure matching-engine and historical source preservation rules; no builds."""
import copy
import re
from eacc_connection_parent_custody_v3 import ALLOWED, ARCHIVE_ROOTS
import azores_2009_section_projection_v1 as projection

KEY = 'azores_2009_section_engine_delivery_v1'
MANIFEST = 'almanac/query-engine.manifest.json'
WASM = 'almanac/query-engine.wasm'
PARENT_MANIFEST_SHA = 'e5ccd930ffeb1086821144fbe6c2ffcd3b94781750368b91465d7e83702daf34'
PARENT_WASM_SHA = '33fa5177803cca74fb0cc8d50ee6f2171c45ea9e20fc47c656063d8e822522cd'
ADAPTER = 'rust/osw-query/src/azores_section_review.rs'
CHANGES = {'rust/osw-query/src/' + p + '.rs' for p in ['lib', 'atlas_data', 'seasons_data']} | {
    'almanac/' + p for p in ['query.html', 'reference-routes.html', 'seasons.html',
                            'seasons.js', 'atlas-width-evidence.js', 'query-charts.js']}
CONTRACTS = {projection.REVIEW, projection.BINDINGS, projection.VISUAL, projection.FIGURE}
INDEX = {'almanac/index-catalog.json', 'almanac/index-data.json.gz', 'almanac/index-sources.json'}
GENERATED = INDEX | {'almanac/query-data.json'}


def scope_check(scope):
    if (scope.get('schema') != 'osw.azores-2009-section-runtime-scope.v1'
            or scope.get('parent_engine_manifest_sha256') != PARENT_MANIFEST_SHA
            or scope.get('parent_wasm_sha256') != PARENT_WASM_SHA
            or scope.get('parent_logical_sha256') != projection.PARENT
            or set(scope['runtime_source_changes']) != CHANGES
            or set(scope['added_runtime_source']) != {ADAPTER}
            or set(scope['additional_compiled_source_contracts']) != CONTRACTS
            or scope.get('additional_test_only_fixtures') != []
            or scope.get('new_physical_dimensions') != 0):
        raise ValueError('Exact Azores source-only runtime scope required')


def verify_parent(parent, metadata, historical_bindings, scope):
    scope_check(scope)
    if (parent.get('schema') != 'osw.query-engine-manifest.v1' or parent.get('abi_version') != 1
            or parent.get('engine') != 'rust-osw-query-v1' or parent['sha256'].get(WASM) != PARENT_WASM_SHA):
        raise ValueError('Exact installed parent engine required')
    legacy = {r['manifest_path']: r for r in historical_bindings}
    changes = scope['runtime_source_changes']
    if len(legacy) != len(historical_bindings) or set(legacy) != set(ALLOWED):
        raise ValueError('Exact five inherited historical source bindings required')
    for path, row in legacy.items():
        # query.html has an older inherited archive and an installed version
        # now archived by this scope. Verify both versions, not the new UI bytes
        # against the old installed hash.
        installed = metadata(changes[path]['archive_path'] if path in changes else path)
        if (row['role'] != ALLOWED[path] or not row['archive_path'].startswith(ARCHIVE_ROOTS)
                or metadata(row['archive_path']) != (row['historical_sha256'], row['historical_bytes'])
                or installed != (row['installed_path_sha256'], row['installed_path_bytes'])
                or parent['sha256'].get(path) not in {row['historical_sha256'], row['installed_path_sha256']}):
            raise ValueError('Inherited historical/current source custody differs: ' + path)
    for path, row in changes.items():
        if (parent['sha256'].get(path) != row['historical_sha256']
                or not row['archive_path'].startswith('research/azores-2009-section-runtime-history-v1/')
                or metadata(row['archive_path']) != (row['historical_sha256'], row['bytes'])
                or metadata(path)[0] != row['candidate_sha256']
                or row['candidate_sha256'] == row['historical_sha256']):
            raise ValueError('Changed installed/candidate source custody: ' + path)
    for path, digest in {**scope['added_runtime_source'], **scope['additional_compiled_source_contracts']}.items():
        if path in parent['sha256'] or metadata(path)[0] != digest:
            raise ValueError('New compiled dependency already present or changed: ' + path)
    direct = []; inherited = []; revised = []
    for path, digest in parent['sha256'].items():
        current, _ = metadata(path)
        if path in changes:
            revised.append(path)
        elif current == digest:
            direct.append(path)
        elif path in legacy and digest == legacy[path]['historical_sha256']:
            inherited.append(path)
        else:
            raise ValueError('Unregistered installed parent byte mismatch: ' + path)
    return {'status': 'PASS', 'manifest_paths_verified': len(parent['sha256']),
            'unchanged_current_paths': len(direct), 'historical_paths': sorted(inherited),
            'scoped_runtime_paths': sorted(revised)}


def compile_inventory(original, parent, scope, *, catalog_sha, logical_sha):
    scope_check(scope)
    if (len(original['rust_source_sha256']) != 100 or len(original['compile_time_data_sha256']) != 147
            or len(original['excluded_test_only_data_references']) != 9
            or original['saved_candidate_logical_sha256'] != projection.PARENT):
        raise ValueError('Exact installed South Java compiler inventory required')
    result = copy.deepcopy(original)
    for name in ['rust_source_sha256', 'compile_time_data_sha256']:
        for path, digest in original[name].items():
            if parent['sha256'].get(path) != digest:
                raise ValueError('Installed compiler inventory differs: ' + path)
    for path in CHANGES:
        if path.endswith('.rs'):
            if path not in result['rust_source_sha256']:
                raise ValueError('Revised Rust dependency absent from installed compiler inventory')
            result['rust_source_sha256'][path] = scope['runtime_source_changes'][path]['candidate_sha256']
    result['rust_source_sha256'].update(scope['added_runtime_source'])
    result['compile_time_data_sha256'].update(scope['additional_compiled_source_contracts'])
    result['compile_time_data_sha256']['almanac/index-catalog.json'] = catalog_sha
    if (len(result['rust_source_sha256']) != 101 or len(result['compile_time_data_sha256']) != 151
            or not all(re.fullmatch('[0-9a-f]{64}', v) for v in [catalog_sha, logical_sha])):
        raise ValueError('Unexpected compiled dependency inventory')
    result.update(schema='osw.azores-2009-section-compiled-inputs.v1',
                  parent_logical_sha256=projection.PARENT, saved_candidate_logical_sha256=logical_sha,
                  saved_candidate_catalog_sha256=catalog_sha)
    return result


def engine_manifest(parent, inventory, scope, replacements, *, logical_sha, wasm_sha,
                    compiler, parent_manifest_sha, source_commit, dependency_proof):
    scope_check(scope)
    if (parent_manifest_sha != PARENT_MANIFEST_SHA or parent['sha256'].get(WASM) != PARENT_WASM_SHA
            or KEY in parent or not compiler.startswith('rustc 1.95.0 ')
            or not re.fullmatch('[0-9a-f]{64}', wasm_sha)
            or not re.fullmatch('[0-9a-f]{40}', source_commit)
            or inventory['saved_candidate_logical_sha256'] != logical_sha):
        raise ValueError('Exact matching-engine identities required')
    actual = dependency_proof.get('production_dependencies', [])
    allowed = set(inventory['rust_source_sha256']) | set(inventory['compile_time_data_sha256'])
    required = {ADAPTER, 'almanac/index-catalog.json'} | CONTRACTS | {p for p in CHANGES if p.endswith('.rs')}
    if (dependency_proof.get('compiled_catalog_dependency_verified') is not True
            or dependency_proof.get('test_only_fixtures_compiled') != 0
            or len(actual) != len(set(actual)) or len(actual) != dependency_proof.get('production_dependency_count')
            or not required <= set(actual) or not set(actual) <= allowed):
        raise ValueError('Actual production dependencies differ from scoped compiler inputs')
    parts = {p for p in replacements if re.fullmatch(r'almanac/query-parts/\d{6}-[0-9a-f]{64}\.bin', p)}
    changes = CHANGES | GENERATED | parts
    required_replacements = GENERATED | CHANGES | CONTRACTS | {ADAPTER}
    if not required_replacements <= set(replacements):
        raise ValueError('Incomplete compiled source or generated candidate identity')
    for path, digest in replacements.items():
        if (not re.fullmatch('[0-9a-f]{64}', digest)
                or path in parent['sha256'] and parent['sha256'][path] != digest and path not in changes):
            raise ValueError('Unrelated installed pin would change: ' + path)
    for path, row in scope['runtime_source_changes'].items():
        if replacements[path] != row['candidate_sha256']:
            raise ValueError('Runtime source replacement differs: ' + path)
    for path, digest in {**scope['added_runtime_source'], **scope['additional_compiled_source_contracts']}.items():
        if replacements[path] != digest:
            raise ValueError('New compiled source replacement differs: ' + path)
    result = copy.deepcopy(parent)
    result['sha256'].update(replacements)
    result['sha256'][WASM] = wasm_sha
    result['rustc'] = compiler
    result[KEY] = {'schema': 'osw.azores-2009-section-engine-delivery.v1',
        'parent_engine_manifest_sha256': parent_manifest_sha, 'parent_logical_sha256': projection.PARENT,
        'previous_binary_sha256': PARENT_WASM_SHA, 'matching_binary_sha256': wasm_sha,
        'logical_sha256': logical_sha, 'source_commit': source_commit,
        'runtime_source_changes': copy.deepcopy(scope['runtime_source_changes']),
        'dependency_proof': copy.deepcopy(dependency_proof), 'new_physical_dimensions': 0}
    if any(result[k] != parent[k] for k in parent if k not in {'sha256', 'rustc'}):
        raise ValueError('An inherited complete engine namespace changed')
    return result
