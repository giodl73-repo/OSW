"""Regional source-reference connection; no measured whole-current axis."""
import copy
import hashlib
import io
import itertools
import json
import math
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

import shapefile
from pyproj import Geod
from shapely.geometry import LineString, box, shape
from shapely.ops import unary_union
from build_cartographic_current_state_join import load_states, project
from build_motion_state_join import PROVINCES, polygon_parts
import hansen_asar_widths as asar
import madagascar_coastline_comparison as land_source
from build_current_reference_path_candidate import display_coordinates

ROOT = Path(__file__).resolve().parents[1]
INPUT = 'research/nwasc-source-anchor-reference-route-input.json'
FILE = 'research/nwasc-source-anchor-reference-route.json'
FIGURE = 'figures/nwasc-source-anchor-reference-route.svg'
PROTOCOL = 'plans/nwasc-source-anchor-route-protocol-v1.md'
OPERATOR = 'analysis/nwasc_source_anchor_route.py'
BASE = 'research/ocean-current-working-reference-routes.json'
METHOD = 'source:nwasc-source-anchor-route-v1'
ROUTE = 'norwegian-atlantic-slope-asar-regional-reference-route'
CURRENT = 'norwegian-atlantic-slope'
GEOD = Geod(ellps='WGS84')
ANCHORS = [[-.5, 62], [3, 62 + 40 / 60], [4.25, 62.8]]


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf8')


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def distance(points):
    return sum(GEOD.inv(*a, *b)[2] for a, b in zip(points, points[1:])) / 1000


def densify(points, metres=1000):
    result = [list(points[0])]
    for a, b in zip(points, points[1:]):
        n = max(1, math.ceil(GEOD.inv(*a, *b)[2] / metres))
        if n > 1:
            result.extend([list(p) for p in GEOD.npts(*a, *b, n - 1)])
        result.append(list(b))
    return result


def bend(a, b, offset):
    azimuth, _, length = GEOD.inv(*a, *b)
    lon, lat, _ = GEOD.fwd(*a, azimuth, length / 2)
    forward = GEOD.inv(lon, lat, *b)[0]
    lon, lat, _ = GEOD.fwd(lon, lat, forward + 90, offset * 1000)
    return [lon, lat]


def source_input():
    doc = json.loads((ROOT / INPUT).read_bytes())
    source, _ = asar.verify_inputs()
    points = [source['width_records'][0]['source_reference_position_lon_lat'],
              source['mixed_contexts'][0]['source_reference_position_lon_lat'],
              source['width_records'][1]['source_reference_position_lon_lat']]
    if points != ANCHORS or doc['coordinates_lon_lat'] != points or doc['source_anchor_ids'] != ['P1', 'P2', 'S1']:
        raise ValueError('Changed source anchors, sign, source order or ownership')
    if (doc['bend_probe_offsets_km'] != [-10, 0, 10] or doc['report_rounding_km'] != 10
            or doc['land_region_lon_lat'] != [-4, 58, 10, 66] or doc['current_id'] != CURRENT
            or doc['crs'] != 'OGC:CRS84' or doc['source_url'] != asar.URL):
        raise ValueError('Changed declared bend/readback convention')
    if doc['reference_period'] != {'start_month': '2007-08', 'end_month': '2010-07',
            'interpretation': 'Source mean-field context; no exact route occupation dates or dated current axis.'}:
        raise ValueError('Changed mean-field scope')
    for key in ['physical_current_axis_admitted', 'physical_current_edges_admitted',
                'physical_state_join_eligible', 'seasonal_playback_eligible', 'rank_eligible']:
        if doc[key] is not False:
            raise ValueError('Reference connection promoted: ' + key)
    return doc


