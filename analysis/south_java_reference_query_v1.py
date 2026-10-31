"""Prepare one audited South Java editorial reference; never load a packet here."""
import copy
import hashlib
import html
import json
from pathlib import Path
from urllib.parse import quote

from check_south_java_parent_audit_v1 import publication
from loop_published_metrics_query_v1 import checked_ids, encoded, fingerprint

ROOT = Path(__file__).resolve().parents[1]
CURRENT = 'south-java'
TARGET = 'current:' + CURRENT
ROUTE = 'south-java-java-bali-reference-reach-v1'
METHOD = 'source:south-java-java-bali-reference-method-v1'
PARENT = 'f0e046651b75c84da488c4e81204e410b18f37256e102c26a0ab2f70b5f69184'
CANDIDATE = 'research/south-java-java-bali-reference-path-v2-candidate.json'
FIGURE = 'figures/south-java-java-bali-reference-path-v2-candidate.svg'
COMPACT = 'figures/south-java-java-bali-reference-compact-v1.svg'
AUDIT = 'research/south-java-parent-audit-result-v1.json'
SELECTED = 'research/south-java-parent-audit-selected-records-v1.json'
REVIEW = 'research/south-java-reference-map-review-v2.json'
GEOGRAPHY = 'research/south-java-reference-geography-v1.json'
AUDIT_REVIEW = 'research/south-java-parent-audit-execution-review-v1.json'
PROTOCOL = 'plans/south-java-reference-query-protocol-v1.md'
MODULE = 'analysis/south_java_reference_query_v1.py'
FILE = 'research/south-java-reference-query-contract-v1.json'
PAGE = 'almanac/south-java-reference-support.html'
PRIMARY_URL = 'https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2006JC003486'
PINS = {'research/south-java-java-bali-reference-path-v2-candidate.json': 'e0e280c236c9836c45c3857338927eb07a48ab549045f83b1c1b9785dad7c2e1', 'figures/south-java-java-bali-reference-path-v2-candidate.svg': 'dfa3f2d9b4ccc9b7e7b15da136ea49ae248090db149274dd629406ea56b00dd5', 'figures/south-java-java-bali-reference-compact-v1.svg': '3fea9a65937e512d2601f6db0d4b2a3f5ce525fd5ddea47d92aa84e6be3b8bd2', 'research/south-java-parent-audit-result-v1.json': '59d8117852efd89da7142d01fb10d775e6053689b1209f630d0eb67c6e2ea63e', 'research/south-java-parent-audit-selected-records-v1.json': '650d09c5babc6001050846f0eda1b4f1abd51c40bfd4b9c917819793e1e2ab68', 'research/south-java-reference-map-review-v2.json': 'd7a5c613fbd33e106671b625c45d671fc3e2182a329041c170f94e86c856b069', 'research/south-java-reference-geography-v1.json': 'ee627712d27ddc272eddaafb37b270bd51ce247f4e3de2b26b8d02dbf53e2da7', 'research/south-java-parent-audit-execution-review-v1.json': '37873895cf96dff192356b0ea919eab53ca2266b84ddaff9bae31aee9b01f136', 'research/south-java-alongflow-source-review-v1.json': '8ab91ed9836f3458f0523c13a010bcea87863972877765f287886eab9405acae', 'research/south-java-reference-geography-result-v1.json': 'db80d1a7622cde218a04f1b5e41cc89457a06e12db8c4cac212d0499d168ccd1'}


def read(root, path):
    return json.loads((Path(root) / path).read_bytes())


def query_url():
    value = {'collection': 'reference_routes', 'filters': [{'field': 'id', 'op': 'eq', 'value': ROUTE}], 'limit': 1}
    return 'query.html?q=' + quote(json.dumps(value, separators=(',', ':'))) + '&inspect=' + quote(ROUTE) + '#query-map-section'


def atlas_url():
    return 'reference-routes.html?atlas-layout=map&atlas-feature=' + quote(TARGET) + '&atlas-route=' + quote(ROUTE) + '#route-atlas'


