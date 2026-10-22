"""Read-only field/array/ZIP diagnostics for cross-platform source rebuilds."""
import hashlib
import json
from pathlib import Path
import platform
import tempfile
import zipfile
import zlib

import numpy as np
from acquire_indian_secc_hycom_2013 import compile_source, pin
from package_indian_secc_hycom_2013 import DESTINATION, unpack_checked
from inspect_scientific_reproduction import differences


def inspect():
    source = DESTINATION
    manifest = json.loads((source/'acquisition.json').read_bytes())
    result = {'schema': 'osw.hycom-source-reproduction-inspection.v1',
              'environment': {'python': platform.python_version(), 'platform': platform.platform(),
                              'numpy': np.__version__, 'zlib_runtime': zlib.ZLIB_RUNTIME_VERSION},
              'products': {}, 'array_comparisons': {}, 'zip_member_comparisons': {}}
    with tempfile.TemporaryDirectory(prefix='osw-hycom-inspect-') as work:
        work = Path(work)
        unpack_checked(source/'source-responses.zip', manifest['archive_members'], work)
        compile_source(work)
        for name in ['quality.json', 'monthly.npz', 'monthly-fields.json']:
            expected, rebuilt = pin(source/name), pin(work/name)
            record = {'retained': expected, 'rebuilt': rebuilt, 'exact': expected == rebuilt}
            if name.endswith('.json') and not record['exact']:
                record['field_differences'] = differences(json.loads((source/name).read_bytes()), json.loads((work/name).read_bytes()))
            result['products'][name] = record
        with np.load(source/'monthly.npz', allow_pickle=False) as expected, np.load(work/'monthly.npz', allow_pickle=False) as rebuilt:
            assert set(expected.files) == set(rebuilt.files)
            for name in expected.files:
                a, b = expected[name], rebuilt[name]
                result['array_comparisons'][name] = {
                    'retained_dtype': a.dtype.str, 'rebuilt_dtype': b.dtype.str,
                    'retained_shape': list(a.shape), 'rebuilt_shape': list(b.shape),
                    'retained_bits_sha256': hashlib.sha256(a.tobytes()).hexdigest(),
                    'rebuilt_bits_sha256': hashlib.sha256(b.tobytes()).hexdigest(),
                    'exact_bits': a.dtype == b.dtype and a.shape == b.shape and a.tobytes() == b.tobytes()}
        with zipfile.ZipFile(source/'monthly.npz') as expected, zipfile.ZipFile(work/'monthly.npz') as rebuilt:
            for name in expected.namelist():
                a, b = expected.getinfo(name), rebuilt.getinfo(name)
                fields = ['compress_size', 'file_size', 'compress_type', 'create_system', 'create_version',
                          'extract_version', 'flag_bits', 'external_attr', 'date_time', 'CRC']
                result['zip_member_comparisons'][name] = {
                    'retained_npy_sha256': hashlib.sha256(expected.read(name)).hexdigest(),
                    'rebuilt_npy_sha256': hashlib.sha256(rebuilt.read(name)).hexdigest(),
                    'metadata_differences': {f: {'retained': getattr(a, f), 'rebuilt': getattr(b, f)} for f in fields if getattr(a, f) != getattr(b, f)}}
    result['status'] = 'PASS' if all(v['exact'] for v in result['products'].values()) else 'FAIL'
    return result


if __name__ == '__main__':
    result = inspect()
    print(json.dumps(result, indent=2, allow_nan=False), flush=True)
    raise SystemExit(0 if result['status'] == 'PASS' else 1)
