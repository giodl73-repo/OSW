"""All paired gradient/velocity candidates, without named-current admission."""
import argparse
import json
from pathlib import Path

import numpy as np
from wgs84_decimal_meridian import meridian_km

from acquire_indian_secc_hycom_2013 import pin
from acquire_eac_100m_source import write_json
from acquire_south_indian_hycom_hydrography import FIELDS
from package_south_indian_hycom_hydrography import DESTINATION, ROOT

PROTOCOL = 'plans/south-indian-paired-profile-diagnostic-protocol-v2.md'
PREFLIGHT = 'research/south-indian-paired-profile-diagnostic-preflight-v2.json'
REPORT = 'research/south-indian-hycom-2013-paired-profile-candidates-v2.json'


def positive_maxima(values):
    """Whole equal-valued plateaus; missing/domain flanks remain censored."""
    values = np.asarray(values, dtype=float)
    events = []
    i = 0
    while i < len(values):
        if not np.isfinite(values[i]) or values[i] <= 0:
            i += 1
            continue
        end = i
        while end+1 < len(values) and values[end+1] == values[i]:
            end += 1
        sides = []
        maximum = True
        for side, j in [('south', i-1), ('north', end+1)]:
            if j < 0 or j >= len(values):
                sides.append({'side': side, 'status': 'domain_end'})
            elif not np.isfinite(values[j]):
                sides.append({'side': side, 'status': 'missing_neighbor'})
            else:
                sides.append({'side': side, 'status': 'finite', 'value': float(values[j])})
                maximum &= values[i] > values[j]
        if maximum:
            events.append({'start_index': i, 'end_index': end, 'value': float(values[i]),
                           'flanks': sides, 'both_flanks_finite': all(s['status'] == 'finite' for s in sides)})
        i = end+1
    return events


def adjacent_gradients(latitudes, longitude, fields):
    latitude = np.asarray(latitudes, dtype=float)
    if len(latitude) < 2 or not np.isfinite(latitude).all() or not np.all(np.diff(latitude) > 0):
        raise ValueError('Latitude must be finite and strictly increasing')
    if not np.isfinite(longitude):
        raise ValueError('Invalid longitude')
    distances = np.asarray([meridian_km(a,b) for a,b in zip(latitude[:-1],latitude[1:])])
    if not np.all(np.isfinite(distances) & (distances > 0)):
        raise ValueError('Invalid native geodesic separation')
    gradients = {}
    for name in FIELDS:
        values = np.asarray(fields[name], dtype=float)
        if values.shape != latitude.shape or np.isinf(values).any():
            raise ValueError('Invalid profile field shape/value')
        gradients[name] = np.diff(values)/distances
    return distances, gradients


def support_distance(longitude, a, b):
    """Distance between closed latitude supports, not their drawn midpoints."""
    if max(a[0], b[0]) <= min(a[1], b[1]):
        return 0.
    left, right = (a[1], b[0]) if a[1] < b[0] else (b[1], a[0])
    return meridian_km(left,right)


def profile(latitudes, longitude, fields):
    latitude = np.asarray(latitudes, dtype=float)
    spacing, gradients = adjacent_gradients(latitude, longitude, fields)
    salinity = positive_maxima(gradients['salinity'])
    for i, event in enumerate(salinity):
        event.update(id=f'salinity-gradient-{i}', latitude_bracket_degrees_north=[
            float(latitude[event['start_index']]), float(latitude[event['end_index']+1])])
    eastward = positive_maxima(fields['water_u'])
    for i, event in enumerate(eastward):
        indices = list(range(event['start_index'], event['end_index']+1))
        support = [float(latitude[indices[0]]), float(latitude[indices[-1]])]
        distances = [support_distance(longitude, support, s['latitude_bracket_degrees_north']) for s in salinity]
        event.update(id=f'eastward-peak-{i}', latitude_support_degrees_north=support,
                     native_values={name: [float(fields[name][j]) if np.isfinite(fields[name][j]) else None for j in indices] for name in FIELDS},
                     closest_positive_salinity_gradient_ids=[s['id'] for s,d in zip(salinity,distances) if d <= min(distances)+1e-9] if distances else [],
                     closest_gradient_support_distance_km=min(distances) if distances else None,
                     current_association_verified=False, physical_width_admitted=False)
    def nullable(values):
        return [float(v) if np.isfinite(v) else None for v in values]
    return {'adjacent_separation_km': spacing.tolist(),
            'adjacent_gradients_per_km': {name: nullable(v) for name,v in gradients.items()},
            'positive_salinity_gradient_maxima': salinity,
            'positive_eastward_velocity_maxima': eastward}


