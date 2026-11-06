"""Cloud-only actual source-index registration; no compiler, browser or installation."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
REQUEST='research/chen-indian-sec-index-request-v1.json'
PREFLIGHT='research/chen-indian-sec-index-preflight-v1.json'
OUT=ROOT/'.pytest_cache/chen-indian-sec-index-v1'
WORK=ROOT/'.pytest_cache/chen-indian-sec-index-work-v1'
def read(p):return json.loads((ROOT/p).read_bytes())
def sha(p):
    with (ROOT/p).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def controls():
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
        or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps'):raise ValueError('Cloud index registration only')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:raise ValueError('One CPU and nice15 required')
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(key)!='1':raise ValueError('One worker required')
    r=read(REQUEST)
    if r.get('schema')!='osw.chen-indian-sec-index-request.v1' or r.get('execute') is not True:raise ValueError('Disabled request')
    for key in ['cloud_parent_packet_read_permitted','cloud_index_load_permitted','cloud_index_registration_permitted']:
        if r.get(key) is not True:raise ValueError('Index registration not enabled')
    for key in ['native_build_permitted','wasm_build_permitted','ocean_field_processing_permitted','browser_permitted','installation_permitted','local_bulk_sync_permitted','main_merge_permitted']:
        if r.get(key) is not False:raise ValueError('Unrelated operation enabled')
    if sha(PREFLIGHT)!=r['preflight_sha256']:raise ValueError('Changed freeze')
    pref=read(PREFLIGHT)
    for p,h in pref['input_sha256'].items():
        if sha(p)!=h:raise ValueError('Changed input: '+p)
    for p,row in pref['installed_files'].items():
        if sha(p)!=row['sha256'] or (ROOT/p).stat().st_size!=row['bytes']:raise ValueError('Changed installed parent: '+p)
    for p in pref['disabled_requests']:
        value=read(p)
        if value.get('execute',value.get('execution_permitted')) is not False:raise ValueError('Older request enabled')
    if read('research/current-gap-delivery-phase.json')['heavy_work_permitted'] is not False:raise ValueError('Broad work enabled')
    if subprocess.check_output(['git','-c','core.fsmonitor=false','rev-parse','HEAD']).decode().strip()!=os.environ['GITHUB_SHA'] or subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain']).strip():raise ValueError('Clean exact checkout required')
    return pref

def run():
    pref=controls();OUT.mkdir(exist_ok=False,parents=True);WORK.mkdir(exist_ok=False,parents=True)
    import chen_indian_sec_ridge_index_v1 as index
    from query_packet import read_bundle_bytes
    from check_chen_indian_sec_candidate_v2 import verify_extension
    query=index.query;contract,replay=query.validated_contract()
    raw=read_bundle_bytes(ROOT/'almanac/query-data.json')
    if index.sha(raw)!=query.PARENT or len(raw)!=190686988:raise ValueError('Changed logical parent')
    parent=json.loads(raw);del raw
    collections,manifest=query.prepare(parent['collections'],parent['manifest'],contract,parent_logical_sha256=query.PARENT)
    candidate={**parent,'collections':collections,'manifest':manifest};comparison=verify_extension(parent,candidate,contract)
    raw=index.encode(candidate)
    if index.sha(raw)!='7ad12e7984c1c87e2903f8a2a4567255f9d3a994382f0535ac8d1d2fa7a043fc':raise ValueError('Pre-index candidate differs from verified native candidate')
    del raw,parent
    generated,audit=index.source_index((ROOT/'almanac/index-catalog.json').read_bytes(),(ROOT/'almanac/index-data.json.gz').read_bytes(),(ROOT/'almanac/index-sources.json').read_bytes())
    final=index.attach(candidate,generated,audit)
    expected_manifest={**candidate['manifest'],'input_sha256':{**candidate['manifest']['input_sha256'],**{p:index.sha(b) for p,b in generated.items()}},index.KEY:final['manifest'][index.KEY]}
    if final['collections'] is not candidate['collections'] or final!={**candidate,'manifest':expected_manifest}:raise ValueError('Index attachment altered packet data')
    for p,b in generated.items():(WORK/Path(p).name).write_bytes(b)
    body=index.encode(final);logical_sha=index.sha(body);logical_bytes=len(body);del body
    catalog=json.loads(generated['almanac/index-catalog.json']);registry=json.loads(generated['almanac/index-sources.json'])
    for p,row in pref['installed_files'].items():
        if sha(p)!=row['sha256'] or (ROOT/p).stat().st_size!=row['bytes']:raise ValueError('Installed file changed during registration')
    report={'schema':'osw.chen-indian-sec-index-result.v1','status':'PASS_ACTUAL_SOURCE_INDEX_REGISTRATION_NOT_INSTALLED','source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],'request_sha256':sha(REQUEST),'preflight_sha256':sha(PREFLIGHT),'pre_index_logical_sha256':'7ad12e7984c1c87e2903f8a2a4567255f9d3a994382f0535ac8d1d2fa7a043fc','indexed_candidate_logical_sha256':logical_sha,'indexed_candidate_logical_bytes':logical_bytes,'candidate_comparison':comparison,'source_count':catalog['source_count'],'registry_declared_documents':len(registry['documents']),'source_index_audit':audit,'generated_files':{p:{'sha256':index.sha(b),'bytes':len(b)} for p,b in generated.items()},'added_documents':{p:{'sha256':sha(p),'bytes':(ROOT/p).stat().st_size} for p in index.DOCUMENTS},'measurement_collections_changed_by_index_attachment':False,'installed_parent_files_preserved':21,'index_or_packet_uploaded':False,'native_wasm_built':False,'browser_run':False,'installed_data_changed':False,'local_bulk_sync':False,'full_goal_complete':False}
    (OUT/'result.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps(report),flush=True)

if __name__=='__main__':
    try:run()
    except Exception as error:
        if os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true':
            OUT.mkdir(exist_ok=True,parents=True);(OUT/'failure.json').write_bytes((json.dumps({'status':'FAIL','error':str(error),'source_commit':os.environ.get('GITHUB_SHA')},indent=2)+'\n').encode())
        raise
