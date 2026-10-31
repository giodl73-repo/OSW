"""Cloud-only EACC case, execution revision2; no original has run under v1.

The complete committed preflight, source phase and GitHub checkout identity
must agree before creating an output directory or requesting any velocities.
"""
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import urllib.error
import urllib.request


REPOSITORY = 'giodl73-repo/OSW'
REF = 'refs/heads/codex/current-measurement-gaps'
PHASE = 'research/current-gap-delivery-phase.json'
PHASE_NAME = 'eacc-regional-model-core-v2'
PREFLIGHT = 'research/eacc-regional-model-core-preflight-v2-execution-v2.json'
SELECTION = 'research/eacc-hycom-2013-source-selection-candidate-v1.json'
WORKFLOW = '.github/workflows/eacc-regional-model-core-v2.yml'
REQUIREMENTS = 'requirements-eacc-core-v2-execution-v2.txt'
METADATA = {
    'metadata.dds': 'research/source-data/eacc-hycom-2013-metadata-v1/metadata.dds',
    'metadata.das': 'research/source-data/eacc-hycom-2013-metadata-v1/metadata.das',
    'coordinates.ascii': 'research/source-data/eacc-hycom-2013-coordinates-v1/coordinates.ascii',
}
ENTRYPOINTS = (
    'analysis/eacc_hycom_cloud_acquisition_v2.py',
    'analysis/test_eacc_hycom_cloud_acquisition_v2.py',
    'analysis/eacc_hycom_source_selection_v1.py',
    'analysis/test_eacc_hycom_source_selection_v1.py',
    'analysis/eacc_hycom_source_compilation_v1.py',
    'analysis/test_eacc_hycom_source_compilation_v1.py',
    'analysis/eacc_model_core_seed_v2.py',
    'analysis/test_eacc_model_core_seed_v2.py',
    'analysis/eacc_model_core_diagnostic_v2.py',
    'analysis/test_eacc_model_core_diagnostic_v2.py',
    'analysis/eacc_model_core_figures_v1.py',
    'analysis/test_eacc_model_core_figures_v1.py',
)
DOCUMENTS = (
    'plans/eacc-regional-model-core-width-protocol-v2.md',
    'plans/eacc-hycom-source-compilation-protocol-v1.md',
    'plans/eacc-regional-model-core-execution-protocol-v2.md',
    'plans/eacc-regional-model-core-execution-recovery-v1.md',
    'research/eacc-original-startup-yaml-rejection-review-v1.json',
    'signals/roles/check/eacc-original-execution-recovery-v1-roles-check-2026-10-24.md',
    'signals/roles/check/eacc-regional-model-core-original-case-v2-roles-check-2026-10-24.md',
    'research/source-data/natural-earth-land-10m-5.1.1/ne_10m_land.zip',
    'research/source-data/natural-earth-land-10m-5.1.1/acquisition.json',
)


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode('utf8')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _read(root, name, limit=4 * 1024 * 1024):
    path = (root / name).resolve()
    if not path.is_relative_to(root) or path.stat().st_size > limit:
        raise ValueError('Input path or byte limit is invalid: ' + name)
    return path.read_bytes()


def _git(root, *args):
    return subprocess.check_output(['git', '-c', 'core.fsmonitor=false', '-C', str(root), *args])


def required_input_paths(root):
    """Conservatively freeze every imported repo analysis module, not just entrypoints."""
    root = Path(root).resolve()
    pending = list(ENTRYPOINTS)
    found = set()
    while pending:
        name = pending.pop()
        if name in found:
            continue
        tree = ast.parse(_read(root, name).decode('utf8'), filename=name)
        found.add(name)
        for node in ast.walk(tree):
            modules = [alias.name for alias in node.names] if isinstance(node, ast.Import) else [node.module] if isinstance(node, ast.ImportFrom) and node.module else []
            for module in modules:
                candidate = 'analysis/' + module.split('.')[0] + '.py'
                if (root / candidate).is_file() and candidate not in found:
                    pending.append(candidate)
    return found | set(DOCUMENTS) | {SELECTION, REQUIREMENTS, WORKFLOW} | set(METADATA.values())


