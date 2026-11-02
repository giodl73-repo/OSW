"""Add a source-latitude branch profile without inventing map coordinates."""
import copy,csv,hashlib,io,json,math
from pathlib import Path
import build_current_depth_route_projections_v6 as previous

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-route-projection-operator-v7.json'
OUTPUT='research/current-depth-route-projections-v7.json'
CSV='research/current-depth-route-projections-v7.csv'
CASE_SHA256='9d30188d208f2be50e6305fa58991248106a84c40e363f59a64f711899d28f57'


def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def validate_case(case,references):
    if digest(case)!=CASE_SHA256:raise ValueError('Unreviewed PCUC branch/section/latitude interpolation contract')
    for a in case['anchors']:
        r=references[a['reference_id']]
        if r!=a['source_context']:raise ValueError('Source context changed')
        if r['entity_id']!=case['entity_id'] or r['source_branch']!='peru_chile_undercurrent' or r['metric']!='lower_flow_boundary_depth' or r['section_latitude_degrees_north']!=a['section_latitude_degrees_north'] or r['approximate_value_m']!=a['approximate_depth_descriptor_m']:raise ValueError('Wrong branch, quantity or section')
        if r['boundary_definition']!={'kind':'maximum_depth_of_source_poleward_velocity_isotach','speed_m_s':0.02} or r['model_analysis_years']!=[3,10] or r['model_years_are_calendar_years'] is not False or r['potential_vorticity_prediction_used'] is not False:raise ValueError('Isotach depth cannot become PV prediction, thickness or calendar record')


def interpolate_latitude(anchors,latitude):
    if not math.isfinite(latitude):raise ValueError('Finite source-section latitude required')
    if not all(a['section_latitude_degrees_north']>b['section_latitude_degrees_north'] for a,b in zip(anchors,anchors[1:])):raise ValueError('Strictly ordered poleward source sections required')
    for a in anchors:
        if abs(latitude-a['section_latitude_degrees_north'])<1e-10:return a['approximate_depth_descriptor_m'],[a['reference_id']],'source_reported_section_anchor'
    for a,b in zip(anchors,anchors[1:]):
        north,south=a['section_latitude_degrees_north'],b['section_latitude_degrees_north']
        if south<latitude<north:
            f=(north-latitude)/(north-south);depth=a['approximate_depth_descriptor_m']+f*(b['approximate_depth_descriptor_m']-a['approximate_depth_descriptor_m'])
            return 10*math.floor(depth/10+.5),[a['reference_id'],b['reference_id']],'assumed_linear_in_source_section_latitude'
    return None,[],'unknown_outside_source_section_sequence'


def project(case,eligibility):
    anchors=copy.deepcopy(case['anchors']);latitudes=set(case['sample_latitudes_degrees_north'])|{a['section_latitude_degrees_north'] for a in anchors};samples=[]
    for latitude in sorted(latitudes,reverse=True):
        value,refs,status=interpolate_latitude(anchors,latitude)
        samples.append({'section_latitude_degrees_north':latitude,'projected_depth_descriptor_m':value,'status':status,'source_reference_ids':refs,'distance_along_reference_route_km':None,'longitude':None,'source_section_name':next((a['section_name'] for a in anchors if a['section_latitude_degrees_north']==latitude),None),'depth_uncertainty_m':None,'physical_thickness_m':None,'volume_eligible':False})
    return {'id':case['id'],'entity_id':case['entity_id'],'source_branch':case['source_branch'],'status':'REGIONAL_BRANCH_LATITUDE_INTERPOLATION_SCENARIO','metric':'projected_source_isotach_maximum_depth_by_latitude','vertical_datum':'local_sea_surface_positive_down','coordinate_kind':'source_cross_section_latitude_not_geographic_point','geometry_role':'named_branch_section_sequence_without_route_geometry','route_id':None,'route_file':None,'route_length_km':None,'source_reference_ids':[a['reference_id'] for a in anchors],'anchors':anchors,'samples':samples,'model_product':'Penven2005_ROMS_climatology','model_analysis_years':[3,10],'model_years_are_calendar_years':False,'model_time_basis':'Climatologically forced annual mean from simulation years3–10; no calendar-year mapping.','calendar_months':None,'interpolation_coordinate':'source_section_latitude_degrees_north','interpolation_assumption':'Piecewise linear in latitude between adjacent source section depths, with10m display rounding. No along-distance linearity, full-flow bottom or continuous physical jet reconstruction claimed.','supported_section_latitude_interval_degrees_north':[-18.6,-6],'unknown_outside_interval':True,'whole_current_representative':False,'uncertainty_m':None,'annual_range_m':None,'physical_thickness_m':None,'source_scope_qualification':case['source_scope_qualification'],'eligibility':copy.deepcopy(eligibility),'full_goal_complete':False}


