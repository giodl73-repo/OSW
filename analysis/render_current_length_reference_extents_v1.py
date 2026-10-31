"""Render the declared Atlantic length estimates in their geographic context."""
import json
import hashlib
import math
import re
from pathlib import Path
import xml.etree.ElementTree as ET
from pyproj import Geod
from shapely.geometry import Polygon,LineString,box
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[1]
NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)


def render():
    document=json.loads((ROOT/'research/current-length-reference-extents-v1.json').read_bytes())
    root=ET.Element('{'+NS+'}svg',{'viewBox':'0 0 1000 760','role':'img','aria-labelledby':'title desc'})
    def add(tag,attributes=None,text=None,parent=root):
        element=ET.SubElement(parent,'{'+NS+'}'+tag,attributes or {});element.text=text;return element
    add('title',{'id':'title'},'Atlantic NEC and SEC geographic length estimates')
    add('desc',{'id':'desc'},'Declared reference routes and all72 endpoint/drawing sensitivity paths; not observed current axes.')
    add('rect',{'width':'1000','height':'760','fill':'#f3f7f8'})
    def label(x,y,size,text):add('text',{'x':str(x),'y':str(y),'font-size':str(size),'font-family':'Arial','fill':'#163b49'},text)
    label(35,40,26,'Atlantic current length estimates')
    label(35,75,18,'Declared geographic extents · WGS84 leg sums · approximate, not observed axes')
    add('rect',{'x':'35','y':'105','width':'930','height':'465','fill':'#e7f1f4'})
    region=root
    base_path=ROOT/'figures/ocean-motion-dashboard-ground.svg';base=ET.parse(base_path).getroot()
    coast=next(n for n in base.iter() if n.tag.endswith('path') and n.get('fill')=='#33515b').get('d')
    if set(re.findall('[A-Za-z]',coast))!={'M','L','Z'}:raise ValueError('Unexpected coarse coast encoding')
    polygons=[]
    for ring in coast.split('M')[1:]:
        values=[float(n) for n in re.findall(r'-?\d+(?:\.\d+)?',ring)]
        polygon=Polygon(list(zip(values[::2],values[1::2])))
        polygons.append(polygon if polygon.is_valid else polygon.buffer(0))
    land=unary_union(polygons);clipped=land.intersection(box(512.222222,357.222222,882.222222,542.222222))
    def local(x,y):return 35+(x-512.222222)*930/370,105+(y-357.222222)*465/185
    def ring_path(points):return ' '.join(('M' if i==0 else 'L')+f'{x:.3f},{y:.3f}' for i,(x,y) in enumerate(local(*p) for p in points))+' Z'
    for polygon in getattr(clipped,'geoms',[clipped]):
        d=ring_path(polygon.exterior.coords)+' '+' '.join(ring_path(r.coords) for r in polygon.interiors)
        add('path',{'d':d,'fill':'#c7d8dc','stroke':'#77969f','stroke-width':'.7','fill-rule':'evenodd'})
    def world(point):return 60+(point[0]+180)/360*1480,90+(90-point[1])/180*740
    def project(point):return local(*world(point))
    def path(points):return ' '.join(('M' if i==0 else 'L')+f'{x:.5f},{y:.5f}' for i,(x,y) in enumerate(map(project,points)))
    geod=Geod(ellps='WGS84');checks=[]
    for row in document['records']:
        results=[]
        for scenario in row['scenarios']:
            points=[scenario['coordinates_lon_lat'][0]]
            for a,b in zip(scenario['coordinates_lon_lat'],scenario['coordinates_lon_lat'][1:]):
                steps=max(1,math.ceil(geod.inv(*a,*b)[2]/10000))
                if steps>1:points.extend(geod.npts(*a,*b,steps-1))
                points.append(b)
            results.append(not LineString([world(p) for p in points]).intersects(land))
        checks.append({'entity_id':row['entity_id'],'scenarios':len(results),'coarse_land_clear':sum(results),'all_clear':all(results)})
    if not all(r['all_clear'] for r in checks):raise ValueError('A declared route intersects the coarse OSW land mask')
    report={'schema':'osw.current-length-coarse-geography.v1','source_file':'figures/ocean-motion-dashboard-ground.svg','source_sha256':hashlib.sha256(base_path.read_bytes()).hexdigest(),
        'estimate_file_sha256':hashlib.sha256((ROOT/'research/current-length-reference-extents-v1.json').read_bytes()).hexdigest(),
        'method':'All declared geodesic legs densified at no more than10km, tested against the retained coarse display land polygons. Invalid display polygons repaired by buffer(0).',
        'records':checks,'fine_coast_checked':False,'physical_axis_verified':False}
    (ROOT/'research/current-length-reference-extents-geography-v1.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
    for row,color in zip(document['records'],['#49e1e5','#ffcc65']):
        for scenario in row['scenarios']:add('path',{'d':path(scenario['coordinates_lon_lat']),'stroke':'#087f8c' if color=='#49e1e5' else '#ac6812','stroke-width':'.6','stroke-opacity':'.3','fill':'none'},parent=region)
        add('path',{'d':path(row['coordinates_lon_lat']),'stroke':'#087f8c' if color=='#49e1e5' else '#ac6812','stroke-width':'3','fill':'none'},parent=region)
        for point in [row['coordinates_lon_lat'][0],row['coordinates_lon_lat'][-1]]:
            x,y=project(point);add('circle',{'cx':str(x),'cy':str(y),'r':'1.9','fill':color,'stroke':'#fff','stroke-width':'.4'},parent=region)
    for i,row in enumerate(document['records']):
        name='North Equatorial Current' if i==0 else 'South Equatorial Current';low,high=row['scenario_range_km']
        label(35,610+i*36,22,f'{name}: ≈ {row["length_estimate_km"]:,} km · route/gate sensitivity {low:,}–{high:,} km')
    label(35,698,17,'Source context: Philander (2001), Figure 1, July–September schematic. Coordinates are OSW choices.')
    label(35,728,17,'All72 cases clear the coarse OSW land mask. Fine coast unchecked. Sensitivity is not annual change.')
    return ET.tostring(root,encoding='utf8',xml_declaration=True)


if __name__=='__main__':(ROOT/'figures/atlantic-basin-current-length-estimates-v1.svg').write_bytes(render())
