"""Cloud-only Indian EUC daily profiles with fixed regional priors and persistence gates."""
import calendar
import copy
import hashlib
import json
import math
import signal
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime,timedelta
from pathlib import Path
import collect_tao_pacific_euc_daily_depth_v1 as frozen

ROOT=Path(__file__).resolve().parents[1]
OP='research/indian-euc-rama-2005-depth-operator-v1.json'
CONTEXT='research/indian-euc-rama-2005-depth-source-context-v1.json'
METADATA='research/source-data/tao-pacific-euc-daily-depth-v1/metadata.raw'
OLD_JOURNAL='research/source-data/tao-pacific-euc-daily-depth-v1/journal.json'
OLD_PLAN='research/source-data/tao-pacific-euc-direct-source-v2/field-plan.json'
DIRECT='https://coastwatch.pfeg.noaa.gov/erddap/tabledap/pmelTaoDyAdcp.csv?'


def plan():
    output=[]
    for lon in [90,80.5]:
        for month in [2,3,4,5]:
            days=list(range(1,calendar.monthrange(2005,month)[1]+1)) if lon==90 else [14,15,16]
            dates=[f'2005-{month:02d}-{day:02d}T12:00:00Z' for day in days]
            query=','.join(frozen.FIELDS)+f'&longitude={lon}&latitude=0&time>={dates[0]}&time<={dates[-1]}&depth>=40&depth<=300&orderByClosest("station,time,depth/10")'
            output.append({'target_id':f'indian-field-{len(output):02d}','nominal_longitude':lon,'times_utc':dates,
                           'sampling_role':'continuous_daily_window' if lon==90 else 'sparse_comparison_only',
                           'url':DIRECT+urllib.parse.quote(query,safe=',&=():/'),
                           'cap_bytes':125000 if lon==90 else 50000,'maximum_rows':len(dates)*30,
                           'reserved_numeric_scalars':len(dates)*30*6})
    return output


def preflight(root=ROOT):
    targets=plan();old=json.loads((root/OLD_PLAN).read_bytes())
    if {t['url'] for t in targets}&{t['url'] for t in old} or {t['nominal_longitude'] for t in targets}&{t['nominal_longitude'] for t in old}:
        raise ValueError('New independent current programme must be geographically disjoint from all retained Pacific targets')
    if len(targets)!=8 or sum(len(t['times_utc']) for t in targets)!=132 or sum(t['reserved_numeric_scalars'] for t in targets)!=23760:
        raise ValueError('Fixed all-site/all-month source reserve cannot reset')
    raw=(root/METADATA).read_bytes();journal=json.loads((root/OLD_JOURNAL).read_bytes())
    if hashlib.sha256(raw).hexdigest()!=journal['requests'][0]['sha256']:raise ValueError('Exact prior metadata bytes required')
    return targets,frozen.metadata(raw)


def layer(z,u,threshold):
    original=frozen.connected_layer(z,u,threshold,(60,160))
    if 'core_index' not in original:return original
    seed=original['core_index'];lo=hi=seed
    while lo>0 and z[lo]-z[lo-1]<=15:lo-=1
    while hi+1<len(z) and z[hi+1]-z[hi]<=15:hi+=1
    if lo==hi:
        result={'threshold_m_s':threshold,'core_index':seed,'core_depth_m':z[seed],'core_velocity_m_s':u[seed],
                'upper_depth_m':None,'lower_depth_m':None,'layer_thickness_m':None,
                'upper_status':'censored_at_returned_depth_gap','lower_status':'censored_at_returned_depth_gap',
                'status':'unresolved_connected_layer_boundary'}
    else:
        result=frozen.connected_layer(z[lo:hi+1],u[lo:hi+1],threshold,(z[seed],z[seed]));result['core_index']=seed
        for side,gapped in [('upper',lo>0),('lower',hi+1<len(z))]:
            if gapped and result[side+'_status']=='censored_at_sample_domain_edge':result[side+'_status']='censored_at_returned_depth_gap'
        if result['status']=='resolved_connected_model_threshold_layer':result['status']='resolved_connected_observed_daily_mean_threshold_layer'
    result.update(core_search_depth_interval_m=[60,160],core_search_window_edge=z[seed] in [60,160],
                  source_sampling='original_rows_near10m_not_all_original_instrument_bins',
                  between_retained_levels_assumption='piecewise_linear_no_unobserved_reversals')
    return result


