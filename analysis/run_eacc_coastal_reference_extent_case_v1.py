"""Gated one-CPU derived-profile review on the completed saved EACC case."""
import argparse
import ast
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re

from eacc_diagnostic_support_inspection_v1 import (
    encoded,digest,read,git,verify_source_identity,ARTIFACT_METADATA,RUN_METADATA,
)

REQUEST='research/eacc-coastal-reference-extent-request-v1.json'
PREFLIGHT='research/eacc-coastal-reference-extent-preflight-v1.json'
PHASE='research/current-gap-delivery-phase.json'
WORKFLOW='.github/workflows/eacc-coastal-reference-extent-case-v1.yml'
REQUIREMENTS='requirements-eacc-core-v2-execution-v2.txt'
CONTINUATION='research/eacc-hycom-source-resume-preflight-v2.json'
SUPPORT='research/eacc-diagnostic-support-preflight-v1.json'
PROTOTYPE='research/coastal-reference-extent-preparation-review-v1.json'
REVIEW='research/eacc-hycom-source-resume-execution-review-v1.json'
MAP_MANIFEST='research/eacc-hycom-2013-model-core-figures-manifest-v1.json'
PROTOCOL='plans/eacc-coastal-reference-extent-execution-v1.md'
ROLES='signals/roles/check/eacc-coastal-reference-extent-case-v1-roles-check-2026-10-24.md'
SOURCE_RUN=40117999392
SOURCE_COMMIT='69cddec0412ca5b1a57c8416067a3e2fd10720af'
DIAGNOSTIC_SHA='acc14e75d4cbfb6287d2db99e3eb71b01736e7d2693ad45c7a5a91d609e3d9e7'
FIELDS_SHA='a786835a4b11e8f6b3dce924227b70afbcf665fab3a3a2b94b374a9e19e7e7c2'
BASIS_MEMBERS={
    'diagnostic.json':DIAGNOSTIC_SHA,
    'monthly-fields.json':FIELDS_SHA,
    'result.json':'0bd2123f90425ad48e0d2e84fd93dad69219fa87604154254a274d64ca4d99c7',
    'environment.json':'a8cf0ad83c2a72a101a8032266b46ef2b56b000648eb28ba0d68ff06ec0cfa63',
    'preflight.json':'c596a4da53ac2082339a5ca8f415816ea24e0be49948d618056a2205d3695409',
    'resume-preflight.json':'fab1c625a2a5b40b26e64ec15c105248d28d77f6002e645356225a5428667460',
    'source-lineage.json':'8140c26c3c00d693c9d75bf319ba06907abbcdfbcb14cf3e6b2d8e3617acbbf5',
    'figures/manifest.json':'9b78c72cb715984ce088335864aacc3bbd00430c44b22bbbb67551dd9fcd0a75',
}
EXTRA_INPUTS={
    'analysis/eacc_coastal_reference_extent_adapter_v1.py',
    'analysis/test_eacc_coastal_reference_extent_adapter_v1.py',
    'analysis/eacc_coastal_reference_extent_evidence_v1.py',
    'analysis/test_eacc_coastal_reference_extent_evidence_v1.py',
    'analysis/run_eacc_coastal_reference_extent_case_v1.py',
    'analysis/test_run_eacc_coastal_reference_extent_case_v1.py',
    WORKFLOW,PROTOCOL,ROLES,PROTOTYPE,CONTINUATION,SUPPORT,
    'plans/coastal-current-extent-measurement-design-v1.md',
    'research/eacc-diagnostic-support-inspection-result-v1.json',
    'research/eacc-diagnostic-support-inspection-review-v1.json'}


def required_paths(root):
    old=json.loads(read(root,CONTINUATION))['input_sha256']
    support=json.loads(read(root,SUPPORT))['input_sha256']
    prototype=json.loads(read(root,PROTOTYPE))['source_sha256']
    paths=set(old)|set(support)|set(prototype)|EXTRA_INPUTS
    for name in paths:
        if not name.endswith('.py'):continue
        for node in ast.walk(ast.parse(read(root,name).decode())):
            modules=[a.name for a in node.names] if isinstance(node,ast.Import) else [node.module] if isinstance(node,ast.ImportFrom) and node.module else []
            for module in modules:
                candidate='analysis/'+module.split('.')[0]+'.py'
                if (root/candidate).is_file() and candidate not in paths:
                    raise ValueError('Unfrozen source dependency: '+candidate)
    return paths


