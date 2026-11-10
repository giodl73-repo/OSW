"""Conditional daily-before-monthly thermodynamics from retained genuine originals."""
import json
import shutil
from pathlib import Path
import tempfile

import numpy as np

from acquire_indian_secc_hycom_2013 import coordinates, pin
from acquire_south_indian_front_levels import ROOT, BASE, FIELDS, common_means, validate_response
from south_indian_front_level_preflight import checked, DECLARATION
from package_south_indian_front_levels import DESTINATION
from south_indian_front_temperature import daily, monthly, VERSION
from package_indian_secc_hycom_2013 import unpack_checked

OPERATOR = 'analysis/build_south_indian_front_temperature.py'
REPORT = 'research/south-indian-2013-front-level-potential-temperature.json'
THETA = 'potential_temperature_0_dbar_assuming_ITS90_c'


def converted_month(grids, expected_times, raw_month, depth, lat, lon, scale, offsets):
    if not grids:
        raise ValueError('Missing entire source month')
    times = np.concatenate([g['time'] for g in grids])
    if not np.array_equal(times, expected_times) or raw_month['sample_days'] != len(times):
        raise ValueError('Changed complete daily source cohort')
    fields = {n: np.concatenate([g[n] for g in grids]) for n in FIELDS}
    minimum = raw_month['minimum_common_samples']
    counts, raw_means = common_means(fields, minimum, scale, offsets)
    if not np.array_equal(counts, np.asarray(raw_month['common_samples'])):
        raise ValueError('Changed raw common-valid counts')
    for name in FIELDS:
        expected = np.asarray(raw_month['fields'][name], dtype=float)
        if not np.array_equal(raw_means[name], expected, equal_nan=True):
            raise ValueError('Raw monthly mean differs from genuine daily source: '+name)
    result = daily(fields, depth, lat, lon, scale, offsets)
    derived_counts, theta = monthly(result, minimum)
    if not np.array_equal(counts, derived_counts):
        raise ValueError('Thermodynamic conversion changed raw common support')
    mask = result['common_mask']
    absolute = np.full(counts.shape, np.nan, dtype='<f8')
    np.divide(np.where(mask, result['absolute_salinity_g_kg'], 0).sum(axis=0, dtype=np.float64),
              counts, out=absolute, where=counts >= minimum)
    return {'common_samples': counts, THETA: theta, 'absolute_salinity_g_kg': absolute,
            'sea_pressure_dbar': result['sea_pressure_dbar'][0]}


def nullable(array):
    result = np.asarray(array).astype(object)
    result[~np.isfinite(array)] = None
    return result.tolist()


