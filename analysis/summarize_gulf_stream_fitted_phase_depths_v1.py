"""Section and sampled annual-fit phase spans of retained Gulf Stream depth descriptors."""
import copy,csv,hashlib,io,json,math,signal,socket
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OP='research/gulf-stream-fitted-phase-depth-summary-operator-v1.json'
SOURCE='research/gulf-stream-fit-error-depth-sensitivity-v1.json'
SOURCE_OPERATOR='research/gulf-stream-spray-depth-sections-operator-v1.json'
SECTIONS=['coastal-30n','coastal-32n','coastal-34n','offshore-73w','offshore-70w']
ROLE='half_sampled_core_component_decay_depth_not_physical_bottom_or_error_bound'


def finite(v):return type(v) in (int,float) and math.isfinite(v)


def thin_case(case,index):
    if case['entity_id']!='current:gulf-stream' or case['section_id'] not in SECTIONS:raise ValueError('Original Gulf Stream section owner required')
    kind=case['source_product_kind'];month=case['calendar_month_phase']
    if not ((kind=='mean' and month is None) or (kind=='annual_cycle' and type(month)==int and 1<=month<=12)):raise ValueError('One mean fit or original day15 annual phase,never observed month/year')
    if case['timestamp_is_instantaneous_observation_date'] or case['whole_route_representative'] or case['physical_state_join_eligible'] or case['seasonal_extrema_eligible']:raise ValueError('Fitted phase timestamps and scoped regional descriptors cannot promote physical claims')
    d=case['nominal_source_half_core_descriptor'];a=case['sensitivity']
    if d['relative_sampled_core_fraction']!=0.5 or d['quantity_role']!=ROLE:raise ValueError('Half sampled core metric,not absolute10cm/s or physical bottom')
    if not finite(d['core_velocity_m_s']) or not d['core_velocity_m_s']>0 or not math.isclose(d['threshold_m_s'],0.5*d['core_velocity_m_s'],rel_tol=0,abs_tol=1e-12):raise ValueError('Exact original nominal half-core cutoff required')
    expected={k:v for k,v in d.items() if k not in ['relative_sampled_core_fraction','quantity_role']}
    if a['nominal_layer']!=expected or a['fixed_nominal_cutoff_m_s']!=d['threshold_m_s'] or a['fixed_nominal_core_index']!=d['core_index'] or a['source_component_SE_multiplier']!=1:raise ValueError('Existing nominal component/core/cutoff response alignment required')
    for k in ['confidence_interval_established','component_covariance_used','normal_distribution_assumed','direction_uncertainty_propagated','core_selection_uncertainty_propagated','cutoff_uncertainty_propagated','physical_current_bottom_established','volume_eligible']:
        if a[k] is not False:raise ValueError('Preserve original conditional SE-response limitations')
    depth=d['lower_depth_m'];response=a['lower_depth_sensitivity_range_m']
    if depth is not None:
        if not finite(depth) or not 10<=depth<=1000 or d['lower_status']!='adjacent_isotach_crossing':raise ValueError('Retained resolved adjacent depth inside10-1000m fitted domain')
        bracket=d['lower_bracket_m']
        if len(bracket)!=2 or not all(finite(v) for v in bracket) or not 10<=bracket[0]<bracket[1]<=1000 or not bracket[0]<=depth<=bracket[1]:raise ValueError('Original native bracket must contain existing depth')
    if response is not None:
        if depth is None or len(response)!=2 or not all(finite(v) for v in response) or not 10<=response[0]<=depth<=response[1]<=1000:raise ValueError('Valid conditional fixed-cutoff response bracket required')
    pos=case['source_lon_lat'];direction=case['locked_reference_direction_at100m_degrees']
    if len(pos)!=2 or not all(finite(v) for v in pos) or not -180<=pos[0]<=180 or not -90<=pos[1]<=90 or not finite(direction):raise ValueError('Original valid source position and locked direction required,not route projection')
    return {'case_id':case['section_id']+':'+kind+':'+(str(month) if month is not None else 'mean'),
      'entity_id':'current:gulf-stream','section_id':case['section_id'],'source_product_kind':kind,'calendar_month_phase':month,
      'source_case_pointer':'/cases/'+str(index),'source_section_file':case['source_file'],'source_section_sha256':case['source_sha256'],'source_section_pointer':case['source_pointer'],
      'actual_provider_phase_timestamp_utc':case['actual_provider_phase_timestamp_utc'],'nominal_phase_calendar_date':case['nominal_phase_calendar_date'],
      'timestamp_is_instantaneous_observation_date':False,'source_lon_lat':copy.deepcopy(pos),'horizontal_selection_status':case['horizontal_selection_status'],
      'selected_section_column_index':case['selected_section_column_index'],'locked_reference_direction_at100m_degrees':direction,
      'relative_sampled_core_fraction':0.5,'fixed_nominal_cutoff_m_s':d['threshold_m_s'],'original_nominal_core_depth_m':d['core_depth_m'],
      'nominal_half_core_lower_depth_m':depth,'nominal_upper_boundary_status':d['upper_status'],'nominal_lower_boundary_status':d['lower_status'],
      'nominal_lower_native_bracket_m':copy.deepcopy(d.get('lower_bracket_m')),'conditional_one_reported_SE_depth_response_m':copy.deepcopy(response),
      'conditional_response_status':a['status'],'source_component_SE_multiplier':1,'whole_profile_physical_depth_uncertainty_m':None,
      'phase_winner_may_shift_spatially':True,'core_cutoff_and_direction_uncertainty_propagated':False,
      'physical_current_bottom_established':False,'physical_thickness_m':None,'annual_depth_range_m':None,
      'confidence_interval_established':False,'source_date_is_independent_observation':False,
      'volume_eligible':False,'physical_state_join_eligible':False,'reference_route_projection_eligible':False,'seasonal_playback_eligible':False}


