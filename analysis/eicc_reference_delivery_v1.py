"""Pure lossless EICC delivery projections; real data is supplied only in cloud."""
import copy
import gzip
import hashlib
import json
import re
from collections import Counter

import eicc_reference_query_v1 as context
from current_gap_index_extension import extend
from query_packet import descriptors
from south_java_model_context_projection_v1 import projects

DASHBOARD = 'research/ocean-motion-dashboard.json'
CATALOG = 'almanac/index-catalog.json'
WASM = 'almanac/query-engine.wasm'
MANIFEST = 'almanac/query-engine.manifest.json'
INDEX = {CATALOG, 'almanac/index-data.json.gz', 'almanac/index-sources.json'}
GENERATED = INDEX | {DASHBOARD, 'almanac/query-data.json'}
DOCUMENTS = {context.FACTS, context.CANDIDATE, context.CALCULATION, context.PROTOCOL, context.FILE,
             'research/eicc-reference-query-preparation-v1.json',
             'research/eicc-gangopadhyay-2013-regional-reference-source-v1.json',
             'research/eicc-spring-regional-reference-protocol-v1.json'}
RECEIPT = 'eicc_reference_spectral_delivery_v1'
OWNER_SECTION = 'eicc_regional_reference_and_spectral_support'
OWNER_FIELDS = {field for field, _ in context.OWNER_FIELDS.values()} | {
    'capabilities', 'evidence_links', 'map_features', 'source_ids', 'linked_source_count',
    'section_fingerprints', 'fingerprint'}
CAPABILITIES = {cap for _, cap in context.OWNER_FIELDS.values()}
PARENT_LOGICAL_SHA = 'b4d60a69eeea0339e06088f0b1e737ef50ec2983521615dc96341dd69d736551'
PARENT_LOGICAL_BYTES = 189986194
PARENT_MANIFEST_SHA = '16e67dacdc80d9aeee09253e628f934f84685d5a6f3fe7aadb4756e319579dff'
PARENT_WASM_SHA = '5d6361f21456c023bbf2e0801dcfed14a232ff336c178ea045f581cd7989c7ae'


def encoded(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(',', ':')) + '\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def fingerprint(value):
    return sha(encoded(value))


def changed_fields(before, after):
    return {k for k in set(before) | set(after)
            if k not in before or k not in after or fingerprint(before[k]) != fingerprint(after[k])}


def verify_owner(before, after):
    changed = changed_fields(before, after)
    if changed - OWNER_FIELDS:
        raise ValueError('Physical or unrelated EICC owner field changed')
    for name, allowed in [('capabilities', CAPABILITIES), ('section_fingerprints', {OWNER_SECTION})]:
        if set(after[name]) - set(before[name]) - allowed:
            raise ValueError('Undeclared EICC owner metadata')
        for key, value in before[name].items():
            if key not in allowed and (key not in after[name] or fingerprint(after[name][key]) != fingerprint(value)):
                raise ValueError('Prior physical capability or fingerprint changed')
    for name in ['map_features', 'evidence_links', *[field for field, _ in context.OWNER_FIELDS.values()]]:
        prior = before.get(name, [])
        if fingerprint(after[name][:len(prior)]) != fingerprint(prior):
            raise ValueError('Prior EICC reference, link or feature changed')
    if not set(before['source_ids']) <= set(after['source_ids']):
        raise ValueError('Prior EICC source reference erased')
    return sorted(changed)


