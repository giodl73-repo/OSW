"""One-shot cloud custody of three prospectively bounded full-depth LADCP casts."""
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import time
import urllib.error
import urllib.request
import netCDF4
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OP = 'research/a20-gulf-stream-cast-acquisition-operator-v1.json'


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('wb') as stream:
        stream.write((json.dumps(value, indent=2, allow_nan=False) + '\n').encode())
        stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise RuntimeError('Redirect is an unreserved additional operation; no retry')


def validate_operator(op):
    if op['case_operation_cap'] != 3 or op['case_response_byte_cap'] != 600000 or op['per_response_byte_cap'] != 200000:
        raise ValueError('Original aggregate acquisition caps required')
    if op['native_scalar_case_cap'] != 250000 or op['native_byte_case_cap'] != 7000000 or op['future_selected_levels_per_cast_cap'] != 40:
        raise ValueError('No native budget reset or level-cap relaxation')
    if [t['station'] for t in op['targets']] != ['014', '015', '016'] or len({t['url'] for t in op['targets']}) != 3:
        raise ValueError('Exactly three distinct predeclared Gulf Stream casts')
    for t in op['targets']:
        expected = 'https://currents.soest.hawaii.edu/go-ship/ladcp/downloads/2021_A20/' + t['station'] + '.nc'
        if t['url'] != expected:
            raise ValueError('No source or host substitution')
    if any(op['eligibility'].values()):
        raise ValueError('Headers are not admitted depth measurements')


def reserve(journal, folder, target):
    if len(journal['operations']) >= 3 or any(r['url'] == target['url'] for r in journal['operations']):
        raise ValueError('No retry or fourth operation')
    row = {'station': target['station'], 'url': target['url'], 'attempts': 1,
           'status': 'reserved_before_request', 'bytes_received': 0}
    journal['operations'].append(row)
    write_json(folder / 'journal.json', journal)
    return row


