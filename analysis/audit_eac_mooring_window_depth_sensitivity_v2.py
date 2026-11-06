"""Bounded wider-window EAC sensitivity preserving original nominal components."""
import copy,csv,hashlib,io,json,math,signal,socket
from pathlib import Path
from audit_eac_mooring_local_depth_sensitivity_v1 import crossing,finite,THRESHOLDS,STATIONS,DATES
ROOT=Path(__file__).resolve().parents[1]
OP='research/eac-mooring-window-depth-sensitivity-operator-v2.json'
SOURCE='research/source-data/eac-mooring-depth-benchmark-v1/candidate.json'
PRIOR='research/eac-mooring-local-depth-sensitivity-v1.json'


def select_window(n,layers,old_indices):
    if type(n)!=int or not 2<=n<=500 or len(old_indices)>6 or any(type(i)!=int or not 0<=i<n for i in old_indices):raise ValueError('Original coordinate cardinality and <=6 prior selected levels required')
    anchor=None
    for cutoff in [0.1,0.05,0.2]:
        layer=next(r for r in layers if r['source_threshold_m_s']==cutoff)
        if layer['endpoint_source_indices'] is not None:
            anchor=layer;break
    if anchor is None:return None
    j,k=anchor['endpoint_source_indices']
    if k!=j+1 or not 0<=j<k<n:raise ValueError('Exact original adjacent lower bracket indices required')
    # Two bracket levels plus sixteen native levels on each side, clipped only.
    selected=list(range(max(0,j-16),min(n,j+18)))
    union=set(selected)|set(old_indices)
    if len(selected)>34 or len(union)>40:raise ValueError('Cumulative selected-level cap cannot reset between methods/cutoffs')
    return {'anchor_threshold_m_s':anchor['source_threshold_m_s'],'anchor_bracket_indices':[j,k],
      'window_source_indices':selected,'prior_selected_indices':sorted(old_indices),'combined_selected_indices':sorted(union),
      'selection_uses_error_values':False,'clipped_window_shifted_or_extended':False}


def first_crossing(z,v,t):
    if not 2<=len(z)<=34 or len(v)!=len(z) or any(not finite(x) for x in z) or any(b<=a for a,b in zip(z,z[1:])) or z[0]<0 or not finite(t) or t<=0:raise ValueError('Bounded ordered window and positive fixed threshold required')
    if any(x is not None and not finite(x) for x in v):raise ValueError('Finite-or-null window velocities required')
    if v[0] is None:return {'status':'WINDOW_ENTRY_MISSING','depth_m':None}
    if v[0]<=t:return {'status':'WINDOW_ENTRY_NOT_QUALIFYING','depth_m':None}
    for i in range(1,len(z)):
        if v[i] is None:return {'status':'CENSORED_BEFORE_MISSING_WINDOW_LEVEL','depth_m':None,'last_connected_depth_m':z[i-1]}
        if v[i]<=t:return {'status':'FIRST_DOWNWARD_WINDOW_CROSSING','depth_m':crossing(z[i-1:i+1],v[i-1:i+1],t),'window_bracket_indices':[i-1,i],'bracket_depths_m':z[i-1:i+1]}
    return {'status':'CENSORED_AT_WINDOW_BOTTOM','depth_m':None,'last_connected_depth_m':z[-1]}


def sensitivity(z,mean,se,t,original_depth):
    if len(se)!=len(mean) or any(e is not None and (not finite(e) or e<0) for e in se):raise ValueError('Source component standard error finite nonnegative or null')
    nominal=first_crossing(z,mean,t)
    low=[None if v is None or e is None else v-e for v,e in zip(mean,se)]
    high=[None if v is None or e is None else v+e for v,e in zip(mean,se)]
    lower=first_crossing(z,low,t);upper=first_crossing(z,high,t)
    reproduces=nominal['depth_m'] is not None and finite(original_depth) and math.isclose(nominal['depth_m'],original_depth,rel_tol=0,abs_tol=1e-8)
    span=None
    if reproduces and lower['depth_m'] is not None and upper['depth_m'] is not None:
        a,b=lower['depth_m'],upper['depth_m']
        if not a-1e-8<=nominal['depth_m']<=b+1e-8:raise ValueError('Componentwise ordered profiles must preserve first-crossing order')
        span=[a,b]
    return {'status':'COMPLETE_CONDITIONAL_WINDOW_RESPONSE' if span is not None else 'WINDOW_RESPONSE_UNRESOLVED',
      'nominal_scenario':nominal,'lower_component_scenario':lower,'upper_component_scenario':upper,
      'original_nominal_crossing_reproduced':reproduces,'complete_conditional_depth_response_range_m':span,
      'full_profile_or_original_core_connection_reassessed':False,'fixed_window_entry':True,'confidence_interval_established':False,
      'source_error_independence_assumed':False,'normal_distribution_assumed':False,'physical_depth_uncertainty_m':None,
      'annual_depth_range_m':None,'physical_thickness_m':None,'physical_current_bottom_established':False,
      'volume_eligible':False,'physical_state_join_eligible':False,'reference_route_projection_eligible':False,'seasonal_playback_eligible':False}


