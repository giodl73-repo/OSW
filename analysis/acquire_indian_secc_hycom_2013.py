"""Frozen daily-00Z HYCOM source preparation; no current-width admission.

Run `plan` against retained metadata, then `acquire`, then `compile`.
Velocity requests are bounded and resumable; compilation is offline.
"""
import argparse
import calendar
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import quote
from urllib.request import urlopen

import numpy as np
from acquire_eac_100m_source import write_json, write_npz
from acquire_south_australian_hycom_2d import check_metadata, parse_ascii

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://tds.hycom.org/thredds/dodsC/GLBv0.08/expt_53.X/data/2013'
PROTOCOL = 'plans/indian-secc-hycom-2013-source-protocol-v1.md'
PREFLIGHT = 'research/indian-secc-hycom-2013-source-preflight.json'
LIMIT = 20_000_000


def pin(path):
    raw = Path(path).read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def coordinates(text):
    headers = list(re.finditer(r'(?m)^(time|depth|lat|lon)\[(\d+)\][\r ]*$', text))
    if not text.startswith('Dataset {') or len(headers) != 4:
        raise ValueError('Incomplete coordinate response')
    result = {}
    for i, h in enumerate(headers):
        body = text[h.end():headers[i+1].start() if i+1 < len(headers) else len(text)]
        values = np.array([float(x) for x in body.strip().split(',')], dtype='<f8')
        if h[1] in result or len(values) != int(h[2]) or not np.all(np.isfinite(values)):
            raise ValueError('Invalid or duplicate coordinate')
        if len(values) > 1 and np.any(np.diff(values) <= 0):
            raise ValueError('Coordinates must strictly increase')
        result[h[1]] = values
    if set(result) != {'time', 'depth', 'lat', 'lon'}:
        raise ValueError('Missing coordinate')
    return result


def index_runs(indices):
    """Preserve every requested index, splitting whenever the stride changes."""
    runs = []
    start = 0
    while start < len(indices):
        stop = start + 1
        stride = indices[stop] - indices[start] if stop < len(indices) else 1
        while stop + 1 < len(indices) and indices[stop+1] - indices[stop] == stride:
            stop += 1
        runs.append(indices[start:stop+1])
        start = stop + 1
    return runs


def make_plan(directory):
    directory = Path(directory)
    check_metadata((directory / 'metadata.das').read_text(encoding='utf8'))
    das = (directory / 'metadata.das').read_text(encoding='utf8')
    for variable, frame in [('water_u', 'eastward'), ('water_v', 'northward')]:
        block = re.search(r'\b' + variable + r' \{(.*?)\n    \}', das, re.S)
        if block is None or f'String standard_name "{frame}_sea_water_velocity";' not in block[1]:
            raise ValueError('Unverified Earth velocity frame')
    c = coordinates((directory / 'coordinates.ascii').read_text(encoding='utf8'))
    dds = (directory / 'metadata.dds').read_text(encoding='utf8')
    for name, size in [('time', 2884), ('depth', 40), ('lat', 3251), ('lon', 4500)]:
        if len(c[name]) != size or f'{name}[{name} = {size}]' not in dds:
            raise ValueError('Unexpected source coordinate dimensions')
    depth = np.flatnonzero(c['depth'] == 15)
    if len(depth) != 1:
        raise ValueError('Missing unique exact 15m level')
    selection = {'depth': [int(depth[0])]}
    for name, lo, hi in [('lat', -12, 0), ('lon', 75, 85)]:
        ix = np.flatnonzero((c[name] >= lo-1e-5) & (c[name] <= hi+1e-5))
        if len(ix) < 2 or np.any(np.diff(ix) != 1):
            raise ValueError('Noncontiguous viewport')
        selection[name] = ix.tolist()
    origin = datetime(2000, 1, 1, tzinfo=timezone.utc)
    actual = {origin + timedelta(hours=float(h)): i for i, h in enumerate(c['time'])}
    if any(t.year != 2013 or t.minute or t.second or t.microsecond for t in actual):
        raise ValueError('Unexpected source calendar')
    requested = [datetime(2013, 1, 1, tzinfo=timezone.utc) + timedelta(days=i) for i in range(365)]
    requests = []
    for month in range(1, 13):
        indices = [actual[t] for t in requested if t.month == month and t in actual]
        runs = [r[i:i+6] for r in index_runs(indices) for i in range(0, len(r), 6)]
        for run_number, run in enumerate(runs):
            stride = run[1]-run[0] if len(run) > 1 else 1
            section = f'[{run[0]}:{stride}:{run[-1]}][{selection["depth"][0]}]'
            section += ''.join(f'[{selection[n][0]}:1:{selection[n][-1]}]' for n in ['lat', 'lon'])
            expression = ','.join(v+section for v in ['water_u', 'water_v'])
            requests.append({'file': f'm{month:02d}-r{run_number:02d}.ascii', 'month': month,
                             'time_indices': run, 'url': BASE+'.ascii?'+quote(expression, safe='')})
    return {'schema': 'osw.indian-secc-hycom-selection.v1', 'dataset_url': BASE,
            'inputs': {n: pin(directory/n) for n in ['metadata.dds', 'metadata.das', 'coordinates.ascii']},
            'rules': {n: pin(ROOT/n) for n in [PROTOCOL, PREFLIGHT]},
            'selection': selection, 'requests': requests,
            'missing_daily_00z': [t.isoformat() for t in requested if t not in actual],
            'packing_scale_float32_as_float64': float(np.float32(0.001)),
            'packing_scale_float64_hex': float(np.float32(0.001)).hex(),
            'calendar_days': [calendar.monthrange(2013, m)[1] for m in range(1, 13)],
            'minimum_pairs': [int(np.ceil(.8*calendar.monthrange(2013, m)[1])) for m in range(1, 13)],
            'width_admission': False, 'axis_admission': False}


