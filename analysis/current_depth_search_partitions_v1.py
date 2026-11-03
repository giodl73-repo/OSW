"""Declared search partitions retain canonical owners; they do not classify fronts."""
import math


def validate_partitions(op):
    partitions=op['search_partitions'];currents=op['currents'];sections=op['sections']
    if not partitions or not currents or not sections:raise ValueError('Nonempty declared partition plan required')
    for entity,c in currents.items():
        if c['entity_id']!=entity or c['core_search_depth_interval_m']!=c['selection_depth_interval_m'] or c['surface_component_gate_m_s'] is not None or c.get('temperature_gate') is not None:raise ValueError('Canonical owner and interval-only diagnostic contract required')
    if set(p['entity_id'] for p in partitions.values())!=set(currents):raise ValueError('Every canonical owner needs its declared partitions')
    seen=set();grouped={key:[] for key in partitions}
    for key,p in partitions.items():
        if p['id']!=key or p['kind']!='editorial_latitude_search_context':raise ValueError('Stable editorial partition identity required')
        if any(p.get(field) is not False for field in ['front_or_water_mass_classification_performed','persistent_jet_identity_validated','cross_partition_interpolation_permitted','canonical_current_ownership_changed']):raise ValueError('Partition identity cannot promote physical/front claims')
        gate=p['latitude_gate_degrees_north']
        if len(gate)!=2 or not all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in gate) or not -90<=gate[0]<gate[1]<=90:raise ValueError('Finite ordered latitude interval required')
    for s in sections:
        key=s['search_partition_id']
        if key not in partitions or s['id'] in seen:raise ValueError('Unknown partition or duplicate source section ID')
        seen.add(s['id']);p=partitions[key]
        if s['entity_id']!=p['entity_id'] or s['fixed_axis']!='longitude' or s['latitude_gate_degrees_north']!=p['latitude_gate_degrees_north']:raise ValueError('Section owner/axis/gate differs from declared partition')
        grouped[key].append(s)
    for key,items in grouped.items():
        longitudes=[s['longitude_degrees_east'] for s in items]
        if len(items)<2 or not all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in longitudes) or any(a>=b for a,b in zip(longitudes,longitudes[1:])):raise ValueError('At least two unique eastward-ordered longitude stops required per partition')
    for entity in currents:
        keys=[key for key,p in partitions.items() if p['entity_id']==entity]
        for i,key in enumerate(keys):
            a=partitions[key]['latitude_gate_degrees_north']
            for other in keys[i+1:]:
                b=partitions[other]['latitude_gate_degrees_north']
                if max(a[0],b[0])<min(a[1],b[1]):raise ValueError('Partition interiors cannot overlap;one shared boundary is allowed')
                if [s['longitude_degrees_east'] for s in grouped[key]]!=[s['longitude_degrees_east'] for s in grouped[other]]:raise ValueError('Paired latitude contexts require the same declared longitude stops')
    return grouped


def validate_section_partition(section,op):
    key=section['search_partition_id'];p=op['search_partitions'].get(key)
    if p is None or section['entity_id']!=p['entity_id'] or section['section_definition']['search_partition_id']!=key:raise ValueError('Retained partition/owner identity changed')
    matches=[s for s in op['sections'] if s['id']==section['section_definition']['id']]
    if len(matches)!=1 or section['section_definition']!=matches[0]:raise ValueError('Retained source section is not the exact declared partition section')
    if section['search_partition_kind']!=p['kind'] or section['front_or_water_mass_classification_performed'] is not False:raise ValueError('Retained partition semantics changed')
    return key
