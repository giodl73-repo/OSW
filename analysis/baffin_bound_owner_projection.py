"""Exact Baffin owner transition; source-stage and physical records stay unchanged."""
import argparse
import copy
import json
from collections import Counter

import baffin_bound_admission as a
from current_gap_candidate_metadata import fingerprint
from object_source_links import project

PARENT = 'research/baffin-bound-parent-owner-v1.json'
PARENT_SHA = 'c9fa011656ef90aa43c2e77f5dfd32d63fde0431f0b539c84cd6e4ce79836e8c'
FILE = 'research/baffin-bound-owner-transition-v1.json'
OPERATOR = 'analysis/baffin_bound_owner_projection.py'
METADATA_FIELDS = {'measurement_ids', 'evidence_links', 'source_ids', 'linked_source_count',
                   'recorded_claims', 'claim_review_counts', 'section_fingerprints', 'fingerprint',
                   'regional_length_bound', 'evidence_transition'}


def parent():
    if a.pin(PARENT) != PARENT_SHA:
        raise ValueError('Changed verified Baffin parent owner')
    doc = json.loads(a.read(PARENT))
    if doc['schema'] != 'osw.baffin-bound-parent-owner.v1' or doc['owner']['id'] != a.ENTITY:
        raise ValueError('Wrong Baffin owner projection')
    return doc


def expected_owner(document):
    old = parent()['owner']
    result = copy.deepcopy(old)
    if a.MEASUREMENT in old['measurement_ids']:
        raise ValueError('Bound is already owned; refuse duplicate transition')
    result['measurement_ids'].append(a.MEASUREMENT)
    result['evidence_links'].extend(copy.deepcopy(document['card_links']))
    result['source_ids'] = sorted(set(old['source_ids']) | {row['id'] for row in document['source_records']})
    result['linked_source_count'] = len(result['source_ids'])
    result['recorded_claims'] += 1
    status = document['claim']['review_status']
    result['claim_review_counts'][status] = result['claim_review_counts'].get(status, 0) + 1
    result['regional_length_bound'] = {
        'value_km': document['measurement']['value'], 'admission_id': a.ADMISSION,
        'measurement_id': a.MEASUREMENT, 'conditional_on_nominal_gates': True,
        'whole_current_representative': False, 'rank_eligible': False,
        'annual_length_range_km': None,
    }
    changes = {
        'claims': [document['claim']],
        'measurements': [document['measurement'], document['length_assessment']],
        'sources': document['source_records'],
    }
    # Display-change fingerprints preserve the previous digest as a parent.
    # They are not a recomputation of unavailable historical source inputs.
    for group, additions in changes.items():
        result['section_fingerprints'][group] = fingerprint({
            'parent_section_fingerprint': old['section_fingerprints'][group],
            'admission_id': a.ADMISSION, 'added_evidence': additions,
        })
    result['section_fingerprints']['source_ownership'] = fingerprint(result['source_ids'])
    result['evidence_transition'] = {
        'id': 'owner_transition:baffin:latitude-bound-v1',
        'parent_owner_fingerprint': old['fingerprint'],
        'parent_owner_projection_sha256': PARENT_SHA,
        'section_digest_method': 'hash_of_prior_section_digest_and_explicit_admitted_evidence',
        'scientific_source_inputs_recomputed': False,
    }
    result['fingerprint'] = fingerprint({key: value for key, value in result.items() if key != 'fingerprint'})
    if {k:v for k,v in result.items() if k not in METADATA_FIELDS} != {k:v for k,v in old.items() if k not in METADATA_FIELDS}:
        raise ValueError('Physical Baffin owner fields changed')
    return result


def build_transition():
    document = json.loads(a.read(a.FILE))
    if a.encoded(document) != a.encoded(a.build_contract()):
        raise ValueError('Unverified Baffin admission contract')
    return {
        'schema': 'osw.baffin-bound-owner-transition.v1',
        'status': 'prepared_exact_owner_projection_delivery_unverified',
        'entity_id': a.ENTITY, 'admission_file': a.FILE,
        'parent_owner_file': PARENT, 'parent_owner_sha256': PARENT_SHA,
        'admission_contract_sha256': a.pin(a.FILE), 'owner': expected_owner(document),
        'physical_fields_and_capabilities_preserved': True,
        'working_delivery_verified': False,
    }


def prepare(collections, document):
    """All-or-nothing candidate preparation, including registered owner evidence."""
    transition = json.loads(a.read(FILE))
    if a.encoded(transition) != a.encoded(build_transition()):
        raise ValueError('Changed owner transition')
    owners = [r for r in collections.get('objects', []) if r.get('id') == a.ENTITY]
    if owners != [parent()['owner']]:
        raise ValueError('Changed or duplicate verified parent Baffin owner')
    staged, receipt = a.prepare_records(collections, document)
    expected = transition['owner']
    owned = []
    for name, rows in staged.items():
        if name in {'objects', 'sources'}:
            continue
        owned.extend(row for row in rows if a.ENTITY in [row.get(key) for key in ('id','entity_id','subject_id','object_id')]
                     or row.get('current_id') == 'baffin')
    registered = [r['id'] for r in staged['sources']]
    if project(expected, registered, owned)['source_ids'] != expected['source_ids']:
        raise ValueError('Unexpected Baffin source ownership')
    claims = [r for r in staged['claims'] if a.ENTITY in (r.get('subject_id'), r.get('object_id'))]
    counts = dict(Counter(r.get('review_status') or 'unspecified' for r in claims))
    if len(claims) != expected['recorded_claims'] or counts != expected['claim_review_counts']:
        raise ValueError('Prior Baffin claim inventory differs from verified parent')
    measures = [r['id'] for r in staged['measurements'] if r.get('entity_id') == a.ENTITY]
    widths = [r['id'] for r in staged.get('widths',[]) if r.get('current_id') == 'baffin']
    if measures != expected['measurement_ids'] or set(widths) != set(expected['width_ids']) or len(widths) != len(expected['width_ids']):
        raise ValueError('Changed Baffin measurement or width ownership')
    staged['objects'] = [copy.deepcopy(expected) if r.get('id') == a.ENTITY else r for r in collections['objects']]
    return staged, {**receipt, 'status':'prepared_owner_and_records_delivery_pending',
                    'owner_projection_verified':True, 'physical_fields_and_capabilities_preserved':True}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build','check'])
    args = parser.parse_args()
    raw = a.encoded(build_transition())
    if args.action == 'build':
        with (a.ROOT / FILE).open('xb') as stream:
            stream.write(raw)
    elif a.read(FILE) != raw:
        raise ValueError('Changed exact Baffin owner transition')
    print('PASS prepared Baffin owner transition; live packet unchanged')
