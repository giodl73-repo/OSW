"""Remaining-field consumer using exact retained metadata and original aggregate caps."""
import copy
import hashlib
import json
import signal
import time
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path
import collect_tao_pacific_euc_daily_depth_v1 as frozen

ROOT=Path(__file__).resolve().parents[1]
OP='research/tao-pacific-euc-direct-source-operator-v2.json'
PRIOR='research/source-data/tao-pacific-euc-daily-depth-v1'
DIRECT='https://coastwatch.pfeg.noaa.gov/erddap/tabledap/pmelTaoDyAdcp.csv?'


def plan():
    output=[]
    for lon in [165,190,220,250]:
        for month in [3,6,9,12]:
            dates=[f'2005-{month:02d}-{day:02d}T12:00:00Z' for day in [14,15,16]]
            query=','.join(frozen.FIELDS)+f'&longitude={lon}&latitude=0&time>={dates[0]}&time<={dates[-1]}&depth>=5&depth<=350&orderByClosest("station,time,depth/10")'
            output.append({'target_id':f'field-{len(output):02d}','nominal_longitude':lon,'times_utc':dates,
                           'url':DIRECT+urllib.parse.quote(query,safe=',&=():/'),'cap_bytes':50000,
                           'maximum_rows':120,'reserved_numeric_scalars':720})
    return output


def diagnose(raw,target):
    rows=frozen.table(raw,frozen.FIELDS,frozen.UNITS,120)
    pairs={(r['array'],r['station']) for r in rows}
    if len(pairs)>1 or any(not a or not s for a,s in pairs):raise ValueError('One returned identifier pair per nominal-location patch required')
    a,s=next(iter(pairs)) if pairs else (None,None)
    bound={**target,'station':{'array':a,'station':s,'longitude':target['nominal_longitude'],'latitude':0}}
    value,numeric=frozen.profiles(raw,bound)
    for row in value:row['station_identifier_source']='returned_data_rows_not_guessed'
    return value,numeric


def imported(root=ROOT):
    j=json.loads((root/PRIOR/'journal.json').read_bytes())
    if [v['target_id'] for v in j['requests']]!=['metadata','catalogue'] or j['field_scalars_decoded']!=0 or j['maximum_requests']!=18 or not j['producer_finalized_before_artifact_upload']:
        raise ValueError('Exactly two completed historical metadata attempts and no fields required')
    if j['requests'][0]['status']!='received_archived_before_derivation' or j['requests'][1]['status']!='attempted_failed_or_interrupted_no_retry' or j['requests'][1]['error_type']!='HTTPError' or j['requests'][1]['error_summary']!='HTTP Error 302: ':
        raise ValueError('Original successful metadata and non-replayed302 must remain explicit')
    raw=(root/PRIOR/'metadata.raw').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=j['requests'][0]['sha256'] or j['total_body_bytes']!=14059:
        raise ValueError('Exact archived metadata and accumulated body custody required')
    return copy.deepcopy(j),frozen.metadata(raw)


