"""A reproducible coast-following atlas reference; no velocity-axis inference."""
from pathlib import Path
import hashlib,itertools,json,math,xml.etree.ElementTree as ET
from pyproj import CRS,Transformer,Geod
from shapely.geometry import LineString,Point,MultiPoint
from shapely.ops import transform,substring
import madagascar_coastline_comparison as coast

ROOT=coast.ROOT
FILE='research/southern-east-madagascar-coastal-reference-curve.json'
FIGURE='figures/southern-east-madagascar-coastal-reference-curve.svg'
OPERATOR='analysis/madagascar_reference_curve.py'
PROTOCOL='plans/southern-east-madagascar-coastal-reference-curve-protocol-v1.md'
ROUTE_ID='southern-east-madagascar-coastal-reference-curve'
CATALOGUE='research/ocean-current-working-reference-routes.json'
BASE_CATALOGUE='research/ocean-current-reference-path-candidates.json'
BASE_JOIN='research/ocean-current-reference-route-state-join.json'
WORKING_JOIN='research/ocean-current-working-reference-route-state-join.json'
GEOD=Geod(ellps='WGS84')
LOCAL='+proj=aeqd +lat_0=-23 +lon_0=47.5 +datum=WGS84 +units=m +no_defs'
TO_LOCAL=Transformer.from_crs('EPSG:4326',CRS.from_proj4(LOCAL),always_xy=True)
TO_GEO=Transformer.from_crs(CRS.from_proj4(LOCAL),'EPSG:4326',always_xy=True)

def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def encoded(value):return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def inverse_display(x,y):return (x-60)/1480*360-180,90-(y-90)/740*180
def distance(coords):return sum(GEOD.inv(*a,*b)[2] for a,b in zip(coords,coords[1:]))/1000
def readback(value,digits):
    result=round(value,digits)
    return 0.0 if result==0 else result

def gate_point(ring,line,axis,largest):
    cross=ring.intersection(line)
    points=[cross] if cross.geom_type=='Point' else list(cross.geoms) if cross.geom_type=='MultiPoint' else []
    if not points:raise ValueError('Gate must have isolated contour intersections')
    return (max if largest else min)(points,key=lambda p:p.coords[0][axis])

def arc_forward(ring,a,b):
    if a<=b:return list(substring(ring,a,b).coords)
    return list(substring(ring,a,ring.length).coords)+list(substring(ring,0,b).coords)[1:]

def shorter_arc(ring,start,end):
    a,b=ring.project(start),ring.project(end)
    choices=[arc_forward(ring,a,b),list(reversed(arc_forward(ring,b,a)))]
    if any(len(c)<2 for c in choices):raise ValueError('Degenerate contour arc')
    return min(choices,key=distance)

def densify(coords,maximum_metres=1000):
    output=[coords[0]]
    for a,b in zip(coords,coords[1:]):
        n=max(1,math.ceil(GEOD.inv(*a,*b)[2]/maximum_metres))
        if n>1:output.extend(GEOD.npts(*a,*b,n-1))
        output.append(b)
    return output

def land_contact(coords,land):
    return not LineString([coast.project(*p) for p in densify(coords)]).intersection(land).is_empty

