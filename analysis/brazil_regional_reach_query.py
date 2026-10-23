"""Prepare exact Brazil source-reach records for the next canonical batch."""
import argparse
import copy
import hashlib
import json
from urllib.parse import quote

import published_current_regional_reaches_v2 as method
from build_ocean_motion_claims import review_fingerprint

ROOT = method.ROOT
ADAPTER = 'analysis/brazil_regional_reach_query.py'
FILE = 'research/brazil-regional-reach-query-contract-v1.json'
COLLECTION = 'current_regional_reaches'
ENTITY = 'current:brazil'
ID = 'regional-reach:brazil:tomczak-ch14-2002-initial'
SOURCE_ID = 'source:tomczak-godfrey-brazil-ch14-2002'
METHOD_ID = 'source:published-current-regional-reaches-v2'
CLAIM_ID = 'claim:'+ID


def pin(path):
    with (ROOT/path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def card_links():
    def query(label, collection, value):
        request = {'collection': collection, 'filters': [{'field': 'id', 'op': 'eq', 'value': value}], 'limit': 1}
        return {'label': label, 'url': 'query.html?q='+quote(json.dumps(request, separators=(',', ':')), safe='')}
    return [
        {'label': 'View the source-reported initial reach: 1500 km', 'url': '../'+method.FIGURE},
        query('Query the initial reach; observation dates unspecified', COLLECTION, ID),
        query('Read the textbook passage, version and source custody', 'sources', SOURCE_ID)]


def build_contract():
    report = method.build()
    if method.encoded(report) != (ROOT/method.REPORT).read_bytes():
        raise ValueError('Changed frozen Brazil regional-reach report')
    if method.figure(report) != (ROOT/method.FIGURE).read_bytes():
        raise ValueError('Changed frozen Brazil regional-reach figure')
    if report['id'] != ID or report['entity_id'] != ENTITY:
        raise ValueError('Changed registered Brazil source-reach identity')
    source = report['source']
    record = copy.deepcopy(report)
    record.update(source_id=SOURCE_ID, method_source_id=METHOD_ID, claim_id=CLAIM_ID,
                  source_file=method.REPORT, source_file_sha256=pin(method.REPORT),
                  figure_file=method.FIGURE, figure_sha256=pin(method.FIGURE))
    claim = {'id': CLAIM_ID, 'subject_id': ENTITY, 'object_id': None,
             'predicate': report['constraint']['quantity'], 'value': copy.deepcopy(report['constraint']),
             'unit': 'km', 'target_collection': COLLECTION, 'target_id': ID,
             'source_id': SOURCE_ID, 'source_locator': source['source_locator'],
             'source_locator_status': 'specific', 'evidence_class': 'textbook_source_reported_regional_reach',
             'assertion_status': report['status'], 'scope': report['scope'],
             'method_source_id': METHOD_ID, 'method': method.PROTOCOL, 'method_status': 'described',
             'source_date': None, 'publication_year': None,
             'first_printed_edition_year': source['first_printed_edition_year'],
             'chapter_pdf_version_month': source['chapter_pdf_version_month'],
             'observation_time': None, 'observation_window': None,
             'review_status': 'not_individually_reviewed', 'reviewer': None, 'review_date': None,
             'review_note': 'Internal original-source and scope checks; no external scientific review claimed.'}
    claim['review_fingerprint'] = review_fingerprint(claim)
    acquisition = json.loads((ROOT/method.ACQUISITION).read_bytes())
    primary = {'id': SOURCE_ID, 'kind': 'book_excerpt',
               'label': 'Tomczak and Godfrey Brazil Current initial reach, chapter14 PDF v1.2 (2002)',
               'title': source['source_title'], 'url': source['source_url'],
               'source_locator': source['source_locator'], 'source_kind': source['source_kind'],
               'first_printed_edition_year': source['first_printed_edition_year'],
               'chapter_pdf_version': source['chapter_pdf_version'],
               'chapter_pdf_version_month': source['chapter_pdf_version_month'],
               'original_file': source['original_file'], 'original_sha256': source['original_sha256'],
               'document_identity_sha256': source['original_sha256'],
               'original_bytes': source['original_bytes'], 'original_pages': source['original_pdf_pages'],
               'source_copy_complete': None, 'selected_reviewed_pdf_pages': [254, 255],
               'provider_asset_redistributed': False,
               'material_use_class': 'attributed_textbook_fact_and_short_passage_not_full_book',
               'rights_basis': acquisition['source_license'], 'custody_file': method.ACQUISITION,
               'metadata_note': 'A scoped excerpt of the existing retained compilation, not another independent document or observation. Whole-book completeness unassessed; observation dates unspecified.'}
    internal = {'id': METHOD_ID, 'kind': 'internal',
                'label': 'OSW source-reported initial regional reach protocol v2',
                'title': 'Preserve the source value, approximate context and unspecified observation support',
                'url': '../'+method.PROTOCOL, 'path': method.PROTOCOL,
                'provider_asset_redistributed': False, 'material_use_class': 'internal_source_extraction_method',
                'metadata_note': 'No distance calculation, inferred dates/endpoints, whole-current length, physical width or seasonal range.'}
    paths = {*method.INPUTS, method.PREFLIGHT, method.REPORT, method.FIGURE, ADAPTER,
             'analysis/build_ocean_motion_claims.py', 'analysis/object_source_links.py'}
    return {'schema': 'osw.brazil-regional-reach.query-contract.v1',
            'id': ID, 'entity_id': ENTITY, 'collection': COLLECTION, 'record': record,
            'claim': claim, 'source_record': primary, 'method_source': internal,
            'card_links': card_links(),
            'host_explanation': 'This source reports only an initial regional reach. Independent section-width evidence is separate; whole-current dimensions and observation dates are not supplied by this statement.',
            'projection_prerequisite': 'Project complete registered owner references, including media, before this atomic admission. Existing source count must equal the number of source IDs; metadata dictionaries are not sources.',
            'source_documents': sorted({p for p in paths if p.endswith('.json')} | {FILE}),
            'input_sha256': {p: pin(p) for p in sorted(paths)}}


def evidence():
    document = build_contract()
    if method.encoded(document) != (ROOT/FILE).read_bytes():
        raise ValueError('Changed Brazil regional-reach query contract; explicitly rebuild after review')
    return document, {**document['input_sha256'], FILE: pin(FILE)}


def records(document):
    return [(COLLECTION, document['record']), ('claims', document['claim']),
            ('sources', document['source_record']), ('sources', document['method_source'])]


def append(collections, document):
    if method.encoded(document) != (ROOT/FILE).read_bytes():
        raise ValueError('Unverified Brazil regional-reach query contract')
    owners = [row for row in collections.get('objects', []) if row['id'] == ENTITY]
    if len(owners) != 1:
        raise ValueError('Missing or duplicate Brazil regional-reach owner')
    owner = owners[0]
    for field in ['regional_reach_ids', 'source_ids']:
        values = owner.get(field, [])
        if (not isinstance(values, list) or any(not isinstance(v, str) for v in values)
                or len(values) != len(set(values))):
            raise ValueError('Invalid or duplicate Brazil owner references')
    if ID in owner.get('regional_reach_ids', []):
        raise ValueError('Duplicate Brazil regional-reach owner reference')
    existing_sources = [row['id'] for row in collections.get('sources', [])]
    if len(existing_sources) != len(set(existing_sources)):
        raise ValueError('Duplicate existing source records')
    if any(ref not in existing_sources for ref in owner.get('source_ids', [])):
        raise ValueError('Unresolved existing Brazil source reference')
    if 'linked_source_count' in owner and (isinstance(owner['linked_source_count'], bool)
            or not isinstance(owner['linked_source_count'], int)
            or owner['linked_source_count'] != len(owner.get('source_ids', []))):
        raise ValueError('Existing Brazil source count differs from references')
    additions = records(document)
    for collection, row in additions:
        if any(old['id'] == row['id'] for old in collections.get(collection, [])):
            raise ValueError('Duplicate Brazil regional-reach query record')
    # All rejection checks precede all mutations. Existing dimensions remain exact.
    for collection, row in additions:
        collections.setdefault(collection, []).append(copy.deepcopy(row))
    owner.setdefault('regional_reach_ids', []).append(ID)
    owner['source_ids'] = sorted(set(owner.get('source_ids', [])) | {SOURCE_ID, METHOD_ID})
    owner['linked_source_count'] = len(owner['source_ids'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build', 'check'])
    args = parser.parse_args()
    if args.command == 'build':
        (ROOT/FILE).write_bytes(method.encoded(build_contract()))
    else:
        evidence()
    print('PASS prepared Brazil regional-reach query contract '+args.command)


if __name__ == '__main__':
    main()
