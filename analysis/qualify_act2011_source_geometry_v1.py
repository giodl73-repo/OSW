"""Original ACT geometry documentation and bounded typed-point consistency checks."""
import copy,ftplib,hashlib,json,os,re,signal,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OP='research/act2011-source-geometry-operator-v1.json'
INDEX='research/act2010-retained-instrument-manifest-index-v1.json'
POINTS='research/act2011-native-point-observations-v2.json'
PRIOR='research/source-data/act2011-observed-pair-v1/journal.json'
AUDIT='research/act2011-retained-native-point-audit-v2.json'
BASE='/nodc/archive/arc0085/0140939/1.1/'
HOST='ftp-oceans.ncei.noaa.gov'
PATHS=['about/0140939_lonlat.txt','about/journal.txt']


def sha(raw):return hashlib.sha256(raw).hexdigest()
def atomic(path,obj):
    raw=(json.dumps(obj,indent=2,allow_nan=False)+'\n').encode();tmp=path.with_suffix(path.suffix+'.tmp')
    with tmp.open('wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)
def alarm(signum,frame):
    if signum!=signal.SIGALRM:raise SystemExit('Qualification producer stopped; no reconnect')
    raise TimeoutError('Absolute source qualification deadline')


def plan(index):
    lookup={r['manifest_path']:r for r in index['entries']}
    out=[]
    for i,path in enumerate(PATHS):
        r=lookup[path]
        if not r['regular_file'] or not r['documentation_candidate'] or r['provider_size_bytes']>5000:raise ValueError('Exact small observed public metadata document required')
        out.append({'target_id':['archive-lonlat','archive-journal'][i],'path':BASE+path,
          'provider_size_bytes':r['provider_size_bytes'],'provider_asserted_sha256':r['provider_asserted_sha256']})
    return out


def compare(points,context):
    if context['latitude_limits_degrees_north']!=[-34.9,-33.5] or context['longitude_limits_degrees_east']!=[27.4,28.4]:raise ValueError('Exact reviewed catalog extent required, no fitted correction')
    rows=[]
    for instrument,observations in enumerate(points['instrument_observations']):
        for r in observations:
            p=r.get('source_coordinate');valid=isinstance(p,list) and len(p)==2 and all(isinstance(v,(float,int)) for v in p)
            if valid:
                lon,lat=p;valid=-180<=lon<=360 and -90<=lat<=90
            inside=bool(valid and 27.4<=p[0]<=28.4 and -34.9<=p[1]<=-33.5)
            rows.append({'instrument_index':instrument,'requested_time_utc':r['requested_time_utc'],
               'provider_coordinate':copy.deepcopy(p),'coordinate_valid_numeric_degrees':bool(valid),
               'provider_coordinate_inside_catalogue_extent':inside,
               'provider_latitude_inside_catalogue_extent':bool(valid and -34.9<=p[1]<=-33.5),
               'provider_longitude_inside_catalogue_extent':bool(valid and 27.4<=p[0]<=28.4),
               'coordinate_correction_applied':False,'geographic_assignment_eligible':False})
    if len(rows)!=6:raise ValueError('All six original selected point outcomes must be represented')
    conflict=any(r['coordinate_valid_numeric_degrees'] and not r['provider_coordinate_inside_catalogue_extent'] for r in rows)
    return {'status':'SOURCE_CATALOGUE_EXTENT_CONFLICT' if conflict else 'NO_EXTENT_CONFLICT_BUT_LOCATION_STILL_UNVERIFIED',
       'point_outcomes':rows,'point_outcomes_checked':len(rows),
       'points_outside_catalogue_extent':sum(r['coordinate_valid_numeric_degrees'] and not r['provider_coordinate_inside_catalogue_extent'] for r in rows),
       'catalogue_extent_membership_is_location_validation':False,'geographic_assignment_eligible':False,
       'physical_state_join_eligible':False,'route_projection_eligible':False,'provider_coordinates_modified':False,
       'corrected_nominal_position':None,'source_native_points_retained':True}


def reserve(j,folder,key,command,path,cap):
    if len(j['operations'])>=18 or len(j['operations'])-10>=3:raise ValueError('Original18case/3qualificationoperation caps cannot reset')
    if any(r['target_id']==key or (r['command'],r['path'])==(command,path) for r in j['operations']):raise ValueError('No original resource or response replay')
    if j['qualification_body_bytes']+cap+1>10000:raise ValueError('Whole qualification response reserve exhausted')
    row={'target_id':key,'command':command,'path':path,'attempts':1,'phase':'existing_native_case_geometry_qualification',
         'cap_bytes':cap,'bytes_received':0,'status':'reserved_before_remote_operation'}
    j['operations'].append(row);atomic(folder/'journal.json',j);return row


def acquire(client,folder,j,target,deadline):
    if time.monotonic()+26>deadline:raise TimeoutError('Insufficient original-case time remains')
    row=reserve(j,folder,target['target_id'],'RETR',target['path'],target['provider_size_bytes']);path=folder/(target['target_id']+'.raw');size=0
    signal.setitimer(signal.ITIMER_REAL,min(25,deadline-time.monotonic()))
    try:
        with path.open('xb') as f:
            def callback(block):
                nonlocal size
                part=block[:max(0,target['provider_size_bytes']+1-size)];f.write(part);f.flush();os.fsync(f.fileno())
                size+=len(part);row['bytes_received']=size
                if size>target['provider_size_bytes']:raise ValueError('Manifest document size cap exceeded')
            client.retrbinary('RETR '+target['path'],callback,blocksize=4096)
        raw=path.read_bytes();row.update(raw_file=path.name,sha256=sha(raw))
        if size!=target['provider_size_bytes'] or sha(raw)!=target['provider_asserted_sha256']:raise ValueError('Original document size/providerSHA256 mismatch')
        row['status']='provider_hash_verified_archived_before_interpretation';return raw
    except BaseException as error:
        row.update(status='failed_or_interrupted_no_retry',error_type=type(error).__name__,error_summary=str(error)[:240])
        if path.exists():row.update(raw_file=path.name,sha256=sha(path.read_bytes()))
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL,0);j['qualification_body_bytes']+=size;j['total_body_bytes']+=size;atomic(folder/'journal.json',j)