def dashboard_projection(manifest, before, after):
    receipt = manifest.get('dashboard_receipt', {})
    raw = receipt.get('source_json')
    if (not isinstance(raw, str) or receipt.get('source_file') != DASHBOARD
            or receipt.get('source_sha256') != sha(raw.encode())
            or manifest.get('input_sha256', {}).get(DASHBOARD) != sha(raw.encode())):
        raise ValueError('Parent dashboard custody differs')
    dashboard = json.loads(raw)
    if dashboard.get('schema') != 'osw.motion-dashboard.v1' or dashboard.get('fingerprint_version') != 2:
        raise ValueError('Unsupported parent dashboard')
    old, new = ({r['id']: r for r in rows} for rows in [before, after])
    entries = {r['id']: r for r in dashboard['entries']}
    if (len(old) != len(before) or len(new) != len(after) or len(entries) != len(dashboard['entries'])
            or set(old) != set(new) or set(old) != set(entries) or context.TARGET not in old
            or dashboard['counts'] != dict(Counter(r['type'] for r in before)) or RECEIPT in dashboard):
        raise ValueError('Dashboard identity/count coverage or delivery history differs')
    for ident in old:
        if not projects(old[ident], entries[ident]):
            raise ValueError('Parent dashboard does not project owner')
        if ident != context.TARGET and fingerprint(old[ident]) != fingerprint(new[ident]):
            raise ValueError('Other dashboard owner changed')
    changed = verify_owner(old[context.TARGET], new[context.TARGET])
    updated = copy.deepcopy(dashboard)
    replacement = copy.deepcopy(entries[context.TARGET])
    for key in changed:
        replacement[key] = copy.deepcopy(new[context.TARGET][key])
    if not projects(new[context.TARGET], replacement):
        raise ValueError('Updated dashboard projection differs')
    updated['entries'] = [replacement if r['id'] == context.TARGET else r for r in updated['entries']]
    updated['snapshot_fingerprint'] = context.fingerprint(updated['entries'])
    updated[RECEIPT] = {'parent_source_sha256': sha(raw.encode()), 'changed_owner_ids': [context.TARGET],
                        'new_physical_dimensions_admitted': 0}
    body = (json.dumps(updated, ensure_ascii=False, indent=2) + '\n').encode()
    result = copy.deepcopy(manifest)
    result['dashboard_receipt'] = {'source_file': DASHBOARD, 'source_sha256': sha(body), 'source_json': body.decode()}
    result['input_sha256'][DASHBOARD] = sha(body)
    return result, body, {'changed_owner_fields': changed, 'unchanged_dashboard_entries': len(old) - 1,
                         'parent_dashboard_sha256': sha(raw.encode()), 'candidate_dashboard_sha256': sha(body)}


def candidate(bundle, contract):
    if bundle.get('schema') != 'osw.query-bundle.v1' or RECEIPT in bundle['manifest']:
        raise ValueError('Unmodified compatible parent bundle required')
    before = bundle['collections']
    owner = next(r for r in before['objects'] if r['id'] == context.TARGET)
    if OWNER_SECTION in owner['section_fingerprints']:
        raise ValueError('Partial or prior EICC delivery marker already exists')
    hashes = {name: fingerprint(rows) for name, rows in before.items()}
    counts = {name: len(rows) for name, rows in before.items()}
    rows = dict(before)
    context.append(rows, contract)
    append_only = set(context.OWNER_FIELDS) | {'sources'}
    affected = append_only | {'objects', 'route_decisions'}
    if set(rows) != set(before) | set(context.OWNER_FIELDS):
        raise ValueError('Unexpected candidate collection set')
    for name, old in before.items():
        if fingerprint(before[name]) != hashes[name]:
            raise ValueError('Caller-owned parent changed during projection')
        if name not in affected and fingerprint(rows[name]) != hashes[name]:
            raise ValueError('Prior scientific collection changed')
        if name in append_only and fingerprint(rows[name][:len(old)]) != hashes[name]:
            raise ValueError('Prior append-only collection prefix changed')
    if fingerprint([r for r in rows['objects'] if r['id'] != context.TARGET]) != fingerprint(
            [r for r in before['objects'] if r['id'] != context.TARGET]):
        raise ValueError('Other current or eddy owner changed')
    old_decisions = {r['id']: r for r in before['route_decisions']}
    new_decisions = {r['id']: r for r in rows['route_decisions']}
    if (len(old_decisions) != len(before['route_decisions'])
            or len(new_decisions) != len(rows['route_decisions'])
            or set(old_decisions) != set(new_decisions)):
        raise ValueError('Editorial route decision identity set changed')
    changed_decisions = []
    for ident, old in old_decisions.items():
        new = new_decisions[ident]
        if old.get('entity_id') != context.TARGET:
            if fingerprint(old) != fingerprint(new):
                raise ValueError('Other editorial route decision changed')
        else:
            if fingerprint(new.get('prior_route_decision')) != fingerprint(old):
                raise ValueError('Exact prior EICC route decision not retained')
            changed_decisions.append(ident)
    if len(changed_decisions) != 1:
        raise ValueError('Exactly one EICC editorial route decision required')
    manifest, dashboard, projection = dashboard_projection(bundle['manifest'], before['objects'], rows['objects'])
    manifest[RECEIPT] = {'contract_sha256': sha(context.encoded(contract)),
                         'source_input_sha256': copy.deepcopy(contract['input_sha256']),
                         'changed_editorial_route_decision_ids': changed_decisions,
                         'new_physical_dimensions_admitted': 0}
    return {**bundle, 'manifest': manifest, 'collections': rows}, dashboard, {
        'parent_collection_counts': counts, 'candidate_collection_counts': {n: len(r) for n, r in rows.items()},
        'prior_collection_hashes': hashes, 'prior_append_only_prefixes_preserved': True,
        'other_objects_preserved': len(before['objects']) - 1,
        'prior_editorial_route_decision_retained': True, 'changed_editorial_route_decision_ids': changed_decisions,
        'dashboard_projection': projection, 'new_evidence_records': 15,
        'new_source_records': len(rows['sources']) - counts.get('sources', 0)}


