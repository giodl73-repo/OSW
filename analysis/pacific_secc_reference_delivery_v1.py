"""Lossless Pacific reference packet, dashboard and source-index projections."""
import copy
import gzip
import json
from collections import Counter

import pacific_secc_publication_admission_v1 as admission
from pacific_secc_reference_runtime_v1 import query, PARENT_LOGICAL, KEY
from current_gap_index_extension import extend
from south_java_model_context_projection_v1 import projects

DASHBOARD = 'research/ocean-motion-dashboard.json'
CATALOG = 'almanac/index-catalog.json'
INDEX = {CATALOG, 'almanac/index-data.json.gz', 'almanac/index-sources.json'}
DOCUMENTS = {query.CANDIDATE, query.FILE, admission.runtime.FILE, admission.FILE,
             admission.AUDIT, admission.SELECTED, query.REVIEW, query.GEOGRAPHY}
OWNER_FIELDS = {'route_ids', 'capabilities', 'evidence_links', 'map_features', 'source_ids',
                'linked_source_count', 'section_fingerprints', 'fingerprint', 'route_url'}


def encoded(value):
    return (admission.runtime.compact(value) + '\n').encode()


def changed(before, after):
    return {k for k in set(before) | set(after) if k not in before or k not in after
            or query.fingerprint(before[k]) != query.fingerprint(after[k])}


def verify_owner(before, after):
    fields = changed(before, after)
    if fields - OWNER_FIELDS:
        raise ValueError('Physical or unrelated current owner field changed')
    for name, allowed in [('capabilities', {'reference_route'}),
                          ('section_fingerprints', {'pacific_secc_western_reference'})]:
        if changed(before[name], after[name]) - allowed:
            raise ValueError('Other owner capability or scientific fingerprint changed')
    for key in ['route_ids', 'evidence_links', 'map_features']:
        if after[key][:len(before[key])] != before[key]:
            raise ValueError('Prior owner reference or feature prefix changed')
    if not set(before['source_ids']) <= set(after['source_ids']):
        raise ValueError('Prior owner provenance erased')
    return sorted(fields)


