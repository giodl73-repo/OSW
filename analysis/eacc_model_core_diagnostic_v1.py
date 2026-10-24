"""Prospective regional model-core diagnostic; no source IO or admission.

Only synthetic fields have been used during preparation. Freeze the complete
source/operator/protocol dependency graph before the first original case.
"""
import math

from eacc_model_core_seed_v1 import northward_support, offset_seed, select_anchor
from indian_secc_local_normals import (
    GEOD, advance, normal_point, packed_peak, packed_row, peak_audit, profile, sample,
)


FRACTIONS = (.4, .5, .6)
COMPETING_RISE_FRACTION = .01


def _edge(field, data, peak_index, direction, fraction):
    rows = data['rows']
    peak = rows[peak_index]['q']
    threshold = fraction * peak
    minimum = peak
    previous = peak_index
    base = {'status': 'profile_limit_without_crossing', 'offset_km': None,
            'point_lon_lat': None, 'threshold_projected_m_s': threshold,
            'bracket': None, 'crossing_residual_m_s': None}
    current = previous + direction
    while 0 <= current < len(rows):
        a, b = rows[previous], rows[current]
        if b['status'] != 'ok' or b['q'] is None:
            return {**base, 'status': b['status'] + '_before_crossing'}
        if b['q'] <= threshold:
            weight = (threshold - a['q']) / (b['q'] - a['q'])
            offset = a['s'] + weight * (b['s'] - a['s'])
            point, _ = normal_point(data['origin'], data['bearing'], offset)
            evaluated = sample(field, data['origin'], data['bearing'], offset)
            if evaluated['status'] != 'ok':
                return {**base, 'status': 'unsupported_interpolated_crossing'}
            return {**base, 'status': 'connected_sampled_crossing', 'offset_km': offset,
                    'point_lon_lat': list(point), 'bracket': [packed_row(a), packed_row(b)],
                    'crossing_residual_m_s': evaluated['q'] - threshold,
                    '_bracket_indices': [previous, current]}
        # A rise before separating below the threshold may be another core.
        # This chosen sensitivity gate is not a physical eddy identification.
        if b['q'] - minimum > COMPETING_RISE_FRACTION * peak:
            return {**base, 'status': 'unresolved_rise_before_crossing',
                    'rise_m_s': b['q'] - minimum, 'rise_offset_km': b['s']}
        minimum = min(minimum, b['q'])
        previous, current = current, current + direction
    return base


def _native_scale(field, rows, left, right):
    """Conservative largest native-cell edge touched by crossing brackets.

    Include cells in every supported segment's bounding rectangle, matching
    the sampler's conservative support convention, rather than center only.
    Native spacing is not a claim about effective model resolution.
    """
    cells = set()
    points = [row['point'] for row in rows[left:right + 1]]
    for a, b in zip(points, points[1:]):
        low = field.cell(min(a[0], b[0]), min(a[1], b[1]))
        high = field.cell(max(a[0], b[0]), max(a[1], b[1]))
        if low is None or high is None:
            raise ValueError('Crossing bracket extends outside native support')
        cells.update((yi, xi) for yi in range(low[0], high[0] + 1)
                     for xi in range(low[1], high[1] + 1))
    maximum = 0.0
    for yi, xi in cells:
        west, east = float(field.x[xi]), float(field.x[xi + 1])
        south, north = float(field.y[yi]), float(field.y[yi + 1])
        edges = [(west, south, east, south), (west, north, east, north),
                 (west, south, west, north), (east, south, east, north)]
        maximum = max(maximum, *(GEOD.inv(*edge)[2] / 1000 for edge in edges))
    if not math.isfinite(maximum) or maximum <= 0:
        raise ValueError('No valid native resolution support')
    return maximum, len(cells)


