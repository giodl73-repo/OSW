"""Read-only installed metadata reconciliation; packet access is cloud-only."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
REQUEST='research/dimoune-2023-width-parent-request-v1.json'
PREFLIGHT='research/dimoune-2023-width-parent-preflight-v1.json'
PREPARED='research/dimoune-2023-section-width-records-prepared-v1.json'
OUT=ROOT/'.pytest_cache/dimoune-2023-width-parent-v1'
LOGICAL='dc671a2af236089e37c02489e0cba6bea52e81298879abf0ea809f8d9552a936'
LENGTH=195248051
ENGINE='f3a5008f7a1f30a386ec27825e46bab337f0aa6857275fb0c3e56a96ce55a967'
MAIN='19148702de6433253dbf412a0a28c0cb4f8e409e'
OWNERS=('current:north-brazil','current:guiana','current:atlantic-north-equatorial-countercurrent',
        'current:atlantic-south-equatorial','current:south-equatorial')

def require(value,message):
    if not value:raise ValueError(message)

def read(path):return json.loads((ROOT/path).read_bytes())

def sha(raw):return hashlib.sha256(raw).hexdigest()

def summarize(bundle,prepared):
    collections=bundle['collections']
    sources=collections['sources'];widths=collections['widths']
    for name,rows in collections.items():
        require(isinstance(rows,list),'Collection must be a list: '+name)
    for name in ('sources','widths','objects','entities'):
        ids=[r['id'] for r in collections[name]]
        require(len(ids)==len(set(ids)),'Duplicate installed IDs: '+name)
    source_matches=[r for r in sources if '10.5194/os-19-251-2023' in json.dumps(r).lower()
                    or 'dimoune' in json.dumps(r).lower()]
    require(source_matches,'Registered publication missing')
    owners={}
    for owner in OWNERS:
        selected={name:[r for r in collections[name] if r['id']==owner] for name in ('objects','entities')}
        require(all(len(v)==1 for v in selected.values()),'Owner missing or ambiguous: '+owner)
        selected['widths']=[r for r in widths if r.get('entity_id')==owner or r.get('current_id')==owner.removeprefix('current:')]
        selected['memberships']=[r for r in collections.get('current_basin_memberships',[])
                                if owner in json.dumps(r)]
        owners[owner]=selected
    existing={r['id']:r for r in widths}
    duplicates=[];candidates=[];unplaced=[]
    for row in prepared['records']:
        match=row['matched_existing_inventory_record_id'];action=row['candidate_action']
        require(row['id'] not in existing,'Prepared ID already installed')
        if action=='duplicate_context_only':
            require(match in existing,'Known duplicate missing from installed packet: '+str(match))
            duplicates.append({'source_row':row['source_flow_label'],'prepared':row,'installed':existing[match]})
        elif action=='scoped_width_admission_candidate':
            require(row['candidate_entity_id'] in OWNERS and row['candidate_entity_id']!='current:south-equatorial',
                    'Candidate needs basin/component owner')
            candidates.append(row)
        else:
            require(action=='taxonomy_review_before_admission' and row['candidate_entity_id'] is None,
                    'Unplaced surface flow must not be assigned to EUC')
            unplaced.append(row)
    require((len(duplicates),len(candidates),len(unplaced))==(5,6,3),'Prepared partitions differ')
    related=[{'collection':name,'record':r} for name,rows in collections.items()
             for r in rows if name not in ('sources','objects','entities')
             and ('dimoune' in json.dumps(r).lower() or '10.5194/os-19-251-2023' in json.dumps(r).lower())]
    surface_identities=[{'collection':name,'record':r} for name in ('objects','entities')
                        for r in collections[name] if 'equatorial surface' in json.dumps(r).lower()]
    return {'collection_counts':{n:len(r) for n,r in sorted(collections.items())},
            'source_matches':source_matches,'owners':owners,'existing_duplicate_rows':duplicates,
            'additional_candidates':candidates,'unplaced_surface_current_rows':unplaced,
            'all_publication_related_records':related,'possible_surface_current_identities':surface_identities,
            'admission_performed':False,'family_evidence_inherited':False,
            'review_required':'Inspect installed source IDs, all publication-related records, and branch ownership before admission.'}

def guard():
    require(os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true'
            and os.environ.get('RUNNER_OS')=='Linux' and os.environ.get('OSW_DIMOUNE_WIDTH_PARENT_V1')=='1',
            'Cloud-only installed metadata audit')
    require(os.environ.get('GITHUB_REF')=='refs/heads/codex/current-measurement-gaps'
            and os.environ.get('GITHUB_REPOSITORY')=='giodl73-repo/OSW'
            and os.environ.get('GITHUB_EVENT_NAME')=='push','Wrong repository/event/ref')
    require(len(os.sched_getaffinity(0))==1 and os.getpriority(os.PRIO_PROCESS,0)>=15,'One low-priority CPU required')
    for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
        require(os.environ.get(key)=='1','Worker limit differs')
    request=read(REQUEST)
    require(request['schema']=='osw.dimoune-2023-width-parent-request.v1'
            and request['execute'] is True and request['cloud_parent_packet_read_permitted'] is True,'Audit disabled')
    for key in ('index_load_permitted','native_wasm_build_permitted','browser_automation_permitted',
                'ocean_field_processing_permitted','provider_download_permitted','installation_permitted',
                'local_bulk_sync_permitted','main_update_permitted'):
        require(request[key] is False,'Unrelated permission enabled: '+key)
    require(request['max_cloud_jobs']==1 and request['max_local_heavy_jobs']==0,'Job bounds differ')
    require(sha((ROOT/PREFLIGHT).read_bytes())==request['preflight_sha256'],'Preflight differs')
    pref=read(PREFLIGHT)
    for path,pin in pref['input_sha256'].items():require(sha((ROOT/path).read_bytes())==pin,'Source differs: '+path)
    require(read('research/current-gap-delivery-phase.json')['heavy_work_permitted'] is False,'Broad phase enabled')
    for path in pref['disabled_requests']:
        value=read(path);require(value.get('execute',value.get('execution_permitted')) is False,'Other request enabled: '+path)
    def git(*args):return subprocess.check_output(['git','-c','core.fsmonitor=false',*args],text=True,timeout=55).strip()
    require(git('rev-parse','HEAD')==os.environ['GITHUB_SHA'] and not git('status','--porcelain'),'Checkout differs')
    require(git('ls-remote','origin','refs/heads/codex/current-measurement-gaps').split()[0]==os.environ['GITHUB_SHA'],'Branch moved')
    require(git('ls-remote','origin','refs/heads/main').split()[0]==MAIN,'Main moved')
    for path,row in pref['installed_files'].items():
        require(git('rev-parse','HEAD:'+path)==row['git_blob_oid']
                and int(git('cat-file','-s',row['git_blob_oid']))==row['bytes'],'Installed identity differs: '+path)
    require(sha((ROOT/'almanac/query-engine.manifest.json').read_bytes())==ENGINE,'Engine differs')

def main():
    guard();OUT.mkdir(parents=True,exist_ok=False)
    import query_packet
    raw=query_packet.read_bundle_bytes(ROOT/'almanac/query-data.json')
    require(len(raw)==LENGTH and sha(raw)==LOGICAL,'Exact complete installed packet required')
    bundle=json.loads(raw);del raw
    result=summarize(bundle,read(PREPARED))
    require(result['collection_counts']['sources']==225 and result['collection_counts']['widths']==179,'Parent counts differ')
    result.update(schema='osw.dimoune-2023-width-parent-audit.v1',status='PASS_EXACT_PARENT_METADATA_RECONCILIATION',
                  source_commit=os.environ['GITHUB_SHA'],run_id=os.environ['GITHUB_RUN_ID'],run_attempt=os.environ['GITHUB_RUN_ATTEMPT'],
                  parent_logical_sha256=LOGICAL,parent_logical_bytes=LENGTH,
                  installed_packet_loaded_locally=False,index_corpus_loaded=False,ocean_fields_processed=False,
                  native_wasm_build=False,installed=False,main_updated=False,full_goal_complete=False)
    encoded=(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
    require(len(encoded)<1500000,'Compact metadata bound exceeded')
    (OUT/'audit.json').write_bytes(encoded)
    print(json.dumps({'status':result['status'],'source_ids':[r['id'] for r in result['source_matches']],
                      'additional_candidates':len(result['additional_candidates']),'metadata_bytes':len(encoded)}))

if __name__=='__main__':main()
