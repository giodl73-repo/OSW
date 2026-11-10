"""Interpolate compatible retained depth corners; regional scenarios only."""
import copy,csv,hashlib,io,json,math,os,signal,socket,time
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery

ROOT=Path(__file__).resolve().parents[1]
OP='research/barents-makassar-depth-surface-operator-v1.json'
SOURCE='research/barents-makassar-paired-section-geometry-v1.json'
SOURCE_SHA='0567e901b74ba28e2bf7033938bbcbc96d8fbf52c3d39feed0ee46645e481a89'
REVIEW='research/current-depth-barents-makassar-paired-section-geometry-source-review-v1.json'
DATES=['2022-03-15T00:00:00Z','2022-06-15T00:00:00Z','2022-09-15T00:00:00Z','2022-12-15T00:00:00Z']
CUTS={'current:north-cape':[(f'section-{v}e',v) for v in [20,22,24,26]],'current:indonesian-throughflow':[(f'section-{v}s',-v) for v in [1,2,3,4]]}
BEARINGS={'current:north-cape':90,'current:indonesian-throughflow':180}
RADIUS=6371008.8

def finite(x):return type(x) in (int,float) and math.isfinite(x)
def encode(x):return (json.dumps(x,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()

def latitude_weights(south,north):
    if not all(finite(v) for v in [south,north]) or not -75<=south<north<=75:raise ValueError('Ordered supported latitudes required')
    lo,hi=map(math.radians,[south,north]);mid=(lo+hi)/2;half=(hi-lo)/2
    # Integrate an affine latitude field against the spherical cos(latitude)
    # Jacobian. Stable series for1-h*cot(h); remainder is O(h**8).
    correction=half**2/3+half**4/45+2*half**6/945 if half<.001 else 1-half/math.tan(half)
    north_weight=.5-math.tan(mid)*correction/(2*half)
    if not 0<north_weight<1:raise ValueError('Positive spherical integration weights')
    return 1-north_weight,north_weight,2*math.cos(mid)*math.sin(half)

def integrate_corners(corners):
    if len(corners)!=4:raise ValueError('Four matched finite depth corners required')
    points=[c['lon_lat'] for c in corners]
    if any(len(p)!=2 or not all(finite(v) for v in p) or not -180<=p[0]<=180 or not -75<=p[1]<=75 for p in points):raise ValueError('Finite native geographic corners')
    xs=sorted({p[0] for p in points});ys=sorted({p[1] for p in points})
    if len(xs)!=2 or len(ys)!=2 or len({tuple(p) for p in points})!=4 or not 0<xs[1]-xs[0]<=2.2 or not 0<ys[1]-ys[0]<=1.1:raise ValueError('One original rectangular neighboring-cut cell required')
    lookup={tuple(c['lon_lat']):c for c in corners};ordered=[lookup[xs[0],ys[0]],lookup[xs[1],ys[0]],lookup[xs[1],ys[1]],lookup[xs[0],ys[1]]]
    sw,nw,jacobian=latitude_weights(*ys);weights=[sw/2,sw/2,nw/2,nw/2]
    area=RADIUS**2*math.radians(xs[1]-xs[0])*jacobian
    values=[];bounds=[]
    for c in ordered:
        up,down=c['upper_depth_m'],c['lower_depth_m'];h=c['thickness_m'];b=c['sampling_thickness_bounds_m']
        if not all(finite(v) for v in [up,down,h]) or not 0<=up<down or not math.isclose(h,down-up,abs_tol=1e-8) or len(b)!=2 or not all(finite(v) for v in b) or not 0<=b[0]<=h<=b[1]:raise ValueError('Finite paired source contours and sampling scenarios required')
        values.append(h);bounds.append(b)
    central=area*sum(w*h for w,h in zip(weights,values))/1e9
    scenarios=[area*sum(w*b[k] for w,b in zip(weights,bounds))/1e9 for k in [0,1]]
    if not scenarios[0]<=central<=scenarios[1]:raise ValueError('Scenario-volume enclosure in the declared interpolant')
    polygon=[list(c['lon_lat']) for c in ordered];polygon.append(polygon[0][:])
    return {'horizontal_polygon_lon_lat':polygon,'corners_sw_se_ne_nw':copy.deepcopy(ordered),'surface_footprint_km2':area/1e6,'spherical_latitude_weights_south_north':[sw,nw],'conditional_partial_component_volume_km3':central,'sampling_bracket_volume_scenarios_km3':scenarios}

def native_overlap(corners):
    return max(c['native_depth_indices_inclusive'][0] for c in corners)<=min(c['native_depth_indices_inclusive'][1] for c in corners)

def endpoint(case,cut_value):
    owner=case['entity_id'];fixed=0 if owner=='current:north-cape' else 1;varying=1-fixed
    if case['component_bearing_degrees_true']!=BEARINGS[owner] or case['velocity_threshold_m_s']!=.1 or case['named_current_axis_independently_validated'] is not False or case['whole_section_area_established'] is not False or case['volume_km3'] is not None:raise ValueError('Original nonphysical branch component context required')
    columns=case['columns'];strips=case['strips']
    if case['status']=='ORIGINAL_AXIS_UNRESOLVED_NO_SECTION_GEOMETRY':
        if columns or strips or case['conditional_partial_area_km2'] is not None:raise ValueError('Unresolved endpoint cannot acquire geometry')
        return None
    if case['status']!='CONDITIONAL_PARTIAL_COMPONENT_SECTION_GEOMETRY' or len(strips)!=len(columns)-1 or not columns:raise ValueError('Original paired section descriptors required')
    position=columns[0]['sampled_lon_lat'][fixed]
    for i,c in enumerate(columns):
        p=c['sampled_lon_lat'];scale=math.cos(math.radians(p[1])) if fixed==0 else 1.
        if c['native_column_index']!=i or abs(p[fixed]-position)>1e-8 or RADIUS*math.radians(abs(p[fixed]-cut_value))*scale>5000:raise ValueError('Original fixed axis, native order and5km target-coordinate tolerance')
        if i and p[varying]<=columns[i-1]['sampled_lon_lat'][varying]:raise ValueError('Ascending transverse native coordinates')
    for i,s in enumerate(strips):
        if (s['left_column_index'],s['right_column_index'])!=(i,i+1):raise ValueError('No skipped original native strip')
    return {'fixed_axis':fixed,'transverse_axis':varying,'fixed_coordinate':position,'transverse_coordinates':[c['sampled_lon_lat'][varying] for c in columns]}

def corners_for(case,strip_index,patch):
    indices=[patch['left_run_index'],patch['right_run_index']];out=[]
    for column_index,run_index in zip([strip_index,strip_index+1],indices):
        c=case['columns'][column_index];r=c['runs'][run_index]
        if r['status']!='FINITE_PAIRED_COMPONENT_CONTOURS':raise ValueError('No censored corner substitution')
        out.append({'lon_lat':copy.deepcopy(c['sampled_lon_lat']),'source_case_pointer':case['source_descriptor_pointer'],'source_section_id':case['section_id'],'source_column_index':column_index,'source_run_index':run_index,**{k:copy.deepcopy(r[k]) for k in ['native_depth_indices_inclusive','upper_depth_m','lower_depth_m','thickness_m','sampling_thickness_bounds_m']}})
    return out

def segment(a,b,cut_a,cut_b):
    if (a['entity_id'],a['snapshot_time_utc'],a['branch_scope'])!=(b['entity_id'],b['snapshot_time_utc'],b['branch_scope']):raise ValueError('One unchanged owner, date and branch required')
    owner=a['entity_id'];stamp=a['snapshot_time_utc'];aid,bid=a['section_id'],b['section_id']
    allowed=[(x,y) for x,y in zip(CUTS[owner],CUTS[owner][1:])]
    if ((aid,cut_a),(bid,cut_b)) not in allowed:raise ValueError('Only declared neighboring cuts; never skip an unresolved cut')
    ga,gb=endpoint(a,cut_a),endpoint(b,cut_b)
    out={'id':owner+':'+stamp+':'+aid+':'+bid,'entity_id':owner,'snapshot_time_utc':stamp,'branch_scope':a['branch_scope'],'section_ids':[aid,bid],'source_case_pointers':[a['source_descriptor_pointer'],b['source_descriptor_pointer']],'source_lateral_gate_censoring':[a.get('lateral_gate_censored'),b.get('lateral_gate_censored')],'status':'UNRESOLVED_ENDPOINT_NO_DEPTH_SURFACE_SCENARIO','cells':[],'conditional_partial_component_volume_km3':None,'sampling_bracket_volume_scenarios_km3':None,'whole_segment_volume_established':False,'whole_current_depth_m':None,'physical_volume_km3':None,'physical_uncertainty_m':None,'annual_range_m':None,'physical_state_join_eligible':False,'global_total_eligible':False}
    if ga is None or gb is None:return out
    if ga['transverse_axis']!=gb['transverse_axis'] or len(ga['transverse_coordinates'])!=len(gb['transverse_coordinates']) or any(abs(x-y)>1e-8 for x,y in zip(ga['transverse_coordinates'],gb['transverse_coordinates'])):raise ValueError('Homologous unchanged native transverse coordinates required')
    # The cuts are at most2degrees longitude or1degree latitude apart. This is
    # a declared coarse interpolation scenario, not evidence of interior support.
    for i,(sa,sb) in enumerate(zip(a['strips'],b['strips'])):
        ac=[corners_for(a,i,p) for p in sa['patches']];bc=[corners_for(b,i,p) for p in sb['patches']]
        links=[(x,y) for x,ca in enumerate(ac) for y,cb in enumerate(bc) if native_overlap(ca+cb)]
        patches=[];rejected=[]
        for x,y in links:
            if sum(l==x for l,r in links)!=1 or sum(r==y for l,r in links)!=1:
                rejected.append({'left_section_patch_index':x,'right_section_patch_index':y,'reason':'AMBIGUOUS_BETWEEN_SECTION_SPLIT_OR_MERGE'});continue
            patch=integrate_corners(ac[x]+bc[y]);patch.update(left_section_patch_index=x,right_section_patch_index=y)
            patches.append(patch)
        out['cells'].append({'transverse_column_indices':[i,i+1],'status':'ASSUMED_BILINEAR_DEPTH_SURFACES' if patches else 'NO_COMMON_FINITE_FOUR_CORNER_SURFACE_UNKNOWN_NOT_ZERO','patches':patches,'rejected_links':rejected,'unmatched_left_section_patches':[x for x in range(len(ac)) if not any(l==x for l,r in links)],'unmatched_right_section_patches':[y for y in range(len(bc)) if not any(r==y for l,r in links)]})
    accepted=[p for c in out['cells'] for p in c['patches']]
    out['status']='PARTIAL_ASSUMED_DEPTH_SURFACE_SCENARIO' if accepted else 'NO_MATCHED_FOUR_CORNER_DEPTH_SURFACE_SCENARIO'
    if accepted:
        out['conditional_partial_component_volume_km3']=sum(p['conditional_partial_component_volume_km3'] for p in accepted)
        out['sampling_bracket_volume_scenarios_km3']=[sum(p['sampling_bracket_volume_scenarios_km3'][k] for p in accepted) for k in [0,1]]
    return out

def build(source,review):
    if source['schema']!='osw.barents-makassar-conditional-section-geometry.v1' or review['status']!='PASS_EIGHTEEN_PARTIAL_COMPONENT_SECTIONS_WITH_PAIRED_DEPTHS_AND_SAMPLING_SCENARIOS' or review['actual_complete_32_case_json_csv_roundtrip_passed'] is not True:raise ValueError('Exact validated paired geometry source required')
    cases=source['cases'];keys=[(c['entity_id'],c['snapshot_time_utc'],c['section_id']) for c in cases]
    expected={(o,t,s) for o,cuts in CUTS.items() for t in DATES for s,v in cuts}
    if len(keys)!=32 or len(set(keys))!=32 or set(keys)!=expected:raise ValueError('All32 original source cases required')
    indexed=dict(zip(keys,cases));rows=[]
    for owner,cuts in CUTS.items():
        for stamp in DATES:
            for (sa,va),(sb,vb) in zip(cuts,cuts[1:]):rows.append(segment(indexed[owner,stamp,sa],indexed[owner,stamp,sb],va,vb))
    patches=[p for r in rows for c in r['cells'] for p in c['patches']]
    if len(patches)*4>6000:raise ValueError('Bounded derived surface control nodes')
    counts={'source_cases':32,'source_unresolved_cases_preserved':sum(c['status']=='ORIGINAL_AXIS_UNRESOLVED_NO_SECTION_GEOMETRY' for c in cases),'declared_neighbor_segment_cases':len(rows),'segments_with_partial_depth_surface_scenarios':sum(r['conditional_partial_component_volume_km3'] is not None for r in rows),'segments_with_unresolved_endpoint':sum(r['status']=='UNRESOLVED_ENDPOINT_NO_DEPTH_SURFACE_SCENARIO' for r in rows),'conditional_depth_surface_patches':len(patches),'gap_cells':sum(not c['patches'] for r in rows for c in r['cells']),'rejected_between_section_ambiguity_links':sum(len(c['rejected_links']) for r in rows for c in r['cells']),'surface_control_corner_occurrences':4*len(patches),'new_provider_requests':0,'new_native_values_decoded':0,'new_observations':0,'whole_route_physical_depth_profiles':0,'physical_volume_estimates':0}
    if counts['source_unresolved_cases_preserved']!=14 or len(rows)!=24:raise ValueError('All declared gaps and adjacent segment slots preserved')
    return {'schema':'osw.barents-makassar-conditional-regional-depth-surfaces.v1','source_descriptor':{'file':SOURCE,'sha256':SOURCE_SHA},'counts':counts,'segments':rows,'surface_interpolation':'Upper and lower depth surfaces affine in longitude and latitude with a bilinear cross term over each matched rectangle. The unsampled interior is explicitly assumed, not measured or newly resolved by the model.','volume_operator':'Integrate bilinear thickness over spherical surface area,with analytic cos(latitude) weights;6371008.8m sphere and constant-surface-footprint vertical extrusion. No radial-shell correction. Convert m3 to km3.','sampling_scenarios':'Original corner crossing-bracket thickness scenarios propagated through the same positive integration weights;not physical uncertainty,confidence intervals,true-volume guarantees or seasonal extrema.','interpretation':'Partial signed-component regional reference-geometry scenarios at the source0.1m/s cutoff. Four-corner matches do not establish water-mass identity,an axis,interior topography or whole-current extent. Unknown cells remain gaps;no annual/current/global sum.','source_credit':source['source_credit'],'runtime_changed':False,'full_goal_complete':False}

def geojson(report):
    features=[]
    for row in report['segments']:
        for ci,cell in enumerate(row['cells']):
            for pi,p in enumerate(cell['patches']):
                features.append({'type':'Feature','id':row['id']+f':cell{ci}:patch{pi}','geometry':{'type':'Polygon','coordinates':[p['horizontal_polygon_lon_lat']]},'properties':{'entity_id':row['entity_id'],'snapshot_time_utc':row['snapshot_time_utc'],'segment_id':row['id'],'corner_order':'SW,SE,NE,NW','upper_depth_m':[c['upper_depth_m'] for c in p['corners_sw_se_ne_nw']],'lower_depth_m':[c['lower_depth_m'] for c in p['corners_sw_se_ne_nw']],'vertical_coordinate':'retained_provider_depth_m_positive_down_not_WGS84_altitude','geometry_role':'2D_footprint_of_assumed_bilinear_depth_surface','conditional_partial_component_volume_km3':p['conditional_partial_component_volume_km3'],'sampling_bracket_volume_scenarios_km3':p['sampling_bracket_volume_scenarios_km3'],'physical_volume_eligible':False}})
    return {'type':'FeatureCollection','features':features,'interpretation':'Coordinates are2Dlongitude/latitude only. Positive-down provider depths are properties,not GeoJSON ellipsoidal altitudes. These are assumed regional component surfaces,not measured current boundaries.','runtime_changed':False,'full_goal_complete':False}

def csv_bytes(rows):
    fields=['id','entity_id','snapshot_time_utc','section_ids','status','conditional_partial_component_volume_km3','sampling_bracket_volume_scenarios_km3','source_lateral_gate_censoring','whole_segment_volume_established','physical_volume_km3','annual_range_m','source_case_pointers']
    stream=io.StringIO(newline='');w=csv.DictWriter(stream,fieldnames=fields,lineterminator='\n');w.writeheader()
    for row in rows:w.writerow({k:json.dumps(row[k],separators=(',',':')) if isinstance(row[k],(list,dict,bool)) else '' if row[k] is None else row[k] for k in fields})
    return stream.getvalue().encode()

def main():
    start=float(os.environ['OSW_DEPTH_SURFACE_START'])
    def stop(*args):raise TimeoutError('Shared60second surface scenario deadline')
    signal.signal(signal.SIGALRM,stop);signal.signal(signal.SIGTERM,stop);elapsed=time.monotonic()-start
    if not 0<=elapsed<30:raise ValueError('Shared synthetic/producer clock required')
    signal.alarm(max(1,int(60-elapsed)));socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline descriptors only'))
    out=ROOT/'barents-makassar-depth-surfaces-v1';out.mkdir(exist_ok=False)
    def save(v):
        temp=out/'query-ledger.tmp';temp.write_bytes(encode(v));os.replace(temp,out/'catalog-query-ledger.json')
    query=DescriptorQuery(save,prior_numeric=0,prior_bytes=0);reader=query.reader(lambda p:(ROOT/p).read_bytes())
    try:
        with query.decoding():
            op=json.loads(reader(OP))
            for p,pin in op['input_sha256'].items():
                if sha((ROOT/p).read_bytes())!=pin:raise ValueError('Frozen source or operator changed:'+p)
            raw=reader(SOURCE)
            if sha(raw)!=SOURCE_SHA:raise ValueError('Exact reviewed section geometry bytes required')
            source=json.loads(raw);original=copy.deepcopy(source);report=build(source,json.loads(reader(REVIEW)))
            if source!=original:raise ValueError('Source descriptors changed')
            report['input_sha256']=op['input_sha256'];mapping=geojson(report);rr=encode(report);gr=encode(mapping);table=csv_bytes(report['segments'])
            if json.loads(rr)!=report or json.loads(gr)!=mapping or csv_bytes(json.loads(rr)['segments'])!=table or len(list(csv.DictReader(io.StringIO(table.decode()))))!=24:raise ValueError('Complete report/24-case CSV/GeoJSON roundtrip')
            if len(rr)+len(gr)+len(table)+(out/'catalog-query-ledger.json').stat().st_size>2400000:raise ValueError('Whole output cap')
            for name,data in [('depth-surfaces.json',rr),('depth-surfaces.geojson',gr),('segments.csv',table)]:(out/name).write_bytes(data)
            print(json.dumps({'counts':report['counts'],'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_unique_json_bytes':query.ledger['unique_json_bytes']}),flush=True)
    finally:signal.alarm(0)

if __name__=='__main__':main()
