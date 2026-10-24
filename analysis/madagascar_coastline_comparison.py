"""Compare unchanged route experiments against two explicitly identified land masks."""
from pathlib import Path
import hashlib,io,itertools,json,zipfile,xml.etree.ElementTree as ET
import shapefile
from shapely.geometry import LineString,box,shape
from shapely.ops import transform,unary_union
from build_current_reference_path_candidate import display_coordinates,PROVINCES
from build_cartographic_current_state_join import project

ROOT=Path(__file__).resolve().parents[1]
FILE='research/madagascar-coastline-comparison.json'
FIGURE='figures/madagascar-coastline-comparison.svg'
OPERATOR='analysis/madagascar_coastline_comparison.py'
PROTOCOL='plans/madagascar-coastline-comparison-protocol-v1.md'
DIRECTORY='research/source-data/natural-earth-land-10m-5.1.1/'
ARCHIVE=DIRECTORY+'ne_10m_land.zip'
RECEIPT=DIRECTORY+'acquisition.json'
SOURCE_SHA='e547d749445eaa0964aba76738090ec88f5e63c4585122170f98c67a7ea922dc'
V1='research/southern-east-madagascar-reference-route-v1-rejected-input.json'
V2='research/southern-east-madagascar-offshore-navigation-input.json'
REGION=box(42,-28,52,-18)
ID='diagnostic:madagascar-coastline-comparison'

def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def read(path):return json.loads((ROOT/path).read_bytes())
def encoded(value):return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()

def source_land():
    receipt=read(RECEIPT);data=(ROOT/ARCHIVE).read_bytes()
    if sha(ARCHIVE)!=SOURCE_SHA or receipt['sha256']!=SOURCE_SHA or receipt['bytes']!=len(data) or receipt['package_version']!='5.1.1':
        raise ValueError('Changed Natural Earth original archive/edition')
    if shapefile.__version__!='2.3.1':raise ValueError('Use the declared PyShp2.3.1 reader')
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        members={name for name in archive.namelist() if not name.endswith('/')}
        if members!=set(receipt['members']):raise ValueError('Changed Natural Earth archive members')
        for name,expected in receipt['members'].items():
            raw=archive.read(name)
            if len(raw)!=expected['bytes'] or hashlib.sha256(raw).hexdigest()!=expected['sha256']:
                raise ValueError('Changed Natural Earth member: '+name)
        if archive.read('ne_10m_land.VERSION.txt').decode().strip()!='5.1.1':raise ValueError('Wrong land package version')
        if 'GCS_WGS_1984' not in archive.read('ne_10m_land.prj').decode():raise ValueError('Unexpected source CRS')
        options={suffix:io.BytesIO(archive.read('ne_10m_land.'+suffix)) for suffix in ['shp','shx','dbf']}
        with shapefile.Reader(**options) as reader:
            geometries=[];selected=0
            for item in reader.iterShapes(bbox=REGION.bounds):
                geometry=shape(item.__geo_interface__)
                if not geometry.is_valid:raise ValueError('Invalid original land polygon; do not silently repair')
                clipped=geometry.intersection(REGION)
                if not clipped.is_empty:geometries.append(clipped);selected+=1
    land=unary_union(geometries)
    if land.is_empty or not land.is_valid:raise ValueError('Missing/invalid regional land')
    return transform(project,land),selected

def coarse_land():
    from build_motion_state_join import polygon_parts
    root=ET.parse(PROVINCES).getroot()
    return unary_union(polygon_parts(next(r.get('d') for r in root.iter() if r.get('class')=='land-context')))

def scenarios(source):
    for lon,start,end in itertools.product(source['longitude_offsets_degrees'],source['endpoint_latitude_offsets_degrees'],source['endpoint_latitude_offsets_degrees']):
        coords=[[x+lon,y] for x,y in source['coordinates_lon_lat']];coords[0][1]+=start;coords[-1][1]+=end
        if not REGION.contains(LineString(coords)):raise ValueError('A route exceeds the declared land comparison region')
        yield {'longitude_offset_degrees':lon,'start_latitude_offset_degrees':start,'end_latitude_offset_degrees':end,'coordinates_lon_lat':coords}

def land_result(line,land):
    intersection=line.intersection(land)
    return {'land_contact':not intersection.is_empty,'positive_length_intersection':intersection.length>0,
        'intersection_display_length':round(intersection.length,6),
        'legacy_coarse_length_gate_rejected':intersection.length>1e-8}

