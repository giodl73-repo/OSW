"""Conditional strip geometry from retained depth descriptors; no native fields."""
import copy,csv,hashlib,io,json,math,os,signal,socket,time
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery

ROOT=Path(__file__).resolve().parents[1]
OP='research/north-brazil-paired-depth-geometry-operator-v1.json'
SOURCE='research/north-brazil-north-brazil-velocity-depth-curtains-v1.json'
SOURCE_SHA='9a2d47bfba05092d5815ae3285df56f19313aa4690b4f4dc091bdf4b6bc8ef8a'
REVIEW='research/current-depth-north-brazil-north-brazil-velocity-curtains-source-review-v1.json'
METHOD='research/north-brazil-depth-sections-operator-v1.json'
DATES=['2022-01-15T00:00:00Z','2022-07-15T00:00:00Z']
OWNERS={'current:north-brazil':315}

def finite(x):return type(x) in (int,float) and math.isfinite(x)
def encode(x):return (json.dumps(x,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()

def boundary(layer,side):
    value=layer.get(side+'_depth_m');status=layer[side+'_status']
    if status=='surface_bounded_layer' and side=='upper':
        if value!=0:raise ValueError('Surface-bounded top must be zero')
        return [0.,0.]
    if status!='adjacent_isotach_crossing':return None
    bracket=layer[side+'_bracket_m']
    if not finite(value) or len(bracket)!=2 or not all(finite(v) for v in bracket) or not 0<=bracket[0]<=value<=bracket[1] or bracket[0]>=bracket[1]:raise ValueError('Finite original crossing inside its original sampling bracket required')
    return bracket

def run_geometry(run,z):
    indices=run['native_depth_indices_inclusive'];layer=run['threshold_layer']
    if len(indices)!=2 or not all(type(i)==int for i in indices) or not 0<=indices[0]<=indices[1]<len(z) or layer['threshold_m_s']!=.1:raise ValueError('Original native run and primary cutoff required')
    up=boundary(layer,'upper');down=boundary(layer,'lower')
    result={'native_depth_indices_inclusive':copy.deepcopy(indices),'contains_original_core':run['contains_original_core'],'upper_status':layer['upper_status'],'lower_status':layer['lower_status'],'upper_depth_m':layer.get('upper_depth_m'),'lower_depth_m':layer.get('lower_depth_m'),'thickness_m':None,'sampling_thickness_bounds_m':None,'status':'CENSORED_BOUNDARY_NO_FINITE_THICKNESS'}
    if up is None or down is None:
        if layer.get('layer_thickness_m') is not None:raise ValueError('A censored boundary cannot supply finite thickness')
        return result
    upper=layer['upper_depth_m'];lower=layer['lower_depth_m'];thickness=lower-upper
    if not 0<=upper<=z[indices[0]]<=z[indices[1]]<=lower or thickness<=0 or not finite(layer['layer_thickness_m']) or not math.isclose(thickness,layer['layer_thickness_m'],abs_tol=1e-8):raise ValueError('Exact paired top/bottom thickness and native support required')
    result.update(thickness_m=thickness,sampling_thickness_bounds_m=[max(0.,down[0]-up[1]),down[1]-up[0]],status='FINITE_PAIRED_COMPONENT_CONTOURS')
    return result

def separation(a,b):
    if any(len(p)!=2 or not all(finite(v) for v in p) or not -180<=p[0]<=180 or not -90<=p[1]<=90 for p in [a,b]):raise ValueError('Finite geographic coordinates required')
    lon1,lat1,lon2,lat2=map(math.radians,[*a,*b]);q=math.sin((lat2-lat1)/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    distance=2*6371008.8*math.asin(math.sqrt(min(1.,max(0.,q))))
    if not 0<distance<=20000:raise ValueError('Only consecutive original neighboring columns within20km')
    return distance

def strip(left,right):
    distance=separation(left['sampled_lon_lat'],right['sampled_lon_lat']);ls=left['runs'];rs=right['runs']
    links=[(i,j) for i,a in enumerate(ls) for j,b in enumerate(rs) if max(a['native_depth_indices_inclusive'][0],b['native_depth_indices_inclusive'][0])<=min(a['native_depth_indices_inclusive'][1],b['native_depth_indices_inclusive'][1])]
    patches=[];rejected=[]
    for i,j in links:
        if sum(x==i for x,y in links)!=1 or sum(y==j for x,y in links)!=1:
            rejected.append({'left_run_index':i,'right_run_index':j,'reason':'AMBIGUOUS_VERTICAL_SPLIT_OR_MERGE'});continue
        a,b=ls[i],rs[j]
        if any(r['thickness_m'] is None for r in [a,b]):
            rejected.append({'left_run_index':i,'right_run_index':j,'reason':'CENSORED_TOP_OR_BOTTOM'});continue
        area=distance*(a['thickness_m']+b['thickness_m'])/2
        bounds=[distance*(a['sampling_thickness_bounds_m'][k]+b['sampling_thickness_bounds_m'][k])/2 for k in [0,1]]
        if not bounds[0]<=area<=bounds[1]:raise ValueError('Interpolated area must stay within sampling-bracket scenarios')
        patches.append({'left_run_index':i,'right_run_index':j,'linear_contour_strip_area_km2':area/1e6,'sampling_bracket_strip_area_bounds_km2':[v/1e6 for v in bounds]})
    return {'left_column_index':left['native_column_index'],'right_column_index':right['native_column_index'],'distance_m':distance,'patches':patches,'rejected_links':rejected,'unmatched_left_runs':[i for i in range(len(ls)) if not any(x==i for x,y in links)],'unmatched_right_runs':[j for j in range(len(rs)) if not any(y==j for x,y in links)],'status':'CONDITIONAL_PARTIAL_STRIP_GEOMETRY' if patches else 'NO_INTEGRABLE_PAIRED_CONTOURS_UNKNOWN_NOT_ZERO'}

def derive_case(case,pointer,branch_scope):
    owner=case['entity_id']
    if owner not in OWNERS or case['component_bearing_degrees_true']!=OWNERS[owner] or case['velocity_threshold_m_s']!=.1 or case['snapshot_time_utc'] not in DATES:raise ValueError('Original branch/date/frame/cutoff required')
    if case['core_reselected'] is not False or case['named_current_axis_independently_validated'] is not False or case['water_mass_classification_performed'] is not False:raise ValueError('No identity or selection promotion')
    out={k:copy.deepcopy(case[k]) for k in ['entity_id','section_id','snapshot_time_utc','source_file','source_sha256','source_geometry','component_bearing_degrees_true','original_horizontal_selection_status','original_selected_column_index','native_input_column_count']}
    out.update(source_descriptor_pointer=pointer,branch_scope=branch_scope,velocity_threshold_m_s=.1,status='ORIGINAL_AXIS_UNRESOLVED_NO_SECTION_GEOMETRY',columns=[],strips=[],conditional_partial_area_km2=None,sampling_bracket_partial_area_bounds_km2=None,integrated_strip_span_m=None,equivalent_paired_component_thickness_m=None,physical_cross_section_area_km2=None,physical_current_thickness_m=None,volume_km3=None,whole_section_area_established=False,annual_extrema_established=False,physical_uncertainty_m=None,named_current_axis_independently_validated=False,whole_route_depth_eligible=False,physical_volume_eligible=False)
    if case['status']=='ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':
        if case['columns']:raise ValueError('Unresolved case must not acquire substitute columns')
        return out
    if case['status']!='REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN':raise ValueError('Unsupported retained curtain status')
    z=case['depth_levels_m']
    if not 2<=len(z)<=40 or not all(finite(v) and v>=0 for v in z) or any(b<=a for a,b in zip(z,z[1:])):raise ValueError('Original ascending descriptor depth coordinates')
    cols=case['columns']
    if not 3<=len(cols)<=150 or len(cols)!=case['native_input_column_count'] or [c['native_column_index'] for c in cols]!=list(range(len(cols))):raise ValueError('Every original ordered native column required')
    for c in cols:
        runs=[run_geometry(r,z) for r in c['connected_depth_runs']]
        if any(a['native_depth_indices_inclusive'][1]>=b['native_depth_indices_inclusive'][0] for a,b in zip(runs,runs[1:])):raise ValueError('Separate non-overlapping vertical runs required')
        out['columns'].append({'native_column_index':c['native_column_index'],'sampled_lon_lat':copy.deepcopy(c['sampled_lon_lat']),'runs':runs,'status':c['status']})
    for a,b in zip(cols,cols[1:]):
        fixed,varying=1,0
        if abs(a['sampled_lon_lat'][fixed]-b['sampled_lon_lat'][fixed])>1e-8 or b['sampled_lon_lat'][varying]<=a['sampled_lon_lat'][varying] or b['global_longitude_index']-a['global_longitude_index']!=(0 if fixed==0 else 1) or b['global_latitude_index']-a['global_latitude_index']!=(1 if fixed==0 else 0):raise ValueError('Unchanged transverse axis and consecutive native indices required')
    out['strips']=[strip(a,b) for a,b in zip(out['columns'],out['columns'][1:])]
    supported=[s for s in out['strips'] if s['patches']]
    out.update(status='CONDITIONAL_PARTIAL_COMPONENT_SECTION_GEOMETRY',lateral_gate_censored=case['lateral_gate_censored'])
    if supported:
        area=sum(p['linear_contour_strip_area_km2'] for s in supported for p in s['patches']);span=sum(s['distance_m'] for s in supported)
        out.update(conditional_partial_area_km2=area,sampling_bracket_partial_area_bounds_km2=[sum(p['sampling_bracket_strip_area_bounds_km2'][k] for s in supported for p in s['patches']) for k in [0,1]],integrated_strip_span_m=span,equivalent_paired_component_thickness_m=area*1e6/span)
    return out

def build(source,review,method):
    if method['entity_id']!='current:north-brazil' or method['component_bearing_degrees_true']!=315 or method['primary_threshold_m_s']!=.1 or method['snapshot_times_utc']!=DATES or any(method['eligibility'].values()):raise ValueError('Unchanged original NBC method and no eligibility promotion')
    if source['schema']!='osw.north-brazil-velocity-depth-curtains.v1' or source['status']!='REGIONAL_MODEL_COMPONENT_THRESHOLD_GEOMETRY_NOT_PHYSICAL_CURRENT_BOTTOM' or review['status']!='ORIGINAL_SOURCE_PRIMARY_CURRENT_BATCH_RETAINED':raise ValueError('Exact already-reviewed source cohort required')
    cases=source['cases'];expected={('current:north-brazil',s['id'],t) for s in method['sections'] for t in DATES}
    actual=[(c['entity_id'],c['section_id'],c['snapshot_time_utc']) for c in cases]
    if len(cases)!=14 or len(set(actual))!=14 or set(actual)!=expected:raise ValueError('All14 original NBC cases required; no dropped dates or sections')
    definitions={v['id']:v for v in method['sections']}
    for c in cases:
        target=definitions[c['section_id']]['latitude_degrees_north']
        if any(abs(col['sampled_lon_lat'][1]-target)*math.pi/180*6371008.8>3000 for col in c['columns']):raise ValueError('Original3km fixed-latitude tolerance')
    rows=[derive_case(c,'/cases/'+str(i),method['branch_scope']) for i,c in enumerate(cases)]
    for row,original in zip(rows,cases):
        row['original_primary_layer']=copy.deepcopy(original['original_primary_layer'])
        row['section_orientation']='fixed_latitude_not_flow_normal'
        selected=row['original_selected_column_index']
        if type(selected)!=int or not 0<=selected<len(row['columns']):raise ValueError('Original selected column retained')
        column=row['columns'][selected]
        core_runs=[r for r in column['runs'] if r['contains_original_core']]
        if len(core_runs)!=1:raise ValueError('Exactly one original-core-containing run required')
        primary=original['original_primary_layer'];anchor=core_runs[0]
        for key in ['upper_status','lower_status','upper_depth_m','lower_depth_m']:
            if anchor[key]!=primary[key]:raise ValueError('Original selected primary boundaries must remain exact')
        if anchor['thickness_m']!=primary['layer_thickness_m']:raise ValueError('Original primary thickness/censor must remain exact')
        row['original_axis_proxy_depth_anchor']={'sampled_lon_lat':copy.deepcopy(column['sampled_lon_lat']),'native_column_index':selected,'paired_component_run':copy.deepcopy(core_runs[0]),'independent_current_axis_validated':False,'physical_current_depth_m':None,'whole_route_interpolation_allowed':False}
    counts={'source_cases':len(rows),'original_unresolved_cases':sum(r['status']=='ORIGINAL_AXIS_UNRESOLVED_NO_SECTION_GEOMETRY' for r in rows),'cases_with_integrable_partial_geometry':sum(r['conditional_partial_area_km2'] is not None for r in rows),'retained_column_descriptors':sum(len(r['columns']) for r in rows),'finite_paired_column_runs':sum(p['thickness_m'] is not None for r in rows for c in r['columns'] for p in c['runs']),'conditional_strip_patches':sum(len(s['patches']) for r in rows for s in r['strips']),'strips_without_integrable_geometry':sum(not s['patches'] for r in rows for s in r['strips']),'rejected_ambiguous_links':sum(p['reason']=='AMBIGUOUS_VERTICAL_SPLIT_OR_MERGE' for r in rows for s in r['strips'] for p in s['rejected_links']),'new_provider_requests':0,'new_native_values_decoded':0,'whole_route_physical_depth_profiles':0,'physical_volume_estimates':0}
    if counts['original_unresolved_cases']!=0:raise ValueError('All original14 supported cases must retain their source status')
    return {'schema':'osw.north-brazil-paired-depth-geometry.v1','source_descriptor':{'file':SOURCE,'sha256':SOURCE_SHA},'counts':counts,'cases':rows,'method':'Linear upper/lower contours only between consecutive native columns with unique one-to-one overlapping native depth runs and finite paired boundaries; geodesic strip lengths on mean-radius sphere6371008.8m. No lateral endpoint closure or split/merge interpolation.','range_interpretation':'Sampling-bracket geometry scenarios under the same linear-contour assumption; not statistical confidence, physical uncertainty, annual envelope or guaranteed true-area bounds.','axis_anchor_interpretation':'Fourteen discrete original model-axis-proxy component depth anchors, not an independently validated continuous named-current path. No between-section interpolation, depth averaging across dates, annual envelope or volume.', 'interpretation':'Partial model signed-component section geometry at the original0.1m/s cutoff, not physical current area/width/thickness or a whole-section area. Missing and ambiguous patches remain gaps. Areas from different sections/dates/owners must not be summed into water volume.','source_credit':'HYCOM Consortium,NRL,COAPS-FSU; original source attributes and review retained.','runtime_changed':False,'full_goal_complete':False}

def csv_bytes(rows):
    fields=['entity_id','section_id','snapshot_time_utc','status','original_axis_proxy_depth_anchor','original_primary_layer','conditional_partial_area_km2','sampling_bracket_partial_area_bounds_km2','integrated_strip_span_m','equivalent_paired_component_thickness_m','lateral_gate_censored','whole_section_area_established','physical_current_thickness_m','volume_km3','source_descriptor_pointer']
    stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=fields,lineterminator='\n');writer.writeheader()
    for row in rows:writer.writerow({k:json.dumps(row.get(k),ensure_ascii=False,separators=(',',':')) if isinstance(row.get(k),(dict,list,bool)) else '' if row.get(k) is None else row[k] for k in fields})
    return stream.getvalue().encode()

def main():
    start=float(os.environ['OSW_NBC_PAIRED_DEPTH_START'])
    def stop(*a):raise TimeoutError('Shared60second descriptor geometry deadline')
    signal.signal(signal.SIGALRM,stop);signal.signal(signal.SIGTERM,stop);elapsed=time.monotonic()-start
    if not 0<=elapsed<30:raise ValueError('One shared synthetic-test/producer clock required')
    signal.alarm(max(1,int(60-elapsed)));socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline descriptors only'))
    out=ROOT/'north-brazil-paired-depth-geometry-v1';out.mkdir(exist_ok=False)
    def save(v):
        tmp=out/'query-ledger.tmp';tmp.write_bytes(encode(v));os.replace(tmp,out/'catalog-query-ledger.json')
    query=DescriptorQuery(save,prior_numeric=0,prior_bytes=0);reader=query.reader(lambda p:(ROOT/p).read_bytes())
    try:
        with query.decoding():
            op=json.loads(reader(OP))
            for path,pin in op['input_sha256'].items():
                if sha((ROOT/path).read_bytes())!=pin:raise ValueError('Frozen descriptor input changed:'+path)
            raw=reader(SOURCE)
            if sha(raw)!=SOURCE_SHA:raise ValueError('Exact reviewed curtain bytes required')
            source=json.loads(raw);before=copy.deepcopy(source);report=build(source,json.loads(reader(REVIEW)),json.loads(reader(METHOD)))
            if source!=before:raise ValueError('Source descriptors must remain exact')
            report['input_sha256']=op['input_sha256'];rr=encode(report);table=csv_bytes(report['cases'])
            restored=json.loads(rr)
            if restored!=report or len(list(csv.DictReader(io.StringIO(table.decode()))))!=14 or csv_bytes(restored['cases'])!=table:raise ValueError('Complete report/CSV roundtrip')
            if len(rr)+len(table)+(out/'catalog-query-ledger.json').stat().st_size>2400000:raise ValueError('Whole output cap')
            (out/'section-geometry.json').write_bytes(rr);(out/'sections.csv').write_bytes(table)
            print(json.dumps({'counts':report['counts'],'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_unique_json_bytes':query.ledger['unique_json_bytes']}),flush=True)
    finally:signal.alarm(0)

if __name__=='__main__':main()
