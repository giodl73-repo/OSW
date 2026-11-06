"""Explicit hypothetical solids between admitted finite section patches."""
import copy,hashlib,json,math,os,signal,socket,time
from collections import Counter
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery
ROOT=Path(__file__).resolve().parents[1]
OP='research/north-brazil-reference-solids-operator-v1.json'
SOURCE='research/north-brazil-paired-depth-geometry-v1.json'
METHOD='research/north-brazil-depth-sections-operator-v1.json'
REVIEW='research/current-depth-north-brazil-paired-depth-geometry-source-review-v1.json'
RADIUS_M=6371008.8
DATES=['2022-01-15T00:00:00Z','2022-07-15T00:00:00Z']
finite=lambda x:type(x) in (int,float) and math.isfinite(x)
sha=lambda b:hashlib.sha256(b).hexdigest()
encode=lambda x:(json.dumps(x,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()

def possible_overlap(a,b):
    # Missing boundaries are unbounded only for conservative topology screening;
    # they never become a finite depth, thickness or volume.
    for r in [a,b]:
        for key in ['upper_depth_m','lower_depth_m']:
            if r[key] is not None and (not finite(r[key]) or r[key]<0):raise ValueError('Known depth is finite nonnegative')
        if r['upper_depth_m'] is not None and r['lower_depth_m'] is not None and r['upper_depth_m']>=r['lower_depth_m']:raise ValueError('Ordered known boundaries')
    return not ((a['lower_depth_m'] is not None and b['upper_depth_m'] is not None and a['lower_depth_m']<=b['upper_depth_m']) or (b['lower_depth_m'] is not None and a['upper_depth_m'] is not None and b['lower_depth_m']<=a['upper_depth_m']))

def links(left,right):
    candidates=[(i,j) for i,a in enumerate(left) for j,b in enumerate(right) if possible_overlap(a,b)]
    chosen={i:j for i,j in candidates if sum(x==i for x,y in candidates)==1 and sum(y==j for x,y in candidates)==1}
    values=[chosen[i] for i in sorted(chosen)]
    if any(a>=b for a,b in zip(values,values[1:])):raise ValueError('Ordered source bands cannot cross')
    return chosen

def check_run(run):
    upper,lower,thick=[run[k] for k in ['upper_depth_m','lower_depth_m','thickness_m']];bounds=run['sampling_thickness_bounds_m']
    if not all(finite(v) for v in [upper,lower,thick]) or not 0<=upper<lower or not math.isclose(lower-upper,thick,rel_tol=1e-10,abs_tol=1e-8):raise ValueError('Only finite original paired contours can form a solid')
    if not isinstance(bounds,list) or len(bounds)!=2 or not all(finite(v) for v in bounds) or not 0<=bounds[0]<=thick<=bounds[1]:raise ValueError('Original enclosing sampling thickness bracket')

def integrate(lon0,lon1,lat0,lat1,runs):
    if len(runs)!=4 or not all(finite(v) for v in [lon0,lon1,lat0,lat1]) or not -180<=lon0<lon1<=180 or not -90<lat0<lat1<90 or lon1-lon0>.1 or lat1-lat0>3.1:raise ValueError('Original narrow longitude cell and declared neighboring latitude interval only')
    for run in runs:check_run(run)
    area=RADIUS_M**2*math.radians(lon1-lon0)*(math.sin(math.radians(lat1))-math.sin(math.radians(lat0)))
    mean=sum(r['thickness_m'] for r in runs)/4
    volume=area*mean/1e9;bounds=[area*sum(r['sampling_thickness_bounds_m'][k] for r in runs)/4/1e9 for k in [0,1]]
    if not finite(volume) or not 0<=bounds[0]<=volume<=bounds[1]:raise ValueError('Finite spherical area times positive interpolated thickness')
    return {'horizontal_reference_cell_area_km2':area/1e6,'mean_reference_component_thickness_m':mean,
        'reference_solid_volume_km3':volume,'sampling_bracket_reference_volume_bounds_km3':bounds}

def face(row):
    if row['entity_id']!='current:north-brazil' or row['component_bearing_degrees_true']!=315 or row['velocity_threshold_m_s']!=.1 or row['snapshot_time_utc'] not in DATES:raise ValueError('Exact source owner/frame/cutoff/date')
    if row['whole_section_area_established'] is not False or row['physical_volume_eligible'] is not False or row['whole_route_depth_eligible'] is not False or row['named_current_axis_independently_validated'] is not False or row['physical_current_thickness_m'] is not None or row['volume_km3'] is not None:raise ValueError('Source physical/whole-route ineligibility must remain')
    cols=row['columns']
    if not cols:raise ValueError('All admitted fourteen NBC sections have retained columns')
    latitude=cols[0]['sampled_lon_lat'][1]
    if any(c['native_column_index']!=i or len(c['sampled_lon_lat'])!=2 or not all(finite(v) for v in c['sampled_lon_lat']) or abs(c['sampled_lon_lat'][1]-latitude)>1e-10 for i,c in enumerate(cols)):raise ValueError('Original fixed native latitude and ordered columns')
    if any(a['sampled_lon_lat'][0]>=b['sampled_lon_lat'][0] for a,b in zip(cols,cols[1:])):raise ValueError('Original increasing longitudes')
    for col in cols:
        for run in col['runs']:
            interval=run['native_depth_indices_inclusive']
            if len(interval)!=2 or any(type(v)!=int for v in interval) or not 0<=interval[0]<=interval[1]:raise ValueError('Original ordered native run index interval')
        for a,b in zip(col['runs'],col['runs'][1:]):
            if a['native_depth_indices_inclusive'][1]>=b['native_depth_indices_inclusive'][0] or (a['lower_depth_m'] is not None and b['upper_depth_m'] is not None and a['lower_depth_m']>b['upper_depth_m']):raise ValueError('Disjoint source vertical bands required')
    if len(row['strips'])!=len(cols)-1:raise ValueError('All original neighboring strips required')
    mapping={}
    for i,strip in enumerate(row['strips']):
        if strip['left_column_index']!=i or strip['right_column_index']!=i+1 or not 0<strip['distance_m']<=20000:raise ValueError('Original adjacent transverse strip within20km')
        a,b=cols[i:i+2];seen=set()
        for patch in strip['patches']:
            pair=patch['left_run_index'],patch['right_run_index']
            if pair in seen or not 0<=pair[0]<len(a['runs']) or not 0<=pair[1]<len(b['runs']):raise ValueError('Unique original finite face patches')
            seen.add(pair)
            for run in [a['runs'][pair[0]],b['runs'][pair[1]]]:check_run(run)
        if len({p[0] for p in seen})!=len(seen) or len({p[1] for p in seen})!=len(seen):raise ValueError('One-to-one admitted face patches only')
        mapping[(a['sampled_lon_lat'][0],b['sampled_lon_lat'][0])]=(i,strip)
    return latitude,mapping

def between(a,b,ai,bi):
    lat0,first=face(a);lat1,second=face(b)
    if lat0>=lat1 or a['snapshot_time_utc']!=b['snapshot_time_utc']:raise ValueError('Same instant and ordered adjacent declared sections')
    result={'south_section_id':a['section_id'],'north_section_id':b['section_id'],'snapshot_time_utc':a['snapshot_time_utc'],
        'source_case_indices':[ai,bi],'actual_native_latitude_degrees_north':[lat0,lat1],
        'reference_between_section_meridional_distance_km':RADIUS_M*math.radians(lat1-lat0)/1000,
        'cells':[],'unknown_reference_cells':[],'physical_water_volume_km3':None,'whole_current_volume_km3':None}
    for cell in sorted(set(first)|set(second)):
        missing={'longitude_cell_degrees_east':list(cell),'reference_volume_km3':None}
        if cell not in first or cell not in second:
            result['unknown_reference_cells'].append(dict(missing,reason='NO_EXACT_COMMON_NATIVE_LONGITUDE_FACE'));continue
        ia,sa=first[cell];ib,sb=second[cell];al,ar=a['columns'][ia:ia+2];bl,br=b['columns'][ib:ib+2]
        left=links(al['runs'],bl['runs']);right=links(ar['runs'],br['runs'])
        partner={(p['left_run_index'],p['right_run_index']):j for j,p in enumerate(sb['patches'])};used=set()
        for pi,patch in enumerate(sa['patches']):
            i,j=patch['left_run_index'],patch['right_run_index'];why=None
            if i not in left or j not in right:why='NO_UNIQUE_CROSS_SECTION_DEPTH_INTERVAL_LINK'
            elif (left[i],right[j]) not in partner:why='NO_ADMITTED_FINITE_PARTNER_FACE_PATCH'
            if why:
                result['unknown_reference_cells'].append(dict(missing,south_patch_index=pi,reason=why));continue
            pj=partner[(left[i],right[j])]
            if pj in used:raise ValueError('No duplicated north partner patch')
            used.add(pj);runs=[al['runs'][i],ar['runs'][j],bl['runs'][left[i]],br['runs'][right[j]]]
            values=integrate(*cell,lat0,lat1,runs)
            result['cells'].append({'longitude_cell_degrees_east':list(cell),'source_strip_indices':[ia,ib],'source_patch_indices':[pi,pj],
                'source_run_indices_southwest_southeast_northwest_northeast':[i,j,left[i],right[j]],
                'original_four_corner_runs':copy.deepcopy(runs),**values})
        for pj in range(len(sb['patches'])):
            if pj not in used:result['unknown_reference_cells'].append(dict(missing,north_patch_index=pj,reason='NORTH_FACE_PATCH_WITHOUT_ACCEPTED_SOLID'))
        if not sa['patches'] and not sb['patches']:result['unknown_reference_cells'].append(dict(missing,reason='NO_FINITE_PAIRED_FACE_PATCHES_UNKNOWN_NOT_ZERO'))
    result['counts']={'accepted_reference_solids':len(result['cells']),'unknown_or_rejected_reference_items':len(result['unknown_reference_cells'])}
    if result['cells']:
        result['partial_reference_solid_volume_km3']=sum(c['reference_solid_volume_km3'] for c in result['cells'])
        result['sampling_bracket_partial_reference_volume_bounds_km3']=[sum(c['sampling_bracket_reference_volume_bounds_km3'][k] for c in result['cells']) for k in [0,1]]
    else:result.update(partial_reference_solid_volume_km3=None,sampling_bracket_partial_reference_volume_bounds_km3=None)
    result['partial_reference_volume_is_bound_on_physical_current_volume']=False
    return result

def build(source,method,review):
    if source['schema']!='osw.north-brazil-paired-depth-geometry.v1' or source.get('runtime_changed') is not False or source.get('full_goal_complete') is not False or review['status']!='PASS_ALL14_PAIRED_COMPONENT_SECTIONS_AND_ORIGINAL_DEPTH_ANCHORS_RETAINED':raise ValueError('Exact admitted fourteen-case source only')
    if method['entity_id']!='current:north-brazil' or method['component_bearing_degrees_true']!=315 or method['primary_threshold_m_s']!=.1 or method['snapshot_times_utc']!=DATES or any(method['eligibility'].values()):raise ValueError('Original physical eligibility not promoted')
    definitions=sorted(method['sections'],key=lambda s:s['latitude_degrees_north']);rows=source['cases']
    expected={(s['id'],t) for s in definitions for t in DATES};lookup={(r['section_id'],r['snapshot_time_utc']):(i,r) for i,r in enumerate(rows)}
    if len(rows)!=14 or len(definitions)!=7 or len(lookup)!=14 or set(lookup)!=expected:raise ValueError('All fourteen original sections/dates, no subset or date join')
    for s in definitions:
        for t in DATES:
            _,row=lookup[s['id'],t];lat,_=face(row)
            if abs(lat-s['latitude_degrees_north'])*math.pi/180*RADIUS_M>3000:raise ValueError('Original target/native latitude tolerance')
    pairs=[]
    for t in DATES:
        for south,north in zip(definitions,definitions[1:]):
            ai,a=lookup[south['id'],t];bi,b=lookup[north['id'],t];pairs.append(between(a,b,ai,bi))
    by_date=[]
    for t in DATES:
        own=[p for p in pairs if p['snapshot_time_utc']==t];known=[p for p in own if p['partial_reference_solid_volume_km3'] is not None]
        by_date.append({'snapshot_time_utc':t,'partial_reference_solid_volume_km3':sum(p['partial_reference_solid_volume_km3'] for p in known) if known else None,
            'sampling_bracket_partial_reference_volume_bounds_km3':[sum(p['sampling_bracket_partial_reference_volume_bounds_km3'][k] for p in known) for k in [0,1]] if known else None,
            'accepted_reference_solid_count':sum(len(p['cells']) for p in own),'unknown_or_rejected_reference_item_count':sum(len(p['unknown_reference_cells']) for p in own),
            'whole_current_or_physical_volume_km3':None,'annual_extrema_established':False})
    return {'schema':'osw.north-brazil-reference-solids.v1','entity_id':'current:north-brazil',
        'counts':{'source_cases':len(rows),'declared_neighbor_section_date_pairs':len(pairs),'accepted_reference_solids':sum(len(p['cells']) for p in pairs),'unknown_or_rejected_reference_items':sum(len(p['unknown_reference_cells']) for p in pairs)},
        'by_date':by_date,'section_pairs':pairs,'source_paired_geometry':SOURCE,
        'reference_interpolation':'Bilinear upper/lower depth surfaces in longitude and sin(latitude) on a mean-radius6371008.8m sphere. Only exact common original longitude cells,admitted finite face patches and unique conservative cross-section interval links; no current-axis or flow-normal extrusion assumption.',
        'interpretation':'Hypothetical partial reference solids under newly declared between-section interpolation,not measured water volume or reconstructed physical current geometry. Endpoint support does not validate interior flow,land-free support,current identity or continuity. Missing/censored/ambiguous/unmatched cells stay unknown. The retained-solid sum is not a bound on whole-current water volume. Sampling-bracket scenarios are not physical uncertainty or annual ranges. Do not mix dates,branches,owners or add to overlapping historical scenarios/global totals.',
        'original_source_between_section_interpolation_performed':False,'reference_scenario_between_section_interpolation_performed':True,
        'original_physical_volume_ineligibility_preserved':True,'physical_volume_eligible':False,'whole_current_volume_km3':None,
        'source_credit':'HYCOM Consortium,NRL,COAPS-FSU; original section/source review retained.',
        'new_observations':0,'new_canonical_references':0,'runtime_changed':False,'full_goal_complete':False}

def main():
    start=float(os.environ['OSW_NBC_REFERENCE_SOLIDS_START'])
    def stop(*a):raise TimeoutError('Shared60second test/producer deadline')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stop)
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared synthetic-test/producer clock')
    signal.alarm(max(1,int(60-(time.monotonic()-start))));socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline admitted geometry query only'))
    out=ROOT/'north-brazil-reference-solids-v1';out.mkdir(exist_ok=False)
    def save(value):
        tmp=out/'query-ledger.tmp';tmp.write_bytes(encode(value));os.replace(tmp,out/'query-ledger.json')
    query=DescriptorQuery(save,prior_numeric=0,prior_bytes=0);reader=query.reader(lambda p:(ROOT/p).read_bytes())
    try:
        with query.decoding():
            op=json.loads(reader(OP))
            for path,pin in op['input_sha256'].items():
                if sha((ROOT/path).read_bytes())!=pin:raise ValueError('Frozen input changed:'+path)
            review=json.loads(reader(REVIEW));raw=reader(SOURCE);piece=review['outputs'][SOURCE]
            if len(raw)!=piece['bytes'] or sha(raw)!=piece['sha256']:raise ValueError('Exact reviewed source geometry bytes')
            source=json.loads(raw);before=copy.deepcopy(source);report=build(source,json.loads(reader(METHOD)),review)
            if source!=before:raise ValueError('Admitted source remains exact')
            report['source_geometry_sha256']=sha(raw);data=encode(report)
            if json.loads(data)!=report or encode(json.loads(data))!=data:raise ValueError('Full actual reference geometry JSON roundtrip')
        total=len(data)+(out/'query-ledger.json').stat().st_size
        if total>2400000:raise ValueError('Whole output cap')
        (out/'reference-solids.json').write_bytes(data)
        print(json.dumps({'counts':report['counts'],'by_date':report['by_date'],'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_bytes':query.ledger['unique_json_bytes'],'whole_output_bytes':total,'cumulative_active_seconds':time.monotonic()-start,'physical_volume_eligible':False,'full_goal_complete':False}))
    finally:signal.alarm(0)

if __name__=='__main__':main()
