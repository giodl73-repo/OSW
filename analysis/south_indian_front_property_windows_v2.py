"""Conditional native property supports and all surface-peak comparisons."""
import argparse
import calendar
import datetime
import json
import math
from pathlib import Path

import numpy as np

from acquire_indian_secc_hycom_2013 import pin
from south_indian_paired_profiles_v2 import positive_maxima
from wgs84_decimal_meridian import meridian_km

ROOT = Path(__file__).resolve().parents[1]
OPERATOR = 'analysis/south_indian_front_property_windows_v2.py'
PROTOCOL = 'plans/south-indian-front-property-windows-protocol-v2.md'
PREFLIGHT = 'research/south-indian-front-property-windows-preflight-v2.json'
REPORT = 'research/south-indian-2013-front-property-windows-v2.json'
OLD = 'research/source-data/hycom-south-indian-hydrography-2013/'
NEW = 'research/source-data/hycom-south-indian-front-levels-2013/'
DERIVED = 'research/south-indian-2013-front-level-potential-temperature.json'
THETA = 'potential_temperature_0_dbar_assuming_ITS90_c'
CRITERIA = [
    {'id': 'stf_theta100', 'depth_m': 100, 'quantities': {'theta0_c': [10, 12]}},
    {'id': 'stf_sp100', 'depth_m': 100, 'quantities': {'practical_salinity': [34.6, 35.0]}},
    {'id': 'stf_joint100', 'depth_m': 100,
     'quantities': {'theta0_c': [10, 12], 'practical_salinity': [34.6, 35.0]}},
    {'id': 'arf_theta200', 'depth_m': 200, 'quantities': {'theta0_c': [12, 16]}},
]


def masks(theta100, sp100, theta200, eligible100, eligible200):
    arrays = [np.asarray(a, dtype=float) for a in [theta100, sp100, theta200]]
    eligibility = [np.asarray(a) for a in [eligible100, eligible200]]
    if (any(a.ndim != 1 or a.shape != arrays[0].shape for a in [*arrays, *eligibility])
            or any(a.dtype != np.bool_ for a in eligibility)
            or any(np.isinf(a).any() for a in arrays)):
        raise ValueError('Malformed property profile or eligibility')
    t, s, a = arrays
    valid = [eligibility[0] & np.isfinite(t), eligibility[0] & np.isfinite(s),
             eligibility[0] & np.isfinite(t) & np.isfinite(s), eligibility[1] & np.isfinite(a)]
    predicates = [(t >= 10) & (t <= 12), (s >= 34.6) & (s <= 35),
                  (t >= 10) & (t <= 12) & (s >= 34.6) & (s <= 35),
                  (a >= 12) & (a <= 16)]
    return {c['id']: [bool(p) if v else None for p, v in zip(pred, supported)]
            for c, pred, supported in zip(CRITERIA, predicates, valid)}


def supports(mask, latitudes, prefix):
    lat = np.asarray(latitudes, dtype=float)
    if (lat.ndim != 1 or len(mask) != len(lat) or not np.isfinite(lat).all()
            or not np.all(np.diff(lat) > 0) or np.any(np.abs(lat) > 90)
            or any(v is not None and type(v) is not bool for v in mask)):
        raise ValueError('Invalid native membership or latitude support')
    def flank(index):
        if not 0 <= index < len(mask):
            return {'status': 'domain_end', 'native_index': None}
        return {'status': 'unsupported_property' if mask[index] is None else 'outside_window',
                'native_index': index, 'latitude_degrees_north': float(lat[index])}
    runs = []
    i = 0
    while i < len(mask):
        if mask[i] is not True:
            i += 1
            continue
        end = i
        while end + 1 < len(mask) and mask[end + 1] is True:
            end += 1
        runs.append({'id': f'{prefix}:run{len(runs)}', 'start_index': i, 'end_index': end,
                     'native_indices': list(range(i, end + 1)),
                     'latitude_support_degrees_north': [float(lat[i]), float(lat[end])],
                     'south_flank': flank(i - 1), 'north_flank': flank(end + 1),
                     'physical_edges': None, 'physical_width_km': None})
        i = end + 1
    return runs


