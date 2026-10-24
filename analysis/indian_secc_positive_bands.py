"""Exhaustive native-grid eastward bands; connectivity is not current identity."""
import hashlib
import json
import math
from collections import deque

from build_indian_secc_oscar_2d_source import ROOT, REPORT as SOURCE, verify as verify_source
from build_basin_surface_section_spans import measure

PROTOCOL = 'plans/indian-secc-positive-band-connectivity-protocol-v1.md'
READBACK_PROTOCOL = 'plans/indian-secc-band-calculation-readback-protocol-v1.md'
OPERATOR = 'analysis/indian_secc_positive_bands.py'
REPORT = 'research/indian-secc-positive-band-connectivity.json'
HISTORICAL = 'research/indian-secc-oscar-1995-2016-monthly-sections.json'
FIGURE = 'figures/indian-secc-positive-band-connectivity.svg'
MANIFEST = 'research/indian-secc-positive-band-figure.json'
FRACTIONS = (.4, .5, .6)


def digest(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def distance_readback(case):
    """Round new geodesic distances only; original source and brackets stay exact."""
    def number(value):
        if value is None: return None
        if not math.isfinite(value): raise ValueError('Nonfinite geodesic readback')
        value = round(value, 6)
        return 0.0 if value == 0 else value
    return {**case, 'span_km': number(case['span_km']),
            'grid_bracket_span_km': None if case['grid_bracket_span_km'] is None else
                [number(v) for v in case['grid_bracket_span_km']]}


def positive_runs(values):
    """Maximal consecutive strictly positive cells; no zero/NaN bridges."""
    runs = []; start = None
    for i in range(len(values)+1):
        value = values[i] if i < len(values) else None
        good = value is not None and math.isfinite(value) and value > 0
        if good and start is None:
            start = i
        if not good and start is not None:
            runs.append((start, i-1)); start = None
    return runs


def maxima(values, low, high):
    plateaus = []; i = low
    while i <= high:
        end = i
        while end < high and values[end+1] == values[i]:
            end += 1
        if (i == low or values[i-1] < values[i]) and (end == high or values[end+1] < values[i]):
            plateaus.append({'first_row': i, 'last_row': end, 'eastward_m_s': values[i]})
        i = end+1
    return plateaus


def zero_edge(profile, inner, direction):
    outer = inner+direction
    if not 0 <= outer < len(profile):
        return {'status': 'source_boundary_without_crossing', 'latitude': None, 'bracket_rows': None}
    a, b = profile[inner], profile[outer]
    if b['component_m_s'] is None:
        return {'status': 'missing_before_crossing', 'latitude': None, 'bracket_rows': [inner, outer]}
    assert a['component_m_s'] > 0 and b['component_m_s'] <= 0
    t = a['component_m_s']/(a['component_m_s']-b['component_m_s'])
    return {'status': 'exact_native_zero' if b['component_m_s'] == 0 else 'linear_zero_crossing',
            'latitude': a['latitude']+t*(b['latitude']-a['latitude']), 'bracket_rows': [inner, outer]}


def column_nodes(profile, longitude, column):
    values = [p['component_m_s'] for p in profile]; nodes = []
    for ordinal, (low, high) in enumerate(positive_runs(values)):
        peak = max(values[low:high+1]); ties = [i for i in range(low, high+1) if values[i] == peak]
        section = {'fixed_axis': 'longitude', 'fixed_coordinate': longitude, 'varying_axis': 'latitude',
                   'peak_search': [profile[low]['latitude'], profile[high]['latitude']]}
        spans = [distance_readback(measure(profile, section, fraction)) for fraction in FRACTIONS]
        for case in spans:
            for edge in case['boundaries'].values():
                if edge.get('coordinate') is not None:
                    # A positive threshold cannot cross a nonpositive or missing separator.
                    assert profile[max(0, low-1)]['latitude'] <= edge['coordinate'] <= profile[min(len(profile)-1, high+1)]['latitude']
        nodes.append({'id': f'x{column:03d}:r{ordinal:02d}', 'column': column, 'longitude': longitude,
                      'first_row': low, 'last_row': high, 'south_native_latitude': profile[low]['latitude'],
                      'north_native_latitude': profile[high]['latitude'], 'peak_eastward_m_s': peak,
                      'peak_latitude': profile[ties[0]]['latitude'], 'equal_global_peak_rows': ties,
                      'local_maximum_plateaus': maxima(values, low, high),
                      'south_zero_edge': zero_edge(profile, low, -1), 'north_zero_edge': zero_edge(profile, high, 1),
                      'threshold_cases': spans, 'west_neighbors': [], 'east_neighbors': []})
    return nodes


def connect(columns):
    nodes = {r['id']: r for col in columns for r in col}
    for left, right in zip(columns, columns[1:]):
        for a in left:
            for b in right:
                if max(a['first_row'], b['first_row']) <= min(a['last_row'], b['last_row']):
                    a['east_neighbors'].append(b['id']); b['west_neighbors'].append(a['id'])
    components = []
    for node in nodes.values():
        if 'component_id' in node:
            continue
        cid = f'component-{len(components):03d}'; queue = deque([node['id']]); members = []
        node['component_id'] = cid
        while queue:
            current = nodes[queue.popleft()]; members.append(current['id'])
            for neighbor in current['west_neighbors']+current['east_neighbors']:
                if 'component_id' not in nodes[neighbor]:
                    nodes[neighbor]['component_id'] = cid; queue.append(neighbor)
        selected = [nodes[k] for k in members]
        sides = set()
        for r in selected:
            if r['column'] == 0: sides.add('west')
            if r['column'] == len(columns)-1: sides.add('east')
            for direction in ['south', 'north']:
                if r[direction+'_zero_edge']['status'] == 'source_boundary_without_crossing': sides.add(direction)
        components.append({'id': cid, 'node_ids': sorted(members), 'nodes': len(members),
                           'native_columns': len({r['column'] for r in selected}),
                           'longitude_domain': [min(r['longitude'] for r in selected), max(r['longitude'] for r in selected)],
                           'native_latitude_domain': [min(r['south_native_latitude'] for r in selected), max(r['north_native_latitude'] for r in selected)],
                           'source_boundary_contacts': sorted(sides),
                           'eastward_splits': sum(len(r['east_neighbors']) > 1 for r in selected),
                           'eastward_merges': sum(len(r['west_neighbors']) > 1 for r in selected),
                           'multiple_local_peak_nodes': sum(len(r['local_maximum_plateaus']) > 1 for r in selected),
                           'equator_or_north_native_cells': any(r['north_native_latitude'] >= 0 for r in selected)})
    return list(nodes.values()), components


def profiles(source, frame):
    order = sorted(range(len(source['latitude_degrees_north'])), key=lambda i: source['latitude_degrees_north'][i])
    result = []
    for xi, lon in enumerate(source['longitude_degrees_east']):
        profile = []
        for yi in order:
            u = frame['eastward_m_s'][yi][xi]; v = frame['northward_m_s'][yi][xi]
            paired = u is not None and v is not None
            lat = source['latitude_degrees_north'][yi]
            profile.append({'coordinate': lat, 'latitude': lat, 'longitude': lon,
                            'component_m_s': u if paired else None, 'eastward_m_s': u,
                            'northward_m_s': v, 'paired_source_samples': frame['paired_samples'][yi][xi]})
        result.append(profile)
    return result


def compact_case(case):
    return {'fraction': case['fraction'], 'status': case['status'], 'span_km': case['span_km'],
            'boundaries': {k: {'status': v['status'], 'latitude': v.get('coordinate')} for k, v in case['boundaries'].items()}}


def compare_cases(previous, current):
    """Keep support changes independent of platform-dependent geodesic floats."""
    a, b = compact_case(previous), compact_case(distance_readback(current))
    boundaries_exact = {k:v for k,v in a.items() if k != 'span_km'} == {k:v for k,v in b.items() if k != 'span_km'}
    old_span, new_span = a['span_km'], b['span_km']
    span_matches = old_span is None and new_span is None or old_span is not None and new_span is not None and round(old_span,6) == new_span
    old_north = a['boundaries'].get('high_coordinate', {})
    new_north = b['boundaries'].get('high_coordinate', {})
    recovered_north = old_north.get('status') == 'domain_edge_without_crossing' and new_north.get('status') == 'resolved'
    return {'historical': a, 'surrounding_domain': b,
            'boundary_coordinates_and_status_exact': boundaries_exact,
            'span_readback_matches': span_matches,
            'comparison_kind': 'same_boundaries_and_status' if boundaries_exact else
                'northern_domain_extension' if recovered_north else 'other_boundary_or_support_difference',
            'northern_crossing_recovered': recovered_north,
            'span_readback_difference_km': None if old_span is None or new_span is None else round(new_span-round(old_span,6),6)}


def build():
    source, pins = verify_source(); historical = json.loads((ROOT/HISTORICAL).read_bytes())
    months = []; summaries = []; comparisons = []
    for frame in source['months']:
        cols = profiles(source, frame)
        bands = [column_nodes(profile, source['longitude_degrees_east'][xi], xi) for xi, profile in enumerate(cols)]
        nodes, components = connect(bands); by_id = {n['id']: n for n in nodes}; anchors = []
        for old in historical['sections']:
            lon = old['longitude_degrees_east']; xi = min(range(len(cols)), key=lambda i: abs(source['longitude_degrees_east'][i]-lon))
            assert abs(source['longitude_degrees_east'][xi]-lon) < 1e-8
            section = {'fixed_axis': 'longitude', 'fixed_coordinate': lon, 'varying_axis': 'latitude', 'peak_search': [-6, -2.5]}
            cases = [distance_readback(measure(cols[xi], section, f)) for f in FRACTIONS]; nominal = cases[1]
            anchor = {'section_id': old['section_id'], 'longitude': lon, 'status': nominal['status'],
                      'search_latitude_domain': [-6, -2.5], 'selected_peak_latitude': nominal.get('peak_coordinate'),
                      'selected_peak_eastward_m_s': nominal.get('peak_component_m_s'), 'band_id': None, 'component_id': None}
            if nominal.get('peak_component_m_s', -1) >= .02:
                row = next(i for i, p in enumerate(cols[xi]) if p['latitude'] == nominal['peak_coordinate'])
                band = next(n for n in bands[xi] if n['first_row'] <= row <= n['last_row'])
                anchor.update(band_id=band['id'], component_id=band['component_id'],
                              selected_peak_is_band_global_peak=nominal['peak_component_m_s'] == band['peak_eastward_m_s'])
            old_cases = old['yearly']['2013']['months'][frame['month']-1]['threshold_scenarios']
            for previous, current in zip(old_cases, cases):
                comparisons.append({'month': frame['month'], 'section_id': old['section_id'], 'fraction': current['fraction'],
                                    **compare_cases(previous, current),
                                    'domain_comparison': 'historical_12S_to_equator_vs_surrounding_10S_to_2N'})
            anchor['anchor_search_threshold_cases'] = cases; anchors.append(anchor)
        selected_ids = sorted({a['component_id'] for a in anchors if a['component_id'] is not None})
        selected_components = [c for c in components if c['id'] in selected_ids]
        selected_nodes = [n for n in nodes if n['component_id'] in selected_ids]
        summary = {'month': frame['month'], 'native_longitude_columns': len(cols), 'positive_bands': len(nodes),
                   'connected_components': len(components), 'eastward_splits': sum(c['eastward_splits'] for c in components),
                   'eastward_merges': sum(c['eastward_merges'] for c in components),
                   'half_peak_paired_bands': sum(n['threshold_cases'][1]['status'] == 'paired_boundaries' for n in nodes),
                   'weak_bands_retained': sum(n['peak_eastward_m_s'] < .02 for n in nodes),
                   'eligible_anchor_count': sum(a['component_id'] is not None for a in anchors),
                   'eligible_anchors_same_component': len(selected_ids) == 1 if all(a['component_id'] is not None for a in anchors) else None,
                   'anchor_components': selected_ids,
                   'anchor_component_columns': len({n['column'] for n in selected_nodes}),
                   'anchor_component_equator_or_north_reach': any(c['equator_or_north_native_cells'] for c in selected_components) if selected_components else None,
                   'anchor_component_source_truncation': any(c['source_boundary_contacts'] for c in selected_components) if selected_components else None,
                   'anchor_component_split_merge_nodes': sum(c['eastward_splits']+c['eastward_merges'] for c in selected_components),
                   'recovered_threshold_cases_from_northern_extension': sum(c['northern_crossing_recovered'] for c in comparisons if c['month'] == frame['month']),
                   'physical_axis_or_width_admitted': False}
        for anchor in anchors:
            section_key = anchor['section_id'].removeprefix('indian-secc-').replace('-', '_')
            case = anchor['anchor_search_threshold_cases'][1]
            summary['anchor_'+section_key+'_half_peak_component_span_km'] = case['span_km']
            summary['anchor_'+section_key+'_half_peak_status'] = case['status']
            summary['anchor_'+section_key+'_northern_edge_degrees_north'] = case['boundaries'].get('high_coordinate', {}).get('coordinate')
        summaries.append(summary)
        months.append({'month': frame['month'], 'source_times': frame['source_times'], 'bands': nodes,
                       'components': components, 'anchors': anchors})
    inputs = [PROTOCOL, READBACK_PROTOCOL, OPERATOR, HISTORICAL, 'analysis/build_basin_surface_section_spans.py']
    return {'schema': 'osw.indian-secc-positive-band-connectivity.v2', 'status': 'exploratory_grid_connectivity_not_current_axis',
            'current_id': source['current_id'], 'entity_id': source['entity_id'], 'source_file': SOURCE,
            'nominal_depth_m': 15, 'source_first_time': source['source_first_time'], 'source_last_time': source['source_last_time'],
            'longitude_degrees_east': source['longitude_degrees_east'], 'latitude_order': 'south_to_north',
            'source_latitude_domain': [-10, 2], 'connectivity_rule': 'four_neighbor_strict_positive_eastward_paired_native_cells',
            'component_span_rule': 'fixed_meridian_0.4_0.5_0.6_global_run_peak_eastward_component_minimum_peak_0.02_m_s',
            'months': months, 'monthly_summary': summaries, 'historical_section_comparisons': comparisons,
            'counts': {'monthly_columns': sum(s['native_longitude_columns'] for s in summaries),
                       'positive_bands': sum(s['positive_bands'] for s in summaries),
                       'historical_threshold_cases': len(comparisons),
                       'historical_boundary_status_exact': sum(c['boundary_coordinates_and_status_exact'] for c in comparisons),
                       'historical_span_readback_matches': sum(c['span_readback_matches'] for c in comparisons),
                       'historical_domain_differences': sum(not c['boundary_coordinates_and_status_exact'] for c in comparisons)},
            'derived_distance_readback_decimal_km': 6,
            'distance_readback_is_physical_uncertainty': False,
            'historical_values_rounded_or_rewritten': False,
            'current_association_verified': False, 'physical_current_axis_admitted': False,
            'whole_current_length_km': None, 'whole_current_width_km': None, 'annual_physical_width_range_km': None,
            'length_rank_eligible': False, 'width_rank_eligible': False, 'physical_state_join_eligible': False,
            'comparison_figure': FIGURE,
            'input_sha256': {**pins, **{p: digest(p) for p in inputs}},
            'limitations': ['Native-grid connectivity is neither flow direction along an axis nor proof of named-current association.',
                'Positive bands may join competing jets or eddies; all splits, merges, weak runs and censored edges are retained.',
                'Local fixed-meridian component spans are not flow-normal widths, whole-current dimensions or physical annual ranges.',
                'The coarse source grid and mapped monthly means do not resolve fine coasts or instantaneous transport boundaries.',
                'Threshold sensitivity and grid brackets are method/resolution diagnostics, not confidence intervals.']}


def encoded(document):
    return (json.dumps(document, separators=(',', ':'), allow_nan=False)+'\n').encode()


def verify():
    document = json.loads((ROOT/REPORT).read_bytes())
    if encoded(document) != encoded(build()):
        raise ValueError('Changed positive-band source/operator/report')
    manifest = json.loads((ROOT/MANIFEST).read_bytes())
    if manifest['source_file'] != REPORT or manifest['source_sha256'] != digest(REPORT) or manifest['current_geometry_admitted'] is not False:
        raise ValueError('Changed positive-band figure/source binding')
    pins = {**document['input_sha256'], REPORT: digest(REPORT), MANIFEST: digest(MANIFEST),
            manifest['generator_file']: manifest['generator_sha256']}
    pins.update({a['file']: a['sha256'] for a in manifest['figures'].values()})
    for path, pin in pins.items():
        if digest(path) != pin: raise ValueError('Changed positive-band dependency:'+path)
    return document, pins


if __name__ == '__main__':
    document = build(); (ROOT/REPORT).write_bytes(encoded(document)); print(json.dumps(document['counts']))
