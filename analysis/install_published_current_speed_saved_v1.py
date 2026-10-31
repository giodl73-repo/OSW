"""Install the exact reviewed speed delivery in cloud; no builds or data decoding."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import zipfile
import install_azores_2009_section_saved_v1 as base
import verified_artifact_git_transport_v1 as transport
import published_current_speed_delivery_v1 as delivery

ROOT=Path(__file__).resolve().parents[1]
REPO=base.REPO;BRANCH=base.BRANCH
REQUEST='research/published-current-speed-installation-request-v1.json'
PREFLIGHT='research/published-current-speed-installation-preflight-v1.json'
WORKFLOW='.github/workflows/install-published-current-speed-saved-v1.yml'
PROOF='research/published-current-speed-installed-v1.json'
SAVED='research/published-current-speed-installation-saved-engine-manifest-v1.json'
FULL='research/published-current-speed-delivery-engine-evidence-v1.json'
EXECUTION='research/published-current-speed-delivery-execution-review-v1.json'
REVIEW='research/published-current-speed-delivery-visual-review-v1.json'
BROWSER='research/published-current-speed-delivery-browser-evidence-v1.json'
INVENTORY='research/published-current-speed-delivery-compile-inventory-v1.json'
OUT=ROOT/'.pytest_cache/published-current-speed-installation-v1'
SOURCE='d11dd2ddc80e8972209f95dde29c41facfa7ddec'
RUN=40609548146
LOGICAL='037ef0045d75dac4b8893df9bf200bd55e049d4708ceaa56195df9d6da9f5cc4'
BINARY='a59352b7e3dc875d656f3f592ff7809386b8015bfe8412b307ae359818bb3f9b'
FINAL_MANIFEST='6e5f7e0b2cbe710b911c24360b57c884e905c0a8707c29877ba7b9e39aa9a8d2'
ARTIFACT={'id':12783426280,'bytes':96193895,'sha256':'dd8f509442aad186dc7a0538dd4c404f90881c46a927e9fd23897165911deab1'}
sha,oid,encode,api,objects,file_sha=base.sha,base.oid,base.encode,base.api,base.objects,base.file_sha


def read(path):return json.loads((ROOT/path).read_bytes())


def verify_request(request):
    for key,value in {'schema':'osw.published-current-speed-installation-request.v1','workflow':WORKFLOW,'execution_permitted':True,
            'working_branch_installation_permitted':True,'cloud_git_object_transport_permitted':True,
            'max_cloud_jobs':1,'max_heavy_local_jobs':0}.items():
        assert type(request.get(key)) is type(value) and request[key]==value,key
    for key in ['native_build_permitted','wasm_build_permitted','browser_automation_permitted',
                'scientific_source_processing_permitted','source_field_processing_permitted',
                'local_bulk_sync_permitted','main_merge_permitted']:
        assert request.get(key) is False,key


def verify_evidence(full,execution,review,browser):
    assert full['status']=='PASS' and full['stage']=='engine_verified' and full['source_commit']==SOURCE
    assert execution['status']=='PASS_ENGINE_SOURCE_INDEX_BROWSER_AND_INDIVIDUAL_VISUAL_REVIEW_INSTALLATION_PENDING'
    assert execution['source_commit']==review['source_commit']==SOURCE
    assert execution['run_id']==review['run_id']==RUN
    assert full['logical_sha256']==execution['logical_sha256']==LOGICAL and full['logical_bytes']==190509162
    assert full['wasm_sha256']==execution['wasm_sha256']==BINARY
    assert full['rust_tests_passed']==214 and full['main_query_comparisons']==33 and full['source_query_comparisons']==13 and full['complete_api_comparisons']==2
    assert full['source_index_audit']['original_source_strings_preserved']==627 and full['source_index_audit']['replaced_source_paths']==[]
    assert execution['source_documents_after']==628 and execution['regional_speed_summary_records']==15
    assert execution['underlying_observations']==328 and execution['unique_drifters']==45
    assert execution['summaries_overlap_the_same_cohort'] is True
    assert execution['installed'] is False and execution['new_length_records']==execution['new_width_records']==0
    assert review['status']=='PASS_12_ACTUAL_SCREENSHOTS_INDIVIDUALLY_INSPECTED' and review['independent_visual_review_complete'] is True
    assert browser['status']=='PASS' and not browser['page_errors'] and not browser['missing_assets'] and not browser['original_science_downloads']
    assert review['screenshots']==browser['screenshots'] and len(review['screenshots'])==12
    assert len({r['path'] for r in review['screenshots']})==12
    assert all(r['geometry']['clipped_axes']==[] for r in review['screenshots'])
    assert execution['candidate_artifact']=={**ARTIFACT,'downloaded_locally':False}
    hashes=full['generated_sha256'];assert len(hashes)==18
    assert hashes[delivery.MANIFEST]==FINAL_MANIFEST and hashes[delivery.WASM]==BINARY
    assert sum(p.startswith('almanac/query-parts/') for p in hashes)==12
    assert all(re.fullmatch('[0-9a-f]{64}',h) for h in hashes.values())
    return dict(hashes)


def extract_candidate(archive,hashes,engine_sha,target):
    """Accept only the two upload layouts, exact members and exact bytes."""
    layouts=[({'artifact/'+p:h for p,h in hashes.items()}|{'engine.json':engine_sha},'artifact'),
             (dict(hashes)|{'engine.json':engine_sha},'')]
    with zipfile.ZipFile(archive) as z:names=[i.filename for i in z.infolist() if not i.is_dir()]
    assert len(names)==len(set(names))==len(hashes)+1
    for expected,folder in layouts:
        actual=set(names)
        if actual!=set(expected):
            prefixes={n.split('/',1)[0] for n in names}
            if len(prefixes)!=1:continue
            prefix=next(iter(prefixes))+'/'
            if {n[len(prefix):] for n in names}!=set(expected):continue
        base.extract_verified(archive,expected,target)
        return target/folder
    raise AssertionError('Changed saved candidate packaging or inventory')


def controls():
    assert os.environ.get('GITHUB_ACTIONS')=='true' and os.environ.get('RUNNER_OS')=='Linux'
    assert os.environ.get('OSW_SPEED_INSTALL_V1')=='1' and os.environ.get('GITHUB_EVENT_NAME')=='push'
    assert os.environ.get('GITHUB_REPOSITORY')=='giodl73-repo/OSW' and os.environ.get('GITHUB_REF')=='refs/heads/'+BRANCH
    assert len(os.sched_getaffinity(0))==1 and os.getpriority(os.PRIO_PROCESS,0)>=15
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:assert os.environ.get(key)=='1'
    source=os.environ['GITHUB_SHA'];assert transport.git('rev-parse','HEAD')==base.branch_head()==source
    assert not transport.git('status','--porcelain').strip()
    request=read(REQUEST);verify_request(request);assert file_sha(ROOT/PREFLIGHT)==request['preflight_sha256']
    pref=read(PREFLIGHT)
    for path,pin in pref['input_sha256'].items():assert file_sha(ROOT/path)==pin,path
    phase=read('research/current-gap-delivery-phase.json');assert phase['phase']=='source-review-only-v1' and phase['heavy_work_permitted'] is False and phase['max_heavy_local_jobs']==0 and phase['max_heavy_cloud_jobs']==1
    for path in pref['disabled_requests']:
        doc=read(path);assert doc.get('execute',doc.get('execution_permitted')) is False,path
    hashes=verify_evidence(read(FULL),read(EXECUTION),read(REVIEW),read(BROWSER))
    for name,count in [('main',33),('index',13),('snapshots',2)]:
        parity=read('research/published-current-speed-delivery-'+name+'-parity-v1.json')
        assert parity['status']=='PASS' and len(parity['checks'])==count and parity['initialization_metadata_equal'] is True
        assert all(r['entire_response_equal'] for r in parity['checks']) and parity['wasm_sha256']==BINARY
        if name=='index':assert parity['mismatched_corpus_refused'] is True
        else:assert parity['payload_sha256']==LOGICAL
    result=read('research/published-current-speed-delivery-result-v1.json')
    assert result['browser_verified'] is True and result['installed'] is False and result['source_commit']==SOURCE
    assert str(result['run_id'])==str(RUN) and str(result['run_attempt'])=='1'
    assert result['generated_sha256']==hashes
    assert not (ROOT/PROOF).exists() and not (ROOT/SAVED).exists()
    assert file_sha(ROOT/delivery.MANIFEST)==delivery.PARENT_MANIFEST
    for path,row in pref['parent_files'].items():assert file_sha(ROOT/path)==row['sha256'] and (ROOT/path).stat().st_size==row['bytes'],path
    return source,request,pref,hashes


def artifact():
    run=api(REPO+f'/actions/runs/{RUN}/attempts/1');assert run['status']=='completed' and run['conclusion']=='success' and run['head_sha']==SOURCE and run['head_branch']==BRANCH
    jobs=api(REPO+f'/actions/runs/{RUN}/attempts/1/jobs')['jobs'];assert {j['name'] for j in jobs}=={'select-request','delivery'} and all(j['conclusion']=='success' for j in jobs)
    meta=api(REPO+'/actions/artifacts/'+str(ARTIFACT['id']));assert meta['workflow_run']['id']==RUN and meta['workflow_run']['head_sha']==SOURCE
    assert meta['name']=='published-current-speed-delivery-candidate-v1' and meta['expired'] is False
    assert meta['size_in_bytes']==ARTIFACT['bytes'] and meta['digest']=='sha256:'+ARTIFACT['sha256']
    path=OUT/'candidate.zip'
    with path.open('xb') as stream:subprocess.run(['gh','api',REPO+f"/actions/artifacts/{ARTIFACT['id']}/zip"],stdout=stream,check=True,timeout=600)
    assert path.stat().st_size==ARTIFACT['bytes'] and file_sha(path)==ARTIFACT['sha256']
    return path


def verify_candidate(target,hashes):
    final=json.loads((target/delivery.MANIFEST).read_bytes());assert file_sha(target/delivery.MANIFEST)==FINAL_MANIFEST
    old=read(delivery.MANIFEST)
    for key in old:
        if key not in {'sha256','rustc'}:assert final[key]==old[key],key
    receipt=final[delivery.KEY];assert receipt['source_commit']==SOURCE and receipt['logical_sha256']==LOGICAL and receipt['matching_binary_sha256']==BINARY
    assert receipt['regional_speed_summary_records']==15 and receipt['new_length_records']==receipt['new_width_records']==0
    for path,pin in hashes.items():
        assert file_sha(target/path)==pin,path
        if path!=delivery.MANIFEST:assert final['sha256'][path]==pin,path
    inv=read(INVENTORY)
    for group in ['rust_source_sha256','compile_time_data_sha256']:
        for path,pin in inv[group].items():
            actual=target/path if path in hashes else ROOT/path
            assert file_sha(actual)==pin and final['sha256'][path]==pin,path
    changed,added,contracts=delivery.scopes()
    for path,pin in {**{p:r['candidate_sha256'] for p,r in changed.items()},**added,**contracts}.items():
        assert final['sha256'][path]==pin and file_sha(ROOT/path)==pin,path
    packet=json.loads((target/'almanac/query-data.json').read_bytes())
    assert packet['logical_sha256']==LOGICAL and packet['logical_byte_length']==190509162
    assert len(packet['parts'])==12 and sum(p['byte_length'] for p in packet['parts'])==190509162
    assert {'almanac/'+p['path'] for p in packet['parts']}=={p for p in hashes if p.startswith('almanac/query-parts/')}
    for row in packet['parts']:
        path='almanac/'+row['path'];assert hashes[path]==row['sha256'] and (target/path).stat().st_size==row['byte_length']
    catalog=json.loads((target/'almanac/index-catalog.json').read_bytes())
    assert catalog['source_count']==628 and catalog['bundle_sha256']==read('research/published-current-speed-delivery-index-parity-v1.json')['payload_sha256']
    return final


def install(source,request,pref,hashes):
    main=api(REPO+'/git/ref/heads/main')['object']['sha']
    protected=(set(pref['input_sha256'])|set(pref['parent_files'])|set(pref['disabled_requests'])|{PREFLIGHT})-set(hashes)-{REQUEST,PROOF,SAVED}
    before=objects(source,protected);assert all(before.values())
    restored=OUT/'restored';target=extract_candidate(artifact(),hashes,file_sha(ROOT/FULL),restored)
    assert (restored/'engine.json').read_bytes()==(ROOT/FULL).read_bytes()
    verify_candidate(target,hashes)
    files={};entries=[]
    for path,origin in [(p,target/p) for p in sorted(hashes)]+[(SAVED,target/delivery.MANIFEST)]:
        raw=origin.read_bytes();identity=transport.store(raw);assert identity==oid(raw)
        files[path]={'sha256':sha(raw),'bytes':len(raw),'git_blob_oid':identity};entries.append({'path':path,'mode':'100644','type':'blob','sha':identity});del raw
    proof={'schema':'osw.published-current-speed-installed.v1','status':'EXACT_REVIEWED_ARTIFACT_INSTALLED','installation_transport':'cloud_git_nonforce_single_ref_v1','installation_control_commit':source,'installation_run_id':os.environ['GITHUB_RUN_ID'],'installation_run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],'files':dict(files),'logical_sha256':LOGICAL,'logical_bytes':190509162,'engine_manifest_sha256':FINAL_MANIFEST,'wasm_sha256':BINARY,'candidate_artifact':ARTIFACT,'visual_review_sha256':file_sha(ROOT/REVIEW),'verified_delivery_run_id':RUN,'source_documents':628,'regional_speed_summary_records':15,'underlying_observations':328,'unique_drifters':45,'dimensional_coverage':read('research/current-measurement-coverage-checkpoint-v5.json')['counts'],'new_length_records':0,'new_width_records':0,'browser_verified':True,'visual_review_complete':True,'local_preview_synchronized':False,'main_merged':False,'full_goal_complete':False}
    request.update(execution_permitted=False,working_branch_installation_permitted=False,cloud_git_object_transport_permitted=False,status='DISABLED_IN_EXACT_ARTIFACT_INSTALLATION_COMMIT')
    for path,raw in [(PROOF,encode(proof)),(REQUEST,encode(request))]:
        identity=transport.store(raw);assert identity==oid(raw);files[path]={'sha256':sha(raw),'bytes':len(raw),'git_blob_oid':identity};entries.append({'path':path,'mode':'100644','type':'blob','sha':identity})
    commit=transport.candidate(source,entries,OUT/'installation.index');checked=transport.objects(commit,files)
    assert checked=={p:{'oid':r['git_blob_oid'],'byteSize':r['bytes']} for p,r in files.items()}
    assert transport.objects(commit,protected)==before
    assert base.branch_head()==source and api(REPO+'/git/ref/heads/main')['object']['sha']==main
    transport.publish(commit,BRANCH)
    assert base.branch_head()==commit and objects(commit,files)==checked and api(REPO+'/git/ref/heads/main')['object']['sha']==main
    (OUT/'result.json').write_bytes(encode({'status':'PASS','installed_commit':commit,'control_commit':source,'files':files,'protected_paths_preserved':len(protected),'request_disabled_in_installed_commit':True,'working_branch_installed':True,'main_unchanged':True,'local_preview_synchronized':False,'full_goal_complete':False}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--cloud-install',action='store_true',required=True);parser.add_argument('--preflight-only',action='store_true');args=parser.parse_args()
    source,request,pref,hashes=controls()
    if args.preflight_only:print('Exact saved speed installation preflight passed')
    else:
        OUT.mkdir(parents=True,exist_ok=False)
        try:install(source,request,pref,hashes)
        except Exception as error:
            (OUT/'failure.json').write_bytes(encode({'status':'FAIL','control_commit':source,'error':type(error).__name__+': '+str(error)[:2500],'instruction':'Inspect authoritative branch; ref update may already have succeeded.'}));raise
