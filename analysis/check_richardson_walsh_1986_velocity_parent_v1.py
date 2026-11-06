"""Read-only cloud audit of Atlantic characteristic velocity and family metadata and publication identities."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit,unquote

ROOT=Path(__file__).resolve().parents[1]
REQUEST='research/richardson-walsh-1986-characteristic-velocity-parent-request-v1.json'
PREFLIGHT='research/richardson-walsh-1986-characteristic-velocity-parent-preflight-v1.json'
WORKFLOW='.github/workflows/richardson-walsh-1986-characteristic-velocity-parent-cloud-v1.yml'
OUT=ROOT/'.pytest_cache/richardson-walsh-1986-characteristic-velocity-parent-v1'
OWNER='current:atlantic-north-equatorial'
ENGINE='0d6f469fe5849cd95f447280eee842f158711dc0b7016102319d3fef316dd54b'
LOGICAL='404de2dee8ca4fc4968f24a23f892b336bd5392d8b44a3556206a8944e2b2e3a'
LENGTH=195287491
FORBIDDEN=['index_load_permitted','native_wasm_build_permitted','browser_permitted','ocean_field_processing_permitted',
           'working_branch_installation_permitted','local_bulk_sync_permitted','main_merge_permitted']
PAPERS={'richardson_walsh_1986': {'doi': '10.1029/jc091ic09p10537', 'title': 'Mapping climatological seasonal variations of surface currents in the tropical Atlantic using ship drifts', 'urls': ['https://www2.whoi.edu/staff/prichardson/wp-content/uploads/sites/75/2018/11/Richardson-Walsh-1986-jgr.pdf']}}

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
            match=(doi(row.get('doi',''))==paper['doi'] or doi(row.get('url',''))==paper['doi']
                or url(row.get('url','')) in {url(u) for u in paper['urls']}
                or title(row.get('title',''))==title(paper['title'])
                or title(row.get('label',''))==title(paper['title']))
            if match:
                matches.append(row)
                if row.get('doi') and doi(row['doi'])!=paper['doi']:conflicts.append(row['id'])
        selected[key]=matches
        status='CONFLICTING_METADATA' if conflicts else 'MISSING' if not matches else 'UNIQUE_EXISTING' if len(matches)==1 else 'RECONCILIATION_REQUIRED'
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
    for key,value in {'schema':'osw.richardson-walsh-1986-characteristic-velocity-parent-request.v1','workflow':WORKFLOW,'execute':True,
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
    for name,count in [('reference_routes',83),('widths',187),('sources',227),('current_basin_memberships',5)]:
        if len(collections[name])!=count:raise ValueError('Installed inventory differs: '+name)
    selected={'identities':{}}
    for owner in ['current:'+value for value in ['caribbean','guiana','north-brazil','brazil','guinea','atlantic-north-equatorial','atlantic-north-equatorial-countercurrent','atlantic-south-equatorial','north-equatorial','south-equatorial']]:
        record={}
        for key,collection,field in [('object','objects','id'),('entity','entities','id'),('planning_decision','route_decisions','entity_id')]:
            rows=[r for r in collections[collection] if r.get(field)==owner]
            if len(rows)!=1:raise ValueError('One installed identity record required: '+owner+'/'+key)
            record[key]=rows[0]
        for name in ['widths','reference_routes','length_assessments','current_basin_memberships','current_speed_statistics','current_core_velocity_estimates']:
            record[name]=[r for r in collections[name] if r.get('current_id')==owner.removeprefix('current:') or r.get('entity_id')==owner or r.get('family_entity_id')==owner]
        record['owner_sources']=[r for r in collections['sources'] if r['id'] in record['object']['source_ids']]
        record['linked_inventory']={name:{'count':len(matched),'ids':[r.get('id') for r in matched]} for name,rows in collections.items() if (matched:=[r for r in rows if r.get('current_id')==owner.removeprefix('current:') or r.get('entity_id')==owner])}
        selected['identities'][owner]=record
    selected['candidate_record_id_matches']=[r for records in collections.values() for r in records if r.get('id') in {f'richardson-walsh1986-table1-characteristic-velocity-{i:02}' for i in range(1,11)}]
    selected['publications'],resolutions=publications(collections['sources'])
    source_ids={row['id'] for matches in selected['publications'].values() for row in matches}
    selected['publication_linked_measurement_records']=[r for name in ['widths','current_speed_statistics','current_core_velocity_estimates','current_characteristic_velocities'] for r in collections.get(name,[]) if source_ids.intersection(set(r.get('source_ids',[]))|{r.get('source_id')}) or any(doi(r.get(k,'')) in {p['doi'] for p in PAPERS.values()} for k in ['source_doi','doi','source_url'])]
    selected['manifest_namespaces']=sorted(bundle['manifest'])
    if 'equatorial_basin_identities_v3' not in bundle['manifest']:raise ValueError('Installed basin admission marker missing')
    return selected,resolutions


def audit():
    head=controls()
    from query_packet import descriptors,read_bundle_bytes
    manifest_raw=(ROOT/'almanac/query-engine.manifest.json').read_bytes()
    if sha(manifest_raw)!=ENGINE:raise ValueError('Exact Dimoune-inclusive installed engine required')
    manifest=json.loads(manifest_raw);packet_raw=(ROOT/'almanac/query-data.json').read_bytes();packet=json.loads(packet_raw)
    parts=descriptors(packet)
    if (manifest['sha256']['almanac/query-data.json']!=sha(packet_raw) or packet['logical_sha256']!=LOGICAL or packet['logical_byte_length']!=LENGTH):raise ValueError('Installed descriptor differs')
    if any(manifest['sha256'].get('almanac/'+p['path'])!=p['sha256'] for p in parts):raise ValueError('Part receipt differs')
    raw=read_bundle_bytes(ROOT/'almanac/query-data.json')
    if sha(raw)!=LOGICAL or len(raw)!=LENGTH:raise ValueError('Installed logical bytes differ')
    bundle=json.loads(raw);del raw
    selected,resolutions=select_records(bundle);data=encoded(selected)
    if len(data)>900000:raise ValueError('Bounded selected metadata exceeded')
    if subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain']).strip():raise ValueError('Audit changed tracked files')
    result={'schema':'osw.richardson-walsh-1986-characteristic-velocity-parent-audit.v1','status':'PASS_READ_ONLY','source_commit':head,
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
