"""Cloud-only Florida Straits profiles from published Spray fitted climatologies."""
import hashlib
import json
import math
from pathlib import Path
import netCDF4
import numpy as np
from derive_eac_connected_layer_thickness_v1 import connected_layer

ROOT = Path(__file__).resolve().parents[1]
OPERATOR = 'research/florida-spray-seasonal-depth-operator-v1.json'
OUT = Path('florida-spray-seasonal-depth-v1')
VELOCITY = ('eastward_velocity', 'northward_velocity', 'eastward_velocity_uncertainty', 'northward_velocity_uncertainty')
SUPPORT = ('along_stream_scale', 'cross_stream_scale', 'downstream_direction', 'n_pts_fit', 'n_missions_fit', 'max_gap', 'arc_fit')


def phase_indices(times):
    result = []
    for month in range(1, 13):
        hits = [i for i, t in enumerate(times) if t.month == month and t.day == 15]
        if len(hits) != 1:
            raise ValueError('Exactly one fitted phase labelled the15th per calendar month required')
        result.append((month, hits[0]))
    return result


def select_axis(z, columns):
    indices = [i for i, depth in enumerate(z) if 10 <= depth <= 200]
    if len(indices) < 2 or z[indices[0]] != 10 or z[indices[-1]] != 200:
        raise ValueError('Complete prescribed10-200m integration axis required')
    scores = []
    for v in columns:
        if len(v) != len(z):
            raise ValueError('Velocity/depth size mismatch')
        if any(v[i] is None for i in indices) or max(v[i] for i in indices) <= .05:
            scores.append(None)
            continue
        scores.append(sum((v[a] + v[b]) * (z[b] - z[a]) / 2 for a, b in zip(indices, indices[1:])))
    eligible = [i for i, score in enumerate(scores) if score is not None and score > 0]
    return (max(eligible, key=lambda i: scores[i]) if eligible else None), scores


def check_budget(nz, nx, used, maximum):
    if nz != 100 or not 1 <= nx <= 20:
        raise ValueError('Expected bounded100-level Florida section')
    scalars = nz * nx * len(VELOCITY) + nz * len(SUPPORT)
    if used + scalars > maximum:
        raise ValueError('Scalar budget exceeded before field retrieval')
    return scalars


def clean(values):
    return [float(v) if math.isfinite(float(v)) else None for v in values]


