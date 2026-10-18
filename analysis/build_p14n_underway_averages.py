"""Explore component boundaries without bridging native underway runs."""
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import json
import math
from pyproj import Geod
from build_p14n_native_field_audit import verify as verify_native

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = 'research/aleutian-p14n-1993-underway-averages.json'
PROTOCOL = 'plans/aleutian-p14n-underway-averaging-protocol-v1.md'
INPUTS = {
    PROTOCOL: '25ebbc702dbec71e22229e960deda8366e69e147cfbe9cbc9cfd774d116451e7',
    'research/aleutian-p14n-1993-native-vector-support.json': 'b41d6f82bc60475de67c3bfb6e596dad0f72a726034126ae67bbed29cfd82962',
    'analysis/build_p14n_native_field_audit.py': '887ee7629dff09d25211f6544f8ba2558f7c89e5ee3c1c67b986289f72b6b83a',
}
GEOD = Geod(ellps='WGS84')
FIELDS = ['eastward_m_s', 'northward_m_s', 'latitude_degrees_north', 'longitude_degrees_east']


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, allow_nan=False) + '\n').encode()


def stamp(time):
    return time.isoformat().replace('+00:00', 'Z')


def separation(a, b):
    return GEOD.inv(a['longitude_degrees_east'], a['latitude_degrees_north'],
                    b['longitude_degrees_east'], b['latitude_degrees_north'])[2] / 1000


def average_bin(rows, start, seconds, index):
    end = start + timedelta(seconds=seconds)
    clips = []
    for row in rows:
        left = max(start, datetime.fromisoformat(row['ensemble_start_utc']))
        right = min(end, datetime.fromisoformat(row['ensemble_end_utc']))
        if left < right:
            clips.append((left, right, row))
    points = sorted({t for left, right, _ in clips for t in [left, right]})
    integrals = dict.fromkeys(FIELDS, 0.)
    coverage = overlap = 0.
    for left, right in zip(points, points[1:]):
        active = [row for a, b, row in clips if a <= left and b >= right]
        if not active:
            continue
        duration = (right - left).total_seconds()
        coverage += duration
        if len(active) > 1:
            overlap += duration
        for key in FIELDS:
            values = [row['layer_mean'][key] if key.endswith('_m_s') else row[key] for row in active]
            integrals[key] += duration * math.fsum(values) / len(values)
    means = {key: value / coverage if coverage else None for key, value in integrals.items()}
    contributors = [row for _, _, row in clips]
    return {
        'bin_index': index, 'window_start_utc': stamp(start), 'window_end_utc': stamp(end),
        'declared_window_seconds': seconds, 'union_coverage_seconds': coverage,
        'missing_seconds': seconds - coverage, 'multiply_covered_seconds': overlap,
        'coverage_fraction': coverage / seconds, 'boundary_eligible_coverage': coverage >= .8 * seconds,
        'mean': means,
        'contributors': [{'source_time_index': row['source_time_index'],
                          'clipped_start_utc': stamp(left), 'clipped_end_utc': stamp(right)}
                         for left, right, row in clips],
        'contributor_latitude_range': [min(r['latitude_degrees_north'] for r in contributors),
                                       max(r['latitude_degrees_north'] for r in contributors)] if contributors else None,
        'contributor_longitude_range': [min(r['longitude_degrees_east'] for r in contributors),
                                        max(r['longitude_degrees_east'] for r in contributors)] if contributors else None,
        'ensemble_end_position_track_km': sum(separation(a, b) for a, b in zip(contributors, contributors[1:])),
        'mean_position_is_instantaneous_observation': False,
    }


def average_run(rows, minutes):
    start = datetime.fromisoformat(rows[0]['ensemble_start_utc'])
    end = datetime.fromisoformat(rows[-1]['ensemble_end_utc'])
    seconds = minutes * 60
    count = math.ceil((end - start).total_seconds() / seconds)
    return [average_bin(rows, start + timedelta(seconds=i * seconds), seconds, i) for i in range(count)]


def eligibility(row, window):
    if not row['boundary_eligible_coverage']:
        return 'insufficient_coverage'
    low, high = row['contributor_latitude_range']
    if low < window[0] or high > window[1]:
        return 'branch_window_edge'
    return 'eligible'


def walk(bins, peak, step, window, threshold):
    inside = peak
    while True:
        outside = inside + step
        if outside < 0 or outside >= len(bins):
            return {'status': 'run_end', 'crossing': None}
        a, b = bins[inside], bins[outside]
        if b['bin_index'] != a['bin_index'] + step:
            return {'status': 'missing_bin', 'crossing': None}
        state = eligibility(b, window)
        if state != 'eligible':
            return {'status': state, 'crossing': None, 'stopped_at_bin_index': b['bin_index']}
        u = b['mean']['eastward_m_s']
        if u <= threshold:
            fraction = (a['mean']['eastward_m_s'] - threshold) / (a['mean']['eastward_m_s'] - u)
            point = {key: a['mean'][key] + fraction * (b['mean'][key] - a['mean'][key])
                     for key in ['latitude_degrees_north', 'longitude_degrees_east']}
            return {'status': 'resolved', 'inside_bin_index': a['bin_index'],
                    'outside_bin_index': b['bin_index'], 'fraction_from_inside': fraction,
                    'crossing': point, 'weighted_position_bracket_km': separation(a['mean'], b['mean'])}
        inside = outside


