"""Compute declared geographic length estimates, never scientific admissions."""
import hashlib
import itertools
import json
import math
from pathlib import Path
from pyproj import Geod

ROOT=Path(__file__).resolve().parents[1]
INPUT='research/current-length-reference-extents-input-v1.json'
OUTPUT='research/current-length-reference-extents-v1.json'
GEOD=Geod(ellps='WGS84')


def length(points):
    if len(points)<2:raise ValueError('Two or more vertices required')
    for lon,lat in points:
        if not math.isfinite(lon) or not math.isfinite(lat) or not -180<=lon<=180 or not -90<=lat<=90:raise ValueError('Invalid CRS84 vertex')
    return sum(GEOD.inv(a[0],a[1],b[0],b[1])[2] for a,b in zip(points,points[1:]))/1000


def build():
    raw=(ROOT/INPUT).read_bytes();document=json.loads(raw);step=document['rounding_km'];records=[]
    for item in document['currents']:
        scenarios=[]
        for east,west,uniform,bend in itertools.product(item['eastern_gate_longitudes'],item['western_gate_longitudes'],document['sensitivity']['uniform_latitude_offsets_degrees'],document['sensitivity']['interior_latitude_offsets_degrees']):
            points=[list(p) for p in item['coordinates_lon_lat']];points[0][0]=east;points[-1][0]=west
            for i,p in enumerate(points):p[1]+=uniform+(bend if 0<i<len(points)-1 else 0)
            scenarios.append({'eastern_gate_longitude':east,'western_gate_longitude':west,'uniform_latitude_offset':uniform,'interior_latitude_offset':bend,'coordinates_lon_lat':points,'length_km':round(length(points),6)})
        if len(scenarios)!=document['sensitivity']['cases_per_current']:raise ValueError('Incomplete declared sensitivity grid')
        nominal=length(item['coordinates_lon_lat']);bounds=[min(r['length_km'] for r in scenarios),max(r['length_km'] for r in scenarios)]
        records.append({**item,'length_estimate_km':step*math.floor(nominal/step+0.5),'computed_reference_length_km':round(nominal,6),
            'scenario_range_km':[step*math.floor(bounds[0]/step),step*math.ceil(bounds[1]/step)],'scenarios':scenarios,
            'source_url':document['source']['url'],'source_locator':document['source']['read_support'],
            'method':document['method'],'source_time_convention':document['source']['source_time_convention'],
            'status':'provisional_geographic_reference_estimate','geography_review_status':'See separately hash-bound current-length-reference-extents-geography-v1.json; no physical-axis verification implied.',
            'physical_axis_admitted':False,'annual_length_range_km':None,'uncertainty_km':None,'rank_eligible_published_estimates':False})
    return {'schema':'osw.current-length-reference-extents.v1','input_file':INPUT,'input_sha256':hashlib.sha256(raw).hexdigest(),
        'generator_file':'analysis/estimate_current_reference_extents_v1.py','generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'source':document['source'],'sensitivity_interpretation':document['sensitivity']['interpretation'],'records':records,'independent_observations_added':0}


if __name__=='__main__':
    value=build();(ROOT/OUTPUT).write_bytes((json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode())
    print(json.dumps([{'current':r['entity_id'],'estimate_km':r['length_estimate_km'],'sensitivity_km':r['scenario_range_km']} for r in value['records']]))
