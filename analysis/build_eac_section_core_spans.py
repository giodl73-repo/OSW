"""Exploratory EAC section-normal core spans; no physical-width admission."""
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
import argparse
import json
import math
import statistics

from pyproj import Geod
from acquire_eac_100m_source import ROOT, sha
from check_eac_100m_source import load, times, iso

REPORT = 'research/eac-csiro-100m-section-core-spans.json'
PROTOCOL = 'plans/eac-csiro-100m-section-core-span-protocol-v1.md'
OPERATOR = 'analysis/build_eac_section_core_spans.py'
INPUTS = {
    PROTOCOL: '8e808c3790c0f17b75e8d25ff529da9d153657de46e22d056b61c960799eeb7e',
    'research/eac-csiro-v23-100m-source-query-contract.json': 'a6a0c7b07793c89b104d1a1ad7721f0117d69efcaf5eb9ae505d62dff80321b0',
    'research/eac-csiro-v23-100m-source-quality.json': '2448c181c5c8552a9095672c8e7a97262b6311fafe26b24c8e273ca3149b326a',
    'research/source-data/eac-csiro-v23-100m/selected-source.npz': '5b892c7fb32a1d5597961bf8eb6475aeefb522d4e2be7963ab4e6cb5554355f8',
}
FRACTIONS = (0.4, 0.5, 0.6)
SCENARIOS = (('central', 0), ('minus_supplied_component_magnitudes', -1),
             ('plus_supplied_component_magnitudes', 1))


def geometry(longitude, latitude):
    if len(longitude) < 2 or len(longitude) != len(latitude):
        raise ValueError('Section needs paired geographic positions')
    if any(not math.isfinite(v) for v in [*longitude, *latitude]):
        raise ValueError('Nonfinite section geography')
    if any(abs(v) > 90 for v in latitude) or any(abs(v) > 180 for v in longitude):
        raise ValueError('Invalid section geography')
    geod = Geod(ellps='WGS84'); distance = [0.]; bearings = []
    for i in range(len(longitude)-1):
        _, _, length = geod.inv(longitude[i], latitude[i], longitude[i+1], latitude[i+1])
        if not math.isfinite(length) or length <= 0:
            raise ValueError('Repeated or invalid section position')
        distance.append(distance[-1]+length)
    for i in range(len(longitude)):
        a, b = max(0, i-1), min(len(longitude)-1, i+1)
        bearing, _, _ = geod.inv(longitude[a], latitude[a], longitude[b], latitude[b])
        bearings.append(bearing)
    return {'longitude_latitude_points': [list(p) for p in zip(longitude, latitude)],
            'distance_m': distance, 'forward_bearing_deg': bearings,
            'crs': 'WGS84', 'role': 'fixed_source_section_not_current_edges'}


def project(u, v, eu, ev, bearings, bottom):
    if len({len(a) for a in [u, v, eu, ev, bearings, bottom]}) != 1:
        raise ValueError('Inconsistent section field support')
    q, allowance, along, barriers = [], [], [], []
    for x, y, ex, ey, bearing, depth in zip(u, v, eu, ev, bearings, bottom):
        if not math.isfinite(bearing) or not math.isfinite(depth) or depth < 0:
            raise ValueError('Invalid section bearing/bottom')
        if any(z is not None and not math.isfinite(z) for z in [x, y, ex, ey]):
            raise ValueError('Fields must be finite or null')
        if any(z is not None and z < 0 for z in [ex, ey]):
            raise ValueError('Negative supplied uncertainty magnitude')
        barrier = 'source_bottom_at_or_above_level' if depth <= 100 else 'missing_paired_velocity' if x is None or y is None else None
        barriers.append(barrier)
        if barrier:
            q.append(None); allowance.append(None); along.append(None); continue
        angle = math.radians(bearing); c, s = math.cos(angle), math.sin(angle)
        q.append(x*c-y*s); along.append(x*s+y*c)
        allowance.append(None if ex is None or ey is None else abs(c)*ex+abs(s)*ey)
    return q, allowance, along, barriers