def summarize_section(rows,definition):
    if len(rows)!=13 or len({(r['source_product_kind'],r['calendar_month_phase']) for r in rows})!=13:raise ValueError('Exactly mean+12unique fitted phases per section')
    means=[r for r in rows if r['source_product_kind']=='mean' and r['calendar_month_phase'] is None]
    phases=sorted([r for r in rows if r['source_product_kind']=='annual_cycle'],key=lambda r:r['calendar_month_phase'])
    if len(means)!=1 or [r['calendar_month_phase'] for r in phases]!=list(range(1,13)):raise ValueError('Fixed phase denominator12;mean cannot be13th phase')
    if any(r['section_id']!=definition['id'] for r in rows):raise ValueError('Do not mix sections into one phase range')
    values=[r['nominal_half_core_lower_depth_m'] for r in phases if r['nominal_half_core_lower_depth_m'] is not None]
    if any(not finite(v) or v<0 for v in values):raise ValueError('Finite nominal descriptor or explicit missing required')
    interval=[min(values),max(values)] if values else None;complete=len(values)==12
    return {'section_id':definition['id'],'source_section_definition':copy.deepcopy(definition),'expected_fitted_day15_phases':12,
      'resolved_nominal_phase_depths':len(values),'unresolved_nominal_phase_months':[r['calendar_month_phase'] for r in phases if r['nominal_half_core_lower_depth_m'] is None],
      'resolved_phase_subset_nominal_depth_span_m':interval,'phase_subset_span_is_conditional':not complete,
      'complete_twelve_sampled_phase_nominal_depth_span_m':interval if complete else None,
      'phase_months_at_sampled_min_depth':[r['calendar_month_phase'] for r in phases if interval is not None and r['nominal_half_core_lower_depth_m']==interval[0]],
      'phase_months_at_sampled_max_depth':[r['calendar_month_phase'] for r in phases if interval is not None and r['nominal_half_core_lower_depth_m']==interval[1]],
      'conditional_source_error_responses_available_phase_count':sum(r['conditional_one_reported_SE_depth_response_m'] is not None for r in phases),
      'phase_selected_source_positions_vary':len({tuple(r['source_lon_lat']) for r in phases})>1,
      'phase_nominal_cutoffs_vary':len({r['fixed_nominal_cutoff_m_s'] for r in phases})>1,
      'phase_locked_100m_directions_vary':len({round(r['locked_reference_direction_at100m_degrees']%360,12) for r in phases})>1,
      'mean_fit_case':copy.deepcopy(means[0]),'fitted_phase_cases':copy.deepcopy(phases),
      'mean_fit_is_a_thirteenth_seasonal_phase':False,'mean_of_phase_depths_compared_to_mean_fit':False,
      'sampled_phase_span_is_continuous_annual_fit_extrema':False,'sampled_phase_span_is_observed_annual_extrema':False,
      'sampled_phase_span_is_measurement_error_or_confidence_interval':False,'cross_current_fixed_cutoff_depth_ranking_eligible':False,
      'full_reference_route_depth_profile_established':False,'physical_current_bottom_established':False,
      'physical_depth_uncertainty_m':None,'physical_thickness_m':None,'annual_depth_range_m':None,'volume_eligible':False}


