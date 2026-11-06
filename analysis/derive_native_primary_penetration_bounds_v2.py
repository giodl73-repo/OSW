"""Audit frozen classic latitude studies with distinct native censoring classes."""
import copy,hashlib,json,math
from latitude_depth_section_geometry_v1 import validate_retained
from build_current_depth_route_projections_v18 import full_section_cases,INTERIOR
from derive_florida_primary_penetration_bounds_v1 import bound_at_original_node as missing_bound


def bound_at_original_node(section,config):
    d=section['diagnosis'];selected=d['selected_column_index']
    if selected is None or d['horizontal_selection_status']!=INTERIOR:
        return {'reach_eligible':False,'lower_bound_m':None,'reason':'original_axis_proxy_not_interior'}
    primary=next((x for x in d['selected_column_threshold_layers'] if x['threshold_m_s']==config['primary_threshold_m_s']),None)
    if primary is None:raise ValueError('Original primary layer required')
    z=section['depth_levels_m'];v=section['columns'][selected]['signed_reference_component_m_s']
    if primary['lower_status']!='censored_at_sample_domain_edge':
        result=missing_bound(section,config)
        if result['reach_eligible']:result.update(censoring_kind='missing_signed_component_level',native_domain_deep_limit_m=z[-1],native_level_count=len(z))
        return result
    if primary['lower_depth_m'] is not None:raise ValueError('Domain-censored layer cannot have a resolved lower boundary')
    if primary['upper_status']!='surface_bounded_layer' or primary['upper_depth_m']!=0:
        return {'reach_eligible':False,'lower_bound_m':None,'reason':'primary_layer_not_surface_connected'}
    last=primary['lower_last_connected_depth_m']
    if len(v)!=len(z) or last!=z[-1] or last<=0 or any(x is None or not math.isfinite(x) or x<=config['primary_threshold_m_s'] for x in v):raise ValueError('Domain-censored bound requires full contiguous native support through the final level')
    return {'reach_eligible':True,'reason':'surface_connected_primary_reach_censored_at_native_domain_limit','censoring_kind':'native_vertical_domain_limit','lower_bound_m':last,'last_connected_native_index':len(z)-1,'last_connected_velocity_m_s':v[-1],'next_native_index':None,'next_native_depth_m':None,'next_signed_component_m_s':None,'native_domain_deep_limit_m':z[-1],'native_level_count':len(z),'primary_layer':copy.deepcopy(primary)}


