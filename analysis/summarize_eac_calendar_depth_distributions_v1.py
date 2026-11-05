"""Calendar-month distributions of already derived EAC monthly depth descriptors."""
import copy,csv,hashlib,io,json,math,signal,socket,statistics
from collections import Counter
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OP='research/eac-calendar-depth-distribution-operator-v1.json'
SOURCE='research/source-data/eac-chandler-seasonal-depth-v1/candidate.json'
YEARS=list(range(2004,2020))
THRESHOLDS=[0.0,0.05,0.1]
RESOLVED='resolved_adjacent_level_crossing'
UNRESOLVED={'right_censored_at_native_domain_end','unknown_gap_after_core','threshold_not_exceeded','no_core','unknown_axis_outside_EAC_gate'}


def finite(x):return type(x) in (int,float) and math.isfinite(x)


def descriptor(record,threshold):
    derived=record.get('derived',{})
    if record['status']!='axis_within_EAC_gate':return {'status':'unknown_axis_outside_EAC_gate','depth_m':None}
    if derived.get('status')=='unknown_no_supported_poleward_core':return {'status':'no_core','depth_m':None}
    raw=copy.deepcopy(derived['crossings'][str(threshold)]);status=raw['status'];value=raw.get('depth_m')
    if status==RESOLVED:
        bracket=raw['bracketing_native_depths_m']
        if not finite(value) or not 0<=value<=1975 or len(bracket)!=2 or not all(finite(v) for v in bracket) or not 0<=bracket[0]<bracket[1]<=1975 or not bracket[0]<=value<=bracket[1]:raise ValueError('Exact finite adjacent-level derived crossing in retained native domain required')
    elif status in UNRESOLVED:
        if value is not None:raise ValueError('Unresolved/censored/threshold-not-exceeded descriptor cannot have numeric depth')
        if 'last_supported_depth_m' in raw and (not finite(raw['last_supported_depth_m']) or not 0<=raw['last_supported_depth_m']<=1975):raise ValueError('Valid source support limit required,not physical current bottom')
    else:raise ValueError('Unknown crossing status must not be silently dropped')
    return raw


def summarize(cases,mean_descriptor,expected_years):
    if len(cases)!=len(expected_years) or sorted(c['source_year'] for c in cases)!=expected_years or len({c['source_date'] for c in cases})!=len(cases):raise ValueError('All exact cohort years,unique monthly dates and fixed denominator required')
    statuses=Counter(c['descriptor']['status'] for c in cases)
    resolved=[c for c in cases if c['descriptor']['status']==RESOLVED]
    values=[c['descriptor']['depth_m'] for c in resolved]
    if any(not finite(v) for v in values):raise ValueError('Finite derived crossing values required')
    complete=len(values)==len(expected_years)
    round6=lambda v:None if v is None else round(v,6)
    avg=math.fsum(values)/len(values) if values else None
    interval=[min(values),max(values)] if values else None
    old=copy.deepcopy(mean_descriptor);old_depth=old.get('depth_m') if old.get('status')==RESOLVED else None
    if old_depth is not None and not finite(old_depth):raise ValueError('Finite original mean-profile crossing required')
    difference=round6(avg-old_depth) if complete and old_depth is not None else None
    return {'expected_years':list(expected_years),'expected_monthly_estimates':len(expected_years),'status_counts':dict(sorted(statuses.items())),
      'resolved_crossing_count':len(values),'right_censored_count':statuses.get('right_censored_at_native_domain_end',0),
      'gap_or_no_core_or_axis_unknown_count':sum(statuses.get(k,0) for k in ['unknown_gap_after_core','no_core','unknown_axis_outside_EAC_gate']),
      'threshold_not_exceeded_count':statuses.get('threshold_not_exceeded',0),
      'resolved_years':[c['source_year'] for c in resolved],
      'unresolved_cases':[{'source_date':c['source_date'],'source_year':c['source_year'],'descriptor':copy.deepcopy(c['descriptor'])} for c in cases if c['descriptor']['status']!=RESOLVED],
      'resolved_subset_depth_min_max_m':interval,'resolved_subset_arithmetic_mean_depth_m':round6(avg),
      'resolved_subset_median_depth_m':round6(statistics.median(values)) if values else None,
      'resolved_subset_statistics_are_conditional':not complete,'all_cohort_year_crossings_resolved':complete,
      'complete_cohort_calendar_month_reconstructed_depth_range_m':interval if complete else None,
      'original_mean_velocity_profile_crossing':old,'same_cohort_mean_of_crossing_depths_minus_crossing_of_mean_profile_m':difference,
      'operator_comparison_status':'COMPLETE_COHORT_DISTINCT_NONCOMMUTING_OPERATORS' if difference is not None else 'COMPARISON_UNRESOLVED_DO_NOT_SUBSTITUTE_FINITE_SUBSET_FOR_FULL_COHORT',
      'range_is_confidence_interval':False,'range_is_instantaneous_annual_extrema':False,'monthly_estimates_assumed_independent':False,
      'physical_depth_uncertainty_m':None,'physical_thickness_m':None,'annual_depth_range_m':None,'whole_current_depth_m':None,
      'physical_current_bottom_established':False,'volume_eligible':False,'physical_state_join_eligible':False,'reference_route_projection_eligible':False,'seasonal_playback_eligible':False}


