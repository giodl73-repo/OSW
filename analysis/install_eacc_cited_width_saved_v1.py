"""Install the exact reviewed EACC width artifact in cloud without rebuilding."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import install_published_current_speed_saved_v1 as saved
import eacc_cited_width_delivery_v2 as delivery
import verified_artifact_git_transport_v1 as transport

ROOT=Path(__file__).resolve().parents[1]
REPO=saved.REPO;BRANCH=saved.BRANCH
REQUEST='research/eacc-cited-width-installation-request-v1.json'
PREFLIGHT='research/eacc-cited-width-installation-preflight-v1.json'
WORKFLOW='.github/workflows/install-eacc-cited-width-saved-v1.yml'
PROOF='research/eacc-cited-width-installed-v1.json'
SAVED='research/eacc-cited-width-installation-saved-engine-manifest-v1.json'
EVIDENCE='research/eacc-cited-width-verified-run-v3/'
REVIEW='research/eacc-cited-width-visual-review-v1.json'
EXECUTION='research/eacc-cited-width-delivery-execution-review-v1.json'
OUT=ROOT/'.pytest_cache/eacc-cited-width-installation-v1'
SOURCE='2c049b6c8bbf382c11c4bba3a7fe5b0b76cfddaf'
RUN=40663806252
BROWSER_RUN=40663806252
BROWSER_SOURCE='2c049b6c8bbf382c11c4bba3a7fe5b0b76cfddaf'
BROWSER_ARTIFACT={'id':12806347818,'bytes':1192485,'sha256':'0a170aad055c1b5868374e180866c10161ed72bcc892c3153a091496c234a6a7'}
BROWSER_EVIDENCE='research/eacc-cited-width-verified-run-v3/'
LOGICAL='bb343f71dd42ba40dcc688aa4209c72a884f909f31d046e2158d14ea994bfc24'
LOGICAL_BYTES=190553938
BINARY='a0c96141734ec124dbd7b0153c412de8ed755cf15357cbb06781f07a4eeab1a0'
FINAL_MANIFEST='bfd24fac7c745b3891136fca77a1f6c1ac8a2a55923abc0f74dd30aaa52870e5'
ARTIFACT={'id':12806227928,'bytes':96283990,'sha256':'7b9ff562b37933cc1763b75d4d10b433b6afa804dfd74c018ee681ceca620329'}
INDEX_LOGICAL='1116cb07022cc9c4dfc19cf57b03af6c25dae9cd6df77f6aa75e8c66bb4e65c9'
PARITY_SOURCE='analysis/check_eacc_cited_width_parity_v1.mjs'
PARITY_SOURCE_SHA='e01178b43e2bf5858f798d84d6d9cecf3daeb39b7d76cce9e5e1b73a365a31ab'
sha,oid,encode,api,objects,file_sha=saved.sha,saved.oid,saved.encode,saved.api,saved.objects,saved.file_sha

def read(path):return json.loads((ROOT/path).read_bytes())

def verify_parity_receipt(name,parity):
    count={'main':71,'index':27,'snapshots':3}[name]
    assert parity['status']=='PASS' and len(parity['checks'])==count and parity['initialization_metadata_equal'] is True
    assert all(r['entire_response_equal'] is True for r in parity['checks']) and parity['wasm_sha256']==BINARY
    assert 0<parity['max_wasm_linear_memory_bytes']<=3221225472
    assert parity['payload_sha256']==(INDEX_LOGICAL if name=='index' else LOGICAL)
    assert parity['mode']==('candidate' if name=='snapshots' else name)
    if name=='snapshots':assert {r['view'] for r in parity['checks']}=={'atlas','seasons','dashboard'}

def verify_request(request):
    for key,value in {'schema':'osw.eacc-cited-width-installation-request.v1','workflow':WORKFLOW,
            'execution_permitted':True,'working_branch_installation_permitted':True,
            'cloud_git_object_transport_permitted':True,'max_cloud_jobs':1,'max_heavy_local_jobs':0}.items():
        assert type(request.get(key)) is type(value) and request[key]==value,key
    for key in ['native_build_permitted','wasm_build_permitted','browser_automation_permitted',
            'scientific_source_processing_permitted','source_field_processing_permitted',
            'local_bulk_sync_permitted','main_merge_permitted']:assert request.get(key) is False,key

def verify_evidence(engine,result,execution,review,browser):
    assert engine['status']=='PASS' and engine['source_commit']==SOURCE
    assert engine['logical_sha256']==LOGICAL and engine['logical_bytes']==LOGICAL_BYTES and engine['wasm_sha256']==BINARY
    assert [engine[k] for k in ['rust_tests_passed','main_query_comparisons','source_query_comparisons','complete_api_comparisons']]==[239,71,27,3]
    assert engine['prior_speed_whole_responses_preserved']==2 and engine['new_width_records']==1
    assert engine['new_width_samples']==engine['new_length_records']==0 and engine['installed'] is False
    assert engine['source_index_audit']=={'original_sources_verified':631,'original_source_strings_preserved':631,'replaced_source_paths':[],'added_source_paths':[delivery.core.SOURCE],'scientific_source_documents_replaced':0}
    assert result=={**engine,'browser_verified':True,'visual_review_complete':False,'run_id':str(RUN),'run_attempt':'1','installed':False,'full_goal_complete':False}
    assert execution['status']=='PASS_ENGINE_SOURCE_INDEX_BROWSER_AND_INDIVIDUAL_VISUAL_REVIEW_INSTALLATION_PENDING'
    assert execution['candidate_artifact']=={**ARTIFACT,'downloaded_locally':False}
    assert execution['source_commit']==review['source_commit']==SOURCE
    assert execution['run_id']==review['run_id']==RUN and execution['run_attempt']==review['run_attempt']==1
    assert execution['engine_manifest_sha256']==FINAL_MANIFEST and execution['logical_sha256']==LOGICAL and execution['logical_bytes']==LOGICAL_BYTES and execution['wasm_sha256']==BINARY
    assert execution['intended_width_records_after_installation']==176 and execution['intended_width_owners_after_installation']==89 and execution['intended_indexed_documents_after_installation']==632 and execution['installed'] is False
    assert review['status']=='PASS_20_ACTUAL_SCREENSHOTS_INDIVIDUALLY_INSPECTED' and review['independent_visual_review_complete'] is True
    assert review['evidence_zip_digest_and_extracted_members_verified'] is True
    assert execution['evidence_artifact']==review['evidence_artifact']==BROWSER_ARTIFACT
    assert browser['status']=='PASS' and not browser['page_errors'] and not browser['missing_assets'] and not browser['original_science_downloads']
    assert review['screenshots']==browser['screenshots'] and len(review['screenshots'])==20 and len({r['path'] for r in review['screenshots']})==20
    assert all(r['geometry']['clipped_axes']==[] and r['geometry']['width']>0 and r['geometry']['height']>0 for r in review['screenshots'])
    hashes=engine['generated_sha256'];assert len(hashes)==18 and hashes[delivery.WASM]==BINARY and hashes[delivery.MANIFEST]==FINAL_MANIFEST
    assert sum(p.startswith('almanac/query-parts/') for p in hashes)==12
    return dict(hashes)



def controls():
    assert os.environ.get('GITHUB_ACTIONS')=='true' and os.environ.get('RUNNER_OS')=='Linux'
    assert os.environ.get('OSW_EACC_CITED_WIDTH_INSTALL_V1')=='1' and os.environ.get('GITHUB_EVENT_NAME')=='push'
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
    run=api(REPO+f'/actions/runs/{RUN}/attempts/1')
    assert run['status']=='completed' and run['conclusion']=='success' and run['head_sha']==SOURCE and run['head_branch']==BRANCH
    jobs=api(REPO+f'/actions/runs/{RUN}/attempts/1/jobs')['jobs']
    assert {j['name'] for j in jobs}=={'select-request','delivery'} and all(j['conclusion']=='success' for j in jobs)
    steps={s['name']:s['conclusion'] for j in jobs for s in j['steps']}
    for name in ['Verify frozen inputs and lightweight checks','Assemble indexed candidate, build once and verify parity','Verify desktop and narrow query, atlas, seasons, dashboard updates and source links']:assert steps[name]=='success'
    for desc,name in [(BROWSER_ARTIFACT,'eacc-cited-width-delivery-evidence-v3'),(ARTIFACT,'eacc-cited-width-delivery-candidate-v3')]:
        meta=api(REPO+'/actions/artifacts/'+str(desc['id']))
        assert meta['workflow_run']['id']==RUN and meta['workflow_run']['head_sha']==SOURCE and meta['name']==name and meta['expired'] is False
        assert meta['size_in_bytes']==desc['bytes'] and meta['digest']=='sha256:'+desc['sha256']
    path=OUT/'candidate.zip'
    with path.open('xb') as stream:subprocess.run(['gh','api',REPO+f"/actions/artifacts/{ARTIFACT['id']}/zip"],stdout=stream,check=True,timeout=600)
    assert path.stat().st_size==ARTIFACT['bytes'] and file_sha(path)==ARTIFACT['sha256']
    return path


def verify_candidate(target,hashes):
    manifest_path=target/delivery.MANIFEST;assert file_sha(manifest_path)==FINAL_MANIFEST
    final=json.loads(manifest_path.read_bytes());inventory=read(EVIDENCE+'compile-inventory.json');scope=delivery.scopes()
    assert len(inventory['rust_source_sha256'])==106 and len(inventory['compile_time_data_sha256'])==156
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
    catalog=json.loads((target/'almanac/index-catalog.json').read_bytes());assert catalog['source_count']==632
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
    proof={'schema':'osw.eacc-cited-width-installed.v1','status':'EXACT_REVIEWED_ARTIFACT_INSTALLED',
        'installation_transport':'cloud_git_nonforce_single_ref_v1','installation_control_commit':source,
        'installation_run_id':os.environ['GITHUB_RUN_ID'],'installation_run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],
        'files':dict(files),'logical_sha256':LOGICAL,'logical_bytes':LOGICAL_BYTES,'engine_manifest_sha256':FINAL_MANIFEST,
        'wasm_sha256':BINARY,'candidate_artifact':ARTIFACT,'visual_review_sha256':file_sha(ROOT/REVIEW),
        'verified_engine_run_id':RUN,'verified_engine_run_attempt':1,
        'verified_browser_run_id':BROWSER_RUN,'verified_browser_run_attempt':1,'source_documents':632,'scoped_width_records':176,'scoped_width_owners':89,
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
    if args.preflight_only:print('Exact saved EACC width installation preflight passed')
    else:
        OUT.mkdir(parents=True,exist_ok=False)
        try:install(source,request,pref,hashes)
        except Exception as error:
            (OUT/'failure.json').write_bytes(encode({'status':'FAIL','control_commit':source,'error':type(error).__name__+': '+str(error)[:2500],'instruction':'Inspect authoritative branch; ref update may already have succeeded.'}));raise