def source_index(catalog, compressed, registry, documents, dashboard):
    if (set(documents) != DOCUMENTS or sha(compressed) != catalog['compressed_sha256']
            or len(compressed) != catalog['compressed_bytes']):
        raise ValueError('Exact source documents and parent index required')
    raw = gzip.decompress(compressed)
    if len(raw) != catalog['bundle_bytes'] or sha(raw) != catalog['bundle_sha256']:
        raise ValueError('Parent logical index differs')
    additions = {**documents, DASHBOARD: dashboard}
    updated, corpus, registry, audit = extend(catalog, json.loads(raw), registry, additions)
    if set(audit['replaced_source_paths']) - {DASHBOARD} or set(audit['added_source_paths']) != DOCUMENTS:
        raise ValueError('Historical source replaced or already-indexed delivery source')
    body = encoded(corpus)
    packed = gzip.compress(body, compresslevel=9, mtime=0)
    registry_raw = encoded(registry)
    updated.update(bundle_sha256=sha(body), bundle_bytes=len(body), compressed_sha256=sha(packed), compressed_bytes=len(packed))
    updated['input_sha256'] = {**updated.get('input_sha256', {}), **{p: sha(b) for p, b in additions.items()},
                              'almanac/index-sources.json': sha(registry_raw)}
    return {CATALOG: encoded(updated), 'almanac/index-data.json.gz': packed,
            'almanac/index-sources.json': registry_raw}, audit


def packet_manifest(manifest, generated, documents, audit):
    if set(generated) != INDEX or set(documents) != DOCUMENTS or RECEIPT not in manifest:
        raise ValueError('Exact appended manifest, index and documents required')
    result = copy.deepcopy(manifest)
    result['input_sha256'].update({p: sha(b) for p, b in {**generated, **documents}.items()})
    result[RECEIPT]['source_index_audit'] = copy.deepcopy(audit)
    result[RECEIPT]['parent_logical_sha256'] = PARENT_LOGICAL_SHA
    return result


