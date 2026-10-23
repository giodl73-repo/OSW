"""Prospective described-latitude floor; no mapped or whole-current length."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path

from north_atlantic_gate_bound import calculation as established_gate_operator
from build_ocean_motion_claims import review_fingerprint

ROOT = Path(__file__).resolve().parents[1]
REPORT = 'research/labrador-latitude-gate-bound-v1.json'
FIGURE = 'figures/labrador-latitude-gate-bound-v1.svg'
PROTOCOL = 'plans/labrador-latitude-gate-bound-protocol-v1.md'
PREFLIGHT = 'research/labrador-latitude-gate-bound-preflight-v1.json'
OPERATOR = 'analysis/labrador_latitude_gate_bound_v1.py'
TEST = 'analysis/test_labrador_latitude_gate_bound_v1.py'
FACTS = 'research/labrador-thompson-2009-original-custody-followup.json'
BASE = 'research/ocean-current-measurements-aleutian-edition.json'
ENTITY = 'current:labrador'
SOURCE_ID = 'source:labrador-thompson-2009-selected-original'
METHOD_ID = 'source:labrador-latitude-gate-bound-v1'
MEASUREMENT_ID = 'measurement:labrador:described-latitude-floor'
INPUTS = [OPERATOR, TEST, PROTOCOL, FACTS, BASE,
          'analysis/north_atlantic_gate_bound.py',
          'analysis/build_ocean_motion_claims.py',
          'research/labrador-thompson-2009-regional-width-scope-audit.json']


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf8')


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def input_pins():
    return {path: digest(path) for path in INPUTS}


def source_facts(document):
    if (document['current_id'] != 'labrador'
            or document['source_doi'] != '10.1029/2008JC004859'
            or document['reported_regional_latitudes_degrees_north'] != [43, 60]
            or document['original_sha256'] != '1bbfdaf1c19dba0c6a274a8b06345e7dc0bd73b2980dc17e347fad985387bfdc'
            or document['original_bytes'] != 572833
            or document['original_pages'] != 11
            or document['selected_pdf_pages_visually_reviewed'] != [6, 7]
            or document['original_redistributed'] is not False
            or document['new_numeric_calculation_performed'] is not False):
        raise ValueError('Changed reviewed original-source facts or support')
    return copy.deepcopy(document)


def calculate_gates(lower, upper):
    if (any(type(v) not in (int, float) or not math.isfinite(v) for v in (lower, upper))
            or not (-89.5 <= lower < upper <= 89.5)
            or upper - lower <= 1):
        raise ValueError('Finite ordered latitude gates with all nine scenarios in range required')
    return established_gate_operator(lower, upper)


def figure(calc):
    floor = calc['rounded_conditional_geographic_floor_km']
    low, high = calc['nominal_latitudes_degrees_north']
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 470" role="img" aria-labelledby="title desc">
<title id="title">Labrador Current: described latitude-gate separation</title>
<desc id="desc">Conditional geographic floor from a regional prose description. Not a mapped current route or whole-current length. Nine editorial gate scenarios are not physical uncertainty or seasonal variability.</desc>
<style>text{{font-family:system-ui,sans-serif;fill:#e8f4f5}}.small{{font-size:17px}}</style>
<rect width="960" height="470" rx="12" fill="#102733"/>
<text x="34" y="46" font-size="28">Labrador Current · described latitude span</text>
<text x="34" y="94" font-size="32">{floor:,.0f} km · conditional geographic floor</text>
<text x="34" y="128" class="small">Rounded down to 100 km; no measured centerline or guaranteed physical minimum.</text>
<path d="M110 197 H850" stroke="#71cbdc" stroke-width="12"/>
<path d="M110 180 V214 M850 180 V214" stroke="#e8f4f5" stroke-width="3"/>
<text x="72" y="249" class="small">Southern gate {low:g}°N</text>
<text x="673" y="249" class="small">Northern gate {high:g}°N</text>
<text x="34" y="292" class="small">Nominal WGS84 latitude separation: {calc['direct_gate_distance_km']:,.1f} km.</text>
<text x="34" y="324" class="small">Nine ±0.5° gate scenarios: {calc['scenario_min_km']:,.1f}–{calc['scenario_max_km']:,.1f} km.</text>
<text x="34" y="356" class="small">Editorial sensitivity only; no annual range, confidence interval or source position error.</text>
<text x="34" y="391" class="small">Thompson et al. (2009), §4.2 ¶29, original PDF pages 6–7. Branches differ.</text>
<text x="34" y="426" class="small">Diagram is scalar. The calculation meridian is not a current location.</text>
</svg>'''.encode('utf8')


def declare():
    if any((ROOT / path).exists() for path in (PREFLIGHT, REPORT, FIGURE)):
        raise ValueError('Retain declarations/products and use a new version')
    result = {'schema': 'osw.labrador-latitude-bound-preflight.v1',
              'phase': 'prospective_declaration', 'input_sha256': input_pins(),
              'actual_labrador_gate_distance_calculated': False,
              'source_prose_and_original_pages_previously_inspected': True,
              'whole_current_length_admitted': False}
    (ROOT / PREFLIGHT).write_bytes(encoded(result))
    return result


def build():
    declaration = json.loads((ROOT / PREFLIGHT).read_bytes())
    if (declaration['input_sha256'] != input_pins()
            or declaration['actual_labrador_gate_distance_calculated'] is not False):
        raise ValueError('Changed prospective latitude-bound inputs')
    facts = source_facts(json.loads((ROOT / FACTS).read_bytes()))
    calc = calculate_gates(*facts['reported_regional_latitudes_degrees_north'])
    locator = 'Thompson et al. (2009), section4.2 paragraph29, PDF pages6–7; regional 43–60°N description'
    scope = ('Conditional WGS84 geographic floor between described regional latitude gates. '
             'Hudson Strait and the tail of Grand Bank delimit a shelf/slope prose description; '
             'onshore branches and Flemish Cap bifurcation differ. No dated connected axis, '
             'precise geographic endpoints or common fixed layer is established. '
             'Not a measured whole-current length or guaranteed physical minimum.')
    measurement = {'id': MEASUREMENT_ID, 'claim_id': 'claim:' + MEASUREMENT_ID,
                   'entity_id': ENTITY, 'quantity': 'length_lower_bound',
                   'value': calc['rounded_conditional_geographic_floor_km'], 'unit': 'km',
                   'rank_eligible': False, 'evidence_status': 'derived_lower_bound',
                   'source_id': SOURCE_ID, 'source_locator': locator, 'scope': scope,
                   'method_source_id': METHOD_ID, 'method_file': PROTOCOL,
                   'gate_type': 'source_latitude_span',
                   'direct_gate_distance_km': calc['direct_gate_distance_km'],
                   'conditional_on_nominal_gates': True, 'guaranteed_physical_minimum': False,
                   'whole_current_representative': False, 'observation_time': None,
                   'uncertainty_km': None, 'fixed_layer_bounds_m': None,
                   'endpoint_coordinates_lon_lat': None, 'annual_length_range_km': None,
                   'geometry_id': None, 'historical_release_admitted': False}
    assessment = copy.deepcopy(next(r for r in json.loads((ROOT / BASE).read_bytes())['length_assessments'] if r['entity_id'] == ENTITY))
    if assessment['evidence_status'] != 'no_numeric_length' or assessment['rank_eligible'] is not False:
        raise ValueError('Renew the prior Labrador assessment declaration')
    sensitivity = {key: calc[key] for key in ('scenario_count', 'scenario_min_km', 'scenario_max_km')}
    sensitivity.update(perturbation_degrees=0.5,
                       interpretation='Finite editorial gate scenarios; not physical uncertainty, source position errors, confidence intervals or seasonal extrema.')
    assessment.update(evidence_status='derived_lower_bound', lower_bound_km=measurement['value'],
                      length_source_id=SOURCE_ID, length_source_locator=locator,
                      gate_distance_method_source_id=METHOD_ID, gate_distance_sensitivity=sensitivity,
                      scope=scope, measurement_id=MEASUREMENT_ID, measurement_admission_file=REPORT,
                      conditional_on_nominal_gates=True, guaranteed_physical_minimum=False)
    claim = {'id': measurement['claim_id'], 'subject_id': ENTITY, 'object_id': None,
             'predicate': 'length_lower_bound', 'value': measurement['value'], 'unit': 'km',
             'target_collection': 'measurements', 'target_id': MEASUREMENT_ID,
             'source_id': SOURCE_ID, 'source_locator': locator, 'source_locator_status': 'specific',
             'evidence_class': 'derived_lower_bound', 'assertion_status': 'reported_or_derived_measurement',
             'scope': scope, 'method_source_id': METHOD_ID, 'method': PROTOCOL,
             'method_status': 'described', 'source_date': '2009-07-15',
             'source_snapshot_id': None, 'support_claim_id': None, 'observation_time': None,
             'review_status': 'not_individually_reviewed', 'reviewer': None, 'review_date': None,
             'review_note': 'Internal source and arithmetic checks; no external scientific review claimed.'}
    claim['review_fingerprint'] = review_fingerprint(claim)
    source_record = {'id': SOURCE_ID, 'kind': 'paper',
                     'label': 'Thompson et al.2009 selected original Labrador description',
                     'url': facts['original_url'], 'doi': facts['source_doi'],
                     'title': 'Mean surface topography of the northwest Atlantic: Comparison of estimates based on satellite, terrestrial gravity, and oceanographic observations',
                     'source_locator': locator, 'source_facts_file': FACTS,
                     'original_sha256': facts['original_sha256'],
                     'material_use_class': 'metadata_and_factual_extraction',
                     'provider_asset_redistributed': False,
                     'metadata_note': 'Selected original PDF pages6–7 visually reviewed; original retained privately, no original or source figure redistributed. Regional prose is not a measured axis.'}
    method_source = {'id': METHOD_ID, 'kind': 'internal',
                     'label': 'OSW Labrador described-latitude geographic floor protocol v1',
                     'url': '../' + PROTOCOL, 'path': PROTOCOL, 'repository_path': PROTOCOL,
                     'title': 'Labrador latitude-gate geographic bound v1',
                     'material_use_class': 'internal_calculation_method', 'provider_asset_redistributed': False,
                     'used_in_collections': ['measurements', 'claims', 'length_assessments', 'current_length_bound_admissions'],
                     'metadata_note': 'Same WGS84 calculation, 100km downward rounding and nine gate scenarios as the frozen North Atlantic operator. No whole-current rank.'}
    return {'schema': 'osw.labrador-latitude-bound-admission.v1',
            'id': 'current_length_bound_admission:labrador', 'version': '1',
            'entity_id': ENTITY, 'current_id': 'labrador',
            'status': 'conditional_described_latitude_geographic_floor_admitted_unranked',
            'source_url': facts['original_url'], 'source_file': FACTS,
            'source_locator': locator, 'source_doi': facts['source_doi'],
            'original_sha256': facts['original_sha256'], 'original_redistributed': False,
            'source_citation': 'Thompson, Huang, Véronneau, Wright and Lu (2009), JGR114 C07015, doi:10.1029/2008JC004859',
            'calculation': calc, 'measurement': measurement, 'claim': claim,
            'length_assessment': assessment, 'source_record': source_record,
            'method_source': method_source, 'figure_file': FIGURE,
            'whole_current_length_km': None, 'annual_length_range_km': None,
            'rank_eligible': False, 'physical_state_join_eligible': False,
            'original_review_scope': 'Selected PDF pages6–7; full-article or source-figure digitization not claimed.',
            'input_sha256': {**input_pins(), PREFLIGHT: digest(PREFLIGHT),
                             FIGURE: hashlib.sha256(figure(calc)).hexdigest()}}


def verify_inputs():
    report = build()
    if ((ROOT / REPORT).read_bytes() != encoded(report)
            or (ROOT / FIGURE).read_bytes() != figure(report['calculation'])):
        raise ValueError('Changed complete Labrador bound report or scalar figure')
    return report, {**report['input_sha256'], REPORT: digest(REPORT)}


def verify_original(path):
    facts = source_facts(json.loads((ROOT / FACTS).read_bytes()))
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != facts['original_sha256'] or len(raw) != facts['original_bytes']:
        raise ValueError('Different institutional original PDF')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['declare', 'build', 'check', 'original'])
    parser.add_argument('--original-path')
    args = parser.parse_args()
    if args.action == 'declare': declare()
    elif args.action == 'original': verify_original(args.original_path)
    elif args.action == 'check': verify_inputs()
    else:
        if (ROOT / REPORT).exists() or (ROOT / FIGURE).exists():
            raise ValueError('Retain existing products; use check or a new version')
        result = build()
        (ROOT / REPORT).write_bytes(encoded(result))
        (ROOT / FIGURE).write_bytes(figure(result['calculation']))
        print(json.dumps(result['calculation']))
