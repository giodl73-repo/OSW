"""Copy retained EACC support evidence in cloud; no numerical producers or source requests."""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import subprocess

REQUEST = 'research/eacc-diagnostic-support-request-v1.json'
PREFLIGHT = 'research/eacc-diagnostic-support-preflight-v1.json'
PHASE = 'research/current-gap-delivery-phase.json'
WORKFLOW = '.github/workflows/eacc-diagnostic-support-inspection-v1.yml'
REVIEW = 'research/eacc-hycom-source-resume-execution-review-v1.json'
CORE = 'research/eacc-regional-model-core-preflight-v2-execution-v2.json'
CONTINUATION = 'research/eacc-hycom-source-resume-preflight-v2.json'
REQUIREMENTS = 'requirements-eacc-support-v1.txt'
SOURCE_RUN = 40117999392
SOURCE_COMMIT = '69cddec0412ca5b1a57c8416067a3e2fd10720af'
DIAGNOSTIC_SHA = 'acc14e75d4cbfb6287d2db99e3eb71b01736e7d2693ad45c7a5a91d609e3d9e7'
INPUTS = {'analysis/eacc_diagnostic_support_inspection_v1.py',
    'analysis/test_eacc_diagnostic_support_inspection_v1.py', WORKFLOW, REVIEW, CORE, CONTINUATION, REQUIREMENTS,
    'research/eacc-hycom-2013-model-core-result-v1.json',
    'research/eacc-hycom-2013-model-core-figures-manifest-v1.json',
    'plans/eacc-completed-diagnostic-support-inspection-v1.md',
    'signals/roles/check/eacc-diagnostic-support-inspection-v1-roles-check-2026-10-24.md'}
REPOSITORY = 'giodl73-repo/OSW'
REF = 'refs/heads/codex/current-measurement-gaps'
ARTIFACT_METADATA = '.pytest_cache/eacc-diagnostic-support-artifact.json'
RUN_METADATA = '.pytest_cache/eacc-diagnostic-support-source-run.json'
THRESHOLD_KEYS = ('fraction','status','diagnostic_span_km','resolved_span_km',
    'native_cell_scale_km','native_cell_count','span_in_native_cell_scales','effective_resolution_verified')


