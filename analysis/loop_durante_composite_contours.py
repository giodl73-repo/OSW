"""All declared composite contour/gateway cases, including failed components."""
from scientific_readback import canonicalize
from collections import Counter
import itertools
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

import contourpy
import numpy as np
from pyproj import Geod
from shapely.geometry import LineString, box
from shapely.ops import unary_union

from acquire_loop_durante_2026 import ROOT, DIRECTORY, verify as verify_source, sha, write
from build_motion_state_join import PROVINCES, polygon_parts
from build_current_reference_path_candidate import display_coordinates

PROTOCOL='plans/loop-durante-2026-composite-contour-protocol-v1.md'
PROTOCOL_SHA='80da02ccd4560d3f455963f2790c3aa55f582cf66d1edb24daa2eb46aae6da4f'
GENERATOR='analysis/loop_durante_composite_contours.py'
OUTPUT='research/loop-durante-2026-composite-contour-paths.json'
GEOD=Geod(ellps='WGS84')
LEVELS=(.50,.55,.60)
OFFSETS=(-.125,0.,.125)


def line_parts(geometry):
    if geometry.is_empty:return [],0
    if geometry.geom_type=='LineString':return [geometry],0
    if geometry.geom_type=='Point':return [],1
    parts=[];touches=0
    if hasattr(geometry,'geoms'):
        for child in geometry.geoms:
            lines,count=line_parts(child);parts.extend(lines);touches+=count
    return parts,touches


def orient(points, south, east):
    p=[[float(x),float(y)] for x,y in points]
    def entry(v):return abs(v[1]-south)<1e-7 and -86.875<=v[0]<=-85.125
    def exit(v):return abs(v[0]-east)<1e-7 and 23<=v[1]<=25
    if len(p)<2 or p[0]==p[-1]:return None
    if exit(p[0]) and entry(p[-1]):p.reverse()
    if not (entry(p[0]) and exit(p[-1])):return None
    return [[round(x,6),round(y,6)] for x,y in p]


def sample(x, y, u, v, lon, lat):
    """Strict four-corner vector support; cell addresses are zero based."""
    i=int(np.searchsorted(y,lat,side='right'))-1
    j=int(np.searchsorted(x,lon,side='right'))-1
    if i<0 or j<0 or i+1>=len(y) or j+1>=len(x):return None
    wy=float((lat-y[i])/(y[i+1]-y[i]));wx=float((lon-x[j])/(x[j+1]-x[j]))
    corners=[(i,j),(i+1,j),(i,j+1),(i+1,j+1)]
    weights=[(1-wy)*(1-wx),wy*(1-wx),(1-wy)*wx,wy*wx]
    values=np.asarray([[u[a,b],v[a,b]] for a,b in corners])
    if not np.isfinite(values).all():return None
    uv=np.asarray(weights)@values
    return {'cell_row_column':[i,j],'corner_rows_columns':[[a,b] for a,b in corners],
            'bilinear_weights':weights,'corner_eastward_northward_m_s':values.tolist(),
            'eastward_m_s':float(uv[0]),'northward_m_s':float(uv[1])}


