"""Audit frozen interval studies and derive core-connected minimum sampled reach."""
import copy,hashlib,json,math
from pathlib import Path
from mixed_interval_section_geometry_v1 import validate_retained
from interval_depth_diagnostic_v1 import INTERIOR
from build_current_depth_route_projections_v40 import full_section_cases as barents_cases
from build_current_depth_route_projections_v43 import full_section_cases as coastal_cases
from build_current_depth_route_projections_v49 import full_section_cases as guiana_cases

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/interval-core-connected-reach-audit-operator-v1.json'
FROZEN_CASES={'barents-makassar':barents_cases,'coastal-upper-layer':coastal_cases,'guiana-egcc':guiana_cases}


def bound_at_original_node(section,config):
    diagnosis=section['diagnosis'];selected=diagnosis['selected_column_index'];no=lambda why:{'reach_eligible':False,'lower_bound_m':None,'reason':why}
    if selected is None or diagnosis['horizontal_selection_status']!=INTERIOR:return no('original_axis_proxy_not_interior')
    layer=next(x for x in diagnosis['selected_column_threshold_layers'] if x['threshold_m_s']==config['primary_threshold_m_s'])
    if layer['lower_depth_m'] is not None:return no('resolved_primary_boundary_not_relabelled_as_censored_reach')
    if layer['lower_status'] not in ['censored_before_missing_or_dry_level','censored_at_sample_domain_edge']:return no('not_a_declared_native_lower_censoring_class')
    z=section['depth_levels_m'];v=section['columns'][selected]['signed_reference_component_m_s'];last=layer['lower_last_connected_depth_m'];core=layer['core_index']
    if len(z)!=len(v) or z.count(last)!=1 or not 0<=core<len(z) or z[core]!=layer['core_depth_m'] or not config['core_search_depth_interval_m'][0]<=z[core]<=config['core_search_depth_interval_m'][1] or last<=0:raise ValueError('Exact original native core and positive last supported level required')
    i=z.index(last)
    if i<core or any(x is None or not math.isfinite(x) or x<=config['primary_threshold_m_s'] for x in v[core:i+1]):raise ValueError('No missing/weak bridge from original core to supported reach')
    domain=layer['lower_status']=='censored_at_sample_domain_edge'
    if domain:
        if i!=len(z)-1:raise ValueError('Domain-censored reach must end at final native level')
    elif i+1>=len(z) or v[i+1] is not None:raise ValueError('Missing-level censoring must stop before first missing signed component')
    return {'reach_eligible':True,'reason':'original_primary_core_connected_support_with_unresolved_lower_boundary','lower_bound_m':last,'lower_bound_operator':'>=','censoring_kind':'native_vertical_domain_limit' if domain else 'missing_signed_component_level','core_native_index':core,'core_depth_m':z[core],'core_velocity_m_s':v[core],'last_connected_native_index':i,'last_connected_velocity_m_s':v[i],'next_native_index':None if domain else i+1,'next_native_depth_m':None if domain else z[i+1],'next_signed_component_m_s':None,'source_native_domain_deep_limit_m':z[-1],'source_native_level_count':len(z),'primary_layer':copy.deepcopy(layer),'source_surface_connection_established':layer['upper_status']=='surface_bounded_layer' and layer['upper_depth_m']==0,'physical_current_bottom_established':False,'physical_layer_thickness_m':None}


