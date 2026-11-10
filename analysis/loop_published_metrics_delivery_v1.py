"""Pure compatible delivery projections; callers supply cloud-loaded data bytes."""
import copy
import gzip
import hashlib
import json
import re
from collections import Counter

import loop_published_metrics_query_v1 as context
from current_gap_index_extension import extend
from query_packet import descriptors
from south_java_model_context_projection_v1 import projects

DASHBOARD = 'research/ocean-motion-dashboard.json'
CATALOG = 'almanac/index-catalog.json'
WASM = 'almanac/query-engine.wasm'
MANIFEST = 'almanac/query-engine.manifest.json'
INDEX = {CATALOG, 'almanac/index-sources.json', 'almanac/index-data.json.gz'}
GENERATED = INDEX | {DASHBOARD, 'almanac/query-data.json'}
DOCUMENTS = {context.FACTS, context.PREPARATION, context.FILE,
             'research/loop-published-metrics-query-preparation-v1.json'}
RECEIPT = 'loop_published_metrics_delivery_v1'
OWNER_FIELDS = {field for field, _ in context.OWNER_FIELDS.values()} | {
    'capabilities', 'evidence_links', 'source_ids', 'linked_source_count', 'section_fingerprints', 'fingerprint'}
CAPABILITIES = {cap for _, cap in context.OWNER_FIELDS.values()}
PARENT_LOGICAL_SHA = '950338d2a0be3f479c93879c03a4b2ed6b8a1293ee6b739142f0281db3f94da1'
PARENT_LOGICAL_BYTES = 189948400
PARENT_MANIFEST_SHA = 'f030763e7523bfa0bccabe2a9d5ce395899f6c0f7f1b957affbc526673234b49'
PARENT_WASM_SHA = 'bd26345cd5cb1adf2f9ac4d3b26a28ac6e4aed8874e5304eaedb1c77336635c7'


def sha(raw): return hashlib.sha256(raw).hexdigest()
def encoded(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(',', ':')) + '\n').encode()
def fingerprint(value): return sha(encoded(value))


def verify_owner(before, after):
    changed = {key for key in set(before) | set(after) if fingerprint(before.get(key)) != fingerprint(after.get(key))}
    if changed - OWNER_FIELDS: raise ValueError('Physical or unrelated owner field changed')
    for name in ['capabilities', 'section_fingerprints']:
        allowed = CAPABILITIES if name == 'capabilities' else {'published_contour_events'}
        if set(after[name]) - set(before[name]) - allowed: raise ValueError('Undeclared owner evidence field')
        for key, value in before[name].items():
            if key not in allowed and fingerprint(after[name].get(key)) != fingerprint(value):
                raise ValueError('Prior physical capability/fingerprint changed')
    for name in ['source_ids', 'evidence_links']:
        if name == 'source_ids':
            if not set(before[name]) <= set(after[name]): raise ValueError('Prior source reference erased')
        elif after[name][:len(before[name])] != before[name]: raise ValueError('Prior evidence link changed')
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
    old = {row['id']: row for row in before}; new = {row['id']: row for row in after}
    entries = {row['id']: row for row in dashboard['entries']}
    if (len(old) != len(before) or len(new) != len(after) or len(entries) != len(dashboard['entries'])
            or set(old) != set(new) or set(old) != set(entries) or context.TARGET not in old
            or dashboard['counts'] != dict(Counter(row['type'] for row in before))):
        raise ValueError('Dashboard owner/identity/count coverage differs')
    for key in old:
        if not projects(old[key], entries[key]): raise ValueError('Parent dashboard projection differs')
        if key != context.TARGET and fingerprint(old[key]) != fingerprint(new[key]):
            raise ValueError('Other dashboard object changed')
    changed = verify_owner(old[context.TARGET], new[context.TARGET])
    updated = copy.deepcopy(dashboard)
    replacement = copy.deepcopy(entries[context.TARGET])
    for key in changed: replacement[key] = copy.deepcopy(new[context.TARGET][key])
    if not projects(new[context.TARGET], replacement): raise ValueError('Updated dashboard does not project owner')
    updated['entries'] = [replacement if row['id'] == context.TARGET else row for row in updated['entries']]
    updated['snapshot_fingerprint'] = context.fingerprint(updated['entries'])
    if RECEIPT in updated: raise ValueError('Dashboard delivery already applied')
    updated[RECEIPT] = {'parent_source_sha256': sha(raw.encode()), 'changed_owner_ids': [context.TARGET],
                        'physical_dimension_admission': False}
    body = (json.dumps(updated, ensure_ascii=False, indent=2) + '\n').encode()
    result = copy.deepcopy(manifest)
    result['dashboard_receipt'] = {'source_file': DASHBOARD, 'source_sha256': sha(body), 'source_json': body.decode()}
    result['input_sha256'][DASHBOARD] = sha(body)
    return result, body, {'changed_owner_fields': changed, 'unchanged_dashboard_entries': len(old) - 1,
                           'parent_dashboard_sha256': sha(raw.encode()), 'candidate_dashboard_sha256': sha(body)}