def connected_spans(field, data, peak, axis_supported):
    """Retain all threshold outcomes, including spans in failed diagnostics."""
    cases = []
    for fraction in FRACTIONS:
        case = {'fraction': fraction, 'status': 'no_supported_unique_peak',
                'diagnostic_span_km': None, 'resolved_span_km': None,
                'native_cell_scale_km': None, 'native_cell_count': None,
                'span_in_native_cell_scales': None, 'edges': {},
                'current_association_verified': False,
                'effective_resolution_verified': False}
        if peak['status'] != 'supported_local_peak':
            cases.append(case)
            continue
        edges = [_edge(field, data, peak['index'], direction, fraction) for direction in (-1, 1)]
        case['edges'] = {name: {k: v for k, v in edge.items() if not k.startswith('_')}
                         for name, edge in zip(('negative_normal', 'positive_normal'), edges)}
        case['status'] = 'unresolved_edge_pair'
        if all(edge['status'] == 'connected_sampled_crossing' for edge in edges):
            width = GEOD.inv(*edges[0]['point_lon_lat'], *edges[1]['point_lon_lat'])[2] / 1000
            indices = [index for edge in edges for index in edge['_bracket_indices']]
            scale, count = _native_scale(field, data['rows'], min(indices), max(indices))
            ratio = width / scale
            case.update(diagnostic_span_km=width, native_cell_scale_km=scale,
                        native_cell_count=count, span_in_native_cell_scales=ratio)
            case['status'] = ('insufficient_native_resolution' if ratio < 4 else
                              'local_axis_unresolved' if not axis_supported else
                              'resolved_regional_model_core_diagnostic')
            if case['status'] == 'resolved_regional_model_core_diagnostic':
                case['resolved_span_km'] = width
        cases.append(case)
    return cases


def section(field, point, step, station):
    data = profile(field, point, step)
    peak = peak_audit(data)
    failures = []
    if peak['status'] != 'supported_local_peak':
        failures.append(peak['status'])
    if peak['peak_offset_km'] is not None and abs(peak['peak_offset_km']) > 10:
        failures.append('streamline_peak_displacement_exceeds_10km')
    if peak['direction_difference_degrees'] is not None and peak['direction_difference_degrees'] > 15:
        failures.append('peak_direction_difference_exceeds_15degrees')
    supported = not failures
    return {'station_arc_parameter_km': station, 'origin_lon_lat': list(point),
            'bearing_degrees_true': data['bearing'], 'peak': packed_peak(peak),
            'local_candidate_axis_check': supported, 'failed_axis_checks': failures,
            'threshold_cases': connected_spans(field, data, peak, supported),
            'samples': [packed_row(row) for row in data['rows']]}


def diagnostic_case(field, month, offset, step):
    if type(month) is not int or month not in range(1, 13):
        raise ValueError('Month must be an integer in 1..12')
    if type(offset) is not int or offset not in (-1, 0, 1):
        raise ValueError('Native latitude offset must be -1, 0 or 1')
    if type(step) is not int or step not in (5, 10):
        raise ValueError('Normal profile step must be 5 or 10 km')
    result = {'id': f'm{month:02d}:offset{offset}:step{step}', 'month': month,
              'native_latitude_offset': offset, 'normal_sample_step_km': step,
              'status': 'missing_month_field', 'anchor': None, 'seed': None,
              'initial_refinement': None, 'refined_seed_lon_lat': None,
              'stations': [], 'paths': [], 'all_five_local_axis_checks_pass': False,
              'all_five_half_peak_spans_resolved': False,
              'current_association_verified': False, 'whole_current_width_km': None,
              'whole_current_length_km': None, 'annual_physical_range_admitted': False,
              'physical_state_join_eligible': False, 'length_rank_eligible': False,
              'width_rank_eligible': False}
    if field is None:
        return result
    anchor = select_anchor(field)
    result['anchor'] = anchor
    if anchor['status'] != 'supported_northward_seed':
        return {**result, 'status': anchor['status']}
    seed = offset_seed(field, anchor, offset)
    result['seed'] = seed
    if seed['status'] != 'supported_northward_seed':
        return {**result, 'status': seed['status']}
    initial = profile(field, tuple(seed['origin_lon_lat']), step)
    peak = peak_audit(initial)
    result['initial_refinement'] = {
        'peak': packed_peak(peak), 'samples': [packed_row(row) for row in initial['rows']],
        'threshold_cases': connected_spans(field, initial, peak, False)}
    if peak['status'] != 'supported_local_peak':
        return {**result, 'status': 'seed_refinement_' + peak['status']}
    refined = initial['rows'][peak['index']]['point']
    result['refined_seed_lon_lat'] = list(refined)
    # Check the actual refined Earth-frame vector again, without selecting
    # another point when the winner fails the northward directional guard.
    refined_velocity = field.sample(*refined)
    support = northward_support(*refined_velocity)
    result['refined_vector_support'] = support
    if support['status'] != 'supported_northward_seed':
        return {**result, 'status': 'refined_' + support['status']}
    result['stations'].append(section(field, refined, step, 0))
    if offset != 0:
        return {**result, 'status': 'seed_sensitivity_section_only'}
    for direction in (-1, 1):
        point = refined
        for number in (1, 2):
            path, point = advance(field, point, direction)
            path.update(direction=direction, target_station_arc_parameter_km=direction * number * 50)
            result['paths'].append(path)
            if path['status'] != 'target_station_reached':
                break
            result['stations'].append(section(field, point, step, direction * number * 50))
    result['stations'].sort(key=lambda row: row['station_arc_parameter_km'])
    axis = len(result['stations']) == 5 and all(row['local_candidate_axis_check'] for row in result['stations'])
    resolved = axis and all(row['threshold_cases'][1]['resolved_span_km'] is not None for row in result['stations'])
    return {**result, 'all_five_local_axis_checks_pass': axis,
            'all_five_half_peak_spans_resolved': resolved,
            'status': 'five_station_diagnostic_supported' if resolved else 'candidate_diagnostic_unresolved'}