def branch(runs, name, window):
    candidates = [(ri, bi) for ri, run in enumerate(runs) for bi, row in enumerate(run['bins'])
                  if eligibility(row, window) == 'eligible']
    result = {'branch': name, 'latitude_window': window,
              'candidate_bins': [{'run_index': ri, 'bin_index': bi} for ri, bi in candidates],
              'selected_peak': None, 'boundary_choice_scenarios': [], 'velocity_sensitivity_scenarios': []}
    if not candidates:
        return dict(result, status='no_eligible_bins')
    ri, bi = max(candidates, key=lambda pair: (runs[pair[0]]['bins'][pair[1]]['mean']['eastward_m_s'], -pair[0], -pair[1]))
    bins = runs[ri]['bins']; peak = bins[bi]['mean']['eastward_m_s']
    result['selected_peak'] = {'run_index': ri, 'bin_index': bi, 'eastward_m_s': peak}
    if peak < .02:
        return dict(result, status='below_peak_floor')
    for fraction, offset in [(.4, 0), (.5, 0), (.6, 0), (.5, -.06), (.5, -.02), (.5, .02), (.5, .06)]:
        threshold = peak * fraction + offset
        scenario = {'fraction_of_peak': fraction, 'threshold_displacement_m_s': offset,
                    'comparison_threshold_m_s': threshold, 'endpoint_separation_km': None,
                    'before_peak': None, 'after_peak': None}
        if not 0 < threshold < peak:
            scenario['status'] = 'ineligible_threshold'
        else:
            before = walk(bins, bi, -1, window, threshold)
            after = walk(bins, bi, 1, window, threshold)
            scenario.update(before_peak=before, after_peak=after, status='unresolved')
            if before['status'] == after['status'] == 'resolved':
                scenario.update(status='resolved', endpoint_separation_km=separation(before['crossing'], after['crossing']))
        result['boundary_choice_scenarios' if offset == 0 else 'velocity_sensitivity_scenarios'].append(scenario)
    return dict(result, status='evaluated')


def build():
    for path, pin in INPUTS.items():
        if digest(path) != pin:
            raise ValueError('Changed underway averaging input: ' + path)
    native = verify_native()
    profiles = {row['source_time_index']: row for row in native['profiles']}
    experiments = []
    for speed in native['run_sensitivity']:
        for minutes in [30, 60, 150]:
            runs = [{'run_index': i, 'native_source_time_indices': run['source_time_indices'],
                     'bins': average_run([profiles[j] for j in run['source_time_indices']], minutes)}
                    for i, run in enumerate(speed['runs'])]
            experiments.append({'ship_speed_cutoff_m_s': speed['ship_speed_cutoff_m_s'],
                                'averaging_minutes': minutes, 'runs': runs,
                                'branches': [branch(runs, 'northern', [44, 46]), branch(runs, 'southern', [41, 43])]})
    return {
        'schema': 'osw.underway-component-averaging.v1', 'current_id': 'aleutian',
        'status': 'exploratory_contiguous_run_component_boundaries',
        'input_sha256': dict(INPUTS), 'protocol_file': PROTOCOL,
        'generator_file': Path(__file__).relative_to(ROOT).as_posix(),
        'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'experiments': experiments, 'osw_temporal_ocean_velocity_averaging_applied': True,
        'current_association_verified': False, 'new_width_record_admitted': False,
        'whole_current_width_km': None, 'annual_width_range_km': None,
        'width_rank_eligible': False, 'physical_edge_geometry_admitted': False,
        'seasonal_playback_supported': False, 'station_gaps_bridged': False,
        'sensitivity_is_confidence_interval': False,
        'cautions': ['Means summarize moving measurement footprints, not instantaneous point velocities.',
                     'Eastward component is not an estimated flow-normal coordinate.',
                     'Paper GPS averaging estimates are context, not calibrated errors of these averages.',
                     'Run endpoints, branch-window edges and incomplete bins never substitute for missing crossings.',
                     'Southern eddy attribution and physical branch edges remain unverified.'],
    }


def verify():
    result = build()
    if (ROOT / OUTPUT).read_bytes() != encoded(result):
        raise ValueError('Stale underway averaging report')
    return result


if __name__ == '__main__':
    result = build(); (ROOT / OUTPUT).write_bytes(encoded(result))
    print(json.dumps([{'speed': e['ship_speed_cutoff_m_s'], 'minutes': e['averaging_minutes'],
                       'bins': sum(len(r['bins']) for r in e['runs']),
                       'eligible_bins': sum(b['boundary_eligible_coverage'] for r in e['runs'] for b in r['bins']),
                       'branches': [{'name': b['branch'], 'peak': b['selected_peak'],
                                     'scenarios': [{'status': s['status'], 'km': s['endpoint_separation_km'],
                                                    'before': s['before_peak']['status'] if s['before_peak'] else None,
                                                    'after': s['after_peak']['status'] if s['after_peak'] else None}
                                                   for s in b['boundary_choice_scenarios']]}
                                    for b in e['branches']]} for e in result['experiments']], indent=2))
