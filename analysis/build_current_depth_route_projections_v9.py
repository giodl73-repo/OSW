"""Conditional interval-valued seasonal core support; never invent a midpoint."""
import copy,csv,hashlib,io,json,math
from pathlib import Path
import build_current_depth_route_projections_v8 as previous

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-route-projection-operator-v9.json'
OUTPUT='research/current-depth-route-projections-v9.json'
CSV='research/current-depth-route-projections-v9.csv'
CASE_SHA256='fa8f76aab88046db113842af82239ec70afe99b4a927a226c4880733448384e3'


def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def validate_case(case,references):
    if digest(case)!=CASE_SHA256:raise ValueError('Unreviewed seasonal core-support interval contract')
    expected=['eicc-sen-2022-north-c-core-band','eicc-sen-2022-north-b-reach','eicc-sen-2022-north-a-core']
    if [a['reference_id'] for a in case['anchors']]!=expected:raise ValueError('Intervening shallow section must constrain the profile')
    for a in case['anchors']:
        r=references[a['reference_id']]
        if r!=a['source_context'] or r['entity_id']!=case['entity_id'] or r['source_case_id']!='eicc-sen-2022-northward' or r['calendar_months']!=[2,3,4] or r['flow_direction']!='northward' or r['model_product']!='Sen2022_ROMS_NIO':raise ValueError('Source phase, identity or model changed')
        if r['model_time_basis']!={'kind':'repeating_climatological_forcing','simulation_duration_years':8,'analysis_window':'last_three_simulation_years','calendar_years':None}:raise ValueError('Do not inherit forcing or validation calendar years')
        if a['section_latitude_degrees_north']!=r['section_latitude_degrees_north']:raise ValueError('Wrong source section')
        if a['section_name']=='C' and (r['metric']!='core_depth' or r['range_m']!=[0,100] or a['support_interval_m']!=[0,100]):raise ValueError('Core band must not become a midpoint or thickness')
        if a['section_name']=='B' and (r['metric']!='reported_vertical_extent' or r['approximate_value_m']!=20 or a['support_interval_m']!=[0,20] or a['constraint_kind']!='conditional_core_within_explicitly_surface_confined_layer'):raise ValueError('Layer-derived support is conditional, not a reported core measurement')
        if a['section_name']=='A' and (r['metric']!='core_depth' or r['approximate_value_m']!=150 or a['support_interval_m']!=[150,150]):raise ValueError('Nominal source point must retain source approximation')


def interval_at_latitude(anchors,latitude):
    if not math.isfinite(latitude):raise ValueError('Finite section latitude required')
    if len(anchors)<2 or not all(a['section_latitude_degrees_north']<b['section_latitude_degrees_north'] for a,b in zip(anchors,anchors[1:])):raise ValueError('Strictly northward ordered source sections required')
    for a in anchors:
        low,high=a['support_interval_m']
        if not all(math.isfinite(v) for v in [low,high]) or low<0 or low>high:raise ValueError('Finite nonnegative ordered support interval required')
    for a in anchors:
        if abs(latitude-a['section_latitude_degrees_north'])<1e-10:return list(a['support_interval_m']),list(a['support_interval_m']),[a['reference_id']],a['constraint_kind']
    for a,b in zip(anchors,anchors[1:]):
        south,north=a['section_latitude_degrees_north'],b['section_latitude_degrees_north']
        if south<latitude<north:
            f=(latitude-south)/(north-south);computed=[a['support_interval_m'][i]+f*(b['support_interval_m'][i]-a['support_interval_m'][i]) for i in [0,1]]
            # Outward display rounding cannot falsely narrow an assumed envelope.
            display=[10*math.floor(computed[0]/10),10*math.ceil(computed[1]/10)]
            return computed,display,[a['reference_id'],b['reference_id']],'conditional_piecewise_linear_support_envelope'
    return None,None,[],'unknown_outside_source_section_sequence'