def collect(folder,client,prior,audit,targets,points,context,deadline):
    folder.mkdir(exist_ok=False);started=time.monotonic();j=copy.deepcopy(prior)
    j.update(schema='osw.act2011-source-geometry-journal.v1',prior_journal_file=PRIOR,prior_operation_count=10,
      qualification_body_bytes=0,qualification_body_cap=10000,qualification_operation_cap=3,
      metadata_discovery_stage_operations_used_unchanged=6,metadata_discovery_stage_cap_unchanged=6,
      original_native_file_transfers_corrected=2,prior_native_scalar_bound_including_metadata=audit['conservative_case_scalar_bound_including_prior_metadata'],
      prior_case_time_charge_seconds=audit['case_time_charge_after_audit'],producer_finalized_before_artifact_upload=False)
    report={'schema':'osw.act2011-source-geometry-qualification.v1','entity_id':'current:agulhas','source_accession':'0140939',
       'catalogue_context':context,'consistency':compare(points,context),'documents':[],
       'new_native_ocean_values_decoded':0,'new_depth_references_admitted':0,'native_files_downloaded_again':False,
       'native_TIME_axes_read_again':False,'runtime_changed':False,'full_goal_complete':False}
    failed=False
    try:
        row=reserve(j,folder,'geometry-session-01','CONNECT_LOGIN_ANONYMOUS',BASE+'about/',0)
        signal.setitimer(signal.ITIMER_REAL,min(25,deadline-time.monotonic()))
        try:client.connect(HOST,21,timeout=25);client.login('anonymous','anonymous@');row['status']='explicit_geometry_postflight_session_opened'
        except BaseException as error:row.update(status='failed_no_reconnect',error_type=type(error).__name__,error_summary=str(error)[:240]);raise
        finally:signal.setitimer(signal.ITIMER_REAL,0);atomic(folder/'journal.json',j)
        for target in targets:
            raw=acquire(client,folder,j,target,deadline);text=raw.decode('utf8',errors='strict')
            report['documents'].append({'source_manifest_path':target['path'].removeprefix(BASE),'provider_sha256_verified':sha(raw),
              'source_text':text,'document_is_independent_physical_location_validation':False,
              'explicit_native_identifier_mentions':[s for s in ['M3960201','M3960301','M396-02','M396-03','mooring B'] if s.lower() in text.lower()]})
        report['status']='ORIGINAL_GEOMETRY_DOCUMENTS_RETAINED_CONFLICT_GATED_PENDING_SOURCE_RECONCILIATION'
    except BaseException as error:
        failed=True;report.update(status='GEOMETRY_DOCUMENT_ACQUISITION_PARTIAL_NO_RETRY_JOINS_STILL_GATED',error_type=type(error).__name__,error_summary=str(error)[:240])
    finally:
        signal.setitimer(signal.ITIMER_REAL,0);client.close();j['producer_finalized_before_artifact_upload']=True
        j['unused_independent_case_remote_operations']=18-len(j['operations'])
        j['case_time_charge_seconds']=audit['case_time_charge_after_audit']+time.monotonic()-started
        if j['operations'][:10]!=prior['operations']:raise ValueError('Original10source receipts must remain exact')
        atomic(folder/'journal.json',j);atomic(folder/'qualification.json',report)
        if sum(p.stat().st_size for p in folder.iterdir())>=2400000:raise ValueError('Original scientific chunk cap exceeded')
        print(json.dumps({'status':report['status'],'geometry_status':report['consistency']['status'],
           'point_outcomes_checked':report['consistency']['point_outcomes_checked'],'points_outside_catalogue_extent':report['consistency']['points_outside_catalogue_extent'],
           'aggregate_case_operations':len(j['operations']),'remaining_case_operations':j['unused_independent_case_remote_operations'],
           'qualification_body_bytes':j['qualification_body_bytes'],'new_native_ocean_values_decoded':0,
           'geographic_assignment_eligible':False}),flush=True)
    return report,j,failed


def main():
    op=json.loads((ROOT/OP).read_bytes())
    for f,h in op['input_sha256'].items():
        if sha((ROOT/f).read_bytes())!=h:raise ValueError('Pinned original source geometry input changed:'+f)
    prior=json.loads((ROOT/PRIOR).read_bytes());audit=json.loads((ROOT/AUDIT).read_bytes())
    if len(prior['operations'])!=10 or audit['conservative_case_scalar_bound_including_prior_metadata']!=85175 or audit['aggregate_case_operations_used_unchanged']!=10:raise ValueError('Exact prior case state required')
    if op['case_operations_cap']!=18 or op['additional_operation_cap']!=3 or op['remaining_case_seconds']!=155:raise ValueError('Original case/time/stage caps cannot reset')
    targets=plan(json.loads((ROOT/INDEX).read_bytes()))
    if targets!=op['targets']:raise ValueError('Only two predeclared observed original public documentation files')
    points=json.loads((ROOT/POINTS).read_bytes());context=json.loads((ROOT/op['catalogue_context_file']).read_bytes())
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,alarm)
    _,_,failed=collect(ROOT/'act2011-source-geometry-v1',ftplib.FTP(),prior,audit,targets,points,context,time.monotonic()+155)
    if failed:raise SystemExit(1)

if __name__=='__main__':main()
