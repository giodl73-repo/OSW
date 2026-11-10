"""Prospective cloud-only sample support; no current dimension or geometry."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile

import inspect_osnap_wg_2016_2018_source_v1 as source

ROOT = Path(__file__).resolve().parents[1]
OPERATOR = 'analysis/audit_osnap_wg_sample_support_v1.py'
TESTS = 'analysis/test_osnap_wg_sample_support_v1.py'
PROTOCOL = 'plans/osnap-wg-2016-2018-sample-support-protocol-v1.md'
PREFLIGHT = 'research/osnap-wg-2016-2018-sample-support-preflight-v1.json'
ROLE_REVIEW = 'signals/roles/check/osnap-wg-sample-support-v1-roles-check-2026-10-24.md'
WORKFLOW = '.github/workflows/osnap-wg-sample-support-v1.yml'
HEADERS = 'research/osnap-wg-2016-2018-source-headers-v1.json'
CUSTODY = 'research/osnap-wg-2016-2018-original-custody-v1.json'
SOURCE_REVIEW = 'research/osnap-wg-2016-2018-source-header-execution-review-v1.json'
INPUT = ROOT / '.pytest_cache/osnap-restored-source'
OUTPUT = ROOT / '.pytest_cache/osnap-sample-support-v1'
ARCHIVE_SHA = '5b49ea91547fd17b9b3f2e47c743dd2d377a4cdd7ebace5c56977214ec82dee9'
EPOCH_UNITS = 'days since 1950-01-01T00:00:00Z'


def verify_preflight():
    git = ['git', '-c', 'core.fsmonitor=false']
    raw = subprocess.check_output([*git, 'show', 'HEAD:' + PREFLIGHT], cwd=ROOT)
    if raw != (ROOT / PREFLIGHT).read_bytes():
        raise ValueError('Support preflight must be committed before source samples')
    plan = json.loads(raw)
    required = {OPERATOR, TESTS, PROTOCOL, ROLE_REVIEW, WORKFLOW, HEADERS, CUSTODY, SOURCE_REVIEW,
                source.OPERATOR, source.INVENTORY, source.REVIEW, source.PREFLIGHT}
    required.update(json.loads((ROOT / source.PREFLIGHT).read_bytes())['input_sha256'])
    if (plan.get('schema') != 'osw.osnap-sample-support-preflight.v1'
            or plan.get('phase') != 'prospective_declaration'
            or not required <= plan.get('input_sha256', {}).keys()):
        raise ValueError('Incomplete sample-support freeze')
    for name, pin in plan['input_sha256'].items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT) or source.digest(path) != pin:
            raise ValueError('Frozen support input changed: ' + name)
        if subprocess.check_output([*git, 'show', 'HEAD:' + name], cwd=ROOT) != path.read_bytes():
            raise ValueError('Support input differs from committed bytes: ' + name)
    return hashlib.sha256(raw).hexdigest()


def finite_values(value):
    import numpy as np
    array = np.ma.asarray(value, dtype='float64')
    data = np.asarray(array.data)
    mask = np.ma.getmaskarray(array)
    finite = np.isfinite(data)
    return data, ~mask & finite, {'cells': int(data.size), 'masked_cells': int(mask.sum()),
                                'unmasked_nonfinite_cells': int((~mask & ~finite).sum())}


def extrema(data, available):
    selected = data[available]
    return {'available_cells': int(selected.size),
            'min': float(selected.min()) if selected.size else None,
            'max': float(selected.max()) if selected.size else None}


def audit_time(value):
    import numpy as np
    data, available, counts = finite_values(value)
    if data.ndim != 1 or data.size == 0:
        raise ValueError('TIME must be nonempty and one-dimensional')
    # Declared valid range is 0..90000 days. Refuse overflow and unreviewed eras.
    if ((data[available] < 0) | (data[available] > 90000)).any():
        raise ValueError('TIME outside the reviewed epoch range')
    labels = np.full(data.shape, '', dtype='U7')
    observed = data[available]
    dates = (np.datetime64('1950-01-01', 'us')
             + np.rint(observed * 86400 * 1e6).astype('timedelta64[us]'))
    labels[available] = dates.astype('datetime64[M]').astype(str)
    adjacent = available[:-1] & available[1:]
    diffs = np.diff(data)[adjacent] * 86400
    positive = diffs[diffs > 0]
    months = []
    if dates.size:
        start = dates.min().astype('datetime64[M]')
        stop = dates.max().astype('datetime64[M]') + np.timedelta64(1, 'M')
        months = np.arange(start, stop, dtype='datetime64[M]').astype(str).tolist()
    report = {**counts, 'available_rows': int(available.sum()),
              'first_utc': str(dates.min()) + 'Z' if dates.size else None,
              'last_utc': str(dates.max()) + 'Z' if dates.size else None,
              'adjacent_pairs_with_available_time': int(adjacent.sum()),
              'duplicate_adjacent_times': int((diffs == 0).sum()),
              'backwards_adjacent_times': int((diffs < 0).sum()),
              'duplicate_available_times': int(observed.size - np.unique(observed).size),
              'all_rows_available_and_strictly_increasing': bool(available.all() and (diffs > 0).all()),
              'median_positive_adjacent_interval_seconds': float(np.median(positive)) if positive.size else None,
              'max_positive_adjacent_interval_seconds': float(positive.max()) if positive.size else None,
              'months': months}
    return report, labels, available


def paired_support(u, v, time_available, depth=None):
    import numpy as np
    ud, ua, uc = finite_values(u)
    vd, va, vc = finite_values(v)
    if ud.shape != vd.shape or ud.ndim != 2 or ud.shape[0] != len(time_available):
        raise ValueError('Velocity components must have equal TIME-by-bin shapes')
    paired = ua & va & np.asarray(time_available)[:, None]
    report = {'total_cells': int(ud.size), 'time_available_rows': int(np.asarray(time_available).sum()),
              'u': uc, 'v': vc, 'paired_available_cells': int(paired.sum()),
              'profiles_with_any_pair': int(paired.any(axis=1).sum()),
              'profiles_with_all_bins_paired': int(paired.all(axis=1).sum()),
              'paired_counts_by_bin': paired.sum(axis=0).astype(int).tolist(),
              'paired_with_supplied_time_varying_depth_cells': None}
    if depth is not None:
        dd, da, _ = finite_values(depth)
        if dd.shape != ud.shape:
            raise ValueError('Supplied time-varying depth must match velocity shape')
        report['paired_with_supplied_time_varying_depth_cells'] = int((paired & da).sum())
    return report


def read_array(variable):
    import numpy as np
    if variable.dtype.kind not in 'fiu' or int(np.prod(variable.shape)) * 8 > 64 * 1024**2:
        raise ValueError('Unsupported or over-budget support variable')
    return variable[:]  # netCDF4 automatic mask/scale remains enabled.


def coordinates(dataset):
    result = {}
    for name, lower, upper in [('LATITUDE', -90, 90), ('LONGITUDE', -180, 180)]:
        data, available, counts = finite_values(read_array(dataset.variables[name]))
        values = data[available].reshape(-1).tolist()
        result[name] = {**counts, 'values': values,
                        'singleton_in_bounds': bool(data.size == 1 and len(values) == 1
                                                    and lower <= values[0] <= upper),
                        'attributes': {key: source.attribute_value(dataset.variables[name].getncattr(key))
                                       for key in dataset.variables[name].ncattrs()}}
    result['station_position_available'] = all(result[n]['singleton_in_bounds'] for n in ('LATITUDE', 'LONGITUDE'))
    return result


def audit_dataset(dataset):
    import numpy as np
    variables = dataset.variables
    time = variables['TIME']
    if (time.dimensions != ('TIME',) or time.units != EPOCH_UNITS
            or getattr(time, 'calendar', 'standard') not in ('standard', 'gregorian')):
        raise ValueError('Unreviewed TIME units, dimensions or calendar')
    timeline, labels, ta = audit_time(read_array(time))
    nominal = None
    depth_var = variables['DEPTH']
    depth = read_array(depth_var)
    dd, da, dc = finite_values(depth)
    varying_depth = depth_var.dimensions == ('TIME', 'BINDEPTH')
    if not varying_depth and depth_var.dimensions != ('DEPTH',):
        raise ValueError('Unreviewed DEPTH dimensions')
    if not varying_depth:
        nominal = {'values_m': dd[da].reshape(-1).tolist(), 'interpretation': 'nominal_not_observed_motion'}
    pressure_var = variables['PRES']
    if pressure_var.units != 'decibar':
        raise ValueError('Unreviewed pressure unit')
    pressure = read_array(pressure_var)
    pd, pa, pc = finite_values(pressure)
    if not pressure_var.dimensions or pressure_var.dimensions[0] != 'TIME' or pd.shape[0] != len(ta):
        raise ValueError('Pressure must preserve the TIME axis')
    velocity = None
    u = v = None
    if ('UCUR' in variables) != ('VCUR' in variables):
        raise ValueError('Incomplete velocity pair')
    if 'UCUR' in variables:
        uv, vv = variables['UCUR'], variables['VCUR']
        if (uv.dimensions != vv.dimensions or uv.dimensions not in (('TIME', 'DEPTH'), ('TIME', 'BINDEPTH'))
                or uv.units != 'meter/second' or vv.units != 'meter/second'
                or uv.standard_name != 'eastward_sea_water_velocity'
                or vv.standard_name != 'northward_sea_water_velocity'):
            raise ValueError('Unreviewed velocity identity, shape or unit')
        u, v = read_array(uv), read_array(vv)
        velocity = paired_support(u, v, ta, depth if varying_depth else None)
    monthly = []
    for month in timeline['months']:
        rows = labels == month
        record = {'month': month, 'timestamp_rows': int(rows.sum()),
                  'pressure_decibar': extrema(pd[rows], pa[rows]),
                  'supplied_time_varying_depth_m': extrema(dd[rows], da[rows]) if varying_depth else None,
                  'velocity_availability': paired_support(u[rows], v[rows], ta[rows], depth[rows] if varying_depth else None)
                                           if velocity is not None else None}
        monthly.append(record)
    supplemental = {}
    for name in ('BINDEPTH', 'INSTRDEPTH'):
        if name in variables:
            values, available, _ = finite_values(read_array(variables[name]))
            supplemental[name] = {'values': values[available].reshape(-1).tolist(),
                                  'interpretation': 'source_coordinate_not_fixed_analysis_layer'}
    return {'time': timeline, 'coordinates': coordinates(dataset), 'nominal_depth': nominal,
            'supplied_depth': {**dc, **extrema(dd, da), 'time_varying': varying_depth, 'units': depth_var.units},
            'pressure_proxy_decibar': {**pc, **extrema(pd, pa), 'converted_to_depth': False},
            'source_depth_coordinates': supplemental, 'velocity_availability': velocity, 'monthly': monthly,
            'physical_qc_validity_established': False, 'velocity_rotated_or_detided_by_osw': False}


def verify_restored_source(directory, headers, custody, inventory):
    if json.loads((directory / 'acquisition.json').read_bytes()) != custody:
        raise ValueError('First source acquisition custody changed')
    if (directory / 'result.json').read_bytes() != (ROOT / HEADERS).read_bytes():
        raise ValueError('Restored source header report changed')
    original = directory / '2016-2018.zip'
    if original.stat().st_size != custody['bytes'] or source.digest(original) != ARCHIVE_SHA:
        raise ValueError('Restored archive bytes changed')
    if headers['custody'] != custody or custody['sha256'] != ARCHIVE_SHA:
        raise ValueError('Source report custody mismatch')
    fingerprint, count = source.archive_directory_hash(original)
    if (fingerprint != custody['central_directory_sha256']
            or count != inventory['central_directory_entry_count']):
        raise ValueError('Restored directory differs')
    return original


def main(argv=None):
    # Refuse before reading preflight, original data or importing numeric readers.
    source.require_cloud('--cloud-audit' in (argv if argv is not None else __import__('sys').argv[1:]), os.environ)
    parser = argparse.ArgumentParser()
    parser.add_argument('--cloud-audit', action='store_true', required=True)
    parser.parse_args(argv)
    preflight_sha = verify_preflight()
    os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
    os.nice(5)
    if source.shutil.disk_usage(ROOT).free < 2 * 1024**3 or source.available_memory_bytes() < 2 * 1024**3:
        raise ValueError('Insufficient cloud disk or memory')
    headers = json.loads((ROOT / HEADERS).read_bytes())
    custody = json.loads((ROOT / CUSTODY).read_bytes())
    inventory = json.loads((ROOT / source.INVENTORY).read_bytes())
    original = verify_restored_source(INPUT, headers, custody, inventory)
    indexed = {row['member']: row for row in headers['instrument_headers']}
    if len(indexed) != 78:
        raise ValueError('Expected exactly 78 original source headers')
    OUTPUT.mkdir(parents=True, exist_ok=True)
    from netCDF4 import Dataset
    records = []
    with zipfile.ZipFile(original) as archive:
        members = source.checked_members(archive, inventory['instrument_candidates'])
        if set(indexed) != {info.filename for info in members}:
            raise ValueError('Header and archive instrument identities differ')
        for info in members:
            if info.file_size > 64 * 1024**2:
                raise ValueError('Original member exceeds memory budget')
            raw = archive.read(info)
            expected = indexed[info.filename]
            if (len(raw) != expected['bytes'] or hashlib.sha256(raw).hexdigest() != expected['sha256']
                    or source.header_metadata(raw, OUTPUT) != expected['header']):
                raise ValueError('Original member or decoded header changed: ' + info.filename)
            with tempfile.NamedTemporaryFile(dir=OUTPUT, prefix='support-', suffix='.nc', delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(raw)
            del raw
            try:
                with Dataset(str(temporary), 'r') as dataset:
                    record = audit_dataset(dataset)
            finally:
                temporary.unlink()
            records.append({'member': info.filename, 'sha256': expected['sha256'], **record})
            print('PASS SAMPLE SUPPORT ' + info.filename, flush=True)
    report = {'schema': 'osw.osnap-sample-support-audit.v1', 'status': 'PASS_SAMPLE_SUPPORT_AUDIT_ONLY',
              'source_artifact_id': 12558929959, 'source_run_id': 40092026859, 'custody': custody,
              'execution_commit': subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
              'preflight_sha256': preflight_sha, 'instrument_count': len(records), 'instruments': records,
              'source_header_report_sha256': source.digest(ROOT / HEADERS),
              'physical_measurements_derived': 0, 'annual_current_ranges_derived': 0,
              'new_geometry_or_state_joins': 0, 'working_dataset_admitted': False,
              'scientific_release_published': False, 'fresh_provider_download': False}
    encoded = source.encoded(report)
    if len(encoded) > 8 * 1024**2:
        raise ValueError('Support report exceeds artifact budget')
    source.write_once(OUTPUT / 'result.json', encoded)
    print(json.dumps({'status': report['status'], 'instrument_count': len(records), 'bytes': len(encoded)}))


if __name__ == '__main__':
    main()
