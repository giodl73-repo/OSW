"""Scoped matching-engine and phase custody for the complete EICC integration."""
import copy
import json
import re

import eicc_reference_delivery_v1 as prior
import eicc_reference_projection_v3 as projection
import eicc_reference_query_v1 as context
from eicc_reference_delivery_v1 import (
    CATALOG, DASHBOARD, DOCUMENTS, GENERATED, INDEX, MANIFEST, PARENT_LOGICAL_BYTES,
    PARENT_LOGICAL_SHA, PARENT_MANIFEST_SHA, PARENT_WASM_SHA, RECEIPT, WASM,
    encoded, fingerprint, packet_manifest, sha, source_index,
)
from query_packet import descriptors

SCOPE = 'research/eicc-reference-runtime-scope-v5.json'
RUNTIME = {'rust/osw-query/src/' + name for name in ['planning.rs', 'current_gap_admissions.rs', 'seasons_data.rs', 'atlas_data.rs', 'madagascar_coastal_curve.rs', 'nwasc_reference_route.rs']}
PRESENTATION = {'almanac/reference-routes.js', 'almanac/reference-route-atlas.js'}
candidate = projection.candidate


def scope_custody(scope, source_raw, source_pin):
    """Bind exact source bytes and decoded semantics without conflating hashes."""
    try:
        decoded = json.loads(source_raw)
    except (ValueError, UnicodeError) as error:
        raise ValueError('Invalid runtime/UI scope source JSON') from error
    if source_pin != sha(source_raw) or encoded(decoded) != encoded(scope):
        raise ValueError('Runtime/UI scope source bytes or semantics differ')
    return {'source_sha256': source_pin, 'canonical_sha256': sha(encoded(scope))}


def verify_candidate_identity(packet):
    """The guard correction must not alter the already preserved data payload."""
    if (type(packet.get('logical_byte_length')) is not int
            or packet['logical_byte_length'] != 190404811
            or packet.get('logical_sha256') != '93c7c184e547ad0c2801ff2183cc5f88f2e11f6150b69b7583fc2f0db05ab696'):
        raise ValueError('Candidate data must remain byte-identical to the v3 candidate')


def checked_scope(scope):
    if (scope.get('schema') != 'osw.eicc-reference-runtime-scope.v5'
            or set(scope.get('runtime_source_changes', {})) != RUNTIME
            or set(scope.get('presentation_source_changes', {})) != PRESENTATION
            or scope.get('changed_compile_time_data_paths') != [CATALOG]):
        raise ValueError('Exact reviewed runtime/UI source scope required')
    changes = {**scope['runtime_source_changes'], **scope['presentation_source_changes']}
    for path, change in changes.items():
        if (not all(re.fullmatch('[0-9a-f]{64}', change.get(key, '')) for key in ['parent_sha256', 'candidate_sha256'])
                or change['parent_sha256'] == change['candidate_sha256']
                or not change.get('archive_path', '').startswith('research/eicc-reference-')
                or any(part in ['', '.', '..'] for part in change['archive_path'].split('/'))):
            raise ValueError('Source change/archive identity differs: ' + path)
    return changes


def compile_inventory(original, parent, catalog_sha, logical_sha, scope):
    if (len(original['rust_source_sha256']) != 98 or len(original['compile_time_data_sha256']) != 144
            or len(original['excluded_test_only_data_references']) != 6):
        raise ValueError('Original compiler inventory cardinality differs')
    result = prior.compile_inventory(original, parent, catalog_sha, logical_sha)
    changes = checked_scope(scope)
    for path, change in changes.items():
        if parent['sha256'].get(path) != change['parent_sha256']:
            raise ValueError('Declared source differs from installed parent: ' + path)
        if path in RUNTIME:
            if original['rust_source_sha256'].get(path) != change['parent_sha256']:
                raise ValueError('Original runtime compiler pin differs: ' + path)
            result['rust_source_sha256'][path] = change['candidate_sha256']
    result['schema'] = 'osw.eicc-reference-compiled-inputs.v7'
    result['runtime_source_changes'] = copy.deepcopy(scope['runtime_source_changes'])
    result['presentation_source_changes'] = copy.deepcopy(scope['presentation_source_changes'])
    result['runtime_scope_sha256'] = sha(encoded(scope))
    return result


