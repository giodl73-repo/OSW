"""Install the reviewed current engine and map data without rebuilding.

Requires the frozen completed browser evidence and individual PNG review.
No scientific processing, builds, browser run, local bulk sync or main update.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
from collections import Counter

import install_current_core_dimensions_saved_v1 as shared
import verified_artifact_git_transport_v1 as transport
import current_query_map_focus_presentation_v1 as presentation

ROOT=Path(__file__).resolve().parents[1]
BRANCH='codex/current-measurement-gaps'
REPO='repos/giodl73-repo/OSW'
MAIN='19148702de6433253dbf412a0a28c0cb4f8e409e'
REQUEST='research/current-utf8-validation-installation-request-v1.json'
PREFLIGHT='research/current-utf8-validation-installation-preflight-v1.json'
CONTRACT='research/current-utf8-validation-installation-contract-v1.json'
PROOF='research/current-utf8-validation-installed-v1.json'
SAVED='research/current-utf8-validation-installation-saved-engine-manifest-v1.json'
ENGINE='research/current-utf8-validation-delivery-run-v1/'
BROWSER='research/current-utf8-validation-browser-run-v1/'
VISUAL='research/current-utf8-validation-complete-visual-review-v1.json'
OUT=ROOT/'.pytest_cache/current-utf8-validation-installation-v1'
LOGICAL='09b882c97c922a0643880885a6165388bf41b19903e72a6d9ca44437da1ed41e'
LOGICAL_BYTES=195361434
require=shared.require
sha=shared.sha
encode=shared.encode
file_sha=shared.file_sha
head=shared.head
api=shared.api
leaves=shared.leaves
read=lambda p:json.loads((ROOT/p).read_bytes())


def evidence(frozen):
    engine=read(ENGINE+'result.json')
    require(engine['source_commit']=='fcca8e283ef9d0e868ada629b772aad93980a5c6'
        and engine['run_id']=='41114274466' and engine['run_attempt']=='1'
        and engine['status']=='PASS_COMPLETE_NATIVE_WASM_CANDIDATE_BROWSER_PENDING'
        and engine['rust_tests_passed']==322,'Strict-encoding engine custody differs')
    require(engine['logical_sha256']==LOGICAL and engine['logical_bytes']==LOGICAL_BYTES,'Wrong scientific data')
    require(engine['packet_comparison']=={'historical_collections_checked':78,'existing_measurement_rows_changed':0,
        'reference_routes_added':2,'sources_added':2,'owner_objects_updated':1,'planning_decisions_updated':1},'Wrong scientific delta')
    files=copy.deepcopy(engine['generated_files']);require(len(files)==18,'Exact18 saved files required')
    original_raw=(ROOT/(ENGINE+'engine-manifest.json')).read_bytes()
    require(files['almanac/query-engine.manifest.json']=={'sha256':sha(original_raw),'bytes':len(original_raw)},'Native manifest receipt differs')
    require(sha(original_raw)==presentation.PARENT==frozen['original_engine_manifest_sha256'],'Wrong native manifest')
    manifest_raw=(ROOT/presentation.FILE).read_bytes()
    updates={p:file_sha(ROOT/p) for p in sorted(presentation.PATHS)}
    require(json.loads(manifest_raw)==presentation.overlay(original_raw,updates),'Unreviewed presentation change')
    files['almanac/query-engine.manifest.json']={'sha256':sha(manifest_raw),'bytes':len(manifest_raw)}
    require(engine['wasm_sha256']==files['almanac/query-engine.wasm']['sha256']==frozen['wasm_sha256'],'Wrong binary')
    require(sha(manifest_raw)==frozen['engine_manifest_sha256'],'Wrong manifest')
    for mode,count in [('main',392),('index',122)]:
        parity=read(ENGINE+'compare-'+mode+'.json')
        require(parity['status']=='PASS' and len(parity['checks'])==count and parity['complete_initialization_equal'] is True
            and parity['wasm_sha256']==engine['wasm_sha256'],'Incomplete native/WASM comparison')
        require(all(r['entire_response_equal'] is True and r['comparison']=='exact original JSON bytes' for r in parity['checks']),'Partial comparison')
    result=read(BROWSER+'result.json');observed=read(BROWSER+'browser.json');review=read(VISUAL)
    require(result['source_commit']==frozen['browser']['source_commit'] and result['run_id']==str(frozen['browser']['run_id'])
        and result['run_attempt']=='1' and result['status']=='PASS_BROWSER_OBSERVATION_VISUAL_REVIEW_PENDING','Wrong browser result')
    require(result['saved_engine_run']==41114274466 and result['saved_engine_source']==engine['source_commit']
        and result['saved_artifact']==frozen['engine']['artifact'] and result['logical_sha256']==LOGICAL
        and result['wasm_sha256']==engine['wasm_sha256'] and result['engine_manifest_sha256']==sha(manifest_raw)
        and result['original_engine_manifest_sha256']==presentation.PARENT and result['client_transport_updates']==sorted(presentation.PATHS)
        and result['native_or_wasm_rebuild'] is False and result['installed'] is False,'Browser changed saved engine')
    require(result['screenshots']==30 and result['browser_checks']==21 and len(observed['checks'])==21,'Incomplete browser checks')
    require(Counter(r['width'] for r in observed['checks'])=={1100:9,320:12},'Both viewport check groups required')
    for width in [1100,320]:
        positives=[r['case'] for r in observed['checks'] if r['width']==width and 'expected_error' not in r]
        require(len(positives)==len(set(positives))==9,'Missing or duplicate positive browser group')
    require(observed['viewports']==[1100,320] and observed['one_page_and_renderer'] is True
        and observed['status']==result['status'] and not observed['page_errors'] and not observed['missing_assets']
        and not observed['original_science_downloads'],'Browser errors or unrelated source downloads')
    screenshots=observed['screenshots']
    require(len(screenshots)==len({r['path'] for r in screenshots})==30,'Exact30 unique PNGs required')
    require(review['status']=='PASS_ALL_30_ACTUAL_IMAGES_INDIVIDUALLY_INSPECTED'
        and review['source_commit']==result['source_commit'] and review['run_id']==int(result['run_id'])
        and review['artifact']==frozen['browser']['artifact'] and review['screenshots']==screenshots
        and review['actual_images_individually_inspected']==30 and review['blocking_issues']==[]
        and review['installed'] is False,'Individual visual acceptance missing')
    images=review['image_reviews']
    require(len(images)==30 and [{k:r[k] for k in ['path','bytes','sha256']} for r in images]==screenshots
        and all(r['actually_viewed'] is True and isinstance(r['observation'],str) and r['observation'].strip() for r in images),
        'Per-image visual observations missing')
    require(len(observed['legibility'])==6 and Counter(r['kind'] for r in observed['legibility'])=={'atlas-preview':4,'full-route-card':2}
        and all(r['minimum_text_px']>=11 for r in observed['legibility']),'Unreadable atlas previews or full route cards')
    loads=observed['atlas_load_observations']
    require(len(loads)==2 and loads[0]['cold_browser_context'] is True and all(r['status']['phase']=='ready'
        and r['status']['settled'] is True and [p['phase'] for p in r['status']['completed_phases']]==['load','atlas']
        and all(0<=p['elapsed_ms']<=90000 for p in r['status']['completed_phases']) for r in loads),'Cold atlas budget not proven')
    negatives=[r for r in observed['checks'] if 'expected_error' in r]
    require(len(negatives)==len({r['case'] for r in negatives})==3 and sorted(r['expected_error'] for r in negatives)==['Invalid bundle JSON','Invalid bundle JSON','Unsupported bundle schema'],
        'All three actual malformed-byte refusals required')
    return files,manifest_raw


def controls():
    # Refuse before reading any installed payload or making network requests.
    require(os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true' and os.environ.get('RUNNER_OS')=='Linux'
        and os.environ.get('OSW_CURRENT_UTF8_VALIDATION_INSTALL_V1')=='1','Scoped cloud installation only')
    require(os.environ.get('GITHUB_EVENT_NAME')=='push' and os.environ.get('GITHUB_REPOSITORY')=='giodl73-repo/OSW'
        and os.environ.get('GITHUB_REF')=='refs/heads/'+BRANCH,'Wrong event or branch')
    require(len(os.sched_getaffinity(0))==1 and os.getpriority(os.PRIO_PROCESS,0)>=15,'One low-priority CPU required')
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        require(os.environ.get(key)=='1','One worker required')
    source=os.environ['GITHUB_SHA']
    require(transport.git('rev-parse','HEAD')==head(BRANCH)==source and head('main')==MAIN
        and not transport.git('status','--porcelain'),'Exact clean parent and frozen main required')
    request=read(REQUEST)
    require(request['schema']=='osw.current-utf8-validation-installation-request.v1'
        and request['workflow']=='.github/workflows/install-current-utf8-validation-saved-v1.yml'
        and request['execution_permitted'] is True and request['working_branch_installation_permitted'] is True
        and request['cloud_git_object_transport_permitted'] is True and request['max_cloud_jobs']==1
        and request['max_heavy_local_jobs']==0,'Installation request disabled or changed')
    for key in ['native_build_permitted','wasm_build_permitted','browser_automation_permitted','scientific_source_processing_permitted',
                'source_field_processing_permitted','local_bulk_sync_permitted','main_merge_permitted']:
        require(request.get(key) is False,'Unrelated operation enabled: '+key)
    require(file_sha(ROOT/PREFLIGHT)==request['preflight_sha256'],'Preflight changed')
    pref=read(PREFLIGHT)
    for path,pin in pref['input_sha256'].items():require(file_sha(ROOT/path)==pin,'Frozen input differs: '+path)
    for path,row in pref['parent_files'].items():
        require((ROOT/path).stat().st_size==row['bytes'] and file_sha(ROOT/path)==row['sha256'],'Installed parent differs')
    for path in pref['disabled_requests']:
        old=read(path);require(old.get('execute',old.get('execution_permitted')) is False,'Another request enabled')
    phase=read('research/current-gap-delivery-phase.json')
    require(phase['heavy_work_permitted'] is False and phase['max_heavy_local_jobs']==0
        and phase['max_heavy_cloud_jobs']==1,'Broad phase enabled')
    require(not (ROOT/PROOF).exists() and not (ROOT/SAVED).exists(),'Already installed')
    frozen=read(CONTRACT)
    require(frozen['schema']=='osw.current-utf8-validation-installation-contract.v1','Wrong frozen contract')
    files,raw=evidence(frozen)
    for name,expected_source,expected_run in [('engine','fcca8e283ef9d0e868ada629b772aad93980a5c6',41114274466),
        ('browser',frozen['browser']['source_commit'],frozen['browser']['run_id'])]:
        record=frozen[name];require(record['source_commit']==expected_source and record['run_id']==expected_run,'Wrong run descriptor')
        run=api(REPO+f'/actions/runs/{expected_run}/attempts/1')
        require(run['status']=='completed' and run['conclusion']=='success' and run['head_sha']==expected_source,'Run custody differs')
        desc=record['artifact'];artifact=api(REPO+'/actions/artifacts/'+str(desc['id']))
        require(artifact['workflow_run']['id']==expected_run and artifact['workflow_run']['head_sha']==expected_source
            and artifact['expired'] is False and artifact['size_in_bytes']==desc['bytes']
            and artifact['digest']=='sha256:'+desc['sha256'],'Artifact custody differs')
    return source,request,pref,frozen,files,raw


def verify_extracted(target,files,manifest_raw,pref):
    manifest=json.loads(manifest_raw)
    for path,row in files.items():
        require((target/path).stat().st_size==row['bytes'] and file_sha(target/path)==row['sha256'],'Saved file differs: '+path)
    inventory=read(ENGINE+'compile-inventory.json')
    for group,count in [('rust_source_sha256',121),('compile_time_data_sha256',174)]:
        require(len(inventory[group])==count,'Wrong compiler closure')
        for path,pin in inventory[group].items():
            require(manifest['sha256'][path]==pin and file_sha((target if path in files else ROOT)/path)==pin,'Compiled input differs')
    proof=read(ENGINE+'dependency-proof.json')
    require(proof['production_dependency_count']==287 and len(proof['production_dependencies'])==287
        and proof['test_only_fixtures_compiled']==0 and proof['compiled_catalog_dependency_verified'] is True,'Wrong dependency proof')
    active=set(proof['production_dependencies'])|{p for p in manifest['sha256'] if p.startswith('almanac/') and Path(p).suffix in ['.js','.css','.html']}
    active|=set(pref['presentation_sha256']);require(len(pref['presentation_sha256'])==12,'Incomplete current presentation binding')
    for path in active:require(file_sha((target if path in files else ROOT)/path)==manifest['sha256'][path],'Active input differs: '+path)
    marker=manifest['atlantic_nsec_reference_engine_v1']
    require(marker['logical_sha256']==LOGICAL and marker['source_documents_after']==685
        and marker['source_collection_rows_after']==233 and marker['reference_route_records_after']==85
        and marker['reference_route_owners_after']==77 and marker['whole_current_dimensions_added']==0
        and marker['annual_ranges_added']==0 and marker['new_independent_observations']==0,'Scientific scope differs')
    catalog=json.loads((target/'almanac/index-catalog.json').read_bytes())
    require(catalog['source_count']==685 and catalog['bundle_sha256']==read(ENGINE+'compare-index.json')['payload_sha256'],'Wrong index')
    descriptor=json.loads((target/'almanac/query-data.json').read_bytes())
    require(descriptor['logical_sha256']==LOGICAL and descriptor['logical_byte_length']==LOGICAL_BYTES,'Wrong descriptor')
    parts=descriptor['parts'];require(len(parts)==12 and [p['index'] for p in parts]==list(range(12)),'Wrong part inventory')
    require({'almanac/'+p['path'] for p in parts}=={p for p in files if p.startswith('almanac/query-parts/')},'Unexpected parts')
    logical=hashlib.sha256();total=0
    for row in parts:
        path=target/'almanac'/row['path']
        require(path.stat().st_size==row['byte_length'] and file_sha(path)==row['sha256'],'Wrong packet part')
        with path.open('rb') as stream:
            for block in iter(lambda:stream.read(1048576),b''):logical.update(block);total+=len(block)
    require(total==LOGICAL_BYTES and logical.hexdigest()==LOGICAL,'Wrong complete logical bytes')


def install():
    source,request,pref,frozen,files,manifest_raw=controls()
    OUT.mkdir(parents=True,exist_ok=False);archive=OUT/'engine.zip';desc=frozen['engine']['artifact']
    with archive.open('xb') as output:
        subprocess.run(['gh','api',REPO+'/actions/artifacts/'+str(desc['id'])+'/zip'],stdout=output,check=True,timeout=600)
    require(archive.stat().st_size==desc['bytes'] and file_sha(archive)==desc['sha256'],'Wrong saved engine archive')
    target=OUT/'unpacked';shared.extract_exact(archive,target,read(ENGINE+'result.json')['generated_files'])
    (target/'almanac/query-engine.manifest.json').write_bytes(manifest_raw)
    verify_extracted(target,files,manifest_raw,pref)
    before=leaves(source);entries=[];installed={}
    def add(path,raw):
        oid=transport.store(raw)
        require(oid==hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),'Wrong Git blob')
        entries.append({'path':path,'mode':'100644','type':'blob','sha':oid})
        installed[path]={'sha256':sha(raw),'bytes':len(raw),'git_blob_oid':oid}
    for path in files:add(path,(target/path).read_bytes())
    add(SAVED,manifest_raw)
    proof={'schema':'osw.current-utf8-validation-installed.v1','status':'VERIFIED_ARTIFACTS_READY_FOR_ATOMIC_WORKING_BRANCH_INSTALLATION',
        'installation_control_commit':source,'engine':frozen['engine'],'browser':frozen['browser'],
        'logical_sha256':LOGICAL,'wasm_sha256':frozen['wasm_sha256'],'manifest_sha256':sha(manifest_raw),
        'original_engine_manifest_sha256':presentation.PARENT,'presentation_only_updates':sorted(presentation.PATHS),
        'files':dict(installed),'source_index_documents':685,'publication_source_collection_rows':233,
        'reference_routes':85,'reference_route_owners':77,'scoped_width_records':190,
        'owners_with_admitted_scoped_width_records':93,'owners_with_broader_dashboard_width_capability':94,
        'reference_routes_added':2,'reported_whole_current_lengths_added':0,'width_records_added':0,
        'width_samples_added':0,'annual_ranges_added':0,'physical_state_joins_added':0,'independent_observations_added':0,
        'native_or_wasm_rebuild':False,'main_updated':False,'local_bulk_sync':False,'full_goal_complete':False}
    add(PROOF,encode(proof))
    add(REQUEST,encode(dict(request,execution_permitted=False,working_branch_installation_permitted=False,
        cloud_git_object_transport_permitted=False,completed_by_run=os.environ['GITHUB_RUN_ID'],completed_by_attempt=os.environ['GITHUB_RUN_ATTEMPT'])))
    require(len(entries)==21,'Wrong installation scope')
    candidate=transport.candidate(source,entries,str(OUT/'git-index'));after=leaves(candidate);selected=set(installed)
    require(set(after)==set(before)|selected,'Unexpected tree paths')
    for path,row in before.items():
        if path not in selected:require(after[path]==row,'Protected tree changed: '+path)
    for path,row in installed.items():
        require(after[path]=={'mode':'100644','type':'blob','sha':row['git_blob_oid'],'bytes':row['bytes']},'Wrong selected leaf')
    require(head(BRANCH)==source and head('main')==MAIN,'Remote parent moved')
    transport.publish(candidate,BRANCH)
    require(head(BRANCH)==candidate and head('main')==MAIN,'Published ref differs')
    result=dict(proof,status='PASS_INSTALLED_REVIEWED_WORKING_BRANCH_ARTIFACTS',installed_commit=candidate,files=installed,
        protected_paths_preserved=len(set(before)-selected),installed=True,request_disabled=True,main_unchanged=True)
    (OUT/'result.json').write_bytes(encode(result))
    print(json.dumps({k:result[k] for k in ['status','installed_commit','main_unchanged','full_goal_complete']}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cloud-install',action='store_true',required=True)
    parser.add_argument('--preflight-only',action='store_true');args=parser.parse_args()
    try:
        if args.preflight_only:controls();print('PASS_EXACT_PARENT_EVIDENCE_AND_CUSTODY_PREFLIGHT')
        else:install()
    except Exception as error:
        if os.environ.get('GITHUB_ACTIONS')=='true':
            OUT.mkdir(parents=True,exist_ok=True)
            (OUT/'failure.json').write_bytes(encode({'status':'FAIL','error_type':type(error).__name__,'message':str(error)[:1200],
                'installed':False,'main_updated':False}))
        raise
