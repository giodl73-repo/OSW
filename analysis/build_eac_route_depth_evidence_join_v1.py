"""Cloud-only evidence join and conditional reference-corridor depth segments.

No identity validation, full-route physical profile or water volume is inferred.
"""
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPERATOR = 'research/eac-route-depth-evidence-join-operator-v1.json'
OUT = Path('eac-route-depth-evidence-join-v1')
SUPPORTED = 'poleward_surface_component_supported_not_current_identity'


def indexed(rows, time_field):
    result = {}
    for i, row in enumerate(rows):
        stamp = row[time_field]
        if time_field == 'snapshot_time_utc' and stamp[10:] != 'T00:00:00Z':
            raise ValueError('Only exact prescribed midnight snapshots can be joined')
        key = stamp[:10], row['route_vertex_index']
        if key in result:
            raise ValueError('Duplicate date/vertex evidence cannot be silently selected')
        result[key] = i, row
    return result


def same_number(a, b):
    return (a is None and b is None) or (a is not None and b is not None
        and math.isfinite(a) and math.isfinite(b) and math.isclose(a, b, rel_tol=0, abs_tol=1e-9))


def interpolate(segment, distance_km, quantity='lower_isotach_depth_m'):
    if quantity not in ['lower_isotach_depth_m', 'layer_thickness_m']:
        raise ValueError('Unsupported projected quantity')
    a, b = segment['reference_distance_interval_km']
    if not math.isfinite(distance_km) or not a <= distance_km <= b:
        raise ValueError('No reference-corridor extrapolation')
    values = segment[quantity + '_endpoints']
    if values is None:
        return None
    return values[0] + (values[1] - values[0]) * (distance_km - a) / (b - a)


