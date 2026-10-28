"""Prepare one nullable-range regional route from bounded audited metadata only."""
import copy
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import quote
from check_wicc_reference_parent_v1 import publications

ROOT = Path(__file__).resolve().parents[1]
CURRENT = 'west-india-coastal'
OWNER = 'current:' + CURRENT
ROUTE = 'wicc-winter-10n-22n-regional-reference-v1'
METHOD = 'source:wicc-winter-regional-reference-method-v1'
PARENT = 'bb343f71dd42ba40dcc688aa4209c72a884f909f31d046e2158d14ea994bfc24'
CANDIDATE = 'research/wicc-winter-regional-reference-route-v4-candidate.json'
FIGURE = 'figures/wicc-winter-regional-reference-route-v4-candidate.svg'
PROTOCOL = 'plans/wicc-winter-reference-query-contract-v1.md'
CONTRACT = 'research/wicc-winter-reference-query-contract-v1.json'


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + '\n').encode()


def fingerprint(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def read(path):
    return json.loads((ROOT / path).read_bytes())


def title(value):
    return re.sub('[^a-z0-9]', '', str(value).lower())


def query_url():
    query = {'collection': 'reference_routes', 'filters': [{'field': 'id', 'op': 'eq', 'value': ROUTE}], 'limit': 1}
    return 'query.html?q=' + quote(json.dumps(query, separators=(',', ':'))) + '&inspect=' + ROUTE + '#query-map-section'


def atlas_url():
    return 'reference-routes.html?atlas-layout=map&atlas-feature=' + quote(OWNER) + '&atlas-route=' + ROUTE + '#route-atlas'


def build_contract():
    review = read('research/wicc-reference-parent-execution-review-v1.json')
    result = read('research/wicc-reference-parent-run-v1/result.json')
    selected_path = 'research/wicc-reference-parent-run-v1/selected-records.json'
    selected = read(selected_path)
    candidate = read(CANDIDATE)
    if (review['status'] != 'PASS_READ_ONLY_SOURCE_BINDINGS_VERIFIED' or not review['request_disabled']
            or result['logical_sha256'] != PARENT
            or hashlib.sha256((ROOT / selected_path).read_bytes()).hexdigest() != result['selected_records_sha256']
            or selected['owner']['route_ids'] != [] or selected['owner']['capabilities']['reference_route'] != 0
            or candidate['reported_scenario_range_km'] is not None
            or candidate['length_uncertainty_km'] is not None
            or candidate['annual_length_range_km'] is not None
            or candidate['whole_current_length'] is not False
            or candidate['nominal_reference_path_km'] != 1549.568):
        raise ValueError('Audited parent and corrected regional route required')
    citations = [
        {'id': 'source:wicc-winter-shetye-1991', 'kind': 'publication',
         'title': 'The coastal current off western India during the northeast monsoon',
         'year': 1991, 'doi': '10.1016/0198-0149(91)90087-V', 'url': candidate['source_url'],
         'access_scope': 'publisher_indexed_abstract_only', 'original_methods_reviewed': False},
        {'id': 'source:wicc-shelf-slope-shetye-2008', 'kind': 'publication',
         'title': 'Observational evidence for remote forcing of the West India Coastal Current',
         'year': 2008, 'doi': '10.1029/2008JC004874',
         'url': 'https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2008JC004874',
         'access_scope': 'selected_publisher_full_html_passages', 'role': 'shelf_slope_and_remote_forcing_scope_caution'},
        {'id': METHOD, 'kind': 'internal', 'title': 'OSW WICC winter regional reference protocol v1',
         'path': PROTOCOL, 'url': '../' + PROTOCOL}]
    pins = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in [CANDIDATE, FIGURE, PROTOCOL,
        'analysis/wicc_winter_reference_query_v1.py', 'analysis/check_wicc_reference_parent_v1.py',
        'research/wicc-reference-parent-execution-review-v1.json', selected_path,
        'research/wicc-reference-parent-run-v1/result.json',
        'research/wicc-reference-parent-run-v1/run-receipt.json',
        'research/wicc-winter-regional-reference-route-preparation-review-v1.json',
        'plans/wicc-winter-regional-reference-route-interpretation-v2.md']}
    row = {'id': ROUTE, 'entity_id': OWNER, 'current_id': CURRENT,
           'name': 'WICC winter 10 N-22 N regional reference', 'label': 'WICC winter regional reference',
           'type': 'editorial_regional_reference_connection', 'status': 'regional_editorial_reference_abstract_supported',
           'geometry_role': 'osw_editorial_reference_route', 'crs': candidate['crs'],
           'geometry': {'type': 'LineString', 'coordinates': candidate['coordinates_lon_lat']},
           'scope': candidate['scope'], 'layer': candidate['layer'], 'time_convention': candidate['time_convention'],
           'source_id': citations[0]['id'], 'source_ids': [s['id'] for s in citations],
           'source_url': candidate['source_url'], 'source_locator': candidate['source_locator'],
           'source_file': CANDIDATE, 'source_file_sha256': pins[CANDIDATE],
           'candidate_file': CANDIDATE, 'candidate_sha256': pins[CANDIDATE],
           'approximate_reference_path_km': 1500, 'computed_editorial_path_km': 1549.568,
           'scenario_range_km': None, 'scenario_count': 3,
           'scenario_interpretation': candidate['scenario_length_interpretation'],
           'comparison_group': 'osw_abstract_supported_regional_references',
           'figure': FIGURE, 'figure_file': FIGURE, 'figure_sha256': pins[FIGURE],
           'route_extent_kind': 'Dec1987-Jan1988 regional editorial reference',
           'rank_eligible': False, 'whole_current_length_km': None, 'physical_width_km': None,
           'current_thickness_m': None, 'annual_length_range_km': None, 'annual_width_range_km': None,
           'uncertainty_km': None, 'sample_date': None, 'independent_observation_count': 0,
           'physical_current_axis_admitted': False, 'physical_current_edges_admitted': False,
           'physical_state_join_eligible': False, 'seasonal_playback_eligible': False,
           'geographic_seasonal_playback_eligible': False, 'nasa_identity_verified': False,
           'nominal_atlas_state_crossings': None, 'recommended_nasa_tile_id': None,
           'display_context': {'state_codes': candidate['nominal_atlas_state_crossings'],
                               'recommended_nasa_tile_id': candidate['recommended_nasa_tile_id'],
                               'role': 'editorial_display_overlap_only'}}
    feature = {'geometry': copy.deepcopy(row['geometry']), 'role': 'editorial_reference_route',
               'candidate_id': ROUTE, 'source_id': row['source_id'], 'source_ids': row['source_ids'],
               'note': row['scope'], 'source_url': row['source_url'], 'source_locator': row['source_locator'],
               'source_file_sha256': pins[CANDIDATE], 'observation_date': None, 'layer': row['layer'],
               'time_convention': row['time_convention'], 'physical_current_axis_admitted': False,
               'physical_state_join_eligible': False}
    return {'schema': 'osw.wicc-winter-reference-query-contract.v1', 'status': 'PREPARED_NOT_INSTALLED',
            'parent_logical_sha256': PARENT, 'input_sha256': pins, 'prior_records': selected,
            'parent_collection_counts': result['collection_counts'], 'new_sources': citations,
            'route': row, 'owner_map_feature': feature, 'atlas_report': candidate,
            'query_url_after_installation': query_url(), 'atlas_url_after_installation': atlas_url(),
            'new_editorial_routes': 1, 'new_publication_citations': 2, 'new_physical_dimensions': 0}