def build(root=ROOT):
    reader=lambda p:(root/p).read_bytes();read=lambda p:json.loads(reader(p));op=read(OP)
    for p,h in op['input_sha256'].items():
        if hashlib.sha256(reader(p)).hexdigest()!=h:raise ValueError('Pinned source/method changed:'+p)
    if op['maximum_window_levels']!=34 or op['cumulative_selected_levels_per_profile_cap']!=40 or op['source_component_SE_multiplier']!=1 or op['additional_provider_requests_allowed']!=0:raise ValueError('Predeclared wider window and cumulative limits required')
    raw=reader(SOURCE);prior_raw=reader(PRIOR)
    if len(raw)+len(prior_raw)>800000:raise ValueError('Bounded retained typed source/audit packets required')
    source=json.loads(raw);prior=json.loads(prior_raw)
    if prior['source_sha256']!=hashlib.sha256(raw).hexdigest() or prior['counts']['station_date_threshold_outcomes']!=42 or prior['counts']['complete_endpoint_rectangle_responses']!=0:raise ValueError('Exact previous narrow-bracket experiment required')
    samples=source['samples']
    if len(samples)!=14 or {(r['station'],r['source_date']) for r in samples}!={(s,d) for s in STATIONS for d in DATES} or source['counts']['velocity_scalars_retrieved']!=8768:raise ValueError('All original source profiles/dates required')
    old={(r['station'],r['source_date'],r['source_threshold_m_s']):r for r in prior['outcomes']}
    if len(old)!=42:raise ValueError('All unique prior outcomes required')
    profiles=[];outcomes=[];touches=0;nodes=0
    for index,sample in enumerate(samples):
        layers=[old[(sample['station'],sample['source_date'],t)] for t in THRESHOLDS]
        if [r['original_nominal_layer'] for r in layers]!=sample['threshold_layers']:raise ValueError('Exact original cutoffs/nominal selection must remain')
        previous=set(i for r in layers for i in (r['endpoint_source_indices'] or []));window=select_window(len(sample['depth_levels_m']),layers,previous)
        profile={'station':sample['station'],'source_date':sample['source_date'],'actual_source_time_utc':sample['actual_source_time_utc'],
          'source_profile_pointer':'/samples/'+str(index),'lon_lat':copy.deepcopy(sample['lon_lat']),'window_selection':window,
          'depth_levels_m':None,'poleward_meridional_velocity_m_s':None,'source_northward_velocity_standard_error_m_s':None,
          'original_core_connection_outside_window_unassessed':True,'independently_validated_current_axis':False}
        if window is not None:
            indices=window['window_source_indices'];z=[sample['depth_levels_m'][i] for i in indices]
            north=[sample['source_values']['VCUR'][i] for i in indices];se=[sample['source_values']['VCUR_uncertainty'][i] for i in indices]
            mean=[None if v is None else -v for v in north];touches+=3*len(indices);nodes+=3*len(indices)
            if touches>1680 or nodes+252>6000:raise ValueError('Cumulative whole-experiment scalar/node budgets cannot reset')
            profile.update(depth_levels_m=z,poleward_meridional_velocity_m_s=mean,source_northward_velocity_standard_error_m_s=se)
        profiles.append(profile)
        for prior_row in layers:
            nominal=prior_row['original_nominal_layer'];row={'station':sample['station'],'source_date':sample['source_date'],
              'source_profile_pointer':profile['source_profile_pointer'],'window_profile_pointer':'/profiles/'+str(index),
              'source_threshold_m_s':prior_row['source_threshold_m_s'],'original_nominal_layer':copy.deepcopy(nominal),'sensitivity':None,
              'new_native_measurement':False,'physical_current_bottom_established':False}
            if nominal['lower_depth_m'] is None:row['status']='ORIGINAL_NOMINAL_LOWER_BOUNDARY_UNRESOLVED'
            elif window is None:row['status']='NO_ORIGINAL_NOMINAL_ANCHOR_WINDOW'
            elif not set(prior_row['endpoint_source_indices'])<=set(window['window_source_indices']):row['status']='ORIGINAL_NOMINAL_BRACKET_OUTSIDE_PREDECLARED_WINDOW'
            else:
                result=sensitivity(z,mean,se,prior_row['source_threshold_m_s'],nominal['lower_depth_m'])
                row.update(status=result['status'],sensitivity=result);nodes+=3
            outcomes.append(row)
    if len(outcomes)!=42 or nodes+252>6000:raise ValueError('All original contexts/cumulative geometry budget required')
    stats={'source_profiles':14,'station_date_threshold_outcomes':42,
      'selected_window_profiles':sum(r['window_selection'] is not None for r in profiles),
      'nominal_resolved_lower_boundaries':sum(r['original_nominal_layer']['lower_depth_m'] is not None for r in outcomes),
      'nominal_window_crossings_reproduced':sum(r['sensitivity'] is not None and r['sensitivity']['original_nominal_crossing_reproduced'] for r in outcomes),
      'complete_conditional_window_responses':sum(r['status']=='COMPLETE_CONDITIONAL_WINDOW_RESPONSE' for r in outcomes),
      'assessed_window_responses':sum(r['sensitivity'] is not None for r in outcomes),'window_response_unresolved':sum(r['status']=='WINDOW_RESPONSE_UNRESOLVED' for r in outcomes),
      'original_nominal_boundary_unresolved':sum(r['status']=='ORIGINAL_NOMINAL_LOWER_BOUNDARY_UNRESOLVED' for r in outcomes),
      'original_bracket_outside_window':sum(r['status']=='ORIGINAL_NOMINAL_BRACKET_OUTSIDE_PREDECLARED_WINDOW' for r in outcomes),
      'selected_source_scalar_touches':touches,'maximum_cumulative_selected_levels_per_profile':max(len(r['window_selection']['combined_selected_indices']) if r['window_selection'] else 0 for r in profiles),
      'cumulative_support_and_derived_node_bound':nodes+252,'new_native_measurements':0,'new_reference_inventory_rows':0,'provider_requests':0}
    return {'schema':'osw.eac-mooring-window-depth-sensitivity.v2','status':'PREDECLARED_WIDER_WINDOW_CONDITIONAL_ERROR_RESPONSES_NOT_DEPTH_CONFIDENCE_INTERVALS',
      'source_file':SOURCE,'source_sha256':hashlib.sha256(raw).hexdigest(),'prior_local_report_file':PRIOR,'prior_local_report_sha256':hashlib.sha256(prior_raw).hexdigest(),
      'operator_file':OP,'operator_sha256':hashlib.sha256(reader(OP)).hexdigest(),'input_sha256':op['input_sha256'],
      'method':'One clipped34levelwindow per profile anchored by original0.1lowerbracket,else0.05,else0.2;16nativelevels each side of2bracketlevels. No error-driven shifts/extensions. First downward crossing from fixed window entry for nominal and componentwise+/-1source-SE fields.',
      'scope':'Conditional on original nominal component;source core/path outside window not reassessed. Daily5dayfiltered vertically/timegridded unfilled VCUR. Whole-profile uncertainty,source gridding/core/cutoff/direction/axis/covariance errors remain unassessed.',
      'counts':stats,'profiles':profiles,'outcomes':outcomes,'prior_conservative_case_scalar_reservation':60534,
      'additional_retained_typed_scalar_reservation':20000,'additional_selected_scalar_reservation':1680,'conservative_combined_case_scalar_reservation':82214,
      'original_global_scalar_cap':250000,'original_global_decoded_byte_cap':7000000,'original_field_retrieval_count_unchanged':8768,'original_field_retrieval_cap_unchanged':20000,
      'new_native_array_reads':0,'reference_inventory_rows_unchanged':859,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(rows):
    fields=['station','source_date','source_threshold_m_s','status','original_nominal_depth_m','low_velocity_first_crossing_m','nominal_window_first_crossing_m','high_velocity_first_crossing_m','complete_response_min_m','complete_response_max_m','confidence_interval_established']
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');writer.writeheader()
    for r in rows:
        a=r['sensitivity'];span=a['complete_conditional_depth_response_range_m'] if a else None
        writer.writerow({'station':r['station'],'source_date':r['source_date'],'source_threshold_m_s':r['source_threshold_m_s'],'status':r['status'],
          'original_nominal_depth_m':r['original_nominal_layer']['lower_depth_m'],
          'low_velocity_first_crossing_m':a['lower_component_scenario']['depth_m'] if a else None,'nominal_window_first_crossing_m':a['nominal_scenario']['depth_m'] if a else None,
          'high_velocity_first_crossing_m':a['upper_component_scenario']['depth_m'] if a else None,'complete_response_min_m':span[0] if span else None,'complete_response_max_m':span[1] if span else None,'confidence_interval_established':False})
    return out.getvalue().encode()


def main():
    def denied(*a,**k):raise RuntimeError('Retained window producer forbids source/provider replay')
    def stop(*a):raise SystemExit('Window producer stopped without source retry')
    socket.socket=denied;socket.create_connection=denied
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stop)
    signal.alarm(90);report=build();folder=ROOT/'eac-mooring-window-depth-sensitivity-v2';folder.mkdir(exist_ok=False)
    raw=(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode();table=csv_bytes(report['outcomes'])
    if len(raw)+len(table)>=2400000:raise ValueError('Fixed scientific output chunk cap exceeded')
    (folder/'sensitivity.json').write_bytes(raw);(folder/'sensitivity.csv').write_bytes(table);signal.alarm(0)
    print(json.dumps(report['counts']),flush=True)

if __name__=='__main__':main()
