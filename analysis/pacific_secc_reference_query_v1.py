"""Prepare a source-bound regional reference; no installed packet or fields loaded."""
import argparse
import copy
import hashlib
import html
import json
from pathlib import Path
from urllib.parse import quote, urlsplit

from loop_published_metrics_query_v1 import checked_ids, encoded, fingerprint, normalized_doi

ROOT = Path(__file__).resolve().parents[1]
CURRENT = 'pacific-south-equatorial-countercurrent'
TARGET = 'current:' + CURRENT
ROUTE = CURRENT + '-western-mean-reference-reach-v1'
METHOD = 'source:pacific-secc-western-reference-method-v1'
DOI = '10.1029/2003JC002243'
URL = 'https://www.soest.hawaii.edu/oceanography/bo/CQ04.pdf'
CANDIDATE = 'research/pacific-secc-western-mean-reference-path-v2-candidate.json'
FIGURE = 'figures/pacific-secc-western-mean-reference-path-v2-candidate.svg'
GEOGRAPHY = 'research/pacific-secc-reference-geography-result-v1.json'
REVIEW = 'research/pacific-secc-reference-geography-review-v1.json'
CLOUD = 'research/pacific-secc-reference-cloud-result-v1.json'
PROTOCOL = 'plans/pacific-secc-reference-query-protocol-v1.md'
MODULE = 'analysis/pacific_secc_reference_query_v1.py'
FILE = 'research/pacific-secc-reference-query-contract-v1.json'
PAGE = 'almanac/pacific-secc-reference-support.html'
PINS = {
    CANDIDATE: 'a8bb517551f04dbe1018a6d5a51817cee4c3e3afaf2d82447bccdab03cef1d85',
    FIGURE: 'b1813b4dcbe4e245e007f5139495a71a7b778800103a491b8ab71da7cf5d254e',
    GEOGRAPHY: '7398be6b9ec009d99c9719155a54e7540fc4426a370ae432ea9921e3c559002e',
    REVIEW: '9651c14bb9856d08cc3de5122e7cd20e4921a6d6c5e060d28dddad6853bb0674',
    CLOUD: '3bf0fe783d8f59de34a0096c016072d480fae71644937e43dd133a571ada83e5',
    'research/pacific-secc-woa01-anomaly-scope-audit.json':
        '0a98a08b0191c3450c9e5b4146299c411e724b9ffd6a267cbf548587a5d10051',
}


def query_url():
    query = {'collection': 'reference_routes', 'filters': [{'field': 'id', 'op': 'eq', 'value': ROUTE}], 'limit': 1}
    return 'query.html?q=' + quote(json.dumps(query, separators=(',', ':'))) + '&inspect=' + quote(ROUTE) + '#query-map-section'