def build_contract(root=ROOT):
    root = Path(root)
    for path, expected in PINS.items():
        if hashlib.sha256((root / path).read_bytes()).hexdigest() != expected:
            raise ValueError('Changed reviewed South Java evidence: ' + path)
    candidate, audit, selected, review, geography, audit_review = [read(root, p) for p in
        [CANDIDATE, AUDIT, SELECTED, REVIEW, GEOGRAPHY, AUDIT_REVIEW]]
    if (audit['status'] != 'AUDIT_COMPLETE_READ_ONLY' or audit['logical_sha256'] != PARENT
            or audit['selected_records_sha256'] != PINS[SELECTED]
            or audit_review['status'] != 'PASS' or not audit_review['request_disabled']
            or not audit['original_planning_source_matches'] or not audit['original_planning_receipt_matches']
            or not all(audit['original_publication_records_unchanged'].values())
            or review['status'] != 'PASS_STANDALONE_GEOMETRY_PRESERVING_PRESENTATION'
            or len(review['actual_rendered_images_inspected']) != 3
            or any(row['actually_viewed'] is not True for row in review['actual_rendered_images_inspected'])
            or geography['all_27_clear'] is not True or len(geography['scenarios']) != 27
            or candidate['scenario_count'] != 27 or candidate['current_id'] != CURRENT
            or candidate['nominal_reference_path_km'] != 1127.329
            or candidate['rank_eligible_published_estimates'] is not False
            or candidate['presentation_revision']['geometry_attributes_unchanged'] is not True):
        raise ValueError('Complete audited parent, reviewed geometry and preserved presentation required')
    for name, value in selected['publications'].items():
        if publication(list(selected['publications'].values()), name) != value:
            raise ValueError('Changed existing publication binding')
    pins = dict(PINS)
    for path in [MODULE, PROTOCOL, 'analysis/check_south_java_parent_audit_v1.py',
                 'analysis/loop_published_metrics_query_v1.py']:
        pins[path] = hashlib.sha256((root / path).read_bytes()).hexdigest()
    papers = [selected['publications'][key]['id'] for key in ['iskandar_2006', 'sprintall_2010']]
    row = {
        'id': ROUTE, 'entity_id': TARGET, 'current_id': CURRENT,
        'name': 'South Java — Java-Bali reference reach', 'label': 'South Java: 105E–115E reference',
        'type': 'editorial_regional_reference_connection', 'status': 'reviewed_editorial_regional_reference_connection',
        'record_type': 'regional_editorial_reference_not_observed_axis',
        'scope': candidate['scope'], 'layer': candidate['layer'], 'time_convention': candidate['time_convention'],
        'source_id': papers[0], 'source_ids': papers + [METHOD], 'method_source_id': METHOD,
        'source_url': PRIMARY_URL, 'source_locator': candidate['source_locator'],
        'source_file': CANDIDATE, 'source_file_sha256': PINS[CANDIDATE], 'source_pointer': '',
        'coordinates_lon_lat': copy.deepcopy(candidate['coordinates_lon_lat']),
        'geometry': {'type': 'LineString', 'coordinates': copy.deepcopy(candidate['coordinates_lon_lat'])},
        'geometry_role': 'editorial_reference_route', 'role': 'editorial_reference_route',
        'computed_nominal_reference_length_km': candidate['nominal_reference_path_km'],
        'approximate_reference_path_km': candidate['reported_approximate_reference_path_km'],
        'editorial_probe_length_range_km': candidate['scenario_range_km'],
        'public_editorial_probe_span_km': candidate['reported_scenario_range_km'],
        'scenario_count': 27, 'comparison_group': 'osw_studied_reach_routes',
        'figure': FIGURE, 'figure_file': FIGURE, 'figure_sha256': PINS[FIGURE],
        'compact_figure_file': COMPACT, 'compact_figure_sha256': PINS[COMPACT], 'diagnostic_page': PAGE,
        'rank_eligible': False, 'whole_current_length_km': None, 'physical_width_km': None,
        'current_thickness_m': None, 'annual_length_range_km': None, 'annual_width_range_km': None,
        'uncertainty_km': None, 'sample_date': None, 'independent_observation_count': 0,
        'physical_current_axis_admitted': False, 'physical_current_edges_admitted': False,
        'physical_state_join_eligible': False, 'seasonal_playback_eligible': False,
        'geographic_seasonal_playback_eligible': False, 'nasa_identity_verified': False,
        'nominal_atlas_state_crossings': None, 'recommended_nasa_tile_id': None,
        'display_context': {'state_codes': candidate['nominal_atlas_state_crossings'],
            'recommended_nasa_tile_id': candidate['recommended_nasa_tile_id'], 'role': 'editorial_display_overlap_only'}}
    feature = {'geometry': copy.deepcopy(row['geometry']), 'role': 'editorial_reference_route',
        'candidate_id': ROUTE, 'source_id': papers[0], 'source_ids': papers + [METHOD],
        'note': row['scope'], 'source_url': PRIMARY_URL, 'source_locator': row['source_locator'],
        'source_file_sha256': PINS[CANDIDATE], 'observation_date': None, 'layer': row['layer'],
        'time_convention': row['time_convention'], 'physical_current_axis_admitted': False,
        'physical_state_join_eligible': False}
    return {'schema': 'osw.south-java-reference-query.v1', 'status': 'SOURCE_CONTRACT_PREPARED_NOT_INSTALLED',
        'owner_id': TARGET, 'parent_logical_sha256': PARENT, 'input_sha256': pins,
        'prior_owner': selected['owner'], 'prior_entity': selected['entity'],
        'prior_decision': selected['planning_decision'], 'prior_owner_sources': selected['owner_sources'],
        'existing_publications': selected['publications'], 'expected_parent_source_count': 210,
        'expected_parent_route_count': 81, 'route': row, 'owner_map_feature': feature,
        'method_source': {'id': METHOD, 'kind': 'internal', 'path': PROTOCOL, 'url': '../' + PROTOCOL,
                          'title': 'OSW South Java Java-Bali reference protocol v1'},
        'query_url_after_installation': query_url(), 'atlas_url_after_installation': atlas_url(),
        'admission': {'editorial_reference_routes': 1, 'internal_method_sources': 1,
            'new_publications': 0, 'new_current_identities': 0, 'new_physical_dimensions': 0,
            'independent_observations': 0, 'annual_dimension_ranges': 0, 'physical_state_intersections': 0,
            'whole_current_ranked_lengths': 0}}


