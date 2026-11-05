"""Offline bounded native LADCP sampling; local cutoffs, never physical bottoms."""
import copy
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import signal
import socket
import time
import netCDF4
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OP = 'research/a20-gulf-stream-depth-bracket-operator-v1.json'
HEADER = 'research/a20-gulf-stream-retained-headers-v2.json'
TARGETS = [0, 50, 100, 150, 200, 300, 500, 750, 1000, 1500, 2000, 2500, 3000, 4000, 5000]
CUTOFFS = [.05, .1, .2]


def finite(v):
    return type(v) in (int, float) and math.isfinite(v)


def clean(v):
    if np.ma.is_masked(v): return None
    value = float(v)
    return value if math.isfinite(value) else None


def number_count(value):
    if isinstance(value, dict): return sum(number_count(v) for v in value.values())
    if isinstance(value, list): return sum(number_count(v) for v in value)
    return int(type(value) in (int, float))


def coarse_indices(z):
    if not 2 <= len(z) <= 1000 or any(not finite(v) or v < 0 or v > 10000 for v in z) or any(b <= a for a, b in zip(z, z[1:])):
        raise ValueError('Bounded ascending native metre axis required')
    # Selection uses depth only. First index breaks equal-distance ties.
    indices = {min(range(len(z)), key=lambda i: abs(z[i] - t)) for t in TARGETS if t <= z[-1]}
    indices.add(len(z) - 1)
    if len(indices) > 16: raise ValueError('Reserve at least24of40levels for shared refinement')
    return sorted(indices)


def sample_profile(z, read_point):
    initial = coarse_indices(z)
    cache = {}
    def get(i):
        if i not in cache:
            if len(cache) >= 40: raise ValueError('Whole-profile40level cap reached before native slice')
            point = read_point(i)
            if set(point) != {'u_m_s', 'v_m_s', 'uerr_m_s'} or any(v is not None and not finite(v) for v in point.values()):
                raise ValueError('Finite-or-explicit-missing native components required')
            cache[i] = {'native_index': i, 'depth_m': z[i], **point}
        return cache[i]
    for i in initial: get(i)
    upper = [i for i in initial if z[i] <= 200 and get(i)['u_m_s'] is not None]
    core = max(upper, key=lambda i: get(i)['u_m_s']) if upper else None
    states = []
    for cutoff in CUTOFFS:
        state = {'threshold_m_s': cutoff, 'sampled_upper200m_core_index': core,
                 'coarse_bracket_indices': None, 'refined_bracket_indices': None,
                 'lower_depth_m': None, 'lower_depth_native_bracket_m': None,
                 'status': 'NO_QUALIFYING_SAMPLED_UPPER200M_CORE',
                 'first_native_downcrossing_below_core_verified': False,
                 'continuous_connection_from_core_verified': False,
                 'skipped_native_levels_may_hide_earlier_reversal': True,
                 'physical_current_bottom_established': False,
                 'physical_thickness_m': None, 'annual_range_m': None,
                 'depth_confidence_interval_m': None, 'volume_eligible': False}
        if core is not None and get(core)['u_m_s'] > cutoff:
            state['status'] = 'RIGHT_CENSORED_ON_SAMPLED_COARSE_PATH'
            left = core
            for right in [i for i in initial if i > core]:
                value = get(right)['u_m_s']
                if value is None:
                    state.update(status='CENSORED_AT_MISSING_COARSE_SAMPLE', last_positive_sample_depth_m=z[left])
                    break
                if value <= cutoff:
                    state.update(status='REFINEMENT_PENDING', coarse_bracket_indices=[left, right],
                                 refined_bracket_indices=[left, right])
                    break
                left = right
            else:
                state['last_positive_sample_depth_m'] = z[left]
        states.append(state)
    # Deterministic ascending-cutoff round robin shares the same40level cache.
    while any(s['status'] == 'REFINEMENT_PENDING' for s in states):
        progressed = False
        for state in states:
            if state['status'] != 'REFINEMENT_PENDING': continue
            left, right = state['refined_bracket_indices']
            if right - left == 1:
                a, b = get(left)['u_m_s'], get(right)['u_m_s']
                if not a > state['threshold_m_s'] >= b: raise ValueError('Opposite-sign finite endpoint invariant')
                depth = z[left] + (state['threshold_m_s'] - a) * (z[right] - z[left]) / (b - a)
                state.update(status='ADJACENT_NATIVE_CROSSING_WITHIN_FIRST_COARSE_DESCENDING_BRACKET',
                             lower_depth_m=depth, lower_depth_native_bracket_m=[z[left], z[right]])
                progressed = True
                continue
            mid = (left + right) // 2
            if mid not in cache and len(cache) == 40:
                state['status'] = 'UNRESOLVED_REFINEMENT_LEVEL_BUDGET'
                continue
            value = get(mid)['u_m_s']; progressed = True
            if value is None:
                state.update(status='CENSORED_AT_MISSING_REFINEMENT_SAMPLE', missing_refinement_native_index=mid)
            elif value > state['threshold_m_s']:
                state['refined_bracket_indices'][0] = mid
            else:
                state['refined_bracket_indices'][1] = mid
        if not progressed: break
    for state in states:
        if state['refined_bracket_indices'] is not None:
            state['remaining_endpoint_depth_bracket_m'] = [z[i] for i in state['refined_bracket_indices']]
        state['local_crossing_is_first_crossing_of_entire_native_profile'] = False
        state['linear_interpolation_used_only_between_adjacent_finite_native_endpoints'] = state['lower_depth_m'] is not None
    return {'coarse_native_indices': initial, 'sampled_upper200m_core_index': core,
            'selected_native_indices': sorted(cache), 'selected_native_levels': len(cache),
            'selected_native_samples': [cache[i] for i in sorted(cache)], 'threshold_cases': states,
            'source_upper200m_core_fully_sampled': False, 'entire_native_velocity_profile_read': False,
            'independent_current_axis_verified': False, 'physical_current_bottom_established': False,
            'seasonal_playback_eligible': False, 'reference_route_projection_eligible': False}


