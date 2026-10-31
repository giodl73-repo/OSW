"""Local candidate-axis checks and signed velocity-normal spans; no admission."""
import json
import math
from collections import Counter
import numpy as np
from indian_secc_positive_bands import ROOT, SOURCE, REPORT as BANDS, verify as verify_bands, digest
from west_australian_regional_streamlines import Field, GEOD, readback
from west_australian_regional_streamlines_rk4 import trial, StageFailure, MIN_STEP_KM, TOLERANCE_KM

PROTOCOL = 'plans/indian-secc-local-axis-normal-protocol-v1.md'
OPERATOR = 'analysis/indian_secc_local_normals.py'
REPORT = 'research/indian-secc-local-axis-normal-spans.json'
FIGURE = 'figures/indian-secc-local-axis-normal-spans.svg'
MANIFEST = 'research/indian-secc-local-axis-normal-figure.json'
SAMPLE_COLUMNS = ['normal_offset_km','longitude_degrees_east','latitude_degrees_north',
                  'eastward_m_s','northward_m_s','projected_tangent_m_s',
                  'ascending_latitude_cell_index','longitude_cell_index','status']


def r(value, digits=6):
    return None if value is None else readback(value,digits)


def bearing(velocity):
    return math.degrees(math.atan2(velocity[0],velocity[1])) % 360


def normal_point(origin, tangent, offset):
    if offset == 0: return tuple(origin), tangent % 360
    normal = (tangent+90) % 360
    lon,lat,back = GEOD.fwd(*origin,normal if offset>0 else normal+180,abs(offset)*1000)
    increasing_normal = back+180 if offset>0 else back
    return (lon,lat),(increasing_normal-90) % 360


def sample(field, origin, tangent, offset):
    point,angle = normal_point(origin,tangent,offset);cell = field.cell(*point)
    velocity = field.sample(*point) if cell is not None else None
    status = 'outside_source' if cell is None else 'missing_paired_corner' if velocity is None else 'ok'
    q = None if velocity is None else velocity[0]*math.sin(math.radians(angle))+velocity[1]*math.cos(math.radians(angle))
    return {'s':offset,'point':point,'tangent':angle,'velocity':velocity,'q':q,'cell':cell,'status':status}


def profile(field, origin, step, limit=600):
    velocity = field.sample(*origin)
    if velocity is None: return {'origin':tuple(origin),'bearing':None,'rows':[],'status':'missing_center_support'}
    angle = bearing(velocity);center = sample(field,origin,angle,0);sides = []
    for direction in [-1,1]:
        rows=[];previous=center
        for distance in range(step,limit+1,step):
            row = sample(field,origin,angle,direction*distance)
            if row['status']=='ok' and not field.supported_rectangle(previous['point'],row['point']):
                row.update(status='unsupported_rectangle',velocity=None,q=None)
            rows.append(row)
            if row['status']!='ok':break
            previous=row
        sides.append(rows)
    return {'origin':tuple(origin),'bearing':angle,'rows':list(reversed(sides[0]))+[center]+sides[1],'status':'sampled'}


def peak_audit(data):
    rows=data['rows'];window=[(i,x) for i,x in enumerate(rows) if abs(x['s'])<=40 and x['q'] is not None]
    result={'index':None,'status':'missing_peak_support','usable_for_thresholds':False,'tie_offsets_km':[],
            'peak_offset_km':None,'peak_projected_m_s':None,'endpoint_contrast_fraction':None,'direction_difference_degrees':None}
    if not window:return result
    maximum=max(x['q'] for _,x in window);ties=[(i,x) for i,x in window if maximum-x['q']<=1e-10]
    result.update(peak_projected_m_s=maximum,tie_offsets_km=[x['s'] for _,x in ties])
    if maximum<.02:return {**result,'status':'weak_projected_peak'}
    if len(ties)!=1:return {**result,'status':'numerically_tied_peak'}
    index,peak=ties[0];result.update(index=index,peak_offset_km=peak['s'])
    if abs(peak['s'])>=40:return {**result,'status':'peak_at_search_edge'}
    result['usable_for_thresholds']=0<index<len(rows)-1 and all(x['q'] is not None and x['q']<peak['q'] for x in rows[index-1:index+2:2])
    difference=(bearing(peak['velocity'])-peak['tangent']+180)%360-180
    result['direction_difference_degrees']=abs(difference)
    endpoints=[x for _,x in window if abs(x['s'])==40]
    if len(endpoints)!=2:return {**result,'status':'missing_search_endpoint'}
    contrast=(maximum-max(x['q'] for x in endpoints))/maximum;result['endpoint_contrast_fraction']=contrast
    status='supported_local_peak' if contrast>=.01 and result['usable_for_thresholds'] else 'insufficient_endpoint_contrast'
    return {**result,'status':status}


