"""Gateway-tested ADT contour search; failed candidates never become lengths."""
import hashlib
import json
import math
from pathlib import Path
import contourpy
import numpy as np
from shapely.geometry import LineString, box
from build_gulf_stream_geostrophic_path import ROOT, GEOD, sample_velocity
from build_loop_current_dated_streamline import build as rebuild_noaa, OUTPUT as NOAA_OUTPUT

SOURCE=ROOT/'research/gcoos-duacs-loop-20260925.json'
SOURCE_SHA256='1c6b0b354c48cb69ebf7ca72b5a8f8fb8d71fa0fe7b233cae2b084dcc9be05ea'
PROTOCOL=ROOT/'plans/loop-current-adt-contour-protocol-v1.md'
OUTPUT=ROOT/'research/loop-current-adt-contours-20260925.json'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def field_arrays(source):
    if source['grid_shape']!=[120,160] or source['grid_origin_lon_lat']!=[-98.9375,17.0625] or source['grid_step_degrees']!=[.125,.125]:
        raise ValueError('Unexpected ADT regional grid')
    if source['field_units']!={'adt':'m','ugos':'m/s','vgos':'m/s'}:
        raise ValueError('Unexpected ADT/velocity units')
    fields={n:np.asarray(source['fields'][n],dtype=float) for n in ['adt','ugos','vgos']}
    if any(a.shape!=(120,160) for a in fields.values()):raise ValueError('Unexpected field shape')
    return fields

def orient_gate_path(points):
    if len(points)<2:return None
    p=[list(v) for v in points]
    if abs(p[-1][1]-21.875)<1e-7:p.reverse()
    if not (abs(p[0][1]-21.875)<1e-7 and -86.875<=p[0][0]<=-85.125
            and abs(p[-1][0]+81.5)<1e-7 and 23<=p[-1][1]<=25):return None
    if p[0]==p[-1]:return None
    return [[round(float(x),6),round(float(y),6)] for x,y in p]

def mean_path_speed(source,fields,coordinates):
    total=0.;weighted=0.
    for a,b in zip(coordinates,coordinates[1:]):
        bearing,_,metres=GEOD.inv(*a,*b)
        if metres<=0:continue
        pieces=math.ceil(metres/10000)
        for i in range(pieces):
            lon,lat,_=GEOD.fwd(*a,bearing,metres*(i+.5)/pieces)
            velocity=sample_velocity(source,fields,lon,lat)
            if velocity is None:return None
            weighted+=math.hypot(*velocity)*metres/pieces
        total+=metres
    return weighted/total if total>0 else None

def scan(source,fields):
    x=source['grid_origin_lon_lat'][0]+np.arange(160)*.125
    y=source['grid_origin_lon_lat'][1]+np.arange(120)*.125
    generator=contourpy.contour_generator(x=x,y=y,z=np.ma.masked_invalid(fields['adt']),
        name='serial',corner_mask=False,line_type='Separate')
    candidates=[];levels=[];gate_rejections=0
    for integer in range(5,151):
        level=integer/100;count=0
        for raw in generator.lines(level):
            if len(raw)<2:continue
            clipped=LineString(raw).intersection(box(-98,21.875,-81.5,31))
            parts=[clipped] if clipped.geom_type=='LineString' else list(clipped.geoms) if clipped.geom_type=='MultiLineString' else []
            for part in parts:
                if part.is_empty:continue
                coordinates=orient_gate_path(list(part.coords))
                if coordinates is None:gate_rejections+=1;continue
                count+=1
                first=sample_velocity(source,fields,*coordinates[0]);last=sample_velocity(source,fields,*coordinates[-1])
                status='eligible';speed=None
                if first is None or last is None:status='missing_endpoint_velocity'
                elif first[1]<=0 or last[0]<=0:status='wrong_gateway_flow_direction'
                else:
                    speed=mean_path_speed(source,fields,coordinates)
                    if speed is None:status='missing_velocity_along_path'
                    elif speed<.1:status='weak_mean_speed'
                length=sum(GEOD.inv(*a,*b)[2] for a,b in zip(coordinates,coordinates[1:]))/1000
                candidates.append({'id':f'adt-contour:{integer:03d}:{count}','adt_level_m':level,
                    'status':status,'mean_speed_m_s':round(speed,9) if speed is not None else None,
                    'gate_connected_length_km':round(length,1),
                    'admissible_diagnostic_length_km':round(length,1) if status=='eligible' else None,
                    'coordinates_lon_lat':coordinates})
        levels.append({'adt_level_m':level,'gateway_segment_count':count})
    eligible=[c for c in candidates if c['status']=='eligible']
    selected=max(eligible,key=lambda c:c['mean_speed_m_s']) if eligible else None
    edge=selected is not None and selected['adt_level_m'] in (.05,1.5)
    return {'scanned_levels':levels,'gateway_candidates':candidates,
        'gate_rejected_segment_count':gate_rejections,'eligible_count':len(eligible),
        'selected':selected if not edge else None,'search_edge_peak':edge}

