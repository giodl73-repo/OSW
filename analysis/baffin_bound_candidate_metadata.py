"""Prepare coherent Baffin dashboard/manifest metadata without loading a packet."""
import copy
import json
from collections import Counter

import baffin_bound_admission as a
import baffin_bound_owner_projection as owner
from current_gap_candidate_metadata import DASHBOARD, digest, encoded, fingerprint

VERSION = 'baffin-described-latitudes-v1'
PARENT_PROOF = 'research/davidson-width-installed-delivery-v1.json'


def validate_parent(packet, installed):
    """Require the successful preceding cloud delivery, not just a prepared candidate."""
    from query_packet import descriptors
    descriptors(packet)
    candidate = installed.get('candidate', {})
    if (installed.get('schema') != 'osw.davidson-width-installed-delivery.v1'
            or installed.get('status') != 'verified_cloud_delivery'
            or installed.get('cohort_version') != 'davidson-wallace-line67-v1'
            or installed.get('parent_logical_sha256') != owner.parent()['parent_logical_sha256']
            or installed.get('packet_logical_sha256') != packet['logical_sha256']
            or packet['logical_sha256'] == owner.parent()['parent_logical_sha256']
            or candidate.get('logical_sha256') != packet['logical_sha256']
            or candidate.get('logical_bytes') != packet['logical_byte_length']
            or candidate.get('objects') != 246 or candidate.get('named_currents') != 106
            or candidate.get('widths') != 172 or candidate.get('rows') not in (108529, 108530)
            or any(installed.get(k) is not True for k in
                   ('native_verified','browser_verified','working_dataset_delivery_verified'))
            or installed.get('scientific_release_published') is not False
            or installed.get('main_merged') is not False):
        raise ValueError('A verified installed Davidson parent is required before Baffin export')


def verify_preservation(prior, staged, document):
    declared_records = a.records(document)
    additions = Counter(name for name, _ in declared_records)
    if set(staged) != set(prior) | set(additions):
        raise ValueError('Unexpected Baffin candidate collection')
    preserved = 0
    for name, rows in staged.items():
        if name == 'objects':
            continue
        old = prior.get(name, [])
        expected = [document['length_assessment'] if name == 'length_assessments' and row.get('entity_id') == a.ENTITY else row
                    for row in old]
        appended = [row for collection, row in declared_records if collection == name]
        if rows != expected + appended:
            raise ValueError('Prior evidence changed or unexpected append: ' + name)
        preserved += len(old) - (1 if name == 'length_assessments' else 0)
    if len(staged['objects']) != len(prior['objects']):
        raise ValueError('A geographic bound cannot change object inventory')
    unchanged = 0
    for old, new in zip(prior['objects'], staged['objects']):
        if old['id'] != a.ENTITY:
            if old != new:
                raise ValueError('Unrelated current or eddy changed')
            unchanged += 1
        elif new != owner.expected_owner(document):
            raise ValueError('Changed exact Baffin owner projection')
    return {'all_other_prior_nonobject_rows_exact':True,
            'prior_nonobject_rows_verified':preserved, 'length_assessments_replaced':1,
            'unchanged_objects_verified':unchanged,
            'physical_fields_and_capabilities_preserved':True,
            'qualified_published_length_ranks_preserved':True}


def prepare(manifest, collections, dashboard_raw, document, *, prepared_at_utc):
    if (not isinstance(prepared_at_utc, str) or not prepared_at_utc.endswith('Z')
            or manifest.get('davidson_reported_width_version') != 'wallace-line67-v1'
            or a.VERSION_KEY in manifest):
        raise ValueError('Preceding Davidson cohort and a new preparation time required')
    receipt = manifest.get('dashboard_receipt', {})
    if (receipt.get('source_file') != DASHBOARD
            or receipt.get('source_sha256') != digest(dashboard_raw)
            or receipt.get('source_json') != dashboard_raw.decode('utf8')
            or manifest.get('input_sha256', {}).get(DASHBOARD) != digest(dashboard_raw)):
        raise ValueError('Changed parent dashboard receipt')
    old = json.loads(dashboard_raw)
    if (old.get('schema') != 'osw.motion-dashboard.v1' or old.get('fingerprint_version') != 2
            or old.get('entries') != collections['objects']
            or old.get('snapshot_fingerprint') != fingerprint(collections['objects'])
            or old.get('counts') != dict(Counter(row['type'] for row in collections['objects']))):
        raise ValueError('Parent dashboard no longer projects its owners')
    staged, admission = owner.prepare(collections, document)
    preservation = verify_preservation(collections, staged, document)
    metadata = copy.deepcopy(manifest)
    pins = {**document['input_sha256'], a.FILE:a.pin(a.FILE),
            owner.PARENT:owner.PARENT_SHA, owner.FILE:a.pin(owner.FILE)}
    for path, sha in pins.items():
        prior = metadata['input_sha256'].get(path)
        if prior is not None and prior != sha:
            raise ValueError('Changed parent scientific dependency: ' + path)
        metadata['input_sha256'][path] = sha
    metadata.update(document['manifest_fields'])
    editorial = metadata.get('editorial_collections')
    if not isinstance(editorial, list) or len(editorial) != len(set(editorial)):
        raise ValueError('Invalid parent editorial collection inventory')
    if 'current_length_bound_scenarios' not in editorial:
        editorial.append('current_length_bound_scenarios')
    dashboard = copy.deepcopy(old)
    dashboard['entries'] = copy.deepcopy(staged['objects'])
    dashboard['snapshot_fingerprint'] = fingerprint(staged['objects'])
    dashboard['parent_built_at_utc'] = old.get('built_at_utc')
    dashboard['built_at_utc'] = prepared_at_utc
    dashboard['parent_candidate_delivery'] = copy.deepcopy(old.get('candidate_delivery'))
    dashboard['candidate_delivery'] = {
        'version':VERSION, 'published':False,
        'scope':'One conditional regional geographic floor and nine editorial scenarios; no measured axis, seasonal range or qualified length rank.',
    }
    raw = encoded(dashboard)
    metadata['input_sha256'][DASHBOARD] = digest(raw)
    metadata['dashboard_receipt'] = {'source_file':DASHBOARD,'source_sha256':digest(raw),'source_json':raw.decode('utf8')}
    metadata['baffin_bound_candidate_delivery'] = {
        'version':VERSION,'prepared_at_utc':prepared_at_utc,
        'scientific_release_published':False,
    }
    return metadata, staged, raw, {**admission, 'preservation':preservation}