def packed_row(row):
    uv=row['velocity'] or (None,None);cell=row['cell'] or (None,None)
    return [r(row['s']),*[r(x,8) for x in row['point']],r(uv[0],8),r(uv[1],8),r(row['q'],8),*cell,row['status']]


def packed_peak(peak):
    return {k:r(v,8 if k=='peak_projected_m_s' else 6) if isinstance(v,float) else v for k,v in peak.items()}


def crossing(field,data,index,direction,fraction):
    rows=data['rows'];threshold=rows[index]['q']*fraction;previous=index;current=index+direction
    while 0<=current<len(rows):
        a,b=rows[previous],rows[current]
        if b['q'] is None:return {'status':b['status']+'_before_crossing','offset_km':None,'point':None}
        if b['q']<=threshold:
            weight=(threshold-a['q'])/(b['q']-a['q']);offset=a['s']+weight*(b['s']-a['s'])
            point,_=normal_point(data['origin'],data['bearing'],offset)
            check=sample(field,data['origin'],data['bearing'],offset)
            return {'status':'sampled_linear_crossing','offset_km':r(offset),'point':[r(x,8) for x in point],
                    'bracket':[packed_row(a),packed_row(b)],'threshold_projected_m_s':r(threshold,8),
                    'evaluated_component_residual_m_s':r(None if check['q'] is None else check['q']-threshold,8),
                    '_raw_offset':offset,'_raw_point':point}
        previous=current;current+=direction
    return {'status':'profile_limit_without_crossing','offset_km':None,'point':None}


def spans(field,data,peak):
    cases=[]
    for fraction in [.4,.5,.6]:
        case={'fraction':fraction,'status':'no_supported_unique_peak','span_km':None,'approximate_span_km':None,
              'bracket_span_km':None,'edges':{},'native_grid_scales':None,'resolution_review_required':None}
        if not peak['usable_for_thresholds']:cases.append(case);continue
        edges=[crossing(field,data,peak['index'],direction,fraction) for direction in [-1,1]]
        case['edges']={name:{k:v for k,v in edge.items() if not k.startswith('_')} for name,edge in zip(['negative_normal','positive_normal'],edges)}
        case['status']='unresolved_edge_pair'
        if all(e['status']=='sampled_linear_crossing' for e in edges):
            width=GEOD.inv(*edges[0]['_raw_point'],*edges[1]['_raw_point'])[2]/1000
            lon,lat=data['origin'];yi,xi=field.cell(lon,lat)
            scale=max(GEOD.inv(lon,field.y[yi],lon,field.y[yi+1])[2],GEOD.inv(field.x[xi],lat,field.x[xi+1],lat)[2])/1000
            # If both edges are on one side of the origin, use their signed brackets.
            negative_inner=edges[0]['bracket'][0][0];positive_inner=edges[1]['bracket'][0][0]
            negative_outer=edges[0]['bracket'][1][0];positive_outer=edges[1]['bracket'][1][0]
            case.update(status='paired_sampled_edges',span_km=r(width),approximate_span_km=math.floor(width/10+.5)*10,
                        bracket_span_km=[r(abs(positive_inner-negative_inner)),r(abs(positive_outer-negative_outer))],
                        native_grid_scales=r(width/scale),resolution_review_required=width/scale<4,
                        any_edge_at_or_north_of_equator=any(e['_raw_point'][1]>=0 for e in edges))
        cases.append(case)
    return cases


def section(field,point,step,station):
    data=profile(field,point,step);peak=peak_audit(data);flags=[]
    if peak['status']!='supported_local_peak':flags.append(peak['status'])
    if peak['peak_offset_km'] is not None and abs(peak['peak_offset_km'])>10:flags.append('streamline_peak_displacement_exceeds_10km')
    if peak['direction_difference_degrees'] is not None and peak['direction_difference_degrees']>15:flags.append('peak_direction_difference_exceeds_15degrees')
    return {'station_arc_parameter_km':station,'origin_lon_lat':[r(x,8) for x in point],
            'normal_bearing_degrees_true':r(None if data['bearing'] is None else (data['bearing']+90)%360),
            'peak':packed_peak(peak),'local_candidate_axis_check':not flags,'failed_axis_checks':flags,
            'threshold_cases':spans(field,data,peak),'samples':[packed_row(x) for x in data['rows']]}