def validate_plan(directory):
    plan = json.loads((Path(directory)/'selection.json').read_bytes())
    if plan != make_plan(directory):
        raise ValueError('Frozen source selection or inputs changed')
    return plan


def acquire(directory):
    directory = Path(directory)
    plan = validate_plan(directory)
    def one(request):
        target = directory/request['file']
        receipt = target.with_suffix('.receipt.json')
        if target.exists() and receipt.exists():
            old = json.loads(receipt.read_bytes())
            if old['url'] != request['url'] or old['pin'] != pin(target):
                raise ValueError('Retained source receipt mismatch')
            print('retained', target.name, flush=True)
            return
        if target.exists() or receipt.exists():
            raise ValueError('Incomplete prior acquisition requires inspection')
        try:
            with urlopen(request['url'], timeout=50) as response:
                raw = response.read(LIMIT+1)
                headers = dict(response.headers)
                final_url = response.url
            if len(raw) > LIMIT or not raw.startswith(b'Dataset {'):
                raise ValueError('Oversized or non-DAP response')
            # Validate all array/map identities before retaining a successful receipt.
            validate_cube(raw.decode('utf8'), request, plan, directory)
            target.write_bytes(raw)
            write_json(receipt, {'url': request['url'], 'final_url': final_url, 'pin': pin(target),
                                 'acquired_utc': datetime.now(timezone.utc).isoformat(), 'headers': headers})
            print('acquired', target.name, len(raw), flush=True)
        except Exception as error:
            with (directory/'failures.jsonl').open('a', encoding='utf8') as stream:
                stream.write(json.dumps({'file': request['file'], 'utc': datetime.now(timezone.utc).isoformat(),
                                         'error': repr(error)})+'\n')
            raise
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Collect every submitted task even when another request fails.
        futures = [executor.submit(one, request) for request in plan['requests']]
        errors = []
        for future in futures:
            try:
                future.result()
            except Exception as error:
                errors.append(repr(error))
        if errors:
            raise ValueError(f'{len(errors)} failed requests; retained successful responses; first: {errors[0]}')


