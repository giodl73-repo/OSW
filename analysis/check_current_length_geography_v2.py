"""Coarse geometry screening with periodic land copies for dateline routes."""
import hashlib
import json
import math
import re
from pathlib import Path
import xml.etree.ElementTree as ET
from pyproj import Geod
from shapely.affinity import translate
from shapely.geometry import LineString,Polygon
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[1]
SOURCE='figures/ocean-motion-dashboard-ground.svg'
ESTIMATES='research/current-length-reference-extents-v2.json'
OUTPUT='research/current-length-reference-extents-geography-v2.json'
GEOD=Geod(ellps='WGS84')


def land():
    root=ET.parse(ROOT/SOURCE).getroot();path=next(n for n in root.iter() if n.tag.endswith('path') and n.get('fill')=='#33515b').get('d')
    if set(re.findall('[A-Za-z]',path))!={'M','L','Z'}:raise ValueError('Changed coarse coast encoding')
    shapes=[]
    for ring in path.split('M')[1:]:
        values=[float(n) for n in re.findall(r'-?\d+(?:\.\d+)?',ring)];polygon=Polygon(list(zip(values[::2],values[1::2])))
        shapes.append(polygon if polygon.is_valid else polygon.buffer(0))
    original=unary_union(shapes)
    return original,unary_union([translate(original,xoff=offset) for offset in [-1480,0,1480]])


def unwrap(points,anchor=None):
    result=[]
    for lon,lat in points:
        previous=result[-1][0] if result else anchor if anchor is not None else lon
        lon+=360*round((previous-lon)/360);result.append([lon,lat])
    return result


def world(point):return 60+(point[0]+180)/360*1480,90+(90-point[1])/180*740


def dense(points):
    result=[points[0]]
    for start,end in zip(points,points[1:]):
        count=max(1,math.ceil(GEOD.inv(*start,*end)[2]/10000))
        if count>1:result.extend(GEOD.npts(*start,*end,count-1))
        result.append(end)
    return unwrap(result)


def build():
    raw=(ROOT/ESTIMATES).read_bytes();document=json.loads(raw);_,periodic=land();records=[]
    for row in document['records']:
        tests=[]
        for number,scenario in enumerate(row['scenarios']):
            line=LineString([world(p) for p in dense(scenario['coordinates_lon_lat'])])
            tests.append({'scenario_index':number,'coarse_land_clear':not line.intersects(periodic)})
        records.append({'entity_id':row['entity_id'],'scenarios':len(tests),'coarse_land_clear':sum(x['coarse_land_clear'] for x in tests),
            'all_clear':all(x['coarse_land_clear'] for x in tests),'checks':tests})
    return {'schema':'osw.current-length-coarse-geography.v2','source_file':SOURCE,'source_sha256':hashlib.sha256((ROOT/SOURCE).read_bytes()).hexdigest(),
        'estimate_file_sha256':hashlib.sha256(raw).hexdigest(),'method':'WGS84 legs densified at most10km, continuously unwrapped, checked against three periodic copies of the retained coarse display land. Invalid display polygons repaired with buffer(0).',
        'records':records,'fine_coast_checked':False,'physical_axis_verified':False}


if __name__=='__main__':
    result=build();(ROOT/OUTPUT).write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print(json.dumps([{k:r[k] for k in ['entity_id','scenarios','coarse_land_clear','all_clear']} for r in result['records']]))
    if not all(r['all_clear'] for r in result['records']):raise SystemExit('Retained failed scenarios; no estimate admission')
