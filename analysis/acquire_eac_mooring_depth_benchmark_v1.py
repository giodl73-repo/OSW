"""Cloud-only bounded, unfilled daily IMOS EAC mooring profiles from NOAA."""
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import netCDF4
import numpy as np
from pyproj import Geod
from derive_eac_connected_layer_thickness_v1 import connected_layer

ROOT = Path(__file__).resolve().parents[1]
OPERATOR = 'research/eac-mooring-depth-benchmark-operator-v1.json'
OUT = Path('eac-mooring-depth-benchmark-v1')
FIELDS = ('UCUR', 'VCUR', 'UCUR_uncertainty', 'VCUR_uncertainty')
GEOD = Geod(ellps='WGS84')


def day_index(times, day):
    matches = [i for i, t in enumerate(times) if t.strftime('%Y-%m-%d') == day]
    if len(matches) != 1:
        raise ValueError('Exactly one source daily timestamp per requested date required')
    return matches[0]


def check_budget(time_count, depth_count, used, maximum):
    if not 1 <= time_count <= 4000 or not 2 <= depth_count <= 500:
        raise ValueError('Source coordinate axes exceed declared bounded daily experiment')
    values = 2 * depth_count * len(FIELDS)
    if used + values > maximum:
        raise ValueError('Velocity scalar budget exceeded before retrieval')
    return values


def clean(values):
    return [float(x) if math.isfinite(float(x)) else None for x in values]


