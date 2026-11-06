"""Four-current paired component depth shapes from compiled descriptors only."""
import copy,csv,hashlib,io,json,math,os,signal,socket,time
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery
ROOT=Path(__file__).resolve().parents[1]
OP='research/boundary-subsurface-paired-depth-operator-v1.json'
PRIOR_NUMERIC=0
PRIOR_BYTES=0
PRIOR_ACTIVE_SECONDS_UPPER=0
RUN_NOTE='Inclusive component-thickness lower support under original contiguous piecewise-linear model definition; single-level zero is an uninformative bound, not absence.'
SOURCE='research/boundary-subsurface-velocity-depth-curtains-v1.json'
SOURCE_SHA='6683eb7d8530f865da5e61f9d3ef70f15a2b81b0a034b304c18c1d1bcaf0ef5b'
REVIEW='research/current-depth-boundary-subsurface-velocity-curtains-source-review-v1.json'
METHODS=['research/mauritania-baffin-interval-depth-sections-operator-v1.json','research/northern-interval-depth-sections-operator-v1.json']
QUARTERS=['2022-03-15T00:00:00Z','2022-06-15T00:00:00Z','2022-09-15T00:00:00Z','2022-12-15T00:00:00Z']
SEMI=['2022-01-15T00:00:00Z','2022-07-15T00:00:00Z']
DATES=QUARTERS+SEMI
OWNERS={'current:mauritanian':0,'current:baffin':180,'current:pacific-north-subsurface-countercurrent':90,'current:atlantic-north-equatorial-undercurrent':90}
AXES={'current:mauritanian':'latitude','current:baffin':'latitude','current:pacific-north-subsurface-countercurrent':'longitude','current:atlantic-north-equatorial-undercurrent':'longitude'}
OWNER_DATES={'current:mauritanian':QUARTERS,'current:baffin':QUARTERS,'current:pacific-north-subsurface-countercurrent':SEMI,'current:atlantic-north-equatorial-undercurrent':SEMI}
WINDOWS={'current:mauritanian':[50,300],'current:baffin':[100,300],'current:pacific-north-subsurface-countercurrent':[100,400],'current:atlantic-north-equatorial-undercurrent':[100,400]}
THRESHOLDS={o:(.05 if o=='current:baffin' else .1) for o in OWNERS}
OWNER_CASES={'current:mauritanian':20,'current:baffin':20,'current:pacific-north-subsurface-countercurrent':10,'current:atlantic-north-equatorial-undercurrent':10}

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

def run_geometry(run,z,threshold=.1):
    indices=run['native_depth_indices_inclusive'];layer=run['threshold_layer']
    if len(indices)!=2 or not all(type(i)==int for i in indices) or not 0<=indices[0]<=indices[1]<len(z) or layer['threshold_m_s']!=threshold or not finite(threshold) or threshold<=0:raise ValueError('Original native run and primary cutoff required')
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


def run_support(run,z,threshold=.1):
    if not 2<=len(z)<=40 or not all(finite(v) and v>=0 for v in z) or any(b<=a for a,b in zip(z,z[1:])):raise ValueError('Ascending finite original descriptor depths required')
    out=run_geometry(run,z,threshold);first,last=out['native_depth_indices_inclusive']
    span=z[last]-z[first]
    if out['thickness_m'] is not None and span>out['thickness_m']+1e-8:raise ValueError('Native-supported interval must fit paired component contours')
    out.update(native_supported_depth_interval_m=[z[first],z[last]],native_supported_minimum_component_span_m=span,minimum_span_interpretation='Inclusive component-thickness lower support under original contiguous piecewise-linear model definition; single-level zero is an uninformative bound, not absence.',minimum_span_is_physical_current_bound=False)
    return out