def audit_study(root,study):
    read=lambda f:json.loads((root/f).read_bytes());sop=read(study['source_operator_file']);pop=read(study['projection_operator_file']);manifest=read(study['manifest_file']);ledger=read(study['ledger_file']);facts=read(study['source_facts_file']);digest=lambda f:hashlib.sha256((root/f).read_bytes()).hexdigest()
    if manifest['operator_file']!=study['source_operator_file'] or manifest['operator_sha256']!=digest(study['source_operator_file']) or facts['operator_sha256']!=manifest['operator_sha256'] or facts['manifest_sha256']!=digest(study['manifest_file']) or manifest['input_sha256']!=sop['input_sha256']:raise ValueError('Original source custody mismatch')
    if manifest['transport']!=ledger or manifest['transport_ledger_sha256']!=digest(study['ledger_file']) or facts['transport_ledger_sha256']!=digest(study['ledger_file']):raise ValueError('Original transport custody mismatch')
    expected=[(t,s['entity_id'],s['id']) for t in sop['snapshot_times_utc'] for s in sop['sections']]
    if [(m['snapshot_time_utc'],m['entity_id'],m['section_id']) for m in manifest['sections']]!=expected:raise ValueError('All original source/date cases and order required')
    chunks={};reads=[];profiles=0;pairs=0;arraybytes=0;records=[]
    for meta in manifest['sections']:
        f=study['source_directory']+meta['file'];raw=(root/f).read_bytes()
        if len(raw)!=meta['bytes'] or hashlib.sha256(raw).hexdigest()!=meta['sha256']:raise ValueError('Original section bytes changed')
        section=json.loads(raw);entity=section['entity_id'];config={**sop,**sop['currents'][entity]};validate_retained(section,config)
        if config['surface_component_gate_m_s'] is not None or config['temperature_gate'] is not None or any(config[k]!=pop['currents'][entity][k] for k in ['component_bearing_degrees_true','primary_threshold_m_s','selection_depth_interval_m','core_search_depth_interval_m','surface_component_gate_m_s','temperature_gate']):raise ValueError('Original per-current interval/frame/gates changed')
        if section['operator_file']!=study['source_operator_file'] or section['operator_sha256']!=manifest['operator_sha256'] or section['source_global_attributes'].get('field_type')!='instantaneous' or section['source_product']!=sop['source_product'] or section['opendap_dataset']!=sop['opendap_dataset'] or section['depth_levels_m'][0]!=0 or section['depth_levels_m'][-1]!=5000 or len(section['depth_levels_m'])!=40:raise ValueError('Original instantaneous source/native domain changed')
        for name,standard in [('water_u','eastward_sea_water_velocity'),('water_v','northward_sea_water_velocity')]:
            attrs=section['source_variable_attributes'][name]
            if attrs['units']!='m/s' or attrs['standard_name']!=standard:raise ValueError('Original signed velocity units/frame changed')
        for column in section['columns']:
            for key in ['eastward_velocity_m_s','northward_velocity_m_s','signed_reference_component_m_s']:
                if len(column[key])!=40 or any(x is not None and (not math.isfinite(x) or abs(x)>10) for x in column[key]):raise ValueError('Original standard finite/scaling guard')
        d=section['diagnosis'];selected=d['selected_column_index'];layers=d['selected_column_threshold_layers'];primary=next((x for x in layers if x['threshold_m_s']==config['primary_threshold_m_s']),None)
        if meta['native_columns']!=len(section['columns']) or any(meta[k]!=d[k] for k in ['selected_column_index','horizontal_selection_status','selected_column_threshold_layers']):raise ValueError('Original manifest selection changed')
        n=len(section['columns'])*40;profiles+=len(section['columns']);pairs+=n;arraybytes+=n*8;slab=section['retrieved_hyperslab']
        for name in ['water_u','water_v']:reads.append((name,slab,n))
        chunks[f]=section
        records.append({'study_id':study['id'],'entity_id':entity,'snapshot_time_utc':section['snapshot_time_utc'],'section_id':section['section_definition']['id'],'source_section_file':f,'source_section_sha256':meta['sha256'],'selected_column_index':selected,'source_profile_ref':f+'#/columns/'+str(selected) if selected is not None else None,'source_primary_layer_ref':f+'#/diagnosis/selected_column_threshold_layers/'+str(layers.index(primary)) if primary else None,'sampled_lon_lat':section['columns'][selected]['sampled_lon_lat'] if selected is not None else None,'horizontal_selection_status':d['horizontal_selection_status'],'primary_threshold_m_s':config['primary_threshold_m_s'],'component_bearing_degrees_true':config['component_bearing_degrees_true'],'selection_depth_interval_m':config['selection_depth_interval_m'],'core_search_depth_interval_m':config['core_search_depth_interval_m'],'surface_component_gate_m_s':None,'branch_scope':config['branch_scope'],'primary_layer':copy.deepcopy(primary),**bound_at_original_node(section,config)})
    if len(reads)!=len(ledger['requests']) or ledger['additional_retry_component_values_reserved']!=0:raise ValueError('Original successful no-retry request plan required')
    for row,(name,slab,n) in zip(ledger['requests'],reads):
        keys=['time_index','depth_indices_inclusive','latitude_indices_inclusive','longitude_index'] if 'longitude_index' in slab else ['time_index','depth_indices_inclusive','latitude_index','longitude_indices_inclusive']
        if row['status']!='success' or row['attempt']!=1 or row['variable']!=name or row['requested_component_values']!=n or row['actual_returned_array_bytes']!=n*4 or any(row['source_time_index' if k=='time_index' else k]!=slab[k] for k in keys):raise ValueError('Original exact component request/slice ledger changed')
    if any(ledger[k]!=pairs*2 for k in ['planned_successful_component_values','actual_requested_component_values','successfully_returned_component_values']) or manifest['decoded_velocity_cell_pairs']!=pairs or manifest['preflight_velocity_cell_pairs']!=pairs or manifest['decoded_velocity_array_bytes']!=arraybytes or pairs>sop['maximum_total_cell_pairs'] or pairs*16>sop['maximum_total_decoded_velocity_bytes']:raise ValueError('Original source accounting/caps changed')
    if ledger['maximum_requested_component_values']!=2*sop['maximum_total_cell_pairs'] or ledger['maximum_decoded_byte_bound']!=sop['maximum_total_decoded_velocity_bytes'] or ledger['conservative_all_target_plus_retries_decoded_byte_bound']!=pairs*16:raise ValueError('Original transport ceilings changed')
    generated,blocked=FROZEN_CASES[study['id']](facts,chunks,pop)
    for case in generated+blocked:case['source_surface_component_gate_m_s']=pop['currents'][case['entity_id']]['surface_component_gate_m_s']
    original=read(study['original_projection_addendum_file'])
    if generated!=original['projections'] or blocked!=original['unresolved_reference_cases']:raise ValueError('Original regional projections/gaps must reproduce exactly')
    return {'study_id':study['id'],'source_sections_verified':len(chunks),'native_profiles_verified':profiles,'native_cell_pairs_verified':pairs,'decoded_velocity_array_bytes':arraybytes,'original_component_requests_verified':len(reads),'original_projections_and_gaps_unchanged':True,'records':records,'eligible_core_connected_reach_bounds':sum(r['reach_eligible'] for r in records)}


