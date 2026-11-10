"""Fictional gate, tiny saved JSON and offline checkout; no ocean data or network."""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap

import pytest
import yaml

import run_eacc_coastal_reference_extent_case_v1 as runner


@pytest.fixture
def gate(tmp_path,monkeypatch):
    def write(name,raw):
        path=tmp_path/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    old_names={runner.REVIEW,runner.REQUIREMENTS,runner.MAP_MANIFEST}|{f'science/{n}.json' for n in range(49)}
    support_names={runner.REVIEW}|{f'support/{n}.json' for n in range(10)}
    prototype_names={'analysis/synthetic_operator.py','plans/synthetic_protocol.md'}
    paths=old_names|support_names|prototype_names|runner.EXTRA_INPUTS
    for name in paths:write(name,b'# synthetic\n' if name.endswith('.py') else b'{}\n')
    write(runner.REQUIREMENTS,b'pytest==8.4.2\nPyYAML==6.0.3\n')
    review={'run_id':runner.SOURCE_RUN,'run_attempt':2,'source_commit':runner.SOURCE_COMMIT,
        'run_conclusion':'success','cloud_output_fingerprints':{
            'diagnostic_sha256':runner.DIAGNOSTIC_SHA,'monthly_fields_sha256':runner.FIELDS_SHA}}
    write(runner.REVIEW,runner.encoded(review))
    def pins(names):return {name:runner.digest((tmp_path/name).read_bytes()) for name in names}
    write(runner.CONTINUATION,runner.encoded({'input_sha256':pins(old_names)}))
    write(runner.SUPPORT,runner.encoded({'input_sha256':pins(support_names)}))
    write(runner.PROTOTYPE,runner.encoded({'source_sha256':pins(prototype_names)}))
    preflight={'schema':'osw.eacc-coastal-reference-extent-preflight.v1','workflow':runner.WORKFLOW,
        'python_exact':'3.14.8','saved_profile_extent_execution_permitted':True,
        'provider_requests_permitted':False,'original_producer_rerun_permitted':False,
        'measurement_admission_permitted':False,'max_report_bytes':2097152,'max_summary_bytes':524288,
        'basis_member_sha256':dict(runner.BASIS_MEMBERS),'input_sha256':pins(paths)}
    request={'schema':'osw.eacc-coastal-reference-extent-request.v1','execution_permitted':True,
        'saved_derived_profile_review_only':True,'metadata_projection_only':False,
        'provider_requests_permitted':False,'original_producer_rerun_permitted':False,
        'measurement_admission_permitted':False,'max_heavy_local_jobs':0,'max_cloud_jobs':1,
        'workflow':runner.WORKFLOW,'preflight':runner.PREFLIGHT}
    phase={'phase':'source-review-only-v1','heavy_work_permitted':False,
        'max_heavy_local_jobs':0,'max_heavy_cloud_jobs':1}
    snapshots={}
    def commit():
        write(runner.PREFLIGHT,runner.encoded(preflight))
        request['preflight_sha256']=runner.digest((tmp_path/runner.PREFLIGHT).read_bytes())
        write(runner.REQUEST,runner.encoded(request));write(runner.PHASE,runner.encoded(phase))
        for name in paths|{runner.REQUEST,runner.PREFLIGHT,runner.PHASE}:
            snapshots[name]=(tmp_path/name).read_bytes()
    commit()
    env={'GITHUB_ACTIONS':'true','GITHUB_REPOSITORY':'giodl73-repo/OSW',
        'GITHUB_REF':'refs/heads/codex/current-measurement-gaps','RUNNER_OS':'Linux',
        'GITHUB_WORKSPACE':str(tmp_path),'GITHUB_SHA':'a'*40,'GITHUB_RUN_ID':'123','GITHUB_RUN_ATTEMPT':'1',
        **{key:'1' for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')}}
    def git(root,*args):
        if args==('rev-parse','HEAD'):return b'a'*40+b'\n'
        if args[0]=='status':return b''
        if args[0]=='show':return snapshots[args[1].removeprefix('HEAD:')]
        pytest.fail('Unexpected Git operation')
    monkeypatch.setattr(runner,'git',git)
    monkeypatch.setattr(runner.os,'sched_getaffinity',lambda _:{3},raising=False)
    monkeypatch.setattr(runner.platform,'python_version',lambda:'3.14.8')
    monkeypatch.setattr(runner.importlib.metadata,'version',lambda name:{'pytest':'8.4.2','PyYAML':'6.0.3'}[name])
    return tmp_path,env,request,phase,preflight,commit


def test_complete_fictional_gate_requires_no_source_artifact(gate):
    root,env,request,*_=gate
    assert runner.verify_gate(root,env)[0]==request
    assert not (root/'.pytest_cache').exists()


@pytest.mark.parametrize('key,value',[
    ('GITHUB_ACTIONS','false'),('GITHUB_REPOSITORY','other/repo'),('RUNNER_OS','Windows'),
    ('GITHUB_REF','refs/heads/main'),('GITHUB_RUN_ATTEMPT','0'),('GITHUB_SHA','b'*40),
    ('GITHUB_RUN_ID',''),('OPENBLAS_NUM_THREADS','2')])
def test_incorrect_cloud_context_is_refused(gate,key,value):
    root,env,*_=gate
    with pytest.raises(ValueError):runner.verify_gate(root,{**env,key:value})


def test_local_invocation_is_refused_before_reading_files(tmp_path,monkeypatch):
    def unexpected(*args,**kwargs):pytest.fail('Local invocation read a file')
    monkeypatch.setattr(runner,'read',unexpected)
    with pytest.raises(ValueError,match='cloud working branch'):
        runner.run_case(tmp_path,{},tmp_path/'missing')
    assert list(tmp_path.iterdir())==[]


@pytest.mark.parametrize('which,key,value',[
    ('request','execution_permitted',False),('request','metadata_projection_only',True),
    ('request','saved_derived_profile_review_only',False),('request','provider_requests_permitted',True),
    ('request','original_producer_rerun_permitted',True),('request','measurement_admission_permitted',True),
    ('request','max_cloud_jobs',2),('phase','heavy_work_permitted',True),('phase','max_heavy_local_jobs',1),
    ('preflight','saved_profile_extent_execution_permitted',False),('preflight','provider_requests_permitted',True),
    ('preflight','original_producer_rerun_permitted',True),('preflight','measurement_admission_permitted',True),
    ('preflight','python_exact','3.14.7'),('preflight','max_report_bytes',4194304),
    ('preflight','max_summary_bytes',1048576),('preflight','basis_member_sha256',{})])
def test_scope_and_resource_limits_cannot_be_relaxed(gate,which,key,value):
    root,env,request,phase,preflight,commit=gate
    {'request':request,'phase':phase,'preflight':preflight}[which][key]=value;commit()
    with pytest.raises(ValueError):runner.verify_gate(root,env)


def test_actual_multiple_cpus_are_refused(gate,monkeypatch):
    root,env,*_=gate
    monkeypatch.setattr(runner.os,'sched_getaffinity',lambda _:{1,2},raising=False)
    with pytest.raises(ValueError,match='One actual CPU'):runner.verify_gate(root,env)


def test_uncommitted_input_is_refused(gate):
    root,env,*_=gate
    (root/runner.WORKFLOW).write_bytes(b'changed')
    with pytest.raises(ValueError,match='input'):runner.verify_gate(root,env)


def test_repinning_executed_input_cannot_override_old_freeze(gate):
    root,env,_,_,pref,commit=gate
    name='science/0.json';(root/name).write_bytes(b'changed')
    pref['input_sha256'][name]=runner.digest((root/name).read_bytes());commit()
    with pytest.raises(ValueError,match='All62'):runner.verify_gate(root,env)


def test_repinning_synthetic_operator_cannot_override_preparation_review(gate):
    root,env,_,_,pref,commit=gate
    name='analysis/synthetic_operator.py';(root/name).write_bytes(b'# changed\n')
    pref['input_sha256'][name]=runner.digest((root/name).read_bytes());commit()
    with pytest.raises(ValueError,match='Synthetic-reviewed'):runner.verify_gate(root,env)


def test_repository_import_must_be_inside_freeze(gate):
    root,env,_,_,pref,commit=gate
    (root/'analysis/unfrozen.py').write_bytes(b'# synthetic\n')
    name='analysis/synthetic_operator.py';(root/name).write_bytes(b'import unfrozen\n')
    pref['input_sha256'][name]=runner.digest((root/name).read_bytes());commit()
    with pytest.raises(ValueError,match='Unfrozen source dependency'):runner.verify_gate(root,env)


def test_changed_installed_dependency_is_refused(gate,monkeypatch):
    root,env,*_=gate
    monkeypatch.setattr(runner.importlib.metadata,'version',lambda name:'0.0.0')
    with pytest.raises(ValueError,match='scientific dependency'):runner.verify_gate(root,env)


@pytest.fixture
def saved_basis(tmp_path,monkeypatch):
    basis=tmp_path/'basis';basis.mkdir()
    identity={'run_id':runner.SOURCE_RUN,'run_attempt':2,'source_commit':runner.SOURCE_COMMIT}
    bodies={name:runner.encoded(identity if name in ('result.json','environment.json') else {'synthetic':name})
        for name in runner.BASIS_MEMBERS}
    for name,raw in bodies.items():
        target=basis/name;target.parent.mkdir(exist_ok=True,parents=True);target.write_bytes(raw)
    target=tmp_path/runner.MAP_MANIFEST;target.parent.mkdir(parents=True)
    target.write_bytes(bodies['figures/manifest.json'])
    pins={name:runner.digest(raw) for name,raw in bodies.items()}
    monkeypatch.setattr(runner,'BASIS_MEMBERS',pins)
    return tmp_path,basis,pins


def test_verified_tiny_saved_basis_parses_only_after_byte_checks(saved_basis):
    root,basis,pins=saved_basis
    diagnostic,fields,manifest=runner.load_saved_basis(root,basis,pins)
    assert diagnostic=={'synthetic':'diagnostic.json'} and fields=={'synthetic':'monthly-fields.json'}
    assert manifest=={'synthetic':'figures/manifest.json'}


@pytest.mark.parametrize('name',list(runner.BASIS_MEMBERS))
def test_any_changed_saved_member_is_refused_before_parsing(saved_basis,name):
    root,basis,pins=saved_basis;(basis/name).write_bytes(b'not JSON')
    with pytest.raises(ValueError,match='Saved original input changed'):
        runner.load_saved_basis(root,basis,pins)


def test_incomplete_custody_is_refused(saved_basis):
    root,basis,pins=saved_basis
    with pytest.raises(ValueError,match='source custody'):runner.load_saved_basis(root,basis,{})


def test_saved_basis_cannot_escape_workspace(saved_basis):
    root,basis,pins=saved_basis
    with pytest.raises(ValueError,match='cloud workspace'):runner.load_saved_basis(root,root.parent,pins)


def test_source_identity_and_map_manifest_still_checked_after_fingerprints(saved_basis):
    root,basis,pins=saved_basis
    raw=runner.encoded({'run_id':runner.SOURCE_RUN,'run_attempt':1,'source_commit':runner.SOURCE_COMMIT})
    (basis/'result.json').write_bytes(raw);pins['result.json']=runner.digest(raw)
    with pytest.raises(ValueError,match='source run identity'):runner.load_saved_basis(root,basis,pins)


def test_original_map_manifest_must_equal_reviewed_bytes(saved_basis):
    root,basis,pins=saved_basis;(root/runner.MAP_MANIFEST).write_bytes(b'{}\n')
    with pytest.raises(ValueError,match='source map manifest'):runner.load_saved_basis(root,basis,pins)


def test_compact_review_retains_all_attempts_and_original_failures():
    keys=('quantity','status','extent_bracket_km','maximum_native_cell_scale_km',
        'minimum_span_in_native_cell_scales','source_scale_gate_passed','resolution_status',
        'conditional_on_inshore_flow_assumption','whole_current_width_km','width_rank_eligible',
        'physical_state_join_eligible','physical_uncertainty_km')
    cases=[]
    for m in range(1,13):
        for offset in (-1,0,1):
            for step in (5,10):
                variants=[]
                for fraction in (.4,.5,.6):
                    metrics=[]
                    for quantity in ('core','paired','support','shore'):
                        metric={key:None for key in keys}
                        metric.update(quantity=quantity,status='unresolved',width_rank_eligible=False,
                            physical_state_join_eligible=False,source_scale_gate_passed=False)
                        metrics.append(metric)
                    variants.append({'fraction':fraction,'metrics':metrics})
                cases.append({'case_id':f'm{m:02d}:offset{offset}:step{step}',
                    'source_status':'missing_search_endpoint','legacy_regional_gate':{'passed':False},
                    'adapter_audit':{'retained':True},'status':'unresolved','variants':variants})
    report={'source':{'run':123},'scope':'synthetic','cases':cases};before=deepcopy(report)
    summary=runner.compact_report(report)
    assert report==before and len(summary['cases'])==72
    assert sum(len(case['metrics']) for case in summary['cases'])==864
    assert all(case['legacy_regional_gate']=={'passed':False} for case in summary['cases'])
    assert summary['physical_annual_width_range_km'] is None and not summary['current_association_verified']
    assert summary['new_current_measurements_admitted']==0


def workflow():
    return yaml.safe_load((Path(__file__).resolve().parents[1]/runner.WORKFLOW).read_bytes())


def test_workflow_is_serial_gated_and_does_not_launch_acquisition():
    value=workflow()
    assert value['concurrency']=={'group':'osw-current-gap-delivery','cancel-in-progress':False}
    assert set(value['env'].values())=={'1'}
    job=value['jobs']['derive-saved-extents'];assert job['timeout-minutes']==15
    steps=job['steps'];assert all(step.get('if')=="steps.request.outputs.enabled == 'true'" for step in steps[2:-1])
    text='\n'.join(step.get('run','') for step in steps)
    assert '--cloud-derived-case' in text and 'diagnose_year(' not in text
    assert 'sparse-checkout\',\'set\',\'--no-cone' in text and "'sparse-checkout','add'" not in text
    download=next(s for s in steps if s.get('uses','').startswith('actions/download-artifact'))
    assert download['with']['run-id']==runner.SOURCE_RUN
    for step in steps:
        script=step.get('run','')
        if "python - <<'PY'\n" in script:
            compile(script.split("python - <<'PY'\n",1)[1].rsplit('\nPY',1)[0],'<workflow>','exec')


def test_actual_sparse_bootstrap_restores_tiny_frozen_files_offline(tmp_path):
    """Exercise the actual embedded checkout script, not a mirrored implementation."""
    git=['git','-c','core.fsmonitor=false','-c','maintenance.auto=0','-c','gc.auto=0','-C',str(tmp_path)]
    def call(*args):return subprocess.check_output(git+list(args),stderr=subprocess.STDOUT)
    def write(name,raw):
        target=tmp_path/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    call('init','--quiet');call('config','core.autocrlf','false')
    pins={}
    for i in range(62):
        name=f'analysis/tiny-{i}.txt';raw=f'synthetic{i}\n'.encode();write(name,raw);pins[name]=runner.digest(raw)
    pref=runner.encoded({'input_sha256':pins});write(runner.PREFLIGHT,pref)
    write(runner.PHASE,runner.encoded({'phase':'source-review-only-v1','heavy_work_permitted':False,
        'max_heavy_local_jobs':0,'max_heavy_cloud_jobs':1}))
    write(runner.REQUEST,runner.encoded({'execution_permitted':True,'saved_derived_profile_review_only':True,
        'metadata_projection_only':False,'provider_requests_permitted':False,
        'original_producer_rerun_permitted':False,'measurement_admission_permitted':False,
        'preflight':runner.PREFLIGHT,'preflight_sha256':runner.digest(pref)}))
    write('unrelated/large-placeholder.txt',b'must not restore\n')
    call('add','.');call('-c','user.name=Synthetic','-c','user.email=synthetic@example.invalid',
        '-c','commit.gpgsign=false','commit','--quiet','-m','tiny offline fixture')
    call('sparse-checkout','set','--no-cone',runner.PHASE,runner.REQUEST)
    assert not (tmp_path/'analysis/tiny-0.txt').exists()
    step=next(step for step in workflow()['jobs']['derive-saved-extents']['steps']
        if step.get('name')=='Restore frozen projection input set')
    script=step['run'].split("python - <<'PY'\n",1)[1].rsplit('\nPY',1)[0]
    env={**os.environ,'GITHUB_REF':'refs/heads/codex/current-measurement-gaps'}
    subprocess.run([sys.executable,'-c',textwrap.dedent(script)],cwd=tmp_path,env=env,
        check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
    assert all(runner.digest((tmp_path/name).read_bytes())==sha for name,sha in pins.items())
    assert not (tmp_path/'unrelated/large-placeholder.txt').exists()
    assert call('status','--porcelain','--untracked-files=no')==b''
