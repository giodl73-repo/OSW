"""Offline bounded headers of already archived A20 casts; no native slices."""
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import socket
import netCDF4
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OP = 'research/a20-gulf-stream-retained-header-operator-v2.json'
FOLDER = 'research/source-data/a20-gulf-stream-native-casts-v1'


def numeric_size(v):
    if isinstance(v, np.ndarray):
        return int(v.size) if np.issubdtype(v.dtype, np.number) else 0
    return int(isinstance(v, (int, float, np.number)) and not isinstance(v, (bool, np.bool_)))


def prior_failed_read_charge(path):
    """Reconstruct numeric attribute touches before the first v1 large-string stop."""
    charged = 0
    with netCDF4.Dataset(path) as dataset:
        for name in dataset.ncattrs():
            value = dataset.getncattr(name)
            if isinstance(value, str) and len(value) > 12000:
                return charged
            if isinstance(value, np.ndarray) and value.size > 1000:
                return charged
            charged += numeric_size(value)
    raise ValueError('Expected first-file global-attribute stop was not reproduced')


def safe_attribute(value, ledger):
    ledger['new_numeric_attribute_values_touched'] += numeric_size(value)
    if ledger['prior_failed_numeric_attribute_values'] + ledger['reconstruction_numeric_attribute_touches'] + ledger['new_numeric_attribute_values_touched'] > 10000:
        raise ValueError('Original case-wide numeric metadata cap, no phase reset')
    if isinstance(value, str) and len(value) > 12000:
        raw = value.encode('utf8')
        return {'status': 'oversized_text_attribute_omitted_not_interpreted', 'utf8_bytes': len(raw),
                'sha256': hashlib.sha256(raw).hexdigest()}
    if isinstance(value, np.ndarray):
        if value.size > 1000:
            raise ValueError('Original array-attribute size cap unchanged')
        value = value.tolist()
    elif isinstance(value, np.generic):
        value = value.item()
    def finite(v):
        if isinstance(v, list): return [finite(a) for a in v]
        return str(v) if isinstance(v, float) and not math.isfinite(v) else v
    return finite(value)


def inspect(path, ledger):
    with netCDF4.Dataset(path) as dataset:
        if len(dataset.variables) > 100 or len(dataset.dimensions) > 20:
            raise ValueError('Original single-cast shape guard unchanged')
        result = {'global_attributes': {n: safe_attribute(dataset.getncattr(n), ledger) for n in dataset.ncattrs()},
                  'dimensions': {n: len(d) for n, d in dataset.dimensions.items()},
                  'variables': {n: {'dtype': str(v.dtype), 'shape': list(v.shape), 'dimensions': list(v.dimensions),
                                    'attributes': {a: safe_attribute(v.getncattr(a), ledger) for a in v.ncattrs()}}
                                for n, v in dataset.variables.items()},
                  'variable_values_read': 0, 'native_velocity_values_read': 0, 'native_depth_axis_values_read': 0}
    if len(json.dumps(result)) > 100000:
        raise ValueError('Original retained-header packet cap unchanged')
    return result


def build():
    op = json.loads((ROOT / OP).read_bytes())
    for p, h in op['input_sha256'].items():
        if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != h:
            raise ValueError('Frozen input changed: ' + p)
    journal = json.loads((ROOT / FOLDER / 'journal.json').read_bytes())
    if len(journal['operations']) != 3 or any(r['http_status'] != 200 or r['status'] != 'raw_archived_before_header_interpretation' for r in journal['operations']):
        raise ValueError('All three original transfers succeeded; never retry')
    if journal['case_operation_cap'] != 3 or journal['case_response_bytes'] != 425028:
        raise ValueError('Original aggregate acquisition context required')
    first = ROOT / FOLDER / '014.nc'
    prior = prior_failed_read_charge(first)
    ledger = {'prior_failed_numeric_attribute_values': prior, 'reconstruction_numeric_attribute_touches': prior,
              'new_numeric_attribute_values_touched': 0}
    rows = []
    for operation in journal['operations']:
        p = ROOT / FOLDER / operation['raw_file']
        if p.stat().st_size != operation['bytes_received'] or hashlib.sha256(p.read_bytes()).hexdigest() != operation['sha256']:
            raise ValueError('Original source byte custody required')
        rows.append({'station': operation['station'], 'raw_file': str(Path(FOLDER) / p.name),
                     'raw_sha256': operation['sha256'], 'header': inspect(p, ledger)})
    aggregate_metadata_touch_bound = prior + 2 * (ledger['reconstruction_numeric_attribute_touches'] + ledger['new_numeric_attribute_values_touched'])
    if aggregate_metadata_touch_bound > 10000:
        raise ValueError('Test actual-build plus producer-build touches share original metadata cap')
    return {'schema': 'osw.a20-gulf-stream-retained-headers.v2',
            'status': 'ORIGINAL_THREE_CAST_HEADERS_QUALIFIED_WITH_OVERSIZED_TEXT_HASHED_NOT_INTERPRETED',
            'operator_file': OP, 'input_sha256': op['input_sha256'], 'headers': rows, 'numeric_attribute_ledger': ledger,
            'aggregate_metadata_touch_bound_including_one_test_and_producer': aggregate_metadata_touch_bound,
            'original_case_operations_used': 3, 'original_case_operations_remaining': 0,
            'original_case_response_bytes': 425028, 'new_provider_operations': 0,
            'native_array_values_decoded': 0, 'new_depth_references_admitted': 0,
            'physical_current_bottom_established': False, 'runtime_changed': False, 'full_goal_complete': False}


def main():
    import time
    def stopped(*a): raise SystemExit('Stopped retained-header producer')
    for sig in [signal.SIGALRM, signal.SIGTERM, signal.SIGINT]: signal.signal(sig, stopped)
    socket.socket = lambda *a, **k: (_ for _ in ()).throw(RuntimeError('Offline retained bytes only'))
    signal.alarm(45); start = float(os.environ['OSW_A20_HEADER_PHASE_START'])
    if not 0 <= time.monotonic() - start < 90: raise ValueError('Shared test-and-producer phase clock required')
    folder = ROOT / 'a20-gulf-stream-retained-headers-v2'; folder.mkdir(exist_ok=False)
    report = build()
    report['new_header_processing_seconds'] = time.monotonic() - start
    report['case_time_charge_seconds'] = 3.1966593329999995 + report['new_header_processing_seconds']
    if report['case_time_charge_seconds'] > 180: raise ValueError('Original case time cap cannot reset')
    raw = (json.dumps(report, indent=2, allow_nan=False) + '\n').encode()
    if len(raw) > 400000: raise ValueError('Aggregate bounded header packet required')
    (folder / 'headers.json').write_bytes(raw)
    print(json.dumps({'status': report['status'], 'numeric_attribute_ledger': report['numeric_attribute_ledger'],
                      'case_time_charge_seconds': report['case_time_charge_seconds']}))


if __name__ == '__main__': main()
