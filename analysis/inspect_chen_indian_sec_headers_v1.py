"""Bounded cloud-only custody and MAT variable-header inspection; no field values."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import urllib.request

REQUEST = 'research/chen-indian-sec-header-request-v1.json'
METADATA = 'research/source-data/chen-indian-sec-2022/model-provider-metadata-v1.json'
OUTPUT = Path('.pytest_cache/chen-indian-sec-header-v1/report.json')
URL = 'https://data.scsio.ac.cn/api/web/v1/file/load/metadata/1568072617497661440.mat'
MAX_BYTES = 8 * 1024 * 1024


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def validate_request(request, script_bytes, metadata_bytes):
    if request.get('schema') != 'osw.chen-indian-sec-header-request.v1':
        raise ValueError('Request schema mismatch')
    if request.get('execute') is not True:
        raise ValueError('Request disabled')
    if request.get('script_sha256') != digest(script_bytes):
        raise ValueError('Inspection script changed after freeze')
    if request.get('metadata_sha256') != digest(metadata_bytes):
        raise ValueError('Provider metadata changed after freeze')
    if request.get('url') != URL or request.get('max_download_bytes') != MAX_BYTES:
        raise ValueError('Source or byte budget changed')
    if request.get('field_value_processing_permitted') is not False:
        raise ValueError('Field processing is outside this request')
    rows = json.loads(metadata_bytes)['data']['list']
    sample = [r for r in rows if r['id'] == 3738 and r['fileType'] == 5]
    if len(sample) != 1 or sample[0]['fileUrl'] != URL.split('/file/load/')[1]:
        raise ValueError('Public sample metadata binding mismatch')


def acquire(response, destination):
    """Read one bounded public sample; refuse redirects and declared over-budget bodies."""
    if response.geturl() != URL or response.status != 200:
        raise ValueError('Unexpected source response')
    declared = response.headers.get('Content-Length')
    if declared is not None and (int(declared) < 128 or int(declared) > MAX_BYTES):
        raise ValueError('Declared source size outside budget')
    total = 0
    h = hashlib.sha256()
    with destination.open('xb') as stream:
        while True:
            chunk = response.read(min(65536, MAX_BYTES + 1 - total))
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_BYTES:
                raise ValueError('Source byte budget exceeded')
            h.update(chunk)
            stream.write(chunk)
    if declared is not None and total != int(declared):
        raise ValueError('Source length differs from response declaration')
    with destination.open('rb') as stream:
        header = stream.read(128)
    if len(header) != 128 or not header.startswith(b'MATLAB 5.0 MAT-file') or header[126:128] not in (b'IM', b'MI'):
        raise ValueError('Not a supported original MAT5 file; refuse HTML/login/HDF payload')
    return {'bytes': total, 'sha256': h.hexdigest(), 'declared_bytes': declared,
            'provider_full_object_checksum': None}


def main():
    if os.environ.get('GITHUB_ACTIONS') != 'true' or os.environ.get('GITHUB_REF') != 'refs/heads/codex/current-measurement-gaps':
        raise RuntimeError('Source acquisition is permitted only in the declared cloud branch job')
    if len(os.sched_getaffinity(0)) != 1:
        raise RuntimeError('One CPU affinity required')
    request_bytes = Path(REQUEST).read_bytes()
    metadata_bytes = Path(METADATA).read_bytes()
    request = json.loads(request_bytes)
    validate_request(request, Path(__file__).read_bytes(), metadata_bytes)
    for path, expected in request['additional_input_sha256'].items():
        if digest(Path(path).read_bytes()) != expected:
            raise RuntimeError('Frozen inspection input changed: ' + path)
    phase = json.loads(Path('research/current-gap-delivery-phase.json').read_bytes())
    if phase['phase'] != 'source-review-only-v1' or phase['heavy_work_permitted'] is not False:
        raise RuntimeError('Unexpected source-review phase')
    # Only scipy's variable inventory API is used. No loadmat or array-value access.
    from scipy.io import whosmat
    report = {'schema': 'osw.chen-indian-sec-header-report.v1',
              'source_commit': os.environ['GITHUB_SHA'], 'url': URL,
              'request_sha256': digest(request_bytes), 'metadata_sha256': digest(metadata_bytes),
              'status': 'FAILED', 'field_values_loaded': False, 'measurements_calculated': 0,
              'geometry_admitted': False, 'cpu_count': 1}
    try:
        with tempfile.TemporaryDirectory(prefix='osw-chen-sec-headers-') as directory:
            target = Path(directory) / 'original.mat'
            req = urllib.request.Request(URL, headers={'User-Agent': 'OSW source metadata inspection'})
            with urllib.request.urlopen(req, timeout=40) as response:
                report['custody'] = acquire(response, target)
            report['variables'] = [{'name': name, 'shape': list(shape), 'matlab_class': kind}
                                   for name, shape, kind in whosmat(target)]
            report['status'] = 'HEADERS_INSPECTED_NO_FIELD_VALUES_OR_MEASUREMENTS'
    except Exception as error:
        report['error_type'] = type(error).__name__
        report['error'] = str(error)[:500]
        raise
    finally:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        with OUTPUT.open('xb') as stream:
            stream.write((json.dumps(report, indent=2) + '\n').encode())
        print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
