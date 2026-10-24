"""Dated fixed-array v-component spans, explicitly not physical current widths."""
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import argparse
import hashlib
import json
import math
import statistics

ROOT = Path(__file__).resolve().parents[1]
REPORT = 'research/agulhas-asca-100m-dated-component-spans.json'
PROTOCOL = 'plans/agulhas-asca-100m-component-span-protocol-v1.md'
RAW = 'research/agulhas-asca-100m-observed-profiles.json'
MONTHLY = 'research/agulhas-asca-100m-monthly-sections.json'
CONTRACT = 'research/agulhas-asca-100m-query-contract.json'
OPERATOR = 'analysis/build_asca_component_spans.py'
READBACK = 'plans/asca-alignment-indicator-readback-v1.md'
INPUTS = {
    PROTOCOL: '5c4424987396103237e88f8f5fd495e75d2e1dfc734b60d345ab0abf531c7d6f',
    RAW: 'c0b9423b9f1335a6455c87d8dda0a54794ac474118fa0a3f000048ffad69fd89',
    MONTHLY: 'fd64659cb63e5f560b3da9cdc830c69d4327b83ea55df7e016a12d2e6a8d8a4a',
    CONTRACT: '21682cf3d38d244f735ca43396d495e0dad64783bed4f45bcb5c5a16eca0e2cf',
    READBACK: '73cec459bcf139c8247e0c42a88036001046a2120031f4821149818f8a2d9d4f',
}
FRACTIONS = (0.4, 0.5, 0.6)


