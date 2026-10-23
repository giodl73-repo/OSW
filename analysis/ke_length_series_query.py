"""Delivery admission for frozen regional graph readings; no new calculation."""
import argparse
import copy
import hashlib
import json
from urllib.parse import quote

import ke_qiu_plot_pathlength_v4 as method
from build_ocean_motion_claims import review_fingerprint

ROOT = method.ROOT
OPERATOR = 'analysis/ke_length_series_query.py'
FILE = 'research/ke-qiu-regional-length-query-contract-v1.json'
BASE = 'research/ocean-current-measurements-aleutian-edition.json'
ENTITY = 'current:kuroshio-extension'
SOURCE_ID = 'source:ke-qiu-2023-figure2a-original'
METHOD_ID = 'source:ke-qiu-plot-pathlength-v4'
MEASUREMENT_ID = 'measurement:ke-qiu-2023:regional-plot-length-range'
CLAIM_ID = 'claim:' + MEASUREMENT_ID
encoded = method.encoded


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def scientific_report():
    document = method.build()
    if encoded(document) != (ROOT / method.REPORT).read_bytes():
        raise ValueError('Changed frozen KE graph-reading report')
    if method.figure(document) != (ROOT / method.FIGURE).read_bytes():
        raise ValueError('Changed frozen KE graph-reading figure')
    return document


def prior_assessment():
    rows = json.loads((ROOT / BASE).read_text(encoding='utf8'))['length_assessments']
    found = [r for r in rows if r['entity_id'] == ENTITY]
    if len(found) != 1:
        raise ValueError('Ambiguous declared prior KE length assessment')
    return copy.deepcopy(found[0])


def build_contract():
    report = scientific_report()
    source = report['source']
    locator = 'Qiu, Chen and Oka2023, Figure2a and caption, original PDF page4; sections2 and3.1, PDF page3.'
    scope = ('Editorial readings of the published upstream141E–153E pathlength graphic. '
             'The graphic range includes retained original knots and bounded cubic graph readings, '
             'not extra observations. Approximate graph years have no recovered calendar dates '
             'or verified sample cadence. Not a whole-current length, physical annual extrema, '
             'seasonal envelope, geographic centerline or width.')
    value = report['plotted_graph_reading_range_km']
    measurement = {'id': MEASUREMENT_ID, 'claim_id': CLAIM_ID, 'entity_id': ENTITY,
                   'quantity': 'regional_plotted_length_range', 'value': value, 'unit': 'km',
                   'evidence_status': 'regional_plot_series', 'rank_eligible': False,
                   'source_id': SOURCE_ID, 'source_locator': locator, 'scope': scope,
                   'method_source_id': METHOD_ID, 'method_file': method.PROTOCOL,
                   'series_id': report['id'], 'scientific_report_file': method.REPORT,
                   'length_reading_allowance_km': 50, 'fractional_year_reading_allowance': .1,
                   'allowance_kind': report['allowance_kind'], 'observation_time': None,
                   'uncertainty_km': None, 'fixed_layer_bounds_m': None,
                   'annual_length_range_km': None, 'whole_current_representative': False,
                   'geographic_centerline': None, 'historical_release_admitted': False}
    claim = {'id': CLAIM_ID, 'subject_id': ENTITY, 'object_id': None,
             'predicate': measurement['quantity'], 'value': value, 'unit': 'km',
             'target_collection': 'measurements', 'target_id': MEASUREMENT_ID,
             'source_id': SOURCE_ID, 'source_locator': locator, 'source_locator_status': 'specific',
             'evidence_class': 'editorial_vector_graph_reading',
             'assertion_status': 'reported_or_derived_measurement', 'scope': scope,
             'method_source_id': METHOD_ID, 'method': method.PROTOCOL, 'method_status': 'described',
             'source_date': None, 'publication_year': 2023, 'source_snapshot_id': None,
             'support_claim_id': None, 'observation_time': None, 'review_status': 'not_individually_reviewed',
             'reviewer': None, 'review_date': None,
             'review_note': 'Internal original-source and arithmetic checks; no external scientific review claimed.'}
    claim['review_fingerprint'] = review_fingerprint(claim)
    assessment = prior_assessment()
    assessment.update(evidence_status='regional_plot_series',
                      whole_current_evidence_status='unmeasured',
                      length_source_id=SOURCE_ID, length_source_locator=locator,
                      regional_length_series_id=report['id'], regional_plotted_length_range_km=value,
                      range_kind='published_graphic_reading_range',
                      length_reading_allowance_km=50, fractional_year_reading_allowance=.1,
                      measurement_id=MEASUREMENT_ID, measurement_admission_file=FILE, scope=scope)
    primary = {'id': SOURCE_ID, 'kind': 'paper', 'label': 'Qiu, Chen and Oka2023 upstream KE pathlength graphic',
               'url': source['original_url'], 'doi': source['doi'], 'title': source['citation'],
               'source_locator': locator, 'source_facts_file': method.v1.FACTS,
               'original_sha256': source['original_sha256'], 'original_bytes': source['original_bytes'],
               'original_pages': source['original_pages'], 'material_use_class': 'metadata_and_factual_extraction',
               'provider_asset_redistributed': False,
               'metadata_note': 'Selected original pages1,3,4 reviewed; complete original and source figure not redistributed. Factual graphics commands and derived readings retained.'}
    internal = {'id': METHOD_ID, 'kind': 'internal', 'label': 'OSW upstream KE graph-reading protocol v4',
                'url': '../' + method.PROTOCOL, 'path': method.PROTOCOL, 'repository_path': method.PROTOCOL,
                'title': 'Kuroshio Extension regional graphic length readings v4',
                'material_use_class': 'internal_calculation_method', 'provider_asset_redistributed': False,
                'used_in_collections': ['current_length_series', 'current_length_readings', 'length_assessments', 'measurements', 'claims'],
                'metadata_note': 'Complete graph geometry and approximate readings; editorial allowances do not supply physical uncertainties or seasonal ranges.'}
    header = {k: copy.deepcopy(v) for k, v in report.items() if k != 'samples'}
    header.update(schema='osw.ke-regional-length-query-contract.v1',
                  scientific_report_schema=report['schema'], scientific_report_file=method.REPORT,
                  scientific_report_sha256=sha(method.REPORT), figure_file=method.FIGURE,
                  figure_sha256=sha(method.FIGURE), sample_collection='current_length_readings',
                  source_facts_phase='reviewed_before_numeric_extraction',
                  measurement=measurement, claim=claim, length_assessment=assessment,
                  source_record=primary, method_source=internal)
    header['input_sha256'].update({p: sha(p) for p in [method.REPORT, method.FIGURE, BASE, OPERATOR,
                                                    'analysis/build_ocean_motion_claims.py']})
    return header


