"""Measure declared editorial schematic reaches; no ocean-field or packet access."""
import copy
import hashlib
import itertools
import json
import math
from pathlib import Path

from pyproj import Geod

ROOT = Path(__file__).resolve().parents[1]
INPUT = 'research/atlantic-nsec-schematic-reference-reach-input-v1.json'
OUTPUT = 'research/atlantic-nsec-schematic-reference-reaches-prepared-v1.json'
GEOD = Geod(ellps='WGS84')


def length_km(coords):
    if len(coords) < 2 or any(len(p) != 2 or not all(math.isfinite(v) for v in p)
        or not -180 <= p[0] <= 180 or not -90 <= p[1] <= 90 for p in coords):
        raise ValueError('Finite CRS84 coordinates required')
    return sum(GEOD.inv(*a, *b)[2] for a, b in zip(coords, coords[1:])) / 1000


def truncate(coords, west):
    if coords[0][0] != 0 or any(a[0] <= b[0] for a, b in zip(coords, coords[1:])):
        raise ValueError('Expected strictly westward reach from declared zero-degree gate')
    result = [list(p) for p in coords if p[0] >= west]
    if len(result) < 2 or result[-1][0] != west:
        raise ValueError('Gate must be an explicit supported waypoint')
    return result


def prepare(source):
    if source['current_id'] != 'atlantic-south-equatorial':
        raise ValueError('nSEC is a branch of the Atlantic SEC, not the North Equatorial Current')
    if source['geometry_role'] != 'osw_editorial_reference_route' or source['installed'] is not False:
        raise ValueError('Editorial preparation only')
    if any(source['eligibility'].values()) or any(source[k] is not None for k in
        ['whole_current_length_km', 'annual_length_range_km', 'numerical_length_uncertainty_km']):
        raise ValueError('Unsupported physical measurement or eligibility')
    routes, cases = [], []
    for route in source['routes']:
        support = route['support_waypoints_lon_lat']
        length_km(support)
        nominal = truncate(support, source['gate_convention']['nominal_west_longitude'])
        routes.append(dict(route, coordinates_lon_lat=nominal,
            calculated_reference_length_km=round(length_km(nominal), 3),
            approximate_display_length_km=100 * round(length_km(nominal) / 100)))
        for west, uniform, interior in itertools.product(
            source['gate_convention']['alternative_west_longitudes'],
            source['scenario_rule']['uniform_latitude_shifts_degrees'],
            source['scenario_rule']['interior_latitude_shifts_degrees']):
            coords = truncate(support, west)
            coords = [[lon, lat + uniform + (interior if 0 < i < len(coords)-1 else 0)]
                      for i, (lon, lat) in enumerate(coords)]
            cases.append({'route_id': route['id'], 'west_gate': west,
                'uniform_shift_degrees': uniform, 'interior_shift_degrees': interior,
                'reference_length_km': round(length_km(coords), 3)})
    result = copy.deepcopy(source)
    result.update(schema='osw.atlantic-sec-schematic-reaches-prepared.v1', routes=routes,
        measurement_method='Sum WGS84 shortest geodesic segments between declared OSW waypoints.',
        editorial_sensitivity_cases=cases, editorial_sensitivity_case_count=len(cases),
        sensitivity_interpretation=source['scenario_rule']['interpretation'],
        physical_length_records_added=0, installed_reference_routes_added=0,
        remaining_gates=['Independent branch and waypoint review against original Figure4.',
            'Cloud source-bound geodesic coast-clearance checks before runtime admission.',
            'Exact installed duplicate audit and typed native/WASM query and visual verification.',
            'Whole-current endpoints and other SEC branches remain unresolved.'])
    return result


if __name__ == '__main__':
    raw = (ROOT / INPUT).read_bytes()
    result = prepare(json.loads(raw))
    result['input_sha256'] = hashlib.sha256(raw).hexdigest()
    (ROOT / OUTPUT).write_bytes((json.dumps(result, indent=2, ensure_ascii=False)+'\n').encode())
    print(json.dumps({'status':'PASS_EDITORIAL_REACH_PREPARATION',
        'lengths_km':[r['calculated_reference_length_km'] for r in result['routes']],
        'sensitivity_cases':len(result['editorial_sensitivity_cases']), 'installed':False}))
