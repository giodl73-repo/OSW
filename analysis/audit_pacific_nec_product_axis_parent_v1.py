"""Read-only cloud audit of the exact installed parent before diagnostic delivery."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

from check_chen_indian_sec_ridge_parent_v1 import doi
import pacific_nec_product_axis_records_v1 as contract

ROOT=Path(__file__).resolve().parents[1]
REQUEST='research/pacific-nec-product-axis-parent-request-v1.json'
PREFLIGHT='research/pacific-nec-product-axis-parent-preflight-v1.json'
OUT=ROOT/'.pytest_cache/pacific-nec-product-axis-parent-v1'
LOGICAL='000ec593c4fd1eb597a0a7204824b5c8c8e19cd8e2683080095a46ec50609cb1'
LENGTH=191109635
ENGINE='157ae1b610588ac1e8c58dba524cc4e6a60361be05bba8c1b68ca767fe6366ac'
MAIN='19148702de6433253dbf412a0a28c0cb4f8e409e'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def read(path):return json.loads((ROOT/path).read_bytes())


def require(value,message):
    if not value:raise ValueError(message)


def file_sha(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()


def publications(rows):
    ids=[r.get('id') for r in rows]
    require(all(isinstance(i,str) and i for i in ids) and len(ids)==len(set(ids)),'Unique source IDs required')
    product=[];paper=[];method=[];possible=[]
    for row in rows:
        raw=json.dumps(row,ensure_ascii=False).casefold()
        if 'yearly_336c_0b32_9cd3' in raw:product.append(row)
        if doi(row.get('doi',''))=='10.1029/2019jc015895' or doi(row.get('url',''))=='10.1029/2019jc015895':paper.append(row)
        if row['id']=='source:osw-pacific-nec-connected-product-axis-v1' or 'plans/pacific-nec-connected-core-protocol-v1.md' in raw:method.append(row)
        if 'oscar' in raw and row not in product:possible.append(row)
    selected={'exact_oscar_mirror_dataset':product,'liu_zhou_2020_context':paper,'osw_product_axis_method':method}
    return {'matches':selected,'possible_oscar_aliases':possible,
        'resolutions':{key:{'status':'MISSING' if not value else 'UNIQUE_EXISTING' if len(value)==1 else 'RECONCILIATION_REQUIRED',
                            'source_ids':[r['id'] for r in value]} for key,value in selected.items()}}


def summarize(bundle):
    rows=bundle['collections'];manifest=bundle['manifest']
    require(all(isinstance(v,list) for v in rows.values()),'Collection lists required')
    require(all(name not in rows for name in contract.COLLECTIONS),'Proposed collection already exists')
    require(contract.KEY not in manifest,'Proposed namespace already exists')
    collisions=[{'collection':name,'id':r.get('id')} for name,records in rows.items() for r in records
                if isinstance(r.get('id'),str) and r['id'].startswith(contract.PREFIXES)]
    require(not collisions,'Diagnostic prefix already exists')
    owners={}
    for owner in (contract.OWNER,contract.FAMILY):
        selected={name:[r for r in rows.get(name,[]) if r.get('id')==owner] for name in ('objects','entities')}
        require(len(selected['objects'])==len(selected['entities'])==1,'Exact owner and family identity required')
        selected['linked_records']={name:[r for r in rows.get(name,[]) if r.get('entity_id')==owner
                or r.get('family_entity_id')==owner or r.get('current_id')==owner.removeprefix('current:')]
            for name in ('length_assessments','reference_routes','widths','current_length_series','current_basin_memberships')}
        owners[owner]=selected
    source_rows=rows['sources'];resolved=publications(source_rows)
    counts={name:len(records) for name,records in sorted(rows.items())}
    require(counts['sources']==222 and counts['current_length_series']==2 and counts['current_length_readings']==1687
            and counts['current_length_sensitivities']==120,'Installed parent counts differ')
    return {'collection_counts':counts,'identities':owners,'source_inventory':source_rows,
            'source_resolution':resolved,'proposed_collections_absent':list(contract.COLLECTIONS),
            'proposed_namespace_absent':contract.KEY,'proposed_prefix_collisions':collisions,
            'identity_records_will_remain_unchanged':True,'family_evidence_inherited':False}


def guard():
    require(os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true' and os.environ.get('RUNNER_OS')=='Linux'
        and os.environ.get('OSW_PACIFIC_NEC_AXIS_PARENT_V1')=='1','Cloud-only installed-parent audit')
    require(os.environ.get('GITHUB_REF')=='refs/heads/codex/current-measurement-gaps'
        and os.environ.get('GITHUB_REPOSITORY')=='giodl73-repo/OSW' and os.environ.get('GITHUB_EVENT_NAME')=='push','Wrong repository/event/ref')
    require(len(os.sched_getaffinity(0))==1 and os.getpriority(os.PRIO_PROCESS,0)>=15,'One low-priority CPU required')
    for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):require(os.environ.get(key)=='1','Worker limit differs')
    request=read(REQUEST)
    require(request['schema']=='osw.pacific-nec-product-axis-parent-request.v1' and request['execute'] is True
        and request['cloud_parent_packet_read_permitted'] is True,'Scoped audit disabled')
    for key in ('index_load_permitted','native_wasm_build_permitted','browser_automation_permitted',
        'ocean_field_processing_permitted','provider_download_permitted','installation_permitted','local_bulk_sync_permitted','main_update_permitted'):
        require(request[key] is False,'Unrelated permission enabled: '+key)
    require(request['max_cloud_jobs']==1 and request['max_local_heavy_jobs']==0,'Job bounds differ')
    require(file_sha(ROOT/PREFLIGHT)==request['preflight_sha256'],'Preflight differs')
    pref=read(PREFLIGHT)
    for path,pin in pref['input_sha256'].items():require(file_sha(ROOT/path)==pin,'Source differs: '+path)
    require(read('research/current-gap-delivery-phase.json')['heavy_work_permitted'] is False,'Broad phase enabled')
    for path in pref['disabled_requests']:
        value=read(path);require(value.get('execute',value.get('execution_permitted')) is False,'Other request enabled')
    def git(*args):return subprocess.check_output(['git','-c','core.fsmonitor=false',*args],text=True,timeout=55).strip()
    require(git('rev-parse','HEAD')==os.environ['GITHUB_SHA'] and not git('status','--porcelain'),'Checkout differs')
    require(git('ls-remote','origin','refs/heads/codex/current-measurement-gaps').split()[0]==os.environ['GITHUB_SHA'],'Working branch moved')
    require(git('ls-remote','origin','refs/heads/main').split()[0]==MAIN,'Main moved')
    for path,row in pref['installed_files'].items():
        require(git('rev-parse','HEAD:'+path)==row['git_blob_oid'] and int(git('cat-file','-s',row['git_blob_oid']))==row['bytes'],'Installed file identity differs')
    require(file_sha(ROOT/'almanac/query-engine.manifest.json')==ENGINE,'Installed engine manifest differs')


def main():
    guard();OUT.mkdir(parents=True,exist_ok=False)
    import query_packet
    raw=query_packet.read_bundle_bytes(ROOT/'almanac/query-data.json')
    require(len(raw)==LENGTH and sha(raw)==LOGICAL,'Exact complete parent logical packet required')
    bundle=json.loads(raw);del raw
    result=summarize(bundle)
    result.update(schema='osw.pacific-nec-product-axis-parent-audit.v1',status='PASS_EXACT_COMPLETE_PARENT_READ_ONLY_AUDIT',
        source_commit=os.environ['GITHUB_SHA'],run_id=os.environ['GITHUB_RUN_ID'],run_attempt=os.environ['GITHUB_RUN_ATTEMPT'],
        parent_logical_sha256=LOGICAL,parent_logical_bytes=LENGTH,engine_manifest_sha256=ENGINE,
        installed_packet_loaded_locally=False,index_corpus_loaded=False,ocean_fields_processed=False,
        native_wasm_build=False,installed=False,main_updated=False,full_goal_complete=False)
    encoded=(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
    require(len(encoded)<2000000,'Parent audit exceeds compact metadata bound')
    (OUT/'audit.json').write_bytes(encoded)
    print(json.dumps({'status':result['status'],'source_resolutions':result['source_resolution']['resolutions'],
                      'sources':result['collection_counts']['sources'],'metadata_bytes':len(encoded)}))


if __name__=='__main__':
    try:main()
    except Exception as error:
        if os.environ.get('GITHUB_ACTIONS')=='true':
            OUT.mkdir(parents=True,exist_ok=True)
            (OUT/'failure.json').write_text(json.dumps({'status':'FAIL','error_type':type(error).__name__,'message':str(error)[:2000],'installed':False})+'\n')
        raise