def build():
    op = json.loads((ROOT / OP).read_bytes())
    for p, pin in op['input_sha256'].items():
        if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != pin: raise ValueError('Frozen dependency changed: ' + p)
    if op['coarse_target_depths_m'] != TARGETS or op['thresholds_m_s'] != CUTOFFS or op['maximum_levels_per_cast'] != 40:
        raise ValueError('Exact prospective sampler required')
    raw = (ROOT / HEADER).read_bytes()
    if len(raw) > 400000: raise ValueError('Bounded metadata packet required')
    headers = json.loads(raw); typed = number_count(headers)
    if typed > 3000 or headers['aggregate_metadata_touch_bound_including_one_test_and_producer'] != 1989:
        raise ValueError('Carry all prior metadata plus two bounded packet reads')
    if 1989 + 2 * typed > 10000: raise ValueError('Original case metadata cap cannot reset')
    profiles = []; axis_values = 0; selected_values = 0; geocode_values = 0
    for row in headers['headers']:
        station = row['station']; h = row['header']; path = ROOT / row['raw_file']
        if station not in ['014', '015', '016'] or hashlib.sha256(path.read_bytes()).hexdigest() != row['raw_sha256']:
            raise ValueError('Exact three original cast files required')
        if h['global_attributes']['GEN_Software_orig'] != 'LDEO LADCP software: Version IX_14':
            raise ValueError('Same documented LDEO IX14 component semantics required')
        with netCDF4.Dataset(path) as d:
            for name, unit in [('z', 'Meters'), ('u', 'm/s'), ('v', 'm/s'), ('uerr', 'm/s')]:
                if d[name].dimensions != ('z',) or d[name].getncattr('units') != unit or len(d[name]) > 1000:
                    raise ValueError('Qualified metre axis and native component units/shapes required')
            zraw = d['z'][:]; axis_values += int(zraw.size)
            z = [clean(v) for v in zraw]
            lon, lat = clean(d['lon'][...]), clean(d['lat'][...]); geocode_values += 2
            if lon is None or lat is None or not -180 <= lon <= 180 or not -90 <= lat <= 90:
                raise ValueError('Valid native scalar geocodes required')
            def read_point(i):
                nonlocal selected_values
                selected_values += 3
                return {name + '_m_s': clean(d[name][i]) for name in ['u', 'v', 'uerr']}
            sample = sample_profile(z, read_point)
        profiles.append({'station': station, 'entity_context': 'current:gulf-stream',
                         'current_membership_basis': 'primary_cruise_QC_report_stations14_to21_not_independent_axis_validation',
                         'source_file': row['raw_file'], 'source_sha256': row['raw_sha256'],
                         'cast_datetime_utc': h['global_attributes']['datetime'], 'source_lon_lat': [lon, lat],
                         'native_depth_axis_count': len(z), 'native_depth_axis_domain_m': [z[0], z[-1]],
                         'diagnostic_component': 'source_u_eastward_LDEO_IX14_not_speed_magnitude_or_current_axis_projection',
                         'source_uerr_role': 'provider_uncertainty_estimate_not_standard_error_or_depth_CI', **sample})
    if [r['station'] for r in profiles] != ['014', '015', '016']: raise ValueError('Three prospectively selected casts exactly once')
    native_one_pass = axis_values + selected_values + geocode_values
    all_case_bound = 1989 + 2 * typed + 2 * native_one_pass
    if all_case_bound > 250000 or sum(r['selected_native_levels'] for r in profiles) > 120:
        raise ValueError('Original cumulative scalar/level budget required')
    return {'schema': 'osw.a20-gulf-stream-native-depth-brackets.v1',
            'status': 'BOUNDED_NATIVE_EASTWARD_COMPONENT_LOCAL_CROSSINGS_NOT_PHYSICAL_CURRENT_BOTTOMS',
            'operator_file': OP, 'input_sha256': op['input_sha256'], 'profiles': profiles,
            'counts': {'source_cast_profiles': 3, 'threshold_contexts': 9,
                       'selected_native_levels': sum(r['selected_native_levels'] for r in profiles),
                       'adjacent_local_crossings': sum(c['lower_depth_m'] is not None for r in profiles for c in r['threshold_cases']),
                       'native_axis_values_one_pass': axis_values, 'selected_native_field_values_one_pass': selected_values,
                       'native_geocode_values_one_pass': geocode_values, 'typed_metadata_numbers_per_pass': typed,
                       'prior_metadata_touch_bound': 1989, 'metadata_bound_including_two_packet_reads': 1989 + 2 * typed,
                       'case_scalar_bound_including_one_actual_test_and_producer': all_case_bound,
                       'provider_requests': 0, 'new_canonical_depth_references': 0},
            'original_case_operations_used': 3, 'original_case_operations_remaining': 0,
            'original_case_response_bytes': 425028, 'native_scalar_case_cap_unchanged': 250000,
            'native_byte_case_cap_unchanged': 7000000,
            'metric_is_comparable_to_locked100m_direction_glider_fit_depth': False,
            'skipped_native_levels_may_hide_earlier_crossings': True,
            'whole_route_physical_depth_profile_established': False, 'physical_thickness_m': None,
            'annual_depth_range_m': None, 'volume_m3': None, 'runtime_changed': False, 'full_goal_complete': False}


