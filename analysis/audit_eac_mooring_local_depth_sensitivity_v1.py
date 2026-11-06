"""Conditional EAC local crossing sensitivity to source endpoint standard errors."""
import copy,csv,hashlib,io,itertools,json,math,signal,socket
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OP='research/eac-mooring-local-depth-sensitivity-operator-v1.json'
SOURCE='research/source-data/eac-mooring-depth-benchmark-v1/candidate.json'
THRESHOLDS=[0.05,0.1,0.2]
STATIONS=['NRSNSI','0500','2000','3200','4200','4700','4800']
DATES=['2022-01-15','2022-07-15']


def finite(x):return type(x) in (int,float) and math.isfinite(x)


def crossing(z,v,t):
    if len(z)!=2 or len(v)!=2 or not all(finite(x) for x in [*z,*v,t]) or not 0<=z[0]<z[1] or t<=0:raise ValueError('Two ascending finite source levels and finite velocity/cutoff required')
    if not v[0]>t>=v[1]:return None
    weighted=z[0]+(t-v[0])*(z[1]-z[0])/(v[1]-v[0])
    slope=(v[1]-v[0])/(z[1]-z[0]);independent=(t-(v[0]-slope*z[0]))/slope
    if not math.isclose(weighted,independent,rel_tol=0,abs_tol=1e-8) or not z[0]<=weighted<=z[1]:raise ValueError('Independent two-point interpolation mismatch')
    return weighted


def sensitivity(z,v,se,t):
    nominal=crossing(z,v,t)
    if nominal is None:raise ValueError('Original nominal downward threshold bracket required')
    if len(se)!=2 or any(e is not None and (not finite(e) or e<0) for e in se):raise ValueError('Source standard errors must be nonnegative finite or missing')
    result={'nominal_crossing_depth_m':nominal,'source_endpoint_depths_m':list(z),'source_endpoint_poleward_velocity_m_s':list(v),
      'source_endpoint_northward_standard_errors_m_s':list(se),'source_threshold_m_s':t,'source_component_SE_multiplier':1,
      'corners':[],'complete_endpoint_rectangle_depth_sensitivity_range_m':None,'confidence_interval_established':False,
      'endpoint_errors_assumed_independent':False,'component_covariance_used':False,'normal_distribution_assumed':False,
      'full_profile_or_core_connection_reassessed':False,'fixed_nominal_bracket_retained':True,
      'sensitivity_extrema_are_annual_range':False,'physical_current_bottom_established':False,
      'physical_depth_uncertainty_m':None,'physical_thickness_m':None,'annual_depth_range_m':None,'volume_eligible':False,
      'physical_state_join_eligible':False,'reference_route_projection_eligible':False,'seasonal_playback_eligible':False}
    if any(e is None for e in se):result['status']='SOURCE_ENDPOINT_STANDARD_ERROR_MISSING';return result
    for signs in itertools.product([-1,1],repeat=2):
        pair=[u+a*e for u,a,e in zip(v,signs,se)];root=crossing(z,pair,t)
        result['corners'].append({'endpoint_error_signs':list(signs),'perturbed_poleward_endpoint_velocities_m_s':pair,
          'crossing_depth_m':root,'bracket_survives':root is not None,'status':'ADJACENT_CROSSING_IN_FIXED_BRACKET' if root is not None else 'ORIGINAL_LOCAL_BRACKET_INVALIDATED_NO_SEARCH_OR_EXTRAPOLATION'})
    if all(r['bracket_survives'] for r in result['corners']):
        roots=[r['crossing_depth_m'] for r in result['corners']];span=[min(roots),max(roots)]
        if not span[0]-1e-8<=nominal<=span[1]+1e-8:raise ValueError('Nominal root must lie in complete endpoint rectangle response')
        result.update(status='ALL_FOUR_ENDPOINT_ERROR_CORNERS_PRESERVE_LOCAL_BRACKET',complete_endpoint_rectangle_depth_sensitivity_range_m=span)
    else:result['status']='ENDPOINT_ERROR_RECTANGLE_INVALIDATES_LOCAL_BRACKET'
    return result


