"""Stage the compatible source batch without copying the full atlas payload."""
import hashlib
import copy
from collections import Counter

import brazil_regional_reach_query as brazil
import indian_current_evidence_query as indian
import indian_current_identity_query as identity
import inventory_source_links as provenance


def documents():
    """Read and source-verify all three prepared contracts, sequentially."""
    return identity.evidence()[0], indian.evidence()[0], brazil.evidence()[0]


def prepare(collections, identity_document, evidence_document, brazil_document):
    """Return a staged replacement and receipt; any error leaves input exact.

    Only affected collection lists are copied. Existing large measurement and
    source-array payloads are shared read-only. The Indian adapters create new
    owners; provenance projection detaches older owners before Brazil updates.
    """
    touched = set(identity_document['additions']) | set(evidence_document['additions'])
    touched.update(name for name, _ in brazil.records(brazil_document))
    touched.add('objects')
    stage = dict(collections)
    for name in touched:
        existing = collections.get(name, [])
        if not isinstance(existing, list):
            raise ValueError('Batch collection is not a record list: ' + name)
        stage[name] = list(existing)
    identity.append(stage, identity_document)
    indian.append(stage, evidence_document)
    before_brazil = provenance.append(stage)
    brazil.append(stage, brazil_document)
    after_brazil = provenance.append(stage)
    brazil_owner = next(row for row in stage['objects'] if row['id'] == brazil.ENTITY)
    links = brazil_owner.setdefault('evidence_links', [])
    for link in brazil_document['card_links']:
        if link not in links:
            links.append(dict(link))
    brazil_owner['regional_reach_scope_note'] = brazil_document['host_explanation']
    brazil_owner.setdefault('capabilities', {})['reported_regional_reaches'] = len(brazil_owner['regional_reach_ids'])
    brazil_claims = [row for row in stage['claims'] if brazil.ENTITY in (row.get('subject_id'), row.get('object_id'))]
    brazil_owner['recorded_claims'] = len(brazil_claims)
    brazil_owner['claim_review_counts'] = dict(Counter(row.get('review_status') or 'unspecified' for row in brazil_claims))
    brazil_owner.setdefault('section_fingerprints', {})['claims'] = identity.fingerprint(brazil_claims)
    source_index = {row['id']: row for row in stage['sources']}
    prior_objects = {row['id']: row for row in collections['objects']}
    unchanged_prior_objects = 0
    for owner in stage['objects']:
        prior = prior_objects.get(owner['id'])
        content = lambda row: {key: value for key, value in row.items() if key not in ('fingerprint', 'section_fingerprints')}
        if prior is not None and content(prior) == content(owner):
            owner['fingerprint'] = prior['fingerprint']
            owner['section_fingerprints'] = copy.deepcopy(prior['section_fingerprints'])
            unchanged_prior_objects += 1
            continue
        group = [source_index[ref] for ref in owner['source_ids']]
        owner.setdefault('section_fingerprints', {})['sources'] = identity.fingerprint(group)
        owner['fingerprint'] = identity.fingerprint({key: value for key, value in owner.items() if key != 'fingerprint'})
    for name in ('measurements', 'widths', 'geometries', 'width_samples', 'length_ranks'):
        if stage.get(name) != collections.get(name):
            raise ValueError('Source batch changed physical collection: ' + name)
    receipt = {
        'schema': 'osw.current-gap-admission-batch-receipt.v1',
        'status': 'prepared_batch_applied_to_supplied_collections_not_published',
        'canonical_delivery_verified': False,
        'unchanged_prior_object_fingerprints_preserved': unchanged_prior_objects,
        'operator_sha256': {path: identity.pin(path) for path in (
            'analysis/current_gap_admission_batch.py', 'analysis/inventory_source_links.py', 'analysis/object_source_links.py')},
        'contract_sha256': {path: hashlib.sha256(identity.encoded(doc)).hexdigest()
            for path, doc in [(identity.FILE, identity_document), (indian.FILE, evidence_document), (brazil.FILE, brazil_document)]},
        'added_rows': {name: len(stage.get(name, [])) - len(collections.get(name, [])) for name in sorted(touched)},
        'source_projection_before_brazil': before_brazil,
        'source_projection_after_brazil': after_brazil,
        'physical_collections_unchanged': True,
        'independent_observations_added': 0,
        'canonical_width_samples_added': 0,
        'next_gate': 'Coherent dashboard/query/index/native/WASM generation, typed guards, complete runtime audit and accessible map/card/seasonal delivery.',
    }
    return stage, receipt


def append(collections, identity_document, evidence_document, brazil_document):
    stage, receipt = prepare(collections, identity_document, evidence_document, brazil_document)
    for name in receipt['added_rows']:
        collections[name] = stage[name]
    return receipt