def candidate(bundle, contract):
    """Copy only changed containers; leave the supplied parent mapping untouched."""
    if bundle.get('schema') != 'osw.query-bundle.v1' or RECEIPT in bundle['manifest']:
        raise ValueError('Unmodified compatible parent bundle required')
    before = bundle['collections']
    counts = {name: len(rows) for name, rows in before.items()}
    hashes = {name: fingerprint(rows) for name, rows in before.items()}
    rows = dict(before)
    context.append(rows, contract)
    affected = set(context.OWNER_FIELDS) | {'sources', 'objects'}
    for name, old in before.items():
        if name not in affected and fingerprint(rows[name]) != hashes[name]: raise ValueError('Prior collection changed')
        if name in affected - {'objects'} and fingerprint(rows[name][:len(old)]) != hashes[name]:
            raise ValueError('Prior collection prefix changed')
    if fingerprint([r for r in before['objects'] if r['id'] != context.TARGET]) != fingerprint(
            [r for r in rows['objects'] if r['id'] != context.TARGET]): raise ValueError('Other objects changed')
    manifest, dashboard, projection = dashboard_projection(bundle['manifest'], before['objects'], rows['objects'])
    manifest[RECEIPT] = {'contract_sha256': sha(context.encoded(contract)),
                         'source_input_sha256': copy.deepcopy(contract['input_sha256']),
                         'physical_dimension_admission': False}
    result = {**bundle, 'manifest': manifest, 'collections': rows}
    audit = {'parent_collection_counts': counts, 'candidate_collection_counts': {n: len(r) for n, r in rows.items()},
             'prior_collection_hashes': hashes, 'prior_collection_prefixes_preserved': True,
             'other_objects_preserved': len(before['objects']) - 1, 'dashboard_projection': projection,
             'new_evidence_records': 14, 'new_source_records': len(rows['sources']) - counts.get('sources', 0)}
    return result, dashboard, audit


def source_index(catalog, compressed, registry, documents, dashboard):
    if set(documents) != DOCUMENTS: raise ValueError('Exact four new source documents required')
    if sha(compressed) != catalog['compressed_sha256']: raise ValueError('Parent compressed index differs')
    raw = gzip.decompress(compressed)
    if len(raw) != catalog['bundle_bytes'] or sha(raw) != catalog['bundle_sha256']:
        raise ValueError('Parent logical index differs')
    additions = {**documents, DASHBOARD: dashboard}
    updated, corpus, registry, audit = extend(catalog, json.loads(raw), registry, additions)
    if set(audit['replaced_source_paths']) - {DASHBOARD}: raise ValueError('Historical source replaced')
    if set(audit['added_source_paths']) != DOCUMENTS: raise ValueError('Sources already indexed or new inventory differs')
    body = encoded(corpus); packed = gzip.compress(body, compresslevel=9, mtime=0); registry_raw = encoded(registry)
    updated.update(bundle_sha256=sha(body), bundle_bytes=len(body), compressed_sha256=sha(packed), compressed_bytes=len(packed))
    updated['input_sha256'] = {**updated.get('input_sha256', {}),
                              **{p: sha(b) for p, b in additions.items()}, 'almanac/index-sources.json': sha(registry_raw)}
    return {CATALOG: encoded(updated), 'almanac/index-data.json.gz': packed,
            'almanac/index-sources.json': registry_raw}, audit


def packet_manifest(manifest, generated, documents, audit):
    if set(generated) != INDEX or set(documents) != DOCUMENTS or RECEIPT not in manifest:
        raise ValueError('Appended manifest and exact index/documents required')
    updated = copy.deepcopy(manifest)
    updated['input_sha256'].update({p: sha(b) for p, b in {**generated, **documents}.items()})
    updated[RECEIPT]['source_index_audit'] = copy.deepcopy(audit)
    return updated


