"""Exact legacy binary32 component replay with frozen pre-tag geometry and tracing bodies."""
import copy,math
import numpy as np
import acquire_north_brazil_depth_sections_v1 as legacy
from native_velocity_depth_curtain_v2 import component,runs,connected_layer,digest,encode
from interval_depth_diagnostic_v1 import INTERIOR
GEOD=legacy.GEOD
original_diagnose=legacy.diagnose


def diagnose(z,columns,config,temperatures=None):
    if temperatures is not None or config.get('temperature_gate') is not None:raise ValueError('Legacy NBC has no thermal gate')
    return original_diagnose(z,columns,config)


def validate_original_components(section,config):
    if section['entity_id']!='current:north-brazil' or config['entity_id']!=section['entity_id'] or section['component_bearing_degrees_true']!=config['component_bearing_degrees_true'] or config['component_bearing_degrees_true']!=315 or section['eligibility']!=config['eligibility'] or any(config['eligibility'].values()):raise ValueError('Exact original NBC identity/frame/eligibility required')
    if section['native100m_temperature_degrees_celsius'] is not None or section.get('temperature_source') is not None or config.get('temperature_gate') is not None:raise ValueError('No thermal data or gate on legacy source')
    z=section['depth_levels_m'];columns=section['columns']
    if len(z)!=40 or not 3<=len(columns)<=150 or len(z)*len(columns)>6000:raise ValueError('Original bounded native section required')
    if legacy.canonical_hash(columns)!=section['decoded_columns_sha256']:raise ValueError('Alias-view checksum mismatch')
    original=copy.deepcopy(section);original['section_definition'].pop('entity_id');original.pop('native100m_temperature_degrees_celsius');original.pop('temperature_source')
    for column in original['columns']:column['signed_northwest_component_m_s']=column.pop('signed_reference_component_m_s')
    original['decoded_columns_sha256']=config['legacy_original_decoded_columns_sha256'];legacy.validate_retained(original,config)
    for column in columns:
        if any(len(column[key])!=len(z) for key in ['eastward_velocity_m_s','northward_velocity_m_s','signed_reference_component_m_s']):raise ValueError('Original profile shape changed')
        u=np.asarray([np.nan if x is None else x for x in column['eastward_velocity_m_s']],dtype=np.float32);v=np.asarray([np.nan if x is None else x for x in column['northward_velocity_m_s']],dtype=np.float32)
        if legacy.clean(u)!=column['eastward_velocity_m_s'] or legacy.clean(v)!=column['northward_velocity_m_s']:raise ValueError('Original binary32 component representation required')
        signed=legacy.along_velocity(u,v,315);signed=np.where(np.isfinite(u)&np.isfinite(v),signed,np.nan)
        if legacy.clean(signed)!=column['signed_reference_component_m_s']:raise ValueError('Exact original binary32 signed component mismatch')


def validate_retained(section,config):
    # Preserve the original pre-tag collector format and component audit.
    validate_original_components(section,config)
    definition=section['section_definition'];profiles=section['columns'];slab=section['retrieved_hyperslab'];z=section['depth_levels_m']
    matches=[d for d in config['sections'] if d['entity_id']==section['entity_id'] and d['id']==definition['id']]
    if len(matches)!=1 or definition!=matches[0] or 'fixed_axis' in definition or 'source_section_geometry' in section:raise ValueError('Exact original pre-tag source definition required')
    if len(z)!=40 or z[0]!=0 or z[-1]!=5000 or not 3<=len(profiles)<=150 or slab['depth_indices_inclusive']!=[0,39] or slab['time_index']!=section['source_time_index']:raise ValueError('Original bounded native hyperslab required')
    indices=[p['global_longitude_index'] for p in profiles];longitudes=[p['sampled_lon_lat'][0] for p in profiles]
    if indices!=list(range(indices[0],indices[0]+len(profiles))) or any(b<=a for a,b in zip(longitudes,longitudes[1:])) or slab['longitude_indices_inclusive']!=[indices[0],indices[-1]]:raise ValueError('Original native west-to-east slice required')
    native=section['actual_source_latitude_degrees_north'];west,east=definition['longitude_gate_degrees_east']
    if type(native) not in (int,float) or not math.isfinite(native) or not -90<=native<=90:raise ValueError('Original finite latitude required')
    for p in profiles:
        if 'native_source_latitude_degrees_north' in p or p['sampled_lon_lat'][1]!=native or p['global_latitude_index']!=slab['latitude_index'] or not west<=p['sampled_lon_lat'][0]<=east:raise ValueError('Original fixed native latitude and declared longitude gate required')
    # EXACT original collector convention, including its fixed -45deg meridian.
    distance=GEOD.inv(-45,definition['latitude_degrees_north'],-45,native)[2]/1000
    if distance!=section['nearest_latitude_distance_km'] or distance>config['maximum_nearest_latitude_distance_km']:raise ValueError('Original native latitude offset changed')