def compile_inventory(original, parent_manifest, catalog_sha, logical_sha):
    if not all(re.fullmatch('[0-9a-f]{64}', s) for s in [catalog_sha, logical_sha]):
        raise ValueError('Exact candidate catalog and logical hashes required')
    if CATALOG not in original['compile_time_data_sha256']:
        raise ValueError('Original compiler catalog dependency missing')
    for name, sha256 in original['rust_source_sha256'].items():
        if parent_manifest['sha256'].get(name) != sha256:
            raise ValueError('Compiled runtime source changed')
    for name, sha256 in original['compile_time_data_sha256'].items():
        if name != CATALOG and parent_manifest['sha256'].get(name) != sha256:
            raise ValueError('Parent immutable compiled data differs')
    parent_catalog = parent_manifest['sha256'].get(CATALOG, '')
    if not re.fullmatch('[0-9a-f]{64}', parent_catalog):
        raise ValueError('Installed parent catalog identity missing')
    data = copy.deepcopy(original['compile_time_data_sha256'])
    data[CATALOG] = catalog_sha
    return {'schema': 'osw.eicc-reference-compiled-inputs.v1',
            'original_inventory_fingerprint': fingerprint(original),
            'parent_catalog_sha256': parent_catalog, 'parent_logical_sha256': PARENT_LOGICAL_SHA,
            'saved_candidate_catalog_sha256': catalog_sha, 'saved_candidate_logical_sha256': logical_sha,
            'rust_source_sha256': copy.deepcopy(original['rust_source_sha256']),
            'compile_time_data_sha256': data,
            'excluded_test_only_data_references': copy.deepcopy(original['excluded_test_only_data_references'])}


def engine_manifest(parent, original_inventory, inventory, replacements, source_pins, packet, *,
                    wasm_sha, compiler, parent_manifest_sha, source_commit, dependency_proof):
    if (parent.get('schema') != 'osw.query-engine-manifest.v1' or parent.get('abi_version') != 1
            or RECEIPT in parent or not compiler.startswith('rustc 1.95.0 ')
            or not re.fullmatch('[0-9a-f]{40}', source_commit)
            or not re.fullmatch('[0-9a-f]{64}', wasm_sha)
            or parent_manifest_sha != PARENT_MANIFEST_SHA
            or parent.get('sha256', {}).get(WASM) != PARENT_WASM_SHA):
        raise ValueError('Exact matching parent/build identities required')
    expected = compile_inventory(original_inventory, parent, replacements.get(CATALOG, ''), packet['logical_sha256'])
    if encoded(inventory) != encoded(expected):
        raise ValueError('Undeclared compiler-input changes')
    actual = dependency_proof.get('production_dependencies', [])
    allowed = set(inventory['rust_source_sha256']) | set(inventory['compile_time_data_sha256'])
    if (dependency_proof.get('compiled_catalog_dependency_verified') is not True
            or dependency_proof.get('test_only_fixtures_compiled') != 0
            or len(actual) != len(set(actual)) or len(actual) != dependency_proof.get('production_dependency_count')
            or not {CATALOG, 'rust/osw-query/src/index_store.rs'} <= set(actual) or not set(actual) <= allowed):
        raise ValueError('Actual compiler dependency proof differs')
    parts = {'almanac/' + p['path']: p['sha256'] for p in descriptors(packet)}
    if set(source_pins) & (GENERATED | set(parts) | {WASM, MANIFEST}):
        raise ValueError('Source inventory includes generated outputs')
    if not DOCUMENTS <= set(source_pins):
        raise ValueError('Source inventory omits indexed delivery documents')
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
        if path in parent['sha256'] and parent['sha256'][path] != replacements[path]:
            raise ValueError('Historical engine source pin would change')
    result = copy.deepcopy(parent)
    result['sha256'].update(replacements)
    result['sha256'][WASM] = wasm_sha
    result['rustc'] = compiler
    result[RECEIPT] = {'schema': 'osw.eicc-reference-engine-delivery.v1',
                       'parent_engine_manifest_sha256': parent_manifest_sha,
                       'previous_binary_sha256': parent['sha256'][WASM], 'matching_binary_sha256': wasm_sha,
                       'source_commit': source_commit, 'logical_sha256': packet['logical_sha256'],
                       'changed_compile_time_data_paths': [CATALOG], 'runtime_sources_changed': [],
                       'dependency_proof': copy.deepcopy(dependency_proof),
                       'new_physical_dimensions_admitted': 0}
    return result
