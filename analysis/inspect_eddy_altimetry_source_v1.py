"""Cloud-only, bounded acquisition/header audit; never reads the ADT field."""
import hashlib
import json
import math
import os
import pathlib
import time
import urllib.request

REQUEST = pathlib.Path('research/eddy-altimetry-source-audit-request-v1.json')
OUTPUT = pathlib.Path('.pytest_cache/eddy-altimetry-source-audit-v1')


def plain(value):
    if hasattr(value, 'tolist'):
        return plain(value.tolist())
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, bytes):
        return value.decode('utf8', errors='replace')
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def inspect_header(path):
    import netCDF4
    with netCDF4.Dataset(path) as source:
        result = {
            'data_model': source.data_model,
            'dimensions': {k: len(v) for k, v in source.dimensions.items()},
            'attributes': {k: plain(source.getncattr(k)) for k in source.ncattrs()},
            'variables': {},
            'groups': sorted(source.groups),
        }
        for name, var in source.variables.items():
            row = {'dtype': str(var.dtype), 'dimensions': list(var.dimensions),
                   'shape': list(var.shape),
                   'attributes': {k: plain(var.getncattr(k)) for k in var.ncattrs()}}
            # Only bounded one-dimensional coordinate arrays may be read.
            if name in {'time', 'latitude', 'longitude', 'lat', 'lon'} and len(var.shape) == 1:
                assert 0 < var.size <= 12000
                values = var[:]
                row['coordinate'] = {
                    'count': int(var.size), 'first': plain(values[0]),
                    'last': plain(values[-1]),
                    'strictly_increasing': bool((values[1:] > values[:-1]).all()),
                    'minimum_spacing': plain((values[1:] - values[:-1]).min()) if var.size > 1 else None,
                    'maximum_spacing': plain((values[1:] - values[:-1]).max()) if var.size > 1 else None,
                }
                if name == 'time':
                    dates = netCDF4.num2date([values[0], values[-1]], var.units,
                                            calendar=getattr(var, 'calendar', 'standard'))
                    row['coordinate']['decoded_endpoints'] = [str(v) for v in dates]
            result['variables'][name] = row
    return result


def main():
    assert os.environ.get('GITHUB_ACTIONS') == 'true', 'Source acquisition is cloud-only'
    assert os.environ.get('OSW_EDDY_SOURCE_HEADER_AUDIT_V1') == '1'
    request_bytes = REQUEST.read_bytes()
    request = json.loads(request_bytes)
    assert request['schema'] == 'osw.eddy-altimetry-source-audit-request.v1'
    assert request['execute'] is True and request['maximum_cloud_jobs'] == 1
    assert request['field_values_read_permitted'] is False
    assert request['measurement_admission_permitted'] is False
    assert request['native_build_permitted'] is False and request['wasm_build_permitted'] is False
    assert request['runtime_installation_permitted'] is False
    assert request['maximum_local_heavy_jobs'] == 0
    for path, expected_hash in request['input_sha256'].items():
        assert hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest() == expected_hash, path
    url = request['source']['url']
    assert url == 'https://data.griidc.org/api/file/download/947138'
    expected_bytes = request['source']['expected_bytes']
    assert expected_bytes == 757416604
    OUTPUT.mkdir(parents=True, exist_ok=True)
    original = OUTPUT / 'source.nc'
    result = {'schema': 'osw.eddy-altimetry-source-audit-result.v1',
              'source_commit': os.environ['GITHUB_SHA'],
              'request_sha256': hashlib.sha256(request_bytes).hexdigest(),
              'status': 'FAILED', 'adt_field_values_read': False,
              'measurements_admitted': 0, 'physical_identity_joins_created': 0}
    started = time.monotonic()
    digest = hashlib.sha256()
    try:
        count = 0
        with urllib.request.urlopen(urllib.request.Request(url, headers={
                'User-Agent': 'OSW eddy source header audit'}), timeout=45) as response:
            result['http'] = {'final_url': response.url,
                              'content_type': response.headers.get('Content-Type'),
                              'content_length': response.headers.get('Content-Length')}
            with original.open('wb') as target:
                while True:
                    assert time.monotonic() - started < 480, 'Acquisition deadline exceeded'
                    chunk = response.read(min(1048576, expected_bytes + 1 - count))
                    if not chunk:
                        break
                    count += len(chunk)
                    assert count <= expected_bytes, 'Source grew; review metadata before retry'
                    digest.update(chunk)
                    target.write(chunk)
                    if count % (128 * 1048576) == 0:
                        print(f'Cloud source acquired: {count} bytes', flush=True)
        assert count == expected_bytes, (count, expected_bytes)
        with original.open('rb') as f:
            magic = f.read(8)
        assert magic.startswith(b'CDF') or magic == b'\x89HDF\r\n\x1a\n', 'Not NetCDF'
        result['source'] = {'url': url, 'bytes': count, 'sha256': digest.hexdigest()}
        result['header'] = inspect_header(original)
        assert len(json.dumps(result).encode()) < 250000
        result['status'] = 'PASS_HEADER_AUDIT_ONLY'
    except Exception as error:
        result['error'] = {'type': type(error).__name__, 'message': str(error)[:1200]}
        raise
    finally:
        result['elapsed_seconds'] = round(time.monotonic() - started, 2)
        (OUTPUT / 'result.json').write_text(json.dumps(result, indent=2, ensure_ascii=False,
                                                       allow_nan=False) + '\n', encoding='utf8')
        original.unlink(missing_ok=True)
    print(json.dumps({'status': result['status'], 'source': result['source']}))


if __name__ == '__main__':
    main()
