"""Prepare coherent presentation receipts for the verified current-gap batch.

This adapter consumes an already verified batch. It does not replay scientific
producers, infer geography, or publish the candidate to the live atlas.
"""
import copy
import hashlib
import json
from collections import Counter

VERSION = 'indian-coastal-brazil-t24-v1'
DASHBOARD = 'research/ocean-motion-dashboard.json'
CONTRACTS = (
    'research/indian-current-identity-query-contract-v1.json',
    'research/indian-current-evidence-query-contract-v1.json',
    'research/brazil-regional-reach-query-contract-v1.json',
    'research/eicc-t24-published-width-admission-v1.json',
    'research/indian-current-reference-route-planning-v1.json',
)
CONTEXT_COLLECTIONS = (
    'current_direction_calendars', 'current_direction_descriptions',
    'current_reported_width_evidence', 'current_cross_shore_context',
    'current_regime_context',
)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def fingerprint(value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(',', ':')).encode()
    return digest(raw)


def prepare(manifest, collections, dashboard_raw, contract_bytes, *, prepared_at_utc):
    """Return new metadata/bytes; never mutate the supplied manifest or rows.

    Old scientific receipts, collection rows and per-object fingerprints pass
    through unchanged. The dashboard is a projection of the already admitted
    owners, so its source count cannot grow by appending context dictionaries.
    The caller verifies source contracts before calling this delivery adapter.
    """
    if not isinstance(prepared_at_utc, str) or not prepared_at_utc.endswith('Z'):
        raise ValueError('Explicit candidate preparation timestamp required')
    receipt = manifest.get('dashboard_receipt', {})
    if (receipt.get('source_file') != DASHBOARD
            or receipt.get('source_sha256') != digest(dashboard_raw)
            or receipt.get('source_json') != dashboard_raw.decode('utf-8')
            or manifest.get('input_sha256', {}).get(DASHBOARD) != digest(dashboard_raw)):
        raise ValueError('Changed parent dashboard receipt')
    if set(contract_bytes) != set(CONTRACTS):
        raise ValueError('Incomplete current-gap contract inventory')
    old = json.loads(dashboard_raw)
    if old.get('schema') != 'osw.motion-dashboard.v1' or old.get('fingerprint_version') != 2:
        raise ValueError('Unsupported parent dashboard')
    prior_ids = [row['id'] for row in old['entries']]
    owners = collections['objects']
    owner_ids = [row['id'] for row in owners]
    if len(owner_ids) != len(set(owner_ids)) or len(prior_ids) != len(set(prior_ids)):
        raise ValueError('Duplicate dashboard owner')
    if not set(prior_ids) <= set(owner_ids):
        raise ValueError('Candidate dropped a prior dashboard owner')
    for owner in owners:
        refs = owner['source_ids']
        if (not isinstance(refs, list) or any(not isinstance(ref, str) for ref in refs)
                or len(refs) != len(set(refs)) or owner['linked_source_count'] != len(refs)):
            raise ValueError('Invalid dashboard source projection')
        if owner.get('dashboard_search') != owner['label'] + ' ' + owner['basin']:
            raise ValueError('Invalid dashboard search projection')
    result = copy.deepcopy(manifest)
    pins = result['input_sha256']
    for path, raw in contract_bytes.items():
        document = json.loads(raw)
        for dependency, expected in document.get('input_sha256', {}).items():
            if dependency in pins and pins[dependency] != expected:
                raise ValueError('Conflicting current-gap dependency: ' + dependency)
            pins[dependency] = expected
        if path in pins and pins[path] != digest(raw):
            raise ValueError('Conflicting current-gap contract: ' + path)
        pins[path] = digest(raw)
    # Cross-contract pins must resolve to the exact supplied compiled bytes.
    for path, raw in contract_bytes.items():
        if pins[path] != digest(raw):
            raise ValueError('Current-gap contract dependency disagreement: ' + path)
    result['current_gap_admission_version'] = VERSION
    result['taxonomy']['node_count'] = len(owners)
    result['supplemental_object_collections'] = [
        'widths', 'current_identity_admissions', 'current_measurement_admissions',
        'current_regional_reaches', 'route_decisions', *CONTEXT_COLLECTIONS]
    dashboard = copy.deepcopy(old)
    dashboard['entries'] = copy.deepcopy(owners)
    dashboard['counts'] = dict(Counter(owner['type'] for owner in owners))
    dashboard['snapshot_fingerprint'] = fingerprint(owners)
    # Preparation time describes this presentation, never an observation.
    dashboard['parent_built_at_utc'] = dashboard.pop('built_at_utc', None)
    dashboard['built_at_utc'] = prepared_at_utc
    dashboard['candidate_delivery'] = {
        'version': VERSION, 'published': False,
        'scope': 'Verified source batch projected into candidate owners; no new physical geometry or annual extrema.'}
    raw = encoded(dashboard)
    pins[DASHBOARD] = digest(raw)
    result['dashboard_receipt'] = {
        'source_file': DASHBOARD, 'source_sha256': digest(raw), 'source_json': raw.decode('utf-8')}
    return result, raw