def build():
    comparison,_=coast.verify_inputs()
    if comparison['results']['coastal_v1']['both_land_contacts']!=27:raise ValueError('Renew preceding route evidence')
    fine,_=coast.source_land();geographic=transform(inverse_display,fine)
    pieces=list(geographic.geoms) if geographic.geom_type=='MultiPolygon' else [geographic]
    owned=[p for p in pieces if p.contains(Point(47,-23))]
    if len(owned)!=1:raise ValueError('Ambiguous Madagascar land component')
    island=transform(TO_LOCAL.transform,owned[0]);coarse=coast.coarse_land();cases=[]
    for offset in [10000,25000,50000]:
        buffered=island.buffer(offset,quad_segs=8,join_style='round')
        if buffered.geom_type!='Polygon':raise ValueError('Ambiguous offset contour')
        ring=LineString(transform(TO_GEO.transform,buffered.exterior).coords)
        for latitude,longitude in itertools.product([-19.9,-20.0,-20.1],[45.2,45.3,45.4]):
            start=gate_point(ring,LineString([(42,latitude),(52,latitude)]),0,True)
            end=gate_point(ring,LineString([(longitude,-28),(longitude,-24)]),1,False)
            full=shorter_arc(ring,start,end)
            bounds=LineString(full).bounds
            if not (45<=bounds[0]<=bounds[2]<=51 and -27.5<=bounds[1]<=bounds[3]<=-19.5):
                raise ValueError('Arc leaves declared eastern/southeastern branch region')
            simplified=transform(TO_GEO.transform,transform(TO_LOCAL.transform,LineString(full)).simplify(250,preserve_topology=False))
            raw=list(simplified.coords);export=[[round(x,8),round(y,8)] for x,y in raw]
            full_contact=land_contact(full,fine);export_contact=land_contact(export,fine)
            if full_contact or export_contact:raise ValueError('Coastal reference arc contacts finer land')
            length=distance(export);full_length=distance(full)
            cases.append({'id':f'offset{offset}:start{abs(latitude):.1f}:end{longitude:.1f}',
                'offset_parameter_projected_metres':offset,'start_gate_latitude':latitude,'end_gate_longitude':longitude,
                'coordinates_lon_lat':export,'length_km':round(length,3),'full_contour_length_km':round(full_length,3),
                'full_minus_simplified_length_km':round(full_length-length,3),
                'export_length_change_km':readback(length-distance(raw),6),'full_contour_vertices':len(full),'export_vertices':len(export),
                'full_contour_finer_land_contact':full_contact,'export_finer_land_contact':export_contact,
                'coarse_osw_land_contact':land_contact(export,coarse)})
    nominal=next(c for c in cases if c['offset_parameter_projected_metres']==25000 and c['start_gate_latitude']==-20 and c['end_gate_longitude']==45.3)
    low,high=min(c['length_km'] for c in cases),max(c['length_km'] for c in cases)
    dependencies=[OPERATOR,PROTOCOL,coast.OPERATOR,coast.FILE,coast.ARCHIVE,coast.RECEIPT,
        'requirements-geography.txt','requirements-test.txt','research/southern-east-madagascar-prose-dimension-admissions.json']
    from build_cartographic_current_state_join import load_states
    from shapely.geometry import box
    from shapely.affinity import translate
    from build_current_reference_path_candidate import display_coordinates
    states=load_states();lines=[LineString(display_coordinates(c['coordinates_lon_lat'])) for c in cases]
    for case,line in zip(cases,lines):case['atlas_state_crossings']=sorted(code for code,polygon in states.items() if line.intersection(polygon).length>1e-8)
    tiles_file='almanac/release/v0.1.0/tiles.json';dependencies.append(tiles_file)
    movies=[]
    nominal_line=LineString(display_coordinates(nominal['coordinates_lon_lat']))
    for tile in json.loads((ROOT/tiles_file).read_bytes()):
        west,east=tile['longitude_range_unwrapped'];south,north=tile['latitude_range'];crop=box(*coast.project(west,north),*coast.project(east,south))
        fractions=[max(translate(line,xoff=shift).intersection(crop).length/line.length for shift in [-1480,0,1480]) for line in lines]
        if max(fractions)<=1e-8:continue
        nominal_fraction=max(translate(nominal_line,xoff=shift).intersection(crop).length/nominal_line.length for shift in [-1480,0,1480])
        movies.append({'tile_id':tile['tile_id'],'url':tile['url'],'source_id':tile['source_id'],'zoom':tile['zoom'],
            'nominal_display_route_fraction':round(nominal_fraction,6),'scenario_display_route_fraction_range':[round(min(fractions),6),round(max(fractions),6)],
            'complete_display_route_in_all_scenarios':min(fractions)>=1-1e-8})
    movies.sort(key=lambda r:(-r['zoom'],r['tile_id']));complete=[r for r in movies if r['complete_display_route_in_all_scenarios']]
    return {'schema':'osw.current-reference-path-input.v1','current_id':'southern-east-madagascar','name':'Southern East Madagascar Current',
        'status':'editorial_coastal_reference_curve_scientific_axis_review_pending','geometry_role':'osw_offshore_coastal_reference_curve',
        'crs':'OGC:CRS84','scope':'Eastern/southeastern Madagascar offshore coastal reference curve from an editorial20S gate to45.3E Cape approach. Exact gates and projected coast offsets are OSW conventions; not observed current endpoints, a velocity axis or downstream continuation.',
        'layer':'Undated geographic upper-current context; no fixed depth or velocity-derived axis.',
        'time_convention':'Undated reference geometry; not an April2001 path, seasonal state or annual mean.',
        'source_url':'https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2007JC004639',
        'source_citation':'Nauw et al.2008, doi:10.1029/2007JC004639, Introduction2/6; Natural Earth land1:10 million5.1.1 for geographic construction.',
        'source_locator':'Introduction2: eastern branch from approximately20S to Cape Sainte Marie near25.5S. Introduction6: downstream alternatives unresolved. Exact contour/gates selected by OSW.',
        'method':'Local WGS84 AEQD land buffers; eastern start/southern Cape gates; shorter contour arc;250m projected simplification; WGS84 geodesic polyline summation. All geometry parameters predeclared independently of650km report.',
        'projection':LOCAL,'geometry_parameter_role':'Arbitrary projected offshore cartographic offsets, not measured coast distance, width or current-core position.',
        'nominal_reference_path_km':nominal['length_km'],'reported_approximate_reference_path_km':round(nominal['length_km']/100)*100,
        'scenario_range_km':[low,high],'reported_scenario_range_km':[math.floor(low/100)*100,math.ceil(high/100)*100],
        'scenario_count':len(cases),'coordinates_lon_lat':nominal['coordinates_lon_lat'],'scenarios':cases,
        'published_reported_extent_km':650,'difference_from_reported_extent_km':round(nominal['length_km']-650,3),
        'difference_interpretation':'Different source extent and OSW coastal reference definition; not source-error inference or calibration.',
        'rank_eligible_published_estimates':False,'candidate_comparison_group':'osw_offshore_coastal_reference_curves','whole_system_length':False,
        'route_extent_kind':'offshore coastal branch reference curve','physical_current_axis_verified':False,
        'physical_state_passage_verified':False,'width_measurement_admitted':False,'annual_extrema_eligible':False,'seasonal_playback_eligible':False,
        'source_land_version':'Natural Earth1:10 million5.1.1; not10-metre accuracy','source_land_sha256':coast.SOURCE_SHA,
        'map_land_check':'Every full and exported contour arc clears the finer source land under strict1km-densified checks. Coarse atlas contacts recorded separately. Neither check verifies a current axis, bathymetry or navigation safety.',
        'nominal_atlas_state_crossings':sorted(code for code,polygon in states.items() if nominal_line.intersection(polygon).length>1e-8),
        'nasa_movie_context':movies,'recommended_nasa_tile_id':complete[0]['tile_id'] if complete else None,
        'nasa_crop_recommendation_rule':'Highest zoom containing every retained editorial curve; tile ID tie-break. Navigation only.',
        'state_relation_role':'Editorial curve/display-region crossing; physical current passage unresolved.',
        'remaining_gates':['External scientific axis review; coast offset is not a diagnosed current position.','Verify source-defined coastal/slope endpoint conventions and layer-specific dated axes.','No width buffer, occupied area, physical state passage or seasonal geometry inferred.'],
        'generator_file':OPERATOR,'generator_sha256':sha(OPERATOR),'input_file':PROTOCOL,'input_sha256':sha(PROTOCOL),
        'input_dependencies_sha256':{p:sha(p) for p in dependencies},'figure':FIGURE,
        'map_view_box':[972.6666666667,534,41.1111111111,41.1111111111],'figure_aspect_ratio':1.2,
        'coordinate_selection':'Natural Earth coastline, projected offshore offsets and explicit eastern/southern gates. This is reproducible geographic construction, not current-position extraction.',
        'scenario_rule':'All27 combinations of10/25/50km projected offset,19.9/20.0/20.1S start and45.2/45.3/45.4E end. No current-width, annual-range or confidence interpretation.'}