def advance(field,point,direction,distance=50):
    vertices=[tuple(point)];parameter=0.;length=0.;step=10.;errors=[];rejected=0;status='target_station_reached'
    for _ in range(3000):
        remaining=distance-parameter
        if remaining<1e-9:break
        size=min(step,remaining)
        try:middle,end,error=trial(field,vertices[-1],direction,size)
        except StageFailure as failure:
            rejected+=1
            if size>MIN_STEP_KM+1e-12:step=max(MIN_STEP_KM,size/2);continue
            status=failure.reason;break
        for p in [middle,end]:length+=GEOD.inv(*vertices[-1],*p)[2]/1000;vertices.append(p)
        parameter+=size;errors.append(error)
        if error<TOLERANCE_KM/32:step=min(10,step*2)
    else:status='iteration_limit_guard'
    return {'status':status,'arc_parameter_km':r(parameter),'geodesic_chord_sum_km':r(length),
            'maximum_local_error_estimate_km':r(max(errors,default=0)),'rejected_trials':rejected,
            'vertices_lon_lat':[[r(x,8) for x in p] for p in vertices]},vertices[-1]


def case(field,anchor,offset,step,month):
    key=anchor['section_id'].removeprefix('indian-secc-');origin=(anchor['longitude'],anchor['selected_peak_latitude'])
    row={'id':f'm{month:02d}:{key}:offset{offset}:step{step}','month':month,'section_id':anchor['section_id'],
         'native_latitude_offset':offset,'normal_sample_step_km':step,'primary_seed':offset==0,'stations':[],'paths':[],
         'status':'seed_unavailable','all_five_local_axis_checks_pass':False,'refined_seed_lon_lat':None}
    if origin[1] is None:return row
    yi=min(range(len(field.y)),key=lambda i:abs(field.y[i]-origin[1]));yi+=offset
    if not 0<=yi<len(field.y):return {**row,'status':'seed_offset_outside_source'}
    origin=(origin[0],float(field.y[yi]));row['original_seed_lon_lat']=[r(x,8) for x in origin]
    velocity=field.sample(*origin)
    if velocity is None:return {**row,'status':'missing_seed_support'}
    if velocity[0]<.02 or math.hypot(*velocity)<.02:return {**row,'status':'weak_or_non_eastward_seed'}
    initial=profile(field,origin,step);peak=peak_audit(initial)
    row['initial_refinement']={'peak':packed_peak(peak),'search_samples':[packed_row(x) for x in initial['rows'] if abs(x['s'])<=40]}
    if peak['status']!='supported_local_peak':
        row['initial_refinement'].update(diagnostic_threshold_cases=spans(field,initial,peak),samples=[packed_row(x) for x in initial['rows']])
        return {**row,'status':'seed_refinement_'+peak['status']}
    refined=initial['rows'][peak['index']]['point'];row['refined_seed_lon_lat']=[r(x,8) for x in refined]
    row['stations'].append(section(field,refined,step,0))
    if offset!=0:return {**row,'status':'seed_sensitivity_section_only'}
    for direction in [-1,1]:
        point=refined
        for number in [1,2]:
            path,point=advance(field,point,direction);path.update(direction=direction,target_station_arc_parameter_km=direction*number*50);row['paths'].append(path)
            if path['status']!='target_station_reached':break
            row['stations'].append(section(field,point,step,direction*number*50))
    row['stations'].sort(key=lambda x:x['station_arc_parameter_km'])
    passed=len(row['stations'])==5 and all(s['local_candidate_axis_check'] for s in row['stations'])
    return {**row,'status':'all_five_local_axis_checks_pass' if passed else 'candidate_axis_checks_unresolved',
            'all_five_local_axis_checks_pass':passed}