def profile(t,target,station=None,z=None,raw_u=None,quality=None):
    z=[] if z is None else z;raw_u=[] if raw_u is None else raw_u;quality=[] if quality is None else quality
    u=[frozen.decode(a,q) for a,q in zip(raw_u,quality)]
    contexts=[layer(z,u,threshold) for threshold in [.05,.1,.2]] if len(z)>=2 else []
    primary=contexts[1] if contexts else None
    interior=bool(primary and 'core_index' in primary and not primary.get('core_search_window_edge',True))
    by_depth=dict(zip(z,u));upper=[by_depth.get(d) for d in [40,50]]
    upper_reference=max(upper) if all(v is not None for v in upper) else None
    contrast=primary['core_velocity_m_s']-upper_reference if interior and upper_reference is not None else None
    candidate=bool(interior and contrast is not None and (contrast>=.1 or math.isclose(contrast,.1,rel_tol=0,abs_tol=1e-12)))
    reason=('observed_upper_reference_missing_or_quality_rejected' if upper_reference is None else
            'no_interior_qualifying_core' if not interior else
            'insufficient_observed_subsurface_contrast' if not candidate else 'operational_daily_subsurface_candidate')
    station=station or {'array':None,'station':None,'longitude':target['nominal_longitude'],'latitude':0}
    return {'target_id':target['target_id'],'time_center_utc':t,
            'provider_averaging_interval_utc':{'start':t[:10]+'T00:00:00Z','end_exclusive':(datetime.fromisoformat(t[:10])+timedelta(days=1)).date().isoformat()+'T00:00:00Z'},
            'nominal_station':station,'sampling_role':target['sampling_role'],
            'source_status':'source_profile_returned' if z else 'not_attempted',
            'source_depths_m':z,'source_u_cm_s':[a if math.isfinite(a) and abs(a)<1e34 else None for a in raw_u],
            'source_u_quality':[q if math.isfinite(q) and abs(q)<1e34 else None for q in quality],
            'accepted_eastward_velocity_m_s':u,'threshold_contexts':contexts,
            'primary_core_window_interior':interior,
            'primary_lower_isotach_depth_m':primary['lower_depth_m'] if interior else None,
            'primary_threshold_layer_span_m':primary['layer_thickness_m'] if interior else None,
            'observed_upper_reference_depths_m':[40,50],'observed_upper_reference_max_m_s':upper_reference,
            'operational_core_upper_reference_contrast_m_s':contrast,'operational_daily_context_candidate':candidate,
            'operational_daily_context_status':reason,'persistent_daily_context_qualified':None,
            'physical_current_identity_independently_verified':False,'true_surface_comparison_verified':False,
            'thermocline_membership_independently_verified':False,'daily_underlying_sample_coverage_verified':False,
            'mean_field_depth_is_mean_instantaneous_depth':False,'physical_current_thickness_m':None,
            'annual_range_m':None,'volume_m3':None}


def parse_patch(raw,target):
    rows=frozen.table(raw,frozen.FIELDS,frozen.UNITS,target['maximum_rows'])
    identifiers={(r['array'],r['station']) for r in rows}
    if len(identifiers)>1 or any(not a or not s for a,s in identifiers):raise ValueError('One returned station/array pair required')
    a,s=next(iter(identifiers)) if identifiers else (None,None)
    station={'array':a,'station':s,'longitude':target['nominal_longitude'],'latitude':0}
    groups={t:[] for t in target['times_utc']};seen=set()
    for r in rows:
        z=float(r['depth']);t=r['time']
        if float(r['longitude'])!=target['nominal_longitude'] or float(r['latitude'])!=0 or t not in groups or not 40<=z<=300:
            raise ValueError('Exact planned nominal site/day/reliable depth domain required')
        if (t,z) in seen:raise ValueError('Duplicate source point/time row')
        seen.add((t,z));groups[t].append((z,float(r['u_1205']),float(r['QU_5205'])))
    output=[]
    for t,values in groups.items():
        values.sort()
        if len(values)>30:raise ValueError('Thirty-level regional bound and original forty-level ceiling cannot expand')
        p=profile(t,target,station,[v[0] for v in values],[v[1] for v in values],[v[2] for v in values])
        if not values:p['source_status']='no_source_rows_for_predeclared_day'
        output.append(p)
    return output,len(rows)*6