def catalogue_row(doc):
    return {'id':ROUTE_ID,'current_id':doc['current_id'],'name':doc['name'],'status':doc['status'],
        'comparison_group':doc['candidate_comparison_group'],'scope':doc['scope'],'route_extent_kind':doc['route_extent_kind'],
        'approximate_reference_path_km':doc['reported_approximate_reference_path_km'],'scenario_range_km':doc['reported_scenario_range_km'],
        'scenario_count':doc['scenario_count'],'source_url':doc['source_url'],'source_locator':doc['source_locator'],
        'supporting_sources':[{'url':'https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-land/','role':'Coast geometry only; no current position.'}],
        'candidate_file':FILE,'candidate_sha256':sha(FILE),'generator_sha256':sha(OPERATOR),'figure':FIGURE,
        'nominal_atlas_state_crossings':doc['nominal_atlas_state_crossings'],'recommended_nasa_tile_id':doc['recommended_nasa_tile_id'],
        'remaining_gates':doc['remaining_gates'],'parent_current_id':None,'parent_scope_note':None,'ordering_sensitivity':None,
        'source_ids':sorted([source_record()['id'],primary_source_record()['id']])}

def working_catalogue(doc):
    import copy
    source=coast.read(BASE_CATALOGUE);result=copy.deepcopy(source)
    row=catalogue_row(doc);result['candidates'].append(row)
    result['candidates'].sort(key=lambda r:(-r['approximate_reference_path_km'],r['id']))
    plan=copy.deepcopy(coast.read('research/southern-east-madagascar-prose-dimension-admissions.json')['route_planning_decision'])
    plan.update(candidate_ids=[ROUTE_ID],reference_path_decision='editorial_candidate_present_scientific_review_pending',
        existing_scope='Published approximate650km branch extent and a separate OSW coast-following reference curve. The curve is not a diagnosed current axis.',
        next_action='Review source-specific coastal/slope gates and dated axes. Projected coast offsets are cartographic parameters; preserve physical, annual and width gaps.',
        planning_basis='Current identity and prose dimensions admitted separately. Source coastline supports an editorial reference curve only.')
    result['remaining_current_decisions'].append(plan)
    strategies=result['planning_taxonomy']['strategies']
    strategy=next((r for r in strategies if r['id']==plan['route_strategy_id']),None)
    if strategy is None:
        strategy={'id':plan['route_strategy_id'],'label':plan['route_strategy_label'],'description':plan['planning_basis'],'current_count':0,'unbuilt_count':0};strategies.append(strategy)
    strategy['current_count']+=1
    result['counts'].update(currents_with_route_candidates=source['counts']['currents_with_route_candidates']+1,
        route_candidates=len(result['candidates']),coastal_reference_curve_candidates=1,route_decision_records=len(result['remaining_current_decisions']))
    accepted=coast.read('research/ocean-current-working-catalogue.json')['entries']
    owners={r['current_id'] for r in result['candidates']}
    result['counts'].update(accepted_current_names=len(accepted),currents_without_any_reference_card=len(accepted)-len(owners))
    result.update(working_catalogue_version='0.2.0-draft-coastal-curve-1',base_catalogue_file=BASE_CATALOGUE,
        base_catalogue_sha256=sha(BASE_CATALOGUE),coastal_curve_file=FILE,
        effective_accepted_current_count=101,working_scope='Historical76 candidates plus one source-coastline editorial reference curve. Coast-offset curves are excluded from waypoint-route ordering and published-length rankings.',
        land_source_record=source_record(),primary_source_record=primary_source_record(),working_input_sha256={p:sha(p) for p in [BASE_CATALOGUE,FILE,OPERATOR,PROTOCOL,'research/ocean-current-working-catalogue.json']})
    return result

