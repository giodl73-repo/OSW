"""Draw the Atlantic/coastal reference extents with correct periodic geography."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from shapely.geometry import box
from check_current_length_geography_v2 import land,unwrap,world,dense

ROOT=Path(__file__).resolve().parents[1]
NS='http://www.w3.org/2000/svg';ET.register_namespace('',NS)
GROUPS={'gulf-mexico': ('Loop Current reference length', [-92, -79, 19, 30]), 'tasman': ('Tasman Front reference length', [150, 177, -40, -28]), 'india-monsoon': ('India coastal and monsoon current lengths', [48, 93, 0, 26]), 'java': ('South Java coastal-system reference length', [95, 120, -13, 2]), 'mauritania': ('Mauritanian summer surface reference length', [-23, -12, 12, 24]), 'greenland-coastal': ('East Greenland coastal reference length', [-50, -25, 57, 71]), 'ligurian': ('Ligurian segment reference length', [5, 11, 41.5, 45])}
CAPTIONS={'gulf-mexico': 'Source: Tomczak/Godfrey chapter16. Extended-loop reference phase; detached rings excluded.', 'tasman': 'Source: Tomczak/Godfrey chapter8. Statistical Australia-New Zealand connection; not a dated axis.', 'india-monsoon': 'Source: Schott/McCreary2001 section5.1. Declared coastal envelopes and southwest-monsoon principal route.', 'java': 'Sources: Tomczak/Godfrey chapter11 and retained regional records. Broader Sumatra-Java interpretation.', 'mauritania': 'Source: Tomczak/Godfrey chapter14. Summer surface branch only; winter undercurrent excluded.', 'greenland-coastal': 'Source: Sutherland/Pickart2008. Conditional northern68N extension; continuity as a separate jet uncertain.', 'ligurian': 'Source: Berta et al.2018. Regional Northern Current segment; Corsica feeders/downstream continuation excluded.'}



def render_all():
    document=json.loads((ROOT/'research/current-length-reference-extents-v4.json').read_bytes());_,coasts=land()
    for group,(title,(west,east,south,north)) in GROUPS.items():
        rows=[r for r in document['records'] if r['map_group']==group]
        x1,y1=world([west,north]);x2,y2=world([east,south]);scale=min(930/(x2-x1),500/(y2-y1));height=(y2-y1)*scale;map_width=(x2-x1)*scale;map_left=35+(930-map_width)/2
        footer=110+height+len(rows)*38+35;canvas_height=footer+70
        root=ET.Element('{'+NS+'}svg',{'width':'1000','height':str(canvas_height),'viewBox':f'0 0 1000 {canvas_height}','role':'img','aria-label':title})
        def add(tag,attributes=None,text=None):
            n=ET.SubElement(root,'{'+NS+'}'+tag,attributes or {});n.text=text;return n
        def text(x,y,size,value):add('text',{'x':str(x),'y':str(y),'font-size':str(size),'font-family':'Arial','fill':'#163b49'},value)
        add('rect',{'width':'1000','height':str(canvas_height),'fill':'#f3f7f8'})
        text(35,38,26,title);text(35,73,18,'Declared principal geographic routes · WGS84 length estimates · nominal paths shown')
        add('rect',{'x':str(map_left),'y':'100','width':str(map_width),'height':str(height),'fill':'#e7f1f4'})
        local=lambda p:(map_left+(p[0]-x1)*scale,100+(p[1]-y1)*scale)
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
        text(35,footer,17,CAPTIONS[group])
        text(35,footer+28,17,'36 cases per current clear coarse land. Fine coast unchecked. Sensitivity is not annual variation.')
        path=ROOT/f'figures/{group}-current-length-estimates-v4.svg';path.write_bytes(ET.tostring(root,encoding='utf8',xml_declaration=True))


if __name__=='__main__':render_all()
