"""Gated cloud continuation of the exact saved EACC source prefix."""
import argparse
import ast
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import sys

import eacc_hycom_cloud_acquisition_v2 as original
from eacc_hycom_cloud_acquisition_v2 import _git, _read, _write_once, digest, encoded


PHASE_NAME = 'eacc-source-resume-v2'
WORKFLOW = '.github/workflows/eacc-hycom-source-resume-v2.yml'
CORE_PREFLIGHT = original.PREFLIGHT
CORE_SHA = 'c596a4da53ac2082339a5ca8f415816ea24e0be49948d618056a2205d3695409'
PROTOCOL = 'plans/eacc-hycom-source-resume-protocol-v2.md'
ROLE = 'signals/roles/check/eacc-hycom-source-resume-v2-roles-check-2026-10-24.md'
NEW_INPUTS = {
    'analysis/eacc_hycom_source_resume_v1.py', 'analysis/test_eacc_hycom_source_resume_v1.py',
    'analysis/run_eacc_hycom_source_resume_v2.py', 'analysis/test_run_eacc_hycom_source_resume_v2.py',
    WORKFLOW, PROTOCOL, ROLE, CORE_PREFLIGHT,
    'research/eacc-hycom-source-resume-startup-failure-v1.json',
    '.github/workflows/davidson-width-candidate.yml', '.github/workflows/baffin-bound-candidate.yml',
}


def required_paths(root, review_path):
    """Keep the complete executed freeze and explicitly bind new adapter code."""
    paths = original.required_input_paths(root) | NEW_INPUTS | {review_path}
    for name in sorted(paths):
        if not name.endswith('.py'):
            continue
        for node in ast.walk(ast.parse(_read(root, name).decode('utf8'))):
            modules = [item.name for item in node.names] if isinstance(node, ast.Import) else [node.module] if isinstance(node, ast.ImportFrom) and node.module else []
            for module in modules:
                candidate = 'analysis/' + module.split('.')[0] + '.py'
                if (root / candidate).is_file() and candidate not in paths:
                    raise ValueError('Unfrozen adapter import: ' + candidate)
    return paths