def northern_land(region):
    receipt = json.loads((ROOT / land_source.RECEIPT).read_bytes())
    raw = (ROOT / land_source.ARCHIVE).read_bytes()
    if hashlib.sha256(raw).hexdigest() != land_source.SOURCE_SHA or receipt['sha256'] != land_source.SOURCE_SHA or receipt['bytes'] != len(raw):
        raise ValueError('Changed Natural Earth original')
    if receipt['package_version'] != '5.1.1' or shapefile.__version__ != '2.3.1':
        raise ValueError('Changed land edition/reader')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        if {n for n in archive.namelist() if not n.endswith('/')} != set(receipt['members']):
            raise ValueError('Changed land archive member set')
        for name, item in receipt['members'].items():
            data = archive.read(name)
            if len(data) != item['bytes'] or hashlib.sha256(data).hexdigest() != item['sha256']:
                raise ValueError('Changed land archive member')
        if 'GCS_WGS_1984' not in archive.read('ne_10m_land.prj').decode():
            raise ValueError('Unexpected land CRS')
        with shapefile.Reader(**{x: io.BytesIO(archive.read('ne_10m_land.' + x)) for x in ['shp', 'shx', 'dbf']}) as reader:
            pieces = []
            for item in reader.iterShapes(bbox=region.bounds):
                polygon = shape(item.__geo_interface__)
                if not polygon.is_valid:
                    raise ValueError('Invalid original land polygon; no silent repair')
                clipped = polygon.intersection(region)
                if not clipped.is_empty:
                    pieces.append(clipped)
    land = unary_union(pieces)
    if land.is_empty or not land.is_valid:
        raise ValueError('Missing northern land context')
    return land


def land_contacts(points, fine, coarse):
    samples = densify(points)
    return {'finer_land_contact': not LineString(samples).intersection(fine).is_empty,
            'coarse_land_contact': not LineString([project(*p) for p in samples]).intersection(coarse).is_empty}


