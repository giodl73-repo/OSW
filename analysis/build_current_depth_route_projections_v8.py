"""Source-path core geometry and a separately typed regional volume scenario."""
import copy,csv,hashlib,io,json,math
from pathlib import Path
import build_current_depth_route_projections_v7 as previous
from build_current_depth_route_projections_v6 import integrate_area

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-route-projection-operator-v8.json'
OUTPUT='research/current-depth-route-projections-v8.json'
CSV='research/current-depth-route-projections-v8.csv'
VOLUME_OUTPUT='research/current-regional-core-volume-scenarios-v2.json'
VOLUME_CSV='research/current-regional-core-volume-scenarios-v2.csv'
CASE_SHA256='94073b914cc8707085d618edeef3377bcf76e65a9d4217018633130b5797e495'


def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def validate_case(case,refs,geometry):
    if digest(case)!=CASE_SHA256:raise ValueError('Unreviewed same-mask source-path geometry contract')
    if geometry['pathway']!=case['pathway_context'] or geometry['BSO_included'] is not False:raise ValueError('Pathway or source operator scope changed')
    for a in case['anchors']:
        r=refs[a['reference_id']];g=next(g for g in geometry['sections'] if g['depth_reference_id']==r['id'])
        if r!=a['source_context'] or g!=a['geometry_context'] or digest(r)!=g['depth_reference_sha256']:raise ValueError('Source depth/area pairing changed')
        if r['entity_id']!=case['entity_id'] or r['metric']!='core_lower_boundary_depth' or r['climatology_years']!=[1993,2022] or r['core_definition']['ranking']!='decreasing_absolute_geostrophic_velocity' or r['core_definition']['fraction_of_mean_transport']!=.5 or r['core_definition']['excluded_surface_upper_depth_m']!=50:raise ValueError('Incompatible core, period or water-mass selection')
        if a['maximum_core_depth_m']!=r['approximate_value_m'] or a['cross_section_area_km2']!=g['source_core_area_km2']:raise ValueError('Depth and area must belong to the same static section mask')


def project(case,eligibility):
    anchors=copy.deepcopy(case['anchors']);length=case['reported_path_length_km'];samples=[]
    for distance in range(0,length+1,50):
        f=distance/length;depth=anchors[0]['maximum_core_depth_m']+f*(anchors[1]['maximum_core_depth_m']-anchors[0]['maximum_core_depth_m']);area=anchors[0]['cross_section_area_km2']+f*(anchors[1]['cross_section_area_km2']-anchors[0]['cross_section_area_km2'])
        at=0 if distance==0 else (1 if distance==length else None)
        samples.append({'distance_along_reported_source_path_km':distance,'distance_along_reference_route_km':None,'longitude':None,'latitude':None,'projected_depth_descriptor_m':anchors[at]['maximum_core_depth_m'] if at is not None else 10*math.floor(depth/10+.5),'projected_core_cross_section_area_km2':area,'status':'source_reported_section_anchor' if at is not None else 'assumed_linear_in_reported_source_path_distance','source_reference_ids':[anchors[at]['reference_id']] if at is not None else [a['reference_id'] for a in anchors],'source_section_name':anchors[at]['section_name'] if at is not None else None,'depth_uncertainty_m':None,'physical_thickness_m':None,'volume_eligible':False})
    return {'id':case['id'],'entity_id':case['entity_id'],'metric':'projected_static_transport_core_maximum_depth','status':'REGIONAL_SOURCE_PATH_MEAN_CORE_GEOMETRY_SCENARIO','vertical_datum':'local_sea_surface_positive_down','coordinate_kind':'reported_inter_section_path_distance_without_map_geometry','geometry_role':'source_reported_approximate_path_length_not_OSW_route','route_id':None,'route_file':None,'route_length_km':None,'source_reported_path_length_km':length,'source_path_length_is_approximate':True,'source_path_length_uncertainty_km':None,'source_reference_ids':[a['reference_id'] for a in anchors],'anchors':anchors,'samples':samples,'source_period_years':[1993,2022],'calendar_months':None,'model_product':None,'source_evidence_kind':'published_hydrographic_altimetry_static_mean_core','source_core_selection':'Atlantic Water salinity>=35.16g/kg; exclude upper50m; descending absolute geostrophic velocity until50% of section mean transport. Preserve section-specific lateral domains.','interpolation_assumption':'Linear maximum-mask-depth and section-area changes in an approximate750km source pathway. Positions and section orientations are not recovered; areas are assumed normal to that abstract pathway for regional extrusion.','source_geometry_bias':case['source_geometry_bias'],'regional_volume_scenario_id':case['regional_volume_scenario_id'],'eligibility':copy.deepcopy(eligibility),'physical_thickness_m':None,'uncertainty_m':None,'annual_range_m':None,'whole_current_representative':False,'full_goal_complete':False}