def comparisons(peaks, runs, latitude, velocity_counts, property_counts, days):
    """No preferred pair; equal incomplete counts do not establish a cohort."""
    if (type(days) is not int or days < 1 or len(velocity_counts) != len(latitude)
            or len(property_counts) != len(latitude)
            or any(not isinstance(c, (int, np.integer)) or isinstance(c, (bool, np.bool_)) or not 0 <= c <= days
                   for counts in [velocity_counts, property_counts] for c in counts)):
        raise ValueError('Invalid daily support counts')
    rows = []
    for peak in peaks:
        pi = list(range(peak['start_index'], peak['end_index'] + 1))
        p = [float(latitude[pi[0]]), float(latitude[pi[-1]])]
        for run in runs:
            ri = run['native_indices']; r = run['latitude_support_degrees_north']
            comparable = all(velocity_counts[i] == days for i in pi) and all(property_counts[i] == days for i in ri)
            overlap = max(p[0], r[0]) <= min(p[1], r[1])
            distance = None
            if comparable:
                distance = 0.0 if overlap else meridian_km(p[1], r[0]) if p[1] < r[0] else meridian_km(r[1], p[0])
            rows.append({'peak_id': peak['id'], 'property_run_id': run['id'],
                         'identical_complete_daily_support': comparable,
                         'comparison_status': 'comparable' if comparable else 'incomplete_daily_support_not_proven_identical',
                         'native_supports_overlap': overlap if comparable else None,
                         'support_separation_km': distance,
                         'front_identification_verified': False, 'current_association_verified': False})
    return rows



def evaluate_windows(membership, lat, peaks, velocity_counts, property_counts, days, case_id):
    """Build every declared criterion in the exact function used by all cases."""
    windows = []
    for criterion in CRITERIA:
        key = criterion['id']; zi = 0 if criterion['depth_m'] == 100 else 1
        runs = supports(membership[key], lat, f'{case_id}:{key}')
        windows.append({'criterion_id': key, 'membership': membership[key], 'runs': runs,
                        'qualifying_nodes': sum(v is True for v in membership[key]),
                        'unsupported_nodes': sum(v is None for v in membership[key]),
                        'status': 'qualifying_native_nodes_present' if runs else
                            'all_properties_unsupported' if all(v is None for v in membership[key]) else 'no_qualifying_native_nodes',
                        'peak_comparisons': comparisons(peaks, runs, lat,
                            velocity_counts, property_counts[zi], days)})
    if [w['criterion_id'] for w in windows] != ['stf_theta100', 'stf_sp100', 'stf_joint100', 'arf_theta200']:
        raise ValueError('Incomplete or reordered property-window case')
    return windows


def selected_times(selection, month):
    times = [i for r in selection['requests'] if r['month'] == month for i in r['time_indices']]
    if times != sorted(set(times)):
        raise ValueError('Duplicate or reordered daily support')
    return times


def declare():
    if (ROOT/PREFLIGHT).exists() or (ROOT/REPORT).exists():
        raise ValueError('Declaration/output already exists; do not overwrite a frozen method')
    upstream = json.loads((ROOT/DERIVED).read_bytes())
    for p, expected in upstream['dependencies'].items():
        if pin(ROOT/p)['sha256'] != expected:
            raise ValueError('Cannot declare over changed upstream input: '+p)
    paths = set(upstream['dependencies']) | {
        DERIVED, OPERATOR, PROTOCOL, 'requirements-test.txt',
        'analysis/wgs84_decimal_meridian.py', 'analysis/south_indian_paired_profiles_v2.py',
        'research/sparrow-1996-south-indian-front-definition-review.json',
        'analysis/south_indian_front_property_windows.py',
        'plans/south-indian-front-property-windows-protocol-v1.md',
        'research/south-indian-front-property-windows-preflight-v1.json',
        'research/south-indian-front-property-windows-v1-scope-audit.json',
        *[folder+name for folder in [OLD, NEW] for name in ['acquisition.json', 'selection.json', 'monthly.npz']],
    }
    document = {'schema': 'osw.south-indian-property-window-preflight.v2',
                'declared_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'source_values_already_observed': True,
                'stage': 'Exploratory method fixed before property-mask/comparison calculation; not blinded',
                'criteria': CRITERIA, 'numeric_runtime': {'numpy': '2.4.1', 'distance': 'WGS84 Decimal70'},
                'dependencies': {p: pin(ROOT/p) for p in sorted(paths)},
                'cases_required': 36, 'physical_width_admitted': False,
                'front_identification_verified': False, 'current_association_verified': False}
    (ROOT/PREFLIGHT).write_bytes((json.dumps(document, indent=2, allow_nan=False)+'\n').encode())
    return document