def source_record():
    url='https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-land/'
    title='Natural Earth land polygons, 1:10 million, version5.1.1'
    return {'id':'source:'+hashlib.sha256(url.encode()).hexdigest()[:16],'kind':'external','label':title,'title':title,'url':url,
        'doi':None,'authors':[],'publication_date_parts':None,'publisher':'Natural Earth contributors',
        'preferred_citation':title+'; public domain; naturalearthdata.com.',
        'metadata_status':'Official product and terms inspected; original archive and every member checksum retained.',
        'dataset_version':'5.1.1','license':'Public domain','license_url':'https://www.naturalearthdata.com/about/terms-of-use/',
        'material_use_class':'public_domain_geographic_dataset','provider_asset_redistributed':True,
        'rights_status':'Public-domain source data redistribution permitted by Natural Earth terms.',
        'rights_policy_url':'https://www.naturalearthdata.com/about/terms-of-use/','rights_review_date':'2026-10-21',
        'path':coast.ARCHIVE,'repository_path':coast.ARCHIVE,'source_file_sha256':coast.SOURCE_SHA,
        'used_in_collections':['reference_routes','diagnostics','state_links'],'metadata_note':'Map scale1:10 million is not10-metre accuracy. Land geometry does not establish a current axis, width or dated coastline.'}

