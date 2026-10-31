"""Retain a rejected coastal experiment and an unadmitted offshore alternative."""
from pathlib import Path
import hashlib,itertools,json,math,xml.etree.ElementTree as ET
from shapely.geometry import LineString
from shapely.ops import unary_union
from build_current_reference_path_candidate import display_coordinates,length_km,polygon_parts,PROVINCES

ROOT=Path(__file__).resolve().parents[1]
FILE='research/southern-east-madagascar-route-definition-diagnostic.json'
ID='diagnostic:southern-east-madagascar-route-definition'
OPERATOR='analysis/madagascar_navigation_diagnostic.py'
V1='research/southern-east-madagascar-reference-route-v1-rejected-input.json'
REJECTION='research/southern-east-madagascar-reference-route-v1-rejection.json'
V2='research/southern-east-madagascar-offshore-navigation-candidate.json'
FIGURE='figures/southern-east-madagascar-route-definition-diagnostic.svg'

def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def read(path):return json.loads((ROOT/path).read_bytes())
def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()

def build():
    v1=read(V1);v2=read(V2);rejected=read(REJECTION)
    atlas=ET.parse(PROVINCES).getroot()
    land=unary_union(polygon_parts(next(r.get('d') for r in atlas.iter() if r.get('class')=='land-context')))
    attempts=[]
    for lon,start,end in itertools.product(v1['longitude_offsets_degrees'],v1['endpoint_latitude_offsets_degrees'],v1['endpoint_latitude_offsets_degrees']):
        pts=[[x+lon,y] for x,y in v1['coordinates_lon_lat']];pts[0][1]+=start;pts[-1][1]+=end
        cross=LineString(display_coordinates(pts)).intersection(land)
        attempts.append({'longitude_offset':lon,'start_latitude_offset':start,'end_latitude_offset':end,
            'crosses_coarse_land':cross.length>1e-8,'intersection_display_bounds':list(cross.bounds) if not cross.is_empty else None})
    original_attempts=rejected['attempts']
    same=len(attempts)==len(original_attempts)==27
    for actual,original in zip(attempts,original_attempts):
        same=same and {k:v for k,v in actual.items() if k!='intersection_display_bounds'}=={k:v for k,v in original.items() if k!='intersection_display_bounds'}
        a,b=actual['intersection_display_bounds'],original['intersection_display_bounds']
        same=same and a is not None and b is not None and len(a)==len(b)==4 and all(math.isclose(x,y,rel_tol=0,abs_tol=1e-9) for x,y in zip(a,b))
    if not same or not all(r['crosses_coarse_land'] for r in attempts):
        raise ValueError('Changed rejected Madagascar coastal experiment')
    input_file=v2['input_file'];source=read(input_file)
    if any(v2.get(k)!=v for k,v in source.items()) or source['rank_eligible_published_estimates'] is not False or source['whole_system_length'] is not False:
        raise ValueError('Offshore experiment changed declared scope or source-input projection')
    if v2['input_sha256']!=sha(input_file) or v2['generator_sha256']!=sha(v2['generator_file']):
        raise ValueError('Changed Madagascar offshore experiment producer/input')
    expected=[]
    for lon,start,end in itertools.product(source['longitude_offsets_degrees'],source['endpoint_latitude_offsets_degrees'],source['endpoint_latitude_offsets_degrees']):
        pts=[[x+lon,y] for x,y in source['coordinates_lon_lat']];pts[0][1]+=start;pts[-1][1]+=end
        if LineString(display_coordinates(pts)).intersection(land).length>1e-8:
            raise ValueError('Offshore alternative crosses coarse atlas land')
        expected.append((pts,round(length_km(pts),3)))
    if len(expected)!=27 or [(r['coordinates_lon_lat'],r['length_km']) for r in v2['scenarios']]!=expected:
        raise ValueError('Changed or omitted offshore scenario')
    if round(length_km(v2['coordinates_lon_lat']),3)!=v2['nominal_reference_path_km']:
        raise ValueError('Changed offshore nominal length')
    if v2['reported_approximate_reference_path_km']!=900 or v2['reported_scenario_range_km']!=[800,900]:
        raise ValueError('Renew source/route comparison rather than silently changing conventions')
    inputs=[OPERATOR,V1,REJECTION,V2,input_file,v2['generator_file'],v2['figure'],
        'plans/southern-east-madagascar-reference-route-protocol-v1.md',
        'plans/southern-east-madagascar-reference-route-protocol-v2.md',
        'research/southern-east-madagascar-prose-dimension-admissions.json',
        PROVINCES.relative_to(ROOT).as_posix(),'almanac/release/v0.1.0/tiles.json',FIGURE]
    reported=read('research/southern-east-madagascar-prose-dimension-admissions.json')['measurement']
    if reported['value']!=650:raise ValueError('Changed separately admitted prose extent')
    return {'schema':'osw.current-route-definition-diagnostic.v1','version':'1',
        'current_id':'southern-east-madagascar','entity_id':'current:southern-east-madagascar',
        'status':'offshore_navigation_experiment_not_admitted_current_route',
        'source_url':v2['source_url'],'source_citation':v2['source_citation'],'source_locator':v2['source_locator'],
        'source_access':'Original publisher HTML inspected2026-10-21; source figures not digitized; no original-file checksum claimed.',
        'rejected_v1':{'input_file':V1,'attempts':original_attempts,'rejected_scenarios':27,'reason':'All predeclared routes intersect coarse atlas land; no v1 geometry or length admitted.'},
        'offshore_v2':v2,'published_reported_extent_km':650,
        'offshore_reference_polyline_km':v2['nominal_reference_path_km'],
        'difference_from_reported_extent_km':round(v2['nominal_reference_path_km']-650,3),
        'difference_interpretation':'Different definitions, offshore vertices and endpoints. Not a discrepancy estimate, confidence interval, source correction or validation. No geometry fitted to650km.',
        'endpoint_definition':'Source coastal Cape Sainte Marie near25.5S differs from editorial offshore approach26.1S. Exact named-current termination unresolved.',
        'route_admitted':False,'rank_eligible':False,'physical_current_axis_verified':False,
        'map_feature_admitted':False,'physical_state_passage_verified':False,'annual_extrema_eligible':False,
        'seasonal_playback_eligible':False,'source_figures_digitized':False,
        'next_required_evidence':'Recover source-supported coastal/slope gates and appropriate layer-specific dated axes; resolve offshore-versus-coastal endpoint conventions before route admission. Coarse land clearance alone is insufficient.',
        'figure':FIGURE,'input_sha256':{p:sha(p) for p in inputs}}

