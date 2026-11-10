"""Calculate the next declared geographic extents using the same WGS84 metric."""
import hashlib
import itertools
import json
import math
from pathlib import Path
from estimate_current_reference_extents_v1 import length

ROOT=Path(__file__).resolve().parents[1]
INPUT='research/current-length-reference-extents-input-v4.json'
OUTPUT='research/current-length-reference-extents-v4.json'


def build():
    raw=(ROOT/INPUT).read_bytes();document=json.loads(raw);rounding=document['rounding_km'];rows=[]
    for item in document['currents']:
        axis={'longitude':0,'latitude':1}[item['uniform_offset_axis']];scenarios=[];rounding=item.get('rounding_km',document['rounding_km'])
        for start,end,uniform,interior in itertools.product(item['start_gate_options_lon_lat'],item['end_gate_options_lon_lat'],item.get('uniform_offsets_degrees',document['sensitivity']['uniform_offsets_degrees']),item.get('interior_offsets_degrees',document['sensitivity']['interior_offsets_degrees'])):
            points=[list(p) for p in item['coordinates_lon_lat']];points[0]=list(start);points[-1]=list(end)
            fixed=item.get('fixed_drawing_vertex_indices',[])
            if any(i<=0 or i>=len(points)-1 for i in fixed):raise ValueError('Only declared interior controls may be fixed')
            for i,point in enumerate(points):
                if i not in fixed:point[axis]+=uniform+(interior if 0<i<len(points)-1 else 0)
            scenarios.append({'start_gate_lon_lat':start,'end_gate_lon_lat':end,'uniform_offset':uniform,'interior_offset':interior,
                'coordinates_lon_lat':points,'length_km':round(length(points),6)})
        if len(scenarios)!=document['sensitivity']['cases_per_current']:raise ValueError('Incomplete declared grid')
        nominal=length(item['coordinates_lon_lat']);bounds=[min(r['length_km'] for r in scenarios),max(r['length_km'] for r in scenarios)]
        rows.append({**item,'length_estimate_km':rounding*math.floor(nominal/rounding+0.5),'computed_reference_length_km':round(nominal,6),
            'scenario_range_km':[rounding*math.floor(bounds[0]/rounding),rounding*math.ceil(bounds[1]/rounding)],'scenarios':scenarios,
            'method':document['method'],'source_time_convention':item['source_time_convention'],
            'status':'provisional_geographic_reference_estimate','physical_axis_admitted':False,
            'annual_length_range_km':None,'uncertainty_km':None,'rank_eligible_published_estimates':False})
    return {'schema':'osw.current-length-reference-extents.v4','input_file':INPUT,'input_sha256':hashlib.sha256(raw).hexdigest(),
        'generator_file':'analysis/estimate_current_reference_extents_v4.py','generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'metric_dependency_sha256':hashlib.sha256((ROOT/'analysis/estimate_current_reference_extents_v1.py').read_bytes()).hexdigest(),
        'source':document['source'],'sensitivity_interpretation':document['sensitivity']['interpretation'],'dateline_policy':document['dateline_policy'],
        'records':rows,'independent_observations_added':0}


if __name__=='__main__':
    value=build();(ROOT/OUTPUT).write_bytes((json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode())
    print(json.dumps([{'current':r['entity_id'],'estimate_km':r['length_estimate_km'],'sensitivity_km':r['scenario_range_km']} for r in value['records']]))