def primary_source_record():
    source=coast.read('research/southern-east-madagascar-prose-dimension-admissions.json')['source_record']
    source['used_in_collections']=list(dict.fromkeys(source['used_in_collections']+['reference_routes','diagnostics','state_links']))
    source['metadata_note']+=' The geographic reference uses the described eastern-coast branch; exact gates, coast offsets and display-state joins are OSW conventions, not source station positions or physical passage claims.'
    return source

def working_state_join(doc):
    import copy
    from build_reference_route_state_join import crossing_summary
    result=copy.deepcopy(coast.read(BASE_JOIN));row=catalogue_row(doc)
    for code,summary in crossing_summary(doc,set(result['states'])).items():
        state=result['states'][code]
        state['route_candidates'].append({'candidate_id':ROUTE_ID,'current_id':doc['current_id'],'name':doc['name'],
            'scope':doc['scope'],'layer':doc['layer'],'time_convention':doc['time_convention'],
            'comparison_group':row['comparison_group'],'route_extent_kind':doc['route_extent_kind'],
            'route_url':'reference-routes.html#'+ROUTE_ID,'source_url':doc['source_url'],**summary})
        state['route_candidates'].sort(key=lambda r:(r['name'].casefold(),r['candidate_id']))
        state['current_count']=len({r['current_id'] for r in state['route_candidates']})
        state['nominal_current_count']=len({r['current_id'] for r in state['route_candidates'] if r['nominal_crossing']})
    result['counts'].update(route_candidates=77,currents_with_route_candidates=71,
        states_with_candidate_crossings=sum(bool(s['route_candidates']) for s in result['states'].values()),
        candidate_state_pairs=sum(len(s['route_candidates']) for s in result['states'].values()))
    result.update(working_catalogue_version='0.2.0-draft-coastal-curve-1',base_join_file=BASE_JOIN,
        base_join_sha256=sha(BASE_JOIN),working_scope='Historical route navigation joins plus one undated geographic coast-offset curve; no physical current passage or seasonal occupancy.')
    result['input_sha256'].update({p:sha(p) for p in [BASE_JOIN,CATALOGUE,FILE,OPERATOR,'analysis/build_reference_route_state_join.py']})
    return result