def attach_anchor(row,original):
    row['original_primary_layer']=copy.deepcopy(original['original_primary_layer'])
    row['section_orientation']='fixed_'+AXES[row['entity_id']]+'_not_independently_flow_normal'
    row['original_axis_proxy_depth_anchor']=None
    if row['status']=='ORIGINAL_AXIS_UNRESOLVED_NO_SECTION_GEOMETRY':return
    selected=row['original_selected_column_index']
    if type(selected)!=int or not 0<=selected<len(row['columns']):raise ValueError('Original selected native column required')
    col=row['columns'][selected];runs=[r for r in col['runs'] if r['contains_original_core']]
    if len(runs)!=1:raise ValueError('Exactly one original core-containing run required')
    anchor=runs[0];primary=original['original_primary_layer']
    for key in ['upper_status','lower_status','upper_depth_m','lower_depth_m']:
        if anchor[key]!=primary[key]:raise ValueError('Original primary boundary/status must remain exact')
    if anchor['thickness_m']!=primary['layer_thickness_m']:raise ValueError('Original finite primary thickness or censor must remain exact')
    row['original_axis_proxy_depth_anchor']={'sampled_lon_lat':copy.deepcopy(col['sampled_lon_lat']),'native_column_index':selected,'paired_component_run':copy.deepcopy(anchor),'independent_current_axis_validated':False,'physical_current_depth_m':None,'whole_route_interpolation_allowed':False}

def counts(rows):
    runs=[p for r in rows for c in r['columns'] for p in c['runs']]
    anchors=[r['original_axis_proxy_depth_anchor'] for r in rows if r['original_axis_proxy_depth_anchor'] is not None]
    return {'source_cases':len(rows),'original_unresolved_cases':sum(r['status']=='ORIGINAL_AXIS_UNRESOLVED_NO_SECTION_GEOMETRY' for r in rows),'cases_with_integrable_partial_geometry':sum(r['conditional_partial_area_km2'] is not None for r in rows),'retained_column_descriptors':sum(len(r['columns']) for r in rows),'retained_vertical_runs':len(runs),'finite_paired_column_runs':sum(p['thickness_m'] is not None for p in runs),'censored_runs_with_minimum_support':sum(p['thickness_m'] is None for p in runs),'conditional_strip_patches':sum(len(s['patches']) for r in rows for s in r['strips']),'strips_without_integrable_geometry':sum(not s['patches'] for r in rows for s in r['strips']),'rejected_ambiguous_links':sum(p['reason']=='AMBIGUOUS_VERTICAL_SPLIT_OR_MERGE' for r in rows for s in r['strips'] for p in s['rejected_links']),'original_axis_proxy_anchors':len(anchors),'finite_paired_axis_anchors':sum(a['paired_component_run']['thickness_m'] is not None for a in anchors),'censored_axis_anchors_with_minimum_support':sum(a['paired_component_run']['thickness_m'] is None for a in anchors),'new_provider_requests':0,'new_native_values_decoded':0,'whole_route_physical_depth_profiles':0,'physical_volume_estimates':0}

def effective_window(method,config,key):
    if key in config:return copy.deepcopy(config[key]),'original_owner_override'
    if key not in method:raise ValueError('No invented default depth window')
    return copy.deepcopy(method[key]),'original_explicit_method_default'