def engine_manifest(parent, original_inventory, inventory, replacements, source_pins, packet, scope, *,
                    wasm_sha, compiler, parent_manifest_sha, source_commit, dependency_proof):
    if (parent.get('schema') != 'osw.query-engine-manifest.v1' or parent.get('abi_version') != 1
            or RECEIPT in parent or not compiler.startswith('rustc 1.95.0 ')
            or not re.fullmatch('[0-9a-f]{40}', source_commit) or not re.fullmatch('[0-9a-f]{64}', wasm_sha)
            or parent_manifest_sha != PARENT_MANIFEST_SHA or parent.get('sha256', {}).get(WASM) != PARENT_WASM_SHA):
        raise ValueError('Exact matching parent/build identities required')
    expected = compile_inventory(original_inventory, parent, replacements.get(CATALOG, ''), packet['logical_sha256'], scope)
    if encoded(inventory) != encoded(expected): raise ValueError('Undeclared compiler-input changes')
    changes = checked_scope(scope)
    for path, change in changes.items():
        if source_pins.get(path) != change['candidate_sha256'] or source_pins.get(change['archive_path']) != change['parent_sha256']:
            raise ValueError('Candidate source or archived parent bytes missing: ' + path)
        if change.get('executed_v2_archive_path') and source_pins.get(change['executed_v2_archive_path']) != change.get('working_branch_parent_sha256'):
            raise ValueError('Executed v2 planning source archive differs')
        if change.get('executed_v4_archive_path') and source_pins.get(change['executed_v4_archive_path']) != change.get('working_branch_v4_sha256'):
            raise ValueError('Executed v4 NwASC source archive differs')
    custody = scope_custody(scope, (context.ROOT / SCOPE).read_bytes(), source_pins.get(SCOPE))
    if scope.get('prior_scope_file') and source_pins.get(scope['prior_scope_file']) != scope.get('prior_scope_sha256'):
        raise ValueError('Prior source scope is not preserved')
    for relocation in scope.get('historical_source_relocations', []):
        if source_pins.get(relocation['archive_path']) != relocation['historical_sha256']:
            raise ValueError('Historical source relocation is not pinned')
    if source_pins.get(projection.MODULE) != sha((context.ROOT / projection.MODULE).read_bytes()):
        raise ValueError('Actual admitted-source projection producer missing')
    actual = dependency_proof.get('production_dependencies', [])
    allowed = set(inventory['rust_source_sha256']) | set(inventory['compile_time_data_sha256'])
    if (dependency_proof.get('compiled_catalog_dependency_verified') is not True
            or dependency_proof.get('test_only_fixtures_compiled') != 0
            or len(actual) != len(set(actual)) or len(actual) != dependency_proof.get('production_dependency_count')
            or not (RUNTIME | {CATALOG, 'rust/osw-query/src/index_store.rs'}) <= set(actual)
            or not set(actual) <= allowed):
        raise ValueError('Actual compiler dependency proof differs')
    parts = {'almanac/' + p['path']: p['sha256'] for p in descriptors(packet)}
    if set(source_pins) & (GENERATED | set(parts) | {WASM, MANIFEST}) or not DOCUMENTS <= set(source_pins):
        raise ValueError('Source inventory omits indexed documents or includes generated files')
    contract = context.build_contract()
    if any(source_pins.get(path) != pin for path, pin in contract['input_sha256'].items()):
        raise ValueError('Source inventory omits reviewed query inputs')
    if source_pins.get(context.FILE) != sha(context.encoded(contract)): raise ValueError('Prepared query contract differs')
    required = GENERATED | DOCUMENTS | set(source_pins) | set(parts)
    if (set(replacements) != required or any(not re.fullmatch('[0-9a-f]{64}', h) for h in replacements.values())
            or any(replacements[p] != h for p, h in parts.items())
            or any(replacements[p] != h for p, h in source_pins.items())):
        raise ValueError('Generated/source overlay inventory differs')
    for path in required - GENERATED - set(parts):
        if path in parent['sha256'] and parent['sha256'][path] != replacements[path] and path not in changes:
            raise ValueError('Unrelated historical engine source pin would change: ' + path)
    result = copy.deepcopy(parent)
    result['sha256'].update(replacements); result['sha256'][WASM] = wasm_sha; result['rustc'] = compiler
    result[RECEIPT] = {'schema': 'osw.eicc-reference-engine-delivery.v7',
        'parent_engine_manifest_sha256': parent_manifest_sha,
        'previous_binary_sha256': parent['sha256'][WASM], 'matching_binary_sha256': wasm_sha,
        'source_commit': source_commit, 'logical_sha256': packet['logical_sha256'],
        'changed_compile_time_data_paths': [CATALOG], 'runtime_source_changes': copy.deepcopy(scope['runtime_source_changes']),
        'presentation_source_changes': copy.deepcopy(scope['presentation_source_changes']),
        'runtime_scope_sha256': sha(encoded(scope)), 'dependency_proof': copy.deepcopy(dependency_proof),
        'runtime_scope_source_sha256': custody['source_sha256'],
        'new_physical_dimensions_admitted': 0}
    return result


