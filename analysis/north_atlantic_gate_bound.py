"""Working nominal-section geographic floor, separate from whole-current length."""
import copy
import hashlib
import json
import math
import xml.etree.ElementTree as ET
from itertools import product
from pathlib import Path

from pyproj import Geod
from build_ocean_motion_claims import review_fingerprint

ROOT = Path(__file__).resolve().parents[1]
FILE = 'research/north-atlantic-nominal-gate-bound.json'
PROTOCOL = 'plans/north-atlantic-nominal-gate-bound-protocol-v1.md'
OPERATOR = 'analysis/north_atlantic_gate_bound.py'
ORIGINAL = 'research/source-data/cainzos-atlantic-2023/article.xml'
ACQUISITION = 'research/source-data/cainzos-atlantic-2023/article-acquisition.json'
FIGURE = 'figures/north-atlantic-nominal-gate-bound.svg'
ENTITY = 'current:north-atlantic'
SOURCE_ID = 'source:21f756d2b07063f3'
METHOD_ID = 'source:north-atlantic-nominal-gate-bound-v1'
MEASUREMENT_ID = 'measurement:north-atlantic:nominal-section-floor'
BASE = 'almanac/release/v0.1.0/'


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def encoded(doc):
    return (json.dumps(doc, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')


def source_check():
    receipt = json.loads((ROOT / ACQUISITION).read_bytes())
    if (receipt['sha256'], receipt['bytes'], receipt['doi'], receipt['license']) != (
        digest(ORIGINAL), (ROOT / ORIGINAL).stat().st_size,
        '10.5194/os-19-1009-2023', 'CC BY 4.0'):
        raise ValueError('Changed original article acquisition')
    root = ET.parse(ROOT / ORIGINAL).getroot()
    sections = {s.get('id'): ' '.join(''.join(s.itertext()).split()) for s in root.iter('sec')}
    nac = sections['Ch1.S3.SS1.SSS10']
    methods = sections['Ch1.S2']
    for phrase in ['47∘', '58∘', 'flows northeastward and reaches the section']:
        if phrase not in nac:
            raise ValueError('Missing original NAC source gates')
    for phrase in ['Deviations of some stations from the nominal latitude', 'western', 'eastern']:
        if phrase not in methods:
            raise ValueError('Missing nominal-section warning')


def calculation(start=47.0, end=58.0):
    if not (-90 <= start < end <= 90):
        raise ValueError('Ordered valid latitudes required')
    geod = Geod(ellps='WGS84')
    separation = lambda a, b: round(geod.inv(0, a, 0, b)[2] / 1000, 6)
    distance = separation(start, end)
    scenarios = [{'start_shift_degrees': a, 'end_shift_degrees': b,
                  'nominal_latitudes_degrees_north': [start + a, end + b],
                  'geographic_separation_km': separation(start + a, end + b)}
                 for a, b in product([-0.5, 0.0, 0.5], repeat=2)]
    return {'nominal_latitudes_degrees_north': [start, end],
            'direct_gate_distance_km': distance,
            'rounded_conditional_geographic_floor_km': math.floor(distance / 100) * 100,
            'scenario_min_km': min(s['geographic_separation_km'] for s in scenarios),
            'scenario_max_km': max(s['geographic_separation_km'] for s in scenarios),
            'scenario_count': 9, 'scenarios': scenarios}


def figure(calc):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 450" role="img" aria-labelledby="title desc">
<title id="title">North Atlantic Current nominal-section geographic bound</title>
<desc id="desc">A scalar summary of nominal 47 and 58 degrees north sections. Their WGS84 meridional separation is {calc['direct_gate_distance_km']:.1f} kilometres, rounded down to a conditional 1200 kilometre geographic floor. Not a mapped current route or whole-current length. Section positions, layers and cruises differ. No whole-current length ranking or annual range.</desc>
<rect width="920" height="450" fill="#eef6f8"/>
<g font-family="Arial, sans-serif" fill="#123c4b">
<text x="28" y="42" font-size="25" font-weight="bold">North Atlantic Current · regional geographic bound</text>
<text x="28" y="84" font-size="19">Nominal source sections: 47°N → 58°N</text>
<text x="28" y="138" font-size="34" font-weight="bold">1,200 km · conditional floor · unranked</text>
<text x="28" y="178" font-size="18">WGS84 meridional separation: {calc['direct_gate_distance_km']:.1f} km</text>
<path d="M28 203H892" stroke="#587681"/>
<text x="28" y="238" font-size="17">Actual stations deviate from nominal sections; cruises and layers differ.</text>
<text x="28" y="270" font-size="17">No continuous axis, actual endpoints or guaranteed physical minimum.</text>
<text x="28" y="308" font-size="17">Nine ±0.5° editorial gate scenarios: {calc['scenario_min_km']:.1f}–{calc['scenario_max_km']:.1f} km.</text>
<text x="28" y="338" font-size="17">These scenarios are not measured uncertainty or a seasonal length range.</text>
<text x="28" y="382" font-size="16">Caínzos et al. (2023), §2 and §3.1.10 · doi:10.5194/os-19-1009-2023</text>
<text x="28" y="418" font-size="16">OSW scalar calculation · original article CC BY 4.0 · 12 ranked lengths remain</text>
</g></svg>'''.encode('utf-8')


def build():
    source_check()
    calc = calculation()
    scope = ('Conditional geographic floor between nominal 47°N and eastern 58°N sections identified as North Atlantic Current by Caínzos et al. (2023). '
             'Station latitudes deviate from nominal sections; the northern section combines western 53°N and eastern 58°N portions. '
             'Cruises, sampled branches and density layers differ. No simultaneous connected axis, common fixed layer or actual geographic endpoints inferred. '
             'Not a whole-current length or guaranteed physical minimum.')
    locator = 'Sections 2 and 3.1.10; nominal NAC sections at 47°N and eastern 58°N; OSW WGS84 latitude separation'
    measurement = {'id': MEASUREMENT_ID, 'claim_id': 'claim:' + MEASUREMENT_ID,
                   'entity_id': ENTITY, 'quantity': 'length_lower_bound', 'value': calc['rounded_conditional_geographic_floor_km'],
                   'unit': 'km', 'rank_eligible': False, 'evidence_status': 'derived_lower_bound',
                   'source_id': SOURCE_ID, 'source_locator': locator, 'scope': scope,
                   'method_source_id': METHOD_ID, 'method_file': PROTOCOL, 'gate_type': 'source_latitude_span',
                   'direct_gate_distance_km': calc['direct_gate_distance_km'],
                   'conditional_on_nominal_gates': True, 'guaranteed_physical_minimum': False,
                   'whole_current_representative': False, 'observation_time': None, 'uncertainty_km': None,
                   'fixed_layer_bounds_m': None, 'endpoint_coordinates_lon_lat': None,
                   'annual_length_range_km': None, 'geometry_id': None, 'historical_release_admitted': False}
    assessment = copy.deepcopy(next(r for r in json.loads((ROOT / (BASE + 'length_assessments.json')).read_bytes()) if r['entity_id'] == ENTITY))
    sensitivity = {k: calc[k] for k in ['scenario_count', 'scenario_min_km', 'scenario_max_km']}
    sensitivity.update(perturbation_degrees=0.5, interpretation='Finite editorial gate scenarios; not a physical error, confidence interval, annual range or source-reported gate-location uncertainty.')
    assessment.update(evidence_status='derived_lower_bound', lower_bound_km=measurement['value'],
                      length_source_id=SOURCE_ID, length_source_locator=locator,
                      gate_distance_method_source_id=METHOD_ID, gate_distance_sensitivity=sensitivity,
                      scope=scope, measurement_id=MEASUREMENT_ID, measurement_admission_file=FILE,
                      conditional_on_nominal_gates=True, guaranteed_physical_minimum=False)
    claim = {'id': measurement['claim_id'], 'subject_id': ENTITY, 'object_id': None,
             'predicate': 'length_lower_bound', 'value': measurement['value'], 'unit': 'km',
             'target_collection': 'measurements', 'target_id': MEASUREMENT_ID,
             'source_id': SOURCE_ID, 'source_locator': locator, 'source_locator_status': 'specific',
             'evidence_class': 'derived_lower_bound', 'assertion_status': 'reported_or_derived_measurement',
             'scope': scope, 'method_source_id': METHOD_ID, 'method': PROTOCOL, 'method_status': 'described',
             'source_date': '2023-07-06', 'source_snapshot_id': None, 'support_claim_id': None,
             'observation_time': None, 'review_status': 'not_individually_reviewed', 'reviewer': None,
             'review_date': None, 'review_note': 'Internal source and arithmetic checks; no external scientific review claimed.'}
    claim['review_fingerprint'] = review_fingerprint(claim)
    method_source = {'id': METHOD_ID, 'kind': 'internal', 'label': 'OSW North Atlantic nominal-section geographic floor protocol v1',
                     'url': '../' + PROTOCOL, 'path': PROTOCOL, 'repository_path': PROTOCOL,
                     'title': 'North Atlantic Current nominal-section geographic bound v1',
                     'material_use_class': 'internal_calculation_method', 'provider_asset_redistributed': False,
                     'used_in_collections': ['measurements', 'claims', 'length_assessments', 'current_length_bound_admissions'],
                     'metadata_note': 'Editorial WGS84 gate calculation; source section geometry is approximate; no whole-current rank.'}
    paths = [PROTOCOL, OPERATOR, ORIGINAL, ACQUISITION, BASE + 'length_assessments.json', BASE + 'sources.json',
             'analysis/build_ocean_motion_claims.py']
    return {'id': 'current_length_bound_admission:north-atlantic', 'schema': 'osw.nominal-section-bound-admission.v1',
            'version': '1', 'entity_id': ENTITY, 'current_id': 'north-atlantic',
            'status': 'conditional_nominal_section_geographic_floor_admitted_unranked',
            'source_url': 'https://os.copernicus.org/articles/19/1009/2023/',
            'source_file': ORIGINAL, 'source_locator': locator,
            'source_citation': 'Caínzos et al. (2023), Ocean Science 19, 1009–1045, doi:10.5194/os-19-1009-2023',
            'source_license': 'CC BY 4.0', 'calculation': calc, 'measurement': measurement,
            'claim': claim, 'length_assessment': assessment, 'method_source': method_source,
            'figure_file': FIGURE, 'whole_current_length_km': None, 'annual_length_range_km': None,
            'rank_eligible': False, 'physical_state_join_eligible': False,
            'input_sha256': {**{p: digest(p) for p in paths}, FIGURE: hashlib.sha256(figure(calc)).hexdigest()}}


def verify_inputs():
    doc = build()
    if (ROOT / FILE).read_bytes() != encoded(doc) or (ROOT / FIGURE).read_bytes() != figure(doc['calculation']):
        raise ValueError('Changed North Atlantic nominal-section admission or figure')
    return doc, {**doc['input_sha256'], FILE: digest(FILE), FIGURE: digest(FIGURE)}


def append(collections, doc):
    rows = collections['length_assessments']
    matches = [i for i, r in enumerate(rows) if r['entity_id'] == ENTITY]
    if len(matches) != 1 or rows[matches[0]]['evidence_status'] != 'no_numeric_length':
        raise ValueError('Renew North Atlantic prior-assessment admission')
    rows[matches[0]] = doc['length_assessment']
    for name, key in [('measurements', 'measurement'), ('claims', 'claim'), ('sources', 'method_source')]:
        if any(r['id'] == doc[key]['id'] for r in collections[name]):
            raise ValueError('Duplicate nominal-section admission')
        collections[name].append(doc[key])
    collections['current_length_bound_admissions'] = [doc]


if __name__ == '__main__':
    doc = build()
    (ROOT / FILE).write_bytes(encoded(doc))
    (ROOT / FIGURE).write_bytes(figure(doc['calculation']))
    print(json.dumps(doc['calculation']))
