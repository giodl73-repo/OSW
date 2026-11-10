"""Independent2006positive-IOD event; frozen regional kernel and transport, one source pass."""
import hashlib,json,signal,time,urllib.error,urllib.parse,urllib.request
from datetime import datetime,timedelta
from pathlib import Path
import collect_indian_euc_rama_2005_depth_v1 as prior
import indian_euc_observed_profile_checks_v1 as checks
frozen=prior.frozen
profile=prior.profile
parse_patch=prior.parse_patch
ROOT=Path(__file__).resolve().parents[1]
OP='research/indian-euc-rama-2006-depth-operator-v1.json'
CONTEXT='research/indian-euc-rama-2006-depth-source-context-v1.json'
METADATA=prior.METADATA


def plan():
    targets=[];start=datetime(2006,8,1)
    for patch in range(30):
        dates=[(start+timedelta(days=3*patch+i)).date().isoformat()+'T12:00:00Z' for i in range(3)]
        query=','.join(frozen.FIELDS)+f'&longitude=80.5&latitude=0&time>={dates[0]}&time<={dates[-1]}&depth>=40&depth<=300&orderByClosest("station,time,depth/10")'
        targets.append({'target_id':f'iod2006-field-{patch:02d}','nominal_longitude':80.5,'times_utc':dates,
                        'sampling_role':'continuous_daily_window','url':prior.DIRECT+urllib.parse.quote(query,safe=',&=():/'),
                        'cap_bytes':20000,'maximum_rows':90,'reserved_numeric_scalars':540})
    return targets


def preflight(root=ROOT):
    targets=plan()
    older=[json.loads((root/p).read_bytes()) for p in [prior.OLD_PLAN,'research/source-data/indian-euc-rama-2005-depth-v1/field-plan.json']]
    urls={t['url'] for case in older for t in case}
    keys={(t['nominal_longitude'],d) for case in older for t in case for d in t['times_utc']}
    if any(t['url'] in urls or any((t['nominal_longitude'],d) in keys for d in t['times_utc']) for t in targets):raise ValueError('No prior field target or geotemporal sample may repeat')
    if len(targets)!=30 or sum(len(t['times_utc']) for t in targets)!=90 or sum(t['reserved_numeric_scalars'] for t in targets)!=16200:raise ValueError('Fixed all-event budget cannot reset')
    raw=(root/METADATA).read_bytes();journal=json.loads((root/prior.OLD_JOURNAL).read_bytes())
    if hashlib.sha256(raw).hexdigest()!=journal['requests'][0]['sha256']:raise ValueError('Exact cached metadata required')
    return targets,frozen.metadata(raw)


def mark_persistence(profiles):
    if any(p['nominal_station']['longitude']!=80.5 or p['sampling_role']!='continuous_daily_window' for p in profiles):raise ValueError('Only this continuous80.5E cohort may qualify')
    runs=[];pending=[]
    def finish():
        if len(pending)>=31:
            for p in pending:p['persistent_daily_context_qualified']=True
            runs.append({'nominal_longitude':80.5,'start_date':pending[0]['time_center_utc'][:10],
                         'end_date':pending[-1]['time_center_utc'][:10],'successive_provider_daily_labels':len(pending),
                         'physical_continuous_presence_verified':False,'named_current_identity_independently_verified':False})
        pending.clear()
    for p in profiles:
        if p['nominal_station']['longitude']!=80.5:
            p.update(persistent_daily_context_qualified=None,persistence_status='unassessed_sparse_comparison_sampling')
        else:p.update(persistent_daily_context_qualified=False,persistence_status='continuous_daily_window_operational_test')
    days=sorted([p for p in profiles if p['nominal_station']['longitude']==80.5],key=lambda p:p['time_center_utc'])
    if len({p['time_center_utc'] for p in days})!=len(days):raise ValueError('Unique continuous-site daily labels required')
    for p in days:
        if not p['operational_daily_context_candidate']:finish();continue
        if pending and datetime.fromisoformat(p['time_center_utc'].replace('Z','+00:00'))-datetime.fromisoformat(pending[-1]['time_center_utc'].replace('Z','+00:00'))!=timedelta(days=1):finish()
        pending.append(p)
    finish()
    for p in profiles:
        p['persistent_context_lower_isotach_depth_m']=p['primary_lower_isotach_depth_m'] if p['persistent_daily_context_qualified'] is True else None
    return runs

