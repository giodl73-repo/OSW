"""Kuroshio calendar depth distributions with explicit PX40 observation-era provenance."""
import copy,csv,hashlib,io,json,math,signal,socket,statistics
import summarize_eac_calendar_depth_distributions_v1 as shared
from collections import Counter
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OP='research/kuroshio-calendar-depth-distribution-operator-v1.json'
SOURCE='research/source-data/kuroshio-chandler-seasonal-depth-v1/candidate.json'
YEARS=list(range(2004,2020))
THRESHOLDS=[0.0,0.05,0.1]
RESOLVED='resolved_adjacent_level_crossing'
UNRESOLVED={'right_censored_at_native_domain_end','unknown_gap_after_core','threshold_not_exceeded','no_core','unknown_axis_outside_KUROSHIO_gate'}


def finite(x):return type(x) in (int,float) and math.isfinite(x)


def descriptor(record,threshold):
    derived=record.get('derived',{})
    if record['status'] not in ['axis_within_KUROSHIO_gate','unknown_axis_outside_KUROSHIO_gate']:raise ValueError('No EAC or Kuroshio Extension gate substitution')
    if record['status']!='axis_within_KUROSHIO_gate':return {'status':'unknown_axis_outside_KUROSHIO_gate','depth_m':None}
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
    allowed=UNRESOLVED|{RESOLVED}
    if any(c['descriptor']['status'] not in allowed for c in cases):raise ValueError('Kuroshio-specific original descriptor statuses required')
    result=shared.summarize(cases,mean_descriptor,expected_years)
    # Shared arithmetic is current-neutral; preserve this source's own axis enum.
    result['gap_or_no_core_or_axis_unknown_count']=sum(result['status_counts'].get(k,0) for k in ['unknown_gap_after_core','no_core','unknown_axis_outside_KUROSHIO_gate'])
    return result


