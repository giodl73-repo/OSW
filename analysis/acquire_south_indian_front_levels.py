"""Supplementary frozen native 100m/200m HYCOM sections; no dimension admission."""
import argparse
import calendar
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
import shutil
from urllib.parse import quote
from urllib.request import urlopen

import numpy as np
from acquire_eac_100m_source import write_json
from acquire_indian_secc_hycom_2013 import coordinates, index_runs, pin, write_stored_npz

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://tds.hycom.org/thredds/dodsC/GLBv0.08/expt_53.X/data/2013'
METADATA = ROOT/'research/source-data/hycom-south-indian-hydrography-2013'
PROTOCOL = 'plans/south-indian-front-level-source-protocol-v1.md'
FIELDS = {'water_u': ('eastward_sea_water_velocity', 'm/s', 0),
          'water_v': ('northward_sea_water_velocity', 'm/s', 0),
          'water_temp': ('sea_water_temperature', 'degC', 20),
          'salinity': ('sea_water_salinity', 'psu', 20)}
LIMIT = 20_000_000


def check_metadata(text):
    for name, (standard, units, offset) in FIELDS.items():
        match = re.search(r'\b'+name+r' \{(.*?)\n    \}', text, re.S)
        if match is None:
            raise ValueError('Missing field metadata: '+name)
        for token in [f'String standard_name "{standard}";', f'String units "{units}";',
                      'Int16 _FillValue -30000;', 'Int16 missing_value -30000;',
                      'Float32 scale_factor 0.001;', f'Float32 add_offset {offset}.0;']:
            if token not in match[1]:
                raise ValueError('Changed field frame/packing/units: '+name)
        if name == 'water_temp' and 'String comment "in-situ temperature";' not in match[1]:
            raise ValueError('Unverified temperature convention')
    for token in ['String units "hours since 2000-01-01 00:00:00";', 'String calendar "gregorian";',
                  'String distribution_statement "Approved for public release. Distribution unlimited.";']:
        if token not in text:
            raise ValueError('Changed source clock/distribution')


def make_plan(directory):
    directory = Path(directory)
    for name in ['metadata.das', 'metadata.dds', 'coordinates.ascii']:
        if pin(directory/name) != pin(METADATA/name):
            raise ValueError('Global metadata differs from retained original: '+name)
    check_metadata((directory/'metadata.das').read_text(encoding='utf8'))
    c = coordinates((directory/'coordinates.ascii').read_text(encoding='utf8'))
    if [len(c[n]) for n in ['time', 'depth', 'lat', 'lon']] != [2884, 40, 3251, 4500]:
        raise ValueError('Changed dataset dimensions')
    ix = np.flatnonzero(c['lon'] == 80)
    iz = [np.flatnonzero(c['depth'] == d) for d in [100, 200]]
    if len(ix) != 1 or any(len(v) != 1 for v in iz):
        raise ValueError('Exact native longitude/depth unavailable')
    depths = [int(v[0]) for v in iz]
    latitude = np.flatnonzero((c['lat'] >= -48-1e-5) & (c['lat'] <= -30+1e-5)).tolist()
    if not latitude or any(b-a != 1 for a, b in zip(latitude, latitude[1:])):
        raise ValueError('Invalid latitude selection')
    longitude = [int(ix[0])+offset for offset in [-1, 0, 1]]
    if longitude[0] < 0 or longitude[-1] >= len(c['lon']):
        raise ValueError('Missing native longitude neighbors')
    origin = datetime(2000, 1, 1, tzinfo=timezone.utc)
    actual = {origin+timedelta(hours=float(t)): i for i, t in enumerate(c['time'])}
    requested = [datetime(2013, 1, 1, tzinfo=timezone.utc)+timedelta(days=i) for i in range(365)]
    requests = []
    for m in range(1, 13):
        indices = [actual[t] for t in requested if t.month == m and t in actual]
        runs = [r[i:i+3] for r in index_runs(indices) for i in range(0, len(r), 3)]
        for number, run in enumerate(runs):
            stride = run[1]-run[0] if len(run) > 1 else 1
            section = f'[{run[0]}:{stride}:{run[-1]}][{depths[0]}:{depths[1]-depths[0]}:{depths[1]}]'
            section += f'[{latitude[0]}:1:{latitude[-1]}][{longitude[0]}:1:{longitude[-1]}]'
            requests.append({'file': f'm{m:02d}-r{number:02d}.ascii', 'month': m,
                             'time_indices': run, 'url': BASE+'.ascii?'+quote(','.join(n+section for n in FIELDS), safe='')})
    return {'schema': 'osw.south-indian-hycom-front-level-selection.v1', 'dataset_url': BASE,
            'investigation_current_id': 'south-indian', 'rules': {PROTOCOL: pin(ROOT/PROTOCOL)},
            'operators': {n: pin(ROOT/n) for n in ['analysis/acquire_south_indian_front_levels.py',
                          'analysis/acquire_indian_secc_hycom_2013.py', 'analysis/acquire_eac_100m_source.py',
                          'plans/indian-secc-hycom-array-serialization-protocol-v1.md']},
            'global_metadata_origin': METADATA.relative_to(ROOT).as_posix(),
            'metadata': {n: pin(directory/n) for n in ['metadata.das', 'metadata.dds', 'coordinates.ascii']},
            'selection': {'depth': depths, 'lat': latitude, 'lon': longitude}, 'requests': requests,
            'missing_daily_00z': [t.isoformat() for t in requested if t not in actual],
            'scale': float(np.float32(.001)), 'offsets': {n: float(np.float32(v[2])) for n, v in FIELDS.items()},
            'minimum_pairs': [int(np.ceil(.8*calendar.monthrange(2013, m)[1])) for m in range(1, 13)],
            'width_admission': False, 'current_association_verified': False}


