"""Reuse frozen diagnostics for two non-additive vertical search contexts."""
import copy
from interval_depth_diagnostic_v1 import diagnose
from mixed_interval_section_geometry_v1 import validate_retained

SCHEMA='osw.multi-context-interval-depth-section.v1'


def context_config(config,key):
    contexts=config['diagnostic_contexts']
    if set(contexts)!={'shallow','deep'} or config['default_diagnostic_context_id']!='shallow':raise ValueError('Both declared contexts with shallow default required')
    if config['entity_id']!='current:atlantic-south-equatorial-countercurrent' or config['component_bearing_degrees_true']!=90:raise ValueError('Atlantic SECC eastward owner/frame required')
    expected={'shallow':[0,100],'deep':[150,350]}
    for name,definition in contexts.items():
        if definition['id']!=name or definition['selection_depth_interval_m']!=expected[name] or definition['core_search_depth_interval_m']!=expected[name] or definition['primary_threshold_m_s']!=.1:raise ValueError('Predeclared context window/cutoff changed')
    if config['surface_component_gate_m_s'] is not None or config.get('temperature_gate') is not None:raise ValueError('No surface or thermal gate allowed')
    return {**config,**contexts[key]}


def diagnose_contexts(z,columns,config):
    return {key:{'context_id':key,'selection_depth_interval_m':context_config(config,key)['selection_depth_interval_m'],
                 'core_search_depth_interval_m':context_config(config,key)['core_search_depth_interval_m'],
                 'primary_threshold_m_s':context_config(config,key)['primary_threshold_m_s'],
                 'diagnosis':diagnose(z,columns,context_config(config,key))} for key in ['shallow','deep']}


def validate_contexts(section,config):
    if (section['schema']!=SCHEMA or section['entity_id']!=config['entity_id']
        or section['default_diagnostic_context_id']!='shallow'
        or section['vertical_contexts_are_additive'] is not False
        or section['contexts_are_independent_observations'] is not False
        or set(section['context_diagnoses'])!={'shallow','deep'}):raise ValueError('Retained context identity/non-additive semantics changed')
    for key in ['shallow','deep']:
        cfg=context_config(config,key);entry=section['context_diagnoses'][key]
        if entry['context_id']!=key or any(entry[k]!=cfg[k] for k in ['selection_depth_interval_m','core_search_depth_interval_m','primary_threshold_m_s']):raise ValueError('Retained context configuration changed')
        # Only an in-memory diagnostic view changes; retained arrays/hash/owner stay exact.
        virtual=copy.copy(section);virtual['diagnosis']=entry['diagnosis']
        validate_retained(virtual,cfg)
    if section['diagnosis']!=section['context_diagnoses']['shallow']['diagnosis']:raise ValueError('Default diagnosis is not the declared shallow context')
    return True
