"""Interval-scored column selection without a surface-velocity qualification."""
import math
from derive_eac_connected_layer_thickness_v1 import connected_layer

INTERIOR='interior_section_integral_maximum_with_finite_neighbors_not_independently_validated_axis'


def selection(z,columns,op):
    number=lambda x:type(x) in (int,float) and math.isfinite(x)
    if len(z)<2 or not all(number(x) and x>=0 for x in z) or any(b<=a for a,b in zip(z,z[1:])):
        raise ValueError('Finite increasing native depth axis required')
    interval=op['selection_depth_interval_m']
    if len(interval)!=2 or not all(number(x) for x in interval) or not 0<=interval[0]<interval[1]:
        raise ValueError('Finite increasing selection interval required')
    if op['core_search_depth_interval_m']!=interval or op['surface_component_gate_m_s'] is not None:
        raise ValueError('Declared equal core/selection interval and no surface gate required')
    threshold=op['primary_threshold_m_s']
    if not number(threshold) or threshold<=0 or not 3<=len(columns)<=150:raise ValueError('Positive primary cutoff and bounded section required')
    indices=[i for i,x in enumerate(z) if interval[0]<=x<=interval[1]]
    if len(indices)<2 or z[indices[0]]!=interval[0] or z[indices[-1]]!=interval[1]:
        raise ValueError('Both selection endpoints must be actual native levels')
    candidates=[]
    for column in columns:
        if len(column)!=len(z) or any(x is not None and not number(x) for x in column):
            raise ValueError('Native-size profile with explicit null missing values required')
        complete=all(column[i] is not None for i in indices)
        score=sum((column[a]+column[b])*(z[b]-z[a])/2 for a,b in zip(indices,indices[1:])) if complete else None
        eligible=complete and max(column[i] for i in indices)>threshold and score>0
        candidates.append({'complete_selection_interval_support':complete,'signed_selection_interval_integral_m2_s':score,'eligible':bool(eligible)})
    ready=[i for i,c in enumerate(candidates) if c['eligible']]
    selected=max(ready,key=lambda i:candidates[i]['signed_selection_interval_integral_m2_s']) if ready else None
    if selected is None:status='no_qualifying_interval_component_column'
    elif selected in [0,len(columns)-1]:status='section_gate_edge_maximum_axis_unresolved'
    elif not all(candidates[i]['complete_selection_interval_support'] for i in [selected-1,selected+1]):
        status='selection_interval_support_edge_maximum_axis_unresolved'
    else:status=INTERIOR
    local=[]
    for i in ready:
        score=candidates[i]['signed_selection_interval_integral_m2_s']
        neighbors=[candidates[j]['signed_selection_interval_integral_m2_s'] for j in [i-1,i+1] if 0<=j<len(candidates)]
        if all(v is None or score>=v for v in neighbors):local.append(i)
    return {'selected_column_index':selected,'horizontal_selection_status':status,'candidate_scores':candidates,
        'local_integral_maximum_indices':local,'multiple_peaks_are_independent_currents':False,
        'selection_depth_interval_m':list(interval),'surface_velocity_qualification_applied':False}


def diagnose(z,columns,op):
    result=selection(z,columns,op);selected=result['selected_column_index']
    result['selected_column_threshold_layers']=[connected_layer(z,columns[selected],threshold,op['core_search_depth_interval_m']) for threshold in op['thresholds_m_s']] if selected is not None else []
    return result