def build(root=ROOT):
    read=lambda p:json.loads((root/p).read_bytes());prior=previous.build(root)
    if prior!=read(previous.OUTPUT):raise ValueError('Prior nine regional profiles changed')
    op=read(OPERATOR);source=read(op['depth_register_file']);refs={r['id']:r for r in source['evidence']};geometry=read(op['geometry_source_file'])
    if hashlib.sha256((root/op['depth_register_file']).read_bytes()).hexdigest()!=geometry['depth_register_sha256']:raise ValueError('Geometry depth register pin changed')
    if any(op['eligibility'].values()):raise ValueError('No full-current physical admission')
    validate_case(op['case'],refs,geometry);projections=copy.deepcopy(prior['projections']);projections.append(project(op['case'],op['eligibility']))
    records=[]
    for raw in source['records']:
        row=copy.deepcopy(next(r for r in prior['records'] if r['entity_id']==raw['entity_id']));row['depth_reference_ids']=list(raw['depth_reference_ids']);row['projection_ids']=[p['id'] for p in projections if p['entity_id']==row['entity_id']];row['projection_status']='regional_assumed_interpolation_available' if row['projection_ids'] else 'not_yet_projected';records.append(row)
    files=set(prior['input_sha256'])|{OPERATOR,op['depth_register_file'],op['geometry_source_file'],previous.OUTPUT,previous.CSV,'analysis/build_current_depth_route_projections_v7.py','research/current-regional-core-volume-scenarios-v1.json','research/current-regional-core-volume-scenarios-v1.csv'}
    owners=sum(bool(r['projection_ids']) for r in records)
    return {'schema':'osw.current-depth-route-projections.v8','status':'TENTH_REGIONAL_PROFILE_WITH_MATCHED_SOURCE_PATH_CORE_GEOMETRY','generator_file':'analysis/build_current_depth_route_projections_v8.py','generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_route_projections_v8.py').read_bytes()).hexdigest(),'input_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in sorted(files)},'previous_nine_projection_records_preserved':projections[:9]==prior['projections'],'counts':{'catalog_identities':len(records),'identities_with_regional_projection_scenarios':owners,'identities_not_yet_projected':len(records)-owners,'regional_projection_scenarios':len(projections),'source_anchor_references':len({r for p in projections for r in p['source_reference_ids']}),'new_depth_measurements':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0,'regional_reference_geometry_volume_scenarios':2},'interpretation':'Ten regional profiles. NwASC Gimsøy–Bjørnøya mean-core depths/areas use an approximate reported750km pathway, without invented map geometry. A separate regional area-extrusion scenario is not a physical whole-current volume.','regional_volume_scenario_file':VOLUME_OUTPUT,'records':records,'projections':projections,'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}


