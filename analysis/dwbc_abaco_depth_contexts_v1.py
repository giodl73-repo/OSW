"""Reuse frozen diagnostics for two non-additive vertical search contexts."""
import copy
from interval_depth_diagnostic_v1 import diagnose
from mixed_interval_section_geometry_v1 import validate_retained

SCHEMA='osw.multi-context-interval-depth-section.v1'


def context_config(config,key):
    contexts=config['diagnostic_contexts']
    if set(contexts)!={'upper','lower'} or config['default_diagnostic_context_id']!='upper':raise ValueError('Both declared contexts with upper default required')
    if config['entity_id']!='current:deep-western-boundary' or config['component_bearing_degrees_true']!=180:raise ValueError('Abaco DWBC southward owner/frame required')
    expected={'upper':[1000,3000],'lower':[3000,5000]}
    for name,definition in contexts.items():
        if definition['id']!=name or definition['selection_depth_interval_m']!=expected[name] or definition['core_search_depth_interval_m']!=expected[name] or definition['primary_threshold_m_s']!=.1:raise ValueError('Predeclared context window/cutoff changed')
    if config['surface_component_gate_m_s'] is not None or config.get('temperature_gate') is not None:raise ValueError('No surface or thermal gate allowed')
    return {**config,**contexts[key]}


def diagnose_contexts(z,columns,config):
    return {key:{'context_id':key,'selection_depth_interval_m':context_config(config,key)['selection_depth_interval_m'],
                 'core_search_depth_interval_m':context_config(config,key)['core_search_depth_interval_m'],
                 'primary_threshold_m_s':context_config(config,key)['primary_threshold_m_s'],
                 'diagnosis':diagnose(z,columns,context_config(config,key))} for key in ['upper','lower']}


def validate_contexts(section,config):
    if (section['schema']!=SCHEMA or section['entity_id']!=config['entity_id']
        or section['default_diagnostic_context_id']!='upper'
        or section['vertical_contexts_are_additive'] is not False
        or section['contexts_are_independent_observations'] is not False
        or set(section['context_diagnoses'])!={'upper','lower'}):raise ValueError('Retained context identity/non-additive semantics changed')
    for key in ['upper','lower']:
        cfg=context_config(config,key);entry=section['context_diagnoses'][key]
        if entry['context_id']!=key or any(entry[k]!=cfg[k] for k in ['selection_depth_interval_m','core_search_depth_interval_m','primary_threshold_m_s']):raise ValueError('Retained context configuration changed')
        # Only an in-memory diagnostic view changes; retained arrays/hash/owner stay exact.
        virtual=copy.copy(section);virtual['diagnosis']=entry['diagnosis']
        validate_retained(virtual,cfg)
    if section['diagnosis']!=section['context_diagnoses']['upper']['diagnosis']:raise ValueError('Default diagnosis is not the declared upper context')
    return True
