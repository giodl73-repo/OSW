"""Tiny synthetic records and fictional cloud context; no original profiles or provider."""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

import eacc_diagnostic_support_inspection_v1 as inspect


@pytest.fixture
def diagnostic():
    def sample(offset,status='ok'):
        return [offset,40.0,-9.0,.01,.4,.4 if status=='ok' else None,4,3,status]
    threshold={key:False if key=='effective_resolution_verified' else None for key in inspect.THRESHOLD_KEYS}
    threshold.update(fraction=.5,status='local_axis_unresolved',diagnostic_span_km=123.456789)
    station={'station_arc_parameter_km':0,'origin_lon_lat':[40.,-9.],'bearing_degrees_true':1.,
        'peak':{'status':'supported_local_peak'},'local_candidate_axis_check':False,
        'failed_axis_checks':['synthetic_failure'],'threshold_cases':[threshold],'samples':['must not copy']}
    cases=[]
    for month in range(1,13):
        for offset in (-1,0,1):
            for step in (5,10):
                cases.append({'id':f'm{month:02d}:offset{offset}:step{step}','month':month,
                    'native_latitude_offset':offset,'normal_sample_step_km':step,'status':'synthetic_retained',
                    'anchor':{'selected_lon_lat':[40.,-9.]},'seed':{'origin_lon_lat':[40.,-9.]},
                    'refined_seed_lon_lat':None,'all_five_local_axis_checks_pass':False,
                    'all_five_half_peak_spans_resolved':False,
                    'initial_refinement':{'peak':{'status':'missing_search_endpoint'},
                        'samples':[sample(-50,'missing_paired_corner'),sample(-40),sample(-20),sample(0),
                                   sample(20),sample(40),sample(50,'outside_source')]},
                    'stations':[deepcopy(station)],'paths':['must not copy']})
    return {'schema':'osw.eacc-regional-model-core.numerical-diagnostic.v2',
            'current_association_verified':False,'cases':cases}


def test_copies_original_records_without_mutating_or_reestimating(diagnostic):
    before=deepcopy(diagnostic)
    source={'diagnostic_sha256':'a'*64,'run_id':123}
    result=inspect.project(diagnostic,source)
    assert diagnostic==before and len(result['cases'])==72
    original=diagnostic['cases'][0]; copied=result['cases'][0]
    assert copied['initial_refinement_peak']==original['initial_refinement']['peak']
    assert copied['stations'][0]['threshold_cases'][0]['diagnostic_span_km']==123.456789
    assert copied['initial_window_and_first_unsupported_samples']==original['initial_refinement']['samples']
    assert copied['source']==source
    assert 'samples' not in copied['stations'][0] and 'paths' not in copied
    copied['anchor']['selected_lon_lat'][0]=99
    assert diagnostic==before
    assert not result['numeric_producer_rerun'] and result['new_current_widths_admitted']==0


def test_missing_endpoints_are_not_invented_or_converted_to_zero(diagnostic):
    case=diagnostic['cases'][0]
    case['initial_refinement']['samples']=[row for row in case['initial_refinement']['samples'] if abs(row[0])<40]
    result=inspect.project(diagnostic,{})['cases'][0]
    assert all(not item['present_in_original'] and item['sample'] is None for item in result['search_endpoints'].values())


def test_present_but_unsupported_endpoint_is_retained_exactly(diagnostic):
    row=next(row for row in diagnostic['cases'][0]['initial_refinement']['samples'] if row[0]==-40)
    row[-1]='unsupported_rectangle'; row[3:6]=[None,None,None]
    result=inspect.project(diagnostic,{})['cases'][0]
    assert result['search_endpoints']['negative']['present_in_original']
    assert not result['search_endpoints']['negative']['supported_in_original']
    assert result['search_endpoints']['negative']['sample']==row
    assert result['first_unsupported_samples']['negative']==row


def test_successful_endpoints_are_original_rows(diagnostic):
    result=inspect.project(diagnostic,{})['cases'][0]
    assert all(row['supported_in_original'] for row in result['search_endpoints'].values())


def test_unsupported_initial_case_is_retained_without_profile(diagnostic):
    diagnostic['cases'][0]['initial_refinement']=None
    diagnostic['cases'][0]['stations']=[]
    result=inspect.project(diagnostic,{})['cases'][0]
    assert result['initial_refinement_peak'] is None and result['initial_window_and_first_unsupported_samples']==[]


