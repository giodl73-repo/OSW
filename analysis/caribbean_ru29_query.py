"""Canonical source admission; no new physical dimensions or source edits."""
import argparse
import copy
import json
from urllib.parse import quote

import caribbean_ru29_source_fields_v2 as method

ROOT = method.ROOT
FILE = 'research/caribbean-ru29-query-contract-v1.json'
ADAPTER = 'analysis/caribbean_ru29_query.py'
ID = 'diagnostic:caribbean-ru29-2024-source-fields'
SOURCE_ID = 'source:caribbean-ru29-2024-selected-products'
METHOD_ID = 'source:caribbean-ru29-source-readback-v2'
ENTITY = 'current:caribbean'
PAGE = 'almanac/caribbean-source.html'
PAGE_DATA = 'research/caribbean-ru29-source-page-v1.json'


def pin(path):
    return method.v1.sha((ROOT/path).read_bytes())


def source_link(label, document, pointer, limit):
    request = {'document': document, 'pointer': pointer, 'limit': limit, 'offset': 0}
    return {'label': label, 'url': 'query.html?source-q='+quote(json.dumps(request, separators=(',', ':')), safe='')+'#source-query-title'}


def card_links():
    query = {'collection': 'diagnostics', 'filters': [{'field': 'id', 'op': 'eq', 'value': ID}], 'limit': 1}
    return [
        {'label': 'Compare the 2024 Caribbean velocity sections', 'url': 'caribbean-source.html'},
        {'label': 'Query the retained RU29 source diagnostic', 'url': 'query.html?q='+quote(json.dumps(query, separators=(',', ':')), safe='')},
        source_link('Query all eleven original source inventories', method.REPORT, '/members', 11),
        source_link('Query processed mission field coverage', method.REPORT, '/members/adcp-full.nc/variables', 12),
        source_link('Query occupation 1 eastward velocity cells', method.MIRROR, '/members/adcp-transect-1.nc/variables/u_grid/raw_values', 10),
        source_link('Query occupation 2 eastward velocity cells', method.MIRROR, '/members/adcp-transect-2.nc/variables/u_grid/raw_values', 10),
        source_link('Query retained anticyclonic tracking fields', method.REPORT, '/members/sla-anticyclonic-tracked.nc/variables', 28),
        source_link('Query terminal virtual tracking state', method.MIRROR, '/members/sla-anticyclonic-correspondances.nc/groups/LastVirtualObs/variables', 23)]