def project(case,eligibility):
    anchors=copy.deepcopy(case['anchors']);latitudes=set(case['sample_latitudes_degrees_north'])|{a['section_latitude_degrees_north'] for a in anchors};samples=[]
    for latitude in sorted(latitudes):
        computed,display,refs,kind=interval_at_latitude(anchors,latitude)
        samples.append({'section_latitude_degrees_north':latitude,'computed_core_depth_support_interval_m':computed,'projected_core_depth_support_interval_m':display,'projected_depth_descriptor_m':None,'status':'unknown_outside_source_section_sequence' if computed is None else 'conditional_core_support_interval_available','core_support_interval_kind':kind,'source_reference_ids':refs,'source_section_name':next((a['section_name'] for a in anchors if a['section_latitude_degrees_north']==latitude),None),'distance_along_reference_route_km':None,'longitude':None,'latitude':None,'depth_uncertainty_m':None,'physical_thickness_m':None,'depth_interval_is_confidence_interval':False,'interval_width_is_current_thickness':False,'volume_eligible':False})
    return {'id':case['id'],'entity_id':case['entity_id'],'status':'CONDITIONAL_SEASONAL_CORE_SUPPORT_INTERVAL_SCENARIO','metric':'projected_conditional_velocity_core_depth_support_interval','vertical_datum':'local_sea_surface_positive_down','coordinate_kind':'source_cross_section_latitude_not_geographic_point','geometry_role':'seasonal_section_sequence_without_route_geometry','route_id':None,'route_file':None,'route_length_km':None,'source_reference_ids':[a['reference_id'] for a in anchors],'anchors':anchors,'samples':samples,'model_product':'Sen2022_ROMS_NIO','model_time_basis':case['model_time_basis'],'calendar_months':[2,3,4],'phase_label':'northward_seasonal_mean','flow_direction':'northward','phase_mean_not_monthly_time_series':True,'interpolation_coordinate':'source_section_latitude_degrees_north','interval_meaning':'Conditional nominal support for velocity-core location. Source C band and A approximate point are retained; B support assumes the maximum lies within its explicitly described approximate surface-confined20m layer. Not confidence limits, sampled temporal extrema, thickness, or a guaranteed physical bound.','interpolation_assumption':'Piecewise linear lower/upper support limits with the intervening B constraint retained. No midpoint selected. Interpolated display bounds round outward to10m; exact source-derived anchor descriptors are unchanged.','source_scope_qualification':case['source_scope_qualification'],'depth_uncertainty_m':None,'annual_range_m':None,'physical_thickness_m':None,'whole_current_representative':False,'eligibility':copy.deepcopy(eligibility),'full_goal_complete':False}


def build(root=ROOT):
    read=lambda p:json.loads((root/p).read_bytes());prior=previous.build(root)
    if prior!=read(previous.OUTPUT):raise ValueError('Prior ten regional profiles changed')
    op=read(OPERATOR);source=read(op['depth_register_file']);refs={r['id']:r for r in source['evidence']}
    if any(op['eligibility'].values()):raise ValueError('No physical or whole-current admission')
    validate_case(op['case'],refs);projections=copy.deepcopy(prior['projections']);projections.append(project(op['case'],op['eligibility']))
    records=copy.deepcopy(prior['records'])
    for r in records:
        r['projection_ids']=[p['id'] for p in projections if p['entity_id']==r['entity_id']];r['projection_status']='regional_assumed_interpolation_available' if r['projection_ids'] else 'not_yet_projected'
    files=set(prior['input_sha256'])|{OPERATOR,op['depth_register_file'],previous.OUTPUT,previous.CSV,'analysis/build_current_depth_route_projections_v8.py',prior['regional_volume_scenario_file']}
    owners=sum(bool(r['projection_ids']) for r in records)
    return {'schema':'osw.current-depth-route-projections.v9','status':'ELEVENTH_REGIONAL_SCENARIO_WITH_CONDITIONAL_CORE_DEPTH_INTERVALS','generator_file':'analysis/build_current_depth_route_projections_v9.py','generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_route_projections_v9.py').read_bytes()).hexdigest(),'input_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in sorted(files)},'previous_ten_projection_records_preserved':projections[:10]==prior['projections'],'counts':{'catalog_identities':len(records),'identities_with_regional_projection_scenarios':owners,'identities_not_yet_projected':len(records)-owners,'regional_projection_scenarios':len(projections),'source_anchor_references':len({r for p in projections for r in p['source_reference_ids']}),'new_depth_measurements':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0,'regional_reference_geometry_volume_scenarios':2},'interpretation':'Eleven regional scenarios across ten identities. Northward EICC seasonal core-support intervals retain a reported band, an approximate point and an explicitly conditional shallow-layer constraint. No invented midpoint, full-route depth, current thickness or seasonal time series.','regional_volume_scenario_file':prior['regional_volume_scenario_file'],'records':records,'projections':projections,'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}