def figure_bytes(doc):
    ns='http://www.w3.org/2000/svg';ET.register_namespace('',ns)
    root=ET.Element('{'+ns+'}svg',{'viewBox':'0 0 1000 1200','width':'1000','height':'1200','role':'img','aria-labelledby':'title description'})
    def elem(parent,tag,attrs,text=None):
        node=ET.SubElement(parent,'{'+ns+'}'+tag,attrs);node.text=text;return node
    elem(root,'title',{'id':'title'},'Southern East Madagascar: offshore coastal reference curve')
    elem(root,'desc',{'id':'description'},doc['scope']+' All27 geographic conventions clear both land masks; no measured current axis or width.')
    elem(root,'rect',{'width':'1000','height':'1200','fill':'#f5fafc'})
    lines=[('Southern East Madagascar: coastal reference curve',30),
        (f"Approximately {doc['reported_approximate_reference_path_km']} km; {doc['reported_scenario_range_km'][0]}–{doc['reported_scenario_range_km'][1]} km convention sensitivity.",24),
        ('Nominal: 25 km projected coast offset. This parameter is not current width.',21),
        ('Published branch extent: approximately 650 km, a separate source report.',21),
        ('Undated geographic guide; no measured axis, physical envelope or annual range.',21)]
    for i,(text,size) in enumerate(lines):elem(root,'text',{'x':'25','y':str(42+i*34),'font-size':str(size),'font-family':'sans-serif','fill':'#12374b'},text)
    land,_=coast.source_land();west,north=coast.project(42,-18);east,south=coast.project(52,-28)
    panel=elem(root,'svg',{'x':'28','y':'220','width':'944','height':'810','viewBox':f'{west} {north} {east-west} {south-north}','overflow':'hidden'})
    elem(panel,'rect',{'x':str(west),'y':str(north),'width':str(east-west),'height':str(south-north),'fill':'#e6f2f7'})
    elem(panel,'path',{'d':coast.path_d(land),'fill':'#d4d3c9','fill-rule':'evenodd','stroke':'#687b80','stroke-width':'.06'})
    for case in doc['scenarios']:
        pts=[coast.project(*p) for p in case['coordinates_lon_lat']]
        elem(panel,'polyline',{'points':' '.join(f'{x:.6f},{y:.6f}' for x,y in pts),'fill':'none','stroke':'#4b9bb1','stroke-width':'.06','stroke-opacity':'.45'})
    pts=[coast.project(*p) for p in doc['coordinates_lon_lat']]
    elem(panel,'polyline',{'points':' '.join(f'{x:.6f},{y:.6f}' for x,y in pts),'fill':'none','stroke':'#114d86','stroke-width':'.16','stroke-dasharray':'.65 .25'})
    for (x,y),text in zip([pts[0],pts[-1]],['20°S reference gate','45.3°E Cape approach']):
        elem(panel,'circle',{'cx':str(x),'cy':str(y),'r':'.25','fill':'#114d86'})
        elem(panel,'text',{'x':str(x+.6),'y':str(y),'font-size':'.8','font-family':'sans-serif','fill':'#12374b'},text)
    for i,text in enumerate(['Dashed: nominal geographic curve. Pale: all 27 declared conventions.',
        'Exported curves clear both masks; full contours clear finer land. Axis review remains open.',
        'Source geography: Nauw et al. (2008), doi:10.1029/2007JC004639, Introduction2/6.',
        'Made with Natural Earth land 1:10 million v5.1.1. Map scale is not 10-metre accuracy.',
        'Equirectangular map. Geographic construction only; not an observed current axis.']):
        elem(root,'text',{'x':'25','y':str(1060+i*30),'font-size':'19','font-family':'sans-serif','fill':'#12374b'},text)
    return ET.tostring(root,encoding='utf-8',xml_declaration=True)

def verify_inputs():
    doc=build()
    if (ROOT/FILE).read_bytes()!=encoded(doc):raise ValueError('Stale Madagascar coastal reference curve')
    if (ROOT/FIGURE).read_bytes()!=figure_bytes(doc):raise ValueError('Stale coastal reference figure')
    catalog=working_catalogue(doc)
    if (ROOT/CATALOGUE).read_bytes()!=encoded(catalog):raise ValueError('Stale working reference catalogue')
    join=working_state_join(doc)
    if (ROOT/WORKING_JOIN).read_bytes()!=encoded(join):raise ValueError('Stale working route/state join')
    _,coast_inputs=coast.verify_inputs()
    return doc,catalog,{**coast_inputs,**doc['input_dependencies_sha256'],**catalog['working_input_sha256'],
        **join['input_sha256'],FILE:sha(FILE),FIGURE:sha(FIGURE),CATALOGUE:sha(CATALOGUE),WORKING_JOIN:sha(WORKING_JOIN)}

if __name__=='__main__':
    doc=build();(ROOT/FILE).write_bytes(encoded(doc));(ROOT/FIGURE).write_bytes(figure_bytes(doc));(ROOT/CATALOGUE).write_bytes(encoded(working_catalogue(doc)));(ROOT/WORKING_JOIN).write_bytes(encoded(working_state_join(doc)))
    print(json.dumps({k:doc[k] for k in ['scenario_count','nominal_reference_path_km','reported_approximate_reference_path_km','reported_scenario_range_km','difference_from_reported_extent_km']}))
