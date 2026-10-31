"""Cloud-only coordinate metadata inspection of the exact previously inventoried MAT file."""
import json
import math
import os
from pathlib import Path
import tempfile
import urllib.request

import inspect_chen_indian_sec_headers_v1 as custody

REQUEST = 'research/chen-indian-sec-coordinate-request-v1.json'
OUTPUT = Path('.pytest_cache/chen-indian-sec-coordinate-v1/report.json')
SOURCE_SHA256 = 'ce174a089a2379cd8c5a79ede226982749d9102a7e7b7d2d0a9180c75ac23cb7'
SOURCE_BYTES = 5816818
COORDINATES = ['lat', 'lon', 'time_year']
SHAPES = {'lat': (1, 76), 'lon': (1, 212), 'time_year': (1, 24)}


def summarize(values, name):
    if len(values) != SHAPES[name][1] or any(not math.isfinite(v) for v in values):
        raise ValueError('Invalid coordinate count or nonfinite value: ' + name)
    if name == 'lat' and any(abs(v) > 90 for v in values):
        raise ValueError('Invalid latitude')
    if name == 'lon' and any(v < -180 or v > 360 for v in values):
        raise ValueError('Invalid longitude')
    differences = [b - a for a, b in zip(values, values[1:])]
    increasing = all(v > 0 for v in differences)
    decreasing = all(v < 0 for v in differences)
    if not (increasing or decreasing):
        raise ValueError('Coordinates are not strictly monotonic: ' + name)
    return {'values': values, 'count': len(values), 'minimum': min(values), 'maximum': max(values),
            'order': 'increasing' if increasing else 'decreasing',
            'minimum_step': min(differences), 'maximum_step': max(differences)}


def inspect_coordinates(target, loader):
    content = loader(target, variable_names=list(COORDINATES), squeeze_me=False)
    actual = {key for key in content if not key.startswith('__')}
    if actual != set(COORDINATES):
        raise ValueError('Only the three declared coordinates may be returned')
    result = {}
    for name in COORDINATES:
        array = content[name]
        if tuple(array.shape) != SHAPES[name]:
            raise ValueError('Coordinate shape differs from the inspected header: ' + name)
        result[name] = summarize([float(v) for v in array.tolist()[0]], name)
    years = result['time_year']['values']
    result['provider_year_range_matches'] = years == list(range(1993, 2017))
    return result


def verify_request(request):
    if request.get('schema') != 'osw.chen-indian-sec-coordinate-request.v1' or request.get('execute') is not True:
        raise ValueError('Coordinate request disabled or invalid')
    if request.get('coordinate_variables') != COORDINATES:
        raise ValueError('Coordinate whitelist changed')
    if request.get('source_sha256') != SOURCE_SHA256 or request.get('source_bytes') != SOURCE_BYTES:
        raise ValueError('Source custody changed')
    if request.get('velocity_or_ssh_field_loading_permitted') is not False or request.get('measurements_permitted') is not False:
        raise ValueError('Scientific field processing is outside this request')
    for path, expected in request['input_sha256'].items():
        if custody.digest(Path(path).read_bytes()) != expected:
            raise ValueError('Frozen coordinate inspection input changed: ' + path)


def main():
    if os.environ.get('GITHUB_ACTIONS') != 'true' or os.environ.get('GITHUB_REF') != 'refs/heads/codex/current-measurement-gaps':
        raise RuntimeError('Cloud-only coordinate metadata inspection')
    if len(os.sched_getaffinity(0)) != 1:
        raise RuntimeError('One CPU required')
    raw = Path(REQUEST).read_bytes()
    request = json.loads(raw)
    verify_request(request)
    phase = json.loads(Path('research/current-gap-delivery-phase.json').read_bytes())
    if phase['phase'] != 'source-review-only-v1' or phase['heavy_work_permitted'] is not False:
        raise RuntimeError('Source-review phase changed')
    from scipy.io import loadmat
    report = {'schema': 'osw.chen-indian-sec-coordinate-report.v1', 'source_commit': os.environ['GITHUB_SHA'],
              'request_sha256': custody.digest(raw), 'status': 'FAILED', 'cpu_count': 1,
              'loaded_variables': list(COORDINATES), 'velocity_or_ssh_fields_loaded': False,
              'measurements_calculated': 0, 'physical_geometry_admitted': False}
    try:
        with tempfile.TemporaryDirectory(prefix='osw-chen-sec-coordinates-') as directory:
            target = Path(directory) / 'original.mat'
            req = urllib.request.Request(custody.URL, headers={'User-Agent': 'OSW coordinate metadata inspection'})
            with urllib.request.urlopen(req, timeout=40) as response:
                report['custody'] = custody.acquire(response, target)
            if report['custody']['sha256'] != SOURCE_SHA256 or report['custody']['bytes'] != SOURCE_BYTES:
                raise ValueError('Original changed since header inspection; do not load')
            report['coordinates'] = inspect_coordinates(target, loadmat)
            report['status'] = 'COORDINATES_INSPECTED_NO_VELOCITY_FIELDS_OR_MEASUREMENTS'
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
