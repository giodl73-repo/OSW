"""One-pass cloud-only ACT archive metadata discovery; no ocean fields."""
import ftplib,hashlib,json,os,re,signal,time
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[1]
OP='research/act2010-instrument-metadata-operator-v1.json'
HOST='ftp-oceans.ncei.noaa.gov'
PREFIX='/nodc/archive/arc0085/0140939/'
BODY_CAP=500000


def atomic(path,obj):
    raw=(json.dumps(obj,indent=2,allow_nan=False)+'\n').encode();temp=path.with_suffix(path.suffix+'.tmp')
    with temp.open('wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    os.replace(temp,path)


def timeout(signum,frame):
    if signum!=signal.SIGALRM:raise SystemExit('Producer stopped; no reconnect or retry')
    raise TimeoutError('Absolute operation deadline reached')


def observed_entries(raw,parent):
    if len(raw)>128000 or not parent.startswith(PREFIX):raise ValueError('Bounded exact archive listing required')
    entries=[]
    for line in raw.decode('utf8',errors='strict').splitlines():
        if not line or line.startswith('total '):continue
        parts=line.split(maxsplit=8)
        if len(parts)!=9 or parts[0][0] not in ['d','-','l']:raise ValueError('Unsupported source listing retained without guessed interpretation')
        name=parts[8]
        if parts[0][0]=='l':continue
        if name in ['.','..']:continue
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_. -]{0,180}',name):raise ValueError('Observed simple archive basename required')
        path=parent.rstrip('/')+'/'+name
        if not str(PurePosixPath(path)).startswith(PREFIX):raise ValueError('Archive escape rejected')
        entries.append({'name':name,'path':path,'kind':'directory' if parts[0][0]=='d' else 'file'})
    if len(entries)>2000:raise ValueError('Metadata entry reserve exceeded')
    return entries


def is_document(entry):
    return entry['kind']=='file' and bool(re.fullmatch(r'(?:readme|read_me|license|licence|about)[A-Za-z0-9_. -]*\.txt',entry['name'],re.I))


def reserve(journal,folder,key,command,path,cap):
    if len(journal['operations'])>=6 or any(r['target_id']==key or (r['command'],r['path'])==(command,path) for r in journal['operations']):raise ValueError('Six metadata operations, unique exact targets, no reset')
    if journal['total_body_bytes']+cap+1>BODY_CAP:raise ValueError('Whole-stage response reserve exhausted')
    row={'target_id':key,'command':command,'path':path,'attempts':1,'status':'reserved_before_remote_operation','bytes_received':0,'cap_bytes':cap}
    journal['operations'].append(row);atomic(folder/'journal.json',journal)
    return row


def operation(client,folder,journal,key,command,path,cap,deadline):
    if time.monotonic()+26>deadline:return None
    row=reserve(journal,folder,key,command,path,cap);raw=folder/(key+'.raw');size=0
    signal.setitimer(signal.ITIMER_REAL,min(25,deadline-time.monotonic()))
    try:
        with raw.open('xb') as f:
            def callback(block):
                nonlocal size
                remaining=cap+1-size;part=block[:max(0,remaining)]
                f.write(part);f.flush();os.fsync(f.fileno());size+=len(part)
                row['bytes_received']=size
                if size>cap:raise ValueError('Absolute metadata response body cap exceeded')
            client.retrbinary(command+' '+path,callback,blocksize=4096)
        row.update(status='received_archived_before_interpretation',raw_file=raw.name,sha256=hashlib.sha256(raw.read_bytes()).hexdigest())
        return raw.read_bytes()
    except BaseException as error:
        row.update(status='failed_or_interrupted_no_retry',error_type=type(error).__name__,error_summary=str(error)[:240])
        if raw.exists():row.update(raw_file=raw.name,sha256=hashlib.sha256(raw.read_bytes()).hexdigest())
        if isinstance(error,SystemExit):raise
        return None
    finally:
        signal.setitimer(signal.ITIMER_REAL,0);journal['total_body_bytes']+=size;atomic(folder/'journal.json',journal)


