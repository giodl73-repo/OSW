"""NEC and Aleutian paired component depth shapes from compiled descriptors only."""
import copy,csv,hashlib,io,json,math,os,signal,socket,time
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery
ROOT=Path(__file__).resolve().parents[1]
OP='research/nec-subarctic-paired-depth-operator-v1.json'
PRIOR_NUMERIC=0
PRIOR_BYTES=0
PRIOR_ACTIVE_SECONDS_UPPER=0
RUN_NOTE='Inclusive component-thickness lower support under original contiguous piecewise-linear model definition; single-level zero is an uninformative bound, not absence.'
SOURCE='research/nec-subarctic-velocity-depth-curtains-v1.json'
SOURCE_SHA='6bbfa3e7e5d943db666ba6ffd08b9135ffb55b53c138de2e2631270d2d3c02c5'
REVIEW='research/current-depth-nec-subarctic-velocity-curtains-source-review-v1.json'
METHODS=['research/nec-subarctic-depth-sections-operator-v1.json']
DATES=['2022-01-15T00:00:00Z','2022-07-15T00:00:00Z']
OWNERS={'current:pacific-north-equatorial':270,'current:atlantic-north-equatorial':270,'current:aleutian':90}
THRESHOLDS={o:(.05 if o=='current:aleutian' else .1) for o in OWNERS}
SURFACE_GATES={o:(.02 if o=='current:aleutian' else .05) for o in OWNERS}
OWNER_CASES={'current:pacific-north-equatorial':14,'current:atlantic-north-equatorial':8,'current:aleutian':12}
COLLECTION_ORIGINS={'recovered_original_attempt2':'research/nec-subarctic-depth-sections-operator-v1.json','completion_missing_five':'research/nec-subarctic-depth-completion-operator-v1.json'}


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
    row['section_orientation']='fixed_longitude_not_independently_flow_normal'
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

def longitude_delta(a,b):
    if not finite(a) or not finite(b):raise ValueError('Finite circular longitudes required')
    return (a-b+180)%360-180