def build(root=ROOT):
    reader=lambda p:(root/p).read_bytes();read=lambda p:json.loads(reader(p));op=read(OP)
    for p,h in op['input_sha256'].items():
        if hashlib.sha256(reader(p)).hexdigest()!=h:raise ValueError('Pinned retained source/method changed:'+p)
    if op['source_component_SE_multiplier']!=1 or op['additional_provider_requests_allowed']!=0 or op['maximum_selected_levels_per_profile']!=6 or op['maximum_bracket_scalar_touches']!=252:raise ValueError('Fixed existing profiles,local brackets and source-error scope required')
    raw=reader(SOURCE)
    if len(raw)>500000:raise ValueError('Bounded retained typed source packet required')
    source=json.loads(raw)
    if source['schema']!='osw.eac-mooring-depth-benchmark.v1' or source['counts']['profiles']!=14 or source['counts']['velocity_scalars_retrieved']!=8768 or any(source['eligibility'].values()):raise ValueError('Exact original fourteen-case retained benchmark required')
    samples=source['samples']
    if len(samples)!=14 or {(r['station'],r['source_date']) for r in samples}!={(s,d) for s in STATIONS for d in DATES}:raise ValueError('All seven original stations and both dates must remain')
    for meta in source['source_metadata']:
        a=meta['variable_attributes'];depth=a['DEPTH'];error=a['VCUR_uncertainty'];vel=a['VCUR']
        if depth['units']!='m' or depth['positive']!='down' or depth['reference_datum']!='sea surface':raise ValueError('Original metric source depth datum required')
        if (vel['units'],vel['standard_name'],vel['reference_datum'])!=('m s-1','northward_sea_water_velocity','true north') or (error['units'],error['standard_name'])!=('m s-1','northward_sea_water_velocity standard_error'):raise ValueError('Actual provider northward velocity and standard-error semantics required')
    outcomes=[];touches=0;selected_levels=0;typed_fields=0
    for sample in samples:
        z=sample['depth_levels_m'];values=sample['source_values'];layers=sample['threshold_layers'];chosen=set()
        if not 2<=len(z)<=500 or any(not finite(v) for v in z) or any(b<=a for a,b in zip(z,z[1:])):raise ValueError('Original ordered metric grid bounded before selected-value analysis')
        if [r['threshold_m_s'] for r in layers]!=THRESHOLDS or any(len(values[k])!=len(z) for k in ['UCUR','VCUR','UCUR_uncertainty','VCUR_uncertainty']):raise ValueError('Frozen source field shapes and all three cutoffs required')
        typed_fields+=sum(len(values[k]) for k in ['UCUR','VCUR','UCUR_uncertainty','VCUR_uncertainty'])
        for layer in layers:
            row={'station':sample['station'],'source_date':sample['source_date'],'actual_source_time_utc':sample['actual_source_time_utc'],
              'lon_lat':copy.deepcopy(sample['lon_lat']),'source_threshold_m_s':layer['threshold_m_s'],'original_nominal_layer':copy.deepcopy(layer),
              'source_profile_pointer':'/samples/'+str(len(outcomes)//3),'endpoint_source_indices':None,'sensitivity':None,
              'fixed_station_is_current_axis':False,'physical_current_bottom_established':False,'new_native_measurement':False}
            if layer['lower_depth_m'] is None:
                row['status']='NOMINAL_LOWER_BOUNDARY_UNRESOLVED_NO_LOCAL_SENSITIVITY';outcomes.append(row);continue
            if layer['lower_status']!='adjacent_isotach_crossing':raise ValueError('Finite original lower boundary must have exact adjacent bracket')
            bracket=layer['lower_bracket_m'];indices=[z.index(value) for value in bracket]
            if len(indices)!=2 or indices[1]!=indices[0]+1:raise ValueError('Two original adjacent gridded cells; no gap fill or substitute bracket')
            chosen.update(indices);touches+=6
            if len(chosen)>6 or touches>252:raise ValueError('Whole retained experiment selected-level/scalar bounds cannot reset')
            mean=[None if values['VCUR'][i] is None else -values['VCUR'][i] for i in indices];errors=[values['VCUR_uncertainty'][i] for i in indices]
            if any(v is None for v in mean):raise ValueError('Nominal crossing bracket cannot hide missing native component')
            audit=sensitivity(bracket,mean,errors,layer['threshold_m_s'])
            if not math.isclose(audit['nominal_crossing_depth_m'],layer['lower_depth_m'],rel_tol=0,abs_tol=1e-8):raise ValueError('Independent local formula must reproduce frozen original lower depth')
            row.update(status=audit['status'],endpoint_source_indices=indices,sensitivity=audit);outcomes.append(row)
        selected_levels+=len(chosen)
    if typed_fields!=8768 or typed_fields>20000:raise ValueError('Original typed field count and whole input scalar cap required')
    stats={'source_profiles':14,'station_date_threshold_outcomes':len(outcomes),'nominal_resolved_lower_boundaries':sum(r['sensitivity'] is not None for r in outcomes),
      'complete_endpoint_rectangle_responses':sum(r['status']=='ALL_FOUR_ENDPOINT_ERROR_CORNERS_PRESERVE_LOCAL_BRACKET' for r in outcomes),
      'invalidated_local_brackets':sum(r['status']=='ENDPOINT_ERROR_RECTANGLE_INVALIDATES_LOCAL_BRACKET' for r in outcomes),
      'source_endpoint_standard_error_missing':sum(r['status']=='SOURCE_ENDPOINT_STANDARD_ERROR_MISSING' for r in outcomes),
      'nominal_lower_boundary_unresolved':sum(r['sensitivity'] is None for r in outcomes),
      'corner_outcomes':sum(len(r['sensitivity']['corners']) for r in outcomes if r['sensitivity'] is not None),
      'selected_source_levels_across_profiles':selected_levels,'local_bracket_scalar_touches':touches,'retained_typed_velocity_scalars':typed_fields,
      'new_native_measurements':0,'new_reference_inventory_rows':0,'provider_requests':0}
    if len(outcomes)!=42:raise ValueError('All original outcomes including missing profiles/censored boundaries required')
    for cutoff in THRESHOLDS:
        actual=sum(r['source_threshold_m_s']==cutoff and r['sensitivity'] is not None for r in outcomes)
        if actual!=source['counts']['resolved_lower_boundaries_by_threshold'][str(cutoff)]:raise ValueError('Every nominal resolved boundary must reconcile with frozen source count')
    return {'schema':'osw.eac-mooring-local-depth-sensitivity.v1','status':'CONDITIONAL_LOCAL_ENDPOINT_STANDARD_ERROR_RESPONSE_NOT_DEPTH_CONFIDENCE_INTERVAL',
      'source_file':SOURCE,'source_sha256':hashlib.sha256(raw).hexdigest(),'operator_file':OP,'operator_sha256':hashlib.sha256(reader(OP)).hexdigest(),
      'input_sha256':op['input_sha256'],'source_processing':'Daily unfilled processed observations;vertical/time gridding and5dayfilter;not instantaneous or native independent cells.',
      'operator_scope':'Four corners of plus/minus one reported northward-component standard error at each original lower bracket endpoint; poleward=-VCUR. Fixed threshold,nominalcomponent and bracket. Whole profile/core connectivity not reassessed; no bracket relocation or extrapolation.',
      'interpretation':'A complete local response exists only when every corner retains the original downward crossing. Invalid corners remain unresolved and suppress a complete range. All output ranges are deterministic conditional sensitivity,not confidence/physical uncertainty/annual envelopes.',
      'counts':stats,'outcomes':outcomes,'original_source_field_retrieval_count_unchanged':8768,'original_source_field_retrieval_cap_unchanged':20000,
      'conservative_prior_native_scalar_bound':40282,'additional_retained_typed_scalar_bound':20000,'selected_scalar_bound':252,
      'conservative_combined_scalar_bound':60534,'original_global_scalar_cap':250000,'new_original_native_array_reads':0,
      'new_reference_inventory_rows':0,'reference_inventory_rows_unchanged':859,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(rows):
    fields=['station','source_date','source_threshold_m_s','status','original_nominal_lower_depth_m','complete_local_sensitivity_min_m','complete_local_sensitivity_max_m','source_endpoint_error_missing','physical_current_bottom_established']
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');writer.writeheader()
    for row in rows:
        a=row['sensitivity'];span=a['complete_endpoint_rectangle_depth_sensitivity_range_m'] if a else None
        writer.writerow({'station':row['station'],'source_date':row['source_date'],'source_threshold_m_s':row['source_threshold_m_s'],'status':row['status'],
          'original_nominal_lower_depth_m':row['original_nominal_layer']['lower_depth_m'],'complete_local_sensitivity_min_m':span[0] if span else None,
          'complete_local_sensitivity_max_m':span[1] if span else None,'source_endpoint_error_missing':a is not None and a['status']=='SOURCE_ENDPOINT_STANDARD_ERROR_MISSING','physical_current_bottom_established':False})
    return out.getvalue().encode()


def main():
    def denied(*a,**k):raise RuntimeError('Retained analysis forbids provider/network replay')
    def stopped(*a):raise SystemExit('Stopped producer; no source retry')
    socket.socket=denied;socket.create_connection=denied
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stopped)
    signal.alarm(90)
    report=build();folder=ROOT/'eac-mooring-local-depth-sensitivity-v1';folder.mkdir(exist_ok=False)
    raw=(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode();table=csv_bytes(report['outcomes'])
    if len(raw)+len(table)>=2400000:raise ValueError('Fixed scientific output cap exceeded')
    (folder/'sensitivity.json').write_bytes(raw);(folder/'sensitivity.csv').write_bytes(table);signal.alarm(0)
    print(json.dumps(report['counts']),flush=True)

if __name__=='__main__':main()
