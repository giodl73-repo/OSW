"""Small independent route arithmetic/custody audit; no ocean fields or runtime."""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def inverse_km(a, b):
    """Vincenty inverse on WGS84; refuse nonconvergence instead of fallback."""
    major, flattening = 6378137.0, 1 / 298.257223563
    minor = major * (1 - flattening)
    lon1, lat1 = map(math.radians, a)
    lon2, lat2 = map(math.radians, b)
    u1 = math.atan((1 - flattening) * math.tan(lat1))
    u2 = math.atan((1 - flattening) * math.tan(lat2))
    su1, cu1, su2, cu2 = math.sin(u1), math.cos(u1), math.sin(u2), math.cos(u2)
    longitude = lon2 - lon1
    lam = longitude
    for _ in range(100):
        sl, cl = math.sin(lam), math.cos(lam)
        ss = math.hypot(cu2 * sl, cu1 * su2 - su1 * cu2 * cl)
        if ss == 0:
            return 0.0
        cs = su1 * su2 + cu1 * cu2 * cl
        sigma = math.atan2(ss, cs)
        sa = cu1 * cu2 * sl / ss
        csa = 1 - sa * sa
        c2sm = cs - 2 * su1 * su2 / csa if csa else 0.0
        c = flattening / 16 * csa * (4 + flattening * (4 - 3 * csa))
        updated = longitude + (1 - c) * flattening * sa * (
            sigma + c * ss * (c2sm + c * cs * (-1 + 2 * c2sm * c2sm)))
        if abs(updated - lam) < 1e-13:
            break
        lam = updated
    else:
        raise ValueError('Inverse did not converge')
    usq = csa * (major * major - minor * minor) / (minor * minor)
    ca = 1 + usq / 16384 * (4096 + usq * (-768 + usq * (320 - 175 * usq)))
    cb = usq / 1024 * (256 + usq * (-128 + usq * (74 - 47 * usq)))
    ds = cb * ss * (c2sm + cb / 4 * (cs * (-1 + 2 * c2sm * c2sm)
         - cb / 6 * c2sm * (-3 + 4 * ss * ss) * (-3 + 4 * c2sm * c2sm)))
    return minor * ca * (sigma - ds) / 1000


def audit():
    paths = [f'research/wicc-winter-regional-reference-route-v{v}-candidate.json' for v in (1, 2, 3)]
    versions = [json.loads((ROOT / path).read_bytes()) for path in paths]
    result = versions[-1]
    assert result['scenario_count'] == len(result['scenarios']) == 3
    assert [s['longitude_offset_degrees'] for s in result['scenarios']] == [-.3, -.15, 0]
    for version in versions:
        assert version['scenarios'] == result['scenarios'], 'Presentation revision changed geometry'
        assert version['nominal_reference_path_km'] == result['nominal_reference_path_km']
        assert version['rank_eligible_published_estimates'] is False
        assert version['whole_current_length'] is False
        assert version['physical_current_axis'] is False
        assert version['seasonal_playback_eligible'] is False
        assert hashlib.sha256((ROOT / version['input_file']).read_bytes()).hexdigest() == version['input_sha256']
    differences = []
    calculated = []
    for scenario in result['scenarios']:
        vertices = scenario['coordinates_lon_lat']
        assert vertices[0][1] == 10 and vertices[-1][1] == 22
        assert all(a[1] < b[1] for a, b in zip(vertices, vertices[1:]))
        value = sum(inverse_km(a, b) for a, b in zip(vertices, vertices[1:]))
        differences.append(abs(value - scenario['length_km']))
        calculated.append(value)
    assert max(differences) <= .000501, 'Outside three-decimal storage tolerance'
    assert result['reported_approximate_reference_path_km'] == 1500
    assert result['reported_scenario_range_km'] == [1500, 1600]
    assert all(s['start_latitude_offset_degrees'] == s['end_latitude_offset_degrees'] == 0 for s in result['scenarios'])
    assert hashlib.sha256((ROOT / result['generator_file']).read_bytes()).hexdigest() == result['generator_sha256']
    files = paths + [v['input_file'] for v in versions] + [v['figure'] for v in versions]
    files += ['plans/wicc-winter-regional-reference-route-protocol-v1.md', 'analysis/check_wicc_winter_reference_route_v1.py']
    return {'schema': 'osw.wicc-winter-reference-route-arithmetic-review.v1', 'status': 'PASS',
            'method': 'Independent pure-Python Vincenty inverse using WGS84 constants; generator uses PROJ Geod.',
            'storage_tolerance_km': .000501, 'maximum_difference_km': max(differences),
            'independent_scenario_lengths_km': calculated,
            'presentation_revisions_preserve_all_scenarios': True,
            'input_sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in files},
            'scientific_endpoint_or_axis_validation': False,
            'installed_measurements_added': 0, 'coverage_counts_changed': False}


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
