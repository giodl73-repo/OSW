"""Read-only cloud audit of prepared current reaches, cited widths and named-feature identities."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit,unquote

ROOT=Path(__file__).resolve().parents[1]
REQUEST='research/current-core-gap-followup-parent-request-v1.json'
PREFLIGHT='research/current-core-gap-followup-parent-preflight-v1.json'
WORKFLOW='.github/workflows/current-core-gap-followup-parent-cloud-v1.yml'
OUT=ROOT/'.pytest_cache/current-core-gap-followup-parent-v1'
ENGINE='59ffdc89571f4e589646f029b3cbb512952e813c1001d5fe1c49f937549faa37'
LOGICAL='7b4b5133c915102014f93a6d838e62201b0169e1b183b1d4beae65e01972bccf'
LENGTH=195331266
FORBIDDEN=['index_load_permitted','native_wasm_build_permitted','browser_permitted','ocean_field_processing_permitted',
           'working_branch_installation_permitted','local_bulk_sync_permitted','main_merge_permitted']
PAPERS={
 'peters_2005':{'doi':'10.1175/jpo2679.1','title':'Mixing and Entrainment in the Red Sea Outflow Plume. Part I: Plume Structure',
  'title_aliases':['Mixing and Entrainment in the Red Sea Outflow Plume. Part 1: Plume Structure'],
  'urls':['https://www2.whoi.edu/site/bower-lab/wp-content/uploads/sites/12/2018/03/Peters_2005_MixingEntrainment.pdf']},
 'nilsen_2016':{'doi':'10.1175/jpo-d-15-0058.1','title':'A Simple Shelf Circulation Model: Intrusion of Atlantic Water on the West Spitsbergen Shelf',
  'urls':['https://pureadmin.uhi.ac.uk/ws/portalfiles/portal/1963315/Nilsen_et_al_jpo_2016.pdf']},
 'asclme_2008_51pp':{'doi':None,'title':'2008 ASCLME Survey No. 3, Preliminary cruise report No 7/2008',
  'urls':['https://archive.iwlearn.org/asclme.org/reports2013/Cruise reports/51 ASCLME cruise report 2008 MASCARENE PLATEAUall-acc.pdf']},
 'new_2007':{'doi':'10.1016/j.dsr.2006.08.016','title':'On the circulation of water masses across the Mascarene Plateau in the South Indian Ocean',
  'urls':['https://nora.nerc.ac.uk/id/eprint/144020/']}}
OWNERS=['current:red-sea-saline-overflow','current:indian-south-equatorial','current:west-spitsbergen','current:spitsbergen-atlantic']
CANDIDATE_OWNER='current:spitsbergen-trough'
CANDIDATE_IDS={CANDIDATE_OWNER,'redsox-peters2005-northern-summer-reported-reach',
 'spitsbergen-trough-nilsen2016-tampen-i1-reported-distance',
 'spitsbergen-trough-nilsen2016-lexryggen-i1-reported-distance',
 'indian-sec-asclme2008-literature-cited-upstream-width'}
HIGH_LEVEL=['widths','measurements','length_assessments','reference_routes','current_basin_memberships',
 'current_sections','current_mean_core_sections','current_speed_statistics','current_core_velocity_estimates','current_characteristic_velocities']

def read(p):return json.loads((ROOT/p).read_bytes())
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def title(value):return re.sub('[^a-z0-9]','',str(value or '').casefold())
def url(value):
    parsed=urlsplit(str(value or '').strip())
    return (parsed.hostname or '').casefold(),unquote(parsed.path).rstrip('/').casefold()
def doi(value):
    value=unquote(str(value or '').strip()).lower()
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
        matches=[];conflicts=[];reasons={}
        paper_doi=doi(paper['doi'])
        titles={title(t) for t in [paper['title']]+paper.get('title_aliases',[])}
        for row in rows:
            why=[]
            if paper_doi and paper_doi in [doi(row.get('doi')),doi(row.get('url'))]:why.append('doi')
            if row.get('url') and url(row['url']) in {url(u) for u in paper['urls']}:why.append('url')
            if any(title(row.get(k)) in titles for k in ['title','label']):why.append('title')
            if why:
                matches.append(row);reasons[row['id']]=why
                if paper_doi and row.get('doi') and doi(row['doi'])!=paper_doi:conflicts.append(row['id'])
        selected[key]=matches
        status='CONFLICTING_METADATA' if conflicts else 'MISSING' if not matches else 'UNIQUE_EXISTING' if len(matches)==1 else 'RECONCILIATION_REQUIRED'
        if key=='asclme_2008_51pp' and matches and status=='UNIQUE_EXISTING' and 'url' not in reasons[matches[0]['id']]:
            status='VERSION_REVIEW_REQUIRED'
        resolutions[key]={'status':status,'matching_source_ids':[r['id'] for r in matches],
                          'conflicting_source_ids':conflicts,'match_reasons':reasons}
    return selected,resolutions

def projection(row):
    # Every omitted large field is explicit and has exact canonical bytes/hash.
    out={};omitted={}
    for key,value in row.items():
        raw=canonical(value)
        if len(raw)>16000:omitted[key]={'canonical_bytes':len(raw),'canonical_sha256':sha(raw)}
        else:out[key]=value
    if omitted:return {'record_projection':out,'omitted_fields':omitted,'canonical_record_sha256':sha(canonical(row))}
    return row

def owns(row,owner):
    return row.get('current_id')==owner.removeprefix('current:') or row.get('entity_id')==owner or row.get('family_entity_id')==owner

def named_candidate(row):
    # STC alone is ambiguous; only the full named concept or exact entity ID matches.
    if any(row.get(k)==CANDIDATE_OWNER for k in ['id','entity_id','current_id']):return True
    def scan(value):
        if isinstance(value,str):
            normalized=title(value)
            return any(n in normalized for n in ['spitsbergentroughcurrent','spitzbergentroughcurrent'])
        if isinstance(value,list):return any(scan(v) for v in value)
        if isinstance(value,dict):return any(scan(v) for k,v in value.items() if k not in ['source_json','geometry','coordinates'])
        return False
    return scan(row)

def commit_parent(raw):
    # cat-file retains the actual commit headers even in a depth-one checkout.
    headers=raw.decode('utf8').split('\n\n',1)[0].splitlines()
    parents=[line.removeprefix('parent ') for line in headers if line.startswith('parent ')]
    if len(parents)!=1 or not re.fullmatch('[0-9a-f]{40}',parents[0]):raise ValueError('One exact commit parent required')
    return parents[0]

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
    for key,value in {'schema':'osw.current-core-gap-followup-parent-request.v1','workflow':WORKFLOW,'execute':True,
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
    main=json.loads(subprocess.check_output(['gh','api','repos/giodl73-repo/OSW/git/ref/heads/main']))['object']['sha']
    if main!='19148702de6433253dbf412a0a28c0cb4f8e409e':raise ValueError('Main ref changed')
    if head!=remote or head!=os.environ['GITHUB_SHA']:raise ValueError('Current source checkout required')
    parent=commit_parent(subprocess.check_output(['git','-c','core.fsmonitor=false','cat-file','-p','HEAD']))
    if parent!=pref['source_parent_commit']:raise ValueError('Exact audited source parent required')
    if subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain']).strip():raise ValueError('Clean checkout required')
    return head

def select_records(bundle):
    collections=bundle['collections']
    for name,count in [('reference_routes',83),('widths',189),('sources',229),('current_basin_memberships',5),('current_characteristic_velocities',10)]:
        if len(collections[name])!=count:raise ValueError('Installed inventory differs: '+name)
    if len(collections)!=78 or sum(map(len,collections.values()))!=110320:raise ValueError('Installed full inventory differs')
    selected={'identities':{}}
    for owner in OWNERS+[CANDIDATE_OWNER]:
        record={}
        for key,collection in [('object','objects'),('entity','entities')]:
            rows=[r for r in collections[collection] if r.get('id')==owner]
            if len(rows)>1 or (owner in OWNERS and len(rows)!=1):raise ValueError('Unique installed owner required: '+owner+'/'+key)
            record[key]=rows[0] if rows else None
        record['planning_decisions']=[projection(r) for r in collections['route_decisions'] if r.get('entity_id')==owner]
        for name in HIGH_LEVEL:record[name]=[projection(r) for r in collections.get(name,[]) if owns(r,owner)]
        source_ids=set((record['object'] or {}).get('source_ids',[]))
        record['owner_sources']=[r for r in collections['sources'] if r['id'] in source_ids]
        record['linked_inventory']={}
        for name,rows in collections.items():
            ids=[r.get('id') for r in rows if owns(r,owner)]
            if ids:
                inventory={'count':len(ids),'canonical_ids_sha256':sha(canonical(ids))}
                if len(ids)<=100:inventory['ids']=ids
                else:inventory['ids_omitted_count']=len(ids)
                record['linked_inventory'][name]=inventory
        selected['identities'][owner]=record
    selected['candidate_record_id_matches']=[{'collection':name,'record':projection(r)} for name,rows in collections.items() for r in rows if r.get('id') in CANDIDATE_IDS]
    selected['named_feature_matches']=[{'collection':name,'record':projection(r)} for name,rows in collections.items() for r in rows if named_candidate(r)]
    selected['publications'],resolutions=publications(collections['sources'])
    source_ids={row['id'] for matches in selected['publications'].values() for row in matches}
    paper_dois={doi(p['doi']) for p in PAPERS.values() if p['doi']}
    linked=[]
    for name in HIGH_LEVEL:
        for row in collections.get(name,[]):
            reasons=[]
            if source_ids.intersection(set(row.get('source_ids',[]))|{row.get('source_id')}):reasons.append('source_id')
            if any(doi(row.get(k)) in paper_dois for k in ['source_doi','doi','source_url']):reasons.append('direct_doi_field')
            if reasons:linked.append({'collection':name,'match_reasons':reasons,'record':projection(row)})
    selected['publication_linked_measurement_records']=linked
    terms=('peters','jpo2679','nilsen','jpo-d-15-0058','asclme','mascarene','2006.08.016','tampen','lexryggen')
    selected['related_source_records']=[r for r in collections['sources'] if any(term in json.dumps(r,ensure_ascii=False).casefold() for term in terms)]
    selected['related_high_level_records']=[{'collection':name,'record':projection(r)} for name in HIGH_LEVEL for r in collections.get(name,[]) if any(term in json.dumps(r,ensure_ascii=False).casefold() for term in terms)]
    selected['manifest_namespaces']=sorted(bundle['manifest'])
    selected['scope_note']='Bibliography or text mentions are discovery matches, not proof of source ownership, alias equivalence or duplicate measurement.'
    return selected,resolutions


def audit():
    head=controls()
    from query_packet import descriptors,read_bundle_bytes
    manifest_raw=(ROOT/'almanac/query-engine.manifest.json').read_bytes()
    if sha(manifest_raw)!=ENGINE:raise ValueError('Exact Pacific-jet-inclusive installed engine required')
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
    result={'schema':'osw.current-core-gap-followup-parent-audit.v1','status':'PASS_READ_ONLY','source_commit':head,
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