def build(source,review,methods):
    if source['schema']!='osw.boundary-subsurface-velocity-depth-curtains.v1' or source['status']!='REGIONAL_MODEL_COMPONENT_THRESHOLD_GEOMETRY_NOT_PHYSICAL_CURRENT_BOTTOM' or review['status']!='ALL60_ORIGINAL_CASES_PRESERVED_41_REGIONAL_CURTAINS_19_EXPLICIT_UNRESOLVED':raise ValueError('Exact original60case cohort required')
    groups=[{'current:mauritanian','current:baffin'},{'current:pacific-north-subsurface-countercurrent','current:atlantic-north-equatorial-undercurrent'}]
    if len(methods)!=2 or any(set(m['currents'])!=owners for m,owners in zip(methods,groups)):raise ValueError('Original two distinct owner/operator cohorts required')
    configs={};definitions={};expected=set();rules={}
    for mi,method in enumerate(methods):
        if method['snapshot_times_utc']!=(QUARTERS if mi==0 else SEMI) or any(method['eligibility'].values()):raise ValueError('Original mixed temporal support;no physical promotion')
        for owner,config in method['currents'].items():
            core,core_origin=effective_window(method,config,'core_search_depth_interval_m');window,window_origin=effective_window(method,config,'selection_depth_interval_m')
            if config['entity_id']!=owner or config['component_bearing_degrees_true']!=OWNERS[owner] or config['primary_threshold_m_s']!=THRESHOLDS[owner] or config['surface_component_gate_m_s'] is not None or config['temperature_gate'] is not None or core!=WINDOWS[owner] or window!=WINDOWS[owner]:raise ValueError('Original direction,cutoff,no surface gate and explicit selection stratum')
            configs[owner]=config;rules[owner]={'core':core,'window':window,'core_origin':core_origin,'window_origin':window_origin,'file':METHODS[mi]}
        for definition in method['sections']:
            owner=definition['entity_id'];key=(owner,definition['id'])
            if owner not in method['currents'] or key in definitions or definition['fixed_axis']!=AXES[owner] or method['maximum_nearest_'+AXES[owner]+'_distance_km']!=5:raise ValueError('Original axes,unique cuts and5km tolerance')
            definitions[key]=definition;expected.update((*key,t) for t in OWNER_DATES[owner])
    cases=source['cases'];keys=[(c['entity_id'],c['section_id'],c['snapshot_time_utc']) for c in cases]
    if len(cases)!=60 or len(set(keys))!=60 or set(keys)!=expected:raise ValueError('All60original unique owner-date cases required')
    rows=[]
    for i,c in enumerate(cases):
        owner=c['entity_id'];axis=AXES[owner];definition=definitions[owner,c['section_id']];rule=rules[owner]
        if c['source_geometry']!=axis or c['source_operator']!=rule['file']:raise ValueError('Original cohort geometry tag and rule operator required')
        for col in c['columns']:
            lon,lat=col['sampled_lon_lat'];delta=abs(lat-definition['latitude_degrees_north']) if axis=='latitude' else abs(lon-definition['longitude_degrees_east'])*math.cos(math.radians(lat))
            if delta*math.pi/180*6371008.8>5000:raise ValueError('Original5km fixed-axis tolerance')
        row=derive_case(c,'/cases/'+str(i),configs[owner]['branch_scope']);attach_anchor(row,c);config=configs[owner]
        row['section_fixed_axis']=axis;row['source_rule_operator_file']=rule['file']
        row['source_core_search_depth_interval_m']=copy.deepcopy(rule['core']);row['source_selection_depth_interval_m']=copy.deepcopy(rule['window'])
        row['source_core_search_window_origin']=rule['core_origin'];row['source_selection_window_origin']=rule['window_origin']
        row['source_identity_context']={k:copy.deepcopy(config[k]) for k in ['parent_current_id','identity_relationship','parent_depth_values_inherited','identity_evidence_basis','selection_window_basis'] if k in config}
        row['surface_gate_policy']='not_applied_in_original_method';rows.append(row)
    by_owner={o:counts([r for r in rows if r['entity_id']==o]) for o in OWNERS};total=counts(rows)
    if any(by_owner[o]['source_cases']!=OWNER_CASES[o] for o in OWNERS) or total['original_unresolved_cases']!=19 or total['original_axis_proxy_anchors']!=41:raise ValueError('All original41supported cases and19axis gaps retained')
    return {'schema':'osw.boundary-subsurface-paired-depth.v1','source_descriptor':{'file':SOURCE,'sha256':SOURCE_SHA},'counts':total,'counts_by_current':by_owner,'counts_by_primary_threshold_m_s':{str(t):counts([r for r in rows if r['velocity_threshold_m_s']==t]) for t in [.05,.1]},'cases':rows,'source_selection_windows_m':copy.deepcopy(WINDOWS),'source_dates_by_current':copy.deepcopy(OWNER_DATES),'fixed_axes_by_current':copy.deepcopy(AXES),'temporal_scope':'Preserve original four March/June/September/December2022snapshots for Mauritanian/Baffin and two January/July2022snapshots for northern undercurrents. No padding,temporal averaging or annual extrema.','method':'Finite paired component contours and unique linear transverse strips,with native first-to-last minimum support for censored boundaries. Original core windows select original cores without imposing layer limits or detachment.','layer_metric_interpretation':'Lower component depth is absolute positive model depth;paired component thickness is lower minus upper,not lower depth. A subsurface search stratum does not force a detached physical layer or cap its depth.','minimum_span_interpretation':'Conditional native minimum support under original contiguous piecewise-linear signed-component definition,not a physical named-current thickness bound. Single-level zero is uninformative,not absence.','range_interpretation':'Native-bracket conditional geometry scenarios,not physical uncertainty,confidence intervals or annual envelopes.','axis_anchor_interpretation':'Original model-selected axes only;19unresolved cases retain null anchors and original candidate diagnoses. No replacement core,date,gate,branch,source stratum or between-section interpolation.','interpretation':'Partial regional component geometry,not independently identified current body,water mass,flow-normal width,whole-route depth or physical water volume. No independent terrain clearance.','source_credit':'HYCOM Consortium,NRL,COAPS-FSU; original source fields and qualifiers retained.','runtime_changed':False,'full_goal_complete':False}


