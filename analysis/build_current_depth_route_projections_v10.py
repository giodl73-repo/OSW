"""Historical multi-record mooring connector with explicit weak-support gaps."""
import copy,csv,hashlib,io,json,math
from pathlib import Path
import build_current_depth_route_projections_v9 as previous
from build_current_depth_route_projections_v1 import route_legs,position

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-route-projection-operator-v10.json'
OUTPUT='research/current-depth-route-projections-v10.json'
CSV='research/current-depth-route-projections-v10.csv'
CASE_SHA256='887d2dbe043e0f215ac2e27e50d9ed5ebeee0bdb4b220d21d9caf7dc5922fd57'


def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def validate_case(case,references):
    if digest(case)!=CASE_SHA256:raise ValueError('Unreviewed historical Brazil mooring-connector contract')
    if [a['source_mooring_id'] for a in case['anchors']]!=['MARLIM','DFBS','C3','W333']:raise ValueError('Intervening DFBS site cannot be omitted')
    for a in case['anchors']:
        r=references[a['reference_id']]
        if r!=a['source_context'] or r['entity_id']!=case['entity_id'] or r['metric']!='reported_vertical_extent' or r['evidence_kind']!='published_mooring_mean_modal_reconstruction':raise ValueError('Source extent or reconstruction method changed')
        if a['nominal_lon_lat']!=r['mooring_lon_lat'] or a['reported_extent_m']!=r['approximate_value_m'] or a['record_month_bounds']!=r['source_record_month_bounds'] or a['source_mean_reliability']!=r['source_mean_reliability']:raise ValueError('Site, record, depth or reliability changed')
        if r['source_stratification_year_is_record_year'] is not False or r['common_record_period'] is not None or r['source_modal_fit']['number_of_gravest_dynamical_modes']!=5:raise ValueError('No common calendar period or raw-level interpolation established')


def period_context(a):
    return {'reference_id':a['reference_id'],'source_mooring_id':a['source_mooring_id'],'record_month_bounds':a['record_month_bounds'],'record_precision':'month','source_reported_record_days':a['source_context']['source_record_days'],'source_mean_reliability':a['source_mean_reliability']}


def descriptor_at_distance(anchors,distance):
    if not math.isfinite(distance):raise ValueError('Finite reference distance required')
    if not all(a['distance_km']<b['distance_km'] for a,b in zip(anchors,anchors[1:])):raise ValueError('Strictly ordered mooring locations required')
    for a in anchors:
        if abs(distance-a['distance_km'])<1e-8:return a['reported_extent_m'],[a],'source_reported_site_mean_extent'
    for a,b in zip(anchors,anchors[1:]):
        if a['distance_km']<distance<b['distance_km']:
            f=(distance-a['distance_km'])/(b['distance_km']-a['distance_km']);depth=a['reported_extent_m']+f*(b['reported_extent_m']-a['reported_extent_m'])
            return 50*math.floor(depth/50+.5),[a,b],'assumed_linear_between_different_site_record_means'
    return None,[],'unknown_outside_mooring_connector'


def project(case,eligibility):
    points=[a['nominal_lon_lat'] for a in case['anchors']];legs=route_legs(points)
    # Canonicalize derived geometry beyond the source's geographic precision;
    # serialization decimals are not a physical accuracy or error statement.
    distances=[round(leg[0],6) for leg in legs]+[round(legs[-1][1],6)]
    anchors=[dict(copy.deepcopy(a),distance_km=distance) for a,distance in zip(case['anchors'],distances)]
    sample_distances=set(distances)|{i*50. for i in range(1,math.floor(distances[-1]/50)+1)};samples=[]
    for distance in sorted(sample_distances):
        depth,used,status=descriptor_at_distance(anchors,distance);flagged=any(a['source_mean_reliability']=='source_low_statistical_significance' for a in used)
        anchor=next((a for a in anchors if a['distance_km']==distance),None)
        coordinate=list(anchor['nominal_lon_lat']) if anchor else [round(v,6) for v in position(legs,distance)]
        samples.append({'distance_along_reference_route_km':distance,'nominal_reference_connector_lon_lat':coordinate,'projected_depth_descriptor_m':depth,'depth_descriptor_excluding_flagged_mean_m':None if flagged else depth,'status':status,'source_reference_ids':[a['reference_id'] for a in used],'source_mooring_ids':[a['source_mooring_id'] for a in used],'source_record_periods':[period_context(a) for a in used],'common_record_period':None,'source_mean_reliability_flags':['includes_source_low_statistical_significance_DFBS'] if flagged else [],'depth_uncertainty_m':None,'physical_thickness_m':None,'volume_eligible':False})
    return {'id':case['id'],'entity_id':case['entity_id'],'status':'HISTORICAL_MOORING_MEAN_REFERENCE_CONNECTOR_SCENARIO','metric':'projected_historical_modal_mean_vertical_extent_descriptor','vertical_datum':'local_sea_surface_positive_down','coordinate_kind':'WGS84_cumulative_nominal_mooring_connector_distance','geometry_role':'nominal_source_mooring_connector_not_current_axis','route_id':'brazil-rocha2014-four-mooring-reference-connector','route_file':None,'reference_connector_length_km':distances[-1],'whole_current_length_replaced':False,'source_reference_ids':[a['reference_id'] for a in anchors],'anchors':anchors,'samples':samples,'source_record_periods':[period_context(a) for a in anchors],'common_record_period':None,'simultaneous_record_period_established':False,'source_time_basis':'Different mooring record means with one published five-mode reconstruction framework; not a common-period mean, dated synoptic section or continuous1991–2004 series.','model_product':None,'calendar_months':None,'phase_label':None,'descriptor_display_rounding_m':50,'interpolation_assumption':'Linear descriptor change in WGS84 cumulative nominal connector distance between all four published mooring sites. Geodesic connector is not a traced current axis. Every interpolated sample retains the adjacent records and source reliability.','filtered_descriptor_policy':'Exclude any sample relying on the explicitly low-significance DFBS mean. Leave those values unknown without bridging across the omitted site; filtering is not a confidence interval or a proof of greater accuracy.','source_scope_qualification':case['source_scope_qualification'],'physical_thickness_m':None,'uncertainty_m':None,'annual_range_m':None,'whole_current_representative':False,'eligibility':copy.deepcopy(eligibility),'full_goal_complete':False}