def collect(folder,client,deadline):
    folder.mkdir(exist_ok=False)
    journal={'schema':'osw.act2010-instrument-metadata-journal.v1','host':HOST,'distribution_scheme':'ftp_anonymous_public_listing',
      'source_distribution_url':'ftp://'+HOST+PREFIX,'operations':[],'total_body_bytes':0,
      'maximum_metadata_remote_operations':6,'maximum_independent_case_remote_operations':18,
      'maximum_attempts_per_target':1,'metadata_decoded_scalar_reserve':2000,'decoded_ocean_values':0,
      'ocean_field_requests':0,'all_prior_source_budgets_unchanged':True,'producer_finalized_before_artifact_upload':False}
    report={'schema':'osw.act2010-instrument-metadata.v1','entity_id':'current:agulhas','source_accession':'0140939',
      'observed_entries':[],'documentation_receipts':[],'instrument_file_candidates':[],
      'dataset_access_label_conflict_resolved':False,'native_field_acquisition_eligible':False,
      'native_field_read_count':0,'physical_depth_references_admitted':0,'runtime_changed':False,'full_goal_complete':False}
    queue=[PREFIX];seen=set();failed=False
    try:
        row=reserve(journal,folder,'session-00','CONNECT_LOGIN_ANONYMOUS',PREFIX,0)
        signal.setitimer(signal.ITIMER_REAL,min(25,deadline-time.monotonic()))
        try:
            client.connect(HOST,21,timeout=25);client.login('anonymous','anonymous@')
            row['status']='anonymous_session_opened_no_fields'
        except BaseException as error:
            row.update(status='failed_or_interrupted_no_reconnect',error_type=type(error).__name__,error_summary=str(error)[:240]);raise
        finally:signal.setitimer(signal.ITIMER_REAL,0);atomic(folder/'journal.json',journal)
        while queue and len(journal['operations'])<6:
            parent=queue.pop(0)
            if parent in seen:continue
            seen.add(parent);key='listing-'+str(len(seen)).zfill(2)
            raw=operation(client,folder,journal,key,'LIST',parent,128000,deadline)
            if raw is None:failed=True;break
            entries=observed_entries(raw,parent)
            if len(report['observed_entries'])+len(entries)>2000:raise ValueError('Global metadata entries reserve cannot reset per directory')
            report['observed_entries'].extend(entries)
            # Traverse only observed metadata/archive directories, never guessed names or parallel sessions.
            for e in entries:
                if e['kind']=='directory' and e['name'].lower() in ['data','0-data','documentation','about','docs'] and len(e['path'].split('/'))<=9:queue.append(e['path']+'/')
                if e['kind']=='file' and e['name'].lower().endswith(('.nc','.mat')):report['instrument_file_candidates'].append({'url':'ftp://'+HOST+e['path'],'metadata_listing_target':key,'field_values_read':False})
            docs=[e for e in entries if is_document(e)]
            if docs and not report['documentation_receipts'] and len(journal['operations'])<6:
                doc=sorted(docs,key=lambda e:e['name'])[0]
                body=operation(client,folder,journal,'documentation-01','RETR',doc['path'],64000,deadline)
                report['documentation_receipts'].append({'observed_path':doc['path'],'retained':body is not None,'values_interpreted':False})
                if body is None:failed=True;break
        report['status']='source_metadata_retained_no_field_eligibility' if not failed else 'partial_metadata_no_retry_or_fields'
    except BaseException as error:
        failed=True;report.update(status='source_metadata_failed_or_interrupted_no_retry',error_type=type(error).__name__,error_summary=str(error)[:240])
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        client.close();journal['producer_finalized_before_artifact_upload']=True
        report['bounded_metadata_traversal_complete']=not queue and not failed
        report['unvisited_observed_directories']=queue
        journal['unused_independent_case_remote_operations']=18-len(journal['operations'])
        atomic(folder/'journal.json',journal);atomic(folder/'report.json',report)
        print(json.dumps({'status':report['status'],'remote_operations_reserved':len(journal['operations']),
          'instrument_files_observed':len(report['instrument_file_candidates']),'ocean_field_requests':0,
          'body_bytes':journal['total_body_bytes'],'native_field_acquisition_eligible':False}),flush=True)
    return report,journal,failed


def main():
    op=json.loads((ROOT/OP).read_bytes())
    for f,h in op['input_sha256'].items():
        if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=h:raise ValueError('Pinned metadata input changed:'+f)
    if op['maximum_metadata_remote_operations']!=6 or op['maximum_independent_case_remote_operations']!=18 or op['ocean_field_requests_allowed']!=0:raise ValueError('Predeclared stage/case budget required')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,timeout)
    report,journal,failed=collect(ROOT/'act2010-instrument-metadata-v1',ftplib.FTP(),time.monotonic()+210)
    if failed:raise SystemExit(1)

if __name__=='__main__':main()
