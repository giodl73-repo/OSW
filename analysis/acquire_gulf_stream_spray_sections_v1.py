"""Cloud-only fitted Gulf Stream depth sections with a locked mean-flow frame."""
import hashlib
import json
import math
from pathlib import Path
import urllib.parse
import urllib.request
import netCDF4
import numpy as np
from acquire_florida_spray_seasonal_depth_v1 import phase_indices, nominal_phase_date, source_doi_matches, diagnose

ROOT = Path(__file__).resolve().parents[1]
OPERATOR = 'research/gulf-stream-spray-depth-sections-operator-v1.json'
OUT = Path('gulf-stream-spray-depth-sections-v1')
VELOCITY = ('eastward_velocity', 'northward_velocity', 'eastward_velocity_uncertainty', 'northward_velocity_uncertainty')
SUPPORT = ('along_stream_scale', 'cross_stream_scale', 'downstream_direction', 'n_pts_fit', 'n_missions_fit', 'max_gap', 'arc_fit')
FIELDS = VELOCITY + SUPPORT


def project(u, v, direction):
    if u is None or v is None or direction is None:
        return None
    angle = math.radians(direction)
    return u * math.sin(angle) + v * math.cos(angle)


def select_axis(z, candidates):
    indices = [i for i, d in enumerate(z) if 10 <= d <= 200]
    if len(indices) != 20 or [z[i] for i in indices] != list(range(10, 201, 10)):
        raise ValueError('Complete fixed10-200m fitted integration grid required')
    iz = z.index(100)
    results = []
    for candidate in candidates:
        direction = candidate['source_fit_support']['downstream_direction'][iz]
        raw = candidate['source_values']
        v = [project(u, n, direction) for u, n in zip(raw['eastward_velocity'], raw['northward_velocity'])]
        if direction is None or not 0 <= direction % 360 <= 135:
            score = None
            status = 'reference_direction_outside_prescribed_NE_to_SE_sector_or_missing'
        elif any(v[i] is None for i in indices) or max(v[i] for i in indices) <= .05:
            score = None
            status = 'incomplete_or_nonqualifying_upper_component'
        else:
            score = sum((v[a] + v[b]) * (z[b] - z[a]) / 2 for a, b in zip(indices, indices[1:]))
            status = 'complete_fixed_depth_support'
        results.append({'source_lon_lat': candidate['source_lon_lat'],
                        'reference_direction_at100m_degrees_clockwise_from_north': direction,
                        'upper10_to200m_eastward_velocity_m_s': [raw['eastward_velocity'][i] for i in indices],
                        'upper10_to200m_northward_velocity_m_s': [raw['northward_velocity'][i] for i in indices],
                        'upper10_to200m_locked_direction_component_m_s': [v[i] for i in indices],
                        'upper10_to200m_signed_integral_m2_s': score, 'selection_support_status': status})
    eligible = [i for i, r in enumerate(results) if r['upper10_to200m_signed_integral_m2_s'] is not None
                and r['upper10_to200m_signed_integral_m2_s'] > 0]
    selected = max(eligible, key=lambda i: results[i]['upper10_to200m_signed_integral_m2_s']) if eligible else None
    return selected, results


def check_budget(nz, ny, nx, used, maximum):
    if nz != 100 or min(ny, nx) != 1 or max(ny, nx) > 50:
        raise ValueError('Bounded one-dimensional section with100 fitted levels required')
    count = nz * ny * nx * len(FIELDS)
    if used + count > maximum:
        raise ValueError('Field scalar budget exceeded before subset request')
    return count


def subset_query(it, iy0, iy1, ix0, ix1):
    suffix = f'[{it}][0:1:99][{iy0}:1:{iy1}][{ix0}:1:{ix1}]'
    return ','.join(name + suffix for name in FIELDS)


def fetch(url, maximum):
    with urllib.request.urlopen(url, timeout=55) as response:
        raw = response.read(maximum + 1)
    if len(raw) > maximum or not raw.startswith((b'CDF', b'\x89HDF')):
        raise ValueError('Source response is not bounded NetCDF')
    return raw