def browser_phase_custody(engine, manifest, packet, generated_hashes, *, manifest_sha, source_commit):
    """Verify saved engine work before starting the separately installed browser."""
    if (engine.get('status') != 'PASS' or engine.get('stage') != 'engine_verified'
            or engine.get('source_commit') != source_commit or engine.get('browser_verified') is not False
            or engine.get('working_branch_installed') is not False
            or engine.get('rust_route_inventory_tests_passed') != 2
            or engine.get('rust_planning_tests_passed') != 6 or engine.get('native_smoke_verified') is not True
            or engine.get('engine_manifest_sha256') != manifest_sha
            or engine.get('verified_generated_sha256') != generated_hashes
            or set(engine.get('verified_generated_artifact_paths', [])) != set(generated_hashes)
            or generated_hashes.get(MANIFEST) != manifest_sha
            or generated_hashes.get(WASM) != engine.get('wasm_sha256')):
        raise ValueError('Verified engine phase/artifact custody differs')
    paths = GENERATED | {MANIFEST, WASM} | {'almanac/' + p['path'] for p in descriptors(packet)}
    if paths != set(generated_hashes): raise ValueError('Saved engine phase generated paths differ')
    receipt = manifest.get(RECEIPT, {})
    if (receipt.get('schema') != 'osw.eicc-reference-engine-delivery.v7'
            or not re.fullmatch('[0-9a-f]{64}', receipt.get('runtime_scope_source_sha256', ''))
            or receipt.get('runtime_scope_source_sha256') != manifest.get('sha256', {}).get(SCOPE)
            or receipt.get('source_commit') != source_commit or receipt.get('logical_sha256') != packet['logical_sha256']
            or receipt.get('matching_binary_sha256') != engine['wasm_sha256']
            or any(manifest.get('sha256', {}).get(path) != pin for path, pin in generated_hashes.items() if path != MANIFEST)):
        raise ValueError('Matching engine manifest/packet identities differ')
    for mode, count in [('main', 24), ('index', 25), ('snapshots', 2)]:
        parity = engine.get('native_wasm_parity', {}).get(mode, {})
        if (parity.get('status') != 'PASS' or parity.get('wasm_sha256') != engine['wasm_sha256']
                or parity.get('initialization_metadata_equal') is not True or len(parity.get('checks', [])) != count
                or any(check.get('entire_response_equal') is not True for check in parity['checks'])
                or (mode == 'index' and parity.get('mismatched_corpus_refused') is not True)):
            raise ValueError('Complete engine parity receipt missing: ' + mode)
    return {'status': 'PASS', 'source_commit': source_commit, 'generated_paths_verified': len(paths),
            'engine_manifest_sha256': manifest_sha, 'wasm_sha256': engine['wasm_sha256'],
            'logical_sha256': packet['logical_sha256'], 'browser_started': False}