def dashboard_projection(manifest, before, after):
    receipt = manifest.get('dashboard_receipt', {})
    raw = receipt.get('source_json')
    if (not isinstance(raw, str) or receipt.get('source_file') != DASHBOARD
            or receipt.get('source_sha256') != admission.runtime.sha(raw.encode())
            or manifest.get('input_sha256', {}).get(DASHBOARD) != receipt.get('source_sha256')):
        raise ValueError('Exact parent dashboard source required')
    dashboard = json.loads(raw)
    if (dashboard.get('schema') != 'osw.motion-dashboard.v1' or dashboard.get('fingerprint_version') != 2
            or dashboard.get('counts') != dict(Counter(r['type'] for r in before)) or KEY in dashboard):
        raise ValueError('Original dashboard schema, counts and delivery history required')
    query.checked_ids(before, 'prior owners'); query.checked_ids(after, 'candidate owners')
    query.checked_ids(dashboard['entries'], 'dashboard owners')
    old, new, entries = ({r['id']: r for r in rows} for rows in [before, after, dashboard['entries']])
    if set(old) != set(new) or set(old) != set(entries):
        raise ValueError('Dashboard/owner inventory changed')
    for ident, owner in old.items():
        if not projects(owner, entries[ident]) or (ident != query.TARGET and owner != new[ident]):
            raise ValueError('Prior dashboard projection or other owner changed')
    fields = verify_owner(old[query.TARGET], new[query.TARGET])
    result = copy.deepcopy(dashboard)
    replacement = copy.deepcopy(entries[query.TARGET])
    for field in fields:
        replacement[field] = copy.deepcopy(new[query.TARGET][field])
    if not projects(new[query.TARGET], replacement):
        raise ValueError('Candidate dashboard differs from current owner')
    result['entries'] = [replacement if r['id'] == query.TARGET else r for r in result['entries']]
    result['snapshot_fingerprint'] = query.fingerprint(result['entries'])
    result[KEY] = {'parent_source_sha256': receipt['source_sha256'], 'changed_owner_ids': [query.TARGET],
                   'new_physical_dimensions': 0, 'editorial_reference_routes': 1}
    body = (json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()
    output = copy.deepcopy(manifest)
    output['dashboard_receipt'] = {'source_file': DASHBOARD,
        'source_sha256': admission.runtime.sha(body), 'source_json': body.decode()}
    output['input_sha256'][DASHBOARD] = admission.runtime.sha(body)
    return output, body, {'changed_owner_fields': fields,
        'parent_dashboard_sha256': receipt['source_sha256'],
        'candidate_dashboard_sha256': admission.runtime.sha(body), 'other_dashboard_entries_preserved': len(old) - 1}


def candidate(bundle, document, *, parent_logical_sha256):
    if bundle.get('schema') != 'osw.query-bundle.v1' or parent_logical_sha256 != PARENT_LOGICAL:
        raise ValueError('Exact installed logical parent required')
    before = bundle['collections']
    hashes = {name: query.fingerprint(rows) for name, rows in before.items()}
    counts = {name: len(rows) for name, rows in before.items()}
    after = dict(before)
    manifest = copy.deepcopy(bundle['manifest'])
    result = admission.prepare(after, manifest, document, parent_logical_sha256=parent_logical_sha256)
    affected = {'objects', 'sources', 'reference_routes', 'route_decisions'}
    if set(before) != set(after):
        raise ValueError('Unexpected collection inventory change')
    for name, rows in before.items():
        if query.fingerprint(rows) != hashes[name]:
            raise ValueError('Caller-owned parent collection mutated')
        if name not in affected and query.fingerprint(after[name]) != hashes[name]:
            raise ValueError('Prior scientific collection changed')
    for name, delta in [('sources', 2), ('reference_routes', 1)]:
        if len(after[name]) != counts[name] + delta or query.fingerprint(after[name][:counts[name]]) != hashes[name]:
            raise ValueError('Exact appended reference/source delta required')
    for name in ['objects', 'route_decisions']:
        query.checked_ids(before[name], name); query.checked_ids(after[name], 'candidate ' + name)
        old = {r['id']: r for r in before[name]}
        new = {r['id']: r for r in after[name]}
        if set(old) != set(new):
            raise ValueError('Existing owner/decision inventory changed')
        for ident in old:
            target = ident == query.TARGET if name == 'objects' else old[ident].get('entity_id') == query.TARGET
            if not target and old[ident] != new[ident]:
                raise ValueError('Other owner/decision changed')
            if target and name == 'route_decisions' and new[ident]['prior_route_decision'] != old[ident]:
                raise ValueError('Original route decision not retained')
    manifest, dashboard, dashboard_audit = dashboard_projection(manifest, before['objects'], after['objects'])
    audit = {'status': 'CANDIDATE_PREPARED_NOT_INSTALLED', 'parent_logical_sha256': parent_logical_sha256,
        'parent_collection_counts': counts, 'candidate_collection_counts': {n: len(r) for n, r in after.items()},
        'prior_collection_fingerprints': hashes, 'unrelated_scientific_collections_preserved': True,
        'all_prior_source_and_route_rows_preserved': True, 'dashboard_projection': dashboard_audit,
        'publication_and_reference_admission': result, 'new_physical_dimensions': 0}
    return {**bundle, 'manifest': manifest, 'collections': after}, dashboard, audit


def source_index(catalog, compressed, registry, documents, dashboard):
    if (set(documents) != DOCUMENTS or admission.runtime.sha(compressed) != catalog['compressed_sha256']
            or len(compressed) != catalog['compressed_bytes']):
        raise ValueError('Exact source documents and compressed index required')
    raw = gzip.decompress(compressed)
    if len(raw) != catalog['bundle_bytes'] or admission.runtime.sha(raw) != catalog['bundle_sha256']:
        raise ValueError('Parent logical index identity changed')
    additions = {**documents, DASHBOARD: dashboard}
    updated, corpus, registry, audit = extend(catalog, json.loads(raw), registry, additions)
    if set(audit['replaced_source_paths']) - {DASHBOARD} or set(audit['added_source_paths']) != DOCUMENTS:
        raise ValueError('Historical source replaced or unexpected source-document inventory')
    body = encoded(corpus)
    packed = gzip.compress(body, compresslevel=9, mtime=0)
    registry_raw = encoded(registry)
    updated.update(bundle_sha256=admission.runtime.sha(body), bundle_bytes=len(body),
                   compressed_sha256=admission.runtime.sha(packed), compressed_bytes=len(packed))
    updated['input_sha256'] = {**updated.get('input_sha256', {}),
        **{p: admission.runtime.sha(b) for p, b in additions.items()},
        'almanac/index-sources.json': admission.runtime.sha(registry_raw)}
    return {CATALOG: encoded(updated), 'almanac/index-data.json.gz': packed,
            'almanac/index-sources.json': registry_raw}, audit


def packet_manifest(manifest, generated, documents, audit):
    if set(generated) != INDEX or set(documents) != DOCUMENTS or KEY not in manifest:
        raise ValueError('Exact candidate manifest, documents and index required')
    result = copy.deepcopy(manifest)
    result['input_sha256'].update({p: admission.runtime.sha(raw) for p, raw in {**generated, **documents}.items()})
    result[KEY]['source_index_audit'] = copy.deepcopy(audit)
    return result