def edge(distance, values, barriers, peak, threshold, direction):
    inside = peak
    while 0 <= inside+direction < len(values):
        outside = inside+direction
        if values[outside] is None:
            return {'status': 'unresolved_'+(barriers[outside] or 'missing_supplied_uncertainty'),
                    'last_inside_index': inside, 'blocking_index': outside}
        if values[outside] <= threshold:
            fraction = (threshold-values[inside])/(values[outside]-values[inside])
            indices = sorted([inside, outside])
            return {'status': 'resolved', 'distance_m': distance[inside]+fraction*(distance[outside]-distance[inside]),
                    'inside_index': inside, 'outside_index': outside,
                    'indices_in_distance_order': indices,
                    'distance_bracket_m': [distance[i] for i in indices],
                    'component_bracket_m_s': [values[i] for i in indices],
                    'fraction_inside_to_outside': fraction}
        inside = outside
    return {'status': 'unresolved_section_domain', 'last_inside_index': inside, 'blocking_index': None}


def measure(distance, values, barriers):
    if len(distance) < 2 or len(values) != len(distance) or len(barriers) != len(values):
        raise ValueError('Invalid core-span dimensions')
    if any(not math.isfinite(v) for v in distance) or any(b <= a for a, b in zip(distance, distance[1:])):
        raise ValueError('Section distances must be finite and increasing')
    if any(v is not None and not math.isfinite(v) for v in values):
        raise ValueError('Core component must be finite or null')
    if any(v is not None and barrier is not None for v, barrier in zip(values, barriers)):
        raise ValueError('An excluded cell cannot support a crossing')
    finite = [(v, -i, i) for i, v in enumerate(values) if v is not None]
    peak = max(finite) if finite else None; cases = []
    for fraction in FRACTIONS:
        threshold = None if peak is None else fraction*peak[0]
        case = {'fraction': fraction, 'primary_fraction': fraction == .5, 'threshold_m_s': threshold,
                'shoreward_edge': None, 'offshore_edge': None, 'section_span_km': None,
                'rounded_section_span_km': None, 'sampling_support_interval_km': None}
        if peak is None:
            case['status'] = 'unresolved_no_eligible_component'
        elif peak[0] < .3:
            case['status'] = 'unresolved_peak_below_0_3_m_s'
        else:
            left = edge(distance, values, barriers, peak[2], threshold, -1)
            right = edge(distance, values, barriers, peak[2], threshold, 1)
            case.update(shoreward_edge=left, offshore_edge=right)
            if left['status'] == right['status'] == 'resolved':
                span = (right['distance_m']-left['distance_m'])/1000
                a, b = left['distance_bracket_m'], right['distance_bracket_m']
                case.update(status='resolved_section_component_span', section_span_km=span,
                            rounded_section_span_km=int(Decimal(str(span)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)),
                            sampling_support_interval_km=[(b[0]-a[1])/1000, (b[1]-a[0])/1000])
            else:
                case['status'] = 'unresolved_paired_boundaries'
        cases.append(case)
    return {'peak_index': None if peak is None else peak[2],
            'peak_component_m_s': None if peak is None else peak[0], 'cases': cases}


def summarize(rows):
    results = []
    for name, _ in SCENARIOS:
        for fraction in FRACTIONS:
            cases = [next(c for c in row['scenarios'][name]['cases'] if c['fraction'] == fraction) for row in rows]
            values = [c['section_span_km'] for c in cases if c['section_span_km'] is not None]
            sides = Counter(e['status'] for c in cases for e in [c['shoreward_edge'], c['offshore_edge']] if e and e['status'] != 'resolved')
            results.append({'scenario': name, 'fraction': fraction, 'attempted_dates': len(rows),
                            'resolved_dates': len(values), 'status_counts': dict(sorted(Counter(c['status'] for c in cases).items())),
                            'unresolved_side_counts': dict(sorted(sides.items())),
                            'conditional_min_km': min(values) if values else None,
                            'conditional_median_km': statistics.median(values) if values else None,
                            'conditional_max_km': max(values) if values else None,
                            'conditioned_on_successful_bracketing_not_annual_extrema': True})
    return results


