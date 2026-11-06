"""Fixed-cutoff fitted-velocity error sensitivity; no confidence or physical-bottom claim."""
import copy,hashlib,json,math
from collections import Counter
from pathlib import Path
import acquire_gulf_stream_spray_sections_v1 as source
from derive_eac_connected_layer_thickness_v1 import connected_layer

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/gulf-stream-fit-error-depth-sensitivity-operator-v1.json'


def digest(raw):return hashlib.sha256(raw).hexdigest()
def encode(v):return (json.dumps(v,separators=(',',':'),allow_nan=False)+'\n').encode()
def finite(x):return type(x) in (int,float) and math.isfinite(x)


def rectangle_radius(east_se,north_se,direction):
    if not finite(direction):raise ValueError('Fixed finite source direction required')
    for value in [east_se,north_se]:
        if value is not None and (not finite(value) or value<0):raise ValueError('Nonnegative finite-or-missing source standard errors required')
    if east_se is None or north_se is None:return None
    angle=math.radians(direction)
    return abs(math.sin(angle))*east_se+abs(math.cos(angle))*north_se


def fitted_layer(z,v,cutoff,core):
    layer=connected_layer(z,v,cutoff,[z[core],z[core]])
    if layer['status']=='resolved_connected_model_threshold_layer':layer['status']='resolved_connected_fitted_observation_threshold_layer'
    return layer


def sensitivity(z,mean,radius,core,cutoff):
    if not 2<=len(z)<=100 or len(mean)!=len(z) or len(radius)!=len(z) or type(core)!=int or not 0<=core<len(z) or not finite(cutoff) or cutoff<=0:raise ValueError('Bounded native source profiles and fixed valid core/cutoff required')
    if any(v is not None and not finite(v) for v in mean) or any(v is not None and (not finite(v) or v<0) for v in radius):raise ValueError('Finite-or-missing values and nonnegative sensitivity radii required')
    if mean[core] is None or mean[core]<=cutoff:raise ValueError('Original nominal core must qualify without replacement')
    lower=[None if v is None or e is None else v-e for v,e in zip(mean,radius)];upper=[None if v is None or e is None else v+e for v,e in zip(mean,radius)]
    nominal=fitted_layer(z,mean,cutoff,core);low=fitted_layer(z,lower,cutoff,core);high=fitted_layer(z,upper,cutoff,core)
    pair=None
    if all(v['lower_status']=='adjacent_isotach_crossing' for v in [low,nominal,high]):
        a,n,b=(v['lower_depth_m'] for v in [low,nominal,high])
        if not a<=n<=b:raise ValueError('Fixed-cutoff componentwise ordering must preserve lower crossing order')
        pair=[a,b]
    return {'status':'FINITE_FIXED_CUTOFF_ERROR_RECTANGLE_SENSITIVITY' if pair is not None else 'UNRESOLVED_LOCKED_CORE_OR_LOWER_BOUNDARY_SENSITIVITY','nominal_layer':nominal,'lower_velocity_scenario_layer':low,'upper_velocity_scenario_layer':high,'lower_depth_sensitivity_range_m':pair,'projected_component_error_rectangle_radius_m_s':radius,'lower_velocity_scenario_m_s':lower,'upper_velocity_scenario_m_s':upper,'fixed_nominal_core_index':core,'fixed_nominal_cutoff_m_s':cutoff,'source_component_SE_multiplier':1,'uncertainty_m':None,'annual_range_m':None,'confidence_interval_established':False,'component_covariance_used':False,'normal_distribution_assumed':False,'direction_uncertainty_propagated':False,'core_selection_uncertainty_propagated':False,'cutoff_uncertainty_propagated':False,'physical_current_bottom_established':False,'volume_eligible':False}


def reproduce(row,thresholds):
    z=row['depth_levels_m']
    if z!=list(range(10,1001,10)):raise ValueError('Existing100-level fitted native grid required;do not truncate to HYCOM40-level rules')
    candidates=[]
    for a in row['axis_candidate_audit']:
        directions=[None]*100;directions[9]=a['reference_direction_at100m_degrees_clockwise_from_north'];candidates.append({'source_lon_lat':a['source_lon_lat'],'source_fit_support':{'downstream_direction':directions},'source_values':{'eastward_velocity':a['upper10_to200m_eastward_velocity_m_s']+[None]*80,'northward_velocity':a['upper10_to200m_northward_velocity_m_s']+[None]*80}})
    selected,audit=source.select_axis(z,candidates)
    if selected!=row['selected_section_column_index'] or audit!=row['axis_candidate_audit'] or selected is None:raise ValueError('Exact original upper-layer candidates and horizontal selection required')
    status='edge_maximum_axis_unresolved' if selected in [0,len(candidates)-1] else 'interior_fitted_section_maximum_not_independently_validated_axis'
    if row['horizontal_selection_status']!=status:raise ValueError('Original horizontal status must remain')
    profile=row['selected_profile'];direction=profile['locked_reference_direction_at100m_degrees'];values=profile['source_values']
    if direction!=audit[selected]['reference_direction_at100m_degrees_clockwise_from_north'] or direction!=profile['source_fit_support']['downstream_direction'][9] or profile['source_lon_lat']!=audit[selected]['source_lon_lat']:raise ValueError('Original source column and locked100m direction required')
    mean=[source.project(e,n,direction) for e,n in zip(values['eastward_velocity'],values['northward_velocity'])]
    if len(mean)!=100 or mean!=profile['along_locked_mean_direction_m_s'] or any(len(values[k])!=100 for k in source.VELOCITY):raise ValueError('Exact retained component projection required')
    layers,half=source.diagnose(z,mean,thresholds)
    if layers!=profile['absolute_component_threshold_layers'] or half!=profile['half_sampled_core_component_decay'] or half is None:raise ValueError('All nominal absolute layers and half-core descriptor must reproduce')
    radius=[rectangle_radius(e,n,direction) for e,n in zip(values['eastward_velocity_uncertainty'],values['northward_velocity_uncertainty'])]
    result=sensitivity(z,mean,radius,half['core_index'],half['threshold_m_s']);expected={k:v for k,v in half.items() if k not in ['relative_sampled_core_fraction','quantity_role']}
    if result['nominal_layer']!=expected:raise ValueError('Locked nominal seed must reproduce original half-core layer exactly')
    return result