def build_contract(root=ROOT):
    root = Path(root)
    for path, expected in PINS.items():
        if hashlib.sha256((root / path).read_bytes()).hexdigest() != expected:
            raise ValueError('Changed reviewed Pacific SECC evidence: ' + path)
    candidate, geography, review, cloud = [json.loads((root / p).read_bytes()) for p in [CANDIDATE, GEOGRAPHY, REVIEW, CLOUD]]
    if (cloud['status'] != 'PASS' or geography['all_27_clear'] is not True
            or review['all_scenarios_clear_both_masks'] is not True
            or len(review['actual_maps_viewed']) != 2
            or any(r['actually_viewed'] is not True for r in review['actual_maps_viewed'])
            or len(geography['scenarios']) != 27 or candidate['scenario_count'] != 27
            or candidate['current_id'] != CURRENT):
        raise ValueError('Complete source, calculation, geography and actual visual review required')
    pins = dict(PINS)
    for path in [PROTOCOL, MODULE, 'analysis/loop_published_metrics_query_v1.py']:
        pins[path] = hashlib.sha256((root / path).read_bytes()).hexdigest()
    row = {
        'id': ROUTE, 'entity_id': TARGET, 'current_id': CURRENT,
        'name': 'Pacific SECC — western mean reference reach',
        'label': 'Pacific SECC: 164E–180E regional reference',
        'type': 'editorial_regional_reference_connection',
        'status': 'reviewed_editorial_regional_reference_connection',
        'record_type': 'regional_editorial_reference_not_observed_axis',
        'scope': candidate['scope'], 'layer': candidate['layer'], 'time_convention': candidate['time_convention'],
        'source_url': URL, 'source_locator': candidate['source_locator'],
        'source_file': CANDIDATE, 'source_file_sha256': PINS[CANDIDATE], 'source_pointer': '',
        'method_source_id': METHOD, 'publication_source_binding': 'resolve_unique_existing_registry_record',
        'coordinates_lon_lat': copy.deepcopy(candidate['coordinates_lon_lat']),
        'geometry': {'type': 'LineString', 'coordinates': copy.deepcopy(candidate['coordinates_lon_lat'])},
        'geometry_role': 'editorial_reference_route', 'role': 'editorial_reference_route',
        'computed_nominal_reference_length_km': candidate['nominal_reference_path_km'],
        'approximate_reference_path_km': candidate['reported_approximate_reference_path_km'],
        'editorial_probe_length_range_km': copy.deepcopy(candidate['scenario_range_km']),
        'public_editorial_probe_span_km': copy.deepcopy(candidate['reported_scenario_range_km']),
        'scenario_count': 27, 'comparison_group': 'osw_studied_reach_routes',
        'figure_file': FIGURE, 'figure_sha256': PINS[FIGURE], 'diagnostic_page': PAGE,
        'rank_eligible': False, 'whole_current_length_km': None, 'physical_width_km': None,
        'current_thickness_m': None, 'annual_length_range_km': None, 'annual_width_range_km': None,
        'uncertainty_km': None, 'sample_date': None, 'independent_observation_count': 0,
        'physical_current_axis_admitted': False, 'physical_current_edges_admitted': False,
        'physical_state_join_eligible': False, 'seasonal_playback_eligible': False,
        'geographic_seasonal_playback_eligible': False, 'nasa_identity_verified': False,
        'nominal_atlas_state_crossings': None, 'recommended_nasa_tile_id': None,
        'display_context': {'state_codes': copy.deepcopy(candidate['nominal_atlas_state_crossings']),
                            'recommended_nasa_tile_id': candidate['recommended_nasa_tile_id'],
                            'role': 'editorial_display_overlap_only'},
    }
    feature = {'geometry': copy.deepcopy(row['geometry']), 'role': 'editorial_reference_route',
               'candidate_id': ROUTE, 'note': candidate['scope'], 'source_url': URL,
               'source_locator': row['source_locator'], 'source_file_sha256': PINS[CANDIDATE],
               'observation_date': None, 'layer': row['layer'], 'time_convention': row['time_convention'],
               'physical_current_axis_admitted': False, 'physical_state_join_eligible': False}
    return {'schema': 'osw.pacific-secc-reference-query.v1',
            'status': 'SOURCE_CONTRACT_PREPARED_NOT_INSTALLED', 'owner_id': TARGET,
            'input_sha256': pins, 'route': row, 'owner_map_feature': feature,
            'publication_selector': {'doi': DOI, 'url': URL, 'required_existing_matches': 1},
            'method_source': {'id': METHOD, 'kind': 'internal', 'path': PROTOCOL, 'url': '../' + PROTOCOL,
                              'title': 'OSW Pacific SECC western regional reference protocol v1'},
            'query_url_after_installation': query_url(),
            'atlas_url_after_installation': 'reference-routes.html?atlas-layout=map&atlas-feature=' + quote(TARGET)
                + '&atlas-route=' + quote(ROUTE) + '#route-atlas',
            'admission': {'editorial_reference_routes': 1, 'new_physical_dimensions': 0,
                          'independent_observations': 0, 'annual_dimension_ranges': 0,
                          'physical_state_intersections': 0, 'whole_current_ranked_lengths': 0}}


def canonical_url(value):
    parts = urlsplit(str(value).strip())
    return (parts.hostname or '').lower(), parts.path.rstrip('/')