def verify_inputs():
    doc=build()
    if (ROOT/FILE).read_bytes()!=encoded(doc):raise ValueError('Stale Madagascar route diagnostic')
    return doc,{**doc['input_sha256'],FILE:sha(FILE)}

def record(doc):
    return {'id':ID,'label':'Southern East Madagascar route definition: coastal rejection and offshore alternative',
        'entity_id':doc['entity_id'],'current_id':doc['current_id'],'status':doc['status'],'rank_eligible':False,
        'source_file':FILE,'source_file_sha256':sha(FILE),'source_json':(ROOT/FILE).read_bytes().decode('utf8'),'document':doc}

def figure():
    ns='http://www.w3.org/2000/svg';ET.register_namespace('',ns)
    svg=ET.Element('{'+ns+'}svg',{'viewBox':'0 0 1200 1040','width':'1200','height':'1040','role':'img','aria-labelledby':'title description'})
    def elem(tag,attrs,text=None):
        node=ET.SubElement(svg,'{'+ns+'}'+tag,attrs);node.text=text;return node
    elem('title',{'id':'title'},'Southern East Madagascar: route definition remains unresolved')
    elem('desc',{'id':'description'},'All27 first coastal scenarios failed coarse land clearance. An offshore alternative clears land but has different endpoints and about900km polyline length, versus the source-reported approximate650km extent. Neither is a verified physical current axis. No route admitted.')
    elem('rect',{'width':'1200','height':'1040','fill':'#f5fafc'})
    lines=[('Southern East Madagascar: route definition unresolved',30),
        ('Published contextual extent: approximately 650 km; no source axis recovered.',22),
        ('Coastal attempt: all 27 scenarios rejected on coarse land intersection.',22),
        ('Offshore alternative: approximately 900 km; 800–900 km cartographic sensitivity.',22),
        ('Different endpoints and offshore bends: no fitting, source correction or physical range.',19),
        ('No current route, map feature, physical state passage or annual geometry admitted.',19)]
    for i,(text,size) in enumerate(lines):
        elem('text',{'x':'28','y':str(43+i*34),'font-size':str(size),'font-family':'sans-serif','fill':'#14364b'},text)
    source=read(V2)
    nested=ET.parse(ROOT/source['figure']).getroot();nested.attrib.update(x='28',y='250',width='1144',height='730',overflow='hidden')
    endpoint_names=dict(zip(source['endpoint_labels'],['20°S offshore gate','Cape offshore approach']))
    for item in list(nested):
        if item.tag=='{'+ns+'}text':
            if item.text not in endpoint_names:nested.remove(item)
            else:item.text=endpoint_names[item.text];item.set('font-size','2.3')
    svg.append(nested)
    elem('text',{'x':'28','y':'1012','font-size':'18','font-family':'sans-serif','fill':'#14364b'},'Nauw et al. (2008), doi:10.1029/2007JC004639. OSW experiment; no source figure digitization.')
    (ROOT/FIGURE).write_bytes(ET.tostring(svg,encoding='utf-8',xml_declaration=True))

if __name__=='__main__':
    figure();doc=build();(ROOT/FILE).write_bytes(encoded(doc))
    print(json.dumps({'status':doc['status'],'v1_rejected':27,'v2_retained':27,'route_admitted':False,'offshore_polyline_km':doc['offshore_reference_polyline_km']}))
