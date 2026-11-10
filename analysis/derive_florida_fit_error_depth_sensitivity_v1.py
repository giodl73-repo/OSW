"""Florida northward-component fit-error sensitivity; source selection stays frozen."""
import copy,hashlib,json,math
from collections import Counter
from pathlib import Path
import acquire_florida_spray_seasonal_depth_v1 as source
import derive_gulf_stream_fit_error_depth_sensitivity_v1 as shared

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/florida-fit-error-depth-sensitivity-operator-v1.json'


def digest(raw):return hashlib.sha256(raw).hexdigest()
def encode(v):return (json.dumps(v,separators=(',',':'),allow_nan=False)+'\n').encode()


def reproduce(row,thresholds):
    z=row['depth_levels_m']
    if z!=list(range(10,1001,10)):raise ValueError('Exact existing100-level fitted source grid required')
    selected,scores=source.select_axis(z,row['northward_component_section_columns_m_s'])
    if selected!=row['selected_section_column_index'] or scores!=row['upper10_to200m_component_integrals_m2_s'] or selected is None:raise ValueError('All original northward columns,scores and winner must reproduce')
    status='edge_maximum_axis_unresolved' if selected in [0,len(scores)-1] else 'interior_fitted_section_maximum_not_independently_validated_axis'
    if row['horizontal_selection_status']!=status:raise ValueError('Original axis status required')
    p=row['selected_profile'];values=p['source_values'];mean=values['northward_velocity']
    if p['source_lon_lat']!=[row['section_longitudes'][selected],row['section_latitude']] or mean!=row['northward_component_section_columns_m_s'][selected] or len(mean)!=100:raise ValueError('Original selected source node and northward profile required')
    layers,half=source.diagnose(z,mean,thresholds)
    if layers!=p['absolute_component_threshold_layers'] or half!=p['half_sampled_core_component_decay'] or half is None:raise ValueError('Every nominal absolute/half-core layer must reproduce')
    radius=copy.deepcopy(values['northward_velocity_uncertainty'])
    result=shared.sensitivity(z,mean,radius,half['core_index'],half['threshold_m_s']);expected={k:v for k,v in half.items() if k not in ['relative_sampled_core_fraction','quantity_role']}
    if result['nominal_layer']!=expected:raise ValueError('Locked nominal seed must reproduce original half-core layer exactly')
    return result


def build(root=ROOT):
    op=json.loads((root/OPERATOR).read_bytes())
    if any(op['eligibility'].values()) or op['source_component_SE_multiplier']!=1 or op['component_policy']!='ORIGINAL_NORTHWARD_COMPONENT_AND_NORTHWARD_PROVIDER_SE_ONLY':raise ValueError('Fixed original northward scenario and non-promotion required')
    for p,pin in op['input_sha256'].items():
        if digest((root/p).read_bytes())!=pin:raise ValueError('Pinned source or method changed: '+p)
    source_op=json.loads((root/op['source_operator']).read_bytes());raw=(root/op['source_file']).read_bytes();source_data=json.loads(raw)
    if source_data['schema']!='osw.florida-spray-seasonal-depth.v1' or source_data['entity_context']!='current:florida' or any(source_data['eligibility'].values()):raise ValueError('Exact scoped Florida fitted source required')
    for meta in source_data['source_metadata']:
        a=meta['variable_attributes']['northward_velocity_uncertainty']
        if a['standard_name']!='northward_sea_water_velocity_standard_error' or a['units']!='m s-1' or meta['global_attributes']['product_version']!=op['expected_product_versions'][meta['kind']] or not source.source_doi_matches(meta['global_attributes']['doi']):raise ValueError('Original product and northward fitted standard-error semantics required')
    rows=source_data['records']
    if len(rows)!=13 or {(v['source_product_kind'],v['calendar_month_phase']) for v in rows}!={('mean',None)}|{('annual_cycle',m) for m in range(1,13)}:raise ValueError('One mean and all12 fitted day15phases required')
    cases=[]
    for i,row in enumerate(rows):
        result=reproduce(row,source_op['thresholds_m_s']);cases.append({'entity_id':'current:florida','source_file':op['source_file'],'source_sha256':digest(raw),'source_pointer':'/records/'+str(i),'source_product_kind':row['source_product_kind'],'calendar_month_phase':row['calendar_month_phase'],'actual_provider_phase_timestamp_utc':row['actual_provider_phase_timestamp_utc'],'nominal_phase_calendar_date':row['nominal_phase_calendar_date'],'timestamp_is_instantaneous_observation_date':False,'source_lon_lat':copy.deepcopy(row['selected_profile']['source_lon_lat']),'horizontal_selection_status':row['horizontal_selection_status'],'selected_section_column_index':row['selected_section_column_index'],'component_policy':op['component_policy'],'depth_levels_m':copy.deepcopy(row['depth_levels_m']),'nominal_source_half_core_descriptor':copy.deepcopy(row['selected_profile']['half_sampled_core_component_decay']),'sensitivity':result,'nominal_diagnostics_and_selection_reproduced':True,'horizontal_core_or_direction_reselected':False,'phase_winner_may_shift_spatially':True,'whole_route_representative':False,'physical_state_join_eligible':False,'seasonal_extrema_eligible':False})
    counts={'profile_cases':13,'mean_cases':1,'fitted_day15_phase_cases':12,'status_counts':dict(Counter(c['sensitivity']['status'] for c in cases)),'nominal_lower_status_counts':dict(Counter(c['sensitivity']['nominal_layer']['lower_status'] for c in cases)),'lower_scenario_lower_status_counts':dict(Counter(c['sensitivity']['lower_velocity_scenario_layer']['lower_status'] for c in cases)),'upper_scenario_lower_status_counts':dict(Counter(c['sensitivity']['upper_velocity_scenario_layer']['lower_status'] for c in cases)),'new_ocean_field_requests':0,'new_scalar_depth_references':0,'physical_whole_route_depth_profiles':0,'volume_estimates':0}
    report={'schema':'osw.florida-fit-error-depth-sensitivity.v1','status':'FIXED_NOMINAL_CUTOFF_NORTHWARD_FIT_ERROR_SENSITIVITY_NOT_CONFIDENCE_INTERVAL','operator_file':OPERATOR,'operator_sha256':digest((root/OPERATOR).read_bytes()),'input_sha256':op['input_sha256'],'counts':counts,'source_dataset_doi':source_op['source_dataset_doi'],'source_observation_period_documented':source_op['source_observation_period_documented'],'cases':cases,'interpretation':op['interpretation'],'runtime_changed':False,'full_goal_complete':False};raw=encode(report)
    if len(raw)>=2400000:raise ValueError('Fixed2.4MB output cap exceeded')
    return report,raw


if __name__=='__main__':
    report,raw=build();out=Path('florida-fit-error-depth-sensitivity-v1');out.mkdir(exist_ok=True);(out/'sensitivity.json').write_bytes(raw);print(json.dumps(report['counts']),flush=True)