def build(source=DESTINATION):
    source = Path(source)
    if shutil.disk_usage(ROOT).free < 1024**3:
        raise ValueError('Need1GiB free before derived thermodynamic compilation')
    manifest = json.loads((source/'acquisition.json').read_bytes())
    if (manifest.get('schema') != 'osw.south-indian-front-level-retained-source.v1'
            or manifest.get('source_model_year') != 2013 or manifest.get('native_depths_m') != [100,200]):
        raise ValueError('Changed supplementary source identity')
    inputs = {(source/'acquisition.json').relative_to(ROOT).as_posix(): pin(source/'acquisition.json')['sha256']}
    for name, expected in manifest['files'].items():
        if pin(source/name) != expected: raise ValueError('Changed source product: '+name)
        inputs[(source/name).relative_to(ROOT).as_posix()] = expected['sha256']
    for name, expected in manifest['dependencies'].items():
        if pin(ROOT/name) != expected: raise ValueError('Changed source dependency: '+name)
        inputs[name] = expected['sha256']
    plan = json.loads((source/'selection.json').read_bytes())
    raw = json.loads((source/'monthly-fields.json').read_bytes())
    c = coordinates((source/'coordinates.ascii').read_text(encoding='utf8'))
    depth, lat, lon = [c[n][plan['selection'][n]] for n in ['depth', 'lat', 'lon']]
    if (raw.get('schema') != 'osw.south-indian-hycom-front-level-monthly.v1'
            or raw.get('dataset_url') != BASE or raw.get('source_model_year') != 2013
            or raw.get('selection') != pin(source/'selection.json')
            or raw.get('units') != {n:v[1] for n,v in FIELDS.items()}
            or [m['month'] for m in raw['months']] != list(range(1,13))
            or any(raw.get(k) is not False for k in ['current_association_verified',
                'physical_width_admitted','physical_axis_admitted','seasonal_footprint_admitted'])):
        raise ValueError('Changed source frame, month order, units or admission')
    with np.load(source/'monthly.npz', allow_pickle=False) as arrays:
        for name in FIELDS:
            np.testing.assert_array_equal(np.asarray([m['fields'][name] for m in raw['months']],dtype=float), arrays[name])
        for key, name, expected in [('depth_m','depth',depth), ('latitude_degrees_north','lat',lat),
                                    ('longitude_degrees_east','lon',lon)]:
            np.testing.assert_array_equal(raw[key], expected)
            np.testing.assert_array_equal(arrays[name], expected)
        np.testing.assert_array_equal(arrays['common_samples'], [m['common_samples'] for m in raw['months']])
        np.testing.assert_array_equal(arrays['month'], range(1,13))
    if any(m['minimum_common_samples'] != plan['minimum_pairs'][m['month']-1] for m in raw['months']):
        raise ValueError('Changed calendar eligibility')
    months = []; pressure = None
    (ROOT/'.pytest_cache').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as temporary:
        working = Path(temporary)
        unpack_checked(source/'source-responses.zip', manifest['archive_members'], working)
        checked(working)
        for m in raw['months']:
            requests = [r for r in plan['requests'] if r['month'] == m['month']]
            grids = []
            for request in requests:
                path = working/request['file']
                receipt = json.loads(path.with_suffix('.receipt.json').read_bytes())
                if receipt['url'] != request['url'] or receipt['pin'] != pin(path):
                    raise ValueError('Changed daily source response/receipt')
                grids.append(validate_response(path.read_bytes(), request, plan, working))
            expected = c['time'][[i for r in requests for i in r['time_indices']]]
            out = converted_month(grids, expected, m, depth, lat, lon, plan['scale'], plan['offsets'])
            if pressure is None: pressure = out['sea_pressure_dbar']
            elif not np.array_equal(pressure, out['sea_pressure_dbar']):
                raise ValueError('Static pressure approximation changed between months')
            months.append({'month': m['month'], 'sample_days': m['sample_days'],
                           'minimum_common_samples': m['minimum_common_samples'],
                           'common_samples': out['common_samples'].tolist(),
                           'fields': {n: nullable(out[n]) for n in [THETA, 'absolute_salinity_g_kg']}})
        checked(working)
    for path in [OPERATOR, 'analysis/south_indian_front_temperature.py', DECLARATION,
                 'research/source-data/south-indian-front-temperature-conformance/reference.json',
                 'research/source-data/south-indian-front-temperature-conformance/synthetic.npz']:
        inputs[path] = pin(ROOT/path)['sha256']
    return {'schema': 'osw.south-indian-front-temperature-monthly.v1',
            'role': 'conditional model thermodynamic context; no named-front or current classification',
            'investigation_current_id': 'south-indian', 'source_model_year': 2013,
            'source_file': (source/'monthly-fields.json').relative_to(ROOT).as_posix(),
            'source_manifest': pin(source/'acquisition.json'),
            'dependencies': inputs, 'gsw_version': VERSION,
            'depth_m': depth.tolist(), 'latitude_degrees_north': lat.tolist(),
            'longitude_degrees_east': lon.tolist(), 'sea_pressure_dbar': nullable(pressure),
            'months': months,
            'units': {THETA: 'degC; potential temperature referenced to0dbar, assuming ITS-90',
                      'absolute_salinity_g_kg': 'g/kg; derived from model Practical Salinity'},
            'temperature_scale_verified': False, 'temperature_scale_assumption': 'ITS-90',
            'pressure_reference': 'GSW p_from_z(-native_depth,latitude,0,0); zero dynamic height and surface geopotential approximations, not observed pressure or SSH',
            'averaging': 'Convert each daily common-valid pair, then mean on unchanged raw four-field daily cohort; no conversion of monthly mean inputs.',
            'source_in_situ_temperature_replaced': False, 'front_criteria_applied': False,
            'current_association_verified': False, 'physical_width_admitted': False,
            'physical_axis_admitted': False, 'physical_length_admitted': False,
            'annual_extrema_admitted': False, 'seasonal_footprint_admitted': False}


if __name__ == '__main__':
    document = build()
    output = ROOT/REPORT
    raw = (json.dumps(document, indent=2, allow_nan=False)+'\n').encode()
    if output.exists() and output.read_bytes() != raw:
        raise ValueError('Existing derived report differs; inspect/version the method rather than overwrite')
    output.write_bytes(raw)
    print(REPORT)