def build(directory=DESTINATION):
    directory = Path(directory)
    declared = json.loads((ROOT/PREFLIGHT).read_bytes())
    runtime = {'numpy': np.__version__, 'distance': 'WGS84 Decimal70 meridian series16 trig70'}
    if runtime != declared['numeric_runtime']:
        raise ValueError('Diagnostic numeric runtime differs from declaration')
    for name, expected in declared['dependencies'].items():
        if pin(ROOT/name) != expected:
            raise ValueError('Changed frozen diagnostic dependency: '+name)
    manifest = json.loads((directory/'acquisition.json').read_bytes())
    for name in ['selection.json', 'monthly.npz', 'quality.json']:
        if pin(directory/name) != manifest['files'][name]:
            raise ValueError('Changed source product: '+name)
    if pin(directory/'selection.json') != declared['source_selection']:
        raise ValueError('Diagnostic source selection differs')
    with np.load(directory/'monthly.npz', allow_pickle=False) as source:
        arrays = {name: source[name] for name in source.files}
    if arrays['month'].tolist() != list(range(1,13)) or arrays['depth'].tolist() != [15,1000]:
        raise ValueError('Unexpected time/depth support')
    cases = []
    for mi in range(12):
        for zi, depth in enumerate(arrays['depth']):
            for xi, lon in enumerate(arrays['lon']):
                fields = {name: arrays[name][mi,zi,:,xi] for name in FIELDS}
                cases.append({'id': f'm{mi+1:02d}-z{zi}-x{xi}', 'month':mi+1,
                              'depth_m':float(depth), 'longitude_degrees_east':float(lon),
                              'near_surface': bool(depth == 15),
                              'common_samples':arrays['common_samples'][mi,zi,:,xi].tolist(),
                              **profile(arrays['lat'],float(lon),fields)})
    return {'schema':'osw.south-indian-paired-profile-candidates.v2',
            'status':'exploratory_model_candidates_not_named_current_measurements',
            'current_id':'south-indian', 'model_year':2013,
            'numeric_runtime':runtime,
            'supersedes':declared['supersedes'],
            'dependencies':{PREFLIGHT:pin(ROOT/PREFLIGHT), **declared['dependencies']},
            'source_manifest':pin(directory/'acquisition.json'),
            'source_products':{name:pin(directory/name) for name in ['selection.json','quality.json','monthly.npz']},
            'latitude_degrees_north':arrays['lat'].tolist(),
            'gradient_units':{name:values[1]+'/km' for name,values in FIELDS.items()},
            'gradient_method':'Adjacent monthly means divided by native WGS84 meridional separation; not a mean of daily gradients.',
            'cases':cases, 'current_association_verified':False,
            'physical_width_admitted':False, 'physical_axis_admitted':False,
            'physical_length_admitted':False,'annual_extrema_admitted':False}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory',type=Path,default=DESTINATION)
    parser.add_argument('--output',type=Path,default=ROOT/REPORT)
    args=parser.parse_args()
    report=build(args.directory)
    write_json(args.output,report)
    print(json.dumps({'output':str(args.output.relative_to(ROOT)),'cases':len(report['cases'])}))
