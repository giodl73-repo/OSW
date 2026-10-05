"""Reproduce a gateway-tested dated streamline and retain all failed scenarios."""
import hashlib
import json
import math
from pathlib import Path
from build_gulf_stream_geostrophic_path import load_field, sample_velocity, GEOD, ROOT
from fetch_noaa_lsa_geostrophic_snapshot import EXPECTED_SHA256

SOURCE=ROOT/'research/noaa-lsa-geostrophic-loop-20260925.json'
PROTOCOL=ROOT/'plans/loop-current-dated-streamline-protocol-v1.md'
OUTPUT=ROOT/'research/loop-current-dated-streamline-20260925.json'
SOURCE_SUBSET_SHA256='c2599680d88ff8182eb3ff10e97c16cefed056061f62b78f84b67abb3c5b6af9'

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def trace(source,fields,seed_lon,step_km=10,min_speed=.1):
    if not math.isfinite(seed_lon) or not -86.875<=seed_lon<=-85.125 or step_km not in (5,10,20) or min_speed not in (.05,.1,.15):
        raise ValueError('Undeclared experiment parameter')
    lon,lat=seed_lon,21.875
    coordinates=[[lon,lat]]; reason='distance_cap'; speeds=[]
    for _ in range(math.ceil(4000/step_km)):
        velocity=sample_velocity(source,fields,lon,lat)
        if velocity is None: reason='missing_grid_velocity';break
        speed=math.hypot(*velocity)
        if speed<min_speed: reason='speed_below_threshold';break
        x,y,_=GEOD.fwd(lon,lat,math.degrees(math.atan2(*velocity)),step_km*500)
        mid=sample_velocity(source,fields,x,y)
        if mid is None: reason='missing_midpoint_velocity';break
        if math.hypot(*mid)<min_speed: reason='midpoint_speed_below_threshold';break
        x,y,_=GEOD.fwd(lon,lat,math.degrees(math.atan2(*mid)),step_km*1000)
        if lon < -81.5 <= x:
            fraction=(-81.5-lon)/(x-lon)
            gate_lat=lat+(y-lat)*fraction
            if 23<=gate_lat<=25:
                x,y=-81.5,gate_lat; reason='florida_gate'
            else:
                reason='eastward_crossing_outside_florida_gate'
        elif y<21.875:
            reason='returned_south_of_yucatan_gate'
        elif not (-98<=x<=-79 and 19<=y<=31):
            reason='left_regional_domain'
        coordinates.append([round(x,6),round(y,6)]); speeds.append(speed)
        lon,lat=x,y
        if reason!='distance_cap':break
    # Scientific length uses exactly the coordinates retained in the receipt.
    stored_length=sum(GEOD.inv(*a,*b)[2] for a,b in zip(coordinates,coordinates[1:]))/1000
    reached=reason=='florida_gate'
    return {'seed_lon_lat':[seed_lon,21.875], 'step_km':step_km,'minimum_speed_threshold_m_s':min_speed,
        'stop_reason':reason,'gate_connected':reached, 'travelled_distance_km':round(stored_length,1),
        'open_path_length_km':round(stored_length,1) if reached else None,
        'minimum_sampled_speed_m_s':round(min(speeds),4) if speeds else None,
        'maximum_latitude':round(max(p[1] for p in coordinates),6),
        'coordinates_lon_lat':coordinates}

def build():
    if digest(SOURCE)!=SOURCE_SUBSET_SHA256:
        raise ValueError('Changed pinned regional receipt')
    source=json.loads(SOURCE.read_text(encoding='utf-8'))
    if source['source_response_sha256']!=EXPECTED_SHA256 or source['source_time_start']!='2026-09-25T00:00:00Z':
        raise ValueError('Unexpected source identity/date')
    if source['subset_shape']!=[48,76] or source['grid_origin_lon_lat']!=[-97.875,19.125]:
        raise ValueError('Unexpected regional grid')
    fields=load_field(source)
    candidates=[]
    for index in range(8):
        lon=-86.875+index*.25; v=sample_velocity(source,fields,lon,21.875)
        candidates.append({'longitude':lon,'northward_m_s':v[1] if v else None})
    eligible=[c for c in candidates if c['northward_m_s'] is not None and c['northward_m_s']>0]
    if not eligible:raise ValueError('No supported northward inflow')
    seed=max(eligible,key=lambda c:c['northward_m_s'])['longitude']
    nominal=trace(source,fields,seed)
    scenarios=[]
    for delta in [-.25,-.125,.125,.25]:
        if -86.875<=seed+delta<=-85.125:
            scenarios.append({'variation':'seed_longitude','offset_degrees':delta,**trace(source,fields,seed+delta)})
    for step in [5,20]:scenarios.append({'variation':'step_size',**trace(source,fields,seed,step)})
    for speed in [.05,.15]:scenarios.append({'variation':'speed_threshold',**trace(source,fields,seed,10,speed)})
    return {'schema':'osw.loop-current-dated-streamline.v1','current_id':'loop','observation_date':'2026-09-25',
        'status':'diagnostic_experiment_requires_source_endpoint_and_scientific_review',
        'source_subset':str(SOURCE.relative_to(ROOT)).replace('\\','/'),'source_subset_sha256':digest(SOURCE),
        'source_url':source['source_url'],'source_algorithm':source['source_algorithm'],
        'protocol_file':str(PROTOCOL.relative_to(ROOT)).replace('\\','/'),'protocol_sha256':digest(PROTOCOL),
        'generator_sha256':digest(Path(__file__)),'velocity_sampler_sha256':digest(ROOT/'analysis/build_gulf_stream_geostrophic_path.py'),
        'general_measurement_protocol_sha256':digest(ROOT/'plans/ocean-current-measurement-protocol-v1.md'),
        'layer':'altimetry-derived absolute surface geostrophic velocity',
        'metric':'open_frozen_time_velocity_streamline_between_editorial_regional_gates',
        'nominal_seed_candidates':candidates,'nominal':nominal,'sensitivity_scenarios':scenarios,
        'approximate_diagnostic_path_km':int(math.floor(nominal['open_path_length_km']/100+.5)*100) if nominal['gate_connected'] else None,
        'whole_current_length_km':None,'rank_eligible':False,'width_km':None,'annual_length_range_km':None,
        'confidence_interval_km':None,'sensitivity_range_km':None,
        'failure_count':sum(not s['gate_connected'] for s in scenarios),
        'interpretation':'No range admitted from successful scenarios while other declared scenarios fail. Not the published maximum-velocity contour method, a closed ring, whole-current axis, or particle trajectory.'}

if __name__=='__main__':
    result=build();OUTPUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Loop nominal',result['nominal']['stop_reason'],result['approximate_diagnostic_path_km'],'km; failed sensitivities',result['failure_count'])