def acquire(target, folder, journal, opener):
    row = reserve(journal, folder, target)
    path = folder / (target['station'] + '.nc')
    start = time.monotonic()
    signal.alarm(30)
    try:
        request = urllib.request.Request(target['url'], headers={'User-Agent': 'OSW-bounded-LADCP-custody/1.0'})
        try:
            response = opener.open(request, timeout=25)
        except urllib.error.HTTPError as error:
            response = error
        with response, path.open('xb') as stream:
            row['http_status'] = response.status
            while True:
                part = response.read(min(8192, 200001 - row['bytes_received']))
                if not part:
                    break
                stream.write(part); stream.flush(); os.fsync(stream.fileno())
                row['bytes_received'] += len(part)
                if row['bytes_received'] > 200000:
                    raise ValueError('Response cap exceeded; partial raw retained, no retry')
        raw = path.read_bytes()
        row['sha256'] = hashlib.sha256(raw).hexdigest()
        row['raw_file'] = path.name
        if row['http_status'] != 200 or not raw.startswith((b'CDF', b'\x89HDF')):
            raise ValueError('One-shot target did not return native NetCDF; raw retained')
        row['status'] = 'raw_archived_before_header_interpretation'
        return path
    except BaseException as error:
        row['status'] = 'failed_or_interrupted_no_retry'
        row['error_type'] = type(error).__name__
        if path.exists():
            row['raw_file'] = path.name
            row['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        raise
    finally:
        signal.alarm(0)
        journal['case_time_charge_seconds'] += time.monotonic() - start
        journal['case_response_bytes'] = sum(r['bytes_received'] for r in journal['operations'])
        write_json(folder / 'journal.json', journal)


def header(path):
    metadata_scalars = 0
    def clean(value):
        nonlocal metadata_scalars
        if isinstance(value, np.ndarray):
            if value.size > 1000:
                raise ValueError('Bounded metadata attribute required')
            return clean(value.tolist())
        if isinstance(value, np.generic):
            return clean(value.item())
        if isinstance(value, (list, tuple)):
            return [clean(v) for v in value]
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            metadata_scalars += 1
            return value if math.isfinite(value) else str(value)
        if isinstance(value, str) and len(value) > 12000:
            raise ValueError('Bounded source attribute required')
        return value
    with netCDF4.Dataset(path) as dataset:
        if len(dataset.variables) > 100 or len(dataset.dimensions) > 20:
            raise ValueError('Bounded single-cast header required')
        result = {
            'dimensions': {n: len(d) for n, d in dataset.dimensions.items()},
            'global_attributes': {n: clean(dataset.getncattr(n)) for n in dataset.ncattrs()},
            'variables': {n: {'dtype': str(v.dtype), 'dimensions': list(v.dimensions), 'shape': list(v.shape),
                              'attributes': {a: clean(v.getncattr(a)) for a in v.ncattrs()}}
                          for n, v in dataset.variables.items()},
            'variable_values_read': 0,
            'native_depth_axis_values_read': 0,
            'native_velocity_values_read': 0,
        }
    if metadata_scalars > 10000 or len(json.dumps(result)) > 100000:
        raise ValueError('Whole-case metadata reservation required')
    result['typed_numeric_attribute_values'] = metadata_scalars
    return result


def main():
    def stopped(*args):
        raise SystemExit('Stopped one-shot acquisition; preserve journal and do not replay')
    for sig in [signal.SIGALRM, signal.SIGTERM, signal.SIGINT]:
        signal.signal(sig, stopped)
    op = json.loads((ROOT / OP).read_bytes()); validate_operator(op)
    for p, pin in op['input_sha256'].items():
        if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != pin:
            raise ValueError('Frozen input changed: ' + p)
    folder = ROOT / 'a20-gulf-stream-cast-headers-v1'; folder.mkdir(exist_ok=False)
    journal = {'schema': 'osw.a20-gulf-stream-cast-acquisition-journal.v1', 'operations': [],
               'case_operation_cap': 3, 'case_response_byte_cap': 600000, 'case_response_bytes': 0,
               'case_time_cap_seconds': 180, 'case_time_charge_seconds': 0,
               'native_scalar_case_cap': 250000, 'native_byte_case_cap': 7000000,
               'native_array_values_decoded': 0, 'metadata_numeric_attribute_cap': 10000}
    write_json(folder / 'journal.json', journal)
    start = time.monotonic()
    opener = urllib.request.build_opener(NoRedirect())
    try:
        paths = []
        for target in op['targets']:
            if time.monotonic() - start > 140:
                raise TimeoutError('No fresh time allowance for next cast')
            paths.append(acquire(target, folder, journal, opener))
        # All original raw responses are closed on disk before metadata interpretation.
        signal.alarm(35)
        headers = [{'station': t['station'], 'raw_file': p.name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                    'header': header(p)} for t, p in zip(op['targets'], paths)]
        if sum(r['header']['typed_numeric_attribute_values'] for r in headers) > 10000:
            raise ValueError('Case-wide attribute cap, not per-file reset')
        report = {'schema': 'osw.a20-gulf-stream-cast-headers.v1',
                  'status': 'THREE_NATIVE_CASTS_RETAINED_HEADERS_ONLY_NO_DEPTH_ADMISSION',
                  'operator_file': OP, 'operator_sha256': hashlib.sha256((ROOT / OP).read_bytes()).hexdigest(),
                  'headers': headers, 'source_cast_resources_selected': 3, 'native_profiles_scientifically_decoded': 0,
                  'native_array_values_decoded': 0, 'new_depth_references_admitted': 0,
                  'physical_current_bottom_established': False, 'runtime_changed': False, 'full_goal_complete': False}
        write_json(folder / 'headers.json', report)
        journal['producer_status'] = report['status']
    finally:
        signal.alarm(0)
        journal['case_time_charge_seconds'] = time.monotonic() - start
        write_json(folder / 'journal.json', journal)
    print(json.dumps({'status': report['status'], 'raw_bytes': journal['case_response_bytes'],
                      'operations': len(journal['operations']), 'native_array_values_decoded': 0}))


if __name__ == '__main__':
    main()
