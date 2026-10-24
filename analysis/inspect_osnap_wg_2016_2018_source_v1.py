"""Prepared cloud-only original custody and NetCDF HEADER inspection.

No velocity arrays, widths, lengths, monthly ranges or state joins are derived.
Original execution requires a committed prospective preflight, still pending.
After original execution this version and its dependencies must remain frozen.
"""
import argparse
import datetime
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import shutil
import struct
import subprocess
import tempfile
import time
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OPERATOR = 'analysis/inspect_osnap_wg_2016_2018_source_v1.py'
TESTS = 'analysis/test_osnap_wg_2016_2018_source_inspection_v1.py'
PROTOCOL = 'plans/osnap-wg-2016-2018-source-inspection-protocol-v1.md'
INVENTORY = 'research/west-greenland-osnap-2016-2018-archive-inventory-v1.json'
REVIEW = 'research/west-greenland-osnap-2016-2018-metadata-review-v1.json'
ROLE_REVIEW = 'signals/roles/check/osnap-wg-source-inspection-v1-roles-check-2026-10-24.md'
PREFLIGHT = 'research/osnap-wg-2016-2018-source-inspection-preflight-v1.json'
OUTPUT = ROOT / '.pytest_cache/osnap-wg-2016-2018-source'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def require_cloud(explicit, environment):
    if not explicit or environment.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('Explicit cloud-only source inspection required; local archive access is held')


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode('utf8')


def available_memory_bytes():
    for line in Path('/proc/meminfo').read_text().splitlines():
        if line.startswith('MemAvailable:'):
            return int(line.split()[1]) * 1024
    raise ValueError('Cannot verify available cloud memory')


def write_once(path, raw):
    if path.exists():
        if path.read_bytes() != raw:
            raise ValueError('Existing source receipt differs; do not overwrite: ' + str(path))
        return
    with path.open('xb') as stream:
        stream.write(raw)


def verify_preflight():
    git = ['git', '-c', 'core.fsmonitor=false']
    committed = subprocess.check_output([*git, 'show', 'HEAD:' + PREFLIGHT], cwd=ROOT)
    if committed != (ROOT / PREFLIGHT).read_bytes():
        raise ValueError('Prospective source preflight must be committed before original access')
    preflight = json.loads(committed)
    required = {OPERATOR, TESTS, PROTOCOL, INVENTORY, REVIEW, ROLE_REVIEW, 'requirements-test.txt'}
    workflow = preflight.get('execution_workflow', '')
    if (not workflow.startswith('.github/workflows/') or not workflow.endswith('.yml')
            or not (ROOT / workflow).resolve().is_relative_to((ROOT / '.github/workflows').resolve())):
        raise ValueError('Preflight must bind its cloud execution workflow')
    required.add(workflow)
    pins = preflight.get('input_sha256', {})
    if (preflight.get('schema') != 'osw.osnap-source-inventory-preflight.v1'
            or preflight.get('phase') != 'prospective_declaration' or not required <= pins.keys()):
        raise ValueError('Incomplete prospective source-inspection freeze')
    for name, expected in pins.items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT) or digest(path) != expected:
            raise ValueError('Frozen source-inspection input changed: ' + name)
        if subprocess.check_output([*git, 'show', 'HEAD:' + name], cwd=ROOT) != path.read_bytes():
            raise ValueError('Source-inspection input is not the committed file: ' + name)
    return hashlib.sha256(committed).hexdigest()


def archive_directory_hash(path):
    with path.open('rb') as stream:
        size = stream.seek(0, 2)
        stream.seek(max(0, size - 65557))
        tail = stream.read(65557)
        at = tail.rfind(b'PK\x05\x06')
        if at < 0:
            raise ValueError('Missing ZIP end record')
        _, disk, cd_disk, count_disk, count, length, offset, comment = struct.unpack_from('<4s4H2LH', tail, at)
        if disk or cd_disk or count_disk != count or at + 22 + comment != len(tail):
            raise ValueError('Unexpected ZIP layout')
        if length > 65557 or offset + length != size - len(tail) + at:
            raise ValueError('Unexpected ZIP directory bounds')
        stream.seek(offset)
        return hashlib.sha256(stream.read(length)).hexdigest(), count