def anchor_csv(rows):
    fields=['entity_id','section_id','snapshot_time_utc','status','component_bearing_degrees_true','velocity_threshold_m_s','section_fixed_axis','surface_gate_policy','source_selection_depth_interval_m','source_selection_window_origin','source_rule_operator_file','source_parent_current_id','source_parent_depth_values_inherited','source_identity_relationship','longitude_degrees_east','latitude_degrees_north','upper_component_depth_m','lower_component_depth_m','paired_component_thickness_m','native_supported_minimum_component_span_m','shallowest_supported_component_sample_m','deepest_supported_component_sample_m','upper_boundary_status','lower_boundary_status','original_selected_column_index','source_descriptor_pointer']
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');writer.writeheader()
    for row in rows:
        d={k:row[k] for k in ['entity_id','section_id','snapshot_time_utc','status','component_bearing_degrees_true','velocity_threshold_m_s','section_fixed_axis','original_selected_column_index','source_descriptor_pointer']}
        d.update(surface_gate_policy=row['surface_gate_policy'],source_selection_depth_interval_m=row['source_selection_depth_interval_m'],source_selection_window_origin=row['source_selection_window_origin'],source_rule_operator_file=row['source_rule_operator_file'],source_parent_current_id=row['source_identity_context'].get('parent_current_id'),source_parent_depth_values_inherited=row['source_identity_context'].get('parent_depth_values_inherited'),source_identity_relationship=row['source_identity_context'].get('identity_relationship'))
        a=row['original_axis_proxy_depth_anchor']
        if a is not None:
            p=a['paired_component_run'];lo,hi=p['native_supported_depth_interval_m']
            d.update(longitude_degrees_east=a['sampled_lon_lat'][0],latitude_degrees_north=a['sampled_lon_lat'][1],upper_component_depth_m=p['upper_depth_m'],lower_component_depth_m=p['lower_depth_m'],paired_component_thickness_m=p['thickness_m'],native_supported_minimum_component_span_m=p['native_supported_minimum_component_span_m'],shallowest_supported_component_sample_m=lo,deepest_supported_component_sample_m=hi,upper_boundary_status=p['upper_status'],lower_boundary_status=p['lower_status'])
        writer.writerow({k:'' if d.get(k) is None else json.dumps(d[k],separators=(',',':')) if isinstance(d[k],(dict,list,bool)) else d[k] for k in fields})
    return out.getvalue().encode()