def publication_source(sources):
    """Reuse an existing record; ambiguity must be reconciled before admission."""
    checked_ids(sources, 'sources')
    matches = [r for r in sources if normalized_doi(r.get('doi', '')) == DOI.lower()
               or normalized_doi(r.get('url', '')) == DOI.lower()
               or canonical_url(r.get('url', '')) == canonical_url(URL)]
    if len(matches) != 1:
        raise ValueError('Exactly one existing Chen/Qiu 2004 publication source required')
    record = matches[0]
    if record.get('doi') and normalized_doi(record['doi']) != DOI.lower():
        raise ValueError('Conflicting existing publication DOI')
    return record['id']


def append(collections, document):
    """Prepare an atomic patch, preserving unrelated scientific and source records."""
    if type(collections) is not dict or encoded(document) != encoded(build_contract()):
        raise ValueError('Changed reviewed Pacific SECC query contract')
    for name in ['objects', 'entities', 'reference_routes', 'sources', 'route_decisions']:
        checked_ids(collections.get(name), name)
    owners = [r for r in collections['objects'] if r['id'] == TARGET]
    entities = [r for r in collections['entities'] if r['id'] == TARGET]
    if (len(owners) != 1 or len(entities) != 1 or owners[0].get('type') != 'named_current'
            or entities[0].get('type') != 'named_current'):
        raise ValueError('Accepted current object and entity required')
    if any(r['id'] == ROUTE or r.get('current_id') == CURRENT for r in collections['reference_routes']):
        raise ValueError('Existing Pacific SECC route requires explicit reconciliation')
    owner = copy.deepcopy(owners[0])
    registry = {r['id'] for r in collections['sources']}
    refs = owner.get('source_ids')
    if (not isinstance(refs, list) or any(not isinstance(r, str) for r in refs)
            or len(set(refs)) != len(refs) or set(refs) - registry
            or type(owner.get('linked_source_count')) is not int or owner['linked_source_count'] != len(refs)):
        raise ValueError('Invalid prior owner provenance')
    for key, cls in [('capabilities', dict), ('evidence_links', list), ('map_features', list), ('section_fingerprints', dict)]:
        if not isinstance(owner.get(key), cls):
            raise ValueError('Invalid prior owner evidence container: ' + key)
    if (owner.get('route_ids') != [] or type(owner['capabilities'].get('reference_route')) is not int
            or owner['capabilities']['reference_route'] != 0):
        raise ValueError('Expected empty prior owner route inventory')
    if any(f.get('candidate_id') == ROUTE for f in owner['map_features']):
        raise ValueError('Existing editorial map feature collision')
    decisions = [r for r in collections['route_decisions'] if r.get('entity_id') == TARGET]
    if (len(decisions) != 1 or owner.get('route_decision_ids') != [decisions[0]['id']]
            or decisions[0].get('route_ids') != [] or type(decisions[0].get('candidate_count')) is not int
            or decisions[0]['candidate_count'] != 0 or decisions[0].get('rank_eligible') is not False
            or not isinstance(decisions[0].get('source_decision'), dict)
            or decisions[0]['source_decision'].get('candidate_ids') != []):
        raise ValueError('Consistent empty prior route decision required')
    paper = publication_source(collections['sources'])
    method = copy.deepcopy(document['method_source'])
    existing = [r for r in collections['sources'] if r['id'] == METHOD]
    if existing and existing != [method]:
        raise ValueError('Changed method source collision')
    row = copy.deepcopy(document['route'])
    row.update(source_id=paper, source_ids=[paper, METHOD])
    feature = copy.deepcopy(document['owner_map_feature'])
    feature['source_id'] = paper
    owner['route_ids'] = [ROUTE]
    owner['capabilities']['reference_route'] = 1
    owner['map_features'].append(feature)
    owner['source_ids'] = sorted(set(refs) | {paper, METHOD})
    owner['linked_source_count'] = len(owner['source_ids'])
    owner['evidence_links'].append({'label': 'Pacific SECC western reference and measurement scope',
                                    'url': 'pacific-secc-reference-support.html'})
    owner['section_fingerprints']['pacific_secc_western_reference'] = fingerprint(row)
    owner['fingerprint'] = fingerprint({k: v for k, v in owner.items() if k != 'fingerprint'})
    decision = copy.deepcopy(decisions[0])
    decision['prior_route_decision'] = copy.deepcopy(decisions[0])
    decision.update(route_ids=[ROUTE], candidate_count=1,
                    construction_status='regional_editorial_reference_constructed',
                    source_catalog_file=CANDIDATE, source_catalog_sha256=PINS[CANDIDATE], source_url=URL,
                    next_action='Recover compatible total-flow axes and physical endpoints; regional drawing probes do not establish seasonal dimensions or whole-current length.')
    decision['source_decision'].update(candidate_ids=[ROUTE],
        reference_path_decision=decision['construction_status'], next_action=decision['next_action'])
    updates = {'reference_routes': [*collections['reference_routes'], row],
               'sources': [*collections['sources'], *([] if existing else [method])],
               'objects': [owner if r['id'] == TARGET else r for r in collections['objects']],
               'route_decisions': [decision if r['id'] == decision['id'] else r for r in collections['route_decisions']]}
    collections.update(updates)
    return {'publication_source_id': paper, 'publication_record_reused': True,
            'reference_route_id': ROUTE, 'installed': False}


