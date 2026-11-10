"""Append source-qualified EICC reference routes and typed source-table records."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from urllib.parse import quote, unquote

from loop_published_metrics_query_v1 import checked_ids, encoded, fingerprint, normalized_doi

ROOT = Path(__file__).resolve().parents[1]
TARGET = 'current:east-india-coastal'
CURRENT = 'east-india-coastal'
POINTS = 'current_sampling_reference_points'
SCALES = 'current_spectral_cross_shore_scales'
ROUTES = 'reference_routes'
OWNER_FIELDS = {ROUTES: ('route_ids', 'reference_route'),
                POINTS: ('sampling_reference_point_ids', 'sampling_reference_points'),
                SCALES: ('spectral_cross_shore_scale_ids', 'spectral_cross_shore_scales')}
DURAND = 'source:durand-eicc-altimetry-2009'
GANG = 'source:gangopadhyay-eicc-spring-wbc-2013'
METHOD = 'source:eicc-reference-spectral-query-v1'
FACTS = 'research/eicc-durand-2009-sampling-spectral-source-facts-v1.json'
SOURCE_PREP = 'research/eicc-regional-length-source-preparation-v1.json'
CANDIDATE = 'research/eicc-regional-reference-admission-candidate-v1.json'
CALCULATION = 'research/eicc-spring-regional-reference-calculation-v1.json'
REVIEW = 'research/eicc-regional-reference-execution-review-v1.json'
FIGURE_REVIEW = 'research/eicc-published-support-visual-review-v1.json'
PROTOCOL = 'research/eicc-reference-query-protocol-v1.json'
MODULE = 'analysis/eicc_reference_query_v1.py'
FILE = 'research/eicc-reference-query-contract-v1.json'
PAGE = 'almanac/eicc-reference-support.html'
FIGURE = 'figures/eicc-spring-regional-reference-v1.svg'
SUPPORT_FIGURE = 'figures/eicc-durand-2009-published-support-v1.svg'
PINS = {
    "research/eicc-regional-length-source-preparation-v1.json": "3e1b8646a1294feb91d117051f781077ab609697ad6233744b3a8cc4545a3563",
    "research/eicc-regional-reference-admission-candidate-v1.json": "6c02b4c09e214b5080ce5017849ad9ade9f034c579da7d5c3d1b5a056ad5db9d",
    "research/eicc-regional-reference-execution-review-v1.json": "e93c74a1d8b397d4b3f23596d5d8995aacd2570e31a938beb762402567d500cc",
    "research/eicc-published-support-visual-review-v1.json": "73b0be587a9bbe5fa1dd834803524e9ff5e6fa622d0e2fe2518819c341c4886c",
    "research/eicc-regional-reference-cloud-result-v1.json": "87e1517ecf47c2508fd9f6f829a911529a0b66ce89d286e57311b26748e84373"
}


def query_url(collection):
    key, value = ('current_id', CURRENT) if collection == ROUTES else ('entity_id', TARGET)
    request = {'collection': collection, 'filters': [{'field': key, 'op': 'eq', 'value': value}],
               'sort': {'field': 'id', 'direction': 'asc'}, 'limit': 100}
    return 'query.html?q=' + quote(json.dumps(request, separators=(',', ':')))


def source_query(file, pointer):
    return 'query.html?source-q=' + quote(json.dumps({'document': file, 'pointer': pointer, 'limit': 100}, separators=(',', ':')))


def route_record_query_url(ident):
    request = {'collection': ROUTES, 'filters': [{'field': 'id', 'op': 'eq', 'value': ident}], 'limit': 1}
    return ('query.html?q=' + quote(json.dumps(request, separators=(',', ':')))
            + '&inspect=' + quote(ident) + '#query-map-section')


def build_contract(root=ROOT):
    root = Path(root)
    if len(PINS) != 5:
        raise ValueError('Fixed reviewed receipt inventory required')
    for path, sha in PINS.items():
        if hashlib.sha256((root / path).read_bytes()).hexdigest() != sha:
            raise ValueError('Changed reviewed EICC receipt: ' + path)
    pins = dict(PINS)
    prepared = json.loads((root / SOURCE_PREP).read_bytes())
    for path, sha in prepared['input_sha256'].items():
        if hashlib.sha256((root / path).read_bytes()).hexdigest() != sha:
            raise ValueError('Changed EICC source preparation: ' + path)
        pins[path] = sha
    candidate = json.loads((root / CANDIDATE).read_bytes())
    raw = (root / CALCULATION).read_bytes()
    if hashlib.sha256(raw).hexdigest() != candidate['calculation_sha256']:
        raise ValueError('Regional calculation bytes changed')
    calculation = json.loads(raw)
    review = json.loads((root / REVIEW).read_bytes())
    visual = json.loads((root / FIGURE_REVIEW).read_bytes())
    if (review['visual_review_complete'] is not True or review['actual_png_inspected'] is not True
            or review['failed_cases'] != 0 or review['source_result_sha256'] != hashlib.sha256(raw).hexdigest()
            or calculation['status'] != 'CALCULATED_CARTOGRAPHIC_GATES_PASSED'
            or visual['actual_png_inspected'] is not True or len(calculation['cases']) != 18):
        raise ValueError('Complete numeric, cartographic and actual visual review required')
    if hashlib.sha256((root / FIGURE).read_bytes()).hexdigest() != review['svg_sha256']:
        raise ValueError('Reviewed reference map changed')
    if hashlib.sha256((root / SUPPORT_FIGURE).read_bytes()).hexdigest() != visual['svg_sha256']:
        raise ValueError('Reviewed source support figure changed')
    for path in [CALCULATION, FIGURE, PROTOCOL, MODULE, 'analysis/render_eicc_reference_page_v1.py',
                 'analysis/loop_published_metrics_query_v1.py']:
        pins[path] = hashlib.sha256((root / path).read_bytes()).hexdigest()
    facts = json.loads((root / FACTS).read_bytes())
    if facts['entity_id'] != TARGET:
        raise ValueError('Changed EICC source owner')
    common = {'entity_id': TARGET, 'related_current_id': TARGET, 'method_source_id': METHOD,
              'independent_observation_count': 0, 'rank_eligible': False,
              'physical_state_join_eligible': False, 'geographic_seasonal_playback_eligible': False,
              'nasa_identity_verified': False, 'whole_current_length_km': None,
              'physical_width_km': None, 'annual_length_range_km': None, 'annual_width_range_km': None,
              'sample_date': None, 'diagnostic_page': PAGE}
    collections = {ROUTES: [], POINTS: [], SCALES: [], 'sources': [
        {'id': DURAND, 'kind': 'external', 'doi': facts['source']['doi'], 'url': facts['source']['url'],
         'title': facts['source']['title'], 'label': 'Durand et al. (2009): EICC sampling and spectral scales',
         'publication_year': 2009, 'access_scope': facts['source']['access'],
         'original_asset_retained': False, 'provider_asset_redistributed': False},
        {'id': GANG, 'kind': 'external', 'doi': '10.1002/grl.50412',
         'url': 'https://agupubs.onlinelibrary.wiley.com/doi/10.1002/grl.50412',
         'title': 'On the nature of meandering of the springtime western boundary current in the Bay of Bengal',
         'label': 'Gangopadhyay et al. (2013): springtime Bay of Bengal WBC', 'publication_year': 2013,
         'access_scope': 'Publisher full HTML prose and captions reviewed; source figures not digitized.',
         'original_asset_retained': False, 'provider_asset_redistributed': False},
        {'id': METHOD, 'kind': 'internal', 'title': 'EICC regional reference and spectral-support query protocol v1',
         'label': 'OSW EICC source-qualified query rules', 'path': PROTOCOL, 'url': '../' + PROTOCOL,
         'provider_asset_redistributed': False}]}
    features = []
    if len(candidate['rows']) != 2:
        raise ValueError('Two distinct source-coordinate conventions required')
    for i, original in enumerate(candidate['rows']):
        variant = original['source_variant_id']
        title = 'Springtime WBC reference — ' + ('prose core at 18°N' if variant == 'paragraph8' else 'caption core at 18.5°N')
        case = next(r for r in calculation['cases'] if r['variant_id'] == variant and r['bend_offsets_km'] == [0, 0])
        pointer = '/rows/' + str(i)
        scope = ('Regional editorial source-anchor connection; ' + variant + '. 50 m analysis, March–April 1987 survey context. '
                 'Nine bend probes are editorial sensitivity, not physical uncertainty or annual variability. '
                 'Source calls the northward spring phase WBC; no whole-current EICC length admitted.')
        row = {**copy.deepcopy(common), **copy.deepcopy(original), 'name': title, 'label': title,
               'source_label': original['label'],
               'status': 'reviewed_editorial_regional_reference_connection',
               'record_type': 'source_convention_regional_editorial_reference',
               'source_id': GANG, 'source_ids': [GANG, METHOD], 'method_source_id': METHOD,
               'scope': scope, 'source_file': CANDIDATE, 'source_file_sha256': pins[CANDIDATE],
               'source_pointer': pointer, 'source_query_url': source_query(CANDIDATE, pointer),
               'figure_file': FIGURE, 'figure_sha256': pins[FIGURE],
               'diagnostic_page': PAGE, 'layer': '50 m objectively analyzed hydrographic field context; not current thickness.',
               'time_convention': 'Survey-wide 22 March–28 April 1987 support, not an instantaneous or annually repeated axis.',
               'geometry': {'type': 'LineString', 'coordinates': copy.deepcopy(original['coordinates_lon_lat'])},
               'geometry_role': 'editorial_reference_route', 'role': 'editorial_reference_route',
               'nominal_atlas_state_crossings': None, 'recommended_nasa_tile_id': None}
        row['source_stage_working_dataset_admitted'] = row.pop('working_dataset_admitted')
        collections[ROUTES].append(row)
        features.append({'geometry': {'type': 'LineString', 'coordinates': copy.deepcopy(case['display_coordinates_lon_lat'])},
                         'role': 'editorial_reference_route', 'candidate_id': row['id'], 'note': scope,
                         'source_id': GANG, 'source_url': row['source_url'], 'source_locator': row['source_locator'],
                         'source_file_sha256': hashlib.sha256(raw).hexdigest(),
                         'observation_date': None, 'layer': row['layer'], 'time_convention': row['time_convention'],
                         'physical_current_axis_admitted': False, 'physical_state_join_eligible': False,
                         'coordinate_reference_system': 'WGS84 display convention; source datum unspecified',
                         'spatial_geometry_method': 'WGS84 source-anchor geodesic connection, sampled at <=1 km; display topology only, not physical current passage.'})
    for index, original in enumerate(facts['sampling_points']):
        point = original['source_point_label']
        pointer = '/sampling_points/' + str(index)
        outlet = point == 'G'
        row = {**copy.deepcopy(common), **copy.deepcopy(original), 'source_id': DURAND, 'source_ids': [DURAND, METHOD],
               'record_type': 'published_current_sampling_reference_point',
               'label': 'Point ' + point + ' / track ' + str(original['source_track']) + (' — outlet context' if outlet else ' — EICC reference'),
               'value': f"{original['longitude_degrees_east']:.1f}°E, {original['latitude_degrees_north']:.1f}°N", 'unit': '',
               'scope': ('Monsoon-current outlet context, not strictly on the EICC path. ' if outlet else 'Source-selected variability reference, not a route vertex. ')
                        + 'November 1992–July 2002 coverage. Nearest-shore distance is not width; bathymetry is not current depth.',
               'source_url': facts['source']['url'], 'source_file': FACTS, 'source_file_sha256': pins[FACTS],
               'source_pointer': pointer, 'source_query_url': source_query(FACTS, pointer),
               'figure_file': SUPPORT_FIGURE, 'figure_sha256': pins[SUPPORT_FIGURE],
               'source_time_support': copy.deepcopy(facts['time_support']), 'geometry': None,
               'time_convention': 'Source coverage November 1992–July 2002; no exact observation day assigned.',
               'layer': 'Surface geostrophic anomaly reference; table bathymetry is separate seafloor context.',
               'is_strict_eicc_path_reference': not outlet}
        collections[POINTS].append(row)
    for index, original in enumerate(facts['spectral_cross_shore_scales']):
        pointer = '/spectral_cross_shore_scales/' + str(index)
        collections[SCALES].append({**copy.deepcopy(common), **copy.deepcopy(original),
            'source_id': DURAND, 'source_ids': [DURAND, METHOD],
            'record_type': 'published_annual_power_e_folding_scale',
            'label': 'Track ' + str(original['source_track']) + ' — annual-power e-folding scale',
            'value': original['reported_scale_km'], 'unit': 'km',
            'scope': 'Cross-shore annual spectral-power scale, not paired current width. Source theoretical Ro/2 comparison '
                     + str(original['reported_theoretical_ro_over_2_km']) + ' km is not a second width observation or uncertainty.',
            'source_url': facts['source']['url'], 'source_file': FACTS, 'source_file_sha256': pins[FACTS],
            'source_pointer': pointer, 'source_query_url': source_query(FACTS, pointer),
            'figure_file': SUPPORT_FIGURE, 'figure_sha256': pins[SUPPORT_FIGURE],
            'source_time_support': copy.deepcopy(facts['time_support']), 'geometry': None,
            'time_convention': 'Source coverage November 1992–July 2002; no exact observation day assigned.',
            'layer': original['velocity_support']})
    return {'schema': 'osw.eicc-reference-spectral-query.v1', 'status': 'SOURCE_CONTRACT_PREPARED_NOT_INSTALLED',
            'input_sha256': pins, 'owner_id': TARGET, 'collections': collections, 'owner_map_features': features,
            'counts': {'regional_reference_routes': 2, 'sampling_reference_points': 7, 'spectral_scales': 6,
                       'publication_sources': 2, 'method_sources': 1},
            'example_queries': [json.loads(unquote(query_url(c).split('=', 1)[1])) for c in OWNER_FIELDS],
            'admission': {'new_physical_dimensions': 0, 'whole_current_ranked_lengths': 0, 'paired_widths': 0,
                          'annual_dimension_ranges': 0, 'observed_geometry_records': 0, 'physical_state_intersections': 0,
                          'editorial_reference_display_geometries': 2, 'independent_observations': 0}}


def owner_matches(row, collection):
    return row.get('current_id') == CURRENT if collection == ROUTES else row.get('entity_id') == TARGET


def append(collections, document):
    """Validate all affected containers before replacing any caller-owned list."""
    if type(collections) is not dict or encoded(document) != encoded(build_contract()):
        raise ValueError('Changed reviewed EICC query contract')
    objects, entities = collections.get('objects', []), collections.get('entities', [])
    checked_ids(objects, 'objects'); checked_ids(entities, 'entities')
    owners = [r for r in objects if r['id'] == TARGET]
    if (len(owners) != 1 or owners[0].get('type') != 'named_current'
            or sum(r['id'] == TARGET and r.get('type') == 'named_current' for r in entities) != 1):
        raise ValueError('Admitted EICC object and entity required')
    incoming = document['collections']
    for name in OWNER_FIELDS:
        old_ids = checked_ids(collections.get(name, []), name)
        if old_ids & checked_ids(incoming[name], 'new ' + name):
            raise ValueError('EICC record collision: ' + name)
    sources = collections.get('sources', [])
    registry = checked_ids(sources, 'sources')
    by_id = {r['id']: r for r in sources}
    added_sources = []
    for new in incoming['sources']:
        if new.get('doi'):
            doi = normalized_doi(new['doi'])
            for old in sources:
                if old['id'] != new['id'] and (normalized_doi(old.get('doi', '')) == doi or doi in str(old.get('url', '')).lower()):
                    raise ValueError('Publication requires explicit source-registry reconciliation')
        if new['id'] in by_id:
            if encoded(new) != encoded(by_id[new['id']]):
                raise ValueError('Changed source-ID collision')
        else:
            added_sources.append(copy.deepcopy(new))
    owner = copy.deepcopy(owners[0])
    refs = owner.get('source_ids')
    if (not isinstance(refs, list) or any(not isinstance(r, str) for r in refs)
            or len(set(refs)) != len(refs) or set(refs) - registry
            or type(owner.get('linked_source_count')) is not int or owner['linked_source_count'] != len(refs)):
        raise ValueError('Invalid EICC prior provenance')
    if any(not isinstance(owner.get(key), expected) for key, expected in
           [('capabilities', dict), ('evidence_links', list), ('section_fingerprints', dict), ('map_features', list)]):
        raise ValueError('Invalid prior owner evidence containers')
    for name, (field, capability) in OWNER_FIELDS.items():
        ids = owner.get(field, [])
        available = {r['id']: r for r in collections.get(name, [])}
        if (not isinstance(ids, list) or any(not isinstance(r, str) for r in ids) or len(set(ids)) != len(ids)
                or set(ids) != {r['id'] for r in available.values() if owner_matches(r, name)}):
            raise ValueError('Invalid prior owned EICC references')
        if (ids or capability in owner['capabilities']) and (type(owner['capabilities'].get(capability)) is not int
                or owner['capabilities'][capability] != len(ids)):
            raise ValueError('Prior capability/reference count mismatch')
        for ident in ids:
            old_refs = available[ident].get('source_ids')
            if (not isinstance(old_refs, list) or any(not isinstance(r, str) for r in old_refs)
                    or len(set(old_refs)) != len(old_refs) or set(old_refs) - registry):
                raise ValueError('Unresolved prior record provenance')
        owner[field] = ids + [r['id'] for r in incoming[name]]
        owner['capabilities'][capability] = len(owner[field])
        owner['evidence_links'].append({'label': {ROUTES: 'Query regional source-reference routes',
             POINTS: 'Query source sampling locations', SCALES: 'Query spectral cross-shore scales'}[name], 'url': query_url(name)})
    old_routes = owners[0].get('route_ids', [])
    for feature in owner['map_features']:
        if feature.get('candidate_id') in {r['id'] for r in incoming[ROUTES]}:
            raise ValueError('Existing EICC map-feature collision')
    decisions = collections.get('route_decisions', [])
    checked_ids(decisions, 'route_decisions')
    prior_decisions = [r for r in decisions if r.get('entity_id') == TARGET]
    if (len(prior_decisions) != 1 or owner.get('route_decision_ids') != [prior_decisions[0]['id']]
            or prior_decisions[0].get('route_ids') != old_routes
            or type(prior_decisions[0].get('candidate_count')) is not int
            or prior_decisions[0]['candidate_count'] != len(old_routes)
            or prior_decisions[0].get('rank_eligible') is not False
            or not isinstance(prior_decisions[0].get('source_decision'), dict)):
        raise ValueError('Prior EICC route planning decision is inconsistent')
    if prior_decisions[0]['source_decision'].get('candidate_ids') != old_routes:
        raise ValueError('Prior planning source/reference mismatch')
    decision = copy.deepcopy(prior_decisions[0])
    decision['prior_route_decision'] = copy.deepcopy(prior_decisions[0])
    decision.update(construction_status='regional_source_anchor_connections_constructed',
                    candidate_count=len(owner['route_ids']), route_ids=copy.deepcopy(owner['route_ids']),
                    next_action='Recover continuous source axes and consistent endpoints beyond these regional source-anchor connections before any whole-current or annual length claim.',
                    source_catalog_file=CANDIDATE, source_catalog_sha256=document['input_sha256'][CANDIDATE],
                    source_url=incoming[ROUTES][0]['source_url'])
    decision['source_decision'].update(candidate_ids=copy.deepcopy(owner['route_ids']),
        reference_path_decision=decision['construction_status'], next_action=decision['next_action'])
    owner['map_features'].extend(copy.deepcopy(document['owner_map_features']))
    owner['source_ids'] = sorted(set(refs) | {r['id'] for r in incoming['sources']})
    owner['linked_source_count'] = len(owner['source_ids'])
    owner['evidence_links'].append({'label': 'EICC regional reference maps and source tables', 'url': 'eicc-reference-support.html'})
    owner['section_fingerprints']['eicc_regional_reference_and_spectral_support'] = fingerprint(
        {name: incoming[name] for name in OWNER_FIELDS})
    owner['fingerprint'] = fingerprint({k: v for k, v in owner.items() if k != 'fingerprint'})
    updates = {name: [*collections.get(name, []), *copy.deepcopy(incoming[name])] for name in OWNER_FIELDS}
    updates['sources'] = [*sources, *added_sources]
    updates['objects'] = [owner if r['id'] == TARGET else r for r in objects]
    updates['route_decisions'] = [decision if r['id'] == decision['id'] else r for r in decisions]
    collections.update(updates)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'check'])
    args = parser.parse_args()
    contract = build_contract()
    from render_eicc_reference_page_v1 import page
    html = page(contract)
    if args.action == 'build':
        (ROOT / FILE).write_bytes(encoded(contract))
        (ROOT / PAGE).write_bytes(html)
    elif (ROOT / FILE).read_bytes() != encoded(contract) or (ROOT / PAGE).read_bytes() != html:
        raise ValueError('Contract or evidence page differs from reviewed projection')
    print(json.dumps({'status': 'PASS', 'counts': contract['counts'], 'admission': contract['admission']}))