def build(source,review,methods):
    if source['schema']!='osw.nec-subarctic-velocity-depth-curtains.v1' or source['status']!='REGIONAL_MODEL_COMPONENT_THRESHOLD_GEOMETRY_NOT_PHYSICAL_CURRENT_BOTTOM' or review['status']!='ALL34_ORIGINAL_CASES_PRESERVED_29_REGIONAL_CURTAINS_5_EXPLICIT_UNRESOLVED':raise ValueError('Exact original34case NEC/Aleutian cohort required')
    if len(methods)!=1 or set(methods[0]['currents'])!=set(OWNERS):raise ValueError('Original three separate owner contexts required')
    method=methods[0]
    if method['snapshot_times_utc']!=DATES or any(method['eligibility'].values()) or method['maximum_nearest_longitude_distance_km']!=5 or method['core_search_depth_interval_m']!=[0,200] or method['surface_component_gate_m_s']!=.05:raise ValueError('Original dates,window,common gate and nonpromotion')
    configs=method['currents'];definitions={};expected=set()
    for owner,config in configs.items():
        if config['entity_id']!=owner or config['component_bearing_degrees_true']!=OWNERS[owner] or config['primary_threshold_m_s']!=THRESHOLDS[owner] or config['surface_component_gate_m_s']!=SURFACE_GATES[owner] or config['temperature_gate'] is not None:raise ValueError('Original owner-specific directions,cutoffs and surface gates')
    for definition in method['sections']:
        key=(definition['entity_id'],definition['id'])
        if definition['entity_id'] not in OWNERS or definition['fixed_axis']!='longitude' or key in definitions:raise ValueError('Original unique longitude section definitions')
        definitions[key]=definition;expected.update((*key,t) for t in DATES)
    cases=source['cases'];keys=[(c['entity_id'],c['section_id'],c['snapshot_time_utc']) for c in cases]
    if len(cases)!=34 or len(set(keys))!=34 or set(keys)!=expected:raise ValueError('Every original34unique case required')
    rows=[]
    for i,c in enumerate(cases):
        owner=c['entity_id'];definition=definitions[owner,c['section_id']];g=c['source_geometry']
        if not isinstance(g,dict) or g['section_definition']!=definition or c['source_operator']!=METHODS[0] or c['transport_origin'] not in COLLECTION_ORIGINS or c['source_collection_operator']!=COLLECTION_ORIGINS[c['transport_origin']]:raise ValueError('Original section and recovered/completion custody required')
        native=g['actual_source_longitude_degrees_east'];receipt=g['maximum_nearest_longitude_distance_km']
        if not finite(native) or not finite(receipt) or not 0<=receipt<=5:raise ValueError('Original native longitude/distance receipt required')
        wrapped=(native+180)%360-180
        for col in c['columns']:
            lat=col['sampled_lon_lat'][1]
            if col['sampled_lon_lat'][0]!=wrapped or abs(longitude_delta(wrapped,definition['longitude_degrees_east']))*math.pi/180*6371008.8*math.cos(math.radians(lat))>5000:raise ValueError('Original wrapped longitude and circular every-row5km tolerance')
        row=derive_case(c,'/cases/'+str(i),configs[owner]['branch_scope']);attach_anchor(row,c)
        row['source_core_search_depth_interval_m']=copy.deepcopy(method['core_search_depth_interval_m']);row['source_selection_depth_interval_m']=copy.deepcopy(method['core_search_depth_interval_m'])
        row['source_selection_window_origin']='original_explicit_method_upper200m_integral';row['source_surface_component_gate_m_s']=SURFACE_GATES[owner]
        row['surface_gate_policy']='original_surface_selection_gate_not_primary_layer_boundary';row['source_native_surface_seed_connected']=c['native_surface_seed_connected']
        row['source_surface_connectivity_interpretation']='Original graph topology only;not proof of primary-layer surface top or physical thickness.' if row['original_axis_proxy_depth_anchor'] is not None else 'Graph not constructed because original axis unresolved.'
        row['source_rule_operator_file']=c['source_operator'];row['source_collection_operator']=c['source_collection_operator'];row['source_transport_origin']=c['transport_origin'];rows.append(row)
    by_owner={o:counts([r for r in rows if r['entity_id']==o]) for o in OWNERS};total=counts(rows)
    if any(by_owner[o]['source_cases']!=OWNER_CASES[o] for o in OWNERS) or total['original_axis_proxy_anchors']!=29 or total['original_unresolved_cases']!=5 or by_owner['current:pacific-north-equatorial']['original_unresolved_cases']!=2 or by_owner['current:atlantic-north-equatorial']['original_unresolved_cases']!=3:raise ValueError('Original29anchors/5gaps and owner coverage required')
    return {'schema':'osw.nec-subarctic-paired-depth.v1','source_descriptor':{'file':SOURCE,'sha256':SOURCE_SHA},'counts':total,'counts_by_current':by_owner,'counts_by_primary_threshold_m_s':{str(t):counts([r for r in rows if r['velocity_threshold_m_s']==t]) for t in [.05,.1]},'cases':rows,'primary_thresholds_m_s_by_current':copy.deepcopy(THRESHOLDS),'surface_selection_gates_m_s_by_current':copy.deepcopy(SURFACE_GATES),'temporal_scope':'Two exact January/July15,2022snapshots,not seasonal means/annual extrema.','method':'Finite paired component contours and unique linear strips on consecutive native latitude columns;minimum native-supported span where boundaries are censored. Circular fixed-longitude checks preserve date-line sections.','surface_gate_interpretation':'Original per-owner surface selection gates are weaker than primary layer cutoffs;they do not force the selected primary layer to the surface. Source graph surface connectivity is topology only,not a physical current boundary.','minimum_span_interpretation':'Conditional first-to-last contiguous native support under original piecewise-linear signed-component model,not physical current thickness bounds. Single-level zero is uninformative,not absence.','range_interpretation':'Native-bracket sampling scenarios,not physical uncertainty,confidence intervals or annual envelopes.','identity_scope':'Pacific and Atlantic NEC members remain separate from North Equatorial parent family and eastward counter/undercurrents. Aleutian/Subarctic stays distinct from westward Alaskan Stream,north-slope current and North Pacific Current. No inherited depth or independently classified current body.','axis_anchor_interpretation':'29original model axis proxies and5explicit null gaps with original candidate diagnoses;no replacement core,date,branch,gate or source. Recovered/completion collection provenance retained without replay.','interpretation':'Partial regional component geometry,not independently identified named-current axis,flow-normal width,whole-route depth,terrain clearance or physical volume. No between-section interpolation or additive water bodies.','source_credit':'HYCOM Consortium,NRL,COAPS-FSU;original fields and qualifiers retained.','runtime_changed':False,'full_goal_complete':False}