def atlas_report(document):
    """Keep the reviewed source calculation available to the existing inline card."""
    if encoded(document) != encoded(build_contract()):
        raise ValueError('Changed reviewed Pacific SECC query contract')
    report = json.loads((ROOT / CANDIDATE).read_bytes())
    report.update(status='reviewed_editorial_regional_reference_connection_pending_installation',
                  rendering_role='derived_inline_source_reference_card_not_additional_observation',
                  source_candidate_file=CANDIDATE, source_candidate_sha256=PINS[CANDIDATE],
                  geography_review_file=REVIEW, geography_review_sha256=PINS[REVIEW],
                  physical_current_axis_admitted=False, physical_state_join_eligible=False,
                  whole_current_length_km=None, annual_length_range_km=None,
                  state_scope_note='AUSE is an editorial display overlap. Physical current passage is unresolved.',
                  remaining_gates=[
                      'Install and verify this exact reference in native/WASM queries and atlas cards.',
                      'Recover continuous total-flow axes and physical alongflow endpoints.',
                      'Establish compatible dated width edges, layer and seasonal dimension ranges.'])
    return report


def catalog_projection(catalog, collections, document):
    """Describe the atlas patch for later native/WASM parity checks, without I/O."""
    report = atlas_report(document)
    rows = [r for r in collections['reference_routes'] if r['id'] == ROUTE]
    if len(rows) != 1:
        raise ValueError('Exactly one admitted reference required for atlas projection')
    row = rows[0]
    expected = copy.deepcopy(document['route'])
    paper = publication_source(collections['sources'])
    expected.update(source_id=paper, source_ids=[paper, METHOD])
    if encoded(row) != encoded(expected):
        raise ValueError('Changed admitted route before atlas projection')
    result = copy.deepcopy(catalog)
    if any(r.get('current_id') == CURRENT or r.get('id') == ROUTE for r in result['candidates']):
        raise ValueError('Existing atlas route requires reconciliation')
    decision = [r for r in collections['route_decisions'] if r.get('entity_id') == TARGET]
    plans = [i for i, r in enumerate(result['remaining_current_decisions']) if r['current_id'] == CURRENT]
    if (len(decision) != 1 or len(plans) != 1 or decision[0].get('route_ids') != [ROUTE]
            or result['remaining_current_decisions'][plans[0]].get('candidate_ids') != []):
        raise ValueError('Consistent prior atlas plan and admitted decision required')
    entry = copy.deepcopy(row)
    entry.update(candidate_file=CANDIDATE, candidate_sha256=PINS[CANDIDATE],
                 route_extent_kind='western mean-circulation editorial reference reach',
                 scenario_range_km=copy.deepcopy(row['public_editorial_probe_span_km']),
                 nominal_atlas_state_crossings=[], state_intersection_status='unassessed_no_physical_join_admitted',
                 remaining_gates=copy.deepcopy(report['remaining_gates']), report_inline=report)
    result['candidates'].append(entry)
    result['remaining_current_decisions'][plans[0]] = copy.deepcopy(decision[0]['source_decision'])
    for key, delta in [('route_candidates', 1), ('currents_with_route_candidates', 1),
                       ('currents_without_route_candidates', -1), ('currents_without_any_reference_card', -1)]:
        value = result['counts'].get(key)
        if type(value) is not int or value + delta < 0:
            raise ValueError('Invalid prior atlas count: ' + key)
        result['counts'][key] = value + delta
    strategies = [s for s in result['planning_taxonomy']['strategies'] if s['id'] == decision[0]['strategy_id']]
    if (len(strategies) != 1 or type(strategies[0].get('unbuilt_count')) is not int
            or strategies[0]['unbuilt_count'] < 1):
        raise ValueError('Consistent prior atlas strategy required')
    strategies[0]['unbuilt_count'] -= 1
    return result