def append(collections, contract, *, parent_logical_sha256):
    if parent_logical_sha256 != PARENT or contract != build_contract():
        raise ValueError('Exact audited logical parent and prepared contract required')
    for name in ['sources', 'reference_routes', 'objects', 'entities', 'route_decisions', 'widths']:
        rows = collections.get(name)
        if not isinstance(rows, list) or len(rows) != contract['parent_collection_counts'][name]:
            raise ValueError('Parent inventory differs: ' + name)
        ids = [r.get('id') for r in rows]
        if any(not isinstance(i, str) or not i for i in ids) or len(ids) != len(set(ids)):
            raise ValueError('Duplicate/empty IDs: ' + name)
    prior = contract['prior_records']
    for collection, field, key in [('objects', 'id', 'owner'), ('entities', 'id', 'entity'),
                                  ('route_decisions', 'entity_id', 'planning_decision')]:
        if [r for r in collections[collection] if r.get(field) == OWNER] != [prior[key]]:
            raise ValueError('Audited WICC row differs: ' + collection)
    if [r for r in collections['widths'] if r.get('current_id') == CURRENT] != prior['widths']:
        raise ValueError('Existing WICC width must remain exact')
    if any(r.get('current_id') == CURRENT or r['id'] == ROUTE for r in collections['reference_routes']):
        raise ValueError('WICC route already present')
    matched, _ = publications(collections['sources'])
    if any(matched.values()):
        raise ValueError('Publication now present; reconcile instead of duplicating')
    source_registry = {r['id']: r for r in collections['sources']}
    for row in prior['owner_sources']:
        if source_registry.get(row['id']) != row:
            raise ValueError('Prior owner source differs')
    for new in contract['new_sources']:
        if new['id'] in source_registry or any(title(r.get('title')) == title(new['title']) for r in source_registry.values()):
            raise ValueError('Existing citation identity/title requires reconciliation')
    result = copy.deepcopy(collections)
    result['sources'].extend(copy.deepcopy(contract['new_sources']))
    result['reference_routes'].append(copy.deepcopy(contract['route']))
    owner = next(r for r in result['objects'] if r['id'] == OWNER)
    owner['route_ids'] = [ROUTE]
    owner['capabilities']['reference_route'] = 1
    owner['map_features'].append(copy.deepcopy(contract['owner_map_feature']))
    owner['source_ids'] = sorted(set(owner['source_ids']) | set(contract['route']['source_ids']))
    owner['linked_source_count'] = len(owner['source_ids'])
    owner['route_url'] = atlas_url()
    owner['section_fingerprints']['wicc_winter_regional_reference'] = fingerprint(contract['route'])
    owner['fingerprint'] = fingerprint({k: v for k, v in owner.items() if k != 'fingerprint'})
    decision = next(r for r in result['route_decisions'] if r.get('entity_id') == OWNER)
    decision['prior_route_decision'] = copy.deepcopy(prior['planning_decision'])
    decision.update(route_ids=[ROUTE], candidate_count=1, construction_status='regional_editorial_reference_abstract_supported',
                    source_catalog_file=CANDIDATE, source_catalog_sha256=contract['route']['source_file_sha256'],
                    source_id=contract['route']['source_id'], source_ids=copy.deepcopy(contract['route']['source_ids']),
                    source_url=contract['route']['source_url'],
                    next_action='Recover whole-current endpoints and compatible physical axes; this abstract-supported regional reference does not establish seasonal dimensions or uncertainty.')
    decision['source_decision'].update(candidate_ids=[ROUTE], reference_path_decision=decision['construction_status'],
                                      next_action=decision['next_action'])
    return result


if __name__ == '__main__':
    target = ROOT / CONTRACT
    assert not target.exists(), 'Prepared contracts are frozen; use a new version for revisions'
    target.write_bytes(encoded(build_contract()))
    print('Prepared WICC regional reference contract; runtime integration and installation pending')
