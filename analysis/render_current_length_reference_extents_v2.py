"""Draw the six nominal basin reference extents with correct periodic geography."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from shapely.geometry import box
from check_current_length_geography_v2 import land,unwrap,world,dense

ROOT=Path(__file__).resolve().parents[1]
NS='http://www.w3.org/2000/svg';ET.register_namespace('',NS)
GROUPS={'pacific-equatorial':('Pacific equatorial current lengths',[100,285,-25,35]),
    'south-pacific':('South Pacific Current length',[150,285,-50,-25]),
    'indian':('Indian Ocean current lengths',[35,125,-45,5])}


def render_all():
    document=json.loads((ROOT/'research/current-length-reference-extents-v2.json').read_bytes());_,coasts=land()
    for group,(title,(west,east,south,north)) in GROUPS.items():
        rows=[r for r in document['records'] if r['map_group']==group]
        x1,y1=world([west,north]);x2,y2=world([east,south]);scale=930/(x2-x1);height=(y2-y1)*scale
        footer=110+height+len(rows)*38+35;canvas_height=footer+70
        root=ET.Element('{'+NS+'}svg',{'width':'1000','height':str(canvas_height),'viewBox':f'0 0 1000 {canvas_height}','role':'img','aria-label':title})
        def add(tag,attributes=None,text=None):
            n=ET.SubElement(root,'{'+NS+'}'+tag,attributes or {});n.text=text;return n
        def text(x,y,size,value):add('text',{'x':str(x),'y':str(y),'font-size':str(size),'font-family':'Arial','fill':'#163b49'},value)
        add('rect',{'width':'1000','height':str(canvas_height),'fill':'#f3f7f8'})
        text(35,38,26,title);text(35,73,18,'Declared principal geographic routes · WGS84 length estimates · nominal paths shown')
        add('rect',{'x':'35','y':'100','width':'930','height':str(height),'fill':'#e7f1f4'})
        local=lambda p:(35+(p[0]-x1)*scale,100+(p[1]-y1)*scale)
        def ring(points):return ' '.join(('M' if i==0 else 'L')+f'{x:.3f},{y:.3f}' for i,(x,y) in enumerate(local(p) for p in points))+' Z'
        clipped=coasts.intersection(box(x1,y1,x2,y2))
        for polygon in getattr(clipped,'geoms',[clipped]):
            if polygon.geom_type!='Polygon':continue
            add('path',{'d':ring(polygon.exterior.coords)+' '+' '.join(ring(r.coords) for r in polygon.interiors),'fill':'#c7d8dc','stroke':'#77969f','stroke-width':'.7','fill-rule':'evenodd'})
        for i,(row,color) in enumerate(zip(rows,['#087f8c','#ac6812','#7353a0'])):
            points=unwrap(dense(row['coordinates_lon_lat']),anchor=(west+east)/2)
            d=' '.join(('M' if n==0 else 'L')+f'{x:.3f},{y:.3f}' for n,(x,y) in enumerate(local(world(p)) for p in points))
            add('path',{'d':d,'fill':'none','stroke':'#fff','stroke-width':'6','stroke-linejoin':'round'})
            add('path',{'d':d,'fill':'none','stroke':color,'stroke-width':'3','stroke-linejoin':'round'})
            for point in [points[0],points[-1]]:
                x,y=local(world(point));add('circle',{'cx':str(x),'cy':str(y),'r':'4','fill':color,'stroke':'#fff','stroke-width':'1'})
            label=row['entity_id'].removeprefix('current:').replace('-',' ').title();low,high=row['scenario_range_km']
            text(35,145+height+i*38,21,f'{label}: ≈ {row["length_estimate_km"]:,} km · sensitivity {low:,}–{high:,} km')
        text(35,footer,17,'Source context: Tomczak & Godfrey, Figures 8.6 / 11.3. Gate and branch choices are OSW conventions.')
        text(35,footer+28,17,'36 cases per current clear coarse land. Fine coast unchecked. Sensitivity is not annual variation.')
        path=ROOT/f'figures/{group}-current-length-estimates-v2.svg';path.write_bytes(ET.tostring(root,encoding='utf8',xml_declaration=True))


if __name__=='__main__':render_all()