def main():
    op=json.loads((ROOT/OP).read_bytes())
    for f,h in op['input_sha256'].items():
        if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=h:raise ValueError('Pinned independent-case input changed:'+f)
    if op['maximum_http_requests']!=30 or op['global_scalar_reserve']!=19144 or op['maximum_profiles']!=90 or op['programme_deadline_seconds']!=210:
        raise ValueError('Frozen all-site/all-month programme reserve required')
    targets,metadata=preflight()
    prior_audit=checks.reconstruct_2005(ROOT)
    folder=ROOT/'indian-euc-rama-2006-depth-v1';folder.mkdir(exist_ok=False)
    journal={'schema':'osw.indian-euc-rama2006-source-journal.v1','operator_file':OP,'global_scalar_reserve':19144,'global_node_reserve':4500,
             'operator_sha256':hashlib.sha256((ROOT/OP).read_bytes()).hexdigest(),
             'requests':[],'total_body_bytes':0,'maximum_requests':30,'maximum_attempts_per_target':1,
             'global_field_scalar_reserve':16200,'prior_retained_reconstruction_scalar_reserve':1944,'metadata_coordinate_scalar_reserve':1000,
             'global_scalar_cap':250000,'field_scalars_decoded':0,
             'field_decode_counter_scope':'successfully_parsed_patches_only_global_reserve_also_covers_failed_derivations',
             'metadata_reused_file':METADATA,'metadata_reused_sha256':hashlib.sha256((ROOT/METADATA).read_bytes()).hexdigest(),
             'prior_pacific_programme_budget_unchanged':True,'prior_indian2005_eight_attempts_unchanged':True,'producer_finalized_before_artifact_upload':False}
    results={'schema':'osw.indian-euc-rama2006-depth.v1','entity_id':'current:indian-equatorial-undercurrent',
             'metadata':metadata,'source_context_file':CONTEXT,'source_context_sha256':hashlib.sha256((ROOT/CONTEXT).read_bytes()).hexdigest(),
             'credit':'Modified NOAA/PMEL GTMBA daily ADCP observations accessed at NOAA ERD; original values, quality and nominal coordinates retained.',
             'retained_2005_independent_audit':prior_audit,
             'profiles':[profile(t,target) for target in targets for t in target['times_utc']],
             'target_outcomes':[{'target_id':t['target_id'],'status':'not_attempted'} for t in targets],
             'runtime_changed':False,'full_goal_complete':False,'reference_inventory_admission_performed':False}
    positions={(p['target_id'],p['time_center_utc']):i for i,p in enumerate(results['profiles'])}
    frozen.atomic(folder/'field-plan.json',frozen.encoded(targets));frozen.atomic(folder/'journal.json',frozen.encoded(journal))
    deadline=time.monotonic()+210
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,frozen.alarm)
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*a,**k):return None
    direct_open=urllib.request.build_opener(NoRedirect()).open
    def opener(request,timeout):
        try:return direct_open(request,timeout=timeout)
        except urllib.error.HTTPError as error:
            journal['requests'][-1]['source_http_status']=error.code
            if error.headers.get('Location'):journal['requests'][-1]['source_redirect_location_not_followed']=error.headers['Location'][:2048]
            raise
    try:
        for target,outcome in zip(targets,results['target_outcomes']):
            if len(journal['requests'])>=30 or journal['total_body_bytes']+target['cap_bytes']>650000:raise ValueError('Global programme request/body budget exhausted')
            raw=frozen.acquire(target,folder,journal,opener,deadline)
            if raw is None:
                attempted=any(r['target_id']==target['target_id'] for r in journal['requests'])
                outcome['status']='attempted_transport_failure_no_retry' if attempted else 'not_attempted_deadline'
                for t in target['times_utc']:results['profiles'][positions[target['target_id'],t]]['source_status']=outcome['status']
                if journal['requests'] and journal['requests'][-1].get('source_http_status') in [301,302,303,307,308]:break
                if time.monotonic()+26>deadline:break
                continue
            try:
                values,numeric=parse_patch(raw,target)
                for p in values:checks.verify_indian_profile(p)
                journal['field_scalars_decoded']+=numeric
                if journal['field_scalars_decoded']>16200:raise ValueError('Global all-month scalar reserve exhausted')
                for p in values:results['profiles'][positions[p['target_id'],p['time_center_utc']]]=p
                outcome['status']='parsed_and_diagnosed';journal['requests'][-1]['derivation_status']='parsed_and_diagnosed'
            except Exception as error:
                outcome.update(status='derivation_failed_retained_bytes_no_replay',error_type=type(error).__name__,error_summary=str(error)[:240])
                journal['requests'][-1]['derivation_status']=outcome['status']
                for t in target['times_utc']:results['profiles'][positions[target['target_id'],t]]['source_status']=outcome['status']
            frozen.atomic(folder/'journal.json',frozen.encoded(journal));frozen.atomic(folder/'profiles.json',frozen.encoded(results))
            print(json.dumps({'target':target['target_id'],'status':outcome['status']}),flush=True)
        results['status']='all_planned_targets_attempted' if len(journal['requests'])==30 else 'partial_programme_no_retry'
    except BaseException as error:
        results.update(status='programme_interrupted_no_retry',error_type=type(error).__name__,error_summary=str(error)[:240])
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        results['operational_persistence_runs']=mark_persistence(results['profiles'])
        journal['producer_finalized_before_artifact_upload']=True
        journal['field_decode_counter_is_complete']=all(r['status']=='parsed_and_diagnosed' for r in results['target_outcomes'])
        results['counts']={'source_request_attempts':len(journal['requests']),'expected_profile_outcomes':len(results['profiles']),
            'profiles_with_source_rows':sum(bool(p['source_depths_m']) for p in results['profiles']),
            'profiles_with_any_quality_accepted_velocity':sum(any(v is not None for v in p['accepted_eastward_velocity_m_s']) for p in results['profiles']),
            'finite_primary_lower_threshold_depths':sum(p['primary_lower_isotach_depth_m'] is not None for p in results['profiles']),
            'finite_primary_threshold_layer_spans':sum(p['primary_threshold_layer_span_m'] is not None for p in results['profiles']),
            'operational_daily_context_candidates':sum(p['operational_daily_context_candidate'] for p in results['profiles']),
            'persistent_daily_context_profiles':sum(p['persistent_daily_context_qualified'] is True for p in results['profiles']),
            'persistent_context_finite_lower_depths':sum(p['persistent_context_lower_isotach_depth_m'] is not None for p in results['profiles'])}
        frozen.atomic(folder/'journal.json',frozen.encoded(journal));frozen.atomic(folder/'profiles.json',frozen.encoded(results))
        if sum(p.stat().st_size for p in folder.iterdir())>=2400000:raise ValueError('Scientific programme output cap exceeded')
        print(json.dumps({'status':results['status'],'counts':results['counts'],'field_scalars_decoded':journal['field_scalars_decoded'],'operational_runs':results['operational_persistence_runs']}),flush=True)
    if len(journal['requests'])!=30 or any(r['status']!='parsed_and_diagnosed' for r in results['target_outcomes']):raise SystemExit(1)


if __name__=='__main__':main()