def build():
    for path, pin in INPUTS.items():
        if sha(ROOT/path) != pin:
            raise ValueError('Changed frozen EAC core-span input: '+path)
    _, _, arrays = load(); dates = times(arrays['TIME'])
    geo = geometry(arrays['LONGITUDE'].tolist(), arrays['LATITUDE'].tolist())
    bottom = arrays['BOTTOM_DEPTH'].tolist(); geo['bottom_depth_m'] = bottom
    rows = []
    clean = lambda values: [None if math.isnan(v) else v for v in values.tolist()]
    for index, date in enumerate(dates):
        u, v, eu, ev = [clean(arrays[key][index]) for key in ['UCUR', 'VCUR', 'UCUR_uncertainty', 'VCUR_uncertainty']]
        q, allowance, along, barriers = project(u, v, eu, ev, geo['forward_bearing_deg'], bottom)
        scenarios = {}
        for name, sign in SCENARIOS:
            values = q if sign == 0 else [None if x is None or a is None else x+sign*a for x, a in zip(q, allowance)]
            result = measure(geo['distance_m'], values, barriers); peak = result['peak_index']
            result['peak_source_components'] = None if peak is None else {
                'UCUR': u[peak], 'VCUR': v[peak], 'section_normal_central_m_s': q[peak],
                'section_tangent_m_s': along[peak], 'bearing_deg': geo['forward_bearing_deg'][peak],
                'tangent_to_normal_ratio_not_width_correction': None if q[peak] == 0 else along[peak]/q[peak]}
            scenarios[name] = result
        rows.append({'id': 'eac-section-core:'+str(index), 'source_time_index': index,
                     'source_time_utc': iso(date), 'year': date.year, 'month': date.month,
                     'source_pointer': '/profiles/'+str(index), 'scenarios': scenarios,
                     'section_normal_velocity_m_s': q, 'projected_supplied_magnitudes_m_s': allowance})
    months = []
    for year, month in sorted({(r['year'], r['month']) for r in rows}):
        selected = [r for r in rows if (r['year'], r['month']) == (year, month)]
        months.append({'year': year, 'month': month, 'source_time_indices': [r['source_time_index'] for r in selected],
                       'outcomes': summarize(selected)})
    return {'schema': 'osw.eac-section-core-spans.v1', 'status': 'exploratory_section_component_spans_not_physical_width',
            'entity_id': 'current:east-australian', 'current_id': 'east-australian', 'depth_m': 100,
            'input_sha256': {**INPUTS, OPERATOR: sha(ROOT/OPERATOR)},
            'source_file': 'research/eac-csiro-v23-100m-source-profiles.json',
            'source_sha256': sha(ROOT/'research/eac-csiro-v23-100m-source-profiles.json'),
            'geometry': geo, 'threshold_fractions': list(FRACTIONS), 'minimum_peak_m_s': .3,
            'primary_scenario': 'central', 'primary_fraction': .5,
            'counts': {'source_dates': len(rows), 'scenarios_per_date': 9, 'attempts': len(rows)*9, 'months': len(months)},
            'source_timestamps_independent_observations': False, 'source_bottom_cells_used_as_edges': False,
            'supplied_magnitudes_are_statistical_confidence': False, 'sampling_support_is_measurement_error': False,
            'physical_width_admitted': False, 'whole_current_width_km': None, 'annual_width_range_km': None,
            'geographic_current_edges': None, 'width_rank_eligible': False,
            'overall_outcomes': summarize(rows), 'monthly_summaries': months, 'profiles': rows}


def verify(document=None):
    expected = build(); actual = json.loads((ROOT/REPORT).read_bytes()) if document is None else document
    if actual != expected:
        raise ValueError('EAC core spans differ from frozen source reconstruction')
    return actual


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    result = verify() if args.check else build()
    if not args.check:
        (ROOT/REPORT).write_bytes((json.dumps(result, separators=(',', ':'), allow_nan=False)+'\n').encode())
    print(json.dumps({'counts': result['counts'], 'outcomes': result['overall_outcomes']}))