def derive_case(case,pointer,branch_scope):
    owner=case['entity_id']
    if owner not in OWNERS or case['component_bearing_degrees_true']!=OWNERS[owner] or case['velocity_threshold_m_s']!=THRESHOLDS[owner] or case['snapshot_time_utc'] not in OWNER_DATES[owner]:raise ValueError('Original branch/date/frame/cutoff required')
    if case['core_reselected'] is not False or case['named_current_axis_independently_validated'] is not False or case['water_mass_classification_performed'] is not False:raise ValueError('No identity or selection promotion')
    out={k:copy.deepcopy(case[k]) for k in ['entity_id','section_id','snapshot_time_utc','source_file','source_sha256','source_geometry','component_bearing_degrees_true','original_horizontal_selection_status','original_selected_column_index','native_input_column_count']}
    out.update(source_descriptor_pointer=pointer,branch_scope=branch_scope,velocity_threshold_m_s=THRESHOLDS[owner],status='ORIGINAL_AXIS_UNRESOLVED_NO_SECTION_GEOMETRY',columns=[],strips=[],conditional_partial_area_km2=None,sampling_bracket_partial_area_bounds_km2=None,integrated_strip_span_m=None,equivalent_paired_component_thickness_m=None,physical_cross_section_area_km2=None,physical_current_thickness_m=None,volume_km3=None,whole_section_area_established=False,annual_extrema_established=False,physical_uncertainty_m=None,named_current_axis_independently_validated=False,whole_route_depth_eligible=False,physical_volume_eligible=False)
    if case['status']=='ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN':
        if case['columns']:raise ValueError('Unresolved case must not acquire substitute columns')
        return out
    if case['status']!='REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN':raise ValueError('Unsupported retained curtain status')
    z=case['depth_levels_m']
    if not 2<=len(z)<=40 or not all(finite(v) and v>=0 for v in z) or any(b<=a for a,b in zip(z,z[1:])):raise ValueError('Original ascending descriptor depth coordinates')
    cols=case['columns']
    if not 3<=len(cols)<=150 or len(cols)!=case['native_input_column_count'] or [c['native_column_index'] for c in cols]!=list(range(len(cols))):raise ValueError('Every original ordered native column required')
    for c in cols:
        runs=[run_support(r,z,THRESHOLDS[owner]) for r in c['connected_depth_runs']]
        if any(a['native_depth_indices_inclusive'][1]>=b['native_depth_indices_inclusive'][0] for a,b in zip(runs,runs[1:])):raise ValueError('Separate non-overlapping vertical runs required')
        out['columns'].append({'native_column_index':c['native_column_index'],'sampled_lon_lat':copy.deepcopy(c['sampled_lon_lat']),'runs':runs,'status':c['status']})
    for a,b in zip(cols,cols[1:]):
        fixed,varying=(0,1) if AXES[owner]=='longitude' else (1,0)
        if abs(a['sampled_lon_lat'][fixed]-b['sampled_lon_lat'][fixed])>1e-8 or b['sampled_lon_lat'][varying]<=a['sampled_lon_lat'][varying] or b['global_longitude_index']-a['global_longitude_index']!=(0 if fixed==0 else 1) or b['global_latitude_index']-a['global_latitude_index']!=(1 if fixed==0 else 0):raise ValueError('Unchanged transverse axis and consecutive native indices required')
    out['strips']=[strip(a,b) for a,b in zip(out['columns'],out['columns'][1:])]
    supported=[s for s in out['strips'] if s['patches']]
    out.update(status='CONDITIONAL_PARTIAL_COMPONENT_SECTION_GEOMETRY',lateral_gate_censored=case['lateral_gate_censored'])
    if supported:
        area=sum(p['linear_contour_strip_area_km2'] for s in supported for p in s['patches']);span=sum(s['distance_m'] for s in supported)
        out.update(conditional_partial_area_km2=area,sampling_bracket_partial_area_bounds_km2=[sum(p['sampling_bracket_strip_area_bounds_km2'][k] for s in supported for p in s['patches']) for k in [0,1]],integrated_strip_span_m=span,equivalent_paired_component_thickness_m=area*1e6/span)
    return out

def csv_bytes(rows):
    fields=['entity_id','section_id','snapshot_time_utc','status','component_bearing_degrees_true','velocity_threshold_m_s','section_fixed_axis','surface_gate_policy','source_selection_depth_interval_m','source_selection_window_origin','source_rule_operator_file','source_identity_context','original_axis_proxy_depth_anchor','original_primary_layer','conditional_partial_area_km2','sampling_bracket_partial_area_bounds_km2','integrated_strip_span_m','equivalent_paired_component_thickness_m','lateral_gate_censored','whole_section_area_established','physical_current_thickness_m','volume_km3','source_descriptor_pointer']
    stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=fields,lineterminator='\n');writer.writeheader()
    for row in rows:writer.writerow({k:json.dumps(row.get(k),ensure_ascii=False,separators=(',',':')) if isinstance(row.get(k),(dict,list,bool)) else '' if row.get(k) is None else row[k] for k in fields})
    return stream.getvalue().encode()


def all_report_runs(report):
    for row in report['cases']:
        for column in row['columns']:
            yield from column['runs']
        if row['original_axis_proxy_depth_anchor'] is not None:
            yield row['original_axis_proxy_depth_anchor']['paired_component_run']

def compact_report(report):
    out=copy.deepcopy(report)
    if out['schema']!='osw.boundary-subsurface-paired-depth.v1':raise ValueError('Original scientific report schema required')
    out['schema']='osw.boundary-subsurface-paired-depth.v2';out['run_note']=RUN_NOTE
    for run in all_report_runs(out):
        if run.pop('minimum_span_interpretation')!=RUN_NOTE:raise ValueError('Only exact repeated metadata can be compacted')
        run['minimum_span_definition_ref']='/run_note'
    return out

