"""Continue only observed ACT version/XML targets within the original aggregate budget."""
import copy,ftplib,hashlib,json,signal,time,xml.etree.ElementTree as ET
from pathlib import Path
import discover_act2010_instrument_metadata_v1 as frozen
ROOT=Path(__file__).resolve().parents[1]
OP='research/act2010-version-metadata-operator-v2.json'
PRIOR='research/source-data/act2010-instrument-metadata-v1'


def prior_state(root=ROOT):
    journal=json.loads((root/PRIOR/'journal.json').read_bytes());report=json.loads((root/PRIOR/'report.json').read_bytes())
    if len(journal['operations'])!=2 or journal['total_body_bytes']!=134 or journal['unused_independent_case_remote_operations']!=16 or not journal['producer_finalized_before_artifact_upload']:raise ValueError('Exact completed root-stage custody required')
    expected=[('0140939.1.1.xml','file'),('1.1','directory')]
    if [(e['name'],e['kind']) for e in report['observed_entries']]!=expected:raise ValueError('Only actual observed version and XML targets required')
    raw=(root/PRIOR/'listing-01.raw').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=journal['operations'][1]['sha256'] or len(raw)!=134:raise ValueError('Exact retained root listing bytes required, no repeat')
    return journal,report


def legal_metadata(raw):
    if len(raw)>128000 or b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():raise ValueError('Bounded source XML without entity declarations required')
    tree=ET.fromstring(raw);nodes=list(tree.iter())
    if len(nodes)>5000:raise ValueError('Metadata XML node bound exceeded')
    local=lambda t:t.rsplit('}',1)[-1]
    wanted={'useLimitation','accessConstraints','useConstraints','otherConstraints','distributionStatement','MD_RestrictionCode'}
    legal=[]
    for node in nodes:
        if local(node.tag) in wanted:
            text=' '.join(' '.join(node.itertext()).split())
            if text:legal.append({'tag':local(node.tag),'text':text[:8000],'codeListValue':node.attrib.get('codeListValue')})
    if len(legal)>64 or sum(len(r['text']) for r in legal)>32768:raise ValueError('Global legal metadata materialization cap exceeded')
    return {'provider_legal_statements':legal,'field_permission_automatically_inferred':False,
            'native_unit_QC_depth_time_frame_verified':False}


