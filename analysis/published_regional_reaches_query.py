"""Working query adapter for exact, scoped published regional reach reports."""
import argparse
import copy
import hashlib
import json
from urllib.parse import quote

import published_current_regional_reaches_v1 as method
from build_ocean_motion_claims import review_fingerprint

ROOT = method.ROOT
ADAPTER = 'analysis/published_regional_reaches_query.py'
FILE = 'research/published-regional-reaches-query-contract-v1.json'
COLLECTION = 'current_regional_reaches'
ENTITY = 'current:algerian'
ID = 'regional-reach:algerian:arnone-1990'
SOURCE_ID = 'source:arnone-algerian-1990-original'
METHOD_ID = 'source:published-current-regional-reaches-v1'
CLAIM_ID = 'claim:'+ID


def pin(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def card_links():
    def query(label, collection, value):
        request = {'collection': collection, 'filters': [{'field': 'id', 'op': 'eq', 'value': value}], 'limit': 1}
        return {'label': label, 'url': 'query.html?q='+quote(json.dumps(request, separators=(',', ':')), safe='')}
    return [
        {'label': 'View the May 1986 regional reach: >300 km', 'url': '../'+method.FIGURE},
        query('Query the dated coastal reach and its limits', COLLECTION, ID),
        query('Read the original source and incomplete-copy notice', 'sources', SOURCE_ID)]


def build_contract():
    report = method.build()
    if method.encoded(report) != (ROOT/method.REPORT).read_bytes():
        raise ValueError('Changed frozen regional-reach report')
    if method.figure(report) != (ROOT/method.FIGURE).read_bytes():
        raise ValueError('Changed frozen regional-reach figure')
    if report['id'] != ID or report['entity_id'] != ENTITY:
        raise ValueError('Changed declared regional-reach identity')
    source = report['source']
    record = copy.deepcopy(report)
    record.update(source_id=SOURCE_ID, method_source_id=METHOD_ID,
                  source_file=method.REPORT, source_file_sha256=pin(method.REPORT),
                  figure_file=method.FIGURE, figure_sha256=pin(method.FIGURE), claim_id=CLAIM_ID)
    claim = {'id': CLAIM_ID, 'subject_id': ENTITY, 'object_id': None,
             'predicate': report['constraint']['quantity'],
             'value': copy.deepcopy(report['constraint']), 'unit': 'km',
             'target_collection': COLLECTION, 'target_id': ID,
             'source_id': SOURCE_ID, 'source_locator': source['source_locator'],
             'source_locator_status': 'specific', 'evidence_class': 'primary_source_reported_constraint',
             'assertion_status': 'source_reported_dated_regional_constraint', 'scope': report['scope'],
             'method_source_id': METHOD_ID, 'method': method.PROTOCOL, 'method_status': 'described',
             'source_date': None, 'publication_year': source['publication_year'],
             'observation_time': None, 'observation_window': report['constraint']['study_window'],
             'review_status': 'not_individually_reviewed', 'reviewer': None, 'review_date': None,
             'review_note': 'Internal original-source and scope checks; no external scientific review claimed.'}
    claim['review_fingerprint'] = review_fingerprint(claim)
    primary = {'id': SOURCE_ID, 'kind': 'paper',
               'label': 'Arnone, Wiesenburg and Saunders 1990 Algerian Current original',
               'title': source['source_title'], 'url': 'https://doi.org/'+source['source_doi'],
               'doi': source['source_doi'], 'source_locator': source['source_locator'],
               'original_file': source['original_file'], 'original_sha256': source['original_sha256'],
               'original_bytes': source['original_bytes'], 'original_pages': source['original_pdf_pages'],
               'source_copy_complete': False, 'missing_printed_journal_pages': [1596, 1597],
               'provider_asset_redistributed': True,
               'material_use_class': 'public_release_original_and_factual_source_constraint',
               'rights_basis': 'DTIC cover approves unrestricted public release; printed 1587 states paper is not subject to US copyright.',
               'custody_file': method.FOLDER+'/acquisition.json',
               'metadata_note': 'Selected abstract/results pages verified. Retained copy is incomplete; not a full-paper review or whole-current measurement.'}
    internal = {'id': METHOD_ID, 'kind': 'internal',
                'label': 'OSW dated source-reported regional reach protocol v1',
                'title': 'Preserve strict thresholds, regional scope and missing uncertainty',
                'url': '../'+method.PROTOCOL, 'path': method.PROTOCOL,
                'provider_asset_redistributed': False, 'material_use_class': 'internal_source_extraction_method',
                'metadata_note': 'No distance calculation, route digitization, whole-current length, width or seasonal range.'}
    paths = {*method.INPUTS, method.PREFLIGHT, method.REPORT, method.FIGURE, ADAPTER,
             'analysis/build_ocean_motion_claims.py'}
    return {'schema': 'osw.published-regional-reaches.query-contract.v1',
            'id': ID, 'entity_id': ENTITY, 'collection': COLLECTION, 'record': record,
            'claim': claim, 'source_record': primary, 'method_source': internal,
            'card_links': card_links(),
            'source_documents': sorted({p for p in paths if p.endswith('.json')} | {FILE}),
            'input_sha256': {p: pin(p) for p in sorted(paths)}}


def evidence():
    document = build_contract()
    if method.encoded(document) != (ROOT/FILE).read_bytes():
        raise ValueError('Changed regional-reach query contract; explicitly rebuild after review')
    return document, {**document['input_sha256'], FILE: pin(FILE)}


def records(document):
    return [(COLLECTION, document['record']), ('claims', document['claim']),
            ('sources', document['source_record']), ('sources', document['method_source'])]


def append(collections, document):
    if method.encoded(document) != (ROOT/FILE).read_bytes():
        raise ValueError('Unverified regional-reach query contract')
    owners = [row for row in collections.get('objects', []) if row['id'] == ENTITY]
    if len(owners) != 1:
        raise ValueError('Missing or duplicate regional-reach current owner')
    owner = owners[0]
    for field in ['regional_reach_ids', 'source_ids']:
        values = owner.get(field, [])
        if not isinstance(values, list) or any(not isinstance(v, str) for v in values):
            raise ValueError('Invalid regional-reach owner references')
    if ID in owner.get('regional_reach_ids', []):
        raise ValueError('Duplicate regional-reach owner reference')
    additions = records(document)
    for collection, row in additions:
        if any(old['id'] == row['id'] for old in collections.get(collection, [])):
            raise ValueError('Duplicate regional-reach query record')
    # All rejection checks precede all mutations. Existing dimension rows stay exact.
    for collection, row in additions:
        collections.setdefault(collection, []).append(copy.deepcopy(row))
    owner.setdefault('regional_reach_ids', []).append(ID)
    owner['source_ids'] = sorted(set(owner.get('source_ids', [])) | {SOURCE_ID, METHOD_ID})
    if 'linked_source_count' in owner:
        owner['linked_source_count'] = len(owner['source_ids'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build', 'check'])
    args = parser.parse_args()
    if args.command == 'build':
        (ROOT/FILE).write_bytes(method.encoded(build_contract()))
    else:
        evidence()
    print('PASS regional-reach query contract '+args.command)


if __name__ == '__main__':
    main()