def build(root=ROOT):
    op=json.loads((root/OPERATOR).read_bytes())
    if [s['id'] for s in op['studies']]!=['barents-makassar','coastal-upper-layer','guiana-egcc'] or any(op['eligibility'].values()):raise ValueError('Complete predeclared study set and no physical promotion required')
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256((root/f).read_bytes()).hexdigest()!=pin:raise ValueError('Pinned interval audit input changed: '+f)
    studies=[audit_study(root,s) for s in op['studies']]
    if sum(s['native_cell_pairs_verified'] for s in studies)>250000 or sum(s['native_cell_pairs_verified'] for s in studies)*16>7000000:raise ValueError('Predeclared joint source audit ceiling exceeded')
    return {'schema':'osw.interval-core-connected-reach-audit.v1','operator_file':OPERATOR,'operator_sha256':hashlib.sha256((root/OPERATOR).read_bytes()).hexdigest(),'input_sha256':op['input_sha256'],'studies':studies,'eligible_core_connected_reach_bounds':sum(s['eligible_core_connected_reach_bounds'] for s in studies),'new_ocean_field_requests':0,'new_reference_inventory_rows_admitted':0,'reference_inventory_updated':False,'physical_current_bottom_established':False,'runtime_changed':False,'full_goal_complete':False}


def main():
    report=build();out=Path('interval-core-connected-reach-audit-v1');out.mkdir(exist_ok=True);raw=(json.dumps(report,separators=(',',':'),allow_nan=False)+'\n').encode()
    if len(raw)>=2500000:raise ValueError('Fixed per-file publication cap exceeded')
    (out/'source-report.json').write_bytes(raw)
    print(json.dumps({'eligible_bounds':report['eligible_core_connected_reach_bounds'],'study_counts':[{k:s[k] for k in s if k!='records'} for s in report['studies']],'eligible_nodes':[{'entity':r['entity_id'],'date':r['snapshot_time_utc'],'section':r['section_id'],'minimum_native_reach_m':r['lower_bound_m'],'censoring_kind':r['censoring_kind'],'surface_connection_established':r['source_surface_connection_established']} for s in report['studies'] for r in s['records'] if r['reach_eligible']],'new_ocean_field_requests':0,'new_reference_inventory_rows_admitted':0}))


if __name__=='__main__':main()