def verify_gate(root, env):
    root = Path(root).resolve()
    if (env.get('GITHUB_ACTIONS') != 'true' or env.get('GITHUB_REPOSITORY') != original.REPOSITORY
            or env.get('GITHUB_REF') != original.REF or env.get('RUNNER_OS') != 'Linux'):
        raise ValueError('Source continuation requires the declared Linux GitHub working-branch job')
    if Path(env.get('GITHUB_WORKSPACE', '')).resolve() != root:
        raise ValueError('Unexpected cloud workspace')
    affinity = getattr(os, 'sched_getaffinity', None)
    if affinity is None or len(affinity(0)) != 1 or any(env.get(key) != '1' for key in
            ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS')):
        raise ValueError('One CPU and one numerical worker are required')
    if any(not re.fullmatch(r'[1-9]\d*', env.get(key, '')) for key in ('GITHUB_RUN_ID', 'GITHUB_RUN_ATTEMPT')):
        raise ValueError('Missing continuation run identity')
    if not re.fullmatch('[0-9a-f]{40}', env.get('GITHUB_SHA', '')) or _git(root, 'rev-parse', 'HEAD').decode().strip() != env['GITHUB_SHA']:
        raise ValueError('Changed source checkout identity')
    if _git(root, 'status', '--porcelain', '--untracked-files=no').strip():
        raise ValueError('Continuation needs clean committed inputs')
    phase_raw = _read(root, original.PHASE, 8192); phase = json.loads(phase_raw)
    if (phase.get('phase') != PHASE_NAME or phase.get('heavy_work_permitted') is not True
            or phase.get('max_heavy_local_jobs') != 0 or phase.get('max_heavy_cloud_jobs') != 1
            or phase.get('execution_workflow') != WORKFLOW
            or phase_raw != _git(root, 'show', 'HEAD:' + original.PHASE)):
        raise ValueError('Saved-source continuation phase is not committed/enabled')
    path = phase.get('preflight', '')
    if not re.fullmatch(r'research/eacc-hycom-source-resume-preflight-v[1-9]\d*(?:-case[1-9]\d*)?\.json', path):
        raise ValueError('Invalid versioned continuation preflight path')
    raw = _read(root, path, 262144)
    if digest(raw) != phase.get('preflight_sha256') or raw != _git(root, 'show', 'HEAD:' + path):
        raise ValueError('Changed continuation preflight')
    preflight = json.loads(raw)
    if (preflight.get('schema') != 'osw.eacc-hycom.source-resume-preflight.v1'
            or preflight.get('workflow') != WORKFLOW or preflight.get('original_core_preflight_sha256') != CORE_SHA
            or preflight.get('socket_timeout_seconds') != 50
            or preflight.get('original_velocity_execution_permitted') is not True
            or preflight.get('current_measurement_admission_permitted') is not False):
        raise ValueError('Changed continuation scope or transport declaration')
    review_path = preflight.get('source_review', '')
    if not re.fullmatch(r'research/eacc[a-z0-9-]+\.json', review_path):
        raise ValueError('Invalid source review path')
    core_raw = _read(root, CORE_PREFLIGHT, 262144)
    if digest(core_raw) != CORE_SHA:
        raise ValueError('Executed original preflight changed')
    core = json.loads(core_raw)
    if len(core['input_sha256']) != 40 or set(core['input_sha256']) != original.required_input_paths(root):
        raise ValueError('Executed original scientific freeze is incomplete')
    pins = preflight.get('input_sha256', {})
    if set(pins) != required_paths(root, review_path):
        raise ValueError('Incomplete continuation dependency freeze')
    for name, expected in pins.items():
        item = _read(root, name)
        if digest(item) != expected or item != _git(root, 'show', 'HEAD:' + name):
            raise ValueError('Changed/uncommitted continuation input: ' + name)
    if any(pins[name] != expected for name, expected in core['input_sha256'].items()):
        raise ValueError('Executed scientific inputs cannot change in continuation')
    review = json.loads(_read(root, review_path, 262144))
    if review['preflight_sha256'] != CORE_SHA or review.get('source_compilation_completed') is not False:
        raise ValueError('Source basis is not the reviewed incomplete original method')
    if platform.python_version() != preflight.get('python_exact') or preflight.get('python_exact') != review.get('python'):
        raise ValueError('Python patch version must match the declared continuation')
    for line in _read(root, original.REQUIREMENTS, 8192).decode().splitlines():
        if line.strip() and not line.startswith('#'):
            package, version = line.split('==')
            if importlib.metadata.version(package) != version:
                raise ValueError('Changed numeric/reader package: ' + package)
    return preflight, core, review, raw


def verify_artifact(metadata, review):
    expected = review['artifact']
    if (metadata.get('id') != expected['id'] or metadata.get('name') != expected['name']
            or metadata.get('size_in_bytes') != expected['zip_bytes'] or metadata.get('expired') is not False
            or metadata.get('workflow_run', {}).get('id') != review['run_id']
            or metadata.get('workflow_run', {}).get('head_sha') != review['source_commit']):
        raise ValueError('Wrong/expired saved source artifact')
    if expected.get('github_reported_digest') and metadata.get('digest') != expected['github_reported_digest']:
        raise ValueError('Saved artifact digest changed')


def run_case(root, env, basis, artifact_metadata):
    root = Path(root).resolve()
    preflight, core, review, preflight_raw = verify_gate(root, env)
    verify_artifact(json.loads(_read(root, artifact_metadata, 131072)), review)
    basis = Path(basis).resolve()
    if not basis.is_relative_to(root):
        raise ValueError('Saved source must be restored inside the cloud workspace')
    selection = json.loads(_read(root, original.SELECTION, 131072))
    output = root / '.pytest_cache/eacc-source-resume-v2' / ('run-' + env['GITHUB_RUN_ID'] + '-attempt-' + env['GITHUB_RUN_ATTEMPT'])
    from eacc_hycom_source_resume_v1 import resume_responses, review_projection
    def ready(directory):
        _write_once(directory / 'resume-preflight.json', preflight_raw)
        _write_once(directory / 'environment.json', encoded({
            'source_commit': env['GITHUB_SHA'], 'run_id': int(env['GITHUB_RUN_ID']),
            'run_attempt': int(env['GITHUB_RUN_ATTEMPT']), 'python': platform.python_version(),
            'platform': platform.platform(), 'scientific_input_sha256': core['input_sha256'],
            'continuation_input_sha256': preflight['input_sha256'],
            'original_core_preflight_sha256': CORE_SHA, 'logical_cpu_limit': 1,
            'max_concurrent_requests': 1, 'socket_timeout_seconds': 50}))
    try:
        completed = resume_responses(basis, output, selection, review, ready=ready)
        from eacc_hycom_source_compilation_v1 import compile_source
        metadata = {name: _read(root, path, 262144) for name, path in original.METADATA.items()}
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
        lineage = json.loads(_read(output, 'source-lineage.json', 262144))
        projection = review_projection(fields, diagnostic, lineage)
        _write_once(output / 'review-summary.json', encoded(projection))
        from eacc_model_core_figures_v1 import render_case
        render_case(fields, diagnostic, output / 'figures', rasterize=True)
        result = {'schema': 'osw.eacc-hycom.source-resume-result.v1',
                  'status': 'completed_source_and_diagnostic_not_measurement_admission',
                  'run_id': int(env['GITHUB_RUN_ID']), 'run_attempt': int(env['GITHUB_RUN_ATTEMPT']),
                  'source_commit': env['GITHUB_SHA'], 'reused_requests': len(review['source_responses']),
                  'new_requests': len(completed) - len(review['source_responses']),
                  'total_requests': len(completed), 'cases': len(diagnostic['cases']),
                  'monthly_fields_sha256': digest(encoded(fields)), 'diagnostic_sha256': digest(encoded(diagnostic)),
                  'review_summary_sha256': digest(encoded(projection)), 'original_core_preflight_sha256': CORE_SHA,
                  'current_association_verified': False, 'new_current_widths_admitted': 0,
                  'physical_annual_range_admitted': False, 'main_merged': False}
        _write_once(output / 'result.json', encoded(result)); print(json.dumps(result, indent=2), flush=True)
    except Exception as error:
        if output.is_dir() and not (output / 'case-failure.json').exists():
            _write_once(output / 'case-failure.json', encoded({
                'status': 'source_continuation_failed_retained_no_retry', 'error_type': type(error).__name__,
                'error': str(error)[:2048], 'source_commit': env['GITHUB_SHA'],
                'run_id': int(env['GITHUB_RUN_ID']), 'new_current_widths_admitted': 0}))
        raise
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--verify-cloud-gate', action='store_true')
    group.add_argument('--cloud-continue', action='store_true')
    parser.add_argument('--basis', type=Path)
    parser.add_argument('--artifact-metadata', default='.pytest_cache/eacc-resume-artifact-metadata.json')
    args = parser.parse_args(); root = Path(__file__).resolve().parents[1]
    if args.verify_cloud_gate:
        verify_gate(root, dict(os.environ)); print('saved-source gate verified; provider not accessed')
    elif args.basis is None:
        parser.error('--basis is required for cloud continuation')
    else:
        run_case(root, dict(os.environ), args.basis, args.artifact_metadata)