def digest(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def rounded(value):
    return int(Decimal(str(value)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def validate_section(distance_m, v, u):
    if len(distance_m) < 2 or len(v) != len(distance_m) or len(u) != len(v):
        raise ValueError('Inconsistent ASCA component section dimensions')
    if any(not isinstance(x, (float, int)) or not math.isfinite(x) for x in distance_m):
        raise ValueError('Nonfinite ASCA distance')
    if any(b <= a for a, b in zip(distance_m, distance_m[1:])):
        raise ValueError('ASCA distance must increase without reordering')
    if any(x is not None and (not isinstance(x, (float, int)) or not math.isfinite(x)) for x in [*v, *u]):
        raise ValueError('Velocity must be finite or null')


def edge(distance_m, q, peak_index, threshold, direction):
    inside = peak_index
    while 0 <= inside + direction < len(q):
        outside = inside + direction
        if q[outside] is None:
            return {'status': 'unresolved_missing_barrier', 'last_inside_index': inside, 'blocking_index': outside}
        if q[outside] <= threshold:
            fraction = (threshold-q[inside])/(q[outside]-q[inside])
            position = distance_m[inside] + fraction*(distance_m[outside]-distance_m[inside])
            indices = sorted([inside, outside])
            return {'status': 'resolved', 'distance_m': position,
                    'inside_index': inside, 'outside_index': outside,
                    'indices_in_distance_order': indices,
                    'distance_bracket_m': [distance_m[i] for i in indices],
                    'southwestward_component_bracket_m_s': [q[i] for i in indices],
                    'fraction_inside_to_outside': fraction}
        inside = outside
    return {'status': 'unresolved_domain_truncation', 'last_inside_index': inside, 'blocking_index': None}


def measure(distance_m, v, u):
    validate_section(distance_m, v, u)
    q = [None if x is None else -x for x in v]
    finite = [(value, -i, i) for i, value in enumerate(q) if value is not None]
    peak = max(finite) if finite else None
    common = {'peak_index': None, 'peak_distance_m': None, 'peak_v_m_s': None,
              'peak_U_m_s': None, 'peak_alignment_indicator_deg': None}
    if peak:
        maximum, _, index = peak
        common.update(peak_index=index, peak_distance_m=distance_m[index], peak_v_m_s=v[index], peak_U_m_s=u[index])
        if u[index] is not None and maximum > 0:
            common['peak_alignment_indicator_deg'] = math.degrees(math.atan2(abs(u[index]), maximum))
    cases = []
    for fraction in FRACTIONS:
        threshold = None if peak is None else fraction*maximum
        case = {'fraction': fraction, 'primary': fraction == 0.5,
                'threshold_m_s': threshold, 'smaller_distance_edge': None,
                'larger_distance_edge': None, 'span_km': None,
                'rounded_span_km': None, 'grid_bracket_separation_interval_km': None}
        if peak is None:
            case['status'] = 'unresolved_no_finite_v'
        elif maximum < 0.3:
            case['status'] = 'unresolved_peak_below_0_3_m_s'
        else:
            left = edge(distance_m, q, index, threshold, -1)
            right = edge(distance_m, q, index, threshold, 1)
            case.update(smaller_distance_edge=left, larger_distance_edge=right)
            if left['status'] == right['status'] == 'resolved':
                span = (right['distance_m']-left['distance_m'])/1000
                a, b = left['distance_bracket_m'], right['distance_bracket_m']
                case.update(status='resolved_component_span', span_km=span, rounded_span_km=rounded(span),
                            grid_bracket_separation_interval_km=[(b[0]-a[1])/1000, (b[1]-a[0])/1000])
            else:
                case['status'] = 'unresolved_paired_boundaries'
        cases.append(case)
    return {**common, 'cases': cases}


def summarize(rows):
    outcomes = []
    for fraction in FRACTIONS:
        cases = [next(c for c in row['cases'] if c['fraction'] == fraction) for row in rows]
        values = [c['span_km'] for c in cases if c['span_km'] is not None]
        reasons = Counter()
        for case in cases:
            if case['span_km'] is not None:
                continue
            if case['status'] == 'unresolved_paired_boundaries':
                # A profile with two failed sides contributes twice to side reasons,
                # but only once to the profile status count below.
                reasons.update(e['status'] for e in [case['smaller_distance_edge'], case['larger_distance_edge']] if e['status'] != 'resolved')
        outcomes.append({'fraction': fraction, 'attempted_profiles': len(rows), 'resolved_profiles': len(values),
                         'profile_status_counts': dict(sorted(Counter(c['status'] for c in cases).items())),
                         'unresolved_side_reason_counts': dict(sorted(reasons.items())),
                         'resolved_span_min_km': min(values) if values else None,
                         'resolved_span_median_km': statistics.median(values) if values else None,
                         'resolved_span_max_km': max(values) if values else None,
                         'summary_conditioned_on_resolved_cases': True})
    return outcomes


def build(verify_original=True):
    for path, pin in INPUTS.items():
        if digest(path) != pin:
            raise ValueError('Changed frozen ASCA component input: '+path)
    if verify_original:
        from build_asca_100m_sections import checked_packets
        raw, monthly, _ = checked_packets()
    else:
        raw, monthly = [json.loads((ROOT/path).read_bytes()) for path in [RAW, MONTHLY]]
    rows = []
    for profile in raw['profiles']:
        row = {key: profile[key] for key in ['source_time_index', 'observed_at', 'source_epoch_seconds', 'year', 'month']}
        row.update(id='asca-component-span:'+str(profile['source_time_index']), source_profile_id=profile['id'],
                   source_pointer='/profiles/'+str(profile['source_time_index']),
                   **measure(raw['coordinates']['distance_m'], profile['fields']['v'], profile['fields']['U']))
        rows.append(row)
    summaries = []
    for frame in monthly['frames']:
        selected = [rows[i] for i in frame['source_time_indices']]
        summaries.append({key: frame[key] for key in ['year', 'month', 'complete_calendar_time_support', 'source_time_indices', 'first_observed_at', 'last_observed_at']})
        summaries[-1]['outcomes'] = summarize(selected)
    document = {'schema': 'osw.asca-dated-component-spans.v1',
            'status': 'exploratory_fixed_array_component_spans_not_physical_current_width',
            'current_id': 'agulhas', 'entity_id': 'current:agulhas', 'depth_m': 100,
            'source_url': 'https://zenodo.org/records/20515068', 'source_doi': '10.5281/zenodo.20515068',
            'source_citation': 'Beal Lab / University of Miami, Agulhas System Climate Array product2.0; Beal, McMonigal, Gunn and Novelli; McMonigal et al.(2020), doi:10.1175/JPO-D-20-0018.1; Gunn et al.(2020), doi:10.1175/JPO-D-20-0093.1; associated2022corrigenda.',
            'source_license': 'CC BY4.0, provider record',
            'input_sha256': {**INPUTS, OPERATOR: digest(OPERATOR)},
            'operator': {'component': '-v', 'distance_coordinate': 'source array distance in metres',
                         'peak_selection': 'global finite maximum; first source index on ties',
                         'minimum_peak_m_s': 0.3, 'fractions': list(FRACTIONS), 'primary_fraction': 0.5,
                         'boundary_interpolation': 'linear within intact adjacent source cells only',
                         'missing_value_filling': False, 'axis_rotation_applied': False,
                         'display_rounding_km': 1, 'display_rounding_establishes_resolution': False},
            'counts': {'profiles': len(rows), 'threshold_cases': len(rows)*3, 'calendar_bins': len(summaries)},
            'source_method': {'nominal_time_step_hours': 20, 'low_pass_filter_hours': 40,
                              'time_samples_independent': False, 'source_timestamps_modified': False,
                              'output_grid_spacing_m': 500, 'output_spacing_is_independent_resolution': False,
                              'complete_file_checksum_verified': False, 'full_2022_corrigenda_reviewed': False},
            'interpretation': [
                'Fixed-array, peak-connected southwestward v-component spans at100m; not total-speed or flow-normal widths.',
                'Missing values block edges. One-sided results are retained, never doubled; domain limits are not physical edges.',
                'Threshold fractions are alternative assumptions, not uncertainty or extra observations.',
                'Grid-bracket separation interval describes interpolation support, not measurement error or confidence.',
                'Monthly summaries condition on resolved cases; failures may bias their sampled min/median/max.',
                'Product2.0 is provider corrected; no independent rotation repair. Full2022corrigenda remain unreviewed.',
                'Source field is mapped and filtered; neither500m cells nor20hour samples are independent instrument observations.',
                'No whole-current width, geographic boundaries, annual physical range, climatology or seasonal map playback.'],
            'whole_current_width_km': None, 'annual_width_range_km': None,
            'geographic_edges': None, 'width_measurement_admitted': False,
            'width_rank_eligible': False, 'seasonal_playback_eligible': False,
            'overall_outcomes': summarize(rows), 'profiles': rows, 'monthly_summaries': summaries}
    # Preserve source values and all full-precision measurement decisions.
    # Only this computed, non-decision angle has a declared readback quantum.
    for profile in document['profiles']:
        angle = profile['peak_alignment_indicator_deg']
        if angle is not None:
            profile['peak_alignment_indicator_deg'] = round(angle, 6)
    document['calculation_readback_protocol'] = READBACK
    document['alignment_indicator_readback_decimal_places'] = 6
    return document


def encoded(document):
    return (json.dumps(document, separators=(',', ':'), allow_nan=False)+'\n').encode('utf8')


def verify(document=None):
    expected = build()
    actual = json.loads((ROOT/REPORT).read_bytes()) if document is None else document
    if actual != expected:
        raise ValueError('ASCA component spans differ from frozen source reconstruction')
    return actual


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    if args.check:
        document = verify()
    else:
        document = build()
        (ROOT/REPORT).write_bytes(encoded(document))
    print(json.dumps({'counts': document['counts'], 'outcomes': document['overall_outcomes']}))