def mark_persistence(profiles):
    runs=[];pending=[]
    def finish():
        if len(pending)>=31:
            for p in pending:p['persistent_daily_context_qualified']=True
            runs.append({'nominal_longitude':90,'start_date':pending[0]['time_center_utc'][:10],
                         'end_date':pending[-1]['time_center_utc'][:10],'successive_provider_daily_labels':len(pending),
                         'physical_continuous_presence_verified':False,'named_current_identity_independently_verified':False})
        pending.clear()
    for p in profiles:
        if p['nominal_station']['longitude']!=90:
            p.update(persistent_daily_context_qualified=None,persistence_status='unassessed_sparse_comparison_sampling')
        else:p.update(persistent_daily_context_qualified=False,persistence_status='continuous_daily_window_operational_test')
    days=sorted([p for p in profiles if p['nominal_station']['longitude']==90],key=lambda p:p['time_center_utc'])
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
    if op['maximum_http_requests']!=8 or op['global_scalar_reserve']!=24760 or op['maximum_profiles']!=132 or op['programme_deadline_seconds']!=210:
        raise ValueError('Frozen all-site/all-month programme reserve required')
    targets,metadata=preflight()
    folder=ROOT/'indian-euc-rama-2005-depth-v1';folder.mkdir(exist_ok=False)
    journal={'schema':'osw.indian-euc-rama2005-source-journal.v1','operator_file':OP,
             'operator_sha256':hashlib.sha256((ROOT/OP).read_bytes()).hexdigest(),
             'requests':[],'total_body_bytes':0,'maximum_requests':8,'maximum_attempts_per_target':1,
             'global_field_scalar_reserve':23760,'metadata_coordinate_scalar_reserve':1000,
             'global_scalar_cap':250000,'field_scalars_decoded':0,
             'field_decode_counter_scope':'successfully_parsed_patches_only_global_reserve_also_covers_failed_derivations',
             'metadata_reused_file':METADATA,'metadata_reused_sha256':hashlib.sha256((ROOT/METADATA).read_bytes()).hexdigest(),
             'prior_pacific_programme_budget_unchanged':True,'producer_finalized_before_artifact_upload':False}
    results={'schema':'osw.indian-euc-rama2005-depth.v1','entity_id':'current:indian-equatorial-undercurrent',
             'metadata':metadata,'source_context_file':CONTEXT,'source_context_sha256':hashlib.sha256((ROOT/CONTEXT).read_bytes()).hexdigest(),
             'credit':'Modified NOAA/PMEL GTMBA daily ADCP observations accessed at NOAA ERD; original values, quality and nominal coordinates retained.',
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
            if len(journal['requests'])>=8 or journal['total_body_bytes']+target['cap_bytes']>900000:raise ValueError('Global programme request/body budget exhausted')
            raw=frozen.acquire(target,folder,journal,opener,deadline)
            if raw is None:
                attempted=any(r['target_id']==target['target_id'] for r in journal['requests'])
                outcome['status']='attempted_transport_failure_no_retry' if attempted else 'not_attempted_deadline'
                for t in target['times_utc']:results['profiles'][positions[target['target_id'],t]]['source_status']=outcome['status']
                if journal['requests'] and journal['requests'][-1].get('source_http_status') in [301,302,303,307,308]:break
                if time.monotonic()+26>deadline:break
                continue
            try:
                values,numeric=parse_patch(raw,target);journal['field_scalars_decoded']+=numeric
                if journal['field_scalars_decoded']>23760:raise ValueError('Global all-month scalar reserve exhausted')
                for p in values:results['profiles'][positions[p['target_id'],p['time_center_utc']]]=p
                outcome['status']='parsed_and_diagnosed';journal['requests'][-1]['derivation_status']='parsed_and_diagnosed'
            except Exception as error:
                outcome.update(status='derivation_failed_retained_bytes_no_replay',error_type=type(error).__name__,error_summary=str(error)[:240])
                journal['requests'][-1]['derivation_status']=outcome['status']
                for t in target['times_utc']:results['profiles'][positions[target['target_id'],t]]['source_status']=outcome['status']
            frozen.atomic(folder/'journal.json',frozen.encoded(journal));frozen.atomic(folder/'profiles.json',frozen.encoded(results))
            print(json.dumps({'target':target['target_id'],'status':outcome['status']}),flush=True)
        results['status']='all_planned_targets_attempted' if len(journal['requests'])==8 else 'partial_programme_no_retry'
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
    if len(journal['requests'])!=8 or any(r['status']!='parsed_and_diagnosed' for r in results['target_outcomes']):raise SystemExit(1)


if __name__=='__main__':main()