def encoded(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read(root,name,cap=524288):
    root=Path(root).resolve(); path=(root/name).resolve()
    if not path.is_relative_to(root) or path.stat().st_size>cap:
        raise ValueError('Unsupported input path or byte cap: '+name)
    return path.read_bytes()


def git(root,*args):
    return subprocess.check_output(['git','-c','core.fsmonitor=false','-c','maintenance.auto=0',
        '-c','gc.auto=0','-C',str(root),*args])


def project(diagnostic,source):
    """Select exact stored rows/scalars. No interpolation, resampling or revised gates."""
    if (diagnostic.get('schema')!='osw.eacc-regional-model-core.numerical-diagnostic.v2'
            or diagnostic.get('current_association_verified') is not False):
        raise ValueError('Unexpected original diagnostic identity/admission')
    cases=diagnostic['cases']
    if len(cases)!=72 or len({c['id'] for c in cases})!=72:
        raise ValueError('All72 original case identities are required')
    expected={(m,o,s) for m in range(1,13) for o in (-1,0,1) for s in (5,10)}
    if {(c['month'],c['native_latitude_offset'],c['normal_sample_step_km']) for c in cases}!=expected:
        raise ValueError('Missing or duplicate month/offset/step case')
    rows=[]
    for case in cases:
        if case['id']!=f"m{case['month']:02d}:offset{case['native_latitude_offset']}:step{case['normal_sample_step_km']}":
            raise ValueError('Original case id disagrees with its fields')
        initial=case.get('initial_refinement')
        samples=[] if initial is None else initial['samples']
        if (any(len(row)!=9 or type(row[0]) not in (int,float) for row in samples)
                or len({row[0] for row in samples})!=len(samples)
                or any(a[0]>=b[0] for a,b in zip(samples,samples[1:]))):
            raise ValueError('Malformed retained profile rows')
        first={}
        for side,sign in (('negative',-1),('positive',1)):
            unsupported=[row for row in samples if sign*row[0]>0 and row[-1]!='ok']
            first[side]=min(unsupported,key=lambda row:abs(row[0])) if unsupported else None
        selected=[row for row in samples if abs(row[0])<=40 or any(row is value for value in first.values())]
        endpoints={}
        for side,offset in (('negative',-40),('positive',40)):
            row=next((row for row in samples if row[0]==offset),None)
            endpoints[side]={'normal_offset_km':offset,'present_in_original':row is not None,
                'original_support_status':None if row is None else row[-1],
                'supported_in_original':row is not None and row[-1]=='ok' and row[5] is not None,
                'sample':row}
        stations=[]
        for station in case['stations']:
            stations.append({key:station[key] for key in ('station_arc_parameter_km','origin_lon_lat',
                'bearing_degrees_true','peak','local_candidate_axis_check','failed_axis_checks')} |
                {'threshold_cases':[{key:t[key] for key in THRESHOLD_KEYS} for t in station['threshold_cases']]})
        rows.append({key:case[key] for key in ('id','month','native_latitude_offset','normal_sample_step_km',
            'status','anchor','seed','refined_seed_lon_lat','all_five_local_axis_checks_pass',
            'all_five_half_peak_spans_resolved')} | {
            'refined_vector_support':case.get('refined_vector_support'),
            'initial_refinement_peak':None if initial is None else initial['peak'],
            'initial_window_and_first_unsupported_samples':selected,'search_endpoints':endpoints,
            'first_unsupported_samples':first,'stations':stations,'source':source})
    output={'schema':'osw.eacc-diagnostic-support.v1','source':source,
        'projection_only':True,'initial_search_window_km':[-40,40],
        'sample_columns':['normal_offset_km','longitude_degrees_east','latitude_degrees_north',
            'eastward_m_s','northward_m_s','projected_tangent_m_s','ascending_latitude_cell_index',
            'longitude_cell_index','status'],
        'cases':rows,'case_status_counts':dict(Counter(c['status'] for c in cases)),
        'current_association_verified':False,'new_current_widths_admitted':0,
        'new_velocity_requests':0,'numeric_producer_rerun':False,
        'interpretation':'Copied diagnostic support and method failures; not new measurements, zero flow, current absence or uncertainty.'}
    return deepcopy(output)


def verify_gate(root,env):
    root=Path(root).resolve()
    if (env.get('GITHUB_ACTIONS')!='true' or env.get('GITHUB_REPOSITORY')!=REPOSITORY
            or env.get('GITHUB_REF')!=REF or env.get('RUNNER_OS')!='Linux'
            or Path(env.get('GITHUB_WORKSPACE','')).resolve()!=root):
        raise ValueError('Projection requires declared cloud working-branch context')
    affinity=getattr(os,'sched_getaffinity',None)
    if affinity is None or len(affinity(0))!=1 or any(env.get(key)!='1' for key in
            ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')):
        raise ValueError('One CPU and one worker required')
    if any(not re.fullmatch('[1-9][0-9]*',env.get(key,'')) for key in ('GITHUB_RUN_ID','GITHUB_RUN_ATTEMPT')):
        raise ValueError('Missing current run identity')
    if (not re.fullmatch('[0-9a-f]{40}',env.get('GITHUB_SHA',''))
            or git(root,'rev-parse','HEAD').decode().strip()!=env['GITHUB_SHA']
            or git(root,'status','--porcelain','--untracked-files=no').strip()):
        raise ValueError('Projection requires exact clean checkout')
    request_raw=read(root,REQUEST,16384); request=json.loads(request_raw)
    phase_raw=read(root,PHASE,16384); phase=json.loads(phase_raw)
    if (request_raw!=git(root,'show','HEAD:'+REQUEST) or phase_raw!=git(root,'show','HEAD:'+PHASE)
            or request.get('schema')!='osw.eacc-diagnostic-support-request.v1'
            or request.get('execution_permitted') is not True or request.get('metadata_projection_only') is not True
            or request.get('max_heavy_local_jobs')!=0 or request.get('max_cloud_jobs')!=1
            or request.get('workflow')!=WORKFLOW or request.get('preflight')!=PREFLIGHT
            or phase.get('phase')!='source-review-only-v1' or phase.get('heavy_work_permitted') is not False
            or phase.get('max_heavy_local_jobs')!=0 or phase.get('max_heavy_cloud_jobs')!=1):
        raise ValueError('Committed held phase and explicit metadata-only request required')
    raw=read(root,PREFLIGHT); preflight=json.loads(raw)
    if digest(raw)!=request.get('preflight_sha256') or raw!=git(root,'show','HEAD:'+PREFLIGHT):
        raise ValueError('Changed projection preflight')
    if (preflight.get('schema')!='osw.eacc-diagnostic-support-preflight.v1'
            or preflight.get('workflow')!=WORKFLOW or preflight.get('numeric_producer_execution_permitted') is not False
            or preflight.get('measurement_admission_permitted') is not False
            or preflight.get('max_output_bytes')!=524288 or set(preflight.get('input_sha256',{}))!=INPUTS
            or preflight.get('python_exact')!=platform.python_version()):
        raise ValueError('Changed projection scope, dependency set or environment')
    for name,expected in preflight['input_sha256'].items():
        item=read(root,name)
        if digest(item)!=expected or item!=git(root,'show','HEAD:'+name):
            raise ValueError('Changed/uncommitted projection input: '+name)
    review=json.loads(read(root,REVIEW)); continuation=json.loads(read(root,CONTINUATION))
    core=json.loads(read(root,CORE))
    if (review['run_conclusion']!='success' or review['run_attempt']!=2 or review['run_id']!=SOURCE_RUN
            or review['source_commit']!=SOURCE_COMMIT
            or review['cloud_output_fingerprints']['diagnostic_sha256']!=DIAGNOSTIC_SHA
            or digest(read(root,CORE))!=review['original_preflight_sha256']
            or digest(read(root,CONTINUATION))!=review['continuation_preflight_sha256']
            or len(continuation['input_sha256'])!=52 or len(core['input_sha256'])!=40
            or any(continuation['input_sha256'].get(name)!=sha for name,sha in core['input_sha256'].items())):
        raise ValueError('Wrong completed source/method basis')
    for line in read(root,REQUIREMENTS,8192).decode().splitlines():
        if line.strip() and not line.startswith('#'):
            package,version=line.split('==')
            if importlib.metadata.version(package)!=version:
                raise ValueError('Changed projection test/parser dependency')
    return request,preflight,review


def verify_source_identity(root,review):
    metadata=json.loads(read(root,ARTIFACT_METADATA)); run=json.loads(read(root,RUN_METADATA))
    expected=review['artifact']
    if (metadata.get('id')!=expected['id'] or metadata.get('name')!=expected['name']
            or metadata.get('size_in_bytes')!=expected['size_in_bytes'] or metadata.get('digest')!=expected['digest']
            or metadata.get('expired') is not False or metadata.get('workflow_run',{}).get('id')!=review['run_id']
            or metadata.get('workflow_run',{}).get('head_sha')!=review['source_commit']
            or run.get('id')!=review['run_id'] or run.get('run_attempt')!=review['run_attempt']
            or run.get('head_sha')!=review['source_commit'] or run.get('status')!='completed' or run.get('conclusion')!='success'):
        raise ValueError('Wrong/expired artifact or nonterminal/mixed source run')


def run_project(root,env,basis):
    root=Path(root).resolve()
    request,preflight,review=verify_gate(root,env)
    verify_source_identity(root,review)
    basis=Path(basis).resolve()
    if not basis.is_relative_to(root): raise ValueError('Restore saved diagnostic inside cloud workspace')
    members=preflight['basis_member_sha256']
    expected_members={'diagnostic.json','result.json','environment.json','preflight.json','resume-preflight.json'}
    if set(members)!=expected_members: raise ValueError('Incomplete saved diagnostic custody')
    raw_members={name:read(basis,name,2097152 if name=='diagnostic.json' else 262144) for name in members}
    if any(digest(raw_members[name])!=expected for name,expected in members.items()):
        raise ValueError('Saved diagnostic/method/result fingerprint changed')
    if members['diagnostic.json']!=review['cloud_output_fingerprints']['diagnostic_sha256']:
        raise ValueError('Unreviewed original diagnostic')
    result=json.loads(raw_members['result.json'])
    if (result['run_id']!=review['run_id'] or result['run_attempt']!=review['run_attempt']
            or result['source_commit']!=review['source_commit'] or result['diagnostic_sha256']!=members['diagnostic.json']
            or result['total_requests']!=82 or result['cases']!=72 or result['new_current_widths_admitted']!=0):
        raise ValueError('Original result identity/scope mismatch')
    source={'run_id':review['run_id'],'run_attempt':review['run_attempt'],'source_commit':review['source_commit'],
        'artifact_id':review['artifact']['id'],'diagnostic_sha256':members['diagnostic.json'],
        'projection_commit':env['GITHUB_SHA'],'projection_run_id':int(env['GITHUB_RUN_ID']),
        'projection_run_attempt':int(env['GITHUB_RUN_ATTEMPT'])}
    projection=project(json.loads(raw_members['diagnostic.json']),source)
    raw=encoded(projection)
    if len(raw)>preflight['max_output_bytes']: raise ValueError('Projection output exceeds bounded readback cap')
    out=root/'.pytest_cache/eacc-diagnostic-support-v1'/f"run-{env['GITHUB_RUN_ID']}-attempt-{env['GITHUB_RUN_ATTEMPT']}"
    out.mkdir(parents=True,exist_ok=False)
    for name,content in (('support.json',raw),('request.json',encoded(request)),('preflight.json',encoded(preflight))):
        with (out/name).open('xb') as stream: stream.write(content)
    receipt={'schema':'osw.eacc-diagnostic-support-result.v1','source':source,'support_sha256':digest(raw),
        'support_bytes':len(raw),'cases':72,'numeric_producer_rerun':False,'new_velocity_requests':0,
        'new_current_widths_admitted':0,'case_status_counts':projection['case_status_counts']}
    with (out/'result.json').open('xb') as stream: stream.write(encoded(receipt))
    print(json.dumps(receipt,indent=2),flush=True)
    return out


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    actions=parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('--verify-cloud-gate',action='store_true')
    actions.add_argument('--verify-source-identity',action='store_true')
    actions.add_argument('--cloud-project',action='store_true')
    parser.add_argument('--basis',type=Path)
    args=parser.parse_args(); root=Path(__file__).resolve().parents[1]
    if args.cloud_project:
        if args.basis is None: parser.error('--basis is required')
        run_project(root,dict(os.environ),args.basis)
    else:
        _,_,review=verify_gate(root,dict(os.environ))
        if args.verify_source_identity: verify_source_identity(root,review)
        print('Metadata projection gate verified; no provider or numerical producer accessed')
