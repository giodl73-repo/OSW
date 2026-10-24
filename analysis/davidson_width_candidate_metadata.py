"""Prepare Davidson delivery metadata without replaying historical admissions.

Pure small-record operations; complete packet loading belongs to the separate
cloud/resource-gated exporter. This is a working dataset, not a release.
"""
import copy
import json
from collections import Counter

import davidson_wallace_width_admission as admission
from current_gap_candidate_metadata import DASHBOARD, VERSION as PARENT_VERSION
from current_gap_candidate_metadata import digest, encoded, fingerprint
from query_packet import descriptors

PARENT_SHA = '31a0bf88a5fe40e5929c9cd6fa5f5d4cc5db92a03574354e1f8554003bf802e3'
PARENT_BYTES = 189850589
PARENT_OBJECTS = 246
PARENT_ROWS = 108524
PARENT_PACKET = 'research/davidson-width-parent-query-packet-v1.json'
PARENT_PACKET_SHA = '229fecfa0f1043527766a2d0cdea48bea90b62cd85d8441bfc4673d58eae57ed'
VERSION = 'davidson-wallace-line67-v1'
INSTALLED_PROOF = 'research/davidson-width-installed-delivery-v1.json'
PARENT_OWNER = 'research/davidson-width-parent-owner-v1.json'
PARENT_OWNER_SHA = 'ccfa19808990ecc5bdf40f7a222d9facf87491b5201da420296ae16fc4e016c4'
OWNER_METADATA = {
    'width_ids', 'source_ids', 'linked_source_count', 'evidence_links',
    'recorded_claims', 'claim_review_counts', 'section_fingerprints', 'fingerprint',
}


def parent_owner():
    raw = admission.read(PARENT_OWNER)
    if digest(raw) != PARENT_OWNER_SHA:
        raise ValueError('Changed verified Davidson parent projection')
    document = json.loads(raw)
    if (document.get('schema') != 'osw.davidson-width-parent-owner.v1'
            or document.get('parent_logical_sha256') != PARENT_SHA
            or document.get('owner', {}).get('id') != admission.ENTITY):
        raise ValueError('Wrong Davidson parent projection')
    return document


def validate_parent(packet, installed):
    """Accept only the exact already-tested 106-current parent transport."""
    descriptors(packet)
    if packet['logical_sha256'] != PARENT_SHA or packet['logical_byte_length'] != PARENT_BYTES:
        raise ValueError('Unrecognized Davidson parent; refuse replay or downgrade')
    if (installed.get('schema') != 'osw.current-gap-installed-delivery.v1'
            or installed.get('status') != 'verified_cloud_delivery'
            or installed.get('cohort_version') != PARENT_VERSION
            or installed.get('packet_logical_sha256') != PARENT_SHA
            or any(installed.get(key) is not True for key in
                   ['native_verified', 'browser_verified', 'working_dataset_delivery_verified'])):
        raise ValueError('Missing verified 106-current installed parent receipt')
    expected = {'logical_sha256':PARENT_SHA, 'logical_bytes':PARENT_BYTES,
                'objects':PARENT_OBJECTS, 'rows':PARENT_ROWS, 'named_currents':106}
    if installed.get('candidate') != expected:
        raise ValueError('Changed parent inventory receipt')


def validate_current(packet, installed, newer=None, *, contract_sha256=None):
    """Permit an exact replay of this cohort, never a later/unknown cohort."""
    descriptors(packet)
    if packet['logical_sha256'] == PARENT_SHA:
        validate_parent(packet, installed)
        return
    newer = newer or {}
    inventory = newer.get('candidate', {})
    if (newer.get('schema') != 'osw.davidson-width-installed-delivery.v1'
            or newer.get('status') != 'verified_cloud_delivery'
            or newer.get('cohort_version') != VERSION
            or newer.get('parent_logical_sha256') != PARENT_SHA
            or newer.get('packet_logical_sha256') != packet['logical_sha256']
            or not contract_sha256 or newer.get('admission_contract_sha256') != contract_sha256
            or any(newer.get(key) is not True for key in
                   ['native_verified','browser_verified','working_dataset_delivery_verified'])
            or inventory.get('logical_sha256') != packet['logical_sha256']
            or inventory.get('logical_bytes') != packet['logical_byte_length']
            or inventory.get('objects') != PARENT_OBJECTS
            or inventory.get('rows') not in (PARENT_ROWS + 5,PARENT_ROWS + 6)
            or inventory.get('named_currents') != 106 or inventory.get('widths') != 172):
        raise ValueError('Unknown current packet or unverified Davidson replay')