def build():
    source = source_input()
    region = box(*source['land_region_lon_lat'])
    fine = northern_land(region)
    tree = ET.parse(PROVINCES).getroot()
    land_path = next(n.get('d') for n in tree.iter() if n.get('class') == 'land-context')
    coarse = unary_union(polygon_parts(land_path))
    states = load_states()
    scenarios = []
    for first, second in itertools.product(source['bend_probe_offsets_km'], repeat=2):
        points = [ANCHORS[0], bend(ANCHORS[0], ANCHORS[1], first), ANCHORS[1],
                  bend(ANCHORS[1], ANCHORS[2], second), ANCHORS[2]]
        contacts = land_contacts(points, fine, coarse)
        export = [list(p) if i in [0,2,4] else [round(p[0],8),round(p[1],8)] for i,p in enumerate(points)]
        rounded_contacts = land_contacts(export, fine, coarse)
        if any(contacts.values()) or any(rounded_contacts.values()):
            raise ValueError('Declared source-anchored probe contacts a land mask; retain/review, never suppress')
        display = LineString(display_coordinates(points))
        scenarios.append({'id': f'bends:{first}:{second}', 'bend_offsets_km': [first, second],
            'coordinates_lon_lat': export, 'length_km': round(distance(points), 6),
            'atlas_state_crossings': sorted(k for k, polygon in states.items() if display.intersection(polygon).length > 1e-8),
            **contacts, 'rounded_geometry_land_contacts': rounded_contacts})
    nominal = round(distance(ANCHORS), 6)
    low, high = min(s['length_km'] for s in scenarios), max(s['length_km'] for s in scenarios)
    projected = LineString(display_coordinates(ANCHORS))
    nominal_states = sorted(k for k, polygon in states.items() if projected.intersection(polygon).length > 1e-8)
    tiles = json.loads((ROOT / 'almanac/release/v0.1.0/tiles.json').read_bytes())
    movie_context = []
    for tile in tiles:
        west, east = tile['longitude_range_unwrapped']; south, north = tile['latitude_range']
        crop = box(*project(west, north), *project(east, south))
        lines = [LineString(display_coordinates(s['coordinates_lon_lat'])) for s in scenarios]
        fractions = [max(0, min(1, line.intersection(crop).length / line.length)) for line in lines]
        if max(fractions) <= 1e-8:
            continue
        movie_context.append({'tile_id': tile['tile_id'], 'url': tile['url'], 'source_id': tile['source_id'], 'zoom': tile['zoom'],
            'nominal_display_route_fraction': round(projected.intersection(crop).length / projected.length, 6),
            'scenario_display_route_fraction_range': [round(min(fractions), 6), round(max(fractions), 6)],
            'complete_display_route_in_all_scenarios': min(fractions) >= 1 - 1e-8,
            'interpretation': 'Equirectangular reference-line/crop display overlap only; no physical current or dated movie identification.'})
    movie_context.sort(key=lambda r: (-r['zoom'], -r['nominal_display_route_fraction'], r['tile_id']))
    complete = [x for x in movie_context if x['complete_display_route_in_all_scenarios']]
    planning = copy.deepcopy(json.loads((ROOT / 'research/norwegian-atlantic-slope-working-admission.json').read_bytes())['identity_entry']['route_planning_decision'])
    planning.update(reference_path_decision='regional_source_anchor_connection_constructed', candidate_ids=[ROUTE],
        existing_scope=source['scope'],
        next_action='Recover a verified current axis, bathymetric contour and dated geometry beyond the regional P1-P2-S1 connection.',
        planning_basis='Three source-provided reference coordinates support a regional editorial geodesic connection.',
        strategy_next_action='Keep the source anchors fixed; recover independent current geometry before any whole-current or seasonal-axis claim.')
    method = {'id': METHOD, 'kind': 'internal', 'label': 'OSW NwASC source-anchor regional reference protocol v1',
              'url': '../' + PROTOCOL, 'repository_path': PROTOCOL, 'path': PROTOCOL,
              'used_in_collections': ['reference_routes', 'route_decisions', 'objects'],
              'material_use_class': 'internal_calculation_method', 'provider_asset_redistributed': False}
    row = {'id': ROUTE, 'current_id': CURRENT, 'name': source['name'], 'status': source['status'],
           'comparison_group': 'osw_source_anchor_connections', 'scope': source['scope'],
           'route_extent_kind': source['route_extent_kind'], 'approximate_reference_path_km': round(nominal / 10) * 10,
           'scenario_range_km': [math.floor(low / 10) * 10, math.ceil(high / 10) * 10], 'scenario_count': 9,
           'source_url': source['source_url'], 'source_locator': source['source_locator'], 'supporting_sources': [],
           'candidate_file': FILE, 'generator_sha256': digest(OPERATOR), 'figure': FIGURE,
           'nominal_atlas_state_crossings': nominal_states,
           'recommended_nasa_tile_id': complete[0]['tile_id'] if complete else None,
           'remaining_gates': [planning['next_action'], 'No observed axis, physical state passage, seasonal geometry or uncertainty envelope admitted.'],
           'parent_current_id': None, 'parent_scope_note': 'Regional reference only; no reassignment to an ambiguous Norwegian Current family.',
           'physical_state_join_eligible':False,'physical_current_axis_admitted':False,'seasonal_playback_eligible':False,
           'reference_period':source['reference_period'],'ordering_sensitivity': None, 'source_ids': [asar.SOURCE, METHOD], 'rank_eligible': False,
           'geometry': {'type': 'LineString', 'coordinates': ANCHORS}, 'geometry_role': 'editorial_reference_route', 'role':'editorial_reference_route'}
    paths = [INPUT, PROTOCOL, OPERATOR, asar.FILE, asar.ACQUISITION, BASE,
             land_source.ARCHIVE, land_source.RECEIPT, 'analysis/build_current_reference_path_candidate.py',
             'analysis/build_cartographic_current_state_join.py', 'analysis/build_motion_state_join.py',
             'figures/osw-province-atlas-interactive.svg', 'almanac/release/v0.1.0/tiles.json',
             'research/norwegian-atlantic-slope-working-admission.json', 'requirements-geography.txt', 'requirements-test.txt']
    return {**source, 'route_id': ROUTE, 'input_file': INPUT, 'input_sha256': digest(INPUT),
            'generator_file': OPERATOR, 'generator_sha256': digest(OPERATOR),
            'input_dependencies_sha256': {p: digest(p) for p in paths},
            'figure_aspect_ratio': .66, 'map_view_box':[0,0,1000,660],
            'coordinate_selection':'Three unchanged author-provided nominal reference points. OSW connects them with geodesics; no current-core endpoints or500m bathymetric contour inferred.',
            'scenario_rule':'Nine finite fixed-anchor bend probes of-10,0,+10km on each leg; geometry sensitivity only, not positional error or seasonal variability.',
            'source_citation':'Hansen etal(2011), Monitoring the surface inflow of Atlantic Water to the Norwegian Sea using Envisat ASAR,doi:10.1029/2011JC007375.',
            'source_reference_anchors':[{'id':name,'coordinates_lon_lat':p,'source_notation':text} for name,p,text in zip(['P1','P2','S1'],ANCHORS,['62N,0deg30minW','62deg40minN,3E','62deg48minN,4deg15minE'])],
            'method': 'Sum of two shortest WGS84 legs through unchanged source reference points; no current axis or bathymetric contour reconstructed.',
            'nominal_reference_path_km': nominal, 'reported_approximate_reference_path_km': row['approximate_reference_path_km'],
            'scenario_range_km': [low, high], 'reported_scenario_range_km': row['scenario_range_km'],
            'scenario_count': 9, 'scenarios': scenarios, 'figure': FIGURE, 'rank_eligible_published_estimates':False,
            'candidate_comparison_group':'osw_source_anchor_connections',
            'canonical_spatial_geometry': {'type': 'LineString', 'coordinates': [[round((x - 60) * 360 / 1480 - 180, 8),
                round(90 - (y - 90) * 180 / 740, 8)] for x, y in display_coordinates(ANCHORS)]},
            'nominal_atlas_state_crossings': nominal_states, 'state_semantic_exclusions': [],
            'map_land_check': 'Nine retained bend probes and rounded exports avoid coarse OSW and Natural Earth1:10M5.1.1 land masks; no surveyed, bathymetric or navigation clearance.',
            'state_relation_role': 'Editorial source-reference connection/display-state crossings; physical passage unresolved.',
            'atlas_map_sha256': digest('figures/osw-province-atlas-interactive.svg'),
            'nasa_movie_context': movie_context, 'nasa_tiles_sha256': digest('almanac/release/v0.1.0/tiles.json'),
            'recommended_nasa_tile_id': row['recommended_nasa_tile_id'],
            'route_record': row, 'planning_decision': planning, 'method_source': method,
            'bend_sensitivity_is_uncertainty': False, 'source_coordinate_uncertainty_km': None,
            'whole_current_length_km': None, 'annual_length_range_km': None}