def clean(values):
    return [float(v) if math.isfinite(float(v)) else None for v in values]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    op = json.loads((ROOT / OPERATOR).read_bytes())
    for path, pin in op['input_sha256'].items():
        if sha(ROOT / path) != pin:
            raise ValueError('Frozen dependency changed: ' + path)
    OUT.mkdir(exist_ok=True)
    records = {s['id']: [] for s in op['sections']}
    sources = []
    scalar_count = 0
    wire_bytes = 0
    for kind, base in op['datasets'].items():
        with netCDF4.Dataset(base) as remote:
            if (len(remote.dimensions['depth']) != 100 or len(remote.dimensions['latitude']) != 161
                    or len(remote.dimensions['longitude']) != 161 or not source_doi_matches(remote.doi)
                    or remote.product_version != op['expected_product_versions'][kind]):
                raise ValueError('Published product version or grid changed')
            z = clean(remote['depth'][:])
            lat = np.asarray(remote['latitude'][:]);lon = np.asarray(remote['longitude'][:])
            times = netCDF4.num2date(remote['time'][:], remote['time'].units, calendar=remote['time'].calendar)
            if z != list(range(10, 1001, 10)) or remote['depth'].units != 'm' or remote['depth'].positive != 'down':
                raise ValueError('Source depth frame changed')
            if len(times) != (1 if kind == 'mean' else 365):
                raise ValueError('Source mean or365-phase time axis changed')
            phases = [(None, 0)] if kind == 'mean' else phase_indices(times)
            sources.append({'kind': kind, 'opendap_url': base,
                            'global_attributes': {k: str(remote.getncattr(k)) for k in remote.ncattrs()},
                            'variable_attributes': {name: {k: str(remote[name].getncattr(k)) for k in remote[name].ncattrs()} for name in ['time', 'depth', *FIELDS]}})
        for section in op['sections']:
            axis, fixed = section['fixed_axis'], section['fixed_coordinate']
            fixed_values = lat if axis == 'latitude' else lon
            varying = lon if axis == 'latitude' else lat
            fi = int(np.argmin(abs(fixed_values - fixed)))
            vi = np.flatnonzero((varying >= section['varying_gate'][0] - 1e-4) & (varying <= section['varying_gate'][1] + 1e-4))
            if abs(float(fixed_values[fi]) - fixed) > 1e-4 or not len(vi):
                raise ValueError('Prescribed source-grid section missing')
            if axis == 'latitude':
                iy0 = iy1 = fi;ix0, ix1 = int(vi[0]), int(vi[-1])
            else:
                ix0 = ix1 = fi;iy0, iy1 = int(vi[0]), int(vi[-1])
            for month, it in phases:
                scalar_count += check_budget(len(z), iy1-iy0+1, ix1-ix0+1, scalar_count, op['maximum_field_scalars'])
                url = base + '.nc?' + urllib.parse.quote(subset_query(it, iy0, iy1, ix0, ix1), safe=',')
                remaining = op['maximum_total_subset_response_bytes'] - wire_bytes
                if remaining <= 0:
                    raise ValueError('Total subset byte budget exhausted before request')
                raw = fetch(url, min(op['maximum_subset_response_bytes'], remaining))
                wire_bytes += len(raw)
                if wire_bytes > op['maximum_total_subset_response_bytes']:
                    raise ValueError('Total subset byte cap exceeded')
                with netCDF4.Dataset('section.nc', memory=raw) as ds:
                    returned_time = netCDF4.num2date(ds['time'][0], ds['time'].units, calendar=ds['time'].calendar)
                    if (returned_time.strftime('%Y-%m-%dT%H:%M:%SZ') != times[it].strftime('%Y-%m-%dT%H:%M:%SZ')
                            or clean(ds['depth'][:]) != z
                            or not np.allclose(ds['latitude'][:], lat[iy0:iy1+1], rtol=0, atol=1e-5)
                            or not np.allclose(ds['longitude'][:], lon[ix0:ix1+1], rtol=0, atol=1e-5)):
                        raise ValueError('Subset source time or coordinate selection changed')
                    for name in FIELDS:
                        if ds[name].dimensions != ('time', 'depth', 'latitude', 'longitude'):
                            raise ValueError('Subset dimensions changed')
                    if any(ds[name].units != 'm s-1' for name in VELOCITY):
                        raise ValueError('Source velocity/uncertainty units changed')
                    if ds['downstream_direction'].units != 'degrees' or 'clockwise from north' not in ds['downstream_direction'].long_name:
                        raise ValueError('Source reference direction convention changed')
                    decoded = {name: np.ma.filled(ds[name][0], np.nan).reshape(100, -1) for name in FIELDS}
                    candidates = []
                    for j, value in enumerate(varying[vi]):
                        point = [float(value), float(fixed_values[fi])] if axis == 'latitude' else [float(fixed_values[fi]), float(value)]
                        candidates.append({'source_lon_lat': point,
                                           'source_values': {name: clean(decoded[name][:, j]) for name in VELOCITY},
                                           'source_fit_support': {name: clean(decoded[name][:, j]) for name in SUPPORT}})
                selected, audit = select_axis(z, candidates)
                profile = None
                if selected is not None:
                    profile = candidates[selected]
                    values = profile['source_values']
                    if any(v is not None and abs(v) > 5 for n in VELOCITY[:2] for v in values[n]):
                        raise ValueError('Unexpected source velocity scaling')
                    if any(v is not None and v < 0 for n in VELOCITY[2:] for v in values[n]):
                        raise ValueError('Negative provider velocity uncertainty')
                    direction = audit[selected]['reference_direction_at100m_degrees_clockwise_from_north']
                    along = [project(u, v, direction) for u, v in zip(values['eastward_velocity'], values['northward_velocity'])]
                    layers, half = diagnose(z, along, op['thresholds_m_s'])
                    profile.update(locked_reference_direction_at100m_degrees=direction,
                                   along_locked_mean_direction_m_s=along,
                                   absolute_component_threshold_layers=layers,
                                   half_sampled_core_component_decay=half)
                row = {'section_id': section['id'], 'source_product_kind': kind, 'calendar_month_phase': month,
                       'actual_provider_phase_timestamp_utc': times[it].strftime('%Y-%m-%dT%H:%M:%SZ'),
                       'nominal_phase_calendar_date': nominal_phase_date(times[it]).strftime('%Y-%m-%d') if month is not None else None,
                       'timestamp_is_instantaneous_observation_date': False, 'source_time_index': it,
                       'depth_levels_m': z, 'section_definition': section,
                       'source_grid_indices_inclusive': {'latitude': [iy0, iy1], 'longitude': [ix0, ix1]},
                       'axis_candidate_audit': audit, 'selected_section_column_index': selected,
                       'horizontal_selection_status': 'no_qualifying_column' if selected is None else ('edge_maximum_axis_unresolved' if selected in [0, len(candidates)-1] else 'interior_fitted_section_maximum_not_independently_validated_axis'),
                       'selected_profile': profile, 'subset_url': url, 'subset_response_bytes': len(raw),
                       'subset_response_sha256': hashlib.sha256(raw).hexdigest(), 'whole_current_representative': False}
                records[section['id']].append(row)
                (OUT / ('checkpoint-' + section['id'] + '.json')).write_text(json.dumps({
                    'status': 'PARTIAL_FITTED_SECTION_COLLECTION', 'records': records[section['id']],
                    'full_goal_complete': False}, indent=2, allow_nan=False) + '\n', encoding='utf8')
                print(json.dumps({'section': section['id'], 'kind': kind, 'month_phase': month,
                                  'node': profile['source_lon_lat'] if profile else None,
                                  'lower_threshold_depths_m': [r['lower_depth_m'] for r in layers] if profile else None,
                                  'half_core_depth_m': half['lower_depth_m'] if profile and half else None}), flush=True)
    pins = dict(op['input_sha256'], **{OPERATOR: sha(ROOT / OPERATOR),
        'analysis/acquire_gulf_stream_spray_sections_v1.py': sha(Path(__file__))})
    files = []
    for section in op['sections']:
        rows = records[section['id']]
        counts = {'fitted_profiles': len(rows), 'profiles_with_selected_column': sum(r['selected_profile'] is not None for r in rows),
                  'edge_selected_profiles': sum(r['horizontal_selection_status'] == 'edge_maximum_axis_unresolved' for r in rows),
                  'resolved_lower_depths_by_threshold': {str(t): sum(r['selected_profile'] is not None and r['selected_profile']['absolute_component_threshold_layers'][i]['lower_depth_m'] is not None for r in rows) for i, t in enumerate(op['thresholds_m_s'])},
                  'resolved_half_core_depths': sum(r['selected_profile'] is not None and r['selected_profile']['half_sampled_core_component_decay'] is not None and r['selected_profile']['half_sampled_core_component_decay']['lower_depth_m'] is not None for r in rows),
                  'whole_route_physical_depth_profiles': 0, 'water_volume_estimates': 0}
        result = {'schema': 'osw.gulf-stream-spray-depth-section.v1',
                  'status': 'FITTED_REGIONAL_SECTION_DEPTHS_WITH_LOCKED100M_MEAN_FLOW_FRAME',
                  'entity_context': 'current:gulf-stream', 'section_definition': section,
                  'records': rows, 'counts': counts, 'input_sha256': pins,
                  'source_metadata': sources, 'eligibility': op['eligibility'], 'uncertainty_m': None,
                  'full_goal_complete': False}
        name = section['id'] + '.json'
        (OUT / name).write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf8')
        if (OUT / name).stat().st_size >= 2500000:
            raise ValueError('Retained section exceeds fixed per-file publication cap')
        files.append({'file': name, 'bytes': (OUT / name).stat().st_size, 'sha256': sha(OUT / name), 'counts': counts})
    manifest = {'schema': 'osw.gulf-stream-spray-depth-sections-manifest.v1',
                'counts': {'sections': len(files), 'fitted_profiles': sum(r['counts']['fitted_profiles'] for r in files),
                           'decoded_field_scalars_retrieved': scalar_count, 'subset_response_bytes': wire_bytes,
                           'whole_route_physical_depth_profiles': 0, 'water_volume_estimates': 0},
                'sections': files, 'input_sha256': pins, 'full_goal_complete': False}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2, allow_nan=False) + '\n', encoding='utf8')
    print(json.dumps(manifest['counts']))


if __name__ == '__main__':
    main()