def diagnose_months(fields_by_month):
    """Always retain 12 months x 3 seed offsets x 2 sampling steps.

    A missing month remains six explicitly unsupported cases; no seasonal
    range, independent observation or named-current admission follows.
    """
    if any(type(month) is not int or month not in range(1, 13) for month in fields_by_month):
        raise ValueError('Unexpected month key')
    return [diagnostic_case(fields_by_month.get(month), month, offset, step)
            for month in range(1, 13) for offset in (-1, 0, 1) for step in (5, 10)]


def diagnose_year(fields_by_month):
    """Numerical result plus explicit missing support and method comparisons.

    No source identity is inferred from the supplied arrays. An original case
    additionally requires a separate frozen source/protocol/custody envelope.
    """
    cases = diagnose_months(fields_by_month)
    lookup = {(case['month'], case['native_latitude_offset'], case['normal_sample_step_km']): case
              for case in cases}

    def station(case, arc):
        return next((row for row in case['stations'] if row['station_arc_parameter_km'] == arc), None)

    def comparison(a, b, arc):
        sa, sb = station(a, arc), station(b, arc)
        rows = []
        for i, fraction in enumerate(FRACTIONS):
            ta = None if sa is None else sa['threshold_cases'][i]
            tb = None if sb is None else sb['threshold_cases'][i]
            wa = None if ta is None else ta['resolved_span_km']
            wb = None if tb is None else tb['resolved_span_km']
            rows.append({'fraction': fraction,
                         'a_status': a['status'] if ta is None else ta['status'],
                         'b_status': b['status'] if tb is None else tb['status'],
                         'a_resolved_span_km': wa, 'b_resolved_span_km': wb,
                         'b_minus_a_km': None if wa is None or wb is None else wb - wa})
        return {'a_case_id': a['id'], 'b_case_id': b['id'],
                'station_arc_parameter_km': arc, 'thresholds': rows}

    step_comparisons = []
    seed_comparisons = []
    months = []
    for month in range(1, 13):
        for offset in (-1, 0, 1):
            for arc in ((-100, -50, 0, 50, 100) if offset == 0 else (0,)):
                step_comparisons.append(comparison(lookup[month, offset, 5], lookup[month, offset, 10], arc))
        for step in (5, 10):
            for offset in (-1, 1):
                seed_comparisons.append(comparison(lookup[month, 0, step], lookup[month, offset, step], 0))
        primary = [lookup[month, 0, step] for step in (5, 10)]
        spans = []
        for case in primary:
            central = station(case, 0)
            half = None if central is None else central['threshold_cases'][1]
            spans.append({'case_id': case['id'], 'case_status': case['status'],
                          'central_half_peak_status': None if half is None else half['status'],
                          'central_resolved_half_peak_span_km': None if half is None else half['resolved_span_km']})
        months.append({'month': month, 'primary_cases': spans,
                       'both_five_station_half_peak_diagnostics_supported':
                           all(case['all_five_half_peak_spans_resolved'] for case in primary)})
    return {'schema': 'osw.eacc-regional-model-core.numerical-diagnostic.v1',
            'evidence_class': 'regional_model_core_diagnostic_not_named_current_admission',
            'source_identity_verified': False, 'current_association_verified': False,
            'case_count': len(cases), 'cases': cases, 'months': months,
            'normal_step_comparisons': step_comparisons, 'native_seed_comparisons': seed_comparisons,
            'comparison_interpretation': 'Chosen-method sensitivity; not independent observations or measurement uncertainty.',
            'whole_current_width_km': None, 'whole_current_length_km': None,
            'annual_physical_minimum_width_km': None, 'annual_physical_maximum_width_km': None,
            'measurement_uncertainty_km': None,
            'required_followup': 'Verified source identity, regional association maps and separate admission review.',
            'physical_state_join_eligible': False, 'width_rank_eligible': False, 'length_rank_eligible': False}
