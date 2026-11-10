"""Cloud-only second-product surface screen at frozen EAC pilot targets."""
import hashlib
import json
import math
from pathlib import Path
import netCDF4
import numpy as np
from pyproj import Geod

ROOT = Path(__file__).resolve().parents[1]
OPERATOR = 'research/eac-surface-route-screen-operator-v1.json'
OUT = Path('eac-surface-route-screen-v1')
FIELDS = ('UCUR', 'VCUR', 'UCUR_MEAN', 'VCUR_MEAN', 'GSL')
GEOD = Geod(ellps='WGS84')


def along(u, v, bearing):
    if u is None or v is None:
        return None
    return u * math.sin(math.radians(bearing)) + v * math.cos(math.radians(bearing))


def screen(profiles, selected, threshold):
    if selected is not None and (type(selected) is not int or not 0 <= selected < len(profiles)):
        raise ValueError('Frozen model node index invalid')
    candidates = [i for i, p in enumerate(profiles) if p['along_total_m_s'] is not None
                  and p['along_total_m_s'] > threshold]
    peak = max(candidates, key=lambda i: profiles[i]['along_total_m_s']) if candidates else None
    component = profiles[selected]['along_total_m_s'] if selected is not None else None
    if component is None:
        status = 'no_surface_support_at_frozen_model_node'
    elif component > threshold:
        status = 'poleward_surface_component_supported_not_current_identity'
    else:
        status = 'poleward_surface_component_not_corroborated_not_current_absence'
    return {'frozen_model_selected_profile_index': selected, 'status': status,
            'surface_component_at_frozen_model_node_m_s': component,
            'sampled_surface_peak_index': peak,
            'sampled_surface_peak_at_window_edge': peak in [0, len(profiles) - 1] if peak is not None else None,
            'unique_surface_grid_nodes': len({tuple(p['source_grid_index']) for p in profiles}),
            'named_current_axis_validated': False, 'physical_depth_validated': False}


def check_budget(ny, nx, used, maximum):
    if type(ny) is not int or type(nx) is not int or min(ny, nx) < 1 or ny * nx > 500:
        raise ValueError('Bounded patch required before field retrieval')
    values = ny * nx * len(FIELDS)
    if used + values > maximum:
        raise ValueError('Cumulative scalar budget exceeded before field retrieval')
    return values