def validate_plan(directory):
    plan = json.loads((Path(directory)/'selection.json').read_bytes())
    if plan != make_plan(directory):
        raise ValueError('Frozen source selection changed')
    return plan


def parse_ascii(text, nt, nz, ny, nx):
    names = '|'.join(FIELDS)
    headers = list(re.finditer(r'(?m)^('+names+r')\.('+names+r'|time|depth|lat|lon)((?:\[\d+\])+)[\r ]*$', text))
    if not text.startswith('Dataset {') or len(headers) != 20:
        raise ValueError('Incomplete four-field grid/maps response')
    declaration = text[:headers[0].start()]
    for name in FIELDS:
        if declaration.count(f'Int16 {name}[time = {nt}][depth = {nz}][lat = {ny}][lon = {nx}];') != 1:
            raise ValueError('Changed packed field type/dimensions')
    parts = {}
    for i, h in enumerate(headers):
        key = (h[1], h[2])
        if key in parts:
            raise ValueError('Duplicate field/map')
        body = text[h.end():headers[i+1].start() if i+1 < len(headers) else len(text)].strip()
        if h[2] in FIELDS:
            if h[1] != h[2] or h[3] != f'[{nt}][{nz}][{ny}][{nx}]':
                raise ValueError('Changed packed array identity')
            lines = body.splitlines()
            if len(lines) != nt*nz*ny:
                raise ValueError('Missing packed rows')
            array = np.empty((nt, nz, ny, nx), dtype='<i2')
            for row, line in enumerate(lines):
                match = re.fullmatch(r'\[(\d+)\]\[(\d+)\]\[(\d+)\],\s*(.*)', line.strip())
                expected = (row//(nz*ny), (row//ny) % nz, row % ny)
                if match is None or tuple(int(match[j]) for j in [1, 2, 3]) != expected:
                    raise ValueError('Wrong packed row ordering')
                tokens = [v.strip() for v in match[4].split(',')]
                if len(tokens) != nx or any(re.fullmatch(r'-?\d+', v) is None for v in tokens):
                    raise ValueError('Malformed packed row')
                values = [int(v) for v in tokens]
                if any(v < -32768 or v > 32767 for v in values):
                    raise ValueError('Packed value outside Int16')
                array[expected] = values
            parts[key] = array
        else:
            size = {'time': nt, 'depth': nz, 'lat': ny, 'lon': nx}[h[2]]
            values = np.array([float(v) for v in body.split(',')], dtype='<f8')
            if h[3] != f'[{size}]' or len(values) != size or not np.all(np.isfinite(values)):
                raise ValueError('Malformed coordinate map')
            parts[key] = values
    result = {n: parts['water_u', n] for n in ['time', 'depth', 'lat', 'lon']}
    if any(not np.array_equal(parts[field, n], result[n]) for field in FIELDS for n in result):
        raise ValueError('Fields have different coordinate maps')
    result.update({n: parts[n, n] for n in FIELDS})
    return result


def validate_response(raw, request, plan, directory):
    c = coordinates((Path(directory)/'coordinates.ascii').read_text(encoding='utf8'))
    selection = plan['selection']
    arrays = parse_ascii(raw.decode('utf8'), len(request['time_indices']), 2, len(selection['lat']), 3)
    for n in ['time', 'depth', 'lat', 'lon']:
        indices = request['time_indices'] if n == 'time' else selection[n]
        if not np.array_equal(arrays[n], c[n][indices]):
            raise ValueError('Response differs from frozen coordinate selection: '+n)
    return arrays


def acquire(directory, first_request_only=False):
    directory = Path(directory)
    plan = validate_plan(directory)
    from south_indian_front_level_preflight import checked
    checked(directory)
    if shutil.disk_usage(directory).free < 1024**3:
        raise ValueError('Need1GiB free before supplementary acquisition')
    def one(request):
        path = directory/request['file']
        receipt = path.with_suffix('.receipt.json')
        if path.exists() and receipt.exists():
            old = json.loads(receipt.read_bytes())
            if old['url'] != request['url'] or old['pin'] != pin(path):
                raise ValueError('Retained response differs')
            print('retained', path.name, flush=True)
            return
        if path.exists() or receipt.exists():
            raise ValueError('Incomplete previous acquisition requires inspection')
        try:
            with urlopen(request['url'], timeout=180) as response:
                raw = response.read(LIMIT+1)
                headers, final_url = dict(response.headers), response.url
            if len(raw) > LIMIT:
                raise ValueError('Oversized source response')
            validate_response(raw, request, plan, directory)
            with path.open('xb') as stream:
                stream.write(raw)
            write_json(receipt, {'url': request['url'], 'final_url': final_url, 'pin': pin(path),
                                 'acquired_utc': datetime.now(timezone.utc).isoformat(), 'headers': headers})
            print('acquired', path.name, len(raw), flush=True)
        except Exception as error:
            with (directory/'failures.jsonl').open('a', encoding='utf8') as stream:
                stream.write(json.dumps({'file': request['file'], 'url': request['url'],
                                         'utc': datetime.now(timezone.utc).isoformat(), 'error': repr(error)})+'\n')
            raise
    with ThreadPoolExecutor(max_workers=2) as executor:
        selected = plan['requests'][:1] if first_request_only else plan['requests']
        futures = [executor.submit(one, r) for r in selected]
        failures = []
        for future in futures:
            try:
                future.result()
            except Exception as error:
                failures.append(repr(error))
        checked(directory)
        if failures:
            raise ValueError(f'{len(failures)} failed requests; valid responses retained; first: {failures[0]}')


def common_means(fields, minimum, scale, offsets):
    valid = np.logical_and.reduce([fields[n] != -30000 for n in FIELDS])
    counts = valid.sum(axis=0).astype('<i2')
    means = {}
    for n in FIELDS:
        result = np.full(counts.shape, np.nan, dtype='<f8')
        np.divide(np.where(valid, fields[n], 0).sum(axis=0, dtype=np.int64)*scale,
                  counts, out=result, where=counts >= minimum)
        result += offsets[n]
        means[n] = result
    return counts, means


def compile_source(directory):
    directory = Path(directory)
    plan = validate_plan(directory)
    from south_indian_front_level_preflight import checked
    checked(directory)
    if shutil.disk_usage(directory).free < 1024**3:
        raise ValueError('Need1GiB free before supplementary compilation')
    c = coordinates((directory/'coordinates.ascii').read_text(encoding='utf8'))
    products = {n: c[n][plan['selection'][n]] for n in ['depth', 'lat', 'lon']}
    products['month'] = np.arange(1, 13, dtype='<i2')
    monthly, receipts = [], {}
    for m in range(1, 13):
        grids = []
        for request in plan['requests']:
            if request['month'] != m:
                continue
            path = directory/request['file']
            receipt = json.loads(path.with_suffix('.receipt.json').read_bytes())
            if receipt['url'] != request['url'] or receipt['pin'] != pin(path):
                raise ValueError('Changed original source response')
            grids.append(validate_response(path.read_bytes(), request, plan, directory))
            receipts[request['file']] = pin(path)
        if not grids:
            raise ValueError('Missing month')
        expected = [i for r in plan['requests'] if r['month'] == m for i in r['time_indices']]
        actual = np.concatenate([g['time'] for g in grids])
        if not np.array_equal(actual, c['time'][expected]):
            raise ValueError('Missing, repeated or reordered daily monthly support')
        counts, means = common_means({n: np.concatenate([g[n] for g in grids]) for n in FIELDS},
                                     plan['minimum_pairs'][m-1], plan['scale'], plan['offsets'])
        monthly.append({'month': m, 'sample_days': sum(len(g['time']) for g in grids), 'counts': counts, 'means': means})
    products['common_samples'] = np.stack([v['counts'] for v in monthly])
    products.update({n: np.stack([v['means'][n] for v in monthly]) for n in FIELDS})
    write_stored_npz(directory/'monthly.npz', products)
    def nullable(a):
        b = a.astype(object); b[~np.isfinite(a)] = None
        return b.tolist()
    document = {'schema': 'osw.south-indian-hycom-front-level-monthly.v1',
                'selection': pin(directory/'selection.json'), 'dataset_url': BASE,
                'source_model_year': 2013, 'depth_m': products['depth'].tolist(),
                'latitude_degrees_north': products['lat'].tolist(), 'longitude_degrees_east': products['lon'].tolist(),
                'units': {n: v[1] for n, v in FIELDS.items()},
                'months': [{'month': v['month'], 'sample_days': v['sample_days'],
                            'minimum_common_samples': plan['minimum_pairs'][v['month']-1],
                            'common_samples': v['counts'].tolist(),
                            'fields': {n: nullable(v['means'][n]) for n in FIELDS}} for v in monthly],
                'interpretation': 'Common-valid daily00Z model-field monthly sample means at two native levels; in-situ temperature; no vertical mean or geostrophic reference conversion.',
                'current_association_verified': False, 'physical_width_admitted': False,
                'physical_axis_admitted': False, 'seasonal_footprint_admitted': False}
    (directory/'monthly-fields.json').write_bytes((json.dumps(document, separators=(',', ':'), allow_nan=False)+'\n').encode())
    quality = {'schema': 'osw.south-indian-hycom-front-level-quality.v1',
               'selection': pin(directory/'selection.json'), 'original_responses': receipts,
               'products': {n: pin(directory/n) for n in ['monthly.npz', 'monthly-fields.json']},
               'missing_daily_00z': plan['missing_daily_00z'], 'grid_shape': list(products['water_u'].shape),
               'months': [{'month': v['month'], 'sample_days': v['sample_days'],
                           'depths': [{'depth_m': float(products['depth'][z]),
                                       'eligible_cells': int(np.isfinite(v['means']['water_u'][z]).sum()),
                                       'minimum_common_samples': int(v['counts'][z].min()),
                                       'maximum_common_samples': int(v['counts'][z].max())} for z in range(2)]} for v in monthly],
               'width_admission': False, 'current_association_verified': False}
    write_json(directory/'quality.json', quality)
    return quality


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['plan', 'acquire', 'compile'])
    parser.add_argument('--directory', type=Path, default=ROOT/'.pytest_cache/south-indian-front-levels-2013')
    parser.add_argument('--first-request-only', action='store_true', help='Validate the first frozen request before resuming the complete acquisition.')
    args = parser.parse_args()
    if args.action == 'plan':
        if (args.directory.exists() and not (args.directory/'selection.json').exists()
                and any(args.directory.iterdir())):
            raise ValueError('Nonempty working directory requires inspection before initialization')
        args.directory.mkdir(parents=True, exist_ok=True)
        if (args.directory/'selection.json').exists():
            validate_plan(args.directory)
        else:
            for name in ['metadata.das', 'metadata.dds', 'coordinates.ascii']:
                shutil.copyfile(METADATA/name, args.directory/name)
            write_json(args.directory/'selection.json', make_plan(args.directory))
    elif args.action == 'acquire':
        acquire(args.directory, args.first_request_only)
    else:
        print(json.dumps(compile_source(args.directory), indent=2))
