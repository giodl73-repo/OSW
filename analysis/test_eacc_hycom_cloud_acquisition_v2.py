"""Fictional cloud contexts and tiny synthetic HTTP payloads; no network."""
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import sys
import urllib.error

import pytest

import eacc_hycom_cloud_acquisition_v2 as cloud
from test_eacc_hycom_source_compilation_v1 import source


@pytest.fixture
def frozen(tmp_path, monkeypatch):
    for path in cloud.ENTRYPOINTS + cloud.DOCUMENTS + tuple(cloud.METADATA.values()) + (cloud.SELECTION, cloud.WORKFLOW, cloud.REQUIREMENTS):
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b'# fictional fixture\n' if path.endswith('.py') else b'{}\n')
    (tmp_path / cloud.REQUIREMENTS).write_text('numpy==2.4.1\n', encoding='utf8')
    monkeypatch.setattr(cloud.importlib.metadata, 'version', lambda package: '2.4.1')
    monkeypatch.setattr(cloud.os, 'sched_getaffinity', lambda _: {7}, raising=False)
    snapshots = {}
    preflight = {
        'schema': 'osw.eacc-regional-model-core.preflight.v2',
        'execution_revision': 2,
        'original_velocity_execution_permitted': True, 'current_measurement_admission_permitted': False,
        'selection': cloud.SELECTION, 'selection_sha256': cloud.digest((tmp_path / cloud.SELECTION).read_bytes()),
        'workflow': cloud.WORKFLOW, 'metadata_paths': cloud.METADATA,
        'requirements': cloud.REQUIREMENTS, 'python_major_minor': list(sys.version_info[:2]),
        'input_sha256': {path: cloud.digest((tmp_path / path).read_bytes()) for path in cloud.required_input_paths(tmp_path)}}
    phase = {'phase': cloud.PHASE_NAME, 'heavy_work_permitted': True,
             'max_heavy_local_jobs': 0, 'max_heavy_cloud_jobs': 1,
             'execution_workflow': cloud.WORKFLOW, 'preflight': cloud.PREFLIGHT}
    def recommit():
        (tmp_path / cloud.PREFLIGHT).write_bytes(cloud.encoded(preflight))
        phase['preflight_sha256'] = cloud.digest((tmp_path / cloud.PREFLIGHT).read_bytes())
        (tmp_path / cloud.PHASE).write_bytes(cloud.encoded(phase))
        for path in set(preflight['input_sha256']) | {cloud.PHASE, cloud.PREFLIGHT}:
            snapshots[path] = (tmp_path / path).read_bytes()
    recommit()
    env = {'GITHUB_ACTIONS': 'true', 'GITHUB_REPOSITORY': cloud.REPOSITORY, 'GITHUB_REF': cloud.REF,
           'GITHUB_SHA': 'a' * 40, 'GITHUB_RUN_ID': '123', 'GITHUB_RUN_ATTEMPT': '1',
           'GITHUB_WORKSPACE': str(tmp_path), 'RUNNER_OS': 'Linux',
           **{key: '1' for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS')}}
    def git(root, *args):
        if args == ('rev-parse', 'HEAD'): return b'a' * 40 + b'\n'
        if args[:1] == ('status',): return b''
        if args[:1] == ('show',): return snapshots[args[1].removeprefix('HEAD:')]
        pytest.fail('Unexpected Git command in fictional gate')
    monkeypatch.setattr(cloud, '_git', git)
    return tmp_path, env, phase, preflight, snapshots, recommit


def test_complete_fictional_freeze_validates_without_acquisition(frozen):
    root, env, _, preflight, _, _ = frozen
    result, selection = cloud.verify_gate(root, env)
    assert result == preflight and selection == {}
    assert not (root / '.pytest_cache').exists()


@pytest.mark.parametrize('key,value', [
    ('GITHUB_ACTIONS', 'false'), ('GITHUB_REPOSITORY', 'other/repo'), ('GITHUB_REF', 'refs/heads/main'),
    ('RUNNER_OS', 'Windows'), ('GITHUB_RUN_ID', ''), ('GITHUB_RUN_ATTEMPT', '0'),
    ('GITHUB_SHA', 'b' * 40), ('GITHUB_WORKSPACE', '/another-workspace'),
    ('OPENBLAS_NUM_THREADS', '2'), ('OMP_NUM_THREADS', '8'),
])
def test_wrong_cloud_context_or_resource_limits_fail_without_output(frozen, key, value):
    root, env, *_ = frozen
    with pytest.raises(ValueError):
        cloud.verify_gate(root, {**env, key: value})
    assert not (root / '.pytest_cache').exists()


def test_multiple_cpu_affinity_is_refused_even_when_worker_env_claims_one(frozen, monkeypatch):
    root, env, *_ = frozen
    monkeypatch.setattr(cloud.os, 'sched_getaffinity', lambda _: {1, 2}, raising=False)
    with pytest.raises(ValueError, match='one CPU'):
        cloud.verify_gate(root, env)


@pytest.mark.parametrize('key,value', [
    ('phase', 'source-review-only-v1'), ('heavy_work_permitted', False),
    ('max_heavy_local_jobs', 1), ('max_heavy_cloud_jobs', 2),
    ('execution_workflow', 'other.yml'), ('preflight', 'other.json'),
])
def test_inactive_or_unserialized_phase_cannot_start_original_work(frozen, key, value):
    root, env, phase, _, _, recommit = frozen
    phase[key] = value
    recommit()
    with pytest.raises(ValueError):
        cloud.verify_gate(root, env)


@pytest.mark.parametrize('key,value', [
    ('schema', 'other'), ('original_velocity_execution_permitted', False),
    ('current_measurement_admission_permitted', True), ('selection', 'wrong.json'),
    ('selection_sha256', '0' * 64), ('python_major_minor', [0, 0]),
])
def test_wrong_scientific_scope_or_runtime_is_refused(frozen, key, value):
    root, env, _, preflight, _, recommit = frozen
    preflight[key] = value
    recommit()
    with pytest.raises(ValueError):
        cloud.verify_gate(root, env)


def test_omitted_scientific_dependency_is_refused(frozen):
    root, env, _, preflight, _, recommit = frozen
    preflight['input_sha256'].pop(cloud.ENTRYPOINTS[0])
    recommit()
    with pytest.raises(ValueError, match='dependency freeze'):
        cloud.verify_gate(root, env)


def test_changed_input_cannot_become_an_original_case(frozen):
    root, env, *_ = frozen
    (root / cloud.ENTRYPOINTS[2]).write_text('# changed scientific algorithm\n')
    with pytest.raises(ValueError, match='scientific input'):
        cloud.verify_gate(root, env)


def test_input_hash_alone_does_not_allow_uncommitted_changes(frozen):
    root, env, phase, preflight, snapshots, _ = frozen
    name = cloud.ENTRYPOINTS[2]
    (root / name).write_text('# uncommitted algorithm\n')
    preflight['input_sha256'][name] = cloud.digest((root / name).read_bytes())
    (root / cloud.PREFLIGHT).write_bytes(cloud.encoded(preflight))
    phase['preflight_sha256'] = cloud.digest((root / cloud.PREFLIGHT).read_bytes())
    (root / cloud.PHASE).write_bytes(cloud.encoded(phase))
    snapshots[cloud.PREFLIGHT] = (root / cloud.PREFLIGHT).read_bytes()
    snapshots[cloud.PHASE] = (root / cloud.PHASE).read_bytes()
    with pytest.raises(ValueError, match='uncommitted scientific input'):
        cloud.verify_gate(root, env)


def test_dependency_scan_follows_nested_repo_imports_without_executing_them(frozen):
    root, *_ = frozen
    (root / cloud.ENTRYPOINTS[0]).write_text('import extra_scientific\n')
    (root / 'analysis/extra_scientific.py').write_text('from nested_scientific import x\n')
    (root / 'analysis/nested_scientific.py').write_text("raise RuntimeError('must not execute')\n")
    paths = cloud.required_input_paths(root)
    assert {'analysis/extra_scientific.py', 'analysis/nested_scientific.py'} <= paths


def test_local_run_refuses_before_output_or_network(tmp_path, monkeypatch):
    monkeypatch.setattr(cloud, 'acquire_responses', lambda *_: pytest.fail('Network must stay off'))
    with pytest.raises(ValueError, match='GitHub'):
        cloud.run_case(tmp_path, {})
    assert not list(tmp_path.iterdir())


class Response:
    def __init__(self, raw=b'abc', status=200, content_type='text/plain', final_url='https://example.org/source', declared=None):
        self.body = io.BytesIO(raw)
        self.status, self.url, self.reads = status, final_url, 0
        self.headers = {'Content-Type': content_type}
        if declared is not None: self.headers['Content-Length'] = declared
    def __enter__(self): return self
    def __exit__(self, *_): return False
    def read(self, size):
        self.reads += 1
        return self.body.read(size)


def use_response(monkeypatch, response):
    seen = []
    class Opener:
        def open(self, request, timeout):
            seen.append((request.full_url, timeout))
            return response
    monkeypatch.setattr(cloud.urllib.request, 'build_opener', lambda *_: Opener())
    return seen


def test_bounded_fetch_reads_one_plain_response_without_network(monkeypatch):
    response = Response(declared='3')
    seen = use_response(monkeypatch, response)
    result = cloud._fetch_response('https://example.org/source', 4)
    assert result['raw'] == b'abc' and seen == [('https://example.org/source', 30)]


@pytest.mark.parametrize('kwargs', [
    {'status': 403}, {'content_type': 'text/html'}, {'final_url': 'https://example.org/changed'},
    {'declared': '999999'}, {'declared': 'not an integer'},
])
def test_wrong_http_metadata_is_refused_before_body_read(monkeypatch, kwargs):
    response = Response(**kwargs)
    use_response(monkeypatch, response)
    with pytest.raises(ValueError):
        cloud._fetch_response('https://example.org/source', 4)
    assert response.reads == 0


@pytest.mark.parametrize('response', [Response(raw=b'abcde'), Response(raw=b'ab', declared='3')])
def test_oversized_or_truncated_response_is_not_accepted(monkeypatch, response):
    use_response(monkeypatch, response)
    with pytest.raises(ValueError):
        cloud._fetch_response('https://example.org/source', 4)


def test_redirect_handler_never_follows_a_changed_resource():
    assert cloud._NoRedirect().redirect_request(None, None, 302, '', {}, 'https://example.org/changed') is None


def test_acquisition_retains_ordered_original_synthetic_bytes_and_refuses_overwrite(source, tmp_path):
    _, original, responses = source
    plan = {**original, 'requests': original['requests'][:2]}
    by_url = {request['url']: responses[request['file']][0] for request in plan['requests']}
    seen = []
    def fetch(url, cap):
        seen.append(url)
        return {'raw': by_url[url], 'http_status': 200, 'content_type': 'text/plain', 'final_url': url}
    directory = tmp_path / 'fictional-responses'
    names = cloud.acquire_responses(directory, plan, fetch=fetch)
    assert seen == [request['url'] for request in plan['requests']]
    assert names == [request['file'] for request in plan['requests']]
    assert (directory / names[0]).read_bytes() == by_url[seen[0]]
    receipt = json.loads((directory / (names[0] + '.receipt.json')).read_bytes())
    assert receipt['selection_sha256'] == cloud.digest(cloud.encoded(plan))
    with pytest.raises(FileExistsError):
        cloud.acquire_responses(directory, plan, fetch=lambda *_: pytest.fail('Must not overwrite'))


def test_invalid_scientific_response_is_retained_and_stops_before_next_request(source, tmp_path):
    _, original, responses = source
    plan = {**original, 'requests': original['requests'][:3]}
    seen = []
    def fetch(url, cap):
        request = plan['requests'][len(seen)]
        seen.append(url)
        raw = responses[request['file']][0] if len(seen) == 1 else b'Dataset { invalid scientific payload'
        return {'raw': raw, 'http_status': 200, 'content_type': 'text/plain', 'final_url': url}
    directory = tmp_path / 'invalid-synthetic-source'
    with pytest.raises(ValueError):
        cloud.acquire_responses(directory, plan, fetch=fetch)
    assert len(seen) == 2
    failure = json.loads((directory / 'failure.json').read_bytes())
    assert failure['completed_files'] == [plan['requests'][0]['file']]
    assert failure['automatic_retry'] is False
    assert (directory / plan['requests'][1]['file']).read_bytes().startswith(b'Dataset { invalid')
    assert not (directory / plan['requests'][2]['file']).exists()


def test_transport_failure_is_not_retried_and_does_not_create_a_success_receipt(source, tmp_path):
    _, plan, _ = source
    attempts = []
    def fail(url, cap):
        attempts.append(url)
        raise urllib.error.URLError('fictional timeout')
    directory = tmp_path / 'fictional-timeout'
    with pytest.raises(urllib.error.URLError):
        cloud.acquire_responses(directory, plan, fetch=fail)
    assert len(attempts) == 1
    assert list(directory.iterdir()) == [directory / 'failure.json']


def test_reusable_workflow_yaml_and_embedded_python_are_valid():
    import yaml
    root = Path(__file__).resolve().parents[1]
    workflow = yaml.safe_load((root / cloud.WORKFLOW).read_text(encoding='utf8'))
    assert workflow['on'] == {'workflow_call': None}
    steps = workflow['jobs']['acquire-and-diagnose-eacc']['steps']
    commands = [step['run'] for step in steps if 'run' in step]
    assert all(isinstance(command, str) for command in commands)
    assert any('--only-binary=:all:' in command and cloud.REQUIREMENTS in command for command in commands)
    assert sum('analysis/eacc_hycom_cloud_acquisition_v2.py --cloud-original-case' in command for command in commands) == 1
    assert not any('analysis/eacc_hycom_cloud_acquisition_v1.py' in command for command in commands)
    for command in commands:
        if command.startswith("python - <<'PY'"):
            body = command.split('\n', 1)[1].rsplit('\nPY', 1)[0]
            compile(body, cloud.WORKFLOW, 'exec')


def test_unquoted_pip_colon_regression_is_rejected_by_real_yaml_parser():
    import yaml
    with pytest.raises(yaml.YAMLError):
        yaml.safe_load('run: python -m pip install --only-binary=:all: -r requirements.txt\n')


def test_old_execution_revision_cannot_reuse_the_new_preflight(frozen):
    root, env, _, preflight, _, recommit = frozen
    preflight['execution_revision'] = 1
    recommit()
    with pytest.raises(ValueError, match='scope/preflight'):
        cloud.verify_gate(root, env)
