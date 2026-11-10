"""Typed query projection; numerical scientific cases retain their source scope."""
from pathlib import Path
import json
import kuroshio_wang_dimensions as source

ROOT = source.ROOT
FILE = 'research/kuroshio-wang-2024-query-contract.json'
PROTOCOL = 'plans/kuroshio-wang-query-atlas-protocol-v1.md'
OPERATOR = 'analysis/kuroshio_wang_query.py'
COLLECTION = 'current_dimension_samples'
ID = 'diagnostic:kuroshio-wang-2024-dimensions'
SOURCE_ID = 'source:kuroshio-wang-2026-v1'


def sample_id(row, latitude=None):
    prefix=f'dimension:kuroshio:wang-v1:{row["date"]}:z{row["source_level"]:02d}:'
    return prefix+('axis-18n-30n-v1' if latitude is None else 'span-'+format(latitude,'g').replace('.','p')+'n-v1')


def samples(doc):
    rows = []
    for i, r in enumerate(doc['daily']):
        common = {'entity_id': 'current:kuroshio', 'current_id': 'kuroshio',
                  'sample_date': r['date'], 'nominal_depth_m': r['nominal_depth_m'],
                  'source_level': r['source_level'], 'report_case_index': i,
                  'source_id': SOURCE_ID, 'diagnostic_id': ID,
                  'evidence_class': 'model_derived', 'rank_eligible': False,
                  'uncertainty_km': None}
        rows.append({**common, 'id': sample_id(r), 'quantity': 'regional_axis_length',
                     'status': r['axis']['status'], 'value_km': r['axis']['length_km']})
        for s in r['sections']:
            rows.append({**common, 'id': sample_id(r,s['latitude']),
                         'quantity': 'fixed_latitude_boundary_span', 'section_latitude': s['latitude'],
                         'status': s['status'], 'value_km': s['span_km'],
                         'boundary_fallback_occurred': None})
    return rows


def build():
    doc = source.verify_inputs()
    return {'schema': 'osw.kuroshio-regional-query-contract.v1', 'version': '1',
            'source_report_file': source.FILE, 'source_report_sha256': source.digest(source.FILE),
            'scientific_scope_note': 'The scientific extraction carries no live interface flag; this contract declares the integration edition.',
            'input_sha256': {**doc['input_sha256'], **{p: source.digest(p) for p in [source.FILE, source.FIGURE, PROTOCOL, OPERATOR]}},
            'sample_collection': COLLECTION, 'sample_count': 6588, 'diagnostic_id': ID,
            'sample_id_rule': 'Source edition, date, source depth level, metric/gates and analysis v1. Independent of extraction order; case index is only a snapshot-scoped source pointer.',
            'source_record': {'id': SOURCE_ID, 'kind': 'external',
                              'label': 'Wang et al.2026 Kuroshio daily axis/boundary dataset v1',
                              'title': 'A daily three-dimensional dataset of the Kuroshio axis and boundaries in the East China Sea and Luzon Strait',
                              'url': 'https://doi.org/10.6084/m9.figshare.30267070.v1',
                              'doi': '10.6084/m9.figshare.30267070.v1',
                              'preferred_citation': doc['source']['attribution'],
                              'license': 'CC BY4.0', 'license_url': doc['source']['license_url'],
                              'provider_asset_redistributed': True, 'path': None,
                              'used_in_collections': ['objects', COLLECTION, 'diagnostics'],
                              'material_use_class': 'licensed_provider_model_geometry_and_osw_regional_derivatives',
                              'metadata_note': 'Entire2024 original retained byte-exact in gzip;366 days,30 source levels;3 levels extracted. Model boundaries have unknown search-fallback censoring.'},
            'scope': 'Dated regional model-axis lengths and oblique fixed-section boundary spans, not whole-current or perpendicular widths; no inventory admission.'}


def verify_inputs():
    contract = json.loads((ROOT/FILE).read_bytes())
    if contract != build(): raise ValueError('Stale Kuroshio query integration contract')
    return contract, source.verify_inputs()


def record(doc):
    return {'id': ID, 'label': 'Kuroshio2024 regional model dimensions and dated maps',
            'entity_id': 'current:kuroshio', 'current_id': 'kuroshio',
            'rank_eligible': False, 'source_file': source.FILE,
            'source_file_sha256': source.digest(source.FILE),
            'source_json': (ROOT/source.FILE).read_text(encoding='utf8'),
            'summary': {k: doc[k] for k in ['status', 'counts', 'axis_status_counts', 'section_status_counts', 'conventions']}}


if __name__ == '__main__':
    (ROOT/FILE).write_bytes(source.encoded(build()))
    print('Built Kuroshio query contract;6588 typed attempts, no inventory promotion.')