def curtain(section,config,file):
    # Reproduce frozen native geometry, component rotation, full candidate scores
    # and selection. A more favorable or better resolved core is never substituted.
    threshold=config['primary_threshold_m_s']
    if type(threshold) not in (int,float) or threshold<=0 or config['thresholds_m_s'].count(threshold)!=1:raise ValueError('Exact source primary threshold required')
    validate_retained(section,config)
    z=section['depth_levels_m'];columns=section['columns'];velocity=[c['signed_reference_component_m_s'] for c in columns]
    original=section['diagnosis'];reproduced=diagnose(z,velocity,config,section['native100m_temperature_degrees_celsius'])
    if reproduced!=original:raise ValueError('Every original candidate/selection/layer must reproduce exactly')
    selected=original['selected_column_index'];primary=original['selected_column_threshold_layers'][config['thresholds_m_s'].index(threshold)] if selected is not None else None
    result={'entity_id':section['entity_id'],'section_id':section['section_definition']['id'],'snapshot_time_utc':section['snapshot_time_utc'],'source_file':file,'source_sha256':digest(encode(section)),'source_geometry':{'section_definition':copy.deepcopy(section['section_definition']),'retrieved_hyperslab':copy.deepcopy(section['retrieved_hyperslab']),'maximum_nearest_latitude_distance_km':config['maximum_nearest_latitude_distance_km'],'actual_source_latitude_degrees_north':section['actual_source_latitude_degrees_north'],'nearest_latitude_distance_km':section['nearest_latitude_distance_km']},'component_bearing_degrees_true':section['component_bearing_degrees_true'],'original_horizontal_selection_status':original['horizontal_selection_status'],'original_selected_column_index':selected,'original_primary_layer':copy.deepcopy(primary),'depth_levels_m':copy.deepcopy(z),'velocity_threshold_m_s':threshold,'connectivity':'four_native_axis_neighbors_no_diagonal_or_missing_bridge','status':'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN','columns':[],'native_input_column_count':len(columns),'connected_native_node_count':0,'core_reselected':False,'water_mass_classification_performed':False,'native_surface_seed_connected':False,'named_current_axis_independently_validated':False,'physical_current_bottom_established':False,'physical_thickness_m':None,'width_m':None,'cross_section_area_m2':None,'volume_m3':None,'annual_extrema_established':False}
    result['original_horizontal_temperature_gate']=copy.deepcopy(config.get('temperature_gate'))
    temperatures=section['native100m_temperature_degrees_celsius']
    result['original_selected_native100m_temperature_degrees_celsius']=temperatures[selected] if temperatures is not None and selected is not None else None
    result['temperature_screen_applied_to_connected_nodes']=False
    result['temperature_support_policy']='ORIGINAL_NATIVE100M_GATE_FOR_HORIZONTAL_SELECTION_ONLY_NO_3D_TEMPERATURE_MEMBERSHIP'
    if original['horizontal_selection_status']!=INTERIOR:return result
    if primary is None or primary.get('core_index') is None:return {**result,'status':'ORIGINAL_PRIMARY_CORE_UNRESOLVED_NO_CURTAIN'}
    core=primary['core_index'];nodes=component(z,velocity,selected,core,threshold);found=False
    for index,column in enumerate(columns):
        descriptors=[]
        for first,last in runs(nodes,index):
            layer=connected_layer(z,velocity[index],threshold,[z[first],z[first]])
            # This single-depth interval merely seeds an already connected run;
            # it does not reselect the original current core or truncate tracing.
            if layer.get('core_index')!=first:raise ValueError('Frozen boundary routine must seed the declared run')
            contains=index==selected and first<=core<=last
            if contains:
                expected=copy.deepcopy(layer)
                for key in ['core_index','core_depth_m','core_velocity_m_s']:expected[key]=primary[key]
                if expected!=primary:raise ValueError('Original seed-run boundaries must reproduce exactly')
                found=True
            descriptors.append({'native_depth_indices_inclusive':[first,last],'contains_original_core':contains,'threshold_layer':layer})
        result['columns'].append({'native_column_index':index,'global_longitude_index':column['global_longitude_index'],'global_latitude_index':column['global_latitude_index'],'sampled_lon_lat':copy.deepcopy(column['sampled_lon_lat']),'status':'ORIGINAL_SEED_CONNECTED_SUPPORT' if descriptors else 'NO_SEED_CONNECTED_SUPPORT_NOT_CURRENT_ABSENCE','connected_depth_runs':descriptors})
    if not found:raise ValueError('Original seed must remain in its curtain')
    result['native_surface_seed_connected']=any(y==0 and z[y]==0 for x,y in nodes)
    result.update(status='REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN',connected_native_node_count=len(nodes),lateral_gate_censored=any(x in [0,len(columns)-1] for x,y in nodes))
    return result