def build(root=ROOT):
    op=json.loads((root/OPERATOR).read_bytes())
    if any(op['eligibility'].values()) or op['source_component_SE_multiplier']!=1 or op['direction_core_and_cutoff_policy']!='FIX_EACH_ORIGINAL_NOMINAL_SELECTION_DIRECTION_CORE_AND_CUTOFF':raise ValueError('Fixed source scenario rules and non-promotion required')
    for p,pin in op['input_sha256'].items():
        if digest((root/p).read_bytes())!=pin:raise ValueError('Pinned source/method changed: '+p)
    source_op=json.loads((root/op['source_operator']).read_bytes());cases=[]
    if len(op['section_files'])!=5 or len(set(op['section_files']))!=5:raise ValueError('All five retained fitted sections required')
    for file in op['section_files']:
        raw=(root/file).read_bytes();section=json.loads(raw)
        if section['schema']!='osw.gulf-stream-spray-depth-section.v1' or section['entity_context']!='current:gulf-stream' or section['section_definition'] not in source_op['sections'] or any(section['eligibility'].values()):raise ValueError('Exact scoped source section required')
        for meta in section['source_metadata']:
            attrs=meta['variable_attributes']
            if meta['global_attributes']['product_version']!=source_op['expected_product_versions'][meta['kind']]:raise ValueError('Original product version required')
            for stem in ['eastward','northward']:
                error=attrs[stem+'_velocity_uncertainty']
                if error['standard_name']!=stem+'_sea_water_velocity_standard_error' or error['units']!='m s-1':raise ValueError('Source fitted-velocity standard-error semantics required')
        if len(section['records'])!=13 or {(v['source_product_kind'],v['calendar_month_phase']) for v in section['records']}!={('mean',None)}|{('annual_cycle',m) for m in range(1,13)}:raise ValueError('One mean and all12fitted phases required per section')
        for i,row in enumerate(section['records']):
            result=reproduce(row,source_op['thresholds_m_s']);cases.append({'entity_id':'current:gulf-stream','section_id':row['section_id'],'source_file':file,'source_sha256':digest(raw),'source_pointer':'/records/'+str(i),'source_product_kind':row['source_product_kind'],'calendar_month_phase':row['calendar_month_phase'],'actual_provider_phase_timestamp_utc':row['actual_provider_phase_timestamp_utc'],'nominal_phase_calendar_date':row['nominal_phase_calendar_date'],'timestamp_is_instantaneous_observation_date':False,'source_lon_lat':copy.deepcopy(row['selected_profile']['source_lon_lat']),'horizontal_selection_status':row['horizontal_selection_status'],'selected_section_column_index':row['selected_section_column_index'],'locked_reference_direction_at100m_degrees':row['selected_profile']['locked_reference_direction_at100m_degrees'],'depth_levels_m':copy.deepcopy(row['depth_levels_m']),'nominal_source_half_core_descriptor':copy.deepcopy(row['selected_profile']['half_sampled_core_component_decay']),'sensitivity':result,'nominal_diagnostics_and_selection_reproduced':True,'horizontal_core_or_direction_reselected':False,'phase_winner_may_shift_spatially':True,'whole_route_representative':False,'physical_state_join_eligible':False,'seasonal_extrema_eligible':False})
    if len(cases)!=65 or len({(c['section_id'],c['source_product_kind'],c['calendar_month_phase']) for c in cases})!=65:raise ValueError('Complete65-case matrix exactly once required')
    counts={'profile_cases':65,'mean_cases':5,'fitted_day15_phase_cases':60,'status_counts':dict(Counter(c['sensitivity']['status'] for c in cases)),'lower_scenario_lower_status_counts':dict(Counter(c['sensitivity']['lower_velocity_scenario_layer']['lower_status'] for c in cases)),'upper_scenario_lower_status_counts':dict(Counter(c['sensitivity']['upper_velocity_scenario_layer']['lower_status'] for c in cases)),'new_ocean_field_requests':0,'new_scalar_depth_references':0,'physical_whole_route_depth_profiles':0,'volume_estimates':0}
    report={'schema':'osw.gulf-stream-fit-error-depth-sensitivity.v1','status':'FIXED_NOMINAL_CUTOFF_COMPONENT_ERROR_RECTANGLE_SENSITIVITY_NOT_CONFIDENCE_INTERVAL','operator_file':OPERATOR,'operator_sha256':digest((root/OPERATOR).read_bytes()),'input_sha256':op['input_sha256'],'counts':counts,'source_dataset_doi':source_op['source_dataset_doi'],'documented_fit_observation_period':source_op['documented_fit_observation_period'],'cases':cases,'interpretation':op['interpretation'],'runtime_changed':False,'full_goal_complete':False};raw=encode(report)
    if len(raw)>=2400000:raise ValueError('Fixed2.4MB output cap exceeded')
    return report,raw


if __name__=='__main__':
    report,raw=build();out=Path('gulf-stream-fit-error-depth-sensitivity-v1');out.mkdir(exist_ok=True);(out/'sensitivity.json').write_bytes(raw);print(json.dumps(report['counts']),flush=True)