def csv_bytes(document):
    compatible=copy.deepcopy(document);compatible['projections']=compatible['projections'][:10]
    reader=csv.DictReader(io.StringIO(previous.csv_bytes(compatible).decode('utf8')));columns=list(reader.fieldnames);rows=list(reader)
    columns+=['computed_core_depth_support_interval_m','projected_core_depth_support_interval_m','core_support_interval_kind','flow_direction','depth_interval_is_confidence_interval','interval_width_is_current_thickness']
    p=document['projections'][-1]
    for sample in p['samples']:
        row={k:v for k,v in sample.items() if k in columns};row.update(projection_id=p['id'],entity_id=p['entity_id'],geometry_role=p['geometry_role'],coordinate_kind=p['coordinate_kind'],metric=p['metric'],vertical_datum=p['vertical_datum'],model_product=p['model_product'],model_time_basis=json.dumps(p['model_time_basis'],sort_keys=True,separators=(',',':')),calendar_months='[2,3,4]',phase_label=p['phase_label'],flow_direction='northward',interpolation_coordinate=p['interpolation_coordinate'],source_reference_ids=json.dumps(sample['source_reference_ids'],separators=(',',':')),computed_core_depth_support_interval_m=json.dumps(sample['computed_core_depth_support_interval_m'],separators=(',',':')),projected_core_depth_support_interval_m=json.dumps(sample['projected_core_depth_support_interval_m'],separators=(',',':')));rows.append(row)
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows);return out.getvalue().encode('utf8')


def build_phase_comparison(document,root=ROOT):
    source_file=json.loads((root/OPERATOR).read_bytes())['depth_register_file'];source=json.loads((root/source_file).read_bytes());refs={r['id']:r for r in source['evidence']}
    sections=[]
    for name,lat,north,south in [('A',19.3,'eicc-sen-2022-north-a-core',None),('B',16,'eicc-sen-2022-north-b-reach','eicc-sen-2022-south-b-core'),('C',12,'eicc-sen-2022-north-c-core-band','eicc-sen-2022-south-c-core')]:
        phases=[]
        for label,id,months in [('northward',north,[2,3,4]),('southward',south,[10,11,12])]:
            r=refs[id] if id else None
            phases.append({'phase':label,'calendar_months':months,'source_reference_id':id,'native_source_metric':r['metric'] if r else None,'reported_point_m':r['approximate_value_m'] if r else None,'reported_band_m':r['range_m'] if r else None,'status':'scoped_source_descriptor' if r else 'no_section_specific_core_descriptor','is_monthly_time_series':False,'is_physical_thickness':False})
        sections.append({'section_name':name,'section_latitude_degrees_north':lat,'phases':phases,'automatic_core_depth_difference_m':None})
    return {'schema':'osw.eicc-seasonal-depth-comparison.v1','status':'TWO_PHASE_MEANS_WITH_NATIVE_METRICS_AND_SECTION_GAPS_PRESERVED','entity_id':'current:east-india-coastal','model_product':'Sen2022_ROMS_NIO','model_time_basis':document['projections'][-1]['model_time_basis'],'input_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in [OUTPUT,OPERATOR,source_file]},'sections':sections,'northward_conditional_envelope_id':document['projections'][-1]['id'],'regional_southward_reach_reference_id':'eicc-sen-2022-south-regional-reach','regional_reach_assigned_to_unknown_section_core':False,'whole_year_coverage':False,'monthly_interpolation_performed':False,'annual_depth_range_m':None,'physical_thickness_m':None,'query_ui_integration_performed':False,'runtime_changed':False,'full_goal_complete':False}