def validate_cube(text, request, plan, directory):
    c = coordinates((Path(directory)/'coordinates.ascii').read_text(encoding='utf8'))
    selection = plan['selection']
    arrays = parse_ascii(text, len(request['time_indices']), len(selection['lat']), len(selection['lon']))
    for name in ['time', 'depth', 'lat', 'lon']:
        ix = request['time_indices'] if name == 'time' else selection[name]
        if not np.array_equal(arrays[name], c[name][ix]):
            raise ValueError('Response coordinates differ from frozen selection: '+name)
    return arrays


def paired_mean(u, v, minimum, scale):
    valid = (u != -30000) & (v != -30000)
    counts = valid.sum(axis=0).astype('<i2')
    outputs = []
    for array in [u, v]:
        result = np.full(counts.shape, np.nan, dtype='<f8')
        np.divide(np.where(valid, array, 0).sum(axis=0, dtype=np.int64)*scale,
                  counts, out=result, where=counts >= minimum)
        outputs.append(result)
    return counts, *outputs


def compile_source(directory):
    directory = Path(directory)
    plan = validate_plan(directory)
    coordinates_ = coordinates((directory/'coordinates.ascii').read_text(encoding='utf8'))
    monthly = {}
    receipts = {}
    for month in range(1, 13):
        grids = []
        for request in plan['requests']:
            if request['month'] != month:
                continue
            path = directory/request['file']
            receipt = json.loads(path.with_suffix('.receipt.json').read_bytes())
            if receipt['url'] != request['url'] or receipt['pin'] != pin(path):
                raise ValueError('Source receipt mismatch')
            receipts[request['file']] = pin(path)
            grids.append(validate_cube(path.read_text(encoding='utf8'), request, plan, directory))
        if not grids:
            raise ValueError('No daily source samples for a month')
        count, u, v = paired_mean(np.concatenate([g['water_u'] for g in grids]),
                                  np.concatenate([g['water_v'] for g in grids]),
                                  plan['minimum_pairs'][month-1], plan['packing_scale_float32_as_float64'])
        monthly[month] = {'pair_count': count, 'u_m_s': u, 'v_m_s': v,
                          'sample_days': sum(len(g['time']) for g in grids)}
    arrays = {n: coordinates_[n][plan['selection'][n]] for n in ['lat', 'lon', 'depth']}
    arrays['month'] = np.arange(1, 13, dtype='<i2')
    for name in ['pair_count', 'u_m_s', 'v_m_s']:
        arrays[name] = np.stack([monthly[m][name] for m in range(1, 13)])
    write_npz(directory/'monthly.npz', arrays)
    report = {'schema': 'osw.indian-secc-hycom-source-quality.v1', 'selection': pin(directory/'selection.json'),
              'original_responses': receipts, 'monthly_arrays': pin(directory/'monthly.npz'),
              'native_grid_shape': [len(arrays['lat']), len(arrays['lon'])],
              'missing_daily_00z': plan['missing_daily_00z'],
              'months': [{'month': m, 'sample_days': monthly[m]['sample_days'],
                          'calendar_days': plan['calendar_days'][m-1], 'minimum_pairs': plan['minimum_pairs'][m-1],
                          'eligible_cells': int(np.isfinite(monthly[m]['u_m_s']).sum()),
                          'paired_count_min': int(monthly[m]['pair_count'].min()),
                          'paired_count_max': int(monthly[m]['pair_count'].max())} for m in range(1, 13)],
              'interpretation': 'Paired daily-00Z model-vector monthly sample means at provider 15m; not full 3-hour means, observations, climatology, current outlines or measurements.',
              'width_admission': False, 'axis_admission': False, 'seasonal_playback_admission': False}
    write_json(directory/'quality.json', report)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['plan', 'acquire', 'compile'])
    parser.add_argument('--directory', type=Path, default=ROOT/'.pytest_cache/indian-secc-hycom-2013')
    args = parser.parse_args()
    if args.action == 'plan':
        path = args.directory/'selection.json'
        if path.exists():
            validate_plan(args.directory)
        else:
            write_json(path, make_plan(args.directory))
    elif args.action == 'acquire':
        acquire(args.directory)
    else:
        print(json.dumps(compile_source(args.directory), indent=2))