def build(source_path=SOURCE, source_sha256=SOURCE_SHA256, observation_date="2026-09-25", noaa_path=NOAA_OUTPUT, noaa_rebuild=None):
    source_path=Path(source_path);noaa_path=Path(noaa_path)
    if digest(source_path)!=source_sha256:raise ValueError('Changed ADT snapshot')
    source=json.loads(source_path.read_text(encoding='utf-8'))
    if source['observation_date']!=observation_date:raise ValueError('Unexpected ADT date')
    if contourpy.__version__!='1.3.3':raise ValueError('Use pinned contourpy 1.3.3 for this contour receipt')
    fields=field_arrays(source);result=scan(source,fields)
    noaa=json.loads(noaa_path.read_text(encoding='utf-8'))
    if noaa!=(noaa_rebuild or rebuild_noaa)():raise ValueError('NOAA diagnostic is stale')
    if noaa['observation_date']!=source['observation_date']:raise ValueError('Comparison dates differ')
    selected=result['selected'];length=selected['admissible_diagnostic_length_km'] if selected else None
    old=noaa['nominal']['open_path_length_km']
    return {'schema':'osw.loop-current-adt-contours.v1','current_id':'loop','observation_date':source['observation_date'],
        'status':'finite_contour_search_diagnostic_requires_review','layer':'absolute surface geostrophic',
        'metric':'highest_length_weighted_mean_speed_eligible_ADT_contour_between_editorial_gates',
        'source_file':str(source_path.relative_to(ROOT)).replace('\\','/'),'source_sha256':digest(source_path),
        'source_url':source['source_url'],'dataset_page':source['dataset_page'],
        'source_product_id':source['source_metadata']['subset_productId'],
        'source_dataset_id':source['source_metadata']['subset_datasetId'],
        'protocol_file':str(PROTOCOL.relative_to(ROOT)).replace('\\','/'),'protocol_sha256':digest(PROTOCOL),
        'generator_sha256':digest(Path(__file__)),'contourpy_version':contourpy.__version__,
        'velocity_sampler_sha256':digest(ROOT/'analysis/build_gulf_stream_geostrophic_path.py'),
        'source_time_scope':source['time_scope'],**result,
        'approximate_diagnostic_path_km':int(math.floor(length/100+.5)*100) if length is not None else None,
        'comparison':{'noaa_diagnostic_file':str(noaa_path.relative_to(ROOT)).replace('\\','/'),
            'noaa_diagnostic_sha256':digest(noaa_path),'noaa_open_path_length_km':old,
            'duacs_selected_contour_length_km':length,'signed_difference_duacs_minus_noaa_km':round(length-old,1) if length is not None and old is not None else None,
            'scope':'Same labelled date, different products and methods, shared satellite inputs possible; not independent observational validation or an uncertainty interval.'},
        'whole_current_length_km':None,'width_km':None,'annual_length_range_km':None,
        'confidence_interval_km':None,'rank_eligible':False,
        'interpretation':'Finite OSW contour scan inspired by maximum-velocity front methods; original supplemental implementation and gates not reproduced. Scanned levels do not form a physical uncertainty or width range.'}

if __name__=='__main__':
    result=build();OUTPUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('ADT eligible',result['eligible_count'],'selected length',result['approximate_diagnostic_path_km'],'km; comparison',result['comparison']['signed_difference_duacs_minus_noaa_km'],'km')
