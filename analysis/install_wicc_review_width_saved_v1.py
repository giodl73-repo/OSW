"""Install the exact reviewed WICC width artifact in cloud without rebuilding."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import install_published_current_speed_saved_v1 as saved
import wicc_review_width_delivery_v1 as delivery
import verified_artifact_git_transport_v1 as transport

ROOT=Path(__file__).resolve().parents[1]
REPO=saved.REPO;BRANCH=saved.BRANCH
REQUEST='research/wicc-review-width-installation-request-v1.json'
PREFLIGHT='research/wicc-review-width-installation-preflight-v1.json'
WORKFLOW='.github/workflows/install-wicc-review-width-saved-v1.yml'
PROOF='research/wicc-review-width-installed-v1.json'
SAVED='research/wicc-review-width-installation-saved-engine-manifest-v1.json'
EVIDENCE='research/wicc-review-width-engine-run-v1/'
REVIEW='research/wicc-review-width-visual-review-v1.json'
EXECUTION='research/wicc-review-width-delivery-execution-review-v1.json'
OUT=ROOT/'.pytest_cache/wicc-review-width-installation-v1'
SOURCE='93ae2beb342200f39ef22ad9ec91e824ebc9e83c'
RUN=40647043885
BROWSER_RUN=40649784413
BROWSER_SOURCE='e5dea4a0705af1c8ed752c96d77d1a9c9da0184f'
BROWSER_ARTIFACT={'id':12799029548,'bytes':1130399,'sha256':'2d1901f9b822bac34392ef3a691a763919c77b6cf67499d2a3e7e93f696a2e3f'}
BROWSER_EVIDENCE='research/wicc-review-width-browser-run-v1/'
LOGICAL='360e775a1dbb49d5c7934cca1f288ab2f2f8cd71bfa8fd1368fb35b086f4e1e0'
LOGICAL_BYTES=190547331
BINARY='037b6cfcee4d21bff80443bc77e0ab12c797eccc419e4ff39665cb09441e0ee0'
FINAL_MANIFEST='b03b4c865bb14f8960122a5581ae292e5f8576454ff2f0de460c40813e4846d3'
ARTIFACT={'id':12798651340,'bytes':96271344,'sha256':'ade6f51185032f8907d034321f7b2bf8c08123b20cee8930e716a528bfaf4b3f'}
INDEX_LOGICAL='78aa24a81a72105eb7fb7cd69f0f1d2b5fb4dfdf10d127156848f13e8a38bb86'
PARITY_SOURCE='analysis/check_wicc_review_width_parity_v1.mjs'
PARITY_SOURCE_SHA='6ce0f72441e74b113d53860146bcf31550fa9355c3f9b99516fd8f0d8b34a88d'
sha,oid,encode,api,objects,file_sha=saved.sha,saved.oid,saved.encode,saved.api,saved.objects,saved.file_sha

def read(path):return json.loads((ROOT/path).read_bytes())

def verify_parity_receipt(name,parity):
    count={'main':61,'index':25,'snapshots':3}[name]
    assert parity['status']=='PASS' and len(parity['checks'])==count and parity['initialization_metadata_equal'] is True
    assert all(r['entire_response_equal'] is True for r in parity['checks']) and parity['wasm_sha256']==BINARY
    assert 0<parity['max_wasm_linear_memory_bytes']<=3221225472
    assert parity['payload_sha256']==(INDEX_LOGICAL if name=='index' else LOGICAL)
    assert parity['mode']==('candidate' if name=='snapshots' else name)
    if name=='snapshots':assert {r['view'] for r in parity['checks']}=={'atlas','seasons','dashboard'}

def verify_request(request):
    for key,value in {'schema':'osw.wicc-review-width-installation-request.v1','workflow':WORKFLOW,
            'execution_permitted':True,'working_branch_installation_permitted':True,
            'cloud_git_object_transport_permitted':True,'max_cloud_jobs':1,'max_heavy_local_jobs':0}.items():
        assert type(request.get(key)) is type(value) and request[key]==value,key
    for key in ['native_build_permitted','wasm_build_permitted','browser_automation_permitted',
            'scientific_source_processing_permitted','source_field_processing_permitted',
            'local_bulk_sync_permitted','main_merge_permitted']:assert request.get(key) is False,key

def verify_evidence(engine,result,execution,review,browser):
    assert engine['status']=='PASS' and engine['source_commit']==SOURCE
    assert engine['logical_sha256']==LOGICAL and engine['logical_bytes']==LOGICAL_BYTES and engine['wasm_sha256']==BINARY
    assert [engine[k] for k in ['rust_tests_passed','main_query_comparisons','source_query_comparisons','complete_api_comparisons']]==[230,61,25,3]
    assert engine['prior_speed_whole_responses_preserved']==2 and engine['new_width_records']==1
    assert engine['new_width_samples']==engine['new_length_records']==0 and engine['installed'] is False
    assert engine['source_index_audit']=={'original_sources_verified':630,'original_source_strings_preserved':630,
        'replaced_source_paths':[],'added_source_paths':[delivery.core.SOURCE],'scientific_source_documents_replaced':0}
    expected={**engine,'browser_verified':True,'browser_source_commit':BROWSER_SOURCE,
        'browser_run_id':str(BROWSER_RUN),'browser_run_attempt':'2','saved_artifact':ARTIFACT,
        'saved_engine_evidence_sha256':file_sha(ROOT/(EVIDENCE+'engine.json')),
        'browser_harness_sha256':file_sha(ROOT/'analysis/check_wicc_review_width_browser_v2.py'),
        'native_or_wasm_rebuild':False,'runtime_assets_changed':False,'visual_review_complete':False,'installed':False,'full_goal_complete':False}
    assert result==expected
    assert execution['status']=='PASS_ENGINE_SOURCE_INDEX_BROWSER_AND_INDIVIDUAL_VISUAL_REVIEW_INSTALLATION_PENDING'
    assert execution['candidate_artifact']=={**ARTIFACT,'downloaded_locally':False}
    assert execution['engine_source_commit']==review['engine_source_commit']==SOURCE
    assert execution['browser_source_commit']==review['browser_source_commit']==BROWSER_SOURCE
    assert execution['engine_run_id']==review['engine_run_id']==RUN and execution['engine_run_attempt']==review['engine_run_attempt']==2
    assert execution['browser_run_id']==review['browser_run_id']==BROWSER_RUN and execution['browser_run_attempt']==review['browser_run_attempt']==2
    assert execution['engine_manifest_sha256']==FINAL_MANIFEST and execution['intended_width_records_after_installation']==175
    assert execution['intended_width_owners_after_installation']==88 and execution['intended_indexed_documents_after_installation']==631 and execution['installed'] is False
    assert review['status']=='PASS_20_ACTUAL_SCREENSHOTS_INDIVIDUALLY_INSPECTED' and review['independent_visual_review_complete'] is True
    assert review['browser_artifact']==BROWSER_ARTIFACT
    assert browser['status']=='PASS' and not browser['page_errors'] and not browser['missing_assets'] and not browser['original_science_downloads']
    assert review['screenshots']==browser['screenshots'] and len(review['screenshots'])==20
    assert len({r['path'] for r in review['screenshots']})==20
    assert all(r['geometry']['clipped_axes']==[] and r['geometry']['width']>0 and r['geometry']['height']>0 for r in review['screenshots'])
    hashes=engine['generated_sha256'];assert len(hashes)==18 and hashes[delivery.WASM]==BINARY and hashes[delivery.MANIFEST]==FINAL_MANIFEST
    assert sum(p.startswith('almanac/query-parts/') for p in hashes)==12
    return dict(hashes)


def controls():
    assert os.environ.get('GITHUB_ACTIONS')=='true' and os.environ.get('RUNNER_OS')=='Linux'
    assert os.environ.get('OSW_WICC_REVIEW_WIDTH_INSTALL_V1')=='1' and os.environ.get('GITHUB_EVENT_NAME')=='push'
    assert os.environ.get('GITHUB_REPOSITORY')=='giodl73-repo/OSW' and os.environ.get('GITHUB_REF')=='refs/heads/'+BRANCH
    assert len(os.sched_getaffinity(0))==1 and os.getpriority(os.PRIO_PROCESS,0)>=15
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:assert os.environ.get(key)=='1'
    source=os.environ['GITHUB_SHA'];assert transport.git('rev-parse','HEAD')==saved.base.branch_head()==source
    assert not transport.git('status','--porcelain').strip()
    request=read(REQUEST);verify_request(request);assert file_sha(ROOT/PREFLIGHT)==request['preflight_sha256']
    pref=read(PREFLIGHT)
    for path,pin in pref['input_sha256'].items():assert file_sha(ROOT/path)==pin,path
    for path,row in pref['parent_files'].items():assert file_sha(ROOT/path)==row['sha256'] and (ROOT/path).stat().st_size==row['bytes'],path
    phase=read('research/current-gap-delivery-phase.json');assert phase['heavy_work_permitted'] is False and phase['max_heavy_local_jobs']==0 and phase['max_heavy_cloud_jobs']==1
    for path in pref['disabled_requests']:
        doc=read(path);assert doc.get('execute',doc.get('execution_permitted')) is False,path
    hashes=verify_evidence(read(EVIDENCE+'engine.json'),read(BROWSER_EVIDENCE+'result.json'),read(EXECUTION),read(REVIEW),read(BROWSER_EVIDENCE+'browser.json'))
    execution=read(EXECUTION)
    for path,pin in execution['retained_evidence_sha256'].items():assert file_sha(ROOT/path)==pin,path
    assert execution['visual_review_sha256']==file_sha(ROOT/REVIEW)
    # This exact checker asserts compiled-catalog mismatch refusal in index mode
    # before writing PASS. Its receipt does not emit a separate refusal boolean.
    assert file_sha(ROOT/PARITY_SOURCE)==PARITY_SOURCE_SHA
    for name in ['main','index','snapshots']:
        verify_parity_receipt(name,read(EVIDENCE+name+'-parity.json'))
    assert file_sha(ROOT/delivery.MANIFEST)==delivery.PARENT_MANIFEST
    assert not (ROOT/PROOF).exists() and not (ROOT/SAVED).exists()
    delivery.scopes()
    return source,request,pref,hashes

def artifact():
    run=api(REPO+f'/actions/runs/{RUN}/attempts/2')
    assert run['status']=='completed' and run['conclusion']=='failure' and run['head_sha']==SOURCE and run['head_branch']==BRANCH
    jobs=api(REPO+f'/actions/runs/{RUN}/attempts/2/jobs')['jobs']
    assert {j['name'] for j in jobs}=={'select-request','delivery'}
    selected=next(j for j in jobs if j['name']=='select-request');engine_job=next(j for j in jobs if j['name']=='delivery')
    assert selected['conclusion']=='success' and engine_job['conclusion']=='failure'
    steps={s['name']:s['conclusion'] for s in engine_job['steps']}
    assert steps['Assemble indexed candidate, build once and verify parity']=='success'
    assert {n for n,c in steps.items() if c=='failure'}=={'Verify desktop and narrow query, atlas, seasons, dashboard updates and source links'}
    browser_run=api(REPO+f'/actions/runs/{BROWSER_RUN}/attempts/2')
    assert browser_run['status']=='completed' and browser_run['conclusion']=='success' and browser_run['head_sha']==BROWSER_SOURCE and browser_run['head_branch']==BRANCH
    browser_jobs=api(REPO+f'/actions/runs/{BROWSER_RUN}/attempts/2/jobs')['jobs']
    assert {j['name'] for j in browser_jobs}=={'select-request','browser'} and all(j['conclusion']=='success' for j in browser_jobs)
    browser_meta=api(REPO+'/actions/artifacts/'+str(BROWSER_ARTIFACT['id']))
    assert browser_meta['workflow_run']['id']==BROWSER_RUN and browser_meta['workflow_run']['head_sha']==BROWSER_SOURCE
    assert browser_meta['name']=='wicc-review-width-browser-resume-evidence-v1' and browser_meta['expired'] is False
    assert browser_meta['size_in_bytes']==BROWSER_ARTIFACT['bytes'] and browser_meta['digest']=='sha256:'+BROWSER_ARTIFACT['sha256']
    meta=api(REPO+'/actions/artifacts/'+str(ARTIFACT['id']))
    assert meta['workflow_run']['id']==RUN and meta['workflow_run']['head_sha']==SOURCE and meta['name']=='wicc-review-width-delivery-candidate-v1' and meta['expired'] is False
    assert meta['size_in_bytes']==ARTIFACT['bytes'] and meta['digest']=='sha256:'+ARTIFACT['sha256']
    path=OUT/'candidate.zip'
    with path.open('xb') as stream:subprocess.run(['gh','api',REPO+f"/actions/artifacts/{ARTIFACT['id']}/zip"],stdout=stream,check=True,timeout=600)
    assert path.stat().st_size==ARTIFACT['bytes'] and file_sha(path)==ARTIFACT['sha256']
    return path

def verify_candidate(target,hashes):
    manifest_path=target/delivery.MANIFEST;assert file_sha(manifest_path)==FINAL_MANIFEST
    final=json.loads(manifest_path.read_bytes());inventory=read(EVIDENCE+'compile-inventory.json');scope=delivery.scopes()
    assert len(inventory['rust_source_sha256'])==105 and len(inventory['compile_time_data_sha256'])==155
    for path,pin in hashes.items():
        assert file_sha(target/path)==pin,path
        if path!=delivery.MANIFEST:assert final['sha256'][path]==pin,path
    for group in ['rust_source_sha256','compile_time_data_sha256']:
        for path,pin in inventory[group].items():
            actual=target/path if path in hashes else ROOT/path
            assert file_sha(actual)==pin==final['sha256'][path],path
    generated=set(hashes)-{delivery.WASM,delivery.MANIFEST}
    expected=delivery.engine_manifest(read(delivery.MANIFEST),final['sha256'],scope,generated_paths=generated,
        logical_sha=LOGICAL,wasm_sha=BINARY,source_commit=SOURCE,compiler=read(EVIDENCE+'engine.json')['compiler'],
        inventory=inventory,proof=read(EVIDENCE+'dependency-proof.json'))
    assert final==expected
    packet=json.loads((target/'almanac/query-data.json').read_bytes())
    assert packet['logical_sha256']==LOGICAL and packet['logical_byte_length']==LOGICAL_BYTES
    assert len(packet['parts'])==12 and sum(p['byte_length'] for p in packet['parts'])==LOGICAL_BYTES
    assert {'almanac/'+p['path'] for p in packet['parts']}=={p for p in hashes if p.startswith('almanac/query-parts/')}
    for row in packet['parts']:
        path='almanac/'+row['path'];assert hashes[path]==row['sha256'] and (target/path).stat().st_size==row['byte_length']
    catalog=json.loads((target/'almanac/index-catalog.json').read_bytes());assert catalog['source_count']==631
    assert catalog['bundle_sha256']==read(EVIDENCE+'index-parity.json')['payload_sha256']

def install(source,request,pref,hashes):
    main=api(REPO+'/git/ref/heads/main')['object']['sha']
    protected=(set(pref['input_sha256'])|set(pref['parent_files'])|set(pref['disabled_requests'])|{PREFLIGHT})-set(hashes)-{REQUEST,PROOF,SAVED}
    before=objects(source,protected);assert all(before.values())
    restored=OUT/'restored';target=saved.extract_candidate(artifact(),hashes,file_sha(ROOT/(EVIDENCE+'engine.json')),restored)
    assert (restored/'engine.json').read_bytes()==(ROOT/(EVIDENCE+'engine.json')).read_bytes()
    verify_candidate(target,hashes)
    files={};entries=[]
    for path,origin in [(p,target/p) for p in sorted(hashes)]+[(SAVED,target/delivery.MANIFEST)]:
        raw=origin.read_bytes();identity=transport.store(raw);assert identity==oid(raw)
        files[path]={'sha256':sha(raw),'bytes':len(raw),'git_blob_oid':identity};entries.append({'path':path,'mode':'100644','type':'blob','sha':identity});del raw
    proof={'schema':'osw.wicc-review-width-installed.v1','status':'EXACT_REVIEWED_ARTIFACT_INSTALLED',
        'installation_transport':'cloud_git_nonforce_single_ref_v1','installation_control_commit':source,
        'installation_run_id':os.environ['GITHUB_RUN_ID'],'installation_run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],
        'files':dict(files),'logical_sha256':LOGICAL,'logical_bytes':LOGICAL_BYTES,'engine_manifest_sha256':FINAL_MANIFEST,
        'wasm_sha256':BINARY,'candidate_artifact':ARTIFACT,'visual_review_sha256':file_sha(ROOT/REVIEW),
        'verified_engine_run_id':RUN,'verified_engine_run_attempt':2,
        'verified_browser_run_id':BROWSER_RUN,'verified_browser_run_attempt':2,'source_documents':631,'scoped_width_records':175,'scoped_width_owners':88,
        'new_width_records':1,'new_width_samples':0,'new_length_records':0,'new_geographic_footprints':0,
        'browser_verified':True,'visual_review_complete':True,'local_preview_synchronized':False,'main_merged':False,'full_goal_complete':False}
    request.update(execution_permitted=False,working_branch_installation_permitted=False,cloud_git_object_transport_permitted=False,status='DISABLED_IN_EXACT_ARTIFACT_INSTALLATION_COMMIT')
    for path,raw in [(PROOF,encode(proof)),(REQUEST,encode(request))]:
        identity=transport.store(raw);assert identity==oid(raw);files[path]={'sha256':sha(raw),'bytes':len(raw),'git_blob_oid':identity};entries.append({'path':path,'mode':'100644','type':'blob','sha':identity})
    commit=transport.candidate(source,entries,OUT/'installation.index');checked=transport.objects(commit,files)
    assert checked=={p:{'oid':r['git_blob_oid'],'byteSize':r['bytes']} for p,r in files.items()}
    assert transport.objects(commit,protected)==before
    assert saved.base.branch_head()==source and api(REPO+'/git/ref/heads/main')['object']['sha']==main
    transport.publish(commit,BRANCH)
    assert saved.base.branch_head()==commit and objects(commit,files)==checked and api(REPO+'/git/ref/heads/main')['object']['sha']==main
    (OUT/'result.json').write_bytes(encode({'status':'PASS','installed_commit':commit,'control_commit':source,'files':files,
        'protected_paths_preserved':len(protected),'request_disabled_in_installed_commit':True,'working_branch_installed':True,
        'main_unchanged':True,'local_preview_synchronized':False,'full_goal_complete':False}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--cloud-install',action='store_true',required=True);parser.add_argument('--preflight-only',action='store_true');args=parser.parse_args()
    source,request,pref,hashes=controls()
    if args.preflight_only:print('Exact saved WICC width installation preflight passed')
    else:
        OUT.mkdir(parents=True,exist_ok=False)
        try:install(source,request,pref,hashes)
        except Exception as error:
            (OUT/'failure.json').write_bytes(encode({'status':'FAIL','control_commit':source,'error':type(error).__name__+': '+str(error)[:2500],'instruction':'Inspect authoritative branch; ref update may already have succeeded.'}));raise