def verify_gate(root, env):
    root = Path(root).resolve()
    if env.get('GITHUB_ACTIONS') != 'true' or env.get('GITHUB_REPOSITORY') != REPOSITORY or env.get('GITHUB_REF') != REF:
        raise ValueError('Original EACC velocities require the declared GitHub working-branch job')
    if env.get('RUNNER_OS') != 'Linux' or Path(env.get('GITHUB_WORKSPACE', '')).resolve() != root:
        raise ValueError('Original case requires the declared Linux cloud workspace')
    affinity = getattr(os, 'sched_getaffinity', None)
    if affinity is None or len(affinity(0)) != 1 or any(env.get(name) != '1' for name in
            ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS')):
        raise ValueError('Original case requires one CPU and one numerical worker')
    if any(not re.fullmatch(r'[1-9]\d*', env.get(key, '')) for key in ('GITHUB_RUN_ID', 'GITHUB_RUN_ATTEMPT')):
        raise ValueError('Missing original workflow run identity')
    sha = env.get('GITHUB_SHA', '')
    if not re.fullmatch('[0-9a-f]{40}', sha) or _git(root, 'rev-parse', 'HEAD').decode().strip() != sha:
        raise ValueError('Cloud checkout is not the declared source commit')
    if _git(root, 'status', '--porcelain', '--untracked-files=no').strip():
        raise ValueError('Original case requires clean committed tracked inputs')
    phase_raw = _read(root, PHASE, 8192)
    phase = json.loads(phase_raw)
    if (phase.get('phase') != PHASE_NAME or phase.get('heavy_work_permitted') is not True
            or phase.get('max_heavy_local_jobs') != 0 or phase.get('max_heavy_cloud_jobs') != 1
            or phase.get('execution_workflow') != WORKFLOW or phase.get('preflight') != PREFLIGHT):
        raise ValueError('Original EACC source/core phase is not enabled')
    if phase_raw != _git(root, 'show', 'HEAD:' + PHASE):
        raise ValueError('Source phase must be committed')
    preflight_raw = _read(root, PREFLIGHT, 262144)
    if phase.get('preflight_sha256') != digest(preflight_raw) or preflight_raw != _git(root, 'show', 'HEAD:' + PREFLIGHT):
        raise ValueError('Changed or uncommitted original preflight')
    preflight = json.loads(preflight_raw)
    if (preflight.get('schema') != 'osw.eacc-regional-model-core.preflight.v2'
            or preflight.get('execution_revision') != 2
            or preflight.get('original_velocity_execution_permitted') is not True
            or preflight.get('current_measurement_admission_permitted') is not False
            or preflight.get('selection') != SELECTION or preflight.get('workflow') != WORKFLOW
            or preflight.get('metadata_paths') != METADATA or preflight.get('requirements') != REQUIREMENTS):
        raise ValueError('Unexpected original case scope/preflight')
    pins = preflight.get('input_sha256', {})
    if set(pins) != required_input_paths(root):
        raise ValueError('Incomplete or extra scientific dependency freeze')
    for name, sha256 in pins.items():
        raw = _read(root, name)
        if not re.fullmatch('[0-9a-f]{64}', str(sha256)) or digest(raw) != sha256 or raw != _git(root, 'show', 'HEAD:' + name):
            raise ValueError('Changed/uncommitted scientific input: ' + name)
    selection_raw = _read(root, SELECTION, 131072)
    if preflight.get('selection_sha256') != digest(selection_raw):
        raise ValueError('Source request manifest is not frozen exactly')
    # Package installation is a separate earlier cloud step; record/check each
    # direct numeric reader dependency rather than silently installing here.
    for line in _read(root, REQUIREMENTS, 8192).decode().splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        package, version = line.split('==')
        if importlib.metadata.version(package) != version:
            raise ValueError('Unexpected numeric environment: ' + package)
    if preflight.get('python_major_minor') != list(sys.version_info[:2]):
        raise ValueError('Unexpected Python major/minor runtime')
    return preflight, json.loads(selection_raw)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, newurl):
        return None


def _fetch_response(url, cap):
    """One attempt; no redirect, retries, authentication or challenge handling."""
    request = urllib.request.Request(url, headers={'User-Agent': 'OSW-frozen-EACC-case/1.0'})
    opener = urllib.request.build_opener(_NoRedirect)
    with opener.open(request, timeout=30) as response:
        content_type = response.headers.get('Content-Type', '')
        if response.status != 200 or content_type.split(';')[0].strip().lower() != 'text/plain' or response.url != url:
            raise ValueError('Unexpected HTTP status/content type/final source URL')
        declared = response.headers.get('Content-Length')
        if declared is not None and (not declared.isdigit() or int(declared) > cap):
            raise ValueError('Declared source response exceeds byte cap')
        chunks, count = [], 0
        while True:
            chunk = response.read(min(65536, cap + 1 - count))
            if not chunk:
                break
            chunks.append(chunk)
            count += len(chunk)
            if count > cap:
                raise ValueError('Source response exceeds byte cap')
        if declared is not None and count != int(declared):
            raise ValueError('Incomplete source response')
        return {'raw': b''.join(chunks), 'http_status': response.status,
                'content_type': content_type, 'final_url': response.url}


def _write_once(path, raw):
    with path.open('xb') as stream:
        stream.write(raw)