def numeric_scalar_count(value):
    total=0;stack=[value]
    while stack:
        v=stack.pop()
        if isinstance(v,dict):stack.extend(v.values())
        elif isinstance(v,list):stack.extend(v)
        elif type(v) in (int,float):
            if not finite(v):raise ValueError('Strict finite retained numeric values required')
            total+=1
    return total


def build(root=ROOT):
    reader=lambda p:(root/p).read_bytes();read=lambda p:json.loads(reader(p));op=read(OP)
    for p,h in op['input_sha256'].items():
        if hashlib.sha256(reader(p)).hexdigest()!=h:raise ValueError('Pinned existing descriptor source changed:'+p)
    if op['cohort_years']!=YEARS or op['thresholds_m_s']!=THRESHOLDS or op['new_native_profiles_selected_allowed']!=0 or op['new_provider_requests_allowed']!=0:raise ValueError('Whole original descriptor cohort,not new profile sampling or budget reset')
    raw=reader(SOURCE)
    if len(raw)>800000:raise ValueError('Bounded retained typed descriptor packet required')
    source=json.loads(raw);scalar_count=numeric_scalar_count(source)
    if scalar_count>50000 or source['schema']!='osw.eac-chandler-seasonal-depth.v1' or source['entity_id']!='current:east-australian' or source['monthly_profile_count']!=192:raise ValueError('Original bounded192-month derived packet required')
    records=source['records']
    if len(records)!=192:raise ValueError('All existing descriptor records required')
    dates=[]
    for r in records:
        d=date.fromisoformat(r['date'])
        if r['calendar_month']!=d.month:raise ValueError('Original calendar month must match actual source date')
        dates.append((d.year,d.month))
    if sorted(dates)!=[(y,m) for y in YEARS for m in range(1,13)] or len(set(dates))!=192:raise ValueError('Exact16year by12month descriptor lattice required')
    means=source['monthly_climatologies']
    if len(means)!=12 or sorted(m['calendar_month'] for m in means)!=list(range(1,13)):raise ValueError('All12 original full-cohort mean-profile comparisons required')
    means_by_month={m['calendar_month']:(i,m) for i,m in enumerate(means)}
    cases=[]
    for index,r in enumerate(records):
        d=date.fromisoformat(r['date'])
        for t in THRESHOLDS:
            cases.append({'source_date':r['date'],'source_year':d.year,'calendar_month':d.month,'source_threshold_m_s':t,
              'source_axis_status':r['status'],'source_axis_longitude_degrees_east':r.get('longitude'),'source_axis_latitude_degrees_north':r.get('latitude'),
              'source_descriptor_pointer':'/records/'+str(index)+'/derived/crossings/'+str(t),'descriptor':descriptor(r,t),
              'new_native_profile_selected':False,'new_independent_observation':False})
    summaries=[]
    for month in range(1,13):
        mean_index,mean=means_by_month[month]
        if mean['status']!='current_following_monthly_mean_profile' or mean['year_samples']!=16 or mean['years']!=[2004,2019]:raise ValueError('Original16year fixed-contributor mean statistic required')
        for t in THRESHOLDS:
            group=[c for c in cases if c['calendar_month']==month and c['source_threshold_m_s']==t]
            old_descriptor=copy.deepcopy(mean['derived']['crossings'].get(str(t),{'status':'no_core','depth_m':None}))
            row=summarize(group,old_descriptor,YEARS)
            if row['status_counts']!=dict(sorted(mean['individual_crossing_status_counts'][str(t)].items())):raise ValueError('Independent calendar status counts must reproduce frozen original audit')
            row.update(calendar_month=month,source_threshold_m_s=t,original_mean_profile_descriptor_pointer='/monthly_climatologies/'+str(mean_index)+'/derived/crossings/'+str(t),
              source_cases=[{'source_date':c['source_date'],'source_descriptor_pointer':c['source_descriptor_pointer']} for c in group])
            summaries.append(row)
    stats={'original_monthly_depth_descriptor_records':192,'calendar_month_threshold_summaries':len(summaries),'individual_threshold_cases':len(cases),
      'resolved_individual_crossings':sum(c['descriptor']['status']==RESOLVED for c in cases),
      'right_censored_individual_crossings':sum(c['descriptor']['status']=='right_censored_at_native_domain_end' for c in cases),
      'complete_cohort_month_threshold_ranges':sum(s['all_cohort_year_crossings_resolved'] for s in summaries),
      'conditional_finite_subset_month_threshold_summaries':sum(s['resolved_subset_statistics_are_conditional'] for s in summaries),
      'same_cohort_operator_comparisons':sum(s['same_cohort_mean_of_crossing_depths_minus_crossing_of_mean_profile_m'] is not None for s in summaries),
      'retained_typed_numeric_scalars':scalar_count,'new_native_profiles_selected':0,'new_native_ocean_arrays_decoded':0,'provider_requests':0,'new_independent_observations':0,'new_reference_inventory_rows':0}
    return {'schema':'osw.eac-calendar-depth-distributions.v1','status':'SOURCE_PERIOD_MONTHLY_RECONSTRUCTION_VARIABILITY_WITH_EXPLICIT_CENSORING',
      'source_file':SOURCE,'source_sha256':hashlib.sha256(raw).hexdigest(),'operator_file':OP,'operator_sha256':hashlib.sha256(reader(OP)).hexdigest(),
      'input_sha256':op['input_sha256'],'source_period_years':[2004,2019],'source_cohort_years':YEARS,'source_descriptor_statistic':'monthly_reconstructed_current_following_PX30_axis_lower_velocity_crossing',
      'source_definition':'Published2004-2019monthlyHRXBT/Argo/SLAreconstructions,statisticalextensionbelow800m,timeinvariantmeanreferencevelocitynear1000m. Original151-157Eaxisgate/nativecrossingmethod retained.1975mproductlimitnotphysicalbottom.',
      'operator_scope':'Aggregateexistingderivedcrossingmetadataonly;no velocity values or76levelprofiles analysed,no native archive rereads/newprofile selection. All192 existing descriptors and source status denominators retained in one cohort,no permonth/filebudgetreset.',
      'interpretation':'Resolved-subset statistics are conditional whenever any year is censored/unknown/not-exceeding. Complete source-period month ranges require all16 resolved. Mean of individual crossing depths and crossing of mean velocity profile are distinct operators; compare only complete same-cohort cases. Neither range is instantaneous annual extrema,confidence bounds or whole-current physical thickness.',
      'counts':stats,'individual_cases':cases,'calendar_month_summaries':summaries,'source_full_native_array_reads':0,
      'retained_packet_scalar_cap':50000,'global_scalar_cap':250000,'new_decoded_native_bytes':0,'prior_legacy_native_acquisition_replayed':False,
      'source_legacy_acquisition_under_new_native_caps_claimed':False,'existing_reference_inventory_rows_unchanged':859,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(rows):
    fields=['calendar_month','source_threshold_m_s','expected_monthly_estimates','resolved_crossing_count','right_censored_count','threshold_not_exceeded_count','resolved_subset_arithmetic_mean_depth_m','resolved_subset_median_depth_m','resolved_subset_min_depth_m','resolved_subset_max_depth_m','all_cohort_year_crossings_resolved','original_mean_profile_crossing_m','same_cohort_operator_difference_m','range_is_confidence_interval']
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');writer.writeheader()
    for s in rows:
        row={k:s.get(k) for k in fields};span=s['resolved_subset_depth_min_max_m'];row.update(resolved_subset_min_depth_m=span[0] if span else None,resolved_subset_max_depth_m=span[1] if span else None,
          original_mean_profile_crossing_m=s['original_mean_velocity_profile_crossing'].get('depth_m'),same_cohort_operator_difference_m=s['same_cohort_mean_of_crossing_depths_minus_crossing_of_mean_profile_m'])
        writer.writerow(row)
    return out.getvalue().encode()


def main():
    def denied(*a,**k):raise RuntimeError('Descriptor aggregation forbids provider/source replay')
    def stopped(*a):raise SystemExit('Stopped retained descriptor producer')
    socket.socket=denied;socket.create_connection=denied
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stopped)
    signal.alarm(90);report=build();folder=ROOT/'eac-calendar-depth-distributions-v1';folder.mkdir(exist_ok=False)
    raw=(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode();table=csv_bytes(report['calendar_month_summaries'])
    if len(raw)+len(table)>=2400000:raise ValueError('Fixed scientific output chunk cap exceeded')
    (folder/'distributions.json').write_bytes(raw);(folder/'distributions.csv').write_bytes(table);signal.alarm(0)
    print(json.dumps(report['counts']),flush=True)

if __name__=='__main__':main()