def join(model, layers, surface, moorings, op):
    mi = indexed(model['samples'], 'snapshot_time_utc')
    li = indexed(layers['selected_route_samples'], 'snapshot_time_utc')
    si = indexed(surface['samples'], 'source_date')
    expected = {(day, vertex) for day in op['source_dates'] for vertex in range(7)}
    if set(mi) != expected or set(li) != expected or set(si) != expected:
        raise ValueError('Exact complete date/vertex keys required; no intersection-only join')
    for source in [model, layers, surface]:
        if any(source['eligibility'].values()):
            raise ValueError('Unreviewed physical eligibility cannot enter the corridor join')
    nodes = []
    for day, vertex in sorted(expected):
        im, m = mi[day, vertex]
        il, l = li[day, vertex]
        isu, s = si[day, vertex]
        if (m['selected_profile_index'] != l['selected_profile_index']
                or m['selected_profile_index'] != s['screen']['frozen_model_selected_profile_index']
                or m['horizontal_selection_status'] != l['horizontal_selection_status']
                or m['horizontal_selection_status'] != s['frozen_model_horizontal_selection_status']
                or m['editorial_lon_lat'] != l['editorial_lon_lat']
                or m['editorial_lon_lat'] != s['editorial_lon_lat']
                or m['reference_distance_km'] != l['reference_distance_km']
                or not same_number(m['downstream_reference_bearing_degrees_true'], s['downstream_reference_bearing_degrees_true'])
                or m['snapshot_time_utc'] != l['snapshot_time_utc']):
            raise ValueError('Frozen selection, geometry, time or component frame changed')
        if len(s['profiles_at_frozen_targets']) != len(m['sampled_profiles']):
            raise ValueError('Surface target count changed')
        for a, b in zip(m['sampled_profiles'], s['profiles_at_frozen_targets']):
            if a['target_lon_lat'] != b['target_lon_lat']:
                raise ValueError('Surface targets do not match frozen model targets')
        screen = s['screen']
        if screen['named_current_axis_validated'] or screen['physical_depth_validated']:
            raise ValueError('Surface corroboration is not identity/depth validation')
        value = screen['surface_component_at_frozen_model_node_m_s']
        if (screen['status'] == SUPPORTED) != (value is not None and value > .05):
            raise ValueError('Surface support flag disagrees with retained component')
        selected = m['selected_profile_index']
        primary = l['layers_at_frozen_selected_node'][0] if selected is not None else None
        lower = primary['lower_depth_m'] if primary else None
        thickness = primary['layer_thickness_m'] if primary else None
        if primary and (primary['threshold_m_s'] != .05 or not same_number(lower, m['primary_core_lower_descriptor']['lower_isotach_depth_m'])):
            raise ValueError('Primary layer and lower-contour definitions disagree')
        reasons = []
        if lower is None:
            reasons.append('lower_boundary_unresolved')
        if screen['status'] != SUPPORTED:
            reasons.append('surface_component_not_corroborated_or_missing')
        if m['horizontal_selection_status'] != 'interior_sampled_maximum_not_validated_axis':
            reasons.append('horizontal_axis_unresolved_at_window_edge_or_no_node')
        ready = not reasons
        nodes.append({'source_date': day, 'route_vertex_index': vertex,
                      'editorial_lon_lat': m['editorial_lon_lat'],
                      'reference_distance_km': m['reference_distance_km'],
                      'selected_model_node_lon_lat': m['sampled_profiles'][selected]['sampled_lon_lat'] if selected is not None else None,
                      'frozen_model_selected_profile_index': selected,
                      'model_primary_lower_isotach_depth_m': lower,
                      'model_primary_connected_layer': primary,
                      'model_horizontal_selection_status': m['horizontal_selection_status'],
                      'surface_screen': screen,
                      'conditional_lower_depth_projection_node_eligible': ready,
                      'conditional_thickness_projection_node_eligible': ready and thickness is not None,
                      'projection_block_reasons': reasons,
                      'source_pointers': {'model': '/samples/' + str(im),
                                          'layers': '/selected_route_samples/' + str(il),
                                          'surface': '/samples/' + str(isu)},
                      'regional_mooring_context_key': day + '-near27S' if vertex == 4 else None,
                      'current_axis_or_physical_depth_validated': False})
    segments = []
    for day in op['source_dates']:
        daily = [n for n in nodes if n['source_date'] == day]
        for a, b in zip(daily, daily[1:]):
            if b['route_vertex_index'] != a['route_vertex_index'] + 1 or b['reference_distance_km'] <= a['reference_distance_km']:
                raise ValueError('Adjacent vertices with ascending reference distance required')
            ready = a['conditional_lower_depth_projection_node_eligible'] and b['conditional_lower_depth_projection_node_eligible']
            thick = a['conditional_thickness_projection_node_eligible'] and b['conditional_thickness_projection_node_eligible']
            segments.append({'source_date': day, 'route_vertex_interval': [a['route_vertex_index'], b['route_vertex_index']],
                             'reference_distance_interval_km': [a['reference_distance_km'], b['reference_distance_km']],
                             'lower_isotach_depth_m_endpoints': [a['model_primary_lower_isotach_depth_m'], b['model_primary_lower_isotach_depth_m']] if ready else None,
                             'layer_thickness_m_endpoints': [a['model_primary_connected_layer']['layer_thickness_m'], b['model_primary_connected_layer']['layer_thickness_m']] if thick else None,
                             'status': 'conditional_linear_reference_corridor_diagnostic' if ready else 'gap_no_projection',
                             'endpoint_block_reasons': {'start': a['projection_block_reasons'], 'end': b['projection_block_reasons']},
                             'unsampled_interior_assumed_linear_not_observed': bool(ready),
                             'physical_current_continuity_established': False,
                             'volume_eligible': False})
    context = []
    for day in op['source_dates']:
        records = [{'station': r['station'], 'lon_lat': r['lon_lat'],
                    'actual_source_time_utc': r['actual_source_time_utc'],
                    'threshold_layers': r['threshold_layers'], 'source_pointer': '/samples/' + str(i)}
                   for i, r in enumerate(moorings['samples']) if r['source_date'] == day]
        if len(records) != 7 or len({r['station'] for r in records}) != 7:
            raise ValueError('Complete seven-station observational context required')
        context.append({'key': day + '-near27S', 'source_date': day, 'records': records,
                        'role': 'regional_fixed_station_context_not_colocated_or_used_for_model_depth_filling',
                        'temporal_operator': 'five_day_filtered_daily_unfilled_processed_observations',
                        'model_observation_colocated': False})
    counts = {'dated_route_nodes': len(nodes), 'adjacent_reference_segments': len(segments),
              'conditional_lower_depth_nodes': sum(n['conditional_lower_depth_projection_node_eligible'] for n in nodes),
              'conditional_thickness_nodes': sum(n['conditional_thickness_projection_node_eligible'] for n in nodes),
              'conditional_linear_reference_segments': sum(s['status'] != 'gap_no_projection' for s in segments),
              'gap_segments': sum(s['status'] == 'gap_no_projection' for s in segments),
              'regional_mooring_context_profiles': sum(len(c['records']) for c in context),
              'whole_route_physical_depth_profiles': 0, 'water_volume_estimates': 0}
    return {'schema': 'osw.eac-route-depth-evidence-join.v1',
            'status': 'GAP_PRESERVING_CONDITIONAL_REFERENCE_CORRIDOR_DEPTH_SCENARIOS',
            'entity_context': 'current:east-australian', 'counts': counts,
            'nodes': nodes, 'segments': segments, 'regional_mooring_context': context,
            'projection_assumptions': op['projection_assumptions'],
            'uncertainty_m': None, 'eligibility': op['eligibility'], 'full_goal_complete': False}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    op = json.loads((ROOT / OPERATOR).read_bytes())
    for path, pin in op['input_sha256'].items():
        if sha(ROOT / path) != pin:
            raise ValueError('Frozen source changed: ' + path)
    sources = [json.loads((ROOT / op[name + '_file']).read_bytes()) for name in ['model', 'layers', 'surface', 'moorings']]
    result = join(*sources, op)
    result['input_sha256'] = dict(op['input_sha256'], **{OPERATOR: sha(ROOT / OPERATOR),
        'analysis/build_eac_route_depth_evidence_join_v1.py': sha(Path(__file__))})
    OUT.mkdir(exist_ok=True)
    (OUT / 'candidate.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf8')
    print(json.dumps(result['counts']))


if __name__ == '__main__':
    main()
