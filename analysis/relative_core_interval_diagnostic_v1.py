"""Interval selection with an explicit finite surface/core velocity comparison."""
import math
from interval_depth_diagnostic_v1 import selection as interval_selection,INTERIOR
from derive_eac_connected_layer_thickness_v1 import connected_layer


def selection(z,columns,op):
    if op.get('require_core_stronger_than_surface') is not True or not z or z[0]!=0:
        raise ValueError('Declared core>surface comparison and native0m reference required')
    base=interval_selection(z,columns,op)
    indices=[i for i,value in enumerate(z) if op['selection_depth_interval_m'][0]<=value<=op['selection_depth_interval_m'][1]]
    candidates=[]
    for profile,original in zip(columns,base['candidate_scores']):
        surface=profile[0]
        available=type(surface) in (int,float) and math.isfinite(surface)
        peak=max(profile[i] for i in indices) if original['complete_selection_interval_support'] else None
        contrast=peak-surface if available and peak is not None else None
        stronger=contrast is not None and contrast>0
        candidates.append(dict(original,interval_eligible_before_surface_comparison=original['eligible'],
            surface_reference_available=available,surface_component_m_s=surface if available else None,
            subsurface_interval_peak_m_s=peak,core_minus_surface_m_s=contrast,
            core_stronger_than_surface=stronger,eligible=bool(original['eligible'] and stronger)))
    ready=[i for i,c in enumerate(candidates) if c['eligible']]
    selected=max(ready,key=lambda i:candidates[i]['signed_selection_interval_integral_m2_s']) if ready else None
    if selected is None:status='no_qualifying_interval_core_stronger_than_surface_column'
    elif selected in [0,len(columns)-1]:status='section_gate_edge_maximum_axis_unresolved'
    elif not all(candidates[i]['complete_selection_interval_support'] and candidates[i]['surface_reference_available'] for i in [selected-1,selected+1]):
        status='selection_interval_or_surface_reference_support_edge_maximum_axis_unresolved'
    else:status=INTERIOR
    local=[]
    for i in ready:
        score=candidates[i]['signed_selection_interval_integral_m2_s']
        neighbors=[candidates[j]['signed_selection_interval_integral_m2_s'] for j in [i-1,i+1] if 0<=j<len(candidates) and candidates[j]['eligible']]
        if all(value is None or score>=value for value in neighbors):local.append(i)
    return {'selected_column_index':selected,'horizontal_selection_status':status,'candidate_scores':candidates,
        'local_integral_maximum_indices':local,'multiple_peaks_are_independent_currents':False,
        'selection_depth_interval_m':list(op['selection_depth_interval_m']),
        'local_maximum_scope':'Eligible core>surface candidates compared with eligible native neighbors;all candidate scores retained.',
        'surface_velocity_qualification_applied':True,'positive_surface_speed_gate_applied':False,
        'subsurface_core_surface_comparison_applied':True,
        'surface_comparison_definition':'Complete interval primary core must exceed the finite native0m signed component;no positive surface-speed prerequisite.',
        'minimum_core_minus_surface_m_s':0,'contrast_is_uncertainty_or_physical_accuracy':False}


def diagnose(z,columns,op):
    result=selection(z,columns,op);selected=result['selected_column_index']
    result['selected_column_threshold_layers']=[connected_layer(z,columns[selected],threshold,op['core_search_depth_interval_m']) for threshold in op['thresholds_m_s']] if selected is not None else []
    return result
