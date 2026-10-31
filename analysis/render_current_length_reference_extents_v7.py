"""Draw the Atlantic/coastal reference extents with correct periodic geography."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from shapely.geometry import box
from check_current_length_geography_v2 import land,unwrap,world,dense

ROOT=Path(__file__).resolve().parents[1]
NS='http://www.w3.org/2000/svg';ET.register_namespace('',NS)
GROUPS={'antarctic-circuit': ('Antarctic coastal envelope: unrolled one-circuit reference', [-365, 5, -85, -55]), 'azcc': ('Conditional Azores Countercurrent reference length', [-45, -10, 30, 42]), 'dwbc': ('Atlantic DWBC principal corridor reference length', [-85, -25, -50, 65]), 'itf': ('Indonesian Throughflow: selected Makassar-Lombok itinerary', [112, 130, -12, 5]), 'med-outflow': ('Mediterranean Undercurrent principal reference length', [-12, -4, 34, 40]), 'png': ('New Guinea coastal principal reference lengths', [130, 156, -13, 3]), 'solomon': ('Solomon / New Ireland principal reference lengths', [148, 168, -13, 2]), 'persian-overflow': ('Persian Gulf overflow principal reference length', [54, 62, 20, 28]), 'red-overflow': ('Red Sea overflow: northern plume reference length', [42.7, 45, 11.5, 13.3])}
CAPTIONS={'antarctic-circuit': 'Source: Tomczak/Godfrey chapter6. Idealized coastal-system circuit; physical continuity and ice-front axis unverified.', 'azcc': 'Sources: Comas-Rodriguez2011 and retained alongflow review. Subsurface endpoint/continuity hypothesis; not surface drift.', 'dwbc': 'Source: Dengler2004 and retained regional studies. Geographic corridor includes conceptual eddy-mediated connections.', 'itf': 'Source: Sprintall2009. One inflow-to-outflow route; other passages not summed. Fine channel/bathymetric axis unchecked.', 'med-outflow': 'Sources: de Pascual-Collar2019 and Bower2002. Gibraltar-to-Tagus reservoir handoff; far-field salinity excluded.', 'png': 'Sources: Tomczak/Godfrey, Melet2010, Ueki2003. Surface trade-wind and thermocline interpretations remain distinct.', 'solomon': 'Source: Melet2010. Separate principal routes with explicit confluence and EUC handoffs; not added to one another.', 'persian-overflow': 'Source: Bower2000. Northern cascade / Oman-margin route; other branches and far-field salinity excluded.', 'red-overflow': 'Source: Peters2005. Northern descending-plume itinerary to equilibration handoff; Southern Channel not added.'}



def render_all():
    document=json.loads((ROOT/'research/current-length-reference-extents-v7.json').read_bytes());_,coasts=land()
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
        path=ROOT/f'figures/{group}-current-length-estimates-v7.svg';path.write_bytes(ET.tostring(root,encoding='utf8',xml_declaration=True))


if __name__=='__main__':render_all()
