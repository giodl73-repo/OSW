"""Explicit EICC planning-source revision over the preserved v1 delivery contract."""
import copy
import re

import eicc_reference_delivery_v1 as prior
import eicc_reference_query_v1 as context
from eicc_reference_delivery_v1 import (
    CATALOG, DASHBOARD, DOCUMENTS, GENERATED, INDEX, MANIFEST, PARENT_LOGICAL_BYTES,
    PARENT_LOGICAL_SHA, PARENT_MANIFEST_SHA, PARENT_WASM_SHA, RECEIPT, WASM,
    encoded, fingerprint, packet_manifest, sha, source_index,
)
from query_packet import descriptors

PLANNING = 'rust/osw-query/src/planning.rs'
ARCHIVE = 'research/eicc-reference-planning-original-v1.rs'
SCOPE = 'research/eicc-reference-planning-runtime-scope-v2.json'
OLD_SOURCE = 'research/ocean-current-reference-path-candidates.json'


def candidate(bundle, contract):
    result, dashboard, audit = prior.candidate(bundle, contract)
    decision = next(row for row in result['collections']['route_decisions'] if row['entity_id'] == context.TARGET)
    before = decision['prior_route_decision']
    if before['source_catalog_file'] != OLD_SOURCE or before['route_ids'] != []:
        raise ValueError('Exact original EICC planning worklist with no routes required')
    source_raw = (context.ROOT / context.CANDIDATE).read_bytes()
    if sha(source_raw) != contract['input_sha256'][context.CANDIDATE]:
        raise ValueError('Reviewed candidate source bytes differ')
    decision['source_decision']['name_source_url'] = decision['source_url']
    result['manifest'][RECEIPT]['planning_revision'] = {
        'schema': 'osw.eicc-source-reference-planning-revision.v1',
        'owner_id': context.TARGET, 'source_file': context.CANDIDATE,
        'source_sha256': sha(source_raw), 'source_json': source_raw.decode('utf-8'),
        'prior_decision_json': context.encoded(before).decode('utf-8')}
    audit['planning_source_url_projection_consistent'] = True
    audit['planning_source_receipt_version'] = 'osw.eicc-source-reference-planning-revision.v1'
    return result, dashboard, audit


def compile_inventory(original, parent, catalog_sha, logical_sha, scope):
    result = prior.compile_inventory(original, parent, catalog_sha, logical_sha)
    change = scope.get('runtime_source_changes', {}).get(PLANNING, {})
    if (scope.get('schema') != 'osw.eicc-reference-planning-runtime-scope.v2'
            or set(scope.get('runtime_source_changes', {})) != {PLANNING}
            or change.get('parent_sha256') != original['rust_source_sha256'].get(PLANNING)
            or change.get('parent_sha256') != parent['sha256'].get(PLANNING)
            or change.get('archive_path') != ARCHIVE
            or not re.fullmatch('[0-9a-f]{64}', change.get('candidate_sha256', ''))
            or change['candidate_sha256'] == change['parent_sha256']):
        raise ValueError('Undeclared or inconsistent EICC planning-runtime source change')
    result['schema'] = 'osw.eicc-reference-compiled-inputs.v2'
    result['rust_source_sha256'][PLANNING] = change['candidate_sha256']
    result['runtime_source_changes'] = copy.deepcopy(scope['runtime_source_changes'])
    result['runtime_scope_sha256'] = sha(encoded(scope))
    return result


def engine_manifest(parent, original_inventory, inventory, replacements, source_pins, packet, scope, *,
                    wasm_sha, compiler, parent_manifest_sha, source_commit, dependency_proof):
    if (parent.get('schema') != 'osw.query-engine-manifest.v1' or parent.get('abi_version') != 1
            or RECEIPT in parent or not compiler.startswith('rustc 1.95.0 ')
            or not re.fullmatch('[0-9a-f]{40}', source_commit)
            or not re.fullmatch('[0-9a-f]{64}', wasm_sha)
            or parent_manifest_sha != PARENT_MANIFEST_SHA
            or parent.get('sha256', {}).get(WASM) != PARENT_WASM_SHA):
        raise ValueError('Exact matching parent/build identities required')
    expected = compile_inventory(original_inventory, parent, replacements.get(CATALOG, ''), packet['logical_sha256'], scope)
    if encoded(inventory) != encoded(expected): raise ValueError('Undeclared compiler-input changes')
    change = scope['runtime_source_changes'][PLANNING]
    if (source_pins.get(PLANNING) != change['candidate_sha256']
            or source_pins.get(ARCHIVE) != change['parent_sha256']
            or source_pins.get(SCOPE) != sha(encoded(scope))):
        raise ValueError('Explicit runtime scope or original planning-source archive missing')
    actual = dependency_proof.get('production_dependencies', [])
    allowed = set(inventory['rust_source_sha256']) | set(inventory['compile_time_data_sha256'])
    if (dependency_proof.get('compiled_catalog_dependency_verified') is not True
            or dependency_proof.get('test_only_fixtures_compiled') != 0
            or len(actual) != len(set(actual)) or len(actual) != dependency_proof.get('production_dependency_count')
            or not {CATALOG, 'rust/osw-query/src/index_store.rs', PLANNING} <= set(actual) or not set(actual) <= allowed):
        raise ValueError('Actual compiler dependency proof differs')
    parts = {'almanac/' + p['path']: p['sha256'] for p in descriptors(packet)}
    if set(source_pins) & (GENERATED | set(parts) | {WASM, MANIFEST}) or not DOCUMENTS <= set(source_pins):
        raise ValueError('Source inventory omits indexed documents or includes generated files')
    contract = context.build_contract()
    if any(source_pins.get(p) != h for p, h in contract['input_sha256'].items()):
        raise ValueError('Source inventory omits reviewed query inputs')
    if source_pins.get(context.FILE) != sha(context.encoded(contract)):
        raise ValueError('Prepared query contract source differs')
    required = GENERATED | DOCUMENTS | set(source_pins) | set(parts)
    if (set(replacements) != required or any(not re.fullmatch('[0-9a-f]{64}', h) for h in replacements.values())
            or any(replacements[p] != h for p, h in parts.items())
            or any(replacements[p] != h for p, h in source_pins.items())):
        raise ValueError('Generated/source overlay inventory differs')
    for path in required - GENERATED - set(parts):
        if path in parent['sha256'] and parent['sha256'][path] != replacements[path] and path != PLANNING:
            raise ValueError('Historical engine source pin would change')
    result = copy.deepcopy(parent)
    result['sha256'].update(replacements)
    result['sha256'][WASM] = wasm_sha
    result['rustc'] = compiler
    result[RECEIPT] = {'schema': 'osw.eicc-reference-engine-delivery.v2',
        'parent_engine_manifest_sha256': parent_manifest_sha,
        'previous_binary_sha256': parent['sha256'][WASM], 'matching_binary_sha256': wasm_sha,
        'source_commit': source_commit, 'logical_sha256': packet['logical_sha256'],
        'changed_compile_time_data_paths': [CATALOG], 'runtime_source_changes': copy.deepcopy(scope['runtime_source_changes']),
        'runtime_scope_sha256': sha(encoded(scope)), 'dependency_proof': copy.deepcopy(dependency_proof),
        'new_physical_dimensions_admitted': 0}
    return result