def compare(experiments,coarse,finer):
    output=[]
    for name,source in experiments:
        for index,row in enumerate(scenarios(source),1):
            line=LineString(display_coordinates(row['coordinates_lon_lat']))
            output.append({'id':f'{name}:{index:02d}','experiment':name,**row,
                'coarse_osw':land_result(line,coarse),'natural_earth_10m':land_result(line,finer)})
    return output

def build():
    finer,selected=source_land();coarse=coarse_land()
    rows=compare([('coastal_v1',read(V1)),('offshore_v2',read(V2))],coarse,finer)
    if len(rows)!=54:raise ValueError('Missing route alternatives')
    groups={}
    for name in ['coastal_v1','offshore_v2']:
        own=[r for r in rows if r['experiment']==name]
        groups[name]={'scenario_count':len(own),'coarse_land_contacts':sum(r['coarse_osw']['land_contact'] for r in own),
            'natural_earth_land_contacts':sum(r['natural_earth_10m']['land_contact'] for r in own),
            'coarse_only_land_contacts':sum(r['coarse_osw']['land_contact'] and not r['natural_earth_10m']['land_contact'] for r in own),
            'both_land_contacts':sum(r['coarse_osw']['land_contact'] and r['natural_earth_10m']['land_contact'] for r in own)}
    inputs=[OPERATOR,PROTOCOL,ARCHIVE,RECEIPT,V1,V2,PROVINCES.relative_to(ROOT).as_posix(),
        'analysis/build_current_reference_path_candidate.py','analysis/build_cartographic_current_state_join.py',
        'research/southern-east-madagascar-route-definition-diagnostic.json',
        'requirements-geography.txt','requirements-test.txt']
    return {'schema':'osw.current-coastline-support-comparison.v1','version':'1',
        'current_id':'southern-east-madagascar','entity_id':'current:southern-east-madagascar',
        'status':'cartographic_land_support_comparison_not_physical_current_geometry',
        'source_url':'https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-land/',
        'source_citation':'Natural Earth1:10 million land polygons, version5.1.1, public domain.',
        'license':'Public domain','license_url':'https://www.naturalearthdata.com/about/terms-of-use/',
        'source_archive_sha256':SOURCE_SHA,'source_scale':'1:10 million, not10-metre resolution',
        'source_crs':'WGS84 geographic longitude/latitude degrees','reader':'PyShp2.3.1',
        'region_longitude_latitude_bounds':[42,-28,52,-18],'source_features_intersecting_region':selected,
        'polygon_handling':'Preserve source parts and holes; no repair, simplification, buffering, snapping or coordinate rounding before intersection. Clip the declared comparison region only.',
        'method':'Same existing geodesic display polylines, densified to at most10km, against each land product in identical OSW equirectangular coordinates.',
        'contact_rule':'Strict nonempty geometric intersection. Positive-length crossings and the legacy coarse>1e-8 display-length rule retained separately. No physical coastal tolerance.',
        'readback_precision':'Intersection display lengths rounded to6 decimals after decisions; source vertices and all contact booleans unrounded. Display lengths are not physical current dimensions.',
        'results':groups,'attempts':rows,'figure':FIGURE,
        'route_admitted':False,'physical_current_axis_verified':False,'map_feature_admitted':False,
        'width_measurement_admitted':False,'annual_extrema_eligible':False,'physical_state_passage_verified':False,
        'rank_eligible':False,'seasonal_playback_eligible':False,
        'interpretation':'Coastline-dependent clearance diagnoses map support. Neither land mask verifies a current axis, shelf/slope correspondence, current endpoints, seasonal geometry or safe navigation.',
        'input_sha256':{p:sha(p) for p in inputs}}

def path_d(geometry):
    polygons=list(geometry.geoms) if geometry.geom_type=='MultiPolygon' else [geometry]
    pieces=[]
    for polygon in polygons:
        if polygon.geom_type!='Polygon':continue
        for ring in [polygon.exterior,*polygon.interiors]:
            points=list(ring.coords);pieces.append('M'+' L'.join(f'{x:.6f},{y:.6f}' for x,y in points)+' Z')
    return ' '.join(pieces)