def finite(value):
    return float(value) if math.isfinite(float(value)) else None


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    op = json.loads((ROOT / OPERATOR).read_bytes())
    for p, pin in op['input_sha256'].items():
        if sha(ROOT / p) != pin:
            raise ValueError('Frozen input changed: ' + p)
    pilot = json.loads((ROOT / op['pilot_file']).read_bytes())
    rows = []
    sources = []
    used = 0
    for day, url in op['source_datasets'].items():
        with netCDF4.Dataset(url) as ds:
            if len(ds.dimensions['TIME']) != 1 or len(ds.dimensions['LATITUDE']) > 400 or len(ds.dimensions['LONGITUDE']) > 700:
                raise ValueError('Unexpected source coordinate axis sizes')
            time = netCDF4.num2date(ds['TIME'][0], ds['TIME'].units, calendar=ds['TIME'].calendar).strftime('%Y-%m-%dT%H:%M:%SZ')
            if time != day + 'T00:00:00Z' or ds.product_type != 'DM03':
                raise ValueError('Wrong source date or delayed-mode version')
            for name in FIELDS:
                if ds[name].dimensions != ('TIME', 'LATITUDE', 'LONGITUDE') or ds[name].units != ('m' if name == 'GSL' else 'm/s'):
                    raise ValueError('Source axes or units changed')
            if ds['UCUR'].standard_name != 'surface_geostrophic_eastward_sea_water_velocity' or ds['VCUR'].standard_name != 'surface_geostrophic_northward_sea_water_velocity':
                raise ValueError('Source velocity frame changed')
            lats, lons = np.asarray(ds['LATITUDE'][:]), np.asarray(ds['LONGITUDE'][:])
            sources.append({'source_date': day, 'opendap_url': url, 'actual_time_utc': time,
                            'global_attributes': {k: str(ds.getncattr(k)) for k in ds.ncattrs()},
                            'variable_attributes': {n: {k: str(ds[n].getncattr(k)) for k in ds[n].ncattrs()} for n in FIELDS}})
            for sample in [r for r in pilot['samples'] if r['snapshot_time_utc'][:10] == day]:
                targets = [p['target_lon_lat'] for p in sample['sampled_profiles']]
                indices = [(int(np.argmin(abs(lats - lat))), int(np.argmin(abs(lons - lon)))) for lon, lat in targets]
                y0, y1 = min(i[0] for i in indices), max(i[0] for i in indices)
                x0, x1 = min(i[1] for i in indices), max(i[1] for i in indices)
                used += check_budget(y1 - y0 + 1, x1 - x0 + 1, used, op['maximum_field_scalars'])
                fields = {name: np.ma.filled(ds[name][0, y0:y1+1, x0:x1+1], np.nan) for name in FIELDS}
                profiles = []
                for target, (iy, ix) in zip(targets, indices):
                    point = [float(lons[ix]), float(lats[iy])]
                    distance = GEOD.inv(*target, *point)[2] / 1000
                    if distance > op['maximum_nearest_cell_distance_km']:
                        raise ValueError('Nearest cell beyond prescribed surface-grid tolerance')
                    values = {name: finite(field[iy-y0, ix-x0]) for name, field in fields.items()}
                    if any(v is not None and abs(v) > 10 for n, v in values.items() if n != 'GSL'):
                        raise ValueError('Unexpected velocity packing/scaling')
                    bearing = sample['downstream_reference_bearing_degrees_true']
                    profiles.append({'target_lon_lat': target, 'sampled_lon_lat': point, 'source_grid_index': [iy, ix],
                                     'nearest_cell_distance_km': distance, 'source_values': values,
                                     'along_total_m_s': along(values['UCUR'], values['VCUR'], bearing),
                                     'along_OFAM3_mean_m_s': along(values['UCUR_MEAN'], values['VCUR_MEAN'], bearing)})
                row = {'source_date': day, 'route_vertex_index': sample['route_vertex_index'],
                       'editorial_lon_lat': sample['editorial_lon_lat'],
                       'downstream_reference_bearing_degrees_true': sample['downstream_reference_bearing_degrees_true'],
                       'frozen_model_horizontal_selection_status': sample['horizontal_selection_status'],
                       'source_hyperslab_indices_inclusive': {'latitude': [y0, y1], 'longitude': [x0, x1]},
                       'profiles_at_frozen_targets': profiles,
                       'screen': screen(profiles, sample['selected_profile_index'], op['poleward_component_threshold_m_s'])}
                rows.append(row)
                print(json.dumps({'date': day, 'vertex': row['route_vertex_index'], 'screen': row['screen']}), flush=True)
    counts = {'surface_route_cases': len(rows), 'surface_target_samples': sum(len(r['profiles_at_frozen_targets']) for r in rows),
              'decoded_field_scalars_retrieved': used,
              'poleward_component_supported_at_model_node': sum(r['screen']['status'] == 'poleward_surface_component_supported_not_current_identity' for r in rows),
              'poleward_component_not_corroborated_at_model_node': sum(r['screen']['status'] == 'poleward_surface_component_not_corroborated_not_current_absence' for r in rows),
              'missing_surface_support_at_model_node': sum(r['screen']['status'] == 'no_surface_support_at_frozen_model_node' for r in rows),
              'named_current_axes_validated': 0, 'whole_route_physical_depth_profiles': 0}
    result = {'schema': 'osw.eac-surface-route-screen.v1', 'status': 'SECOND_PRODUCT_SURFACE_SUPPORT_NOT_AXIS_VALIDATION',
              'source_metadata': sources, 'samples': rows, 'counts': counts,
              'input_sha256': dict(op['input_sha256'], **{OPERATOR: sha(ROOT / OPERATOR),
                  'analysis/acquire_eac_surface_route_screen_v1.py': sha(Path(__file__))}),
              'statistically_independent_validation_claimed': False, 'wire_byte_hash_claimed': False,
              'eligibility': op['eligibility'], 'full_goal_complete': False}
    OUT.mkdir(exist_ok=True)
    (OUT / 'candidate.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf8')
    print(json.dumps(counts))


if __name__ == '__main__':
    main()
