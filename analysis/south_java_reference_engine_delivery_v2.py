"""Pure compiler inventory, historical custody and matching-engine overlay rules."""
import copy
import re

import south_java_reference_delivery_v1 as delivery
import south_java_reference_runtime_v1 as runtime
from eacc_connection_parent_custody_v3 import ALLOWED, ARCHIVE_ROOTS

PARENT_MANIFEST_SHA = 'a36845e583cf89ba49a1c75612da627f6d78bebacdc15fdf02574985d51d00fa'
PARENT_WASM_SHA = '569b082b354b1e376ad07bcf644a4c6e0cfc27982acaafc334396f02a3940318'
WASM = 'almanac/query-engine.wasm'
MANIFEST = 'almanac/query-engine.manifest.json'
KEY = 'south_java_reference_engine_delivery_v2'
PRESENTATION = 'eacc_regional_connection_presentation_v4'
ADAPTER = 'rust/osw-query/src/south_java_reference.rs'
SOURCE_CONTRACTS = {runtime.FILE}
FIXTURES = {'research/south-java-reference-runtime-fixture-v1.json'}
GENERATED = delivery.INDEX | {delivery.DASHBOARD, 'almanac/query-data.json', runtime.query.PAGE}


def verify_parent(parent, metadata, bindings, scope):
    """Verify every old pin, including current and archived source versions."""
    if (parent.get('schema') != 'osw.query-engine-manifest.v1' or parent.get('engine') != 'rust-osw-query-v1'
            or parent.get('abi_version') != 1 or not isinstance(parent.get('sha256'), dict)):
        raise ValueError('Exact installed parent engine required')
    by_path = {r['manifest_path']: r for r in bindings}
    if len(by_path) != len(bindings) or set(by_path) != set(ALLOWED):
        raise ValueError('Exact five historical source bindings required')
    for path, row in by_path.items():
        if (row['role'] != ALLOWED[path] or not row['archive_path'].startswith(ARCHIVE_ROOTS)
                or row['historical_commit'] != '0c2f0dc67a9ba25cbf488f634702b05f30401f2f'
                or metadata(row['archive_path']) != (row['historical_sha256'], row['historical_bytes'])
                or metadata(path) != (row['installed_path_sha256'], row['installed_path_bytes'])
                or parent['sha256'].get(path) not in {row['historical_sha256'], row['installed_path_sha256']}):
            raise ValueError('Changed historical/current source binding: ' + path)
    changes = scope['runtime_source_changes']
    if len(changes) != 9 or ADAPTER in parent['sha256']:
        raise ValueError('Nine parent changes and one previously absent adapter required')
    checked = 0; historical = []; revised = []
    for path, expected in parent['sha256'].items():
        actual, size = metadata(path)
        if path in changes:
            row = changes[path]
            if (expected != row['historical_sha256'] or actual != row['candidate_sha256']
                    or metadata(row['archive_path']) != (expected, row['bytes'])):
                raise ValueError('Scoped runtime current/archive bytes differ: ' + path)
            revised.append(path)
        elif actual == expected:
            checked += 1
        elif path in by_path and expected == by_path[path]['historical_sha256']:
            historical.append(path)  # Both versions were checked above.
        else:
            raise ValueError('Unregistered parent byte mismatch: ' + path)
    if set(revised) != set(changes):
        raise ValueError('Scoped parent runtime paths missing from installed manifest')
    return {'status': 'PASS', 'manifest_paths_verified': checked + len(historical) + len(revised),
            'historical_paths': sorted(historical), 'scoped_runtime_paths': sorted(revised),
            'all_other_current_path_matches': checked}


def compile_inventory(original, parent, scope, catalog_sha, logical_sha):
    if (len(original['rust_source_sha256']) != 99 or len(original['compile_time_data_sha256']) != 146
            or len(original['excluded_test_only_data_references']) != 8
            or original['saved_candidate_logical_sha256'] != runtime.query.PARENT
            or not all(re.fullmatch('[0-9a-f]{64}', s) for s in [catalog_sha, logical_sha])):
        raise ValueError('Exact installed compiler inventory and candidate identities required')
    sources = {p: parent['sha256'][p] for p in original['rust_source_sha256']}
    data = {p: parent['sha256'][p] for p in original['compile_time_data_sha256']}
    if sources != original['rust_source_sha256'] or data != original['compile_time_data_sha256']:
        raise ValueError('Installed compiler inventory differs from parent engine')
    changes = scope['runtime_source_changes']
    rust_changes = {p: row for p, row in changes.items() if p in sources}
    if (len(changes) != 9 or len(rust_changes) != 8
            or set(changes) - set(rust_changes) != {'almanac/reference-routes.js'}
            or set(scope['added_runtime_source']) != {ADAPTER}):
        raise ValueError('Eight exact Rust revisions and one atlas UI revision required')
    for path, row in rust_changes.items():
        if sources[path] != row['historical_sha256'] or row['candidate_sha256'] == row['historical_sha256']:
            raise ValueError('Installed source does not match declared parent: ' + path)
        sources[path] = row['candidate_sha256']
    if ADAPTER in sources or SOURCE_CONTRACTS.intersection(data):
        raise ValueError('Unexpected prior adapter/source-contract compiler dependency')
    sources.update(scope['added_runtime_source'])
    contracts = scope['additional_compiled_source_contracts']
    if set(contracts) != SOURCE_CONTRACTS:
        raise ValueError('Exact South Java runtime contract must be compiled')
    data.update(contracts)
    data[delivery.CATALOG] = catalog_sha
    excluded = copy.deepcopy(original['excluded_test_only_data_references'])
    additions = scope.get('additional_test_only_data_reference_locations', {})
    if not isinstance(excluded, dict) or set(additions) != FIXTURES or FIXTURES.intersection(excluded):
        raise ValueError('Exact retained and additional test-only dependency metadata required')
    excluded.update(copy.deepcopy(additions))
    if len(sources) != 100 or len(data) != 147 or len(excluded) != 9:
        raise ValueError('Candidate compiler inventory cardinalities differ')
    return {'schema': 'osw.south-java-reference-compiled-inputs.v2',
            'parent_logical_sha256': runtime.query.PARENT,
            'saved_candidate_logical_sha256': logical_sha, 'saved_candidate_catalog_sha256': catalog_sha,
            'rust_source_sha256': sources, 'compile_time_data_sha256': data,
            'excluded_test_only_data_references': excluded}