def build(root=ROOT):
    read=lambda p:json.loads((root/p).read_bytes());prior=previous.build(root)
    if prior!=read(previous.OUTPUT):raise ValueError('Prior eleven regional scenarios changed')
    op=read(OPERATOR);source=read(op['depth_register_file']);refs={r['id']:r for r in source['evidence']}
    if any(op['eligibility'].values()):raise ValueError('No whole-current physical admission')
    case=op['case'];validate_case(case,refs);projections=copy.deepcopy(prior['projections']);projections.append(project(case,op['eligibility']))
    records=[]
    for raw in source['records']:
        r=copy.deepcopy(next(r for r in prior['records'] if r['entity_id']==raw['entity_id']));r['depth_reference_ids']=list(raw['depth_reference_ids']);r['projection_ids']=[p['id'] for p in projections if p['entity_id']==r['entity_id']];r['projection_status']='regional_assumed_interpolation_available' if r['projection_ids'] else 'not_yet_projected';records.append(r)
    files=set(prior['input_sha256'])|{OPERATOR,op['depth_register_file'],previous.OUTPUT,previous.CSV,'analysis/build_current_depth_route_projections_v9.py'};owners=sum(bool(r['projection_ids']) for r in records)
    return {'schema':'osw.current-depth-route-projections.v10','status':'TWELFTH_REGIONAL_SCENARIO_WITH_HISTORICAL_BRAZIL_MOORING_MEANS','generator_file':'analysis/build_current_depth_route_projections_v10.py','generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_route_projections_v10.py').read_bytes()).hexdigest(),'input_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in sorted(files)},'previous_eleven_projection_records_preserved':projections[:11]==prior['projections'],'counts':{'catalog_identities':len(records),'identities_with_regional_projection_scenarios':owners,'identities_not_yet_projected':len(records)-owners,'regional_projection_scenarios':len(projections),'source_anchor_references':len({r for p in projections for r in p['source_reference_ids']}),'new_depth_measurements':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0,'regional_reference_geometry_volume_scenarios':2},'interpretation':'Twelve regional scenarios across eleven identities. Brazil Current source mooring means350/400/550/850m retain different records, modal reconstruction and weak DFBS support. Nominal mooring connector is not a physical axis or simultaneous depth transect.','regional_volume_scenario_file':prior['regional_volume_scenario_file'],'records':records,'projections':projections,'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}


def csv_bytes(document):
    compatible=copy.deepcopy(document);compatible['projections']=compatible['projections'][:11]
    reader=csv.DictReader(io.StringIO(previous.csv_bytes(compatible).decode('utf8')));columns=list(reader.fieldnames);rows=list(reader)
    columns+=['depth_descriptor_excluding_flagged_mean_m','source_mean_reliability_flags','source_mooring_ids','source_time_basis']
    p=document['projections'][-1]
    for sample in p['samples']:
        row={k:v for k,v in sample.items() if k in columns};row.update(projection_id=p['id'],entity_id=p['entity_id'],route_id=p['route_id'],geometry_role=p['geometry_role'],coordinate_kind=p['coordinate_kind'],metric=p['metric'],vertical_datum=p['vertical_datum'],longitude=sample['nominal_reference_connector_lon_lat'][0],latitude=sample['nominal_reference_connector_lon_lat'][1],source_reference_ids=json.dumps(sample['source_reference_ids'],separators=(',',':')),source_record_periods=json.dumps(sample['source_record_periods'],sort_keys=True,separators=(',',':')),source_mean_reliability_flags=json.dumps(sample['source_mean_reliability_flags'],separators=(',',':')),source_mooring_ids=json.dumps(sample['source_mooring_ids'],separators=(',',':')),source_time_basis=p['source_time_basis']);rows.append(row)
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows);return out.getvalue().encode('utf8')
