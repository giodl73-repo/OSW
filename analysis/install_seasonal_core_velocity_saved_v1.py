"""Install the exact reviewed seasonal candidate in one cloud job; no rebuild."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import install_published_current_speed_saved_v1 as saved
import resume_seasonal_core_browser_v1 as resume
import verified_artifact_git_transport_v1 as transport

ROOT=Path(__file__).resolve().parents[1]
REPO=saved.REPO;BRANCH=saved.BRANCH
REQUEST='research/seasonal-core-velocity-installation-request-v1.json'
PREFLIGHT='research/seasonal-core-velocity-installation-preflight-v1.json'
WORKFLOW='.github/workflows/install-seasonal-core-velocity-saved-v1.yml'
PROOF='research/seasonal-core-velocity-installed-v1.json'
SAVED='research/seasonal-core-velocity-installation-saved-engine-manifest-v1.json'
EVIDENCE='research/seasonal-core-velocity-browser-pass-v1/'
REVIEW='research/seasonal-core-velocity-visual-review-v1.json'
EXECUTION='research/seasonal-core-velocity-delivery-execution-review-v1.json'
INVENTORY='research/seasonal-core-velocity-engine-run-v1/compile-inventory.json'
OUT=ROOT/'.pytest_cache/seasonal-core-velocity-installation-v1'
SOURCE='76dccfa3023bae18bdddc75f37b7c3b20acae581'
RUN=40624642430;ATTEMPT=2
LOGICAL='c27c5c8319ab59fa6069274df1b7d19c87cf5a2aea8a7a04ba808a1636b9e212'
BINARY='6caf567278cb644eed9a45c89028bcadf7d919bb4adba6381503af34fe3e0c16'
FINAL_MANIFEST='a3704ee9d03f68fe6dff1fc9737be584ff573998ef99aa997b1505b773edd36e'
ARTIFACT={'id':12788813020,'bytes':96226830,'sha256':'46b4441ee1ee8629a252700a7f70e4a114cbcc06e1309b23273fc3d7c2fb161f'}
sha,oid,encode,api,objects,file_sha=saved.sha,saved.oid,saved.encode,saved.api,saved.objects,saved.file_sha


def read(path):return json.loads((ROOT/path).read_bytes())


def verify_request(request):
    expected={'schema':'osw.seasonal-core-velocity-installation-request.v1','workflow':WORKFLOW,'execution_permitted':True,
              'working_branch_installation_permitted':True,'cloud_git_object_transport_permitted':True,
              'max_cloud_jobs':1,'max_heavy_local_jobs':0}
    for key,value in expected.items():assert type(request.get(key)) is type(value) and request[key]==value,key
    for key in ['native_build_permitted','wasm_build_permitted','browser_automation_permitted',
                'scientific_source_processing_permitted','source_field_processing_permitted',
                'local_bulk_sync_permitted','main_merge_permitted']:assert request.get(key) is False,key


def verify_evidence(full,engine,execution,review,browser):
    assert full['status']=='PASS' and full['source_commit']=='e66cb4fdeda19f98d4a6cd1a34e405869b7916f4'
    assert full['logical_sha256']==LOGICAL and full['logical_bytes']==190528544 and full['wasm_sha256']==BINARY
    assert [full[k] for k in ['rust_tests_passed','main_query_comparisons','source_query_comparisons','complete_api_comparisons']]==[216,41,20,2]
    assert full['pemba_whole_response_preserved'] is True
    assert full['source_index_audit']['original_source_strings_preserved']==628 and full['source_index_audit']['replaced_source_paths']==[]
    for key in full:
        if key not in ['browser_verified','generated_sha256']:assert engine[key]==full[key],key
    assert engine['browser_verified'] is True and engine['native_or_wasm_rebuild'] is False and engine['installed'] is False
    assert engine['engine_run_id']==40620738758 and str(engine['browser_run_id'])==str(RUN) and str(engine['browser_run_attempt'])==str(ATTEMPT)
    assert engine['browser_source_commit']==SOURCE
    hashes=engine['generated_sha256'];assert len(hashes)==18 and hashes['almanac/query-engine.wasm']==BINARY
    assert hashes['almanac/query-engine.manifest.json']==FINAL_MANIFEST
    assert {p for p in hashes if hashes[p]!=full['generated_sha256'][p]}=={'almanac/query-engine.manifest.json'}
    assert execution['status']=='PASS_ENGINE_SOURCE_INDEX_BROWSER_AND_INDIVIDUAL_VISUAL_REVIEW_INSTALLATION_PENDING'
    assert execution['candidate_artifact']=={**ARTIFACT,'downloaded_locally':False}
    assert execution['engine_manifest_sha256']==FINAL_MANIFEST and execution['indexed_source_documents']==629
    assert execution['seasonal_core_velocity_estimates']==6 and execution['seasonal_core_velocity_owners']==3
    assert execution['new_length_records']==execution['new_width_records']==execution['new_geographic_footprints']==0
    assert review['status']=='PASS_18_ACTUAL_SCREENSHOTS_INDIVIDUALLY_INSPECTED' and review['independent_visual_review_complete'] is True
    assert review['run_id']==RUN and review['run_attempt']==ATTEMPT and review['browser_source_commit']==SOURCE
    assert browser['status']=='PASS' and not browser['page_errors'] and not browser['missing_assets'] and not browser['original_science_downloads']
    assert review['screenshots']==browser['screenshots'] and len(review['screenshots'])==18
    assert len({r['path'] for r in review['screenshots']})==18
    assert all(r['geometry']['clipped_axes']==[] and r['geometry']['width']>0 and r['geometry']['height']>0 for r in review['screenshots'])
    return dict(hashes)


def controls():
    assert os.environ.get('GITHUB_ACTIONS')=='true' and os.environ.get('RUNNER_OS')=='Linux'
    assert os.environ.get('OSW_CORE_INSTALL_V1')=='1' and os.environ.get('GITHUB_EVENT_NAME')=='push'
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
    hashes=verify_evidence(read('research/seasonal-core-velocity-engine-evidence-v1.json'),read(EVIDENCE+'engine.json'),read(EXECUTION),read(REVIEW),read(EVIDENCE+'browser.json'))
    execution=read(EXECUTION)
    for path,pin in execution['retained_evidence_sha256'].items():assert file_sha(ROOT/path)==pin,path
    assert execution['visual_review_sha256']==file_sha(ROOT/REVIEW)
    assert read(EVIDENCE+'result.json')==read(EVIDENCE+'engine.json')
    original=read(EVIDENCE+'source-engine-manifest.json')
    assert file_sha(ROOT/(EVIDENCE+'source-engine-manifest.json'))=='f286c4705ec666456b4ef7b4cc9d912c61080a0494009faacdd700aa5ba89b3c'
    revision=read('research/seasonal-core-velocity-browser-revision-v2.json')
    expected=resume.revise_manifest(original,revision,source_commit=SOURCE,verification_inputs=read('research/seasonal-core-velocity-browser-resume-preflight-v2.json')['input_sha256'])
    assert read(EVIDENCE+'candidate-engine-manifest.json')==expected
    assert file_sha(ROOT/(EVIDENCE+'candidate-engine-manifest.json'))==FINAL_MANIFEST
    assert file_sha(ROOT/'almanac/query-engine.manifest.json')=='6e5f7e0b2cbe710b911c24360b57c884e905c0a8707c29877ba7b9e39aa9a8d2'
    assert not (ROOT/PROOF).exists() and not (ROOT/SAVED).exists()
    return source,request,pref,hashes


def artifact():
    run=api(REPO+f'/actions/runs/{RUN}/attempts/{ATTEMPT}');assert run['status']=='completed' and run['conclusion']=='success' and run['head_sha']==SOURCE and run['head_branch']==BRANCH
    jobs=api(REPO+f'/actions/runs/{RUN}/attempts/{ATTEMPT}/jobs')['jobs'];assert {j['name'] for j in jobs}=={'select-request','browser'} and all(j['conclusion']=='success' for j in jobs)
    meta=api(REPO+'/actions/artifacts/'+str(ARTIFACT['id']));assert meta['workflow_run']['id']==RUN and meta['workflow_run']['head_sha']==SOURCE
    assert meta['name']=='seasonal-core-velocity-browser-verified-candidate-v1' and meta['expired'] is False
    assert meta['size_in_bytes']==ARTIFACT['bytes'] and meta['digest']=='sha256:'+ARTIFACT['sha256']
    path=OUT/'candidate.zip'
    with path.open('xb') as f:subprocess.run(['gh','api',REPO+f"/actions/artifacts/{ARTIFACT['id']}/zip"],stdout=f,check=True,timeout=600)
    assert path.stat().st_size==ARTIFACT['bytes'] and file_sha(path)==ARTIFACT['sha256']
    return path


def verify_candidate(target,hashes):
    manifest='almanac/query-engine.manifest.json'
    assert (target/manifest).read_bytes()==(ROOT/(EVIDENCE+'candidate-engine-manifest.json')).read_bytes()
    final=read(EVIDENCE+'candidate-engine-manifest.json')
    for path,pin in hashes.items():
        assert file_sha(target/path)==pin,path
        if path!=manifest:assert final['sha256'][path]==pin,path
    inv=read(INVENTORY)
    assert len(inv['rust_source_sha256'])==103 and len(inv['compile_time_data_sha256'])==153
    for group in ['rust_source_sha256','compile_time_data_sha256']:
        for path,pin in inv[group].items():
            actual=target/path if path in hashes else ROOT/path
            assert file_sha(actual)==pin and final['sha256'][path]==pin,path
    revision=read('research/seasonal-core-velocity-browser-revision-v2.json')
    for path,row in revision['runtime_source_changes'].items():assert file_sha(ROOT/path)==row['candidate_sha256']==final['sha256'][path],path
    packet=json.loads((target/'almanac/query-data.json').read_bytes())
    assert packet['logical_sha256']==LOGICAL and packet['logical_byte_length']==190528544
    assert len(packet['parts'])==12 and sum(p['byte_length'] for p in packet['parts'])==190528544
    assert {'almanac/'+p['path'] for p in packet['parts']}=={p for p in hashes if p.startswith('almanac/query-parts/')}
    for row in packet['parts']:
        path='almanac/'+row['path'];assert hashes[path]==row['sha256'] and (target/path).stat().st_size==row['byte_length']
    catalog=json.loads((target/'almanac/index-catalog.json').read_bytes());assert catalog['source_count']==629
    assert catalog['bundle_sha256']==read('research/seasonal-core-velocity-engine-run-v1/index-parity.json')['payload_sha256']


def install(source,request,pref,hashes):
    main=api(REPO+'/git/ref/heads/main')['object']['sha']
    protected=(set(pref['input_sha256'])|set(pref['parent_files'])|set(pref['disabled_requests'])|{PREFLIGHT})-set(hashes)-{REQUEST,PROOF,SAVED}
    before=objects(source,protected);assert all(before.values())
    restored=OUT/'restored';target=saved.extract_candidate(artifact(),hashes,file_sha(ROOT/(EVIDENCE+'engine.json')),restored)
    assert (restored/'engine.json').read_bytes()==(ROOT/(EVIDENCE+'engine.json')).read_bytes()
    verify_candidate(target,hashes)
    files={};entries=[]
    for path,origin in [(p,target/p) for p in sorted(hashes)]+[(SAVED,target/'almanac/query-engine.manifest.json')]:
        raw=origin.read_bytes();identity=transport.store(raw);assert identity==oid(raw)
        files[path]={'sha256':sha(raw),'bytes':len(raw),'git_blob_oid':identity};entries.append({'path':path,'mode':'100644','type':'blob','sha':identity});del raw
    proof={'schema':'osw.seasonal-core-velocity-installed.v1','status':'EXACT_REVIEWED_ARTIFACT_INSTALLED','installation_transport':'cloud_git_nonforce_single_ref_v1','installation_control_commit':source,'installation_run_id':os.environ['GITHUB_RUN_ID'],'installation_run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],'files':dict(files),'logical_sha256':LOGICAL,'logical_bytes':190528544,'engine_manifest_sha256':FINAL_MANIFEST,'wasm_sha256':BINARY,'candidate_artifact':ARTIFACT,'visual_review_sha256':file_sha(ROOT/REVIEW),'verified_browser_run_id':RUN,'verified_browser_run_attempt':ATTEMPT,'source_documents':629,'seasonal_core_velocity_estimates':6,'seasonal_core_velocity_owners':3,'prior_pemba_summaries':15,'new_length_records':0,'new_width_records':0,'new_geographic_footprints':0,'browser_verified':True,'visual_review_complete':True,'local_preview_synchronized':False,'main_merged':False,'full_goal_complete':False}
    request.update(execution_permitted=False,working_branch_installation_permitted=False,cloud_git_object_transport_permitted=False,status='DISABLED_IN_EXACT_ARTIFACT_INSTALLATION_COMMIT')
    for path,raw in [(PROOF,encode(proof)),(REQUEST,encode(request))]:
        identity=transport.store(raw);assert identity==oid(raw);files[path]={'sha256':sha(raw),'bytes':len(raw),'git_blob_oid':identity};entries.append({'path':path,'mode':'100644','type':'blob','sha':identity})
    commit=transport.candidate(source,entries,OUT/'installation.index');checked=transport.objects(commit,files)
    assert checked=={p:{'oid':r['git_blob_oid'],'byteSize':r['bytes']} for p,r in files.items()}
    assert transport.objects(commit,protected)==before
    assert saved.base.branch_head()==source and api(REPO+'/git/ref/heads/main')['object']['sha']==main
    transport.publish(commit,BRANCH)
    assert saved.base.branch_head()==commit and objects(commit,files)==checked and api(REPO+'/git/ref/heads/main')['object']['sha']==main
    (OUT/'result.json').write_bytes(encode({'status':'PASS','installed_commit':commit,'control_commit':source,'files':files,'protected_paths_preserved':len(protected),'request_disabled_in_installed_commit':True,'working_branch_installed':True,'main_unchanged':True,'local_preview_synchronized':False,'full_goal_complete':False}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--cloud-install',action='store_true',required=True);parser.add_argument('--preflight-only',action='store_true');args=parser.parse_args()
    source,request,pref,hashes=controls()
    if args.preflight_only:print('Exact saved seasonal installation preflight passed')
    else:
        OUT.mkdir(parents=True,exist_ok=False)
        try:install(source,request,pref,hashes)
        except Exception as error:
            (OUT/'failure.json').write_bytes(encode({'status':'FAIL','control_commit':source,'error':type(error).__name__+': '+str(error)[:2500],'instruction':'Inspect authoritative branch; ref update may already have succeeded.'}));raise