def anchor_csv(rows):
    fields=['entity_id','section_id','snapshot_time_utc','status','component_bearing_degrees_true','velocity_threshold_m_s','surface_gate_policy','source_selection_depth_interval_m','source_surface_component_gate_m_s','source_native_surface_seed_connected','source_surface_connectivity_interpretation','source_selection_window_origin','source_rule_operator_file','source_collection_operator','source_transport_origin','longitude_degrees_east','latitude_degrees_north','upper_component_depth_m','lower_component_depth_m','paired_component_thickness_m','native_supported_minimum_component_span_m','shallowest_supported_component_sample_m','deepest_supported_component_sample_m','upper_boundary_status','lower_boundary_status','original_selected_column_index','source_descriptor_pointer']
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');writer.writeheader()
    for row in rows:
        d={k:row[k] for k in ['entity_id','section_id','snapshot_time_utc','status','component_bearing_degrees_true','velocity_threshold_m_s','original_selected_column_index','source_descriptor_pointer']}
        d.update(surface_gate_policy=row['surface_gate_policy'],source_selection_depth_interval_m=row['source_selection_depth_interval_m'],source_surface_component_gate_m_s=row['source_surface_component_gate_m_s'],source_native_surface_seed_connected=row['source_native_surface_seed_connected'],source_surface_connectivity_interpretation=row['source_surface_connectivity_interpretation'],source_selection_window_origin=row['source_selection_window_origin'],source_rule_operator_file=row['source_rule_operator_file'],source_collection_operator=row['source_collection_operator'],source_transport_origin=row['source_transport_origin'])
        a=row['original_axis_proxy_depth_anchor']
        if a is not None:
            p=a['paired_component_run'];lo,hi=p['native_supported_depth_interval_m']
            d.update(longitude_degrees_east=a['sampled_lon_lat'][0],latitude_degrees_north=a['sampled_lon_lat'][1],upper_component_depth_m=p['upper_depth_m'],lower_component_depth_m=p['lower_depth_m'],paired_component_thickness_m=p['thickness_m'],native_supported_minimum_component_span_m=p['native_supported_minimum_component_span_m'],shallowest_supported_component_sample_m=lo,deepest_supported_component_sample_m=hi,upper_boundary_status=p['upper_status'],lower_boundary_status=p['lower_status'])
        writer.writerow({k:'' if d.get(k) is None else json.dumps(d[k],separators=(',',':')) if isinstance(d[k],(dict,list,bool)) else d[k] for k in fields})
    return out.getvalue().encode()


def derive_case(case,pointer,branch_scope):
    owner=case['entity_id']
    if owner not in OWNERS or case['component_bearing_degrees_true']!=OWNERS[owner] or case['velocity_threshold_m_s']!=THRESHOLDS[owner] or case['snapshot_time_utc'] not in DATES:raise ValueError('Original branch/date/frame/cutoff required')
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
        fixed,varying=0,1
        if abs(a['sampled_lon_lat'][fixed]-b['sampled_lon_lat'][fixed])>1e-8 or b['sampled_lon_lat'][varying]<=a['sampled_lon_lat'][varying] or b['global_longitude_index']-a['global_longitude_index']!=(0 if fixed==0 else 1) or b['global_latitude_index']-a['global_latitude_index']!=(1 if fixed==0 else 0):raise ValueError('Unchanged transverse axis and consecutive native indices required')
    out['strips']=[strip(a,b) for a,b in zip(out['columns'],out['columns'][1:])]
    supported=[s for s in out['strips'] if s['patches']]
    out.update(status='CONDITIONAL_PARTIAL_COMPONENT_SECTION_GEOMETRY',lateral_gate_censored=case['lateral_gate_censored'])
    if supported:
        area=sum(p['linear_contour_strip_area_km2'] for s in supported for p in s['patches']);span=sum(s['distance_m'] for s in supported)
        out.update(conditional_partial_area_km2=area,sampling_bracket_partial_area_bounds_km2=[sum(p['sampling_bracket_strip_area_bounds_km2'][k] for s in supported for p in s['patches']) for k in [0,1]],integrated_strip_span_m=span,equivalent_paired_component_thickness_m=area*1e6/span)
    return out

def csv_bytes(rows):
    fields=['entity_id','section_id','snapshot_time_utc','status','component_bearing_degrees_true','velocity_threshold_m_s','surface_gate_policy','source_selection_depth_interval_m','source_surface_component_gate_m_s','source_native_surface_seed_connected','source_surface_connectivity_interpretation','source_selection_window_origin','source_rule_operator_file','source_collection_operator','source_transport_origin','original_axis_proxy_depth_anchor','original_primary_layer','conditional_partial_area_km2','sampling_bracket_partial_area_bounds_km2','integrated_strip_span_m','equivalent_paired_component_thickness_m','lateral_gate_censored','whole_section_area_established','physical_current_thickness_m','volume_km3','source_descriptor_pointer']
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
    if report['schema']!='osw.nec-subarctic-paired-depth.v1':raise ValueError('Full scientific v1 report required')
    out=copy.deepcopy(report);schemas=[];lookup={};strings=[];string_lookup={}
    def pack(value):
        if isinstance(value,dict):
            keys=tuple(value)
            if keys not in lookup:lookup[keys]=len(schemas);schemas.append(list(keys))
            index=lookup[keys]
            return [1,index,[pack(v) for v in value.values()]]
        if isinstance(value,list):return [0,[pack(v) for v in value]]
        if type(value)==str:
            if value not in string_lookup:string_lookup[value]=len(strings);strings.append(value)
            return [2,string_lookup[value]]
        if value is None or type(value) in (bool,int,float):return value
        raise ValueError('Only original JSON values can be packed')
    node=pack(out['cases']);out['cases']={'encoding':'ordered-object-tables.v1','object_key_schemas':schemas,'string_values':strings,'node':node};out['schema']='osw.nec-subarctic-paired-depth.v2'
    return out