def diagnose(z, v, thresholds):
    rows = []
    for threshold in thresholds:
        r = connected_layer(z, v, threshold)
        if r['status'] == 'resolved_connected_model_threshold_layer':
            r['status'] = 'resolved_connected_fitted_observation_threshold_layer'
        rows.append(r)
    qualifying = [v[i] for i, depth in enumerate(z) if 10 <= depth <= 200 and v[i] is not None and v[i] > .05]
    half = None
    if qualifying:
        half = connected_layer(z, v, .5 * max(qualifying))
        half['relative_sampled_core_fraction'] = .5
        half['quantity_role'] = 'half_sampled_core_component_decay_depth_not_physical_bottom_or_error_bound'
        if half['status'] == 'resolved_connected_model_threshold_layer':
            half['status'] = 'resolved_connected_fitted_observation_threshold_layer'
    return rows, half


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    op = json.loads((ROOT / OPERATOR).read_bytes())
    for p, pin in op['input_sha256'].items():
        if sha(ROOT / p) != pin:
            raise ValueError('Frozen operator dependency changed')
    records = []
    sources = []
    used = 0
    OUT.mkdir(exist_ok=True)
    for kind, url in op['datasets'].items():
        with netCDF4.Dataset(url) as ds:
            if (len(ds.dimensions['depth']) != 100 or len(ds.dimensions['latitude']) != 161
                    or len(ds.dimensions['longitude']) != 161 or len(ds.dimensions['time']) != (1 if kind == 'mean' else 365)):
                raise ValueError('Source coordinate dimensions changed')
            if ds['depth'].units != 'm' or ds['depth'].positive != 'down' or ds.doi != '10.21238/S8TC9W':
                raise ValueError('Source identity or metre depth frame changed')
            for name, standard in [('eastward_velocity', 'eastward_sea_water_velocity'), ('northward_velocity', 'northward_sea_water_velocity')]:
                if ds[name].standard_name != standard:
                    raise ValueError('Source velocity frame changed')
            for name in VELOCITY + SUPPORT:
                if ds[name].dimensions != ('time', 'depth', 'latitude', 'longitude'):
                    raise ValueError('Source field dimensions changed')
            for name in VELOCITY:
                if ds[name].units != 'm s-1':
                    raise ValueError('Source velocity/uncertainty units changed')
            z = clean(ds['depth'][:]);lats = np.asarray(ds['latitude'][:]);lons = np.asarray(ds['longitude'][:])
            iy = int(np.argmin(abs(lats - op['section_latitude'])))
            ix = np.flatnonzero((lons >= op['longitude_gate'][0] - 1e-4) & (lons <= op['longitude_gate'][1] + 1e-4))
            if abs(float(lats[iy]) - op['section_latitude']) > 1e-4 or not len(ix):
                raise ValueError('Prescribed source section unavailable')
            x0, x1 = int(ix[0]), int(ix[-1])
            if z != list(range(10, 1001, 10)):
                raise ValueError('Native fitted10m grid changed')
            times = netCDF4.num2date(ds['time'][:], ds['time'].units, calendar=ds['time'].calendar)
            phases = [(None, 0)] if kind == 'mean' else phase_indices(times)
            sources.append({'kind': kind, 'opendap_url': url,
                            'global_attributes': {k: str(ds.getncattr(k)) for k in ds.ncattrs()},
                            'variable_attributes': {n: {k: str(ds[n].getncattr(k)) for k in ds[n].ncattrs()} for n in ['time', 'depth', *VELOCITY, *SUPPORT]}})
            for month, it in phases:
                used += check_budget(len(z), len(ix), used, op['maximum_field_scalars'])
                fields = {name: np.ma.filled(ds[name][it, :, iy, x0:x1+1], np.nan) for name in VELOCITY}
                north = [clean(fields['northward_velocity'][:, i]) for i in range(len(ix))]
                selected, scores = select_axis(z, north)
                profile = None
                if selected is not None:
                    values = {name: clean(field[:, selected]) for name, field in fields.items()}
                    if any(v is not None and abs(v) > 5 for name in VELOCITY[:2] for v in values[name]):
                        raise ValueError('Unexpected velocity magnitude/scaling')
                    if any(v is not None and v < 0 for name in VELOCITY[2:] for v in values[name]):
                        raise ValueError('Negative provider component uncertainty')
                    support = {name: clean(np.ma.filled(ds[name][it, :, iy, x0+selected], np.nan)) for name in SUPPORT}
                    layers, half = diagnose(z, values['northward_velocity'], op['thresholds_m_s'])
                    profile = {'source_lon_lat': [float(lons[x0+selected]), float(lats[iy])],
                               'source_values': values, 'source_fit_support': support,
                               'absolute_component_threshold_layers': layers, 'half_sampled_core_component_decay': half,
                               'sampled_core_at_shallowest_fitted_depth': layers[0].get('core_depth_m') == z[0],
                               'source_shallowest_depth_is_surface': False}
                row = {'source_product_kind': kind, 'calendar_month_phase': month,
                       'actual_provider_phase_timestamp_utc': times[it].strftime('%Y-%m-%dT%H:%M:%SZ'),
                       'timestamp_is_instantaneous_observation_date': False,
                       'source_time_index': it, 'depth_levels_m': z,
                       'section_latitude': float(lats[iy]), 'section_longitudes': clean(lons[x0:x1+1]),
                       'source_longitude_indices_inclusive': [x0, x1], 'source_latitude_index': iy,
                       'northward_component_section_columns_m_s': north,
                       'upper10_to200m_component_integrals_m2_s': scores,
                       'selected_section_column_index': selected,
                       'horizontal_selection_status': 'no_qualifying_column' if selected is None else ('edge_maximum_axis_unresolved' if selected in [0, len(ix)-1] else 'interior_fitted_section_maximum_not_independently_validated_axis'),
                       'selected_profile': profile, 'whole_current_representative': False}
                records.append(row)
                (OUT / 'checkpoint.json').write_text(json.dumps({'status': 'PARTIAL_FITTED_SECTION_COLLECTION',
                    'records': records, 'full_goal_complete': False}, indent=2, allow_nan=False) + '\n', encoding='utf8')
                print(json.dumps({'kind': kind, 'month_phase': month,
                                  'longitude': profile['source_lon_lat'][0] if profile else None,
                                  'lower_threshold_depths_m': [r['lower_depth_m'] for r in layers] if profile else None,
                                  'half_core_depth_m': half['lower_depth_m'] if profile and half else None}), flush=True)
    counts = {'fitted_profiles': len(records), 'annual_phase_profiles': 12,
              'decoded_field_scalars_budgeted': used,
              'profiles_with_selected_column': sum(r['selected_profile'] is not None for r in records),
              'resolved_lower_depths_by_threshold': {str(t): sum(r['selected_profile'] is not None and r['selected_profile']['absolute_component_threshold_layers'][i]['lower_depth_m'] is not None for r in records) for i, t in enumerate(op['thresholds_m_s'])},
              'resolved_half_sampled_core_decay_depths': sum(r['selected_profile'] is not None and r['selected_profile']['half_sampled_core_component_decay'] is not None and r['selected_profile']['half_sampled_core_component_decay']['lower_depth_m'] is not None for r in records),
              'whole_route_physical_depth_profiles': 0, 'water_volume_estimates': 0}
    result = {'schema': 'osw.florida-spray-seasonal-depth.v1',
              'status': 'FITTED_OBSERVATIONAL_SECTION_PHASE_DESCRIPTORS_NOT_WHOLE_CURRENT_DEPTH',
              'entity_context': 'current:florida', 'source_metadata': sources, 'records': records, 'counts': counts,
              'input_sha256': dict(op['input_sha256'], **{OPERATOR: sha(ROOT / OPERATOR),
                  'analysis/acquire_florida_spray_seasonal_depth_v1.py': sha(Path(__file__))}),
              'uncertainty_m': None, 'eligibility': op['eligibility'], 'full_goal_complete': False}
    OUT.mkdir(exist_ok=True)
    (OUT / 'candidate.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf8')
    print(json.dumps(counts))


if __name__ == '__main__':
    main()
