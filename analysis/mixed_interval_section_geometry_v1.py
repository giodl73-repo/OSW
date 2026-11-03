"""Dispatch frozen geometry and interval audits; reserve both axes before fields."""
import acquire_zonal_current_depth_sections_v1 as longitude_geometry
import latitude_depth_section_geometry_v1 as latitude_geometry
from interval_transverse_section_audit_v1 import validate_retained as longitude_audit
from latitude_interval_section_audit_v1 import validate_retained as latitude_audit


def preflight(lats,lons,op):
    ids=[(s['entity_id'],s['id']) for s in op['sections']]
    if len(ids)!=len(set(ids)) or any(s['fixed_axis'] not in ['longitude','latitude'] for s in op['sections']):raise ValueError('Unique supported mixed-axis sections required')
    plans={};pairs=0
    for axis,module in [('longitude',longitude_geometry),('latitude',latitude_geometry)]:
        sections=[s for s in op['sections'] if s['fixed_axis']==axis]
        if not sections:continue
        part,count=module.preflight(lats,lons,{**op,'sections':sections});pairs+=count
        for plan in part:plans[plan['definition']['entity_id'],plan['definition']['id']]=plan
    if pairs>op['maximum_total_cell_pairs'] or pairs*16>op['maximum_total_decoded_velocity_bytes']:raise ValueError('Joint mixed-axis target exceeds original caps')
    if len(plans)!=len(ids):raise ValueError('Every original mixed-axis section required')
    return [plans[key] for key in ids],pairs


def profile_count(plan):
    axis=plan['definition']['fixed_axis']
    if axis=='longitude':return len(plan['latitude_indices'])
    if axis=='latitude':return len(plan['longitude_indices'])
    raise ValueError('Unsupported section axis')


def read_arguments(plan):
    axis=plan['definition']['fixed_axis']
    if axis=='longitude':
        indices=plan['latitude_indices'];return int(indices[0]),int(indices[-1]),int(plan['longitude_index'])
    if axis=='latitude':
        indices=plan['longitude_indices'];return int(plan['latitude_index']),int(indices[0]),int(indices[-1])
    raise ValueError('Unsupported section axis')


def columns_from_arrays(u,v,lats,lons,plan,bearing):
    if plan['definition']['fixed_axis']=='longitude':
        ix=plan['longitude_index'];return longitude_geometry.columns_from_arrays(u,v,lats,float(lons[ix]),ix,plan['latitude_indices'],bearing)
    if plan['definition']['fixed_axis']=='latitude':
        iy=plan['latitude_index'];return latitude_geometry.columns_from_arrays(u,v,lons,float(lats[iy]),iy,plan['longitude_indices'],bearing)
    raise ValueError('Unsupported section axis')


def retained_geometry(plan,lats,lons,time_index,depth_count=40):
    axis=plan['definition']['fixed_axis'];a,b,c=read_arguments(plan)
    if axis=='longitude':
        return {'actual_source_longitude_degrees_east':float(lons[c]),'actual_source_latitude_degrees_north':None,
            'maximum_nearest_longitude_distance_km':plan['maximum_longitude_distance_km'],
            'profile_order':'native_increasing_latitude_first_southern_index_breaks_ties',
            'retrieved_hyperslab':{'time_index':time_index,'depth_indices_inclusive':[0,depth_count-1],'latitude_indices_inclusive':[a,b],'longitude_index':c}}
    if axis=='latitude':
        return {'actual_source_longitude_degrees_east':None,'actual_source_latitude_degrees_north':float(lats[a]),
            'nearest_latitude_distance_km':plan['nearest_latitude_distance_km'],
            'profile_order':'native_increasing_longitude_first_western_index_breaks_ties',
            'retrieved_hyperslab':{'time_index':time_index,'depth_indices_inclusive':[0,depth_count-1],'latitude_index':a,'longitude_indices_inclusive':[b,c]}}
    raise ValueError('Unsupported section axis')


def validate_retained(section,config):
    axis=section['section_definition']['fixed_axis']
    if section['source_section_geometry']!=axis:raise ValueError('Retained geometry tag changed')
    if axis=='longitude':return longitude_audit(section,config)
    if axis=='latitude':return latitude_audit(section,config)
    raise ValueError('Unsupported retained section axis')