def append(collections, document, *, parent_logical_sha256):
    if parent_logical_sha256 != PARENT or encoded(document) != encoded(build_contract()):
        raise ValueError('Exact source contract and installed parent identity required')
    for name in ['sources', 'objects', 'entities', 'reference_routes', 'route_decisions']:
        if not isinstance(collections.get(name), list):
            raise ValueError('Missing parent collection: ' + name)
        checked_ids(collections[name], name)
    if len(collections['sources']) != 210 or len(collections['reference_routes']) != 81:
        raise ValueError('Unexpected parent source/reference counts')
    for collection, field, expected in [('objects', 'id', document['prior_owner']),
            ('entities', 'id', document['prior_entity']), ('route_decisions', 'entity_id', document['prior_decision'])]:
        if [r for r in collections[collection] if r.get(field) == TARGET] != [expected]:
            raise ValueError('Changed audited South Java record: ' + collection)
    if any(r.get('id') == ROUTE or r.get('current_id') == CURRENT for r in collections['reference_routes']):
        raise ValueError('South Java reference already present; reconcile before append')
    registry = {r['id']: r for r in collections['sources']}
    if METHOD in registry:
        raise ValueError('Method-source ID collision')
    for expected in document['prior_owner_sources']:
        if registry.get(expected['id']) != expected:
            raise ValueError('Changed prior South Java bound source')
    for key, expected in document['existing_publications'].items():
        if publication(collections['sources'], key) != expected:
            raise ValueError('Changed existing publication')
    owner = copy.deepcopy(document['prior_owner'])
    if owner['route_ids'] != [] or owner['capabilities']['reference_route'] != 0:
        raise ValueError('Expected empty audited route inventory')
    row = copy.deepcopy(document['route'])
    owner['route_ids'] = [ROUTE]
    owner['capabilities']['reference_route'] = 1
    owner['map_features'].append(copy.deepcopy(document['owner_map_feature']))
    owner['source_ids'] = sorted(set(owner['source_ids']) | set(row['source_ids']))
    owner['linked_source_count'] = len(owner['source_ids'])
    owner['route_url'] = atlas_url()
    owner['evidence_links'].append({'label': 'View the South Java reference reach',
                                    'url': 'south-java-reference-support.html'})
    owner['section_fingerprints']['south_java_java_bali_reference'] = fingerprint(row)
    owner['fingerprint'] = fingerprint({k: v for k, v in owner.items() if k != 'fingerprint'})
    decision = copy.deepcopy(document['prior_decision'])
    decision['prior_route_decision'] = copy.deepcopy(document['prior_decision'])
    decision.update(route_ids=[ROUTE], candidate_count=1, construction_status='regional_editorial_reference_constructed',
        source_catalog_file=CANDIDATE, source_catalog_sha256=PINS[CANDIDATE], source_url=PRIMARY_URL,
        source_id=row['source_id'], source_ids=copy.deepcopy(row['source_ids']),
        next_action='Recover compatible dated physical axes and endpoints; this partial drawing does not establish whole-current or seasonal dimensions.')
    decision['source_decision'].update(candidate_ids=[ROUTE], name_source_url=PRIMARY_URL,
        reference_path_decision=decision['construction_status'], next_action=decision['next_action'])
    updates = {'sources': [*collections['sources'], copy.deepcopy(document['method_source'])],
        'reference_routes': [*collections['reference_routes'], row],
        'objects': [owner if r['id'] == TARGET else r for r in collections['objects']],
        'route_decisions': [decision if r.get('entity_id') == TARGET else r for r in collections['route_decisions']]}
    collections.update(updates)
    return {'reference_route_id': ROUTE, 'existing_publications_reused': 2, 'new_method_sources': 1,
            'new_physical_dimensions': 0, 'installed': False}