def page(document):
    esc = html.escape
    row = document['route']
    return ('''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pacific SECC western reference | OSW</title>
<style>body{font:17px/1.6 system-ui,sans-serif;margin:0;background:#071c2b;color:#e1edf2}
main{max-width:960px;margin:auto;padding:24px}a{color:#89dbf5}img{width:100%;height:auto;background:white}
.metric{font-size:2rem;margin:0}section{margin-block:28px}dt{font-weight:700}dd{margin:0 0 14px}
nav{display:flex;gap:18px;flex-wrap:wrap}h1{line-height:1.2}</style>
<main><nav><a href="dashboard.html">Dashboard</a><a href="reference-routes.html">Reference atlas</a></nav>
<h1>Pacific South Equatorial Countercurrent</h1>
<p>Western mean-circulation reference reach · 164°E–180°E</p>
<p class="metric">Approximately 1,800 km</p>
<p>This distance follows an OSW editorial drawing through the western part of the current’s broad source geography.</p>
<figure style="margin:0"><a href="../''' + esc(FIGURE) + '''"><img src="../''' + esc(FIGURE) + '''"
alt="Editorial western Pacific SECC reference route from 164 degrees east to 180 degrees east near 9 to 9.5 degrees south, with alternative drawings."></a>
<figcaption>Open the reviewed reference map. End gates and bends are OSW drawing choices.</figcaption></figure>
<section><h2>What the estimate means</h2><dl>
<dt>Saved nominal polyline</dt><dd>1,761.235 km, rounded to approximately 1,800 km for display.</dd>
<dt>Drawing sensitivity</dt><dd>27 drawings span 1,760.737–1,775.154 km. The outward-rounded display envelope is 1,700–1,800 km. This is editorial sensitivity; seasonal range and measurement uncertainty remain unknown.</dd>
<dt>Geographic screening</dt><dd>All 27 drawings passed the retained OSW land mask and Natural Earth 1:10 million coastline checks at sample spacing no greater than 1 km.</dd>
<dt>Layer and time</dt><dd>''' + esc(row['layer']) + ' ' + esc(row['time_convention']) + '''</dd>
<dt>Remaining measurements</dt><dd>Whole-current length, physical width, current thickness, annual dimension ranges and dated current axes remain unresolved.</dd>
<dt>Map context</dt><dd>AUSE and NASA crop level2_G_4 overlap this editorial drawing. Physical current passage through the state and identification in NASA imagery remain unverified.</dd>
</dl></section><section><h2>Source and method</h2>
<p><a href="''' + esc(URL) + '''#page=2">Chen and Qiu (2004), Figure 1b</a>,
<a href="https://doi.org/10.1029/2003JC002243">doi:10.1029/2003JC002243</a>.
The publication supplies broad circulation context. The vertices are OSW-selected.</p>
<p><a href="../''' + PROTOCOL + '''">Measurement rules</a> · <a href="../''' + CANDIDATE + '''">Saved calculation</a> ·
<a href="../''' + REVIEW + '''">Geography and map review</a></p></section>
<section><h2>Query and atlas delivery</h2><p>This source page is prepared. The new route is awaiting native/WASM and atlas installation; installed coverage totals are unchanged.</p>
</section></main></html>\n''').encode('utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'check'])
    args = parser.parse_args()
    document = build_contract()
    outputs = {FILE: encoded(document), PAGE: page(document)}
    for path, raw in outputs.items():
        if args.action == 'build':
            (ROOT / path).write_bytes(raw)
        elif (ROOT / path).read_bytes() != raw:
            raise ValueError('Saved projection differs: ' + path)
    print(json.dumps({'status': 'PASS', 'installed': False, 'admission': document['admission']}))