def build_contract():
    products = method.products()
    for path, raw in products.items():
        if (ROOT/path).read_bytes() != raw:
            raise ValueError('Changed frozen source product: '+path)
    report = json.loads(products[method.REPORT])
    facts = json.loads((ROOT/method.SOURCE/'source-facts.json').read_bytes())
    payload = json.loads((ROOT/PAGE_DATA).read_bytes())
    mirror = json.loads(products[method.MIRROR])
    if payload['source_sha256'] != pin(method.MIRROR) or len(payload['occupations']) != 2:
        raise ValueError('Changed complete occupation source binding')
    for n, occupation in enumerate(payload['occupations'], 1):
        if occupation['source_member'] != f'adcp-transect-{n}.nc' or occupation['source_group'] != mirror['members'][occupation['source_member']]:
            raise ValueError('Changed complete occupation delivery record')
    paths = set(method.INPUTS) | set(method.pins(ROOT)) | {
        method.PREFLIGHT, *products, ADAPTER, PAGE_DATA,
        'analysis/build_caribbean_ru29_source_page.py', PAGE,
        'almanac/caribbean-source.js', 'almanac/caribbean-source.css'}
    inputs = {path: pin(path) for path in sorted(paths)}
    source = {'id': SOURCE_ID, 'kind': 'dataset',
              'label': 'Gradone RU29 2024 selected processed velocity and SLA tracking products',
              'title': facts['dataset_title'], 'url': 'https://doi.org/10.5281/zenodo.18332586',
              'doi': '10.5281/zenodo.18332586', 'license': 'CC BY 4.0',
              'attribution': 'Joseph Gradone / Rutgers University',
              'source_locator': 'Eleven original members of data.zip; exact original paths in custody.json.',
              'material_use_class': 'licensed_selected_original_products_and_complete_factual_readback',
              'provider_asset_redistributed': True, 'whole_archive_checksum_locally_verified': False,
              'custody_file': method.SOURCE+'/custody.json',
              'metadata_note': 'Selected original members are checksum-verified; not the complete archive or a reproduction of raw-beam processing/eddy tracking.'}
    internal = {'id': METHOD_ID, 'kind': 'internal', 'label': 'OSW complete RU29 original-product readback v2',
                'title': 'RU29 original packed values, masks and recursive groups',
                'url': '../plans/caribbean-ru29-source-fields-protocol-v2.md',
                'path': 'plans/caribbean-ru29-source-fields-protocol-v2.md',
                'material_use_class': 'internal_source_readback_method', 'provider_asset_redistributed': False,
                'metadata_note': 'Source retention and visualization; no new physical width, whole-current length or seasonal range.'}
    context = {'id': ID, 'source_id': SOURCE_ID, 'method_source_id': METHOD_ID,
               'source_file': method.REPORT, 'source_sha256': inputs[method.REPORT],
               'source_mirror': method.MIRROR, 'source_mirror_sha256': inputs[method.MIRROR],
               'source_products': 11, 'source_variables': 306, 'retained_source_values': 3609111,
               'processed_mission_profile_slots': 486, 'interpolated_occupations': 2,
               'occupation_windows_utc': facts['occupation_windows_utc'],
               'rank_eligible': False, 'physical_width_admitted': False,
               'whole_current_length_admitted': False, 'seasonal_envelope_admitted': False,
               'eddy_pipeline_reproduced': False,
               'scope': 'Processed source profiles and multiweek interpolated sections; incomplete current width/depth, not simultaneous snapshots or seasonal coverage.'}
    diagnostic = {'id': ID, 'entity_id': ENTITY, 'current_id': 'caribbean',
                  'kind': 'provider_processed_velocity_sections',
                  'label': 'Caribbean RU29 2024 complete processed source fields',
                  'source_id': SOURCE_ID, 'method_source_id': METHOD_ID,
                  'source_file': method.REPORT, 'source_file_sha256': inputs[method.REPORT],
                  'document': report, 'source_json': products[method.REPORT].decode('utf8'),
                  'figure': PAGE, 'rank_eligible': False, 'physical_width_admitted': False,
                  'whole_current_length_admitted': False, 'seasonal_envelope_admitted': False,
                  'source_context': context}
    documents = sorted({p for p in inputs if p.endswith('.json')} | {FILE})
    return {'schema': 'osw.caribbean-ru29.query-contract.v1',
            'id': ID, 'entity_id': ENTITY, 'diagnostic': diagnostic,
            'source_record': source, 'method_source': internal, 'card_context': context,
            'card_links': card_links(), 'source_documents': documents, 'input_sha256': inputs}


def evidence():
    expected = build_contract()
    if method.v1.encoded(expected) != (ROOT/FILE).read_bytes():
        raise ValueError('Changed Caribbean admission contract; explicitly build after review')
    return expected, {**expected['input_sha256'], FILE: pin(FILE)}


def append(collections, document):
    if method.v1.encoded(document) != (ROOT/FILE).read_bytes():
        raise ValueError('Unverified Caribbean source admission')
    planned = [('diagnostics', document['diagnostic']),
               ('sources', document['source_record']), ('sources', document['method_source'])]
    owners = [row for row in collections['objects'] if row['id'] == ENTITY]
    if len(owners) != 1 or any(row.get('id') == ID for row in collections['diagnostics']):
        raise ValueError('Missing/duplicate Caribbean source owner or diagnostic')
    if not isinstance(owners[0].get('diagnostic_ids', []), list) or ID in owners[0].get('diagnostic_ids', []):
        raise ValueError('Invalid/duplicate Caribbean diagnostic owner join')
    source_ids = owners[0].get('source_ids', [])
    if not isinstance(source_ids, list) or any(not isinstance(value, str) for value in source_ids):
        raise ValueError('Invalid Caribbean source owner references')
    joined_sources = sorted(set(source_ids) | {SOURCE_ID, METHOD_ID})
    for collection, row in planned:
        if any(existing['id'] == row['id'] for existing in collections[collection]):
            raise ValueError('Duplicate Caribbean admission record')
    for collection, row in planned:
        collections[collection].append(copy.deepcopy(row))
    owners[0].setdefault('diagnostic_ids', []).append(ID)
    owners[0]['source_ids'] = joined_sources


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['build', 'check'])
    args = parser.parse_args()
    if args.command == 'build':
        (ROOT/FILE).write_bytes(method.v1.encoded(build_contract()))
    else:
        evidence()
    print('PASS Caribbean source admission '+args.command)


if __name__ == '__main__':
    main()
