"""Read-only installed metadata audit before basin-qualified current identity admission."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
REQUEST='research/equatorial-basin-parent-request-v1.json'
PREFLIGHT='research/equatorial-basin-parent-preflight-v1.json'
WORKFLOW='.github/workflows/equatorial-basin-parent-cloud-v1.yml'
OUT=ROOT/'.pytest_cache/equatorial-basin-parent-v1'
FACTS='research/equatorial-basin-identity-source-review-v1.json'
ENGINE='c13a6295deac9c7a1897fc7539dc84099d6a0a6af30aa40499f40c660d2d431c'
LOGICAL='bef41b14f78c84a9b7b2d135dd900d67504618bfadaec4b3397be6982ae33ae8'
LENGTH=190601113
FORBIDDEN=['index_load_permitted','native_wasm_build_permitted','browser_permitted','ocean_field_processing_permitted',
           'working_branch_installation_permitted','local_bulk_sync_permitted','main_merge_permitted']

def read(p):return json.loads((ROOT/p).read_bytes())
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def label(value):return re.sub('[^a-z0-9]','',str(value).casefold())
def source_url(value):
    p=urlsplit(str(value).strip())
    return (p.hostname or '').lower().removeprefix('www.'),p.path.rstrip('/').removesuffix('.html')

def select(collections,proposals):
    if len(proposals)!=5 or len({p['proposed_id'] for p in proposals})!=5:raise ValueError('Five unique frozen proposals required')
    for name in ['entities','objects','names','sources']:
        rows=collections[name];ids=[r.get('id') for r in rows]
        if any(not isinstance(i,str) or not i for i in ids) or len(ids)!=len(set(ids)):raise ValueError('Unique IDs required: '+name)
    selected={'proposals':{},'families':{},'existing_glossary_sources':[]}
    for proposal in proposals:
        short=proposal['proposed_id'];owner='current:'+short;parent='current:'+proposal['parent_current_id']
        exact={name:[r for r in collections[name] if r['id']==owner] for name in ['entities','objects']}
        aliases=[r for r in collections['names'] if r.get('entity_id')==owner or label(r.get('label',''))==label(proposal['proposed_label'])]
        collisions={name:[r for r in collections[name] if r['id']!=owner and label(r.get('label',''))==label(proposal['proposed_label'])] for name in ['entities','objects']}
        if any(collisions.values()) or any(r.get('entity_id')!=owner for r in aliases):status='RECONCILIATION_REQUIRED'
        elif all(len(exact[n])==1 for n in exact):status='EXACT_EXISTING_IDENTITY'
        elif any(exact.values()) or aliases:status='PARTIAL_EXISTING_RECORDS'
        else:status='MISSING_EXACT_IDENTITY'
        linked={}
        proposal_rows={}
        for name,rows in collections.items():
            hits=[r for r in rows if r.get('current_id')==short or r.get('entity_id')==owner]
            if hits:linked[name]={'count':len(hits),'ids':[r.get('id') for r in hits]}
            matches=[r for r in rows if r.get('proposal_id')==short or r.get('proposed_id')==short]
            if matches:proposal_rows[name]=matches
        if status=='MISSING_EXACT_IDENTITY' and linked:status='MISSING_IDENTITY_WITH_LINKED_RECORDS'
        selected['proposals'][short]={'status':status,'proposal':proposal,'exact_records':exact,'names':aliases,
            'label_collisions':collisions,'linked_inventory':linked,'existing_proposal_rows':proposal_rows}
        if parent not in selected['families']:
            entry={name:[r for r in collections[name] if r['id']==parent] for name in ['entities','objects']}
            if any(len(v)!=1 for v in entry.values()):raise ValueError('One exact parent entity/object required: '+parent)
            entry['names']=[r for r in collections['names'] if r.get('entity_id')==parent]
            entry['widths']=[r for r in collections.get('widths',[]) if r.get('current_id')==proposal['parent_current_id']]
            selected['families'][parent]=entry
    for r in collections['sources']:
        if source_url(r.get('url',''))==('tidesandcurrents.noaa.gov','/glossary'):selected['existing_glossary_sources'].append(r)
    selected['identity_resolution_counts']={state:sum(p['status']==state for p in selected['proposals'].values()) for state in sorted({p['status'] for p in selected['proposals'].values()})}
    return selected

def controls():
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true'
        or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
        or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps'
        or os.environ.get('GITHUB_EVENT_NAME')!='push'):
        raise ValueError('Exact cloud audit required before installed-packet access')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:raise ValueError('One CPU and nice15 required')
    for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(k)!='1':raise ValueError('Single worker required: '+k)
    request=read(REQUEST)
    for key,value in {'schema':'osw.equatorial-basin-parent-request.v1','workflow':WORKFLOW,'execute':True,
                      'cloud_parent_packet_read_permitted':True,'max_cloud_jobs':1,'max_heavy_local_jobs':0}.items():
        if type(request.get(key)) is not type(value) or request[key]!=value:raise ValueError('Disabled/changed request: '+key)
    if any(request.get(k) is not False for k in FORBIDDEN):raise ValueError('Unrelated permission enabled')
    phase=read('research/current-gap-delivery-phase.json')
    if phase['phase']!='source-review-only-v1' or phase['heavy_work_permitted'] is not False:raise ValueError('Source-field processing must stay disabled')
    if sha((ROOT/PREFLIGHT).read_bytes())!=request['preflight_sha256']:raise ValueError('Changed preflight')
    pref=read(PREFLIGHT)
    for p,pin in pref['input_sha256'].items():
        if sha((ROOT/p).read_bytes())!=pin:raise ValueError('Changed source: '+p)
    for p,row in pref['installed_files'].items():
        with (ROOT/p).open('rb') as stream:actual=hashlib.file_digest(stream,'sha256').hexdigest()
        if actual!=row['sha256'] or (ROOT/p).stat().st_size!=row['bytes']:raise ValueError('Changed installed file: '+p)
    for p in pref['disabled_requests']:
        r=read(p)
        if r.get('execute',r.get('execution_permitted')) is not False:raise ValueError('Older request enabled: '+p)
    head=subprocess.check_output(['git','-c','core.fsmonitor=false','rev-parse','HEAD']).decode().strip()
    remote=json.loads(subprocess.check_output(['gh','api','repos/giodl73-repo/OSW/git/ref/heads/codex/current-measurement-gaps']))['object']['sha']
    if head!=remote or head!=os.environ['GITHUB_SHA']:raise ValueError('Current source checkout required')
    if subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain']).strip():raise ValueError('Clean checkout required')
    return head

def audit():
    head=controls()
    from query_packet import descriptors,read_bundle_bytes
    manifest_raw=(ROOT/'almanac/query-engine.manifest.json').read_bytes()
    if sha(manifest_raw)!=ENGINE:raise ValueError('Exact AzCC-inclusive installed engine required')
    manifest=json.loads(manifest_raw);packet_raw=(ROOT/'almanac/query-data.json').read_bytes();packet=json.loads(packet_raw)
    parts=descriptors(packet)
    if (manifest['sha256']['almanac/query-data.json']!=sha(packet_raw)
        or packet['logical_sha256']!=LOGICAL or packet['logical_byte_length']!=LENGTH):raise ValueError('Installed descriptor differs')
    if any(manifest['sha256'].get('almanac/'+p['path'])!=p['sha256'] for p in parts):raise ValueError('Part receipt differs')
    raw=read_bundle_bytes(ROOT/'almanac/query-data.json')
    if sha(raw)!=LOGICAL or len(raw)!=LENGTH:raise ValueError('Installed logical bytes differ')
    bundle=json.loads(raw);del raw
    collections=bundle['collections']
    for name,count in [('reference_routes',83),('widths',178),('sources',217)]:
        if len(collections[name])!=count:raise ValueError('Installed inventory differs: '+name)
    if sum(r.get('type')=='named_current' for r in collections['entities'])!=106:raise ValueError('Installed current identity count differs')
    selected=select(collections,read(FACTS)['proposals'])
    selected['manifest_namespaces']=sorted(bundle['manifest'])
    data=encoded(selected)
    if len(data)>500000:raise ValueError('Bounded metadata cap exceeded')
    if subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain']).strip():raise ValueError('Audit changed tracked files')
    result={'schema':'osw.equatorial-basin-parent-audit.v1','status':'PASS_READ_ONLY','source_commit':head,
        'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],
        'engine_manifest_sha256':ENGINE,'logical_sha256':LOGICAL,'logical_byte_length':LENGTH,
        'packet_parts_verified':len(parts),'collection_counts':{k:len(v) for k,v in collections.items()},
        'identity_resolution_counts':selected['identity_resolution_counts'],
        'selected_records_sha256':sha(data),'selected_records_bytes':len(data),
        'packet_loaded_only_in_cloud':True,'index_loaded':False,'native_wasm_built':False,
        'scientific_data_changed':False,'browser_run':False,'working_branch_installed':False,'full_goal_complete':False}
    OUT.mkdir(parents=True,exist_ok=False)
    (OUT/'selected-records.json').write_bytes(data);(OUT/'result.json').write_bytes(encoded(result));print(json.dumps(result))

if __name__=='__main__':
    try:audit()
    except Exception as error:
        if os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true':
            OUT.mkdir(parents=True,exist_ok=True)
            (OUT/'failure.json').write_bytes(encoded({'status':'FAIL','error':str(error),'source_commit':os.environ.get('GITHUB_SHA')}))
        raise