def support_page(document, *, installed=False):
    if encoded(document) != encoded(build_contract()):
        raise ValueError('Changed support-page source contract')
    escape = html.escape
    links = ('<p><a href="' + escape(query_url(), quote=True) + '">Inspect the reference record</a> · '
             '<a href="' + escape(atlas_url(), quote=True) + '">Open the atlas card</a></p>') if installed else (
             '<p class="status">Candidate: awaiting query integration. Atlas and record links activate after installation.</p>')
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>South Java reference reach · OSW</title><style>
:root{color-scheme:dark}body{margin:0;background:#071d2d;color:#e9f3f6;font:16px/1.6 system-ui,sans-serif}main{max-width:1000px;margin:auto;padding:24px}a{color:#8cdbf0}nav{display:flex;gap:18px;flex-wrap:wrap}h1{line-height:1.2}picture,img{display:block;width:100%;max-width:800px;border-radius:5px}dl{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}dl div{padding:10px;background:#113044}dt{font-size:13px;color:#b5cfda}dd{margin:0;font-weight:650}.status{padding:10px;background:#17384a}details{margin-top:20px}li{margin:8px 0}@media(max-width:480px){main{padding:14px}dl{grid-template-columns:1fr}}
</style><main><nav><a href="dashboard.html">Dashboard</a><a href="reference-routes.html">Reference atlas</a><a href="query.html">Query</a></nav>
<h1>South Java reference reach</h1><p>An editorial study reach south of Java and Bali, between 105°E and 115°E.</p>
<dl><div><dt>Reference distance</dt><dd>≈ 1,100 km</dd></div><div><dt>Drawing envelope</dt><dd>1,100–1,200 km</dd></div><div><dt>Scope</dt><dd>Partial reference reach</dd></div></dl>
<picture><source media="(max-width:480px)" srcset="../''' + COMPACT + '''"><img src="../''' + FIGURE + '''" alt="South Java editorial reach with 105E and 115E gates and 27 drawing scenarios"></picture>
<p><a href="../''' + FIGURE + '''">Open the full reference map</a></p>
<p>Vertices and gates are OSW drawing choices. This distance is not a measurement of the entire South Java Current.</p>
''' + links + '''<details><summary>How this reference is measured</summary><p>The nominal WGS84 polyline is 1,127.329 km. Three drawings and independent endpoint shifts produce 27 cases, spanning 1,117.074–1,150.703 km. Public values are rounded to 100 km; the drawing envelope is rounded outward. It is not a seasonal range or confidence interval.</p>
<p>All 27 drawings passed the OSW coarse ground and Natural Earth1:10 million coastline checks at no more than 1 km sampling. This establishes geographic screening, not a velocity axis or a physical current boundary.</p></details>
<h2>Source scope</h2><p>The 1990–2003 model context and 2004–2006 Ombai observations remain separate. The source model's upper 150 m analysis band is not a measured thickness. The undercurrent, Savu-Ombai extension, physical widths and annual geometry are excluded from this drawing.</p>
<ul><li><a href="''' + PRIMARY_URL + '''">Iskandar et al.2006: study meridians and surface/undercurrent definitions</a></li>
<li><a href="https://pordlabs.ucsd.edu/jsprintall/pub_dir/Sprintall_etal_DYNAT2010.pdf">Sprintall et al.2010: regional system geography and Ombai observations</a></li></ul>
</main></html>'''


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'check'])
    args = parser.parse_args()
    document = build_contract()
    outputs = {FILE: encoded(document), PAGE: support_page(document).encode()}
    for path, raw in outputs.items():
        if args.action == 'build':
            (ROOT / path).write_bytes(raw)
        elif (ROOT / path).read_bytes() != raw:
            raise ValueError('Changed prepared source output: ' + path)
    print(json.dumps({'status': 'PASS', 'prepared': True, 'installed': False, 'new_physical_dimensions': 0}))
