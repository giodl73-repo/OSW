"""Coherent candidate metadata; no packet or original observations loaded here."""
import copy
import json
from collections import Counter

import indian_coastal_dimension_context_v1 as context
from current_gap_candidate_metadata import DASHBOARD, digest, encoded, fingerprint

PARENT_PROOF = 'research/baffin-bound-installed-delivery-v1.json'
PARENT_PROOF_SHA = '54b54ab66c0fe4d418c6da3a73542c075c61b99b0c3eba80a93e59f55488005d'
PARENT_LOGICAL = '045d6fd80b871ba7a9863154f390d7c84a450f4b3e960b3f5f4e27b8d6a009b0'
VERSION_KEY = 'indian_coastal_dimension_context_version'


def validate_parent(packet, installed):
    from query_packet import descriptors
    descriptors(packet)
    candidate = installed.get('candidate', {})
    if (installed.get('schema') != 'osw.baffin-bound-installed-delivery.v1'
            or installed.get('status') != 'verified_cloud_delivery'
            or installed.get('cohort_version') != 'baffin-described-latitudes-v1'
            or installed.get('packet_logical_sha256') != PARENT_LOGICAL
            or packet.get('logical_sha256') != PARENT_LOGICAL
            or candidate.get('logical_sha256') != PARENT_LOGICAL
            or candidate.get('logical_bytes') != packet.get('logical_byte_length')
            or candidate.get('objects') != 246 or candidate.get('rows') != 108544
            or candidate.get('named_currents') != 106 or candidate.get('widths') != 172
            or installed.get('recovery_workflow_run_id') != 40091783069
            or installed.get('original_validation_job_conclusion') != 'success'
            or any(installed.get(key) is not True for key in
                   ['native_verified', 'browser_verified', 'working_dataset_delivery_verified'])
            or installed.get('scientific_release_published') is not False
            or installed.get('main_merged') is not False):
        raise ValueError('Verified installed Baffin parent required before coastal context export')


def verify_preservation(prior, staged, contract):
    expected, _ = context.prepare(prior, contract)
    if set(staged) != set(expected):
        raise ValueError('Unexpected context candidate collection')
    for name in expected:
        if staged[name] != expected[name]:
            raise ValueError('Prior evidence or projected source context changed: ' + name)
    owners = {context.EACC, context.SJC}
    allowed_fields = {'regional_reach_ids', 'cross_shore_context_ids', 'source_ids',
                      'linked_source_count', 'evidence_links', 'section_fingerprints',
                      'recorded_claims', 'claim_review_counts', 'fingerprint', 'capabilities'}
    allowed_caps = {item[1] for item in context.OWNER_FIELDS.values()}
    unchanged = 0
    for before, after in zip(prior['objects'], staged['objects']):
        if before['id'] not in owners:
            if before != after:raise ValueError('Unrelated object changed')
            unchanged += 1
            continue
        if {k: v for k, v in before.items() if k not in allowed_fields} != {
                k: v for k, v in after.items() if k not in allowed_fields}:
            raise ValueError('Physical owner fields changed during source context projection')
        for field in set(before.get('capabilities', {})) | set(after.get('capabilities', {})):
            if field not in allowed_caps and before.get('capabilities', {}).get(field) != after.get('capabilities', {}).get(field):
                raise ValueError('Physical owner capability changed')
    return {'all_prior_nonobject_rows_exact': True, 'unchanged_objects_verified': unchanged,
            'changed_owner_ids': sorted(owners), 'new_rows': 7,
            'physical_fields_and_capabilities_preserved': True,
            'qualified_published_length_ranks_preserved': True,
            'source_arrays_preserved': True}


def prepare(manifest, collections, dashboard_raw, contract, *, prepared_at_utc):
    if (manifest.get('baffin_latitude_gate_bound_version') != '1' or VERSION_KEY in manifest
            or not isinstance(prepared_at_utc, str) or not prepared_at_utc.endswith('Z')):
        raise ValueError('New coastal context preparation on installed Baffin cohort required')
    receipt = manifest.get('dashboard_receipt', {})
    if (receipt.get('source_file') != DASHBOARD or receipt.get('source_sha256') != digest(dashboard_raw)
            or receipt.get('source_json') != dashboard_raw.decode('utf8')
            or manifest.get('input_sha256', {}).get(DASHBOARD) != digest(dashboard_raw)):
        raise ValueError('Changed parent dashboard receipt')
    old = json.loads(dashboard_raw)
    if (old.get('schema') != 'osw.motion-dashboard.v1' or old.get('fingerprint_version') != 2
            or old.get('entries') != collections['objects']
            or old.get('snapshot_fingerprint') != fingerprint(collections['objects'])
            or old.get('counts') != dict(Counter(row['type'] for row in collections['objects']))):
        raise ValueError('Parent dashboard no longer projects its owners')
    staged, admission = context.prepare(collections, contract)
    preservation = verify_preservation(collections, staged, contract)
    metadata = copy.deepcopy(manifest)
    for path, sha in contract.get('input_sha256', {}).items():
        prior = metadata['input_sha256'].get(path)
        if prior is not None and prior != sha:
            raise ValueError('Changed historical dependency: ' + path)
        metadata['input_sha256'][path] = sha
    editorial = metadata.get('editorial_collections')
    if not isinstance(editorial, list) or len(editorial) != len(set(editorial)):
        raise ValueError('Invalid parent editorial collection inventory')
    for collection in context.OWNER_FIELDS:
        if collection not in editorial:editorial.append(collection)
    metadata[VERSION_KEY] = context.VERSION
    dashboard = copy.deepcopy(old)
    dashboard.update(entries=copy.deepcopy(staged['objects']), snapshot_fingerprint=fingerprint(staged['objects']),
                     parent_built_at_utc=old.get('built_at_utc'), built_at_utc=prepared_at_utc,
                     parent_candidate_delivery=copy.deepcopy(old.get('candidate_delivery')),
                     candidate_delivery={'version': context.VERSION, 'published': False,
                         'scope': 'Two source contexts; no new measured length, paired width, annual range or geometry.'})
    raw = encoded(dashboard)
    metadata['input_sha256'][DASHBOARD] = digest(raw)
    metadata['dashboard_receipt'] = {'source_file': DASHBOARD, 'source_sha256': digest(raw), 'source_json': raw.decode('utf8')}
    return metadata, staged, raw, {**admission, 'preservation': preservation}