def route_record(doc):
    return {**copy.deepcopy(doc['route_record']), 'candidate_sha256': digest(FILE)}


def extend_catalogue(base, doc):
    result = copy.deepcopy(base)
    position=next((i for i,r in enumerate(result['candidates']) if r['approximate_reference_path_km']<doc['reported_approximate_reference_path_km']),len(result['candidates']))
    result['candidates'].insert(position,route_record(doc))
    result['remaining_current_decisions'].append(copy.deepcopy(doc['planning_decision']))
    result['working_scope'] += ' Includes one source-anchor NwASC regional connection; no whole-current axis inferred.'
    result['working_catalogue_version'] = '0.4.0-draft-source-anchor-route'
    result['counts'].update(route_candidates=78, currents_with_route_candidates=72,
        accepted_current_names=102, currents_without_any_reference_card=30,
        source_anchor_connection_candidates=1, route_decision_records=91)
    result['effective_accepted_current_count'] = 102
    for s in result['planning_taxonomy']['strategies']:
        if s['id'] == doc['planning_decision']['route_strategy_id']:
            s['current_count'] += 1
    return result


def figure(doc):
    region = box(-4, 58, 10, 66)
    land = northern_land(region).simplify(.01, preserve_topology=True)
    x0, y0 = project(-4, 66); x1, y1 = project(10, 58)
    def path(points):
        return 'M' + 'L'.join(f'{project(*p)[0]:.6f},{project(*p)[1]:.6f}' for p in points)
    polygons = list(land.geoms) if land.geom_type == 'MultiPolygon' else [land]
    coast = ''.join(f'<path d="{path(p.exterior.coords)}Z" fill="#d7dfd6" stroke="#6c847d" stroke-width=".07"/>' for p in polygons)
    cases = ''.join(f'<path d="{path(densify(s["coordinates_lon_lat"],10000))}" fill="none" stroke="#9dd5dc" stroke-width=".18"/>' for s in doc['scenarios'])
    points = ''.join(f'<circle cx="{project(*p)[0]}" cy="{project(*p)[1]}" r=".28" fill="#102f47"><title>{label}: {p[1]}N,{p[0]}E · nominal source reference</title></circle>' for label, p in zip(['P1','P2','S1'],ANCHORS))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 660" role="img" tabindex="0" aria-labelledby="title desc">