def assess(coordinates, x, y, u, v, land):
    first=sample(x,y,u,v,*coordinates[0]);last=sample(x,y,u,v,*coordinates[-1])
    reasons=[]
    if first is None or last is None:reasons.append('missing_endpoint_velocity')
    elif first['northward_m_s']<=0 or last['eastward_m_s']<=0:reasons.append('wrong_gateway_flow_direction')
    total=weighted=along_weighted=0.;samples=[]
    for index,(a,b) in enumerate(zip(coordinates,coordinates[1:])):
        bearing,_,metres=GEOD.inv(*a,*b)
        if metres<=0:continue
        n=max(1,math.ceil(metres/10000));total+=metres
        for k in range(n):
            lon,lat,back=GEOD.fwd(*a,bearing,metres*(k+.5)/n)
            tangent=(back+180)%360
            velocity=sample(x,y,u,v,lon,lat)
            record={'leg_index':index,'piece_index':k,'piece_count':n,'piece_length_m':metres/n,
                    'longitude_latitude':[lon,lat],'tangent_azimuth_degrees':tangent,'velocity':velocity,
                    'vector_speed_m_s':None,'along_path_m_s':None}
            if velocity is not None:
                east,north=velocity['eastward_m_s'],velocity['northward_m_s']
                speed=math.hypot(east,north)
                along=east*math.sin(math.radians(tangent))+north*math.cos(math.radians(tangent))
                weighted+=speed*metres/n;along_weighted+=along*metres/n
                record.update(vector_speed_m_s=speed,along_path_m_s=along)
            samples.append(record)
    complete=bool(samples) and all(s['velocity'] is not None for s in samples)
    mean=weighted/total if complete else None
    along=along_weighted/total if complete else None
    if not complete:reasons.append('missing_velocity_along_path')
    if any(s['along_path_m_s'] is not None and s['along_path_m_s']<=0 for s in samples):reasons.append('opposing_along_path_velocity')
    if mean is not None and mean<.10:reasons.append('weak_mean_vector_speed')
    projected=LineString(display_coordinates(coordinates))
    land_overlap=float(projected.intersection(land).length)
    if land_overlap>1e-8:reasons.append('coarse_atlas_land_crossing')
    return {'supported':not reasons,'rejection_reasons':reasons,
            'geometric_path_length_km':round(total/1000,1),
            'rounded_geometric_path_km':int(math.floor(total/100000+.5)*100),
            'mean_vector_speed_m_s':mean,'mean_along_path_m_s':along,
            'minimum_along_path_m_s':min((s['along_path_m_s'] for s in samples if s['along_path_m_s'] is not None),default=None),
            'all_midpoints_supported':complete,'endpoints':{'entry':first,'exit':last},
            'midpoint_samples':samples,'coarse_land_overlap_projected_units':land_overlap,
            'coarse_clearance_is_bathymetric_or_high_resolution_clearance':False}


def case(lines, phase, level, south_offset, east_offset, x,y,u,v,land):
    south=21.875+south_offset;east=-81.5+east_offset
    components=[];touches=0
    for contour_index,raw in enumerate(lines):
        source_closed=bool(np.array_equal(raw[0],raw[-1]))
        clipped=LineString(raw).intersection(box(-98,south,east,31))
        parts,count=line_parts(clipped);touches+=count
        for part_index,part in enumerate(parts):
            points=list(part.coords);coordinates=orient(points,south,east)
            component={'source_contour_index':contour_index,'clipped_part_index':part_index,
                       'source_contour_closed':source_closed,'gate_connected':coordinates is not None,
                       'coordinates_lon_lat':coordinates or [[round(float(a),6),round(float(b),6)] for a,b in points]}
            if coordinates is None:
                component.update(supported=False,rejection_reasons=['closed_clipped_ring' if part.is_ring else 'does_not_connect_both_gateways'])
            else:component.update(assess(coordinates,x,y,u,v,land))
            components.append(component)
    eligible=[i for i,p in enumerate(components) if p['supported']]
    status='unique_supported_path' if len(eligible)==1 else 'ambiguous_supported_paths' if len(eligible)>1 else 'no_supported_path'
    selected=components[eligible[0]] if len(eligible)==1 else None
    return {'id':f'{phase.lower()}-adt-{level:.2f}-south-{south:.3f}-east-{east:.3f}',
            'phase':phase,'adt_level_m':level,'south_offset_degrees':south_offset,'east_offset_degrees':east_offset,
            'nominal':level==.55 and south_offset==east_offset==0,
            'gates':{'entry_latitude':south,'entry_longitude_bounds':[-86.875,-85.125],
                     'exit_longitude':east,'exit_latitude_bounds':[23,25]},
            'source_contour_count':len(lines),'point_touch_count':touches,'clipped_component_count':len(components),
            'gate_connected_component_count':sum(c['gate_connected'] for c in components),
            'supported_component_indices':eligible,'status':status,'components':components,
            'supported_contour_path_length_km':selected['geometric_path_length_km'] if selected else None,
            'rounded_supported_contour_path_km':selected['rounded_geometric_path_km'] if selected else None}