@pytest.mark.parametrize('change',['missing','duplicate','identity','row_shape','row_order','duplicate_offset','admitted'])
def test_invalid_original_inventory_or_rows_are_refused(diagnostic,change):
    if change=='missing': diagnostic['cases'].pop()
    if change=='duplicate': diagnostic['cases'][-1]=deepcopy(diagnostic['cases'][0])
    if change=='identity': diagnostic['cases'][0]['id']='made-up'
    if change=='row_shape': diagnostic['cases'][0]['initial_refinement']['samples'][0].pop()
    if change=='row_order': diagnostic['cases'][0]['initial_refinement']['samples'].reverse()
    if change=='duplicate_offset': diagnostic['cases'][0]['initial_refinement']['samples'][0][0]=-40
    if change=='admitted': diagnostic['current_association_verified']=True
    with pytest.raises(ValueError): inspect.project(diagnostic,{})


@pytest.fixture
def gate(tmp_path,monkeypatch):
    def write(name,raw):
        path=tmp_path/name; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(raw)
    for name in inspect.INPUTS:
        write(name,b'# synthetic\n' if name.endswith('.py') else b'{}\n')
    write(inspect.REQUIREMENTS,b'pytest==8.4.2\nPyYAML==6.0.3\n')
    science={f'science/{i}.json':str(i).zfill(64) for i in range(40)}
    write(inspect.CORE,inspect.encoded({'input_sha256':science}))
    write(inspect.CONTINUATION,inspect.encoded({'input_sha256':science|{f'extra/{i}.json':'f'*64 for i in range(12)}}))
    review={'run_conclusion':'success','run_attempt':2,'run_id':inspect.SOURCE_RUN,
        'source_commit':inspect.SOURCE_COMMIT,'cloud_output_fingerprints':{'diagnostic_sha256':inspect.DIAGNOSTIC_SHA},
        'original_preflight_sha256':inspect.digest((tmp_path/inspect.CORE).read_bytes()),
        'continuation_preflight_sha256':inspect.digest((tmp_path/inspect.CONTINUATION).read_bytes())}
    write(inspect.REVIEW,inspect.encoded(review))
    preflight={'schema':'osw.eacc-diagnostic-support-preflight.v1','workflow':inspect.WORKFLOW,
        'numeric_producer_execution_permitted':False,'measurement_admission_permitted':False,
        'max_output_bytes':524288,'python_exact':'3.14.8',
        'input_sha256':{name:inspect.digest((tmp_path/name).read_bytes()) for name in inspect.INPUTS}}
    request={'schema':'osw.eacc-diagnostic-support-request.v1','execution_permitted':True,
        'metadata_projection_only':True,'max_heavy_local_jobs':0,'max_cloud_jobs':1,
        'workflow':inspect.WORKFLOW,'preflight':inspect.PREFLIGHT}
    phase={'phase':'source-review-only-v1','heavy_work_permitted':False,'max_heavy_local_jobs':0,'max_heavy_cloud_jobs':1}
    snapshots={}
    def commit():
        write(inspect.PREFLIGHT,inspect.encoded(preflight))
        request['preflight_sha256']=inspect.digest((tmp_path/inspect.PREFLIGHT).read_bytes())
        write(inspect.REQUEST,inspect.encoded(request));write(inspect.PHASE,inspect.encoded(phase))
        for name in inspect.INPUTS|{inspect.REQUEST,inspect.PHASE,inspect.PREFLIGHT}:
            snapshots[name]=(tmp_path/name).read_bytes()
    commit()
    env={'GITHUB_ACTIONS':'true','GITHUB_REPOSITORY':inspect.REPOSITORY,'GITHUB_REF':inspect.REF,
        'RUNNER_OS':'Linux','GITHUB_WORKSPACE':str(tmp_path),'GITHUB_SHA':'a'*40,
        'GITHUB_RUN_ID':'123','GITHUB_RUN_ATTEMPT':'1',
        **{key:'1' for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')}}
    def git(root,*args):
        if args==('rev-parse','HEAD'): return b'a'*40+b'\n'
        if args[0]=='status': return b''
        if args[0]=='show': return snapshots[args[1].removeprefix('HEAD:')]
        pytest.fail('Unexpected Git operation')
    monkeypatch.setattr(inspect,'git',git)
    monkeypatch.setattr(inspect.os,'sched_getaffinity',lambda _:{3},raising=False)
    monkeypatch.setattr(inspect.platform,'python_version',lambda:'3.14.8')
    monkeypatch.setattr(inspect.importlib.metadata,'version',lambda name:{'pytest':'8.4.2','PyYAML':'6.0.3'}[name])
    return tmp_path,env,request,phase,preflight,commit


def test_complete_fictional_gate_has_no_source_or_output_io(gate):
    root,env,request,_,_,_=gate
    assert inspect.verify_gate(root,env)[0]==request
    assert not (root/'.pytest_cache').exists()


@pytest.mark.parametrize('key,value',[('GITHUB_ACTIONS','false'),('RUNNER_OS','Windows'),
    ('GITHUB_REF','refs/heads/main'),('GITHUB_RUN_ATTEMPT','0'),('OPENBLAS_NUM_THREADS','2')])
def test_local_wrong_branch_or_worker_refused(gate,key,value):
    root,env,*_=gate
    with pytest.raises(ValueError): inspect.verify_gate(root,{**env,key:value})


@pytest.mark.parametrize('which,key,value',[('request','execution_permitted',False),
    ('request','metadata_projection_only',False),('request','max_cloud_jobs',2),
    ('phase','heavy_work_permitted',True),('phase','max_heavy_local_jobs',1),
    ('preflight','numeric_producer_execution_permitted',True),('preflight','measurement_admission_permitted',True)])
def test_projection_scope_and_serialization_cannot_be_relaxed(gate,which,key,value):
    root,env,request,phase,preflight,commit=gate
    {'request':request,'phase':phase,'preflight':preflight}[which][key]=value;commit()
    with pytest.raises(ValueError): inspect.verify_gate(root,env)


def test_actual_multi_cpu_refused(gate,monkeypatch):
    root,env,*_=gate
    monkeypatch.setattr(inspect.os,'sched_getaffinity',lambda _:{1,2},raising=False)
    with pytest.raises(ValueError,match='One CPU'): inspect.verify_gate(root,env)


def test_changed_projection_input_refused(gate):
    root,env,*_=gate
    (root/inspect.WORKFLOW).write_bytes(b'changed')
    with pytest.raises(ValueError,match='projection input'): inspect.verify_gate(root,env)


@pytest.mark.parametrize('field,value',[('id',8),('digest','wrong'),('expired',True),('conclusion','failure'),('run_attempt',1)])
def test_mixed_expired_or_non_successful_source_is_refused(tmp_path,field,value):
    review={'artifact':{'id':7,'name':'source','size_in_bytes':99,'digest':'sha256:abc'},
            'run_id':123,'run_attempt':2,'source_commit':'a'*40}
    metadata={'id':7,'name':'source','size_in_bytes':99,'digest':'sha256:abc','expired':False,
              'workflow_run':{'id':123,'head_sha':'a'*40}}
    run={'id':123,'run_attempt':2,'head_sha':'a'*40,'status':'completed','conclusion':'success'}
    (run if field in ('conclusion','run_attempt') else metadata)[field]=value
    (tmp_path/'.pytest_cache').mkdir()
    (tmp_path/inspect.ARTIFACT_METADATA).write_bytes(inspect.encoded(metadata))
    (tmp_path/inspect.RUN_METADATA).write_bytes(inspect.encoded(run))
    with pytest.raises(ValueError,match='artifact or nonterminal'): inspect.verify_source_identity(tmp_path,review)


def test_incomplete_dependency_freeze_refused(gate):
    root,env,_,_,preflight,commit=gate
    preflight['input_sha256'].pop(inspect.REQUIREMENTS);commit()
    with pytest.raises(ValueError,match='dependency set'): inspect.verify_gate(root,env)


def test_full_projection_ignores_raw_fields_and_preserves_basis(diagnostic,tmp_path,monkeypatch):
    basis=tmp_path/'basis';basis.mkdir()
    review={'run_id':123,'run_attempt':2,'source_commit':'b'*40,'artifact':{'id':789},
            'cloud_output_fingerprints':{}}
    result={'run_id':123,'run_attempt':2,'source_commit':'b'*40,'diagnostic_sha256':inspect.digest(inspect.encoded(diagnostic)),
            'total_requests':82,'cases':72,'new_current_widths_admitted':0}
    files={'diagnostic.json':inspect.encoded(diagnostic),'result.json':inspect.encoded(result),
           'environment.json':b'{}','preflight.json':b'{}','resume-preflight.json':b'{}'}
    for name,raw in files.items(): (basis/name).write_bytes(raw)
    (basis/'monthly-fields.json').write_bytes(b'not JSON; must never load source fields')
    preflight={'basis_member_sha256':{name:inspect.digest(raw) for name,raw in files.items()},'max_output_bytes':524288}
    review['cloud_output_fingerprints']['diagnostic_sha256']=preflight['basis_member_sha256']['diagnostic.json']
    monkeypatch.setattr(inspect,'verify_gate',lambda *_:({},preflight,review))
    monkeypatch.setattr(inspect,'verify_source_identity',lambda *_:None)
    out=inspect.run_project(tmp_path,{'GITHUB_SHA':'a'*40,'GITHUB_RUN_ID':'456','GITHUB_RUN_ATTEMPT':'1'},basis)
    saved=json.loads((out/'support.json').read_bytes())
    assert len(saved['cases'])==72 and all((basis/name).read_bytes()==raw for name,raw in files.items())
    (basis/'diagnostic.json').write_bytes(files['diagnostic.json']+b' ')
    with pytest.raises(ValueError,match='fingerprint'): inspect.run_project(tmp_path,{},basis)


def test_real_workflow_restore_script_and_serial_order_on_tiny_git_fixture(tmp_path):
    root=Path(__file__).resolve().parents[1]
    workflow=yaml.safe_load((root/inspect.WORKFLOW).read_bytes())
    assert workflow['concurrency']=={'group':'osw-current-gap-delivery','cancel-in-progress':False}
    steps=workflow['jobs']['inspect-saved-diagnostic']['steps']
    before=next(i for i,step in enumerate(steps) if '--verify-source-identity' in step.get('run',''))
    download=next(i for i,step in enumerate(steps) if step.get('uses')=='actions/download-artifact@v4')
    assert before<download
    scripts=[]
    for step in steps:
        script=step.get('run','')
        if "python - <<'PY'\n" in script:
            body=script.split("python - <<'PY'\n",1)[1].split('\nPY',1)[0]
            compile(body,'<workflow>','exec');scripts.append(body)
    body=next(body for body in scripts if 'pins = ' in body)
    def git(*args):
        return subprocess.run(['git','-c','core.fsmonitor=false','-c','maintenance.auto=0','-c','gc.auto=0',*args],
            cwd=tmp_path,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    git('init','-q')
    for key,value in (('core.autocrlf','false'),('core.fsmonitor','false'),('gc.auto','0'),('maintenance.auto','0')):
        git('config',key,value)
    (tmp_path/'research').mkdir();(tmp_path/'inputs').mkdir();(tmp_path/'unrelated').mkdir()
    pins={}
    for i in range(11):
        name=f'inputs/{i}.json';(tmp_path/name).write_bytes(b'{}\n');pins[name]=inspect.digest(b'{}\n')
    raw=inspect.encoded({'input_sha256':pins});(tmp_path/inspect.PREFLIGHT).write_bytes(raw)
    request={'execution_permitted':True,'metadata_projection_only':True,'preflight':inspect.PREFLIGHT,'preflight_sha256':inspect.digest(raw)}
    phase={'phase':'source-review-only-v1','heavy_work_permitted':False,'max_heavy_local_jobs':0,'max_heavy_cloud_jobs':1}
    (tmp_path/inspect.REQUEST).write_bytes(inspect.encoded(request));(tmp_path/inspect.PHASE).write_bytes(inspect.encoded(phase))
    (tmp_path/'unrelated/large-not-real.bin').write_bytes(b'tiny fixture only')
    git('add','.');git('-c','user.name=OSW fixture','-c','user.email=fixture@example.invalid','commit','-qm','fixture')
    git('sparse-checkout','set','--no-cone',inspect.REQUEST,inspect.PHASE)
    assert not (tmp_path/'inputs').exists()
    result=subprocess.run([sys.executable,'-c',body],cwd=tmp_path,env={**os.environ,'GITHUB_REF':inspect.REF},
        stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    assert result.returncode==0,result.stderr.decode(errors='replace')
    assert all(inspect.digest((tmp_path/name).read_bytes())==sha for name,sha in pins.items())
    assert (tmp_path/inspect.REQUEST).is_file() and (tmp_path/inspect.PHASE).is_file()
    assert not (tmp_path/'unrelated/large-not-real.bin').exists()