def build():
    bands,pins=verify_bands();source=json.loads((ROOT/SOURCE).read_bytes());cases=[]
    for frame,month in zip(source['months'],bands['months']):
        field=Field(source['longitude_degrees_east'],source['latitude_degrees_north'],frame['eastward_m_s'],frame['northward_m_s'])
        for anchor in month['anchors']:
            for offset in [-1,0,1]:
                for step in [5,10]:cases.append(case(field,anchor,offset,step,frame['month']))
    summaries=[]
    for c in cases:
        central=next((s for s in c['stations'] if s['station_arc_parameter_km']==0),None)
        nominal=central['threshold_cases'][1] if central else None
        summaries.append({k:c[k] for k in ['id','month','section_id','native_latitude_offset','normal_sample_step_km','primary_seed','status','all_five_local_axis_checks_pass']}|
                         {'available_stations':len(c['stations']),'central_half_peak_diagnostic_span_km':None if nominal is None else nominal['span_km'],
                          'central_half_peak_status':None if nominal is None else nominal['status'],
                          'central_resolution_review_required':None if nominal is None else nominal['resolution_review_required'],
                          'central_axis_check_pass':None if central is None else central['local_candidate_axis_check'],
                          'central_failed_axis_checks':[] if central is None else central['failed_axis_checks'],
                          'physical_current_axis_admitted':False,'physical_current_width_admitted':False})
    comparisons=[]
    for a,b in zip(summaries[::2],summaries[1::2]):
        x,y=a['central_half_peak_diagnostic_span_km'],b['central_half_peak_diagnostic_span_km']
        comparisons.append({'month':a['month'],'section_id':a['section_id'],'native_latitude_offset':a['native_latitude_offset'],
                            'step5_case':a['id'],'step10_case':b['id'],'step5_span_km':x,'step10_span_km':y,
                            'absolute_span_difference_km':None if x is None or y is None else r(abs(x-y)),
                            'both_five_station_checks_pass':a['all_five_local_axis_checks_pass'] and b['all_five_local_axis_checks_pass'],
                            'is_physical_uncertainty_interval':False})
    monthly=[{'month':m,'attempts':sum(c['month']==m for c in cases),
              'primary_five_station_passes':sum(c['month']==m and c['all_five_local_axis_checks_pass'] for c in cases),
              'central_paired_spans':sum(s['month']==m and s['central_half_peak_status']=='paired_sampled_edges' for s in summaries),
              'primary_seed_both_steps_pass':sum(c['month']==m and c['native_latitude_offset']==0 and c['both_five_station_checks_pass'] for c in comparisons)} for m in range(1,13)]
    paths=[PROTOCOL,OPERATOR,'analysis/west_australian_regional_streamlines.py','analysis/west_australian_regional_streamlines_rk4.py']
    return {'schema':'osw.indian-secc-local-axis-normal.v1','status':'exploratory_local_candidates_not_current_dimensions',
            'current_id':bands['current_id'],'entity_id':bands['entity_id'],'nominal_depth_m':15,'source_file':SOURCE,'band_file':BANDS,
            'sample_columns':SAMPLE_COLUMNS,'source_cell_latitude_order':'ascending','source_latitude_degrees_north_ascending':sorted(source['latitude_degrees_north']),
            'source_first_time':source['source_first_time'],'source_last_time':source['source_last_time'],
            'cases':cases,'case_summaries':summaries,'step_comparisons':comparisons,'monthly_summary':monthly,
            'counts':{'attempts':len(cases),'primary_seed_attempts':sum(c['primary_seed'] for c in cases),
                      'status_counts':dict(sorted(Counter(c['status'] for c in cases).items())),
                      'all_five_station_passes':sum(c['all_five_local_axis_checks_pass'] for c in cases),
                      'sampled_stations':sum(len(c['stations']) for c in cases),
                      'paired_half_peak_sections':sum(s['threshold_cases'][1]['status']=='paired_sampled_edges' for c in cases for s in c['stations']),
                      'central_paired_half_peak_sections':sum(s['central_half_peak_status']=='paired_sampled_edges' for s in summaries),
                      'primary_seed_both_steps_pass':sum(c['native_latitude_offset']==0 and c['both_five_station_checks_pass'] for c in comparisons)},
            'current_association_verified':False,'physical_current_axis_admitted':False,'whole_current_length_km':None,'whole_current_width_km':None,
            'annual_physical_length_range_km':None,'annual_physical_width_range_km':None,'length_rank_eligible':False,'width_rank_eligible':False,
            'physical_state_join_eligible':False,'seasonal_current_footprint_admitted':False,
            'seed_sensitivity_is_independent_observation':False,'sampling_step_is_source_resolution':False,
            'method_sensitivity_is_measurement_uncertainty':False,
            'comparison_figure':FIGURE,'input_sha256':{**pins,**{p:digest(p) for p in paths}},
            'limitations':['Local mean-field candidate checks do not establish named-current identity, whole-current dimensions or particle trajectories.',
                'Sampling every5/10km interpolates the native one-third-degree product; it does not improve source resolution.',
                'Step, seed and threshold sensitivity are distinct from physical seasonal variation and measurement uncertainty.',
                'Static monthly fields, incomplete source masks and short200km candidate segments cannot prove annual physical extents or state passage.']}


def encoded(d):return (json.dumps(d,separators=(',',':'),allow_nan=False)+'\n').encode()


def verify():
    d=json.loads((ROOT/REPORT).read_bytes())
    if encoded(d)!=encoded(build()):raise ValueError('Changed local normal source/operator/report')
    manifest=json.loads((ROOT/MANIFEST).read_bytes())
    if manifest['source_sha256']!=digest(REPORT) or manifest['source_file']!=REPORT or manifest['current_geometry_admitted'] is not False:
        raise ValueError('Changed local normal figure/source binding')
    pins={**d['input_sha256'],REPORT:digest(REPORT),MANIFEST:digest(MANIFEST),manifest['generator_file']:manifest['generator_sha256']}
    pins.update({v['file']:v['sha256'] for v in manifest['figures'].values()})
    for p,h in pins.items():
        if digest(p)!=h:raise ValueError('Changed local normal dependency:'+p)
    return d,pins


if __name__=='__main__':
    d=build();(ROOT/REPORT).write_bytes(encoded(d));print(json.dumps(d['counts']))