def source_era(year):
    if type(year)!=int or year not in YEARS:raise ValueError('Exact source cohort year required')
    return 'BEFORE_LOCAL_PX40_HRXBT_OCCUPATIONS' if year<2012 else 'LOCAL_PX40_HRXBT_ERA_CONTEXT_NOT_PER_MONTH_OBSERVATION_PROOF'


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
    facts=read('research/kuroshio-chandler-seasonal-depth-source-facts-v1.json')
    if facts['HRXBT_occupation_years']!=[2012,2019] or facts['reconstructed_product_years']!=[2004,2019] or facts['statistical_deep_extension_below_m']!=600 or facts['source_transect']!='PX40_Yokohama_Honolulu':raise ValueError('Original PX40 reconstruction and observation-era context required')
    velmeta=source['source_metadata']['variable_attributes']['vel']
    if velmeta['positive']!='northward' or velmeta['units']!='m/s':raise ValueError('Original northward-positive reconstructed component, not EAC southward sign')
    if scalar_count>50000 or source['schema']!='osw.kuroshio-chandler-seasonal-depth.v1' or source['entity_id']!='current:kuroshio' or source['monthly_profile_count']!=192:raise ValueError('Original bounded192-month derived packet required')
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
        if r['status']=='axis_within_KUROSHIO_gate' and (not finite(r.get('longitude')) or not 138<=r['longitude']<=145):raise ValueError('Original Kuroshio source gate required,no axis relocation')
        for t in THRESHOLDS:
            cases.append({'source_date':r['date'],'source_year':d.year,'calendar_month':d.month,'source_threshold_m_s':t,
              'source_axis_status':r['status'],'source_axis_longitude_degrees_east':r.get('longitude'),'source_axis_latitude_degrees_north':r.get('latitude'),
              'source_descriptor_pointer':('/records/'+str(index)+'/derived/crossings/'+str(t)) if str(t) in r.get('derived',{}).get('crossings',{}) else None,'descriptor':descriptor(r,t),
              'source_record_pointer':'/records/'+str(index),'source_reconstruction_era':source_era(d.year),
              'individual_month_is_direct_PX40_HRXBT_measurement_verified':False,
              'new_native_profile_selected':False,'new_independent_observation':False})
    cohorts=[('reconstructed2004_2019',YEARS),('pre_local_HRXBT2004_2011',list(range(2004,2012))),('local_HRXBT_era_context2012_2019',list(range(2012,2020)))]
    summaries=[]
    for month in range(1,13):
        mean_index,mean=means_by_month[month]
        if mean['status']!='current_following_monthly_mean_profile' or mean['year_samples']!=16 or mean['years']!=[2004,2019]:raise ValueError('Original16year fixed-contributor mean statistic required')
        for t in THRESHOLDS:
            for cohort_id,cohort_years in cohorts:
                group=[c for c in cases if c['calendar_month']==month and c['source_threshold_m_s']==t and c['source_year'] in cohort_years]
                full=cohort_id=='reconstructed2004_2019'
                old_descriptor=copy.deepcopy(mean['derived']['crossings'].get(str(t),{'status':'no_core','depth_m':None})) if full else {'status':'cohort_specific_mean_velocity_profile_not_available','depth_m':None}
                row=summarize(group,old_descriptor,cohort_years)
                if full and row['status_counts']!=dict(sorted(mean['individual_crossing_status_counts'][str(t)].items())):raise ValueError('Full-cohort calendar statuses must reproduce frozen original audit')
                row.update(source_cohort_id=cohort_id,cohort_year_start=cohort_years[0],cohort_year_end=cohort_years[-1],calendar_month=month,source_threshold_m_s=t,
                  source_period_context='Full reconstruction mixes pre2012 and later localHRXBT-era contexts;neither is a set of independent direct monthly sections.' if full else ('Before direct localPX40HRXBT occupations;reconstructed fields.' if cohort_years[-1]<2012 else '2012-2019 localHRXBT-era context;per-month direct observational support not independently verified.'),
                  original_mean_profile_descriptor_pointer='/monthly_climatologies/'+str(mean_index)+'/derived/crossings/'+str(t) if full else None,
                  source_cases=[{'source_date':c['source_date'],'source_record_pointer':c['source_record_pointer'],'source_descriptor_pointer':c['source_descriptor_pointer'],'source_reconstruction_era':c['source_reconstruction_era']} for c in group],
                  source_mean_velocity_profile_available_for_exact_cohort=full,
                  source_support_era_split_is_climate_or_significance_test=False,
                  source_cohort_summaries_are_additive_independent_observations=False)
                summaries.append(row)
    stats={'original_monthly_depth_descriptor_records':192,'calendar_month_threshold_summaries':len(summaries),'full_period_month_threshold_summaries':sum(s['source_cohort_id']=='reconstructed2004_2019' for s in summaries),'era_month_threshold_summaries':sum(s['source_cohort_id']!='reconstructed2004_2019' for s in summaries),'individual_threshold_cases':len(cases),
      'resolved_individual_crossings':sum(c['descriptor']['status']==RESOLVED for c in cases),
      'right_censored_individual_crossings':sum(c['descriptor']['status']=='right_censored_at_native_domain_end' for c in cases),
      'complete_cohort_month_threshold_ranges':sum(s['all_cohort_year_crossings_resolved'] for s in summaries),
      'complete_full_period_month_threshold_ranges':sum(s['source_cohort_id']=='reconstructed2004_2019' and s['all_cohort_year_crossings_resolved'] for s in summaries),
      'complete_era_month_threshold_ranges':sum(s['source_cohort_id']!='reconstructed2004_2019' and s['all_cohort_year_crossings_resolved'] for s in summaries),
      'conditional_finite_subset_month_threshold_summaries':sum(s['resolved_subset_statistics_are_conditional'] for s in summaries),
      'same_cohort_operator_comparisons':sum(s['same_cohort_mean_of_crossing_depths_minus_crossing_of_mean_profile_m'] is not None for s in summaries),
      'retained_typed_numeric_scalars':scalar_count,'before_local_HRXBT_threshold_cases':sum(c['source_year']<2012 for c in cases),'later_HRXBT_era_threshold_cases':sum(c['source_year']>=2012 for c in cases),'new_native_profiles_selected':0,'new_native_ocean_arrays_decoded':0,'provider_requests':0,'new_independent_observations':0,'new_reference_inventory_rows':0}
    return {'schema':'osw.kuroshio-calendar-depth-distributions.v1','status':'SOURCE_PERIOD_AND_OBSERVATION_ERA_CONTEXT_DEPTH_DISTRIBUTIONS_WITH_CENSORING',
      'source_file':SOURCE,'source_sha256':hashlib.sha256(raw).hexdigest(),'operator_file':OP,'operator_sha256':hashlib.sha256(reader(OP)).hexdigest(),
      'input_sha256':op['input_sha256'],'source_period_years':[2004,2019],'source_cohort_years':YEARS,'current_entity_id':'current:kuroshio','positive_poleward_component':'source_northward_positive_cross_transect_velocity','local_HRXBT_occupation_years':[2012,2019],'source_descriptor_statistic':'monthly_reconstructed_current_following_PX40_axis_lower_velocity_crossing',
      'source_definition':'PublishedPX40monthlyArgo/SLA/HRXBTreconstruction2004-2019;localHRXBToccupations2012-2019. Before2012reconstruction is not direct localPX40HRXBTsampling. Deepstatisticalextensionbelow600m,timeinvariantmeanreferencevelocitynear1000m. Originalseparator-basednorthwardKuroshioselectionand138-145Egatepreserved;notKEinheritance.1975mproductlimitnotphysicalbottom.',
      'operator_scope':'Aggregateexistingderivedcrossingmetadataonly;no velocity values or76levelprofiles analysed,no native archive rereads/newprofile selection. All192existingdescriptors retained;full16year andtwo8yearera summaries reuse same cases,not additive independent observations. No8yearmeanofdepthscomparedto16yearmeanvelocityprofile,no permonth/filebudgetreset.',
      'interpretation':'Resolved-subset statistics are conditional whenever any year is censored/unknown/not-exceeding. Complete month ranges require every predeclared cohort year resolved:16 for full period,8 for each era context. Mean of individual crossing depths and crossing of mean velocity profile are distinct operators; compare only complete same-cohort cases. Neither range is instantaneous annual extrema,confidence bounds or whole-current physical thickness.',
      'counts':stats,'era_summaries_overlap_full_period_summaries':True,'era_subcohorts_disjoint_with_each_other':True,'era_split_is_source_support_context_not_trend_detection':True,'individual_cases':cases,'calendar_month_summaries':summaries,'source_full_native_array_reads':0,
      'retained_packet_scalar_cap':50000,'global_scalar_cap':250000,'new_decoded_native_bytes':0,'prior_legacy_native_acquisition_replayed':False,
      'source_legacy_acquisition_under_new_native_caps_claimed':False,'existing_reference_inventory_rows_unchanged':859,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(rows):
    fields=['source_cohort_id','cohort_year_start','cohort_year_end','calendar_month','source_threshold_m_s','expected_monthly_estimates','resolved_crossing_count','right_censored_count','threshold_not_exceeded_count','resolved_subset_arithmetic_mean_depth_m','resolved_subset_median_depth_m','resolved_subset_min_depth_m','resolved_subset_max_depth_m','all_cohort_year_crossings_resolved','original_mean_profile_crossing_m','same_cohort_operator_difference_m','range_is_confidence_interval']
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
    signal.alarm(90);report=build();folder=ROOT/'kuroshio-calendar-depth-distributions-v1';folder.mkdir(exist_ok=False)
    raw=(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode();table=csv_bytes(report['calendar_month_summaries'])
    if len(raw)+len(table)>=2400000:raise ValueError('Fixed scientific output chunk cap exceeded')
    (folder/'distributions.json').write_bytes(raw);(folder/'distributions.csv').write_bytes(table);signal.alarm(0)
    print(json.dumps(report['counts']),flush=True)

if __name__=='__main__':main()