def engine_manifest(parent, inventory, scope, packet, replacements, source_pins, dependency_proof, *,
                    wasm_sha, compiler, parent_manifest_sha, source_commit):
    from query_packet import descriptors
    if (parent_manifest_sha != PARENT_MANIFEST_SHA or parent['sha256'].get(WASM) != PARENT_WASM_SHA
            or KEY in parent or not isinstance(parent.get(PRESENTATION), dict)
            or not compiler.startswith('rustc 1.95.0 ') or not re.fullmatch('[0-9a-f]{64}', wasm_sha)
            or not re.fullmatch('[0-9a-f]{40}', source_commit)):
        raise ValueError('Exact installed parent and matching compiler identities required')
    actual = dependency_proof.get('production_dependencies', [])
    revised_rust = {p for p in scope['runtime_source_changes'] if p.endswith('.rs')}
    allowed = set(inventory['rust_source_sha256']) | set(inventory['compile_time_data_sha256'])
    if (dependency_proof.get('compiled_catalog_dependency_verified') is not True
            or dependency_proof.get('test_only_fixtures_compiled') != 0
            or len(actual) != len(set(actual)) or len(actual) != dependency_proof.get('production_dependency_count')
            or not ({ADAPTER, delivery.CATALOG} | SOURCE_CONTRACTS | revised_rust) <= set(actual) or not set(actual) <= allowed):
        raise ValueError('Actual production compiler dependencies differ')
    parts = {'almanac/' + p['path']: p['sha256'] for p in descriptors(packet)}
    required = GENERATED | delivery.DOCUMENTS | set(source_pins) | set(parts)
    if (set(replacements) != required or set(source_pins) & (GENERATED | set(parts) | {WASM, MANIFEST})
            or any(replacements.get(p) != sha for p, sha in {**parts, **source_pins}.items())):
        raise ValueError('Exact generated/source overlay inventory required')
    for path, sha in {**inventory['rust_source_sha256'], **inventory['compile_time_data_sha256']}.items():
        if replacements.get(path, parent['sha256'].get(path)) != sha:
            raise ValueError('Matching engine does not pin its actual compiler input: ' + path)
    allowed_changes = GENERATED | set(scope['runtime_source_changes'])
    if len(scope['runtime_source_changes']) != 9 or set(scope['added_runtime_source']) != {ADAPTER}:
        raise ValueError('Exact engine runtime scope required')
    for path, row in scope['runtime_source_changes'].items():
        if (parent['sha256'].get(path) != row['historical_sha256']
                or (inventory['rust_source_sha256'].get(path) if path.endswith('.rs') else replacements.get(path)) != row['candidate_sha256']):
            raise ValueError('Runtime scope does not bind installed and compiled versions: ' + path)
    for path, sha in replacements.items():
        if not re.fullmatch('[0-9a-f]{64}', sha):
            raise ValueError('Invalid replacement hash: ' + path)
        if path in parent['sha256'] and parent['sha256'][path] != sha and path not in allowed_changes:
            raise ValueError('Unrelated parent engine pin would change: ' + path)
    if inventory['saved_candidate_logical_sha256'] != packet['logical_sha256']:
        raise ValueError('Candidate packet/compiler identity differs')
    result = copy.deepcopy(parent)
    result['sha256'].update(replacements)
    result['sha256'][WASM] = wasm_sha
    result['rustc'] = compiler
    result[KEY] = {'schema': 'osw.south-java-reference-engine-delivery.v2',
        'parent_engine_manifest_sha256': parent_manifest_sha, 'parent_logical_sha256': runtime.query.PARENT,
        'previous_binary_sha256': PARENT_WASM_SHA, 'matching_binary_sha256': wasm_sha,
        'logical_sha256': packet['logical_sha256'], 'source_commit': source_commit,
        'runtime_source_changes': copy.deepcopy(scope['runtime_source_changes']),
        'added_runtime_source': copy.deepcopy(scope['added_runtime_source']),
        'additional_compiled_source_contracts': sorted(SOURCE_CONTRACTS),
        'dependency_proof': copy.deepcopy(dependency_proof), 'new_physical_dimensions': 0}
    if any(result[k] != parent[k] for k in parent if k not in {'sha256', 'rustc'}):
        raise ValueError('All complete inherited engine namespaces must be preserved')
    return result
