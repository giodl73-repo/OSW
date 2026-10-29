"""Read-only cloud audit of Indian SEC and family records before regional model-grid query delivery."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit,unquote

ROOT=Path(__file__).resolve().parents[1]
REQUEST='research/chen-indian-sec-ridge-length-parent-request-v1.json'
PREFLIGHT='research/chen-indian-sec-ridge-length-parent-preflight-v1.json'
WORKFLOW='.github/workflows/chen-indian-sec-ridge-length-parent-cloud-v1.yml'
OUT=ROOT/'.pytest_cache/chen-indian-sec-ridge-length-parent-v1'
OWNER='current:indian-south-equatorial'
ENGINE='0f5a5b1a32f0b1602687ed2ecb6bdda7e110a26ad07947f4fd7a3cf7f7b9572d'
LOGICAL='3e8dad713d264d5ae4bd4538a503a695174444f2e190803da445b72e62229a38'
LENGTH=190686988
FORBIDDEN=['index_load_permitted','native_wasm_build_permitted','browser_permitted','ocean_field_processing_permitted',
           'working_branch_installation_permitted','local_bulk_sync_permitted','main_merge_permitted']
PAPERS={
    'chen_indian_sec_2022':{'kind':'publication','doi':'10.1029/2022jc018969',
        'title':'Seasonal Structure and Interannual Variation of the South Equatorial Current in the Indian Ocean',
        'urls':['https://doi.org/10.1029/2022JC018969','https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2022JC018969','https://agupubs.onlinelibrary.wiley.com/doi/epdf/10.1029/2022JC018969']},
    'chen_indian_sec_model_deposit':{'kind':'dataset','doi':None,
        'title':'HYCOM and LOM data in the South Indan Ocean',
        'urls':['https://data.scsio.ac.cn/metaData-detail/1567926827663917056','http://data.scsio.ac.cn/metaData-detail/1567926827663917056','https://data.scsio.ac.cn/api/web/v1/metadata/1567926827663917056?lang=ENG']}}
PREFIXES=('model_core_length:indian-sec:chen-2022:', 'model_core_series:indian-sec:chen-2022:', 'model_core_sensitivity:indian-sec:chen-2022:')

def read(p):return json.loads((ROOT/p).read_bytes())
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def title(value):return re.sub('[^a-z0-9]','',str(value).casefold())
def url(value):
    parsed=urlsplit(str(value).strip());return (parsed.hostname or '').lower(),parsed.path.rstrip('/').lower()
def doi(value):
    value=unquote(str(value).strip()).lower()
    if value.startswith(('http://','https://')):
        parsed=urlsplit(value);value=parsed.path
        if parsed.hostname in ['doi.org','dx.doi.org']:value=value.lstrip('/')
        else:
            found=re.search(r'/doi/(?:full/|abs/|epdf/|pdf/)?(10\.[0-9]{4,9}/.+)$',value)
            return found.group(1).rstrip('/') if found else ''
    return value.removeprefix('doi:').strip().rstrip('/')

def publications(rows):
    ids=[r.get('id') for r in rows]
    if any(not isinstance(i,str) or not i for i in ids) or len(ids)!=len(set(ids)):
        raise ValueError('Unique nonempty source IDs required')
    selected,resolutions={},{}
    for key,paper in PAPERS.items():
        matches=[];conflicts=[]
        for row in rows:
            expected=paper['doi']
            match=((bool(expected) and (doi(row.get('doi',''))==expected or doi(row.get('url',''))==expected))
                or (bool(row.get('url')) and url(row['url']) in {url(u) for u in paper['urls']})
                or any(title(row.get(k,''))==title(paper['title']) for k in ['title','label']))
            if match:
                matches.append(row)
                if (expected and row.get('doi') and doi(row['doi'])!=expected) or (row.get('kind') and row['kind']!=paper['kind']):
                    conflicts.append(row['id'])
        status='CONFLICTING_METADATA' if conflicts else 'MISSING' if not matches else 'UNIQUE_EXISTING' if len(matches)==1 else 'RECONCILIATION_REQUIRED'
        selected[key]=matches
        resolutions[key]={'status':status,'matching_source_ids':[r['id'] for r in matches],'conflicting_source_ids':conflicts}
    return selected,resolutions


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
    for key,value in {'schema':'osw.chen-indian-sec-ridge-length-parent-request.v1','workflow':WORKFLOW,'execute':True,
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

def select_records(bundle):
    collections=bundle['collections']
    for name,count in [('reference_routes',83),('widths',179),('sources',219),('current_basin_memberships',5)]:
        if len(collections[name])!=count:raise ValueError('Installed inventory differs: '+name)
    selected={'identities':{}}
    for owner in [OWNER,'current:south-equatorial']:
        record={}
        for key,collection,field in [('object','objects','id'),('entity','entities','id'),('planning_decision','route_decisions','entity_id')]:
            rows=[r for r in collections[collection] if r.get(field)==owner]
            if len(rows)!=1:raise ValueError('One installed identity required: '+owner+'/'+key)
            record[key]=rows[0]
        def belongs(row):
            return row.get('current_id')==owner.removeprefix('current:') or row.get('entity_id')==owner or row.get('family_entity_id')==owner
        for name in ['widths','reference_routes','length_assessments','current_basin_memberships']:
            record[name]=[r for r in collections[name] if belongs(r)]
        record['owner_sources']=[r for r in collections['sources'] if r['id'] in record['object']['source_ids']]
        record['linked_records']={name:matched for name,rows in collections.items() if (matched:=[r for r in rows if belongs(r)])}
        record['linked_inventory']={name:{'count':len(rows),'ids':[r.get('id') for r in rows]} for name,rows in record['linked_records'].items()}
        selected['identities'][owner]=record
    selected['publications'],resolutions=publications(collections['sources'])
    source_ids={r['id'] for matches in selected['publications'].values() for r in matches}
    selected['source_linked_records']={name:matched for name,rows in collections.items() if name!='sources' and (matched:=[r for r in rows if source_ids.intersection(set(r.get('source_ids') or [])|{r.get('source_id')})])}
    selected['candidate_prefix_matches']={name:matched for name,rows in collections.items() if (matched:=[r for r in rows if isinstance(r.get('id'),str) and r['id'].startswith(PREFIXES)])}
    selected['length_collection_fields']={name:sorted({k for r in rows for k in r}) for name,rows in collections.items() if 'length' in name}
    selected['manifest_namespaces']=sorted(bundle['manifest'])
    if not {'equatorial_basin_identities_v3','published_pacific_nec_nominal_width_v1'}.issubset(bundle['manifest']):
        raise ValueError('Installed basin and Pacific NEC markers required')
    return selected,resolutions


def audit():
    head=controls()
    from query_packet import descriptors,read_bundle_bytes
    manifest_raw=(ROOT/'almanac/query-engine.manifest.json').read_bytes()
    if sha(manifest_raw)!=ENGINE:raise ValueError('Exact basin-inclusive installed engine required')
    manifest=json.loads(manifest_raw);packet_raw=(ROOT/'almanac/query-data.json').read_bytes();packet=json.loads(packet_raw)
    parts=descriptors(packet)
    if (manifest['sha256']['almanac/query-data.json']!=sha(packet_raw) or packet['logical_sha256']!=LOGICAL or packet['logical_byte_length']!=LENGTH):raise ValueError('Installed descriptor differs')
    if any(manifest['sha256'].get('almanac/'+p['path'])!=p['sha256'] for p in parts):raise ValueError('Part receipt differs')
    raw=read_bundle_bytes(ROOT/'almanac/query-data.json')
    if sha(raw)!=LOGICAL or len(raw)!=LENGTH:raise ValueError('Installed logical bytes differ')
    bundle=json.loads(raw);del raw
    selected,resolutions=select_records(bundle);data=encoded(selected)
    if len(data)>500000:raise ValueError('Bounded selected metadata exceeded')
    if subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain']).strip():raise ValueError('Audit changed tracked files')
    result={'schema':'osw.chen-indian-sec-ridge-length-parent-audit.v1','status':'PASS_READ_ONLY','source_commit':head,
        'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],
        'engine_manifest_sha256':ENGINE,'logical_sha256':LOGICAL,'logical_byte_length':LENGTH,
        'packet_parts_verified':len(parts),'collection_counts':{k:len(v) for k,v in bundle['collections'].items()},
        'publication_resolutions':resolutions,'selected_records_sha256':sha(data),'selected_records_bytes':len(data),
        'packet_loaded_only_in_cloud':True,'index_loaded':False,'native_wasm_built':False,
        'scientific_data_changed':False,'browser_run':False,'working_branch_installed':False}
    OUT.mkdir(parents=True,exist_ok=False)
    (OUT/'selected-records.json').write_bytes(data);(OUT/'result.json').write_bytes(encoded(result))
    print(json.dumps(result))


if __name__=='__main__':
    try:audit()
    except Exception as error:
        if os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true':
            OUT.mkdir(parents=True,exist_ok=True)
            (OUT/'failure.json').write_bytes(encoded({'status':'FAIL','error':str(error),'source_commit':os.environ.get('GITHUB_SHA')}))
        raise
