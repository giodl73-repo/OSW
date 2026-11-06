"""Small fictional gate fixtures; no original arrays, provider or Git mutation."""
import json
from pathlib import Path

import pytest
import yaml

import run_eacc_hycom_source_resume_v1 as runner
from eacc_hycom_cloud_acquisition_v2 import digest, encoded


@pytest.fixture
def frozen(tmp_path, monkeypatch):
    old = {'research/fictional-%02d.json' % i for i in range(39)} | {runner.original.REQUIREMENTS}
    review_path = 'research/eacc-fictional-review.json'
    for name in old | runner.NEW_INPUTS | {review_path}:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'# fictional\n' if name.endswith('.py') else b'{}\n')
    (tmp_path / runner.original.REQUIREMENTS).write_bytes(b'numpy==2.4.1\n')
    core = {'input_sha256': {name: digest((tmp_path/name).read_bytes()) for name in old}}
    core_raw = encoded(core)
    (tmp_path/runner.CORE_PREFLIGHT).write_bytes(core_raw)
    monkeypatch.setattr(runner, 'CORE_SHA', digest(core_raw))
    monkeypatch.setattr(runner.original, 'required_input_paths', lambda _: old)
    monkeypatch.setattr(runner.os, 'sched_getaffinity', lambda _: {3}, raising=False)
    monkeypatch.setattr(runner.platform, 'python_version', lambda: '3.14.8')
    monkeypatch.setattr(runner.importlib.metadata, 'version', lambda _: '2.4.1')
    review = {'preflight_sha256': digest(core_raw), 'source_compilation_completed': False, 'python': '3.14.8'}
    (tmp_path/review_path).write_bytes(encoded(review))
    preflight_path = 'research/eacc-hycom-source-resume-preflight-v1.json'
    preflight = {'schema': 'osw.eacc-hycom.source-resume-preflight.v1', 'workflow': runner.WORKFLOW,
                 'original_core_preflight_sha256': digest(core_raw), 'socket_timeout_seconds': 50,
                 'original_velocity_execution_permitted': True, 'current_measurement_admission_permitted': False,
                 'source_review': review_path, 'python_exact': '3.14.8',
                 'input_sha256': {name: digest((tmp_path/name).read_bytes()) for name in old | runner.NEW_INPUTS | {review_path}}}
    phase = {'phase': runner.PHASE_NAME, 'heavy_work_permitted': True,
             'max_heavy_local_jobs': 0, 'max_heavy_cloud_jobs': 1,
             'execution_workflow': runner.WORKFLOW, 'preflight': preflight_path}
    snapshots = {}
    def commit():
        raw = encoded(preflight)
        (tmp_path/preflight_path).write_bytes(raw)
        phase['preflight_sha256'] = digest(raw)
        (tmp_path/runner.original.PHASE).write_bytes(encoded(phase))
        for name in set(preflight['input_sha256']) | {preflight_path, runner.original.PHASE}:
            snapshots[name] = (tmp_path/name).read_bytes()
    commit()
    env = {'GITHUB_ACTIONS': 'true', 'GITHUB_REPOSITORY': runner.original.REPOSITORY,
           'GITHUB_REF': runner.original.REF, 'RUNNER_OS': 'Linux', 'GITHUB_WORKSPACE': str(tmp_path),
           'GITHUB_SHA': 'a'*40, 'GITHUB_RUN_ID': '123', 'GITHUB_RUN_ATTEMPT': '1',
           **{name: '1' for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')}}
    def git(root, *args):
        if args == ('rev-parse', 'HEAD'): return b'a'*40 + b'\n'
        if args[0] == 'status': return b''
        if args[0] == 'show': return snapshots[args[1].removeprefix('HEAD:')]
        pytest.fail('Unexpected Git operation')
    monkeypatch.setattr(runner, '_git', git)
    return tmp_path, env, phase, preflight, commit


def test_complete_gate_without_source_io(frozen):
    root, env, _, preflight, _ = frozen
    assert runner.verify_gate(root, env)[0] == preflight
    assert not (root/'.pytest_cache').exists()


@pytest.mark.parametrize('key,value', [('GITHUB_ACTIONS','false'),('GITHUB_REF','refs/heads/main'),
    ('RUNNER_OS','Windows'),('GITHUB_RUN_ATTEMPT','0'),('OPENBLAS_NUM_THREADS','2')])
def test_local_wrong_branch_or_worker_context_is_refused(frozen, key, value):
    root, env, *_ = frozen
    with pytest.raises(ValueError): runner.verify_gate(root, {**env, key:value})
    assert not (root/'.pytest_cache').exists()


@pytest.mark.parametrize('key,value', [('heavy_work_permitted',False),('max_heavy_cloud_jobs',2),('max_heavy_local_jobs',1)])
def test_serial_execution_gate(frozen, key, value):
    root, env, phase, _, commit = frozen
    phase[key] = value; commit()
    with pytest.raises(ValueError): runner.verify_gate(root, env)


def test_actual_affinity_required(frozen, monkeypatch):
    root, env, *_ = frozen
    monkeypatch.setattr(runner.os, 'sched_getaffinity', lambda _: {1,2}, raising=False)
    with pytest.raises(ValueError, match='One CPU'): runner.verify_gate(root, env)


@pytest.mark.parametrize('key,value', [('socket_timeout_seconds',60),('current_measurement_admission_permitted',True),
    ('python_exact','3.14.9'),('source_review','../unsafe.json')])
def test_changed_scope_or_runtime_refused(frozen, key, value):
    root, env, _, preflight, commit = frozen
    preflight[key] = value; commit()
    with pytest.raises(ValueError): runner.verify_gate(root, env)


def test_repinning_executed_science_is_refused(frozen):
    root, env, _, preflight, commit = frozen
    name = 'research/fictional-00.json'
    (root/name).write_bytes(b'{"changed":true}\n')
    preflight['input_sha256'][name] = digest((root/name).read_bytes()); commit()
    with pytest.raises(ValueError, match='scientific inputs cannot change'): runner.verify_gate(root, env)


def test_incomplete_adapter_freeze_refused(frozen):
    root, env, _, preflight, commit = frozen
    preflight['input_sha256'].pop(runner.ROLE); commit()
    with pytest.raises(ValueError, match='dependency freeze'): runner.verify_gate(root, env)


@pytest.fixture
def artifact():
    review = {'artifact': {'id': 7, 'name':'saved', 'zip_bytes':100,'github_reported_digest':'sha256:abc'},
              'run_id':123,'source_commit':'a'*40}
    metadata = {'id':7,'name':'saved','size_in_bytes':100,'expired':False,'digest':'sha256:abc',
                'workflow_run':{'id':123,'head_sha':'a'*40}}
    return metadata, review


def test_exact_artifact(artifact):
    runner.verify_artifact(*artifact)


@pytest.mark.parametrize('key,value', [('id',8),('name','different'),('expired',True),('digest','sha256:other')])
def test_mixed_or_expired_artifact_refused(artifact, key, value):
    metadata, review = artifact; metadata[key] = value
    with pytest.raises(ValueError): runner.verify_artifact(metadata, review)


def test_workflow_checks_before_restoring_bodies_and_compiles_embedded_python():
    root = Path(__file__).resolve().parents[1]
    workflow = yaml.safe_load((root/runner.WORKFLOW).read_bytes())
    assert workflow['on'] == {'workflow_call': None}
    steps = workflow['jobs']['continue-source-and-diagnose']['steps']
    names = [step.get('name','') for step in steps]
    assert next(i for i,s in enumerate(steps) if '--verify-cloud-gate' in s.get('run','')) < names.index('Restore the saved source artifact in the cloud only')
    for step in steps:
        script = step.get('run','')
        if "python - <<'PY'\n" in script:
            body = script.split("python - <<'PY'\n",1)[1].rsplit('\nPY',1)[0]
            compile(body, '<workflow>', 'exec')
    assert workflow['env']['OPENBLAS_NUM_THREADS'] == '1'


def test_only_one_parent_calls_continuation_and_holds_the_shared_lock():
    root = Path(__file__).resolve().parents[1]
    callers = []
    for name in ('davidson-width-candidate.yml','baffin-bound-candidate.yml'):
        workflow = yaml.safe_load((root/'.github/workflows'/name).read_bytes())
        assert workflow['concurrency'] == {'group':'osw-current-gap-delivery','cancel-in-progress':False}
        for job in workflow['jobs'].values():
            if job.get('uses') == './'+runner.WORKFLOW:
                assert job['if'] == "needs.select-delivery-phase.outputs.phase == 'eacc-source-resume-v1'"
                callers.append(name)
    assert callers == ['davidson-width-candidate.yml']