def expand_report(compact):
    out=copy.deepcopy(compact)
    if out['schema']!='osw.boundary-subsurface-paired-depth.v2' or out.pop('run_note')!=RUN_NOTE:raise ValueError('Exact shared note and v2 representation required')
    out['schema']='osw.boundary-subsurface-paired-depth.v1'
    for run in all_report_runs(out):
        if run.pop('minimum_span_definition_ref')!='/run_note':raise ValueError('Exact metadata reference required')
        if 'minimum_span_is_physical_current_bound' not in run:raise ValueError('Original metadata insertion anchor required')
        restored={}
        for key,value in run.items():
            if key=='minimum_span_is_physical_current_bound':restored['minimum_span_interpretation']=RUN_NOTE
            restored[key]=value
        run.clear();run.update(restored)
    return out

def main():
    start=float(os.environ['OSW_BOUNDARY_SUBSURFACE_PAIRED_DEPTH_START'])
    def stop(*a):raise TimeoutError('Shared60second descriptor geometry deadline')
    signal.signal(signal.SIGALRM,stop);signal.signal(signal.SIGTERM,stop);elapsed=time.monotonic()-start+PRIOR_ACTIVE_SECONDS_UPPER
    if not 0<=elapsed<30:raise ValueError('One shared synthetic-test/producer clock required')
    signal.alarm(max(1,int(60-elapsed)));socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline descriptors only'))
    out=ROOT/'boundary-subsurface-paired-depth-v1';out.mkdir(exist_ok=False)
    def save(v):
        tmp=out/'query-ledger.tmp';tmp.write_bytes(encode(v));os.replace(tmp,out/'catalog-query-ledger.json')
    query=DescriptorQuery(save,prior_numeric=PRIOR_NUMERIC,prior_bytes=PRIOR_BYTES);reader=query.reader(lambda p:(ROOT/p).read_bytes())
    try:
        with query.decoding():
            op=json.loads(reader(OP))
            for path,pin in op['input_sha256'].items():
                if sha((ROOT/path).read_bytes())!=pin:raise ValueError('Frozen descriptor input changed:'+path)
            raw=reader(SOURCE)
            if sha(raw)!=SOURCE_SHA:raise ValueError('Exact reviewed curtain bytes required')
            source=json.loads(raw);before=copy.deepcopy(source);report=build(source,json.loads(reader(REVIEW)),[json.loads(reader(p)) for p in METHODS])
            if source!=before:raise ValueError('Source descriptors must remain exact')
            report['input_sha256']=op['input_sha256'];rr=encode(compact_report(report));table=csv_bytes(report['cases']);anchors=anchor_csv(report['cases'])
            restored=expand_report(json.loads(rr))
            if restored!=report or len(list(csv.DictReader(io.StringIO(table.decode()))))!=60 or csv_bytes(restored['cases'])!=table or anchor_csv(restored['cases'])!=anchors or len(list(csv.DictReader(io.StringIO(anchors.decode()))))!=60:raise ValueError('Complete report/CSV/anchor roundtrip')
            if len(rr)+len(table)+len(anchors)+(out/'catalog-query-ledger.json').stat().st_size>2400000:raise ValueError('Whole output cap')
            (out/'section-geometry.json').write_bytes(rr);(out/'sections.csv').write_bytes(table);(out/'depth-anchors.csv').write_bytes(anchors)
            print(json.dumps({'counts':report['counts'],'counts_by_current':report['counts_by_current'],'counts_by_primary_threshold_m_s':report['counts_by_primary_threshold_m_s'],'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_unique_json_bytes':query.ledger['unique_json_bytes'],'prior_failed_numeric_tokens':PRIOR_NUMERIC,'prior_failed_json_bytes':PRIOR_BYTES,'cumulative_active_seconds':time.monotonic()-start+PRIOR_ACTIVE_SECONDS_UPPER,'output_bytes':len(rr)+len(table)+len(anchors)+(out/'catalog-query-ledger.json').stat().st_size}),flush=True)
    finally:signal.alarm(0)

if __name__=='__main__':main()