<title id="title">Norwegian Atlantic Slope Current: source-reference connection, P1–P2–S1</title>
<desc id="desc">Regional editorial connection through three source-provided reference coordinates. Nominal WGS84 reference length{doc['nominal_reference_path_km']:.1f}km. Nine bend probes are geometry sensitivity, not physical uncertainty, annual variation, a diagnosed current axis or a500m contour.</desc>
<rect width="1000" height="660" fill="#f2f7f9"/>
<g font-family="system-ui,sans-serif" fill="#123c4b">
<text x="28" y="40" font-size="25" font-weight="700">NwASC · P1–P2–S1 regional reference connection</text>
<text x="28" y="76" font-size="20">~{doc['reported_approximate_reference_path_km']}km · source anchors, editorial connecting legs</text>
<svg x="28" y="108" width="630" height="414" viewBox="{x0} {y0} {x1-x0} {y1-y0}">
<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="#e3f1f5"/>{coast}{cases}
<path d="{path(densify(ANCHORS,10000))}" fill="none" stroke="#156780" stroke-width=".25" stroke-dasharray=".6 .4"/>{points}</svg>
<text x="680" y="148" font-size="18" font-weight="700">Source anchors</text>
<text x="680" y="183" font-size="17">P1 ·62°N,0.5°W</text><text x="680" y="215" font-size="17">P2 ·62°40′N,3°E</text><text x="680" y="247" font-size="17">S1 ·62.8°N,4.25°E</text>
<text x="680" y="301" font-size="17">Dashed: nominal connection</text><text x="680" y="335" font-size="17">Pale: nine ±10km bend probes</text>
<text x="680" y="380" font-size="17">Not a seasonal or error range.</text><text x="680" y="414" font-size="17">No500m contour reconstructed.</text>
<text x="28" y="552" font-size="17">Equirectangular context · Natural Earth1:10M land5.1.1 · no navigation clearance</text>
<text x="28" y="585" font-size="17">Reference length is separate from the broad historical3,500km reported extent.</text>
<text x="28" y="622" font-size="15">Hansen etal(2011),doi:10.1029/2011JC007375,paragraph10. OSW method and bend probes.</text>
</g></svg>'''.encode('utf8')


def verify_inputs():
    doc = build()
    if (ROOT / FILE).read_bytes() != encoded(doc) or (ROOT / FIGURE).read_bytes() != figure(doc):
        raise ValueError('Changed source-anchor reference route/figure')
    return doc, {**doc['input_dependencies_sha256'], FILE: digest(FILE), FIGURE: digest(FIGURE)}


if __name__ == '__main__':
    doc = build()
    (ROOT / FILE).write_bytes(encoded(doc))
    (ROOT / FIGURE).write_bytes(figure(doc))
    print(json.dumps({'nominal_km': doc['nominal_reference_path_km'], 'reference_km': doc['reported_approximate_reference_path_km'],
                      'bend_probe_span_km': doc['scenario_range_km'], 'scenarios': 9}))
