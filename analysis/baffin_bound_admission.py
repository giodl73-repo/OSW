"""Prepare immutable Baffin source results for a separate working-delivery gate."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from urllib.parse import quote

from build_ocean_motion_claims import review_fingerprint

ROOT = Path(__file__).resolve().parents[1]
FILE = 'research/baffin-latitude-bound-admission-v1.json'
ADAPTER = 'analysis/baffin_bound_admission.py'
REPORT = 'research/baffin-latitude-gate-bound-v1.json'
FIGURE = 'figures/baffin-latitude-gate-bound-v1.svg'
PROOF = 'research/baffin-latitude-gate-bound-execution-proof-v1.json'
BASE = 'research/ocean-current-measurements-aleutian-edition.json'
ENTITIES = 'almanac/release/v0.1.0/entities.json'
ENTITY = 'current:baffin'
PAPER = 'source:baffin-fissel-1982-length-selected-original'
METHOD = 'source:baffin-latitude-gate-bound-v1'
MEASUREMENT = 'measurement:baffin:described-latitude-floor'
ADMISSION = 'current_length_bound_admission:baffin:described-latitudes-v1'
VERSION_KEY = 'baffin_latitude_gate_bound_version'
OUTPUTS = {
    REPORT: 'd893388cea395d9f19017a5cbd77794d26cad963c7d3ef3b13e4f87e293235e5',
    FIGURE: 'e53513daa3fa8ba62dc4af3547c2dbfab087f6188459dc241ce234365ee9b671',
}


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf8')


def read(path):
    target = (ROOT / path).resolve()
    if not target.is_relative_to(ROOT.resolve()) or not target.is_file():
        raise ValueError('Invalid admission dependency: ' + path)
    return target.read_bytes()


def pin(path):
    return hashlib.sha256(read(path)).hexdigest()


def query_url(collection, field, value, limit=1):
    query = {'collection': collection, 'filters': [{'field': field, 'op': 'eq', 'value': value}], 'limit': limit}
    return 'query.html?q=' + quote(json.dumps(query, separators=(',', ':')), safe='')


def build_contract():
    for path, sha in OUTPUTS.items():
        if pin(path) != sha:
            raise ValueError('Executed scientific output changed: ' + path)
    report = json.loads(read(REPORT))
    proof = json.loads(read(PROOF))
    if (proof['freeze_commit'] != report['freeze_commit']
            or proof['first_execution_commit'] != report['freeze_commit']
            or proof['report_sha256'] != OUTPUTS[REPORT]
            or proof['figure_sha256'] != OUTPUTS[FIGURE]
            or proof['actual_source_calculation_and_independent_integration_passed'] is not True
            or proof['working_dataset_admitted'] is not False):
        raise ValueError('Source execution proof does not bind this report')
    for path, sha in report['input_sha256'].items():
        if pin(path) != sha:
            raise ValueError('Frozen scientific dependency changed: ' + path)
    facts = json.loads(read(report['source_review_file']))
    entities = json.loads(read(ENTITIES))
    if isinstance(entities, dict):
        entities = entities['entities']
    accepted = [r for r in entities if r['id'] == ENTITY]
    if len(accepted) != 1 or accepted[0]['type'] != 'named_current':
        raise ValueError('One accepted Baffin identity is required')
    prior = [r for r in json.loads(read(BASE))['length_assessments'] if r['entity_id'] == ENTITY]
    if (len(prior) != 1 or prior[0]['evidence_status'] != 'no_numeric_length'
            or prior[0]['published_length_km'] is not None or prior[0]['rank_eligible'] is not False):
        raise ValueError('Renew the declared prior Baffin assessment')
    calc = report['calculation']
    scope = ('Conditional WGS84 geographic floor between the source-described 67 and 76 degrees N gates. '
             'Summer near-surface observations in 1978 and 1979; exact gate dates and common fixed layer unknown. '
             'The author extends historical Baffin Current naming north to Lady Ann Strait. '
             'No simultaneous connected axis, whole-current length or guaranteed physical minimum established. '
             'Lancaster Sound intrusion and meanders are not reconstructed.')
    measurement = {
        'id': MEASUREMENT, 'entity_id': ENTITY, 'claim_id': 'claim:' + MEASUREMENT,
        'quantity': 'length_lower_bound', 'value': calc['rounded_conditional_geographic_floor_km'],
        'unit': 'km', 'source_id': PAPER, 'source_locator': report['source_locator'],
        'method_source_id': METHOD, 'method_file': 'plans/baffin-latitude-gate-bound-protocol-v1.md',
        'scope': scope, 'evidence_status': 'derived_lower_bound',
        'gate_type': 'source_latitude_span', 'rank_eligible': False,
        'direct_gate_distance_km': calc['direct_gate_distance_km'],
        'conditional_on_nominal_gates': True, 'guaranteed_physical_minimum': False,
        'whole_current_representative': False, 'observation_time': None,
        'uncertainty_km': None, 'fixed_layer_bounds_m': None,
        'endpoint_coordinates_lon_lat': None, 'annual_length_range_km': None,
        'geometry_id': None, 'historical_release_admitted': False,
        'length_bound_admission_id': ADMISSION,
    }
    sensitivity = {key: calc[key] for key in ('scenario_count', 'scenario_min_km', 'scenario_max_km')}
    sensitivity.update(perturbation_degrees=0.5, interpretation=report['sensitivity_interpretation'])
    assessment = copy.deepcopy(prior[0])
    assessment.update(evidence_status='derived_lower_bound', lower_bound_km=measurement['value'],
                      length_source_id=PAPER, length_source_locator=report['source_locator'],
                      gate_distance_method_source_id=METHOD, gate_distance_sensitivity=sensitivity,
                      scope=scope, measurement_id=MEASUREMENT, measurement_admission_file=FILE,
                      conditional_on_nominal_gates=True, guaranteed_physical_minimum=False)
    claim = {
        'id': measurement['claim_id'], 'subject_id': ENTITY, 'object_id': None,
        'predicate': 'length_lower_bound', 'value': measurement['value'], 'unit': 'km',
        'target_collection': 'measurements', 'target_id': MEASUREMENT,
        'source_id': PAPER, 'source_locator': report['source_locator'], 'source_locator_status': 'specific',
        'evidence_class': 'derived_lower_bound', 'assertion_status': 'reported_or_derived_measurement',
        'scope': scope, 'method_source_id': METHOD, 'method': measurement['method_file'],
        'method_status': 'described', 'source_date': None, 'source_publication_year': 1982,
        'source_snapshot_id': None, 'support_claim_id': None, 'observation_time': None,
        'review_status': 'not_individually_reviewed', 'reviewer': None, 'review_date': None,
        'review_note': 'Internal selected-source, arithmetic and role-lens review; no external scientific review claimed.',
    }
    claim['review_fingerprint'] = review_fingerprint(claim)
    sources = [
        {'id': PAPER, 'kind': 'paper', 'label': 'Fissel et al. 1982 selected original Baffin extent',
         'title': 'Major Features of the Summer Near-Surface Circulation of Western Baffin Bay, 1978 and 1979',
         'url': report['source_url'], 'doi': report['source_doi'], 'publication_year': 1982,
         'source_locator': report['source_locator'], 'original_sha256': report['original_sha256'],
         'source_facts_file': report['source_review_file'],
         'material_use_class': 'metadata_and_factual_extraction', 'provider_asset_redistributed': False,
         'review_scope': facts['review_scope'],
         'metadata_note': 'Same underlying original as existing regional width support; a separate provenance reference is not an independent observation.'},
        {'id': METHOD, 'kind': 'internal', 'label': 'OSW Baffin latitude-gate geographic bound v1',
         'url': '../' + measurement['method_file'], 'path': measurement['method_file'],
         'repository_path': measurement['method_file'], 'source_report_file': REPORT,
         'source_report_sha256': OUTPUTS[REPORT], 'source_execution_proof_file': PROOF,
         'material_use_class': 'internal_calculation_method', 'provider_asset_redistributed': False,
         'scientific_approval_inferred': False},
    ]
    scenarios = []
    for index, row in enumerate(calc['scenarios']):
        scenarios.append({
            'id': 'length_bound_scenario:baffin:' + str(index + 1),
            'entity_id': ENTITY, 'current_id': 'baffin', 'admission_id': ADMISSION,
            'measurement_id': MEASUREMENT, 'scenario_index': index + 1,
            **copy.deepcopy(row), 'source_id': PAPER, 'method_source_id': METHOD,
            'scenario_kind': 'editorial_latitude_sensitivity', 'unit': 'km',
            'interpretation': report['sensitivity_interpretation'],
            'is_observation': False, 'is_confidence_interval': False,
            'annual_extrema_eligible': False, 'seasonal_playback_eligible': False,
            'observation_time': None,
        })
    admission = {
        'id': ADMISSION, 'entity_id': ENTITY, 'current_id': 'baffin',
        'schema': 'osw.baffin-latitude-bound-working-admission.v1',
        'status': 'conditional_described_latitude_geographic_floor_unranked',
        'source_id': PAPER, 'method_source_id': METHOD, 'measurement_id': MEASUREMENT,
        'source_locator': report['source_locator'], 'source_report_file': REPORT,
        'figure_file': FIGURE, 'calculation': copy.deepcopy(calc), 'scope': scope,
        'naming_scope': report['naming_scope'], 'study_years': report['study_years'],
        'study_season': report['study_season'], 'exact_gate_occupation_dates': None,
        'fixed_layer_bounds_m': None, 'whole_current_length_km': None,
        'annual_length_range_km': None, 'uncertainty_km': None,
        'rank_eligible': False, 'physical_state_join_eligible': False,
        'seasonal_playback_eligible': False, 'historical_release_admitted': False,
        'independent_scientific_review_completed': False,
    }
    pins = {**report['input_sha256'], **OUTPUTS, PROOF: pin(PROOF), BASE: pin(BASE),
            ENTITIES: pin(ENTITIES), 'analysis/build_ocean_motion_claims.py': pin('analysis/build_ocean_motion_claims.py')}
    return {
        'schema': 'osw.baffin-latitude-bound-admission-contract.v1',
        'status': 'prepared_records_delivery_unverified', 'entity_id': ENTITY,
        'accepted_entity': accepted[0], 'prior_length_assessment': prior[0],
        'length_assessment': assessment, 'measurement': measurement, 'claim': claim,
        'source_records': sources, 'admission': admission, 'scenario_records': scenarios,
        'manifest_fields': {VERSION_KEY: '1'}, 'input_sha256': pins,
        'card_links': [
            {'label': 'Inspect the conditional 1,000 km Baffin geographic floor', 'url': '../' + FIGURE},
            {'label': 'Query the Baffin length assessment', 'url': query_url('length_assessments', 'entity_id', ENTITY)},
            {'label': 'Audit the Baffin bound and historical naming scope', 'url': query_url('current_length_bound_admissions', 'id', ADMISSION)},
            {'label': 'Compare all nine editorial latitude scenarios', 'url': query_url('current_length_bound_scenarios', 'entity_id', ENTITY, 9)},
        ],
        'working_delivery_verified': False, 'scientific_release_published': False,
    }


def records(document):
    return [('measurements', document['measurement']), ('claims', document['claim']),
            ('current_length_bound_admissions', document['admission']),
            *[('sources', row) for row in document['source_records']],
            *[('current_length_bound_scenarios', row) for row in document['scenario_records']]]


def prepare_records(collections, document):
    """Prepare records only; callers must finish owner projection before exporting."""
    if encoded(document) != read(FILE) or encoded(document) != encoded(build_contract()):
        raise ValueError('Changed or unverified Baffin admission contract')
    if {'entities', 'length_assessments', 'measurements', 'claims', 'sources'} - collections.keys():
        raise ValueError('Incomplete parent collections')
    if any(not isinstance(rows, list) or any(not isinstance(r, dict) for r in rows) for rows in collections.values()):
        raise ValueError('Invalid collection shape')
    if [r for r in collections['entities'] if r.get('id') == ENTITY] != [document['accepted_entity']]:
        raise ValueError('Changed accepted Baffin identity')
    prior = [r for r in collections['length_assessments'] if r.get('entity_id') == ENTITY]
    if prior != [document['prior_length_assessment']]:
        raise ValueError('Changed or duplicate prior Baffin assessment')
    staged = dict(collections)
    staged['length_assessments'] = [copy.deepcopy(document['length_assessment']) if r.get('entity_id') == ENTITY else r
                                    for r in collections['length_assessments']]
    for collection, row in records(document):
        previous = staged.get(collection, [])
        if any(r.get('id') == row['id'] for r in previous):
            raise ValueError('Admission identity collision in ' + collection)
        staged[collection] = [*previous, copy.deepcopy(row)]
    source_ids = [r['id'] for r in staged['sources']]
    if len(source_ids) != len(set(source_ids)):
        raise ValueError('Duplicate source registry identity')
    return staged, {'status': 'records_prepared_owner_projection_and_delivery_pending',
                    'appended_rows': 14, 'replaced_length_assessments': 1,
                    'physical_samples_added': 0, 'seasonal_ranges_added': 0,
                    'owner_projection_verified': False, 'working_delivery_verified': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'check'])
    args = parser.parse_args()
    raw = encoded(build_contract())
    if args.action == 'build':
        with (ROOT / FILE).open('xb') as stream:
            stream.write(raw)
    elif read(FILE) != raw:
        raise ValueError('Changed complete Baffin admission contract')
    print('PASS prepared Baffin contract; live packet and delivery unchanged')