def compile_inventory(original, catalog_sha, logical_sha):
    if not all(re.fullmatch('[0-9a-f]{64}', value) for value in [catalog_sha, logical_sha]):
        raise ValueError('Exact generated catalog and packet identities required')
    result = copy.deepcopy(original)
    if CATALOG not in result['compile_time_data_sha256']: raise ValueError('No compiled-catalog dependency')
    result['compile_time_data_sha256'][CATALOG] = catalog_sha
    result['saved_candidate_catalog_sha256'] = catalog_sha
    result['saved_candidate_logical_sha256'] = logical_sha
    return result


def engine_manifest(parent, original_inventory, inventory, replacements, packet, *, wasm_sha, compiler,
                    parent_manifest_sha, source_commit, dependency_proof):
    """Permit one compiled-data change and exact declared derived/source updates."""
    if (parent.get('schema') != 'osw.query-engine-manifest.v1' or parent.get('abi_version') != 1
            or RECEIPT in parent or not compiler.startswith('rustc 1.95.0 ')
            or not re.fullmatch('[0-9a-f]{40}', source_commit)
            or not all(re.fullmatch('[0-9a-f]{64}', h) for h in [wasm_sha, parent_manifest_sha])):
        raise ValueError('Exact matching-engine parent and compiler identity required')
    expected = compile_inventory(original_inventory, inventory['saved_candidate_catalog_sha256'], packet['logical_sha256'])
    if encoded(expected) != encoded(inventory): raise ValueError('Undeclared compile input changes')
    for name, digest in original_inventory['rust_source_sha256'].items():
        if parent['sha256'].get(name) != digest: raise ValueError('Compiled runtime source changed')
    for name, digest in original_inventory['compile_time_data_sha256'].items():
        if parent['sha256'].get(name) != digest: raise ValueError('Parent compiled data custody differs')
    if (replacements.get(CATALOG) != inventory['saved_candidate_catalog_sha256']
            or dependency_proof.get('compiled_catalog_dependency_verified') is not True):
        raise ValueError('Matching compiled catalog and actual dependencies required')
    actual = dependency_proof.get('production_dependencies', [])
    allowed = set(inventory['rust_source_sha256']) | set(inventory['compile_time_data_sha256'])
    if (len(actual) != len(set(actual)) or len(actual) != dependency_proof.get('production_dependency_count')
            or not {CATALOG, 'rust/osw-query/src/index_store.rs'} <= set(actual) or not set(actual) <= allowed
            or dependency_proof.get('test_only_fixtures_compiled') != 0):
        raise ValueError('Undeclared production compiler dependency')
    parts = {'almanac/' + row['path']: row['sha256'] for row in descriptors(packet)}
    contract = context.build_contract()
    reviewed = contract['input_sha256']
    required = GENERATED | DOCUMENTS | set(reviewed) | set(parts)
    if set(replacements) != required or any(not re.fullmatch('[0-9a-f]{64}', h) for h in replacements.values()):
        raise ValueError('Exact generated/source overlay inventory required')
    for name, digest in parts.items():
        if replacements[name] != digest: raise ValueError('Packet descriptor/part hash mismatch')
    for name, digest in reviewed.items():
        if replacements[name] != digest: raise ValueError('Reviewed source hash differs from contract')
    if replacements[context.FILE] != sha(context.encoded(contract)):
        raise ValueError('Query contract hash differs from exact reviewed projection')
    for name in required - GENERATED - set(parts):
        if name in parent['sha256'] and parent['sha256'][name] != replacements[name]:
            raise ValueError('Historical reviewed source would change')
    updated = copy.deepcopy(parent)
    updated['sha256'].update(replacements)
    updated['sha256'][WASM] = wasm_sha
    updated['rustc'] = compiler
    updated[RECEIPT] = {'schema': 'osw.loop-published-metrics-engine-delivery.v1',
                         'parent_engine_manifest_sha256': parent_manifest_sha,
                         'previous_binary_sha256': parent['sha256'][WASM], 'matching_binary_sha256': wasm_sha,
                         'source_commit': source_commit, 'logical_sha256': packet['logical_sha256'],
                         'changed_compile_time_data_paths': [CATALOG],
                         'runtime_sources_changed': [], 'dependency_proof': copy.deepcopy(dependency_proof),
                         'scientific_source_processing': False, 'new_physical_dimensions_admitted': 0}
    return updated