def main():
    op=json.loads((ROOT/OP).read_bytes())
    for f,h in op['input_sha256'].items():
        if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=h:raise ValueError('Pinned input changed:'+f)
    if op['aggregate_maximum_http_requests']!=18 or op['prior_request_attempts']!=2 or op['maximum_new_field_requests']!=16 or op['remaining_programme_seconds']!=160 or op['global_scalar_reserve']!=12520:
        raise ValueError('Original aggregate scope cannot reset')
    journal,metadata=imported();history=copy.deepcopy(journal['requests'])
    folder=ROOT/'tao-pacific-euc-direct-source-v2';folder.mkdir(exist_ok=False)
    journal.update(schema='osw.tao-pacific-euc-direct-source-journal.v2',operator_file=OP,
                   operator_sha256=hashlib.sha256((ROOT/OP).read_bytes()).hexdigest(),
                   producer_finalized_before_artifact_upload=False,imported_prior_attempts=2,
                   imported_metadata_sha256=hashlib.sha256((ROOT/PRIOR/'metadata.raw').read_bytes()).hexdigest(),
                   prior_time_allowance_charged_seconds=50,remaining_programme_seconds=160)
    targets=plan();frozen.atomic(folder/'field-plan.json',frozen.encoded(targets))
    result={'schema':'osw.tao-pacific-euc-direct-source-depth.v2','entity_id':'current:pacific-equatorial-undercurrent',
            'metadata':metadata,'profiles':[],'source_target_outcomes':[{'target_id':t['target_id'],'status':'not_attempted'} for t in targets],
            'credit':'Modified NOAA/PMEL GTMBA daily ADCP observations accessed at NOAA ERD; original values, quality and nominal coordinates retained.',
            'physical_thickness_or_volume_promoted':False,'runtime_changed':False,'full_goal_complete':False}
    deadline=time.monotonic()+160
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,frozen.alarm)
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*a,**k):return None
    direct_open=urllib.request.build_opener(NoRedirect()).open
    def opener(request,timeout):
        try:return direct_open(request,timeout=timeout)
        except urllib.error.HTTPError as error:
            journal['requests'][-1]['source_http_status']=error.code
            if error.headers.get('Location'):
                journal['requests'][-1]['source_redirect_location_not_followed']=error.headers['Location'][:2048]
            raise
    frozen.atomic(folder/'journal.json',frozen.encoded(journal))
    try:
        for target,outcome in zip(targets,result['source_target_outcomes']):
            if len(journal['requests'])>=18:raise ValueError('Original aggregate18request cap exhausted')
            raw=frozen.acquire(target,folder,journal,opener,deadline)
            if raw is None:
                outcome['status']='attempted_failed_no_retry' if any(r['target_id']==target['target_id'] for r in journal['requests']) else 'not_attempted_deadline'
                if journal['requests'][-1].get('source_http_status') in [301,302,303,307,308]:
                    outcome['status']='redirect_rejected_remaining_targets_not_attempted'
                    break
                if time.monotonic()+26>deadline:break
                continue
            try:
                values,numeric=diagnose(raw,target);journal['field_scalars_decoded']+=numeric
                if journal['field_scalars_decoded']>11520:raise ValueError('Original scalar reserve exhausted')
                result['profiles'].extend(values);outcome['status']='parsed_and_diagnosed'
                journal['requests'][-1]['derivation_status']='parsed_and_diagnosed'
            except Exception as error:
                outcome.update(status='derivation_failed_retained_bytes_no_replay',error_type=type(error).__name__,error_summary=str(error)[:240])
                journal['requests'][-1]['derivation_status']=outcome['status']
            frozen.atomic(folder/'journal.json',frozen.encoded(journal));frozen.atomic(folder/'profiles.json',frozen.encoded(result))
            print(json.dumps({'target':target['target_id'],'outcome':outcome['status']}),flush=True)
        result['status']='all_remaining_field_targets_attempted' if len(journal['requests'])==18 else 'partial_deadline_no_retry'
    except BaseException as error:
        result.update(status='programme_interrupted_no_retry',error_type=type(error).__name__,error_summary=str(error)[:240])
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        assert journal['requests'][:2]==history
        journal['producer_finalized_before_artifact_upload']=True
        result['counts']={'aggregate_request_attempts':len(journal['requests']),'prior_request_attempts':2,
                          'new_field_attempts':len(journal['requests'])-2,
                          'profiles_with_reported_rows':sum(bool(p['source_depths_m']) for p in result['profiles']),
                          'daily_profile_rows_in_result':len(result['profiles']),
                          'finite_primary_lower_threshold_depths':sum(p['primary_lower_isotach_depth_m'] is not None for p in result['profiles']),
                          'finite_primary_threshold_layer_spans':sum(p['primary_threshold_layer_span_m'] is not None for p in result['profiles'])}
        frozen.atomic(folder/'journal.json',frozen.encoded(journal));frozen.atomic(folder/'profiles.json',frozen.encoded(result))
        if sum(p.stat().st_size for p in folder.iterdir())>2400000:raise ValueError('Original output cap exceeded')
        print(json.dumps({'status':result['status'],'counts':result['counts'],'field_scalars_decoded':journal['field_scalars_decoded']}),flush=True)
    if len(journal['requests'])!=18 or any(r['status']!='parsed_and_diagnosed' for r in result['source_target_outcomes']):raise SystemExit(1)


if __name__=='__main__':main()