def expand_report(compact):
    out=copy.deepcopy(compact)
    if out['schema']!='osw.nec-subarctic-paired-depth.v2':raise ValueError('Packed scientific v2 report required')
    block=out['cases']
    if not isinstance(block,dict) or set(block)!=set(['encoding','object_key_schemas','string_values','node']) or block['encoding']!='ordered-object-tables.v1':raise ValueError('Exact ordered-object encoding required')
    schemas=block['object_key_schemas']
    if not isinstance(schemas,list) or any(not isinstance(keys,list) or not all(type(k)==str for k in keys) or len(keys)!=len(set(keys)) for keys in schemas) or len(schemas)!=len({tuple(keys) for keys in schemas}):raise ValueError('Unique ordered string-key schemas required')
    strings=block['string_values']
    if not isinstance(strings,list) or not all(type(v)==str for v in strings) or len(strings)!=len(set(strings)):raise ValueError('Unique exact string table required')
    def unpack(node):
        if not isinstance(node,list):
            if node is None or type(node) in (bool,int,float):return node
            raise ValueError('Untagged original object forbidden')
        if len(node)==2 and type(node[0])==int and node[0]==0 and isinstance(node[1],list):return [unpack(v) for v in node[1]]
        if len(node)==2 and type(node[0])==int and node[0]==2 and type(node[1])==int and 0<=node[1]<len(strings):return strings[node[1]]
        if len(node)!=3 or type(node[0])!=int or node[0]!=1 or type(node[1])!=int or not 0<=node[1]<len(schemas) or not isinstance(node[2],list) or len(node[2])!=len(schemas[node[1]]):raise ValueError('Exact object tag,valid schema and full value count required')
        return {key:unpack(value) for key,value in zip(schemas[node[1]],node[2])}
    cases=unpack(block['node'])
    if not isinstance(cases,list) or any(not isinstance(row,dict) for row in cases):raise ValueError('Expanded cases must be objects in a list')
    out['cases']=cases;out['schema']='osw.nec-subarctic-paired-depth.v1';return out


def main():
    start=float(os.environ['OSW_NEC_SUBARCTIC_PAIRED_DEPTH_START'])
    def stop(*a):raise TimeoutError('Shared60second descriptor geometry deadline')
    signal.signal(signal.SIGALRM,stop);signal.signal(signal.SIGTERM,stop);elapsed=time.monotonic()-start+PRIOR_ACTIVE_SECONDS_UPPER
    if not 0<=elapsed<30:raise ValueError('One shared synthetic-test/producer clock required')
    signal.alarm(max(1,int(60-elapsed)));socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline descriptors only'))
    out=ROOT/'nec-subarctic-paired-depth-v1';out.mkdir(exist_ok=False)
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
            if restored!=report or encode(restored)!=encode(report) or len(list(csv.DictReader(io.StringIO(table.decode()))))!=34 or csv_bytes(restored['cases'])!=table or anchor_csv(restored['cases'])!=anchors or len(list(csv.DictReader(io.StringIO(anchors.decode()))))!=34:raise ValueError('Complete report/CSV/anchor roundtrip')
            if len(rr)+len(table)+len(anchors)+(out/'catalog-query-ledger.json').stat().st_size>2400000:raise ValueError('Whole output cap')
            (out/'section-geometry.json').write_bytes(rr);(out/'sections.csv').write_bytes(table);(out/'depth-anchors.csv').write_bytes(anchors)
            print(json.dumps({'counts':report['counts'],'counts_by_current':report['counts_by_current'],'counts_by_primary_threshold_m_s':report['counts_by_primary_threshold_m_s'],'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_unique_json_bytes':query.ledger['unique_json_bytes'],'prior_failed_numeric_tokens':PRIOR_NUMERIC,'prior_failed_json_bytes':PRIOR_BYTES,'cumulative_active_seconds':time.monotonic()-start+PRIOR_ACTIVE_SECONDS_UPPER,'output_bytes':len(rr)+len(table)+len(anchors)+(out/'catalog-query-ledger.json').stat().st_size}),flush=True)
    finally:signal.alarm(0)

if __name__=='__main__':main()