def verify_preservation(prior, staged, receipt):
    """Every old row survives; only Davidson provenance/width ownership changes."""
    expected_additions = receipt['added_rows']
    if set(staged) != set(prior) | set(expected_additions):
        raise ValueError('Unexpected candidate collection')
    for name in staged:
        if name == 'objects':
            continue
        old_rows = prior.get(name, [])
        if (staged[name][:len(old_rows)] != old_rows
                or len(staged[name]) != len(old_rows) + expected_additions.get(name, 0)):
            raise ValueError('Prior rows changed or unexpected append: ' + name)
    if len(staged['objects']) != len(prior['objects']):
        raise ValueError('A width cannot change the object inventory')
    unchanged = 0
    for old, new in zip(prior['objects'], staged['objects']):
        if old['id'] != admission.ENTITY:
            if new != old:
                raise ValueError('Unrelated current or eddy changed')
            unchanged += 1
            continue
        if ({k:v for k,v in old.items() if k not in OWNER_METADATA | {'capabilities'}}
                != {k:v for k,v in new.items() if k not in OWNER_METADATA | {'capabilities'}}):
            raise ValueError('Davidson physical fields changed')
        capabilities = copy.deepcopy(old['capabilities'])
        capabilities['scoped_width'] = capabilities.get('scoped_width', 0) + 1
        if new['capabilities'] != capabilities:
            raise ValueError('Unsupported Davidson physical capability change')
        if new['width_ids'] != [*old['width_ids'], admission.WIDTH]:
            raise ValueError('Historical Davidson width ownership changed')
    return {'all_prior_nonobject_rows_exact':True,
            'prior_rows_verified':sum(len(rows) for name,rows in prior.items() if name != 'objects'),
            'unchanged_objects_verified':unchanged,
            'physical_fields_and_capabilities_preserved_except_scoped_width_count':True}


def prepare(manifest, collections, dashboard_raw, document, *, prepared_at_utc):
    if (not isinstance(prepared_at_utc, str) or not prepared_at_utc.endswith('Z')
            or manifest.get('current_gap_admission_version') != PARENT_VERSION):
        raise ValueError('Verified parent cohort and explicit preparation time required')
    receipt = manifest.get('dashboard_receipt', {})
    if (receipt.get('source_file') != DASHBOARD
            or receipt.get('source_sha256') != digest(dashboard_raw)
            or receipt.get('source_json') != dashboard_raw.decode('utf-8')
            or manifest.get('input_sha256', {}).get(DASHBOARD) != digest(dashboard_raw)):
        raise ValueError('Changed parent dashboard receipt')
    old = json.loads(dashboard_raw)
    if (old.get('schema') != 'osw.motion-dashboard.v1' or old.get('fingerprint_version') != 2
            or old.get('entries') != collections['objects']
            or old.get('snapshot_fingerprint') != fingerprint(collections['objects'])
            or old.get('counts') != dict(Counter(row['type'] for row in collections['objects']))):
        raise ValueError('Parent dashboard no longer projects its owners')
    expected_owner = parent_owner()['owner']
    owners = [row for row in collections['objects'] if row['id'] == admission.ENTITY]
    if len(owners) != 1 or any(owners[0].get(key) != value for key,value in expected_owner.items()):
        raise ValueError('Davidson owner differs from its verified parent projection')
    metadata, staged, admission_receipt = admission.prepare_candidate(manifest, collections, document)
    metadata['input_sha256'][PARENT_OWNER] = PARENT_OWNER_SHA
    preservation = verify_preservation(collections, staged, admission_receipt)
    dashboard = copy.deepcopy(old)
    dashboard['entries'] = copy.deepcopy(staged['objects'])
    dashboard['snapshot_fingerprint'] = fingerprint(staged['objects'])
    dashboard['parent_built_at_utc'] = old.get('built_at_utc')
    dashboard['built_at_utc'] = prepared_at_utc
    dashboard['parent_candidate_delivery'] = copy.deepcopy(old.get('candidate_delivery'))
    dashboard['candidate_delivery'] = {
        'version':VERSION, 'published':False, 'parent_logical_sha256':PARENT_SHA,
        'scope':'One source-reported regional campaign span; no raw samples, annual range or geometry.'}
    raw = encoded(dashboard)
    metadata['input_sha256'][DASHBOARD] = digest(raw)
    metadata['dashboard_receipt'] = {
        'source_file':DASHBOARD, 'source_sha256':digest(raw), 'source_json':raw.decode('utf-8')}
    metadata['davidson_candidate_delivery'] = {
        'version':VERSION, 'parent_logical_sha256':PARENT_SHA,
        'prepared_at_utc':prepared_at_utc, 'scientific_release_published':False}
    return metadata, staged, raw, {**admission_receipt, 'preservation':preservation}