def build():
    if sha(ROOT/PROTOCOL)!=PROTOCOL_SHA:raise ValueError('Changed declared contour protocol')
    if contourpy.__version__!='1.3.3':raise ValueError('Use pinned contourpy1.3.3')
    receipt,_,arrays=verify_source()
    xgrid,ygrid=arrays['xduf'],arrays['yduf'];x,y=xgrid[0,:],ygrid[:,0]
    if not (np.array_equal(xgrid,np.broadcast_to(x,xgrid.shape)) and np.array_equal(ygrid,np.broadcast_to(y[:,None],ygrid.shape))
            and np.all(np.diff(x)==.125) and np.all(np.diff(y)==.125)):
        raise ValueError('Changed native rectilinear grid')
    atlas=ET.parse(PROVINCES).getroot();land=unary_union(polygon_parts(next(r.get('d') for r in atlas.iter() if r.get('class')=='land-context')))
    cases=[];contours=[]
    for phase,suffix in [('Positive','max'),('Negative','min')]:
        generator=contourpy.contour_generator(x=x,y=y,z=np.ma.masked_invalid(arrays['ADT'+suffix]),name='serial',corner_mask=False,line_type='Separate')
        for level in LEVELS:
            lines=generator.lines(level)
            contours.append({'phase':phase,'adt_level_m':level,'coordinates_lon_lat':[line.tolist() for line in lines]})
            for south,east in itertools.product(OFFSETS,OFFSETS):
                cases.append(case(lines,phase,level,south,east,x,y,arrays['U'+suffix],arrays['V'+suffix],land))
    pins={PROTOCOL:PROTOCOL_SHA,GENERATOR:sha(ROOT/GENERATOR),
          'analysis/acquire_loop_durante_2026.py':sha(ROOT/'analysis/acquire_loop_durante_2026.py'),
          'analysis/build_current_reference_path_candidate.py':sha(ROOT/'analysis/build_current_reference_path_candidate.py'),
          'analysis/build_cartographic_current_state_join.py':sha(ROOT/'analysis/build_cartographic_current_state_join.py'),
          'analysis/build_motion_state_join.py':sha(ROOT/'analysis/build_motion_state_join.py'),
          PROVINCES.relative_to(ROOT).as_posix():sha(PROVINCES),
          'plans/ocean-current-measurement-protocol-v1.md':sha(ROOT/'plans/ocean-current-measurement-protocol-v1.md')}
    for name,entry in receipt['files'].items():pins[(DIRECTORY/name).relative_to(ROOT).as_posix()]=entry['sha256']
    pins[(DIRECTORY/'acquisition.json').relative_to(ROOT).as_posix()]=sha(DIRECTORY/'acquisition.json')
    summaries=[]
    for phase in ['Positive','Negative']:
        group=[c for c in cases if c['phase']==phase];values=[c['supported_contour_path_length_km'] for c in group if c['supported_contour_path_length_km'] is not None]
        summaries.append({'phase':phase,'case_count':len(group),'status_counts':dict(Counter(c['status'] for c in group)),
                          'resolved_case_geometric_min_max_km':[min(values),max(values)] if values else None,
                          'envelope_is_annual_range_or_confidence_interval':False,
                          'nominal_case_id':next(c['id'] for c in group if c['nominal'])})
    return canonicalize({'schema':'osw.loop-durante-composite-contour-paths.v1','current_id':'loop',
            'source_doi':'10.5281/zenodo.22652650','source_version':'0',
            'source_kind':'author_processed_surface_phase_composites',
            'metric':'open_absolute_ADT_contour_arc_between_editorial_regional_gateways',
            'source_layer':'surface_geostrophic','observation_date':None,'source_composites_are_seasons':False,
            'protocol_file':PROTOCOL,'input_sha256':dict(sorted(pins.items())),
            'contourpy_version':contourpy.__version__,'coordinate_reference_system':'OGC:CRS84',
            'cell_index_basis':'zero_based_native_row_column','rounding_increment_km':100,
            'all_declared_cases':54,'cases':cases,'source_contours':contours,'phase_summaries':summaries,
            'whole_current_length_km':None,'width_km':None,'annual_length_range_km':None,
            'reference_route_admitted':False,'rank_eligible':False,'current_footprints_admitted':False,
            'interpretation':'Contour geometry of conditional fields, not mean daily path length or a physical current width. Failed/ambiguous cases remain unresolved; editorial level/gateway sensitivity is not uncertainty.'})


if __name__=='__main__':
    result=build();(ROOT/OUTPUT).write_bytes((json.dumps(result,separators=(',',':'),allow_nan=False)+'\n').encode('utf8'))
    print(json.dumps(result['phase_summaries'],indent=2))