def checked_members(archive, expected):
    infos = archive.infolist()
    names = [item.filename for item in infos]
    if len(names) != len(set(names)):
        raise ValueError('Duplicate archive member name')
    for name in names:
        if PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts or '\\' in name:
            raise ValueError('Unsafe archive member name')
    wanted = {row['name']: row for row in expected}
    if len(wanted) != len(expected):
        raise ValueError('Duplicate expected instrument member')
    instruments = {name for name in names if name.split('/')[0] in {f'LS{i}' for i in range(1, 9)}
                   and not name.endswith('/') and not PurePosixPath(name).name.startswith('.')}
    if instruments != set(wanted):
        raise ValueError('Instrument inventory differs from the reviewed archive directory')
    for name, row in wanted.items():
        info = archive.getinfo(name)
        if (info.file_size != row['uncompressed_bytes'] or info.compress_size != row['compressed_bytes']
                or info.compress_type != row['compression'] or f'{info.CRC:08x}' != row['crc32']):
            raise ValueError('Instrument member metadata changed: ' + name)
    return [archive.getinfo(name) for name in sorted(wanted)]


def attribute_value(value):
    if hasattr(value, 'tolist'):
        value = value.tolist()
    if isinstance(value, bytes):
        return {'byte_attribute_hex': value.hex()}
    if isinstance(value, (list, tuple)):
        return [attribute_value(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return {'nonfinite_attribute': str(value)}
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise ValueError('Unsupported NetCDF attribute type: ' + type(value).__name__)


def header_metadata(raw, temporary_directory=None):
    # Import only after the cloud/local guard and original custody checks.
    from netCDF4 import Dataset
    if not raw.startswith((b'CDF\x01', b'CDF\x02', b'CDF\x05', b'\x89HDF\r\n\x1a\n')):
        raise ValueError('Provider-described NetCDF member has an unexpected signature')
    if len(raw) > 64 * 1024**2:
        raise ValueError('Instrument member exceeds the temporary-copy budget')
    # Classic NetCDF zero-record files are not reliably supported by nc_open_mem
    # across platforms. A private exact-byte copy avoids padding source bytes or
    # materializing arrays through an alternate eager reader. No archive path is used.
    with tempfile.NamedTemporaryFile(prefix='osnap-header-', suffix='.nc', dir=temporary_directory, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(raw)
    try:
        with Dataset(str(temporary), mode='r') as dataset:
            if dataset.groups:
                raise ValueError('Nested NetCDF groups require an explicitly reviewed inspection version')
            if any(getattr(dataset, name) for name in ('enumtypes', 'cmptypes', 'vltypes')):
                raise ValueError('User-defined NetCDF types require an explicitly reviewed inspection version')
            attributes = lambda obj: {key: attribute_value(obj.getncattr(key)) for key in obj.ncattrs()}
            result = {'data_model': dataset.data_model, 'attributes': attributes(dataset),
                      'dimensions': {name: {'length': len(dim), 'unlimited': dim.isunlimited()}
                                     for name, dim in dataset.dimensions.items()},
                      'variables': {name: {'dtype': str(var.dtype), 'dimensions': list(var.dimensions),
                                           'shape': list(var.shape), 'attributes': attributes(var)}
                                    for name, var in dataset.variables.items()}}
    finally:
        temporary.unlink()
    if len(encoded(result)) > 256 * 1024:
        raise ValueError('Instrument header exceeds the declared metadata budget')
    return result


def download_original(path, plan):
    size = plan['archive_total_bytes_from_content_range']
    url = plan['provider_content_url']
    if url != 'https://repository.gatech.edu/server/api/core/bitstreams/3fb9512f-56ed-40cb-b57e-ac0bd96be460/content':
        raise ValueError('Unexpected original provider URL')
    partial = path.with_suffix('.partial')
    deadline = time.monotonic() + 600
    created = False
    acquisition = {'started_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   'request': {'method': 'GET', 'url': url, 'headers': {'Accept-Encoding': 'identity'}}}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'Accept-Encoding': 'identity'}), timeout=30) as response:
            if response.status != 200 or response.headers.get('Content-Encoding', 'identity') != 'identity':
                raise ValueError('Unexpected original response encoding or status')
            acquisition['response'] = {'status': response.status, 'url': response.geturl(),
                'headers': {name: response.headers.get(name) for name in
                            ('Content-Type', 'Content-Length', 'ETag', 'Last-Modified')}}
            count = 0
            with partial.open('xb') as output:
                created = True
                while block := response.read(1024 * 1024):
                    count += len(block)
                    if count > size or time.monotonic() > deadline:
                        raise ValueError('Original download exceeded declared byte/time budget')
                    output.write(block)
            if count != size or path.exists():
                raise ValueError('Incomplete original download or existing target')
        partial.rename(path)
        acquisition['completed_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return acquisition
    finally:
        if created and partial.exists():
            partial.unlink()


def custody_record(expected, acquisition, source_commit, previous=None):
    if previous is not None:
        if (any(previous.get(key) != value for key, value in expected.items())
                or not previous.get('first_execution_commit') or not previous.get('acquisition')):
            raise ValueError('Original custody changed or lacks first-acquisition provenance')
        return previous
    if not acquisition or not source_commit:
        raise ValueError('First original custody requires acquisition provenance and source commit')
    return {**expected, 'first_execution_commit': source_commit, 'acquisition': acquisition}


def main():
    # Refuse before argument parsing, source/index reads, output writes or networking.
    require_cloud(True, os.environ)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cloud-inspect', action='store_true')
    args = parser.parse_args()
    require_cloud(args.cloud_inspect, os.environ)
    if hasattr(os, 'sched_getaffinity'):
        os.sched_setaffinity(0, {min(os.sched_getaffinity(0))}); os.nice(5)
    if shutil.disk_usage(ROOT).free < 2 * 1024**3 or available_memory_bytes() < 2 * 1024**3:
        raise ValueError('Cloud source inspection requires 2 GiB free disk and available memory')
    preflight_sha = verify_preflight()
    plan = json.loads((ROOT / INVENTORY).read_bytes())
    source_review = json.loads((ROOT / REVIEW).read_bytes())
    if plan['instrument_candidate_count'] != 78 or len(plan['instrument_candidates']) != 78:
        raise ValueError('Changed reviewed deployment inventory')
    OUTPUT.mkdir(parents=True, exist_ok=True)
    original = OUTPUT / '2016-2018.zip'
    custody = OUTPUT / 'acquisition.json'
    if original.exists() and not custody.exists():
        raise ValueError('Unregistered cached original; custody must precede reuse')
    acquisition = None
    if not original.exists():
        acquisition = download_original(original, plan)
    directory_sha, entries = archive_directory_hash(original)
    if (original.stat().st_size != plan['archive_total_bytes_from_content_range']
            or directory_sha != plan['acquisition_scope']['central_directory_sha256']
            or entries != plan['central_directory_entry_count']):
        raise ValueError('Original differs from the reviewed archive metadata')
    expected_custody = {'schema': 'osw.osnap-original-custody.v1',
                      'provider_url': plan['provider_content_url'], 'bytes': original.stat().st_size,
                      'sha256': digest(original), 'central_directory_sha256': directory_sha,
                      'dataset_doi': plan['dataset_doi'], 'preflight_sha256': preflight_sha,
                      'reported_collection_period': source_review['readme']['reported_collection_period'],
                      'provider_license_link': source_review['metadata_page']['license_link_observed']}
    source_commit = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    source_custody = custody_record(expected_custody, acquisition, source_commit,
                                   json.loads(custody.read_bytes()) if custody.exists() else None)
    write_once(custody, encoded(source_custody))
    records = []
    with zipfile.ZipFile(original) as archive:
        for info in checked_members(archive, plan['instrument_candidates']):
            if info.file_size > 64 * 1024**2:
                raise ValueError('Instrument member exceeds the memory budget')
            raw = archive.read(info)  # ZipFile checks CRC; no archive-path extraction.
            records.append({'member': info.filename, 'bytes': len(raw),
                            'sha256': hashlib.sha256(raw).hexdigest(), 'header': header_metadata(raw, OUTPUT)})
            print('PASS instrument HEADER ' + info.filename, flush=True)
    result = {'schema': 'osw.osnap-wg-source-header-inventory.v1', 'status': 'PASS_SOURCE_HEADERS_ONLY',
              'custody': source_custody, 'instrument_headers': records, 'instrument_count': len(records),
              'observation_variable_arrays_materialized': False, 'physical_widths_or_lengths_derived': 0,
              'annual_ranges_derived': 0, 'new_geometry_or_state_joins': 0,
              'working_dataset_admitted': False, 'scientific_release_published': False}
    report = encoded(result)
    if len(report) > 8 * 1024**2:
        raise ValueError('Source header report exceeds the declared artifact budget')
    write_once(OUTPUT / 'result.json', report)
    print(json.dumps({'status': result['status'], 'instrument_count': len(records),
                      'original_sha256': source_custody['sha256'], 'new_measurements': 0}), flush=True)


if __name__ == '__main__':
    main()