def collect(folder,client,prior_journal,prior_report,deadline):
    folder.mkdir(exist_ok=False);started=time.monotonic()
    journal=copy.deepcopy(prior_journal)
    journal.update(schema='osw.act2010-version-metadata-journal.v2',prior_receipt_source_directory=PRIOR,
      prior_operation_count=2,prior_response_body_bytes=134,prior_stage_maximum_sessions_preserved=1,
      continuation_maximum_sessions=1,aggregate_explicitly_planned_sessions=2,
      prior_operation_time_charge_seconds=50,remaining_case_seconds_before_this_stage=160,
      producer_finalized_before_artifact_upload=False)
    base=next(e['path']+'/' for e in prior_report['observed_entries'] if e['kind']=='directory')
    xml=next(e['path'] for e in prior_report['observed_entries'] if e['kind']=='file')
    report={'schema':'osw.act2010-version-metadata.v2','entity_id':'current:agulhas','source_accession':'0140939',
      'prior_root_listing_retrieved_again':False,'prior_operation_count':2,'prior_response_body_bytes':134,
      'observed_version_directory':base,'provider_legal_metadata':None,'new_observed_entries':[],
      'instrument_file_candidates':[],'native_field_acquisition_eligible':False,'native_ocean_fields_read':0,
      'new_depth_references':0,'metadata_stage_traversal_complete':False,'runtime_changed':False,'full_goal_complete':False}
    failed=False
    try:
        if time.monotonic()+26>deadline:raise TimeoutError('Insufficient remaining aggregate operation time')
        row=frozen.reserve(journal,folder,'phase2-session-01','CONNECT_LOGIN_ANONYMOUS',base,0)
        signal.setitimer(signal.ITIMER_REAL,min(25,deadline-time.monotonic()))
        try:
            client.connect(frozen.HOST,21,timeout=25);client.login('anonymous','anonymous@');row['status']='explicit_continuation_session_opened_no_reconnect'
        except BaseException as error:
            row.update(status='failed_or_interrupted_no_reconnect',error_type=type(error).__name__,error_summary=str(error)[:240]);raise
        finally:signal.setitimer(signal.ITIMER_REAL,0);frozen.atomic(folder/'journal.json',journal)
        raw=frozen.operation(client,folder,journal,'phase2-provider-xml','RETR',xml,128000,deadline)
        if raw is None:raise RuntimeError('Provider XML operation failed; retained/no retry')
        report['provider_legal_metadata']=legal_metadata(raw)
        raw=frozen.operation(client,folder,journal,'phase2-version-list','LIST',base,128000,deadline)
        if raw is None:raise RuntimeError('Version listing failed; retained/no retry')
        entries=frozen.observed_entries(raw,base);report['new_observed_entries'].extend(entries)
        data=[e for e in entries if e['kind']=='directory' and e['name']=='data']
        if len(data)!=1:raise ValueError('One observed data directory needed; no guessed child path')
        path=data[0]['path']+'/'
        raw=frozen.operation(client,folder,journal,'phase2-data-list','LIST',path,128000,deadline)
        if raw is None:raise RuntimeError('Data listing failed; retained/no retry')
        report['new_observed_entries'].extend(frozen.observed_entries(raw,path))
        if len(report['new_observed_entries'])+len(prior_report['observed_entries'])>2000:raise ValueError('Global metadata entry cap, not per-listing cap')
        report['instrument_file_candidates']=[{'url':'ftp://'+frozen.HOST+e['path'],'field_values_read':False} for e in report['new_observed_entries'] if e['kind']=='file' and e['name'].lower().endswith(('.nc','.mat'))]
        report['metadata_stage_traversal_complete']=True
        report['status']='observed_version_provider_metadata_retained_no_field_admission'
    except BaseException as error:
        failed=True;report.update(status='metadata_continuation_failed_or_partial_no_retry',error_type=type(error).__name__,error_summary=str(error)[:240])
    finally:
        signal.setitimer(signal.ITIMER_REAL,0);client.close()
        journal['producer_finalized_before_artifact_upload']=True
        journal['unused_independent_case_remote_operations']=18-len(journal['operations'])
        journal['unused_metadata_stage_remote_operations']=6-len(journal['operations'])
        journal['this_stage_elapsed_seconds']=time.monotonic()-started
        journal['case_time_charge_seconds']=50+journal['this_stage_elapsed_seconds']
        report['unvisited_observed_directories']=[e for e in report['new_observed_entries'] if e['kind']=='directory' and e['name'] not in ['data']]
        if len(json.dumps(report).encode())>1000000:
            report={'schema':report['schema'],'status':'metadata_report_bound_exceeded_retained_raw_no_retry','native_field_acquisition_eligible':False,'native_ocean_fields_read':0,'new_depth_references':0,'raw_custody_recoverable_from_journal':True,'runtime_changed':False,'full_goal_complete':False};failed=True
        frozen.atomic(folder/'journal.json',journal);frozen.atomic(folder/'report.json',report)
        if journal['operations'][:2]!=prior_journal['operations']:raise ValueError('Every prior source receipt must survive exactly')
        print(json.dumps({'status':report['status'],'aggregate_case_operations_reserved':len(journal['operations']),
          'unused_case_operations':journal['unused_independent_case_remote_operations'],'total_metadata_body_bytes':journal['total_body_bytes'],
          'instrument_files_observed':len(report['instrument_file_candidates']),'native_ocean_fields_read':0,'native_field_acquisition_eligible':False}),flush=True)
    return report,journal,failed


def main():
    op=json.loads((ROOT/OP).read_bytes())
    for f,h in op['input_sha256'].items():
        if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=h:raise ValueError('Pinned metadata continuation input changed:'+f)
    if op['prior_operations_charged']!=2 or op['additional_remote_operations_maximum']!=4 or op['aggregate_metadata_operations_cap']!=6 or op['aggregate_case_operations_cap']!=18 or op['remaining_case_seconds']!=160:raise ValueError('Original stage/case/time budget must not reset')
    journal,report=prior_state()
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,frozen.timeout)
    _,_,failed=collect(ROOT/'act2010-version-metadata-v2',ftplib.FTP(),journal,report,time.monotonic()+160)
    if failed:raise SystemExit(1)

if __name__=='__main__':main()