def count_numbers(obj):
    total=0;stack=[obj]
    while stack:
        v=stack.pop()
        if isinstance(v,dict):stack.extend(v.values())
        elif isinstance(v,list):stack.extend(v)
        elif type(v) in (int,float):
            if not finite(v):raise ValueError('Finite retained packet numbers required')
            total+=1
    return total


def build(root=ROOT):
    reader=lambda p:(root/p).read_bytes();read=lambda p:json.loads(reader(p));op=read(OP)
    for p,h in op['input_sha256'].items():
        if hashlib.sha256(reader(p)).hexdigest()!=h:raise ValueError('Pinned existing source/method changed:'+p)
    if op['section_ids']!=SECTIONS or op['relative_sampled_core_fraction']!=0.5 or op['new_native_profiles_selected_allowed']!=0 or op['new_provider_requests_allowed']!=0:raise ValueError('Exact scoped metadata-only half-core phase summary required')
    raw=reader(SOURCE)
    if len(raw)>800000:raise ValueError('Bounded retained typed descriptor/error packet required')
    source=json.loads(raw);number_count=count_numbers(source);source_op=read(SOURCE_OPERATOR)
    if source['schema']!='osw.gulf-stream-fit-error-depth-sensitivity.v1' or source['counts']['profile_cases']!=65 or number_count>50000:raise ValueError('Original65-case bounded retained scalar packet required')
    if source['documented_fit_observation_period']!=['2015-07-16','2023-05-30'] or source['source_dataset_doi']!='10.21238/S8TC9W':raise ValueError('Exact documented fitted observation period/product,not source calendar-year cohort')
    rows=[thin_case(c,i) for i,c in enumerate(source['cases'])]
    if len(rows)!=65 or len({r['case_id'] for r in rows})!=65:raise ValueError('All original distinct65cases exactlyonce')
    definitions={s['id']:s for s in source_op['sections']}
    if set(definitions)!=set(SECTIONS):raise ValueError('All five declared original sections required')
    summaries=[summarize_section([r for r in rows if r['section_id']==key],definitions[key]) for key in SECTIONS]
    matrix=[{'calendar_month_phase':month,'source_phase_type':'fitted_day15_annual_cycle_not_observation_date',
      'section_cases':[{'section_id':key,'case_id':next(r['case_id'] for r in rows if r['section_id']==key and r['calendar_month_phase']==month and r['source_product_kind']=='annual_cycle')} for key in SECTIONS],
      'section_order_is_physical_along_route_distance':False} for month in range(1,13)]
    stats={'original_fit_cases':65,'source_sections':5,'mean_fit_cases':5,'fitted_day15_phase_cases':60,'complete_twelve_sampled_phase_spans':sum(s['complete_twelve_sampled_phase_nominal_depth_span_m'] is not None for s in summaries),
      'resolved_nominal_half_core_depths':sum(r['nominal_half_core_lower_depth_m'] is not None for r in rows),
      'conditional_fit_error_responses_retained':sum(r['conditional_one_reported_SE_depth_response_m'] is not None for r in rows),
      'sections_with_phase_selected_position_changes':sum(s['phase_selected_source_positions_vary'] for s in summaries),
      'sections_with_phase_nominal_cutoff_changes':sum(s['phase_nominal_cutoffs_vary'] for s in summaries),
      'sections_with_phase_locked_direction_changes':sum(s['phase_locked_100m_directions_vary'] for s in summaries),
      'calendar_phase_section_matrix_cells':60,'retained_typed_numeric_scalars':number_count,'new_native_profiles_selected':0,'new_native_ocean_arrays_decoded':0,
      'new_reference_inventory_rows':0,'new_independent_observations':0,'provider_requests':0}
    return {'schema':'osw.gulf-stream-fitted-phase-depth-summary.v1','status':'FIVE_SECTION_SAMPLED_FIT_PHASE_DEPTH_CURVES_WITH_SEPARATE_CONDITIONAL_ERROR_RESPONSES',
      'entity_id':'current:gulf-stream','source_file':SOURCE,'source_sha256':hashlib.sha256(raw).hexdigest(),'operator_file':OP,'operator_sha256':hashlib.sha256(reader(OP)).hexdigest(),'input_sha256':op['input_sha256'],
      'source_dataset_doi':source['source_dataset_doi'],'documented_fit_observation_period':copy.deepcopy(source['documented_fit_observation_period']),
      'metric':'half_sampled_core_locked_component_lower_decay_depth','relative_sampled_core_fraction':0.5,
      'method':'Bookkeep existing65scalar half-core lower depths and originalconditionalSEresponses only. Separatefive meanfits fromsixty fittedday15phases. Complete12sampledphase spans require12finite nominaldepths;do notmixmeanfitintophaseextrema.',
      'interpretation':'Fitted annualphase samples,not monthlymeans or observedannualextrema. Phase winner position,direction and nominal numeric cutoff can vary. Half-core metric cannot be ranked as absolute10cm/s current depth. Conditionalone-reported-SEranges remain separate fromphasevariation;no combined CI/physicalbottom/thickness/routevolume.',
      'counts':stats,'cases':rows,'section_summaries':summaries,'sampled_phase_section_matrix':matrix,
      'source_full_velocity_arrays_reanalysed':False,'source_native_arrays_decoded':0,'retained_packet_numeric_scalar_cap':50000,
      'prior_legacy_acquisition_replayed':False,'legacy_acquisition_compliance_with_new_native_caps_claimed':False,
      'existing_reference_inventory_rows_unchanged':859,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(rows):
    fields=['section_id','source_product_kind','calendar_month_phase','nominal_half_core_lower_depth_m','conditional_error_response_min_m','conditional_error_response_max_m','relative_sampled_core_fraction','fixed_nominal_cutoff_m_s','locked_reference_direction_at100m_degrees','source_longitude','source_latitude','source_case_pointer','timestamp_is_instantaneous_observation_date']
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');writer.writeheader()
    for r in rows:
        row={k:r.get(k) for k in fields};span=r['conditional_one_reported_SE_depth_response_m'];row.update(conditional_error_response_min_m=span[0] if span else None,
          conditional_error_response_max_m=span[1] if span else None,source_longitude=r['source_lon_lat'][0],source_latitude=r['source_lon_lat'][1]);writer.writerow(row)
    return out.getvalue().encode()


def main():
    def denied(*a,**k):raise RuntimeError('Descriptor/response summary forbids source/provider replay')
    def stopped(*a):raise SystemExit('Stopped retained metadata producer')
    socket.socket=denied;socket.create_connection=denied
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stopped)
    signal.alarm(90);report=build();folder=ROOT/'gulf-stream-fitted-phase-depth-summary-v1';folder.mkdir(exist_ok=False)
    raw=(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode();table=csv_bytes(report['cases'])
    if len(raw)+len(table)>=2400000:raise ValueError('Fixed scientific output chunk cap exceeded')
    (folder/'phase-depths.json').write_bytes(raw);(folder/'phase-depths.csv').write_bytes(table);signal.alarm(0)
    print(json.dumps(report['counts']),flush=True)

if __name__=='__main__':main()