def evidence():
    header = build_contract()
    if encoded(header) != (ROOT / FILE).read_bytes():
        raise ValueError('Changed KE delivery contract; review/refresh before consuming build')
    return header, {**header['input_sha256'], FILE: sha(FILE)}


def reading_rows(header):
    report = json.loads((ROOT / method.REPORT).read_text(encoding='utf8'))
    return [{**copy.deepcopy(row), 'series_id': header['id'], 'graph_reading_order': index,
             'source_id': SOURCE_ID, 'method_source_id': METHOD_ID}
            for index, row in enumerate(report['samples'])]


def records(header):
    return [('current_length_series', header),
            *[('current_length_readings', row) for row in reading_rows(header)],
            ('measurements', header['measurement']), ('claims', header['claim']),
            ('sources', header['source_record']), ('sources', header['method_source'])]


def append(collections, header):
    if encoded(header) != (ROOT / FILE).read_bytes():
        raise ValueError('Unverified KE delivery header')
    rows = collections['length_assessments']
    matches = [i for i, row in enumerate(rows) if row['entity_id'] == ENTITY]
    if len(matches) != 1 or rows[matches[0]] != prior_assessment():
        raise ValueError('Renew declared prior KE length assessment')
    additions = records(header)
    existing = {name: {row['id'] for row in rows} for name, rows in collections.items()}
    for name, row in additions:
        ids = existing.setdefault(name, set())
        if row['id'] in ids:
            raise ValueError('Duplicate KE series record: ' + row['id'])
        ids.add(row['id'])
    rows[matches[0]] = copy.deepcopy(header['length_assessment'])
    for name, row in additions:
        collections.setdefault(name, []).append(copy.deepcopy(row))


def links(header):
    def query(label, collection, field, value, limit=1, sort=None):
        request = {'collection': collection, 'filters': [{'field': field, 'op': 'eq', 'value': value}], 'limit': limit}
        if sort:
            request['sort'] = {'field': sort, 'direction': 'asc'}
        return {'label': label, 'url': 'query.html?q=' + quote(json.dumps(request, separators=(',', ':')), safe='')}
    low, high = header['plotted_graph_reading_range_km']
    return [{'label': f'View regional plotted lengths: {low:,}–{high:,} km', 'url': '../' + method.FIGURE},
            query('Query the regional length series and provenance', 'current_length_series', 'id', header['id']),
            query(f"Explore all {header['graph_reading_count']:,} graph readings", 'current_length_readings', 'series_id', header['id'], 100, 'graph_reading_order'),
            query('Read the selected original-source custody', 'sources', 'id', SOURCE_ID),
            query('Query the qualified KE length assessment', 'length_assessments', 'entity_id', ENTITY)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build', 'check'])
    parser.add_argument('--refresh-contract', action='store_true')
    args = parser.parse_args()
    if args.command == 'build':
        raw = encoded(build_contract())
        target = ROOT / FILE
        if target.exists() and target.read_bytes() != raw and not args.refresh_contract:
            raise ValueError('Review delivery edits and explicitly refresh contract before rebuilding')
        target.write_bytes(raw)
    evidence()
    print('KE series delivery contract: PASS')


if __name__ == '__main__':
    main()
