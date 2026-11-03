"""Opposing Monsoon component views over one retained native field section."""
import copy
import numpy as np
from interval_depth_diagnostic_v1 import diagnose
from mixed_interval_section_geometry_v1 import validate_retained
from sample_eac_hycom_route_depth_v1 import along_velocity,clean,canonical_hash

SCHEMA='osw.native-direction-context-depth-section.v1'
TARGET='current:monsoon'


def context_config(config,key):
    if config['entity_id']!=TARGET or config['default_direction_context_id']!='eastward' or set(config['direction_contexts'])!={'eastward','westward'}:raise ValueError('Monsoon owner and both fixed contexts required')
    expected={'eastward':90,'westward':270}
    for name,c in config['direction_contexts'].items():
        if (c['id']!=name or c['component_bearing_degrees_true']!=expected[name] or c['selection_depth_interval_m']!=[0,100] or c['core_search_depth_interval_m']!=[0,100]
            or c['primary_threshold_m_s']!=.1 or c['surface_component_gate_m_s'] is not None or c.get('temperature_gate') is not None):raise ValueError('Predeclared Monsoon frame/window/primary changed')
    return {**config,**config['direction_contexts'][key]}


def context_view(section,config,key):
    cfg=context_config(config,key);virtual=copy.deepcopy(section);virtual['component_bearing_degrees_true']=cfg['component_bearing_degrees_true']
    for column in virtual['columns']:
        u=np.asarray([np.nan if x is None else x for x in column['eastward_velocity_m_s']]);v=np.asarray([np.nan if x is None else x for x in column['northward_velocity_m_s']])
        signed=along_velocity(u,v,cfg['component_bearing_degrees_true'])
        column['signed_reference_component_m_s']=clean(np.where(np.isfinite(u)&np.isfinite(v),signed,np.nan))
    virtual['decoded_columns_sha256']=canonical_hash(virtual['columns'])
    virtual['diagnosis']=diagnose(virtual['depth_levels_m'],[c['signed_reference_component_m_s'] for c in virtual['columns']],cfg)
    validate_retained(virtual,cfg)
    return virtual


def derive_contexts(section,config):
    result={}
    for key in ['eastward','westward']:
        cfg=context_config(config,key);view=context_view(section,config,key)
        result[key]={'context_id':key,'entity_id':TARGET,'component_bearing_degrees_true':cfg['component_bearing_degrees_true'],
                     'selection_depth_interval_m':[0,100],'core_search_depth_interval_m':[0,100],'primary_threshold_m_s':.1,
                     'profiles':[{'sampled_lon_lat':c['sampled_lon_lat'],'source_native_profile_pointer':'/columns/'+str(i),
                                  'component_bearing_degrees_true':cfg['component_bearing_degrees_true'],'signed_reference_component_m_s':c['signed_reference_component_m_s']} for i,c in enumerate(view['columns'])],
                     'decoded_virtual_columns_sha256':view['decoded_columns_sha256'],'diagnosis':view['diagnosis'],
                     'direction_contexts_are_additive':False,'contexts_are_independent_observations':False,'surface_undercurrent_separation_performed':False}
    return result


def validate_contexts(section,config):
    if (section['schema']!=SCHEMA or section['entity_id']!=TARGET or section['default_direction_context_id']!='eastward'
        or section['direction_contexts_are_additive'] is not False or section['contexts_are_independent_observations'] is not False
        or section['surface_undercurrent_separation_performed'] is not False):raise ValueError('Native directional source semantics changed')
    validate_retained(section,context_config(config,'eastward'))
    expected=derive_contexts(section,config)
    if section['direction_contexts']!=expected or section['diagnosis']!=expected['eastward']['diagnosis']:raise ValueError('Retained direction profiles/default/diagnoses changed')
    return True