def build(root=ROOT):
    read=lambda p:json.loads((root/p).read_bytes());prior=previous.build(root)
    if prior!=read(previous.OUTPUT):raise ValueError('Prior eight regional profiles no longer reproduce')
    operator=read(OPERATOR);source=read(operator['depth_register_file']);refs={r['id']:r for r in source['evidence']}
    if any(operator['eligibility'].values()):raise ValueError('No whole-current or physical geometry admission')
    case=operator['case'];validate_case(case,refs);projections=copy.deepcopy(prior['projections']);projections.append(project(case,operator['eligibility']))
    records=[]
    for raw in source['records']:
        row=copy.deepcopy(next(r for r in prior['records'] if r['entity_id']==raw['entity_id']));row['depth_reference_ids']=list(raw['depth_reference_ids']);row['projection_ids']=[p['id'] for p in projections if p['entity_id']==row['entity_id']];row['projection_status']='regional_assumed_interpolation_available' if row['projection_ids'] else 'not_yet_projected';records.append(row)
    files=set(prior['input_sha256'])|{OPERATOR,operator['depth_register_file'],previous.OUTPUT,previous.CSV,'analysis/build_current_depth_route_projections_v6.py',prior['regional_volume_scenario_file']}
    owners=sum(bool(r['projection_ids']) for r in records)
    return {'schema':'osw.current-depth-route-projections.v7','status':'NINTH_REGIONAL_PROFILE_WITH_LATITUDE_ONLY_BRANCH_COORDINATE','generator_file':'analysis/build_current_depth_route_projections_v7.py','generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_route_projections_v7.py').read_bytes()).hexdigest(),'input_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in sorted(files)},'previous_eight_projection_records_preserved':projections[:8]==prior['projections'],'counts':{'catalog_identities':len(records),'identities_with_regional_projection_scenarios':owners,'identities_not_yet_projected':len(records)-owners,'regional_projection_scenarios':len(projections),'source_anchor_references':len({r for p in projections for r in p['source_reference_ids']}),'new_depth_measurements':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0,'regional_reference_geometry_volume_scenarios':1},'interpretation':'Nine regional profiles. New Peru–Chile Undercurrent branch scenario interpolates six source2cm/s section maxima in latitude, with longitude and along-route distance explicitly unknown. It is not a surface Humboldt jet, a whole-system depth, seasonal envelope, thickness or volume.','regional_volume_scenario_file':prior['regional_volume_scenario_file'],'records':records,'projections':projections,'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}


def csv_bytes(document):
    compatible=copy.deepcopy(document);compatible['projections']=compatible['projections'][:8]
    reader=csv.DictReader(io.StringIO(previous.csv_bytes(compatible).decode('utf8')));columns=list(reader.fieldnames);rows=list(reader)
    columns+=['coordinate_kind','source_branch','source_section_name','section_latitude_degrees_north','interpolation_coordinate','model_analysis_years','model_years_are_calendar_years']
    p=document['projections'][-1]
    for sample in p['samples']:
        row={k:v for k,v in sample.items() if k in columns}
        row.update(projection_id=p['id'],entity_id=p['entity_id'],route_id=None,geometry_role=p['geometry_role'],metric=p['metric'],vertical_datum=p['vertical_datum'],model_product=p['model_product'],model_time_basis=p['model_time_basis'],model_analysis_years=json.dumps(p['model_analysis_years'],separators=(',',':')),model_years_are_calendar_years=False,coordinate_kind=p['coordinate_kind'],source_branch=p['source_branch'],interpolation_coordinate=p['interpolation_coordinate'],latitude=sample['section_latitude_degrees_north'],longitude=None,source_reference_ids=json.dumps(sample['source_reference_ids'],separators=(',',':')))
        rows.append(row)
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows)
    return out.getvalue().encode('utf8')