def audit_and_derive(root,op):
    read=lambda f:json.loads((root/f).read_bytes());sop=read(op['source_operator_file']);manifest=read(op['source_manifest_file']);ledger=read(op['source_ledger_file']);facts=read(op['source_facts_file']);pop=read(op['original_projection_operator_file'])
    source_sha=hashlib.sha256((root/op['source_operator_file']).read_bytes()).hexdigest()
    if sop['core_search_depth_interval_m']!=[0,200] or len(set(op['target_entities']))!=len(op['target_entities']) or not set(op['target_entities'])<=set(sop['currents']):raise ValueError('Declared classic upper200m target contexts required')
    for entity in op['target_entities']:
        config=sop['currents'][entity]
        if any(config[k]!=pop['currents'][entity][k] for k in ['entity_id','component_bearing_degrees_true','primary_threshold_m_s','surface_component_gate_m_s','temperature_gate','branch_scope']):raise ValueError('Original per-current frame/primary/selection context changed')
    if manifest['operator_file']!=op['source_operator_file'] or manifest['operator_sha256']!=source_sha or manifest['input_sha256']!=sop['input_sha256'] or facts['operator_sha256']!=source_sha or facts['manifest_sha256']!=hashlib.sha256((root/op['source_manifest_file']).read_bytes()).hexdigest():raise ValueError('Frozen source operator/manifest/facts custody changed')
    if manifest['transport']!=ledger or manifest['transport_ledger_sha256']!=hashlib.sha256((root/op['source_ledger_file']).read_bytes()).hexdigest():raise ValueError('Original transport ledger custody changed')
    expected=[(t,s['entity_id'],s['id']) for t in sop['snapshot_times_utc'] for s in sop['sections']]
    if [(m['snapshot_time_utc'],m['entity_id'],m['section_id']) for m in manifest['sections']]!=expected:raise ValueError('All original section/date cases and order required')
    chunks={};pairs=0;arraybytes=0;expected_reads=[];profiles=0
    for meta in manifest['sections']:
        f=op['source_directory']+meta['file'];raw=(root/f).read_bytes()
        if len(raw)!=meta['bytes'] or hashlib.sha256(raw).hexdigest()!=meta['sha256']:raise ValueError('Original retained section bytes changed')
        s=json.loads(raw);config={**sop,**sop['currents'][s['entity_id']]};validate_retained(s,config)
        if s['operator_file']!=op['source_operator_file'] or s['operator_sha256']!=source_sha or s['input_sha256']!=sop['input_sha256'] or s['opendap_dataset']!=sop['opendap_dataset'] or s['source_product']!=sop['source_product'] or s['source_global_attributes'].get('field_type')!='instantaneous' or s['snapshot_time_utc'] not in sop['snapshot_times_utc']:raise ValueError('Source identity/product/time changed')
        for name,standard in [('water_u','eastward_sea_water_velocity'),('water_v','northward_sea_water_velocity')]:
            if s['source_variable_attributes'][name]['units']!='m/s' or s['source_variable_attributes'][name]['standard_name']!=standard:raise ValueError('Frozen source velocity units/frame required')
        if len(s['depth_levels_m'])!=40 or s['depth_levels_m'][0]!=0 or s['depth_levels_m'][-1]!=5000 or any(b<=a for a,b in zip(s['depth_levels_m'],s['depth_levels_m'][1:])):raise ValueError('Full native 0-5000m support required')
        for column in s['columns']:
            for name in ['eastward_velocity_m_s','northward_velocity_m_s','signed_reference_component_m_s']:
                values=column[name]
                if len(values)!=40 or any(v is not None and (not math.isfinite(v) or abs(v)>10) for v in values):raise ValueError('Standard source velocity shape/scaling guard')
        n=len(s['columns'])*40;pairs+=n;arraybytes+=n*8;profiles+=len(s['columns']);slab=s['retrieved_hyperslab']
        for name in ['water_u','water_v']:expected_reads.append((name,slab,n))
        if any(meta[k]!=s['diagnosis'][k] for k in ['selected_column_index','horizontal_selection_status','selected_column_threshold_layers']) or meta['native_columns']!=len(s['columns']):raise ValueError('Manifest representative diagnosis changed')
        chunks[f]=s
    if len(ledger['requests'])!=len(expected_reads) or ledger['additional_retry_component_values_reserved']!=0:raise ValueError('Original successful no-retry request plan required')
    for row,(name,slab,n) in zip(ledger['requests'],expected_reads):
        if row['status']!='success' or row['attempt']!=1 or row['variable']!=name or row['source_time_index']!=slab['time_index'] or row['latitude_index']!=slab['latitude_index'] or row['longitude_indices_inclusive']!=slab['longitude_indices_inclusive'] or row['depth_indices_inclusive']!=[0,39] or row['requested_component_values']!=n or row['actual_returned_array_bytes']!=n*4:raise ValueError('Original exact component request/frame/slice custody changed')
    if any(ledger[k]!=pairs*2 for k in ['planned_successful_component_values','actual_requested_component_values','successfully_returned_component_values']) or manifest['preflight_velocity_cell_pairs']!=pairs or manifest['decoded_velocity_cell_pairs']!=pairs or manifest['decoded_velocity_array_bytes']!=arraybytes or pairs>sop['maximum_total_cell_pairs'] or pairs*16>sop['maximum_total_decoded_velocity_bytes']:raise ValueError('Frozen source budgets/counts changed')
    if ledger['maximum_requested_component_values']!=2*sop['maximum_total_cell_pairs'] or ledger['maximum_decoded_byte_bound']!=sop['maximum_total_decoded_velocity_bytes'] or ledger['conservative_all_target_plus_retries_decoded_byte_bound']!=pairs*16 or ledger['maximum_attempts_per_component']!=3:raise ValueError('Original transport ceilings changed')
    generated,blocked=full_section_cases(facts,chunks,pop)
    for c in generated+blocked:c['source_surface_component_gate_m_s']=pop['currents'][c['entity_id']]['surface_component_gate_m_s']
    original=read(op['original_projection_addendum_file'])
    if generated!=original['projections'] or blocked!=original['unresolved_reference_cases']:raise ValueError('Original regional projections and gaps must reproduce unchanged')
    records=[]
    for meta in manifest['sections']:
        if meta['entity_id'] not in op['target_entities']:continue
        config={**sop,**sop['currents'][meta['entity_id']]}
        f=op['source_directory']+meta['file'];s=chunks[f];selected=s['diagnosis']['selected_column_index'];primary=next((l for l in s['diagnosis']['selected_column_threshold_layers'] if l['threshold_m_s']==config['primary_threshold_m_s']),None)
        records.append({'entity_id':meta['entity_id'],'branch_scope':config['branch_scope'],'snapshot_time_utc':s['snapshot_time_utc'],'section_id':s['section_definition']['id'],'source_section_file':f,'source_section_sha256':meta['sha256'],'selected_column_index':selected,'source_profile_ref':f+'#/columns/'+str(selected) if selected is not None else None,'source_connected_layer_ref':f+'#/diagnosis/selected_column_threshold_layers/'+str(s['diagnosis']['selected_column_threshold_layers'].index(primary)) if primary else None,'sampled_lon_lat':s['columns'][selected]['sampled_lon_lat'] if selected is not None else None,'horizontal_selection_status':s['diagnosis']['horizontal_selection_status'],'primary_threshold_m_s':config['primary_threshold_m_s'],'surface_component_gate_m_s':config['surface_component_gate_m_s'],'component_bearing_degrees_true':config['component_bearing_degrees_true'],'core_search_depth_interval_m':config['core_search_depth_interval_m'],'primary_layer':copy.deepcopy(primary),**bound_at_original_node(s,config)})
    return {'schema':'osw.native-primary-censored-penetration-source-report.v1','source_operator_file':op['source_operator_file'],'source_operator_sha256':source_sha,'source_manifest_file':op['source_manifest_file'],'source_manifest_sha256':hashlib.sha256((root/op['source_manifest_file']).read_bytes()).hexdigest(),'source_audit':{'sections_verified':len(chunks),'native_profiles_verified':profiles,'native_cell_pairs_verified':pairs,'original_component_requests_verified':len(expected_reads),'decoded_velocity_array_bytes':arraybytes,'original_region_cases_and_gaps_unchanged':True,'new_field_requests':0,'physical_current_identity_validated':False},'records':records,'admitted_supported_reach_bounds':sum(r['reach_eligible'] for r in records),'physical_current_bottom_established':False,'source_missing_values_interpreted_as_bed':False,'interpolation_performed':False,'runtime_changed':False,'full_goal_complete':False}