def build_volume_scenarios(document,root=ROOT):
    read=lambda p:json.loads((root/p).read_bytes());op=read(OPERATOR);p=document['projections'][-1]
    if p!=project(op['case'],op['eligibility']):raise ValueError('Unreviewed depth/area profile supplied for volume')
    prior=read('research/current-regional-core-volume-scenarios-v1.json')
    for path,digest_value in prior['input_sha256'].items():
        if hashlib.sha256((root/path).read_bytes()).hexdigest()!=digest_value:raise ValueError('Previous EAC volume input changed')
    a=[{'reference_id':r['reference_id'],'distance_km':r['source_path_distance_km'],'cross_section_area_km2':r['cross_section_area_km2']} for r in p['anchors']];value,terms=integrate_area(a)
    geometry=read(op['geometry_source_file'])
    row={'id':p['regional_volume_scenario_id'],'entity_id':p['entity_id'],'projection_id':p['id'],'status':'PROVISIONAL_REGIONAL_SOURCE_PATH_MEAN_CORE_VOLUME_SCENARIO','volume_kind':'extrusion_of_source_reconstructed_static_mean_core_section_areas','scope':'Approximate Gimsøy–Bjørnøya source pathway only. Broad source NwASC continuation may overlap modern West Spitsbergen naming; no additive component or full-current volume.','source_reference_ids':p['source_reference_ids'],'source_period_years':[1993,2022],'source_reported_path_length_km':750,'source_path_length_is_approximate':True,'source_section_areas_km2':[8,17],'source_areas_are_approximate':True,'integration_formula':'V_km3 = (A_Gimsoy_km2 + A_Bjornoya_km2)/2 * reported_path_length_km','computed_integral_km3':value,'scenario_volume_km3':1000*math.floor(value/1000+.5),'display_rounding_km3':1000,'computational_terms':terms,'uncertainty_km3':None,'confidence_interval_km3':None,'orientation_assumption':'Section areas are treated as normal to the abstract source pathway for extrusion. Actual section/path angles and map geometry are not recovered.','shape_assumption':'Linearly connect the two source mask areas. Do not multiply source50km contextual box width by maximum depth or infer a uniform thickness.','temporal_interpretation':'Extrusion of static1993–2022 mean-core masks from uneven hydrographic/altimetry sampling; not a dated water volume or a mean of instantaneous core volumes.','source_area_geometry_bias':geometry['area_geometry_bias'],'source_heat_budget_box_context':geometry['source_heat_budget_box_context'],'source_heat_budget_box_used_for_integration':False,'source_box_difference_is_uncertainty':False,'whole_current_volume_estimate':False,'observed_water_volume':False,'mean_of_instantaneous_core_volumes':False,'physical_state_join_eligible':False,'global_total_eligible':False,'regional_scenario_admitted':True}
    files=[OUTPUT,OPERATOR,op['depth_register_file'],op['geometry_source_file'],'analysis/build_current_depth_route_projections_v8.py','research/current-regional-core-volume-scenarios-v1.json','research/current-regional-core-volume-scenarios-v1.csv']
    return {'schema':'osw.current-regional-core-volume-scenarios.v2','status':'TWO_EXPLICIT_REGIONAL_CORE_GEOMETRY_VOLUME_SCENARIOS','input_sha256':{f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in files},'previous_EAC_volume_record_preserved':True,'counts':{'regional_reference_geometry_scenarios':2,'whole_current_volume_estimates':0,'observed_water_volume_estimates':0},'records':copy.deepcopy(prior['records'])+[row],'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}


def csv_bytes(document):
    compatible=copy.deepcopy(document);compatible['projections']=compatible['projections'][:9]
    reader=csv.DictReader(io.StringIO(previous.csv_bytes(compatible).decode('utf8')));columns=list(reader.fieldnames);rows=list(reader)
    columns+=['distance_along_reported_source_path_km','source_period_years','source_path_length_is_approximate']
    p=document['projections'][-1]
    for sample in p['samples']:
        row={k:v for k,v in sample.items() if k in columns};row.update(projection_id=p['id'],entity_id=p['entity_id'],geometry_role=p['geometry_role'],coordinate_kind=p['coordinate_kind'],metric=p['metric'],vertical_datum=p['vertical_datum'],source_reference_ids=json.dumps(sample['source_reference_ids'],separators=(',',':')),source_period_years=json.dumps(p['source_period_years'],separators=(',',':')),source_path_length_is_approximate=True);rows.append(row)
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows);return out.getvalue().encode('utf8')


def volume_csv_bytes(document):
    fields=list(dict.fromkeys(k for r in document['records'] for k in r));out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');writer.writeheader()
    for row in document['records']:writer.writerow({k:json.dumps(v,sort_keys=True,separators=(',',':')) if isinstance(v,(dict,list)) else v for k,v in row.items()})
    return out.getvalue().encode('utf8')
