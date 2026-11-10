"""Cloud-only connected velocity-threshold layers from frozen HYCOM profiles.

Thickness is diagnosed at a sampled model node. Neither a named-current axis,
cross-sectional shape nor whole-current physical thickness is established.
"""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPERATOR = 'research/eac-connected-layer-thickness-operator-v1.json'


def connected_layer(depth, velocity, threshold, core_interval=(0., 200.)):
    z = list(depth)
    v = list(velocity)
    if (len(z) != len(v) or len(z) < 2
            or any(not isinstance(x, (float, int)) or not math.isfinite(x) for x in z)
            or z[0] < 0 or any(b <= a for a, b in zip(z, z[1:]))
            or not math.isfinite(threshold) or threshold <= 0
            or len(core_interval) != 2 or not all(math.isfinite(x) for x in core_interval)
            or core_interval[0] < 0 or core_interval[1] < core_interval[0]):
        raise ValueError('Ascending nonnegative depths, positive threshold and finite core interval required')
    if any(x is not None and (not isinstance(x, (float, int)) or not math.isfinite(x)) for x in v):
        raise ValueError('Missing velocities must be explicit nulls')
    eligible = [i for i, x in enumerate(v) if x is not None and x > threshold
                and core_interval[0] <= z[i] <= core_interval[1]]
    result = {'threshold_m_s': threshold, 'upper_depth_m': None, 'lower_depth_m': None,
              'layer_thickness_m': None, 'upper_status': 'no_qualifying_core',
              'lower_status': 'no_qualifying_core', 'status': 'no_qualifying_core'}
    if not eligible:
        return result
    # First native sample breaks tied maxima, matching the frozen pilot operator.
    seed = max(eligible, key=lambda i: v[i])
    result.update(core_index=seed, core_depth_m=z[seed], core_velocity_m_s=v[seed])
    for direction, side in [(-1, 'upper'), (1, 'lower')]:
        i = seed
        while 0 <= i + direction < len(z):
            j = i + direction
            if v[j] is None:
                result[side + '_status'] = 'censored_before_missing_or_dry_level'
                result[side + '_last_connected_depth_m'] = z[i]
                break
            if v[j] <= threshold:
                crossing = z[i] + (threshold - v[i]) * (z[j] - z[i]) / (v[j] - v[i])
                result[side + '_status'] = 'adjacent_isotach_crossing'
                result[side + '_depth_m'] = crossing
                result[side + '_bracket_m'] = sorted([z[i], z[j]])
                break
            i = j
        else:
            if side == 'upper' and z[0] == 0:
                result.update(upper_status='surface_bounded_layer', upper_depth_m=0.)
            else:
                result[side + '_status'] = 'censored_at_sample_domain_edge'
                result[side + '_last_connected_depth_m'] = z[i]
    if result['upper_depth_m'] is not None and result['lower_depth_m'] is not None:
        result['layer_thickness_m'] = result['lower_depth_m'] - result['upper_depth_m']
        result['status'] = 'resolved_connected_model_threshold_layer'
    else:
        result['status'] = 'unresolved_connected_layer_boundary'
    return result


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def derive(source, op):
    if source['counts']['sampled_cases'] != 14 or len(source['samples']) != 14:
        raise ValueError('Expected frozen fourteen-case experiment')
    rows = []
    profile_rows = []
    for sample in source['samples']:
        profiles = sample['sampled_profiles']
        if len(profiles) != 5:
            raise ValueError('Frozen five-offset window required')
        descriptors = []
        for index, profile in enumerate(profiles):
            layers = [connected_layer(sample['depth_levels_m'], profile['along_velocity_m_s'], t,
                                      op['core_search_depth_interval_m']) for t in op['thresholds_m_s']]
            entry = {'snapshot_time_utc': sample['snapshot_time_utc'],
                     'route_vertex_index': sample['route_vertex_index'],
                     'profile_index': index, 'normal_offset_km': profile['normal_offset_km'],
                     'sampled_lon_lat': profile['sampled_lon_lat'], 'layers': layers}
            profile_rows.append(entry)
            descriptors.append(layers)
        selected = sample['selected_profile_index']
        if selected is not None and (type(selected) is not int or not 0 <= selected < 5):
            raise ValueError('Invalid frozen selected index')
        layers = descriptors[selected] if selected is not None else []
        # Independent upper/lower implementation must reproduce the existing
        # primary seed and lower boundary. Never select a better-resolved node.
        old = sample['primary_core_lower_descriptor']
        if selected is not None:
            if layers[0]['core_depth_m'] != old['core_depth_m']:
                raise ValueError('Frozen core selection changed')
            a, b = layers[0]['lower_depth_m'], old['lower_isotach_depth_m']
            if (a is None) != (b is None) or (a is not None and not math.isclose(a, b, abs_tol=1e-9)):
                raise ValueError('Frozen lower descriptor changed')
        rows.append({'snapshot_time_utc': sample['snapshot_time_utc'],
                     'route_vertex_index': sample['route_vertex_index'],
                     'reference_distance_km': sample['reference_distance_km'],
                     'editorial_lon_lat': sample['editorial_lon_lat'],
                     'selected_profile_index': selected,
                     'horizontal_selection_status': sample['horizontal_selection_status'],
                     'sampled_lon_lat': profiles[selected]['sampled_lon_lat'] if selected is not None else None,
                     'layers_at_frozen_selected_node': layers,
                     'named_current_axis_validated': False,
                     'physical_current_thickness_established': False})
    resolved = lambda entries: sum(x['layer_thickness_m'] is not None for x in entries)
    return {'schema': 'osw.eac-connected-layer-thickness.v1',
            'status': 'MODEL_THRESHOLD_LAYERS_NOT_WHOLE_CURRENT_THICKNESS',
            'entity_context': source['entity_id'],
            'source_product': source['source_product'],
            'counts': {'snapshot_route_cases': len(rows), 'offset_profiles': len(profile_rows),
                       'threshold_descriptors': sum(len(x['layers']) for x in profile_rows),
                       'resolved_selected_node_layers_by_threshold': {
                           str(t): resolved([r['layers_at_frozen_selected_node'][i] for r in rows
                                             if r['selected_profile_index'] is not None])
                           for i, t in enumerate(op['thresholds_m_s'])},
                       'whole_route_physical_depth_profiles': 0, 'water_volume_estimates': 0},
            'selected_route_samples': rows, 'all_offset_profiles': profile_rows,
            'uncertainty_m': None, 'eligibility': op['eligibility'], 'full_goal_complete': False}


def main():
    op = json.loads((ROOT / OPERATOR).read_bytes())
    for path, expected in op['input_sha256'].items():
        if digest(ROOT / path) != expected:
            raise ValueError('Frozen input changed: ' + path)
    if any(op['eligibility'].values()):
        raise ValueError('Unreviewed pilot cannot establish physical eligibility')
    source = json.loads((ROOT / op['source_file']).read_bytes())
    result = derive(source, op)
    result['input_sha256'] = dict(op['input_sha256'], **{OPERATOR: digest(ROOT / OPERATOR),
        'analysis/derive_eac_connected_layer_thickness_v1.py': digest(Path(__file__))})
    out = Path('eac-connected-layer-thickness-v1')
    out.mkdir(exist_ok=True)
    (out / 'candidate.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf8')
    print(json.dumps(result['counts']))


if __name__ == '__main__':
    main()
