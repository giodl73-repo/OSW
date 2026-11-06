"""Reuse frozen diagnostics for two non-additive vertical search contexts."""
import copy
from interval_depth_diagnostic_v1 import diagnose
from mixed_interval_section_geometry_v1 import validate_retained

SCHEMA='osw.branch-multi-context-interval-depth-section.v1'


def branch_config(op,definition):
    if definition not in op['sections'] or definition['entity_id']!='current:mediterranean-undercurrent':raise ValueError('Original canonical branch section required')
    key=definition['diagnostic_branch_id']
    if set(op['branches'])!={'south-iberian','west-iberian'} or key not in op['branches']:raise ValueError('Both declared regional branches required')
    for name,bearing,axis in [('south-iberian',270,'longitude'),('west-iberian',0,'latitude')]:
        b=op['branches'][name]
        if b['id']!=name or b['component_bearing_degrees_true']!=bearing or b['section_geometry']!=axis:raise ValueError('Predeclared branch frame/geometry changed')
    b=op['branches'][key]
    if definition['fixed_axis']!=b['section_geometry']:raise ValueError('Branch section geometry mismatch')
    return {**op,**op['currents'][definition['entity_id']],**b,'diagnostic_branch_id':key}


def context_config(config,key):
    contexts=config['diagnostic_contexts']
    if set(contexts)!={'upper','lower'} or config['default_diagnostic_context_id']!='upper':raise ValueError('Both declared contexts with upper default required')
    if config['entity_id']!='current:mediterranean-undercurrent' or config['diagnostic_branch_id'] not in ['south-iberian','west-iberian'] or config['component_bearing_degrees_true']!={'south-iberian':270,'west-iberian':0}[config['diagnostic_branch_id']]:raise ValueError('Mediterranean owner/declared branch frame required')
    expected={'upper':[500,900],'lower':[900,1500]}
    for name,definition in contexts.items():
        if definition['id']!=name or definition['selection_depth_interval_m']!=expected[name] or definition['core_search_depth_interval_m']!=expected[name] or definition['primary_threshold_m_s']!=.05:raise ValueError('Predeclared context window/cutoff changed')
    if config['surface_component_gate_m_s'] is not None or config.get('temperature_gate') is not None:raise ValueError('No surface or thermal gate allowed')
    return {**config,**contexts[key]}


def diagnose_contexts(z,columns,config):
    return {key:{'context_id':key,'selection_depth_interval_m':context_config(config,key)['selection_depth_interval_m'],
                 'core_search_depth_interval_m':context_config(config,key)['core_search_depth_interval_m'],
                 'primary_threshold_m_s':context_config(config,key)['primary_threshold_m_s'],
                 'diagnosis':diagnose(z,columns,context_config(config,key))} for key in ['upper','lower']}


def validate_contexts(section,config):
    if (section['schema']!=SCHEMA or section['entity_id']!=config['entity_id']
        or section['diagnostic_branch_id']!=config['diagnostic_branch_id'] or section['section_definition']['diagnostic_branch_id']!=config['diagnostic_branch_id']
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