def verify_gate(root,env):
    root=Path(root).resolve()
    if (env.get('GITHUB_ACTIONS')!='true' or env.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
            or env.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps' or env.get('RUNNER_OS')!='Linux'
            or Path(env.get('GITHUB_WORKSPACE','')).resolve()!=root):
        raise ValueError('Derived extent review requires declared cloud working branch')
    affinity=getattr(os,'sched_getaffinity',None)
    if affinity is None or len(affinity(0))!=1 or any(env.get(key)!='1' for key in
            ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')):
        raise ValueError('One actual CPU and one numerical worker required')
    if any(not re.fullmatch('[1-9][0-9]*',env.get(key,'')) for key in ('GITHUB_RUN_ID','GITHUB_RUN_ATTEMPT')):
        raise ValueError('Current run identity required')
    if (not re.fullmatch('[0-9a-f]{40}',env.get('GITHUB_SHA',''))
            or git(root,'rev-parse','HEAD').decode().strip()!=env['GITHUB_SHA']
            or git(root,'status','--porcelain','--untracked-files=no').strip()):
        raise ValueError('Exact clean committed source required')
    raw=read(root,REQUEST,16384);request=json.loads(raw)
    phase_raw=read(root,PHASE,16384);phase=json.loads(phase_raw)
    if (raw!=git(root,'show','HEAD:'+REQUEST) or phase_raw!=git(root,'show','HEAD:'+PHASE)
            or request.get('schema')!='osw.eacc-coastal-reference-extent-request.v1'
            or request.get('execution_permitted') is not True
            or request.get('saved_derived_profile_review_only') is not True
            or request.get('metadata_projection_only') is not False
            or request.get('provider_requests_permitted') is not False
            or request.get('original_producer_rerun_permitted') is not False
            or request.get('measurement_admission_permitted') is not False
            or request.get('max_heavy_local_jobs')!=0 or request.get('max_cloud_jobs')!=1
            or request.get('workflow')!=WORKFLOW or request.get('preflight')!=PREFLIGHT
            or phase.get('phase')!='source-review-only-v1' or phase.get('heavy_work_permitted') is not False
            or phase.get('max_heavy_local_jobs')!=0 or phase.get('max_heavy_cloud_jobs')!=1):
        raise ValueError('Held acquisition phase and explicit saved-profile numerical review request required')
    preflight_raw=read(root,PREFLIGHT);pref=json.loads(preflight_raw)
    if digest(preflight_raw)!=request.get('preflight_sha256') or preflight_raw!=git(root,'show','HEAD:'+PREFLIGHT):
        raise ValueError('Changed original-case preflight')
    if (pref.get('schema')!='osw.eacc-coastal-reference-extent-preflight.v1' or pref.get('workflow')!=WORKFLOW
            or pref.get('python_exact')!='3.14.8' or pref.get('python_exact')!=platform.python_version()
            or pref.get('saved_profile_extent_execution_permitted') is not True
            or pref.get('provider_requests_permitted') is not False or pref.get('original_producer_rerun_permitted') is not False
            or pref.get('measurement_admission_permitted') is not False or pref.get('max_report_bytes')!=2097152
            or pref.get('max_summary_bytes')!=524288 or pref.get('basis_member_sha256')!=BASIS_MEMBERS
            or set(pref.get('input_sha256',{}))!=required_paths(root)):
        raise ValueError('Changed derived-case scope, dependency set or environment')
    for name,expected in pref['input_sha256'].items():
        item=read(root,name,4194304)
        if digest(item)!=expected or item!=git(root,'show','HEAD:'+name):
            raise ValueError('Changed/uncommitted original-case input: '+name)
    old=json.loads(read(root,CONTINUATION))['input_sha256'];support=json.loads(read(root,SUPPORT))['input_sha256']
    if len(old)!=52 or len(old|support)!=62 or any(pref['input_sha256'].get(name)!=sha for name,sha in (old|support).items()):
        raise ValueError('All62 executed source/support inputs must remain unchanged')
    prototype=json.loads(read(root,PROTOTYPE))['source_sha256']
    if any(pref['input_sha256'].get(name)!=sha for name,sha in prototype.items()):
        raise ValueError('Synthetic-reviewed operator/protocol changed before original case')
    review=json.loads(read(root,REVIEW))
    if (review['run_id']!=SOURCE_RUN or review['run_attempt']!=2 or review['source_commit']!=SOURCE_COMMIT
            or review['run_conclusion']!='success' or review['cloud_output_fingerprints']['diagnostic_sha256']!=DIAGNOSTIC_SHA
            or review['cloud_output_fingerprints']['monthly_fields_sha256']!=FIELDS_SHA):
        raise ValueError('Wrong completed scientific basis')
    for line in read(root,REQUIREMENTS,8192).decode().splitlines():
        if line.strip() and not line.startswith('#'):
            package,version=line.split('==')
            if importlib.metadata.version(package)!=version:raise ValueError('Changed scientific dependency: '+package)
    return request,pref,review


def load_saved_basis(root,basis,members):
    """Check all retained bytes before parsing profiles or importing new maths."""
    root=Path(root).resolve();basis=Path(basis).resolve()
    if not basis.is_relative_to(root):raise ValueError('Saved basis must remain in cloud workspace')
    if members!=BASIS_MEMBERS:raise ValueError('Incomplete or wrong source custody')
    raw={name:read(basis,name,4194304) for name in members}
    if any(digest(raw[name])!=value for name,value in members.items()):
        raise ValueError('Saved original input changed')
    result=json.loads(raw['result.json']);environment=json.loads(raw['environment.json'])
    if any(doc['source_commit']!=SOURCE_COMMIT or doc['run_id']!=SOURCE_RUN or doc['run_attempt']!=2
            for doc in (result,environment)):
        raise ValueError('Saved source run identity changed')
    if raw['figures/manifest.json']!=read(root,MAP_MANIFEST):
        raise ValueError('Unreviewed source map manifest')
    return (json.loads(raw['diagnostic.json']),json.loads(raw['monthly-fields.json']),
            json.loads(raw['figures/manifest.json']))


def compact_report(report):
    keys=('quantity','status','extent_bracket_km','maximum_native_cell_scale_km',
        'minimum_span_in_native_cell_scales','source_scale_gate_passed','resolution_status',
        'conditional_on_inshore_flow_assumption','whole_current_width_km','width_rank_eligible',
        'physical_state_join_eligible','physical_uncertainty_km')
    cases=[]
    for case in report['cases']:
        cases.append({'case_id':case['case_id'],'source_status':case['source_status'],
            'legacy_regional_gate':case['legacy_regional_gate'],'adapter_audit':case['adapter_audit'],
            'status':case['status'],'metrics':[{'fraction':v['fraction']}|{key:m[key] for key in keys}
                for v in case['variants'] for m in v['metrics']]})
    return {'schema':'osw.eacc-coastal-reference-extent.compact-review.v1','source':report['source'],
        'cases':cases,'case_count':72,'source_model_year':2013,'provider_standard_output_depth_m':15,
        'all_months_and_failures_retained':True,'current_association_verified':False,
        'new_current_measurements_admitted':0,'whole_current_width_km':None,'physical_annual_width_range_km':None,
        'physical_uncertainty_km':None,'interpretation':report['scope']}


def run_case(root,env,basis):
    root=Path(root).resolve();request,pref,review=verify_gate(root,env)
    verify_source_identity(root,review)
    basis=Path(basis).resolve()
    if not basis.is_relative_to(root):raise ValueError('Saved basis must remain in cloud workspace')
    out=root/'.pytest_cache/eacc-coastal-reference-extent-v1'/f"run-{env['GITHUB_RUN_ID']}-attempt-{env['GITHUB_RUN_ATTEMPT']}"
    out.mkdir(parents=True,exist_ok=False)
    def save(name,raw):
        with (out/name).open('xb') as stream:stream.write(raw)
    save('request.json',read(root,REQUEST));save('preflight.json',read(root,PREFLIGHT))
    save('environment.json',encoded({'source_commit':env['GITHUB_SHA'],'run_id':int(env['GITHUB_RUN_ID']),
        'run_attempt':int(env['GITHUB_RUN_ATTEMPT']),'python':platform.python_version(),
        'input_sha256':pref['input_sha256'],'logical_cpu_limit':1,'worker_limit':1,
        'numeric_scope':'New local extent operator plus readonly original frame/support verification; no completed producer rerun.'}))
    try:
        diagnostic,fields,manifest=load_saved_basis(root,basis,pref['basis_member_sha256'])
        from eacc_coastal_reference_extent_adapter_v1 import adapt_cases
        from coastal_reference_extent_v1 import analyse_cases
        from eacc_coastal_reference_extent_evidence_v1 import render_evidence
        source={'basis_run_id':SOURCE_RUN,'basis_run_attempt':2,'basis_source_commit':SOURCE_COMMIT,
            'basis_artifact_id':review['artifact']['id'],'diagnostic_sha256':DIAGNOSTIC_SHA,'monthly_fields_sha256':FIELDS_SHA,
            'case_run_id':int(env['GITHUB_RUN_ID']),'case_run_attempt':int(env['GITHUB_RUN_ATTEMPT']),
            'case_source_commit':env['GITHUB_SHA'],'preflight_sha256':digest(read(root,PREFLIGHT))}
        adapted=adapt_cases(diagnostic,fields,source)
        report=analyse_cases(adapted)
        audits={case['id']:case['adapter_audit'] for case in adapted}
        for case in report['cases']:case['adapter_audit']=audits[case['case_id']]
        report['source']=source;report['scope']='Method development on retained2013 daily00Z monthly means at15m; no current association, whole-current width or physical annual range admitted.'
        report['old_producer_rerun']=False;report['new_provider_requests']=0
        summary=compact_report(report)
        report_raw=encoded(report);summary_raw=encoded(summary)
        if len(report_raw)>pref['max_report_bytes'] or len(summary_raw)>pref['max_summary_bytes']:
            raise ValueError('Derived report exceeded bounded review cap')
        save('extents.json',report_raw);save('review-summary.json',summary_raw)
        base_maps={m:read(basis,f'figures/m{m:02d}-map.svg',2097152) for m in range(1,13)}
        figure_manifest=render_evidence(adapted,report,base_maps,manifest,out/'figures',rasterize=True)
        result={'schema':'osw.eacc-coastal-reference-extent-result.v1','source':source,'cases':72,
            'status':'method_development_completed_not_measurement_admission','extents_sha256':digest(report_raw),
            'extents_bytes':len(report_raw),'review_summary_sha256':digest(summary_raw),'review_summary_bytes':len(summary_raw),
            'figures_manifest_sha256':digest((out/'figures/manifest.json').read_bytes()),'figure_months':figure_manifest['months'],
            'new_provider_requests':0,'completed_old_producer_rerun':False,'new_current_measurements_admitted':0,
            'physical_annual_width_range_admitted':False,'main_merged':False}
        save('result.json',encoded(result));print(json.dumps(result,indent=2),flush=True)
    except Exception as error:
        save('case-failure.json',encoded({'status':'derived_case_failed_preserved_no_retry','source_commit':env['GITHUB_SHA'],
            'run_id':int(env['GITHUB_RUN_ID']),'run_attempt':int(env['GITHUB_RUN_ATTEMPT']),
            'error_type':type(error).__name__,'error':str(error)[:2048],'new_current_measurements_admitted':0}))
        raise
    return out


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);actions=parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('--verify-cloud-gate',action='store_true');actions.add_argument('--verify-source-identity',action='store_true')
    actions.add_argument('--cloud-derived-case',action='store_true');parser.add_argument('--basis',type=Path)
    args=parser.parse_args();root=Path(__file__).resolve().parents[1]
    if args.cloud_derived_case:
        if args.basis is None:parser.error('--basis is required')
        run_case(root,dict(os.environ),args.basis)
    else:
        _,_,review=verify_gate(root,dict(os.environ))
        if args.verify_source_identity:verify_source_identity(root,review)
        print('Saved-derived-profile review gate verified; provider and original producers not accessed')