def csv_bytes(report):
    fields = ['station', 'cast_datetime_utc', 'threshold_m_s', 'status', 'lower_depth_m',
              'lower_depth_native_bracket_m', 'coarse_bracket_indices', 'refined_bracket_indices',
              'first_native_downcrossing_below_core_verified', 'physical_current_bottom_established']
    out = io.StringIO(newline=''); writer = csv.DictWriter(out, fieldnames=fields, lineterminator='\n'); writer.writeheader()
    for profile in report['profiles']:
        for case in profile['threshold_cases']:
            row = {k: case.get(k) for k in fields}; row.update(station=profile['station'], cast_datetime_utc=profile['cast_datetime_utc'])
            for k in ['lower_depth_native_bracket_m', 'coarse_bracket_indices', 'refined_bracket_indices']:
                row[k] = json.dumps(row[k], separators=(',', ':')) if row[k] is not None else ''
            writer.writerow(row)
    return out.getvalue().encode()


def main():
    def stopped(*a): raise SystemExit('Stopped retained native producer; no source replay')
    for sig in [signal.SIGALRM, signal.SIGTERM, signal.SIGINT]: signal.signal(sig, stopped)
    socket.socket = lambda *a, **k: (_ for _ in ()).throw(RuntimeError('Retained source files only'))
    signal.alarm(60)
    start = float(os.environ['OSW_A20_DEPTH_PHASE_START'])
    if not 0 <= time.monotonic() - start < 90: raise ValueError('Shared actual-test/producer clock required')
    folder = ROOT / 'a20-gulf-stream-native-depth-brackets-v1'; folder.mkdir(exist_ok=False)
    report = build(); report['new_native_phase_seconds'] = time.monotonic() - start
    report['cumulative_case_time_charge_seconds'] = 3.518115545999997 + report['new_native_phase_seconds']
    if report['cumulative_case_time_charge_seconds'] > 180: raise ValueError('Original case time cap unchanged')
    raw = (json.dumps(report, indent=2, allow_nan=False) + '\n').encode(); table = csv_bytes(report)
    if len(raw) + len(table) > 2400000: raise ValueError('Fixed output chunk cap unchanged')
    (folder / 'depths.json').write_bytes(raw); (folder / 'depths.csv').write_bytes(table)
    print(json.dumps(report['counts']))
    for p in report['profiles']:
        print(json.dumps({'station': p['station'], 'selected_levels': p['selected_native_levels'],
                          'thresholds': [{k: c[k] for k in ['threshold_m_s', 'status', 'lower_depth_m', 'lower_depth_native_bracket_m']} for c in p['threshold_cases']]}))


if __name__ == '__main__': main()
