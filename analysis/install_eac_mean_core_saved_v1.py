"""Install reviewed EAC mean-core section artifacts in cloud without rebuilding."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import install_published_current_speed_saved_v1 as saved
import verified_artifact_git_transport_v1 as transport
import eac_mean_core_dashboard_context_v1 as context
import resume_eac_mean_core_browser_v1 as browser_resume
import eac_mean_core_delivery_v1 as delivery

ROOT=Path(__file__).resolve().parents[1]
REPO=saved.REPO;BRANCH=saved.BRANCH
REQUEST='research/eac-mean-core-installation-request-v1.json'
PREFLIGHT='research/eac-mean-core-installation-preflight-v1.json'
WORKFLOW='.github/workflows/install-eac-mean-core-saved-v1.yml'
PROOF='research/eac-mean-core-installed-v1.json'
SAVED='research/eac-mean-core-installation-saved-engine-manifest-v1.json'
EVIDENCE='research/eac-mean-core-engine-run-v1/'
BROWSER='research/eac-mean-core-browser-run-v1/'
REVIEW='research/eac-mean-core-browser-visual-review-v1.json'
EXECUTION='research/eac-mean-core-delivery-execution-review-v1.json'
OUT=ROOT/'.pytest_cache/eac-mean-core-installation-v1'
SOURCE='c67596d8a89f1f8da11868cca3d24d05bb0bd9b4';RUN=40700928560
BROWSER_SOURCE='f0e054b7a6ce409b717352845d1d91c2686f87ab';BROWSER_RUN=40707146533
BROWSER_ARTIFACT={'id':12824661858,'bytes':1169812,'sha256':'bba178727c9697536528d96d3a5c635525e9cad4fd4ba6474779a5d10c33db29'}
ARTIFACT=browser_resume.ARTIFACT
LOGICAL='23f70fec771c7302b2351d8d254ec0acc988397543eb96d233ac10385b384ffb'
LOGICAL_BYTES=190579739
BINARY='f7d4f6eca6fb1c85ca8b27c9bf0d72682804d98ac6e335e2e7b46e822a64f9d0'
FINAL_MANIFEST='243f7cab52958f7c21f4975ec5159e8406eebea05d77641579495658dddf886b'
sha,oid,encode,api,objects,file_sha=saved.sha,saved.oid,saved.encode,saved.api,saved.objects,saved.file_sha

def read(path):return json.loads((ROOT/path).read_bytes())

def verify_request(r):
    for key,value in {'schema':'osw.eac-mean-core-installation-request.v1','workflow':WORKFLOW,
        'execution_permitted':True,'working_branch_installation_permitted':True,
        'cloud_git_object_transport_permitted':True,'max_cloud_jobs':1,'max_heavy_local_jobs':0}.items():
        assert type(r.get(key)) is type(value) and r[key]==value,key
    for key in ['native_build_permitted','wasm_build_permitted','browser_automation_permitted',
        'scientific_source_processing_permitted','source_field_processing_permitted','local_bulk_sync_permitted','main_merge_permitted']:
        assert r.get(key) is False,key

def verify_evidence(engine,result,review,browser):
    browser_resume.verify_engine(engine)
    assert engine['new_mean_core_section_records']==5 and engine['new_width_records']==engine['new_length_records']==engine['new_independent_observations']==0
    for key,value in engine.items():
        if key not in ['generated_sha256','browser_verified']:assert result[key]==value,key
    assert result['browser_verified'] is True and result['browser_source_commit']==BROWSER_SOURCE
    assert str(result['browser_run_id'])==str(BROWSER_RUN) and str(result['browser_run_attempt'])=='1'
    assert result['native_or_wasm_rebuild'] is False and result['scientific_data_or_wasm_changed'] is False
    assert result['manifest_updated_for_presentation'] is True and result['saved_artifact']==ARTIFACT
    assert result['saved_engine_evidence_sha256']==file_sha(ROOT/(EVIDENCE+'engine.json'))
    assert result['presentation_contract_sha256']==context.sha(context.FILE)
    assert result['browser_harness_sha256']==file_sha(ROOT/'analysis/check_eac_mean_core_browser_v2.py')
    old=engine['generated_sha256'];new=result['generated_sha256']
    assert set(old)==set(new) and len(new)==18
    assert new[delivery.MANIFEST]==FINAL_MANIFEST and new[delivery.WASM]==BINARY
    assert all(new[p]==pin for p,pin in old.items() if p!=delivery.MANIFEST)
    context.verify_sources(context.read(context.OLD))
    context.verify_manifest_delta(context.read(context.OLD),read(BROWSER+'engine-manifest.json'),BROWSER_SOURCE)
    assert file_sha(ROOT/(BROWSER+'engine-manifest.json'))==FINAL_MANIFEST
    assert review['status']=='PASS_ALL_16_ACTUAL_CAPTURES_AND_SAVED_ENGINE_CUSTODY_REQUEST_DISABLED'
    assert review['browser_source_commit']==BROWSER_SOURCE and review['browser_run_id']==BROWSER_RUN and review['browser_run_attempt']==1
    assert review['actual_captures_individually_reviewed']==16 and review['request_disabled'] is True
    assert review['ready_for_saved_candidate_installation'] is True and review['installed'] is False
    assert review['browser_artifact']==BROWSER_ARTIFACT and review['saved_engine_artifact']==ARTIFACT
    assert review['browser_result_sha256']==file_sha(ROOT/(BROWSER+'result.json'))
    assert review['browser_report_sha256']==file_sha(ROOT/(BROWSER+'browser.json'))
    assert review['reviewed_engine_manifest_sha256']==FINAL_MANIFEST
    assert review['screenshots']==[{**row,'individually_viewed':True,'readable_without_capture_clipping':True} for row in browser['screenshots']]
    assert browser['status']=='PASS' and not browser['page_errors'] and not browser['missing_assets'] and not browser['original_science_downloads']
    images=browser['screenshots'];assert len(images)==len({r['path'] for r in images})==16
    assert all(r['geometry']['clipped_axes']==[] and r['geometry']['width']>0 and r['geometry']['height']>0 for r in images)
    return dict(new)

def controls():
    assert os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true' and os.environ.get('RUNNER_OS')=='Linux'
    assert os.environ.get('OSW_EAC_MEAN_CORE_INSTALL_V1')=='1' and os.environ.get('GITHUB_EVENT_NAME')=='push'
    assert os.environ.get('GITHUB_REPOSITORY')=='giodl73-repo/OSW' and os.environ.get('GITHUB_REF')=='refs/heads/'+BRANCH
    assert len(os.sched_getaffinity(0))==1 and os.getpriority(os.PRIO_PROCESS,0)>=15
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:assert os.environ.get(key)=='1'
    source=os.environ['GITHUB_SHA'];assert transport.git('rev-parse','HEAD')==saved.base.branch_head()==source
    assert not transport.git('status','--porcelain').strip()
    r=read(REQUEST);verify_request(r);assert file_sha(ROOT/PREFLIGHT)==r['preflight_sha256']
    pref=read(PREFLIGHT)
    for p,pin in pref['input_sha256'].items():assert file_sha(ROOT/p)==pin,p
    for p,row in pref['parent_files'].items():assert file_sha(ROOT/p)==row['sha256'] and (ROOT/p).stat().st_size==row['bytes'],p
    phase=read('research/current-gap-delivery-phase.json');assert phase['heavy_work_permitted'] is False and phase['max_heavy_local_jobs']==0 and phase['max_heavy_cloud_jobs']==1
    for p in pref['disabled_requests']:
        d=read(p);assert d.get('execute',d.get('execution_permitted')) is False,p
    hashes=verify_evidence(read(EVIDENCE+'engine.json'),read(BROWSER+'result.json'),read(REVIEW),read(BROWSER+'browser.json'))
    execution=read(EXECUTION)
    assert execution['status']=='PASS_ENGINE_BROWSER_AND_INDIVIDUAL_VISUAL_REVIEW_INSTALLATION_PENDING'
    assert execution['visual_review_sha256']==file_sha(ROOT/REVIEW)
    for p,pin in execution['retained_evidence_sha256'].items():assert file_sha(ROOT/p)==pin,p
    for name,count in [('main',99),('index',35),('snapshots',3)]:
        d=read(EVIDENCE+name+'-parity.json')
        assert d['status']=='PASS' and len(d['checks'])==count and d['initialization_metadata_equal'] is True
        assert d['wasm_sha256']==BINARY and all(r['entire_response_equal'] is True for r in d['checks'])
        if name!='index':assert d['payload_sha256']==LOGICAL
    assert file_sha(ROOT/delivery.MANIFEST)==delivery.PARENT_MANIFEST
    assert not (ROOT/PROOF).exists() and not (ROOT/SAVED).exists()
    return source,r,pref,hashes

def artifact():
    run=api(REPO+f'/actions/runs/{RUN}/attempts/2')
    assert run['status']=='completed' and run['conclusion']=='failure' and run['head_sha']==SOURCE
    jobs=api(REPO+f'/actions/runs/{RUN}/attempts/2/jobs')['jobs']
    steps={s['name']:s['conclusion'] for j in jobs for s in j['steps']}
    assert steps['Assemble indexed candidate, build native and WASM, verify complete responses']=='success'
    run=api(REPO+f'/actions/runs/{BROWSER_RUN}/attempts/1')
    assert run['status']=='completed' and run['conclusion']=='success' and run['head_sha']==BROWSER_SOURCE
    for desc,runid,source in [(ARTIFACT,RUN,SOURCE),(BROWSER_ARTIFACT,BROWSER_RUN,BROWSER_SOURCE)]:
        meta=api(REPO+'/actions/artifacts/'+str(desc['id']))
        assert meta['workflow_run']['id']==runid and meta['workflow_run']['head_sha']==source and meta['expired'] is False
        assert meta['size_in_bytes']==desc['bytes'] and meta['digest']=='sha256:'+desc['sha256']
    path=OUT/'candidate.zip'
    with path.open('xb') as stream:subprocess.run(['gh','api',REPO+f"/actions/artifacts/{ARTIFACT['id']}/zip"],stdout=stream,check=True,timeout=600)
    assert path.stat().st_size==ARTIFACT['bytes'] and file_sha(path)==ARTIFACT['sha256']
    return path

def verify_candidate(target,hashes):
    final=json.loads((target/delivery.MANIFEST).read_bytes())
    assert file_sha(target/delivery.MANIFEST)==FINAL_MANIFEST
    context.verify_manifest_delta(context.read(context.OLD),final,BROWSER_SOURCE)
    inventory=read(EVIDENCE+'compile-inventory.json')
    assert len(inventory['rust_source_sha256'])==108 and len(inventory['compile_time_data_sha256'])==160
    for p,pin in hashes.items():
        assert file_sha(target/p)==pin,p
        if p!=delivery.MANIFEST:assert final['sha256'][p]==pin,p
    for group in ['rust_source_sha256','compile_time_data_sha256']:
        for p,pin in inventory[group].items():
            actual=target/p if p in hashes else ROOT/p
            assert file_sha(actual)==pin==final['sha256'][p],p
    packet=json.loads((target/'almanac/query-data.json').read_bytes())
    assert packet['logical_sha256']==LOGICAL and packet['logical_byte_length']==LOGICAL_BYTES
    assert len(packet['parts'])==12 and sum(p['byte_length'] for p in packet['parts'])==LOGICAL_BYTES
    assert {'almanac/'+p['path'] for p in packet['parts']}=={p for p in hashes if p.startswith('almanac/query-parts/')}
    for row in packet['parts']:
        p='almanac/'+row['path'];assert hashes[p]==row['sha256'] and (target/p).stat().st_size==row['byte_length']
    catalog=json.loads((target/'almanac/index-catalog.json').read_bytes())
    assert catalog['source_count']==634 and catalog['bundle_sha256']==read(EVIDENCE+'index-parity.json')['payload_sha256']

def install(source,request,pref,hashes):
    main=api(REPO+'/git/ref/heads/main')['object']['sha']
    protected=(set(pref['input_sha256'])|set(pref['parent_files'])|set(pref['disabled_requests'])|{PREFLIGHT})-set(hashes)-{REQUEST,PROOF,SAVED}
    before=objects(source,protected);assert all(before.values())
    engine=read(EVIDENCE+'engine.json');restored=OUT/'restored'
    target=saved.extract_candidate(artifact(),engine['generated_sha256'],file_sha(ROOT/(EVIDENCE+'engine.json')),restored)
    assert (restored/'engine.json').read_bytes()==(ROOT/(EVIDENCE+'engine.json')).read_bytes()
    shutil.copyfile(ROOT/(BROWSER+'engine-manifest.json'),target/delivery.MANIFEST)
    verify_candidate(target,hashes)
    files={};entries=[]
    for p,origin in [(p,target/p) for p in sorted(hashes)]+[(SAVED,target/delivery.MANIFEST)]:
        raw=origin.read_bytes();identity=transport.store(raw);assert identity==oid(raw)
        files[p]={'sha256':sha(raw),'bytes':len(raw),'git_blob_oid':identity};entries.append({'path':p,'mode':'100644','type':'blob','sha':identity});del raw
    proof={'schema':'osw.eac-mean-core-installed.v1','status':'EXACT_REVIEWED_ARTIFACT_INSTALLED',
        'installation_transport':'cloud_git_nonforce_single_ref_v1','installation_control_commit':source,
        'installation_run_id':os.environ['GITHUB_RUN_ID'],'installation_run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],
        'files':dict(files),'logical_sha256':LOGICAL,'logical_bytes':LOGICAL_BYTES,'engine_manifest_sha256':FINAL_MANIFEST,
        'wasm_sha256':BINARY,'candidate_artifact':ARTIFACT,'visual_review_sha256':file_sha(ROOT/REVIEW),
        'verified_engine_run_id':RUN,'verified_engine_run_attempt':2,'verified_browser_run_id':BROWSER_RUN,'verified_browser_run_attempt':1,
        'source_documents':634,'publication_sources':215,'mean_core_section_records':5,'mean_core_section_owners':1,'reference_routes':83,'reference_route_owners':76,'scoped_width_records':176,'scoped_width_owners':89,
        'new_mean_core_section_records':5,'new_length_records':0,'new_width_records':0,'new_independent_observations':0,'native_or_wasm_rebuild':False,
        'browser_verified':True,'visual_review_complete':True,'local_preview_synchronized':False,'main_merged':False,'full_goal_complete':False}
    request.update(execution_permitted=False,working_branch_installation_permitted=False,cloud_git_object_transport_permitted=False,status='DISABLED_IN_EXACT_ARTIFACT_INSTALLATION_COMMIT')
    for p,raw in [(PROOF,encode(proof)),(REQUEST,encode(request))]:
        identity=transport.store(raw);assert identity==oid(raw);files[p]={'sha256':sha(raw),'bytes':len(raw),'git_blob_oid':identity};entries.append({'path':p,'mode':'100644','type':'blob','sha':identity})
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
    if args.preflight_only:print('Exact saved EAC model-mean section installation preflight passed')
    else:
        OUT.mkdir(parents=True,exist_ok=False)
        try:install(source,request,pref,hashes)
        except Exception as error:
            (OUT/'failure.json').write_bytes(encode({'status':'FAIL','control_commit':source,'error':type(error).__name__+': '+str(error)[:2500],'instruction':'Inspect authoritative branch; ref update may already have succeeded.'}));raise