def diagnose(z, v, thresholds):
    south = [-x if x is not None else None for x in v]
    rows = [connected_layer(z, south, t) for t in thresholds]
    for row in rows:
        if row['status'] == 'resolved_connected_model_threshold_layer':
            row['status'] = 'resolved_connected_processed_observation_threshold_layer'
    return south, rows


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    op = json.loads((ROOT / OPERATOR).read_bytes())
    for p, pin in op['input_sha256'].items():
        if sha(ROOT / p) != pin:
            raise ValueError('Frozen input changed: ' + p)
    pilot = json.loads((ROOT / op['model_pilot_file']).read_bytes())
    model = {r['snapshot_time_utc'][:10]: r for r in pilot['samples'] if r['route_vertex_index'] == 4}
    OUT.mkdir(exist_ok=True)
    rows = []
    sources = []
    used = 0
    for station in op['station_codes']:
        url = op['opendap_base'] + 'OS_IMOS-EAC_' + station + '-20120401-20220727_DPR_T1D.nc'
        with netCDF4.Dataset(url) as ds:
            ntime, nz = len(ds.dimensions['TIME']), len(ds.dimensions['DEPTH'])
            increment = check_budget(ntime, nz, used, op['maximum_velocity_scalars'])
            if (ds['DEPTH'].units != 'm' or ds['DEPTH'].positive != 'down'
                    or ds['DEPTH'].reference_datum != 'sea surface'):
                raise ValueError('Source depth datum or units changed')
            for name, standard in [('UCUR', 'eastward_sea_water_velocity'), ('VCUR', 'northward_sea_water_velocity')]:
                if ds[name].standard_name != standard or ds[name].units != 'm s-1':
                    raise ValueError('Source velocity units or direction changed')
            for name in FIELDS:
                if ds[name].dimensions != ('TIME', 'DEPTH') or ds[name].units != 'm s-1':
                    raise ValueError('Source component/uncertainty axes or units changed')
            times = netCDF4.num2date(ds['TIME'][:], ds['TIME'].units, calendar=getattr(ds['TIME'], 'calendar', 'gregorian'))
            z = clean(ds['DEPTH'][:])
            lon, lat = float(ds['LONGITUDE'][...]), float(ds['LATITUDE'][...])
            if not 153 <= lon <= 156 or not -27.5 <= lat <= -26.9:
                raise ValueError('Mooring outside independently documented array region')
            attrs = {k: str(ds.getncattr(k)) for k in ds.ncattrs()}
            sources.append({'station': station, 'opendap_url': url, 'global_attributes': attrs,
                            'variable_attributes': {name: {k: str(ds[name].getncattr(k)) for k in ds[name].ncattrs()}
                                                    for name in ['TIME', 'DEPTH', *FIELDS]},
                            'time_axis_count': ntime, 'depth_axis_count': nz})
            used += increment
            for day in op['source_dates']:
                it = day_index(times, day)
                values = {name: clean(np.ma.filled(ds[name][it, :], np.nan)) for name in FIELDS}
                if any(x is not None and abs(x) > 10 for name in ['UCUR', 'VCUR'] for x in values[name]):
                    raise ValueError('Unexpected source velocity scaling or magnitude')
                if any(x is not None and x < 0 for name in ['UCUR_uncertainty', 'VCUR_uncertainty'] for x in values[name]):
                    raise ValueError('Negative source velocity uncertainty')
                south, layers = diagnose(z, values['VCUR'], op['thresholds_m_s'])
                near = min(enumerate(model[day]['sampled_profiles']),
                           key=lambda pair: GEOD.inv(lon, lat, *pair[1]['sampled_lon_lat'])[2])
                distance = GEOD.inv(lon, lat, *near[1]['sampled_lon_lat'])[2] / 1000
                row = {'station': station, 'source_date': day,
                       'actual_source_time_utc': times[it].strftime('%Y-%m-%dT%H:%M:%SZ'),
                       'source_time_index': it, 'lon_lat': [lon, lat], 'depth_levels_m': z,
                       'source_values': values, 'poleward_meridional_velocity_m_s': south,
                       'threshold_layers': layers,
                       'finite_velocity_depth_levels': sum(x is not None for x in values['VCUR']),
                       'nearest_existing_model_offset_index': near[0],
                       'nearest_existing_model_node_lon_lat': near[1]['sampled_lon_lat'],
                       'nearest_existing_model_node_distance_km': distance,
                       'model_observation_colocation_or_identity_validated': False}
                rows.append(row)
                print(json.dumps({'station': station, 'date': day,
                                  'finite_velocity_depth_levels': row['finite_velocity_depth_levels'],
                                  'lower_crossings': [r['lower_depth_m'] for r in layers],
                                  'thicknesses': [r['layer_thickness_m'] for r in layers]}), flush=True)
    result = {'schema': 'osw.eac-mooring-depth-benchmark.v1',
              'status': 'UNFILLED_PROCESSED_MOORING_PROFILES_REGIONAL_IDENTITY_REVIEW',
              'source_metadata': sources, 'samples': rows,
              'input_sha256': dict(op['input_sha256'], **{OPERATOR: sha(ROOT / OPERATOR),
                  'analysis/acquire_eac_mooring_depth_benchmark_v1.py': sha(Path(__file__))}),
              'counts': {'stations': len(sources), 'dates': len(op['source_dates']),
                         'profiles': len(rows), 'velocity_scalars_retrieved': used,
                         'profiles_with_any_velocity': sum(r['finite_velocity_depth_levels'] > 0 for r in rows),
                         'resolved_lower_boundaries_by_threshold': {
                             str(t): sum(r['threshold_layers'][i]['lower_depth_m'] is not None for r in rows)
                             for i, t in enumerate(op['thresholds_m_s'])},
                         'resolved_layer_thicknesses_by_threshold': {
                             str(t): sum(r['threshold_layers'][i]['layer_thickness_m'] is not None for r in rows)
                             for i, t in enumerate(op['thresholds_m_s'])},
                         'whole_route_physical_depth_profiles': 0, 'water_volume_estimates': 0},
              'source_license': 'CC-BY-4.0', 'source_attribution': op['source_attribution'],
              'uncertainty_m': None, 'eligibility': op['eligibility'],
              'wire_byte_hash_or_complete_source_hash_claimed': False, 'full_goal_complete': False}
    (OUT / 'candidate.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf8')
    print(json.dumps(result['counts']))


if __name__ == '__main__':
    main()