def build():
    declared = json.loads((ROOT/PREFLIGHT).read_bytes())
    if (declared['schema'] != 'osw.south-indian-property-window-preflight.v2'
            or declared['source_values_already_observed'] is not True
            or any(declared.get(k) is not False for k in ['physical_width_admitted',
                'front_identification_verified', 'current_association_verified'])
            or declared['criteria'] != CRITERIA or declared['cases_required'] != 36
            or declared['numeric_runtime'] != {'numpy': np.__version__, 'distance': 'WGS84 Decimal70'}):
        raise ValueError('Changed declared criteria, case count or runtime')
    for p, expected in declared['dependencies'].items():
        if pin(ROOT/p) != expected:
            raise ValueError('Changed frozen property-window input: '+p)
    derived = json.loads((ROOT/DERIVED).read_bytes())
    for p, expected in derived['dependencies'].items():
        if p not in declared['dependencies'] or pin(ROOT/p)['sha256'] != expected:
            raise ValueError('Missing or changed upstream input: '+p)
    required = {DERIVED, OPERATOR, PROTOCOL, 'requirements-test.txt',
                'analysis/wgs84_decimal_meridian.py', 'analysis/south_indian_paired_profiles_v2.py',
                'research/sparrow-1996-south-indian-front-definition-review.json',
        'analysis/south_indian_front_property_windows.py',
        'plans/south-indian-front-property-windows-protocol-v1.md',
        'research/south-indian-front-property-windows-preflight-v1.json',
        'research/south-indian-front-property-windows-v1-scope-audit.json',
                *[folder+name for folder in [OLD, NEW] for name in ['acquisition.json', 'selection.json', 'monthly.npz']]}
    if set(declared['dependencies']) != set(derived['dependencies']) | required:
        raise ValueError('Incomplete or changed declared dependency graph')
    if (derived['depth_m'] != [100, 200] or derived['temperature_scale_verified'] is not False
            or derived['temperature_scale_assumption'] != 'ITS-90'
            or derived['current_association_verified'] is not False):
        raise ValueError('Changed source identity or thermodynamic assumptions')
    selections = [json.loads((ROOT/(f+'selection.json')).read_bytes()) for f in [OLD, NEW]]
    if any(sum(len(selected_times(s, m)) for m in range(1, 13)) != 363 for s in selections):
        raise ValueError('Changed frozen annual daily cohort')
    with np.load(ROOT/(OLD+'monthly.npz'), allow_pickle=False) as old, np.load(ROOT/(NEW+'monthly.npz'), allow_pickle=False) as new:
        for a, expected_depth in [(old, [15, 1000]), (new, [100, 200])]:
            np.testing.assert_array_equal(a['depth'], expected_depth)
            np.testing.assert_array_equal(a['month'], range(1, 13))
            if any(a[k].shape != (12, 2, 326, 3) for k in ['water_u', 'water_v', 'water_temp', 'salinity', 'common_samples']):
                raise ValueError('Changed native source shape')
        lat = old['lat'].copy(); lon = old['lon'].copy()
        np.testing.assert_array_equal(lat, new['lat']); np.testing.assert_array_equal(lon, new['lon'])
        np.testing.assert_array_equal(lat, derived['latitude_degrees_north'])
        np.testing.assert_array_equal(lon, derived['longitude_degrees_east'])
        if len(derived['months']) != 12 or [r['month'] for r in derived['months']] != list(range(1, 13)):
            raise ValueError('Missing, duplicated or reordered derived months')
        cases = []
        for mi, month in enumerate(derived['months']):
            times = [selected_times(s, mi+1) for s in selections]
            if times[0] != times[1] or len(times[0]) != month['sample_days']:
                raise ValueError('Different monthly daily time cohorts')
            days = len(times[0]); minimum = math.ceil(.8*calendar.monthrange(2013, mi+1)[1])
            if minimum != month['minimum_common_samples']:
                raise ValueError('Changed common-calendar quota')
            counts = np.asarray(month['common_samples'])
            np.testing.assert_array_equal(counts, new['common_samples'][mi])
            theta = np.asarray(month['fields'][THETA], dtype=float)
            if theta.shape != (2, 326, 3):
                raise ValueError('Changed derived temperature shape')
            for xi, x in enumerate(lon):
                case_id = f'front-properties:m{mi+1:02d}:x{xi}'
                membership = masks(theta[0, :, xi], new['salinity'][mi, 0, :, xi], theta[1, :, xi],
                                   counts[0, :, xi] >= minimum, counts[1, :, xi] >= minimum)
                peaks = positive_maxima(old['water_u'][mi, 0, :, xi])
                for i, peak in enumerate(peaks):
                    peak.update(id=f'{case_id}:surface-peak{i}',
                                latitude_support_degrees_north=[float(lat[peak['start_index']]), float(lat[peak['end_index']])])
                windows = evaluate_windows(membership, lat, peaks,
                    old['common_samples'][mi, 0, :, xi], counts[:, :, xi], days, case_id)
                cases.append({'id': case_id, 'month': mi+1, 'longitude_degrees_east': float(x),
                              'sample_days': days, 'minimum_common_samples': minimum,
                              'surface_eastward_velocity_m_s': [float(v) if np.isfinite(v) else None for v in old['water_u'][mi, 0, :, xi]],
                              'surface_peaks': peaks, 'property_windows': windows})
    if len(cases) != 36 or any([w['criterion_id'] for w in c['property_windows']] !=
            ['stf_theta100', 'stf_sp100', 'stf_joint100', 'arf_theta200'] for c in cases):
        raise ValueError('Incomplete actual case/criterion matrix')
    return {'schema': 'osw.south-indian-front-property-windows.v2',
            'supersedes': {'operator': 'analysis/south_indian_front_property_windows.py',
                           'scope_audit': 'research/south-indian-front-property-windows-v1-scope-audit.json'},
            'status': 'exploratory_conditional_native_property_supports_not_identified_fronts_or_current_widths',
            'investigation_current_id': 'south-indian', 'model_year': 2013,
            'dependencies': {PREFLIGHT: pin(ROOT/PREFLIGHT), **declared['dependencies']},
            'criteria': CRITERIA, 'numeric_runtime': declared['numeric_runtime'],
            'latitude_degrees_north': lat.tolist(), 'longitude_degrees_east': lon.tolist(),
            'temperature_scale_verified': False, 'temperature_scale_assumption': 'ITS-90',
            'classification_of_monthly_means_not_daily_frequency': True,
            'property_supports_are_physical_edges': False, 'cases': cases,
            'front_identification_verified': False, 'current_association_verified': False,
            'physical_width_admitted': False, 'physical_axis_admitted': False,
            'physical_length_admitted': False, 'annual_extrema_admitted': False,
            'seasonal_footprint_admitted': False, 'saf_identification_attempted': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['declare', 'build', 'check'])
    args = parser.parse_args()
    if args.command == 'declare':
        print('Declared', len(declare()['dependencies']), 'frozen inputs; no source calculation run')
        return
    report = build(); raw = (json.dumps(report, indent=2, allow_nan=False)+'\n').encode()
    path = ROOT/REPORT
    if args.command == 'check':
        if path.read_bytes() != raw:
            raise ValueError('Property-window report differs byte for byte')
        print('PASS complete property-window report byte exact')
    else:
        if path.exists() and path.read_bytes() != raw:
            raise ValueError('Refusing to overwrite a different published report')
        path.write_bytes(raw)
        print('Built', len(report['cases']), 'complete cases; no physical width admitted')


if __name__ == '__main__':
    main()