def acquire_responses(directory, selection, fetch=_fetch_response, clock=None):
    """Internal post-gate acquisition; injectable fetch supports synthetic tests."""
    from eacc_hycom_source_compilation_v1 import RECEIPT_SCHEMA, pin, validate_receipt, validate_response
    clock = clock or (lambda: datetime.now(timezone.utc))
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    completed = []
    for request in selection['requests']:
        try:
            started = clock().isoformat()
            result = fetch(request['url'], selection['response_cap_bytes'])
            finished = clock().isoformat()
            raw = result['raw']
            if type(raw) is not bytes or len(raw) > selection['response_cap_bytes']:
                raise ValueError('Fetch did not return bounded original bytes')
            receipt = {'schema': RECEIPT_SCHEMA, 'request_file': request['file'],
                       'request_url': request['url'], 'final_url': result['final_url'],
                       'http_status': result['http_status'], 'content_type': result['content_type'],
                       'started_utc': started, 'finished_utc': finished,
                       'response': pin(raw), 'selection_sha256': digest(encoded(selection))}
            # Retain even a structurally invalid scientific response and its
            # HTTP receipt, then fail. It must never become a success by editing.
            _write_once(directory / request['file'], raw)
            _write_once(directory / (request['file'] + '.receipt.json'), encoded(receipt))
            validate_receipt(raw, receipt, request, selection)
            validate_response(raw, request, selection)
            completed.append(request['file'])
            print('retained', request['file'], len(raw), flush=True)
        except Exception as error:
            _write_once(directory / 'failure.json', encoded({
                'schema': 'osw.eacc-hycom.acquisition-failure.v1', 'request': request,
                'completed_files': completed, 'error_type': type(error).__name__,
                'error': str(error)[:2048], 'finished_utc': clock().isoformat(),
                'automatic_retry': False, 'source_field_compilation_completed': False}))
            raise
    return completed


def run_case(root, env):
    root = Path(root).resolve()
    preflight, selection = verify_gate(root, env)
    from eacc_hycom_source_selection_v1 import make_selection
    metadata = {name: _read(root, path, 262144) for name, path in METADATA.items()}
    if selection != make_selection(metadata):
        raise ValueError('Exact source request selection cannot be reproduced')
    output = root / '.pytest_cache/eacc-regional-model-core-v2' / ('run-' + env['GITHUB_RUN_ID'] + '-attempt-' + env['GITHUB_RUN_ATTEMPT'])
    output.mkdir(parents=True, exist_ok=False)
    _write_once(output / 'preflight.json', _read(root, PREFLIGHT, 262144))
    _write_once(output / 'selection.json', _read(root, SELECTION, 131072))
    for name, raw in metadata.items():
        _write_once(output / name, raw)
    _write_once(output / 'environment.json', encoded({
        'source_commit': env['GITHUB_SHA'], 'run_id': int(env['GITHUB_RUN_ID']),
        'run_attempt': int(env['GITHUB_RUN_ATTEMPT']), 'python': platform.python_version(),
        'platform': platform.platform(), 'scientific_input_sha256': preflight['input_sha256'],
        'logical_cpu_limit': 1, 'max_concurrent_requests': 1}))
    try:
        completed = acquire_responses(output / 'responses', selection)
        from eacc_hycom_source_compilation_v1 import compile_source
        def load_response(name):
            return (_read(output / 'responses', name, selection['response_cap_bytes']),
                    json.loads(_read(output / 'responses', name + '.receipt.json', 8192)))
        fields = compile_source(metadata, selection, completed, load_response)
        _write_once(output / 'monthly-fields.json', encoded(fields))
        from eacc_model_core_diagnostic_v2 import diagnose_year
        from west_australian_regional_streamlines import Field
        diagnostic = diagnose_year({month['month']: Field(
            fields['longitude_degrees_east'], fields['latitude_degrees_north'],
            month['eastward_m_s'], month['northward_m_s']) for month in fields['months']})
        _write_once(output / 'diagnostic.json', encoded(diagnostic))
        from eacc_model_core_figures_v1 import render_case
        render_case(fields, diagnostic, output / 'figures', rasterize=True)
        result = {'schema': 'osw.eacc-regional-model-core.cloud-result.v2',
                  'status': 'original_diagnostic_completed_not_measurement_admission',
                  'source_commit': env['GITHUB_SHA'], 'run_id': int(env['GITHUB_RUN_ID']),
                  'responses': len(completed), 'cases': len(diagnostic['cases']),
                  'months_with_both_primary_diagnostics_supported': sum(month['both_five_station_half_peak_diagnostics_supported'] for month in diagnostic['months']),
                  'original_input_sha256': preflight['input_sha256'],
                  'monthly_fields_sha256': digest(encoded(fields)), 'diagnostic_sha256': digest(encoded(diagnostic)),
                  'named_current_association_reviewed': False, 'new_current_widths_admitted': 0,
                  'physical_annual_range_admitted': False, 'main_merged': False}
        _write_once(output / 'result.json', encoded(result))
        print(json.dumps(result, indent=2), flush=True)
    except Exception as error:
        _write_once(output / 'case-failure.json', encoded({
            'status': 'original_case_failed_retained_no_retry', 'error_type': type(error).__name__,
            'error': str(error)[:2048], 'source_commit': env['GITHUB_SHA'],
            'run_id': int(env['GITHUB_RUN_ID']), 'new_current_widths_admitted': 0}))
        raise
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cloud-original-case', action='store_true')
    args = parser.parse_args()
    if not args.cloud_original_case:
        parser.error('Original execution requires --cloud-original-case and the frozen cloud phase')
    run_case(Path(__file__).resolve().parents[1], dict(os.environ))