def figure_bytes(doc):
    ns='http://www.w3.org/2000/svg';ET.register_namespace('',ns)
    root=ET.Element('{'+ns+'}svg',{'viewBox':'0 0 1400 1050','width':'1400','height':'1050','role':'img','aria-labelledby':'title description'})
    def elem(parent,tag,attrs,text=None):
        node=ET.SubElement(parent,'{'+ns+'}'+tag,attrs);node.text=text;return node
    elem(root,'title',{'id':'title'},'Madagascar: same54 route scenarios, two coastline products')
    elem(root,'desc',{'id':'description'},doc['interpretation'])
    elem(root,'rect',{'width':'1400','height':'1050','fill':'#f5fafc'})
    texts=['Madagascar: same 54 route scenarios, two coastlines',
        'Blue dashed: coastal experiment. Orange dotted: offshore alternative. Vertices unchanged.',
        'Land clearance is a map check; no current axis, width or seasonal range is admitted.']
    for i,text in enumerate(texts):elem(root,'text',{'x':'28','y':str(42+i*34),'font-size':str(30 if i==0 else 22),'font-family':'sans-serif','fill':'#12374b'},text)
    fine,_=source_land();coarse=coarse_land()
    west,north=project(43,-18);east,south=project(52,-28)
    for x,label,land,key in [(28,'Coarse OSW coastline',coarse,'coarse_land_contacts'),(714,'Natural Earth: 1:10 million, v5.1.1',fine,'natural_earth_land_contacts')]:
        elem(root,'text',{'x':str(x),'y':'166','font-size':'24','font-family':'sans-serif','fill':'#12374b'},label)
        panel=elem(root,'svg',{'x':str(x),'y':'184','width':'658','height':'720','viewBox':f'{west} {north} {east-west} {south-north}','overflow':'hidden'})
        elem(panel,'rect',{'x':str(west),'y':str(north),'width':str(east-west),'height':str(south-north),'fill':'#e6f2f7'})
        elem(panel,'path',{'d':path_d(land),'fill':'#d4d3c9','fill-rule':'evenodd','stroke':'#687b80','stroke-width':'.07'})
        for attempt in doc['attempts']:
            pts=display_coordinates(attempt['coordinates_lon_lat']);coastal=attempt['experiment']=='coastal_v1'
            elem(panel,'polyline',{'points':' '.join(f'{a:.6f},{b:.6f}' for a,b in pts),'fill':'none','stroke':'#165d9b' if coastal else '#b64915',
                'stroke-width':'.09','stroke-opacity':'.55','stroke-dasharray':'.6 .25' if coastal else '.12 .3'})
        for i,(name,text) in enumerate([('coastal_v1','Coastal'),('offshore_v2','Offshore')]):
            count=doc['results'][name][key]
            elem(root,'text',{'x':str(x),'y':str(936+i*30),'font-size':'22','font-family':'sans-serif','fill':'#12374b'},f'{text}: {count} of27 scenarios contact this land mask.')
    elem(root,'text',{'x':'28','y':'1017','font-size':'19','font-family':'sans-serif','fill':'#12374b'},'Natural Earth public-domain land; 1:10 million is a map scale, not 10-metre accuracy. OSW comparison; not a navigation chart.')
    elem(root,'text',{'x':'28','y':'1043','font-size':'18','font-family':'sans-serif','fill':'#12374b'},'Both panels use the same equirectangular projection and unchanged route vertices.')
    return ET.tostring(root,encoding='utf-8',xml_declaration=True)

def verify_inputs():
    doc=build()
    if (ROOT/FILE).read_bytes()!=encoded(doc):raise ValueError('Stale coastline comparison')
    if (ROOT/FIGURE).read_bytes()!=figure_bytes(doc):raise ValueError('Stale coastline comparison figure')
    return doc,{**doc['input_sha256'],FILE:sha(FILE),FIGURE:sha(FIGURE)}

def record(doc):
    return {'id':ID,'label':'Madagascar: land-mask support comparison for54 unchanged route scenarios',
        'entity_id':doc['entity_id'],'current_id':doc['current_id'],'status':doc['status'],'rank_eligible':False,
        'source_file':FILE,'source_file_sha256':sha(FILE),'source_json':(ROOT/FILE).read_bytes().decode('utf8'),'document':doc}

if __name__=='__main__':
    doc=build();(ROOT/FILE).write_bytes(encoded(doc));(ROOT/FIGURE).write_bytes(figure_bytes(doc))
    print(json.dumps({'status':doc['status'],'results':doc['results']}))
