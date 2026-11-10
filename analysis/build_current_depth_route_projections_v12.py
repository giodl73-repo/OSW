"""Gap-preserving regional dated model depth and layer-span projections."""
import copy
import csv
import hashlib
import io
import json
import math
from pathlib import Path
from pyproj import Geod

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-route-projection-operator-v12.json'
OUTPUT='research/current-depth-route-projections-v12.json'
CSV='research/current-depth-route-projections-v12.csv'
GENERATOR='analysis/build_current_depth_route_projections_v12.py'
GEOD=Geod(ellps='WGS84')
QUANTITIES=['model_upper_depth_m','model_lower_depth_m','model_layer_thickness_m']


def valid_number(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) and value>=0


def validate_anchors(anchors):
    if len(anchors)<2 or any(not valid_number(a['distance_km']) for a in anchors):raise ValueError('Complete ordered finite reference anchors required')
    if len({a['id'] for a in anchors})!=len(anchors):raise ValueError('Duplicate reference anchor')
    if any(a['distance_km']>=b['distance_km'] for a,b in zip(anchors,anchors[1:])):raise ValueError('Strict original anchor order required')
    for a in anchors:
        if a['lower_projection_eligible'] and not valid_number(a['model_lower_depth_m']):raise ValueError('Lower projection eligibility requires a resolved model depth')
        if a['layer_projection_eligible']:
            upper,lower,thickness=(a[q] for q in QUANTITIES)
            if (not a['lower_projection_eligible'] or not all(valid_number(v) for v in [upper,lower,thickness])
                or not upper<lower or not math.isclose(thickness,lower-upper,rel_tol=0,abs_tol=1e-8)):
                raise ValueError('Paired model layer span must retain both boundaries and difference')


def interpolate(anchors,distance):
    validate_anchors(anchors)
    if not math.isfinite(distance):raise ValueError('Finite reference distance required')
    for a in anchors:
        if abs(a['distance_km']-distance)<1e-8:
            values={q:a[q] if a['lower_projection_eligible'] and (q=='model_lower_depth_m' or a['layer_projection_eligible']) else None for q in QUANTITIES}
            return values,[a],('source_model_descriptor_at_reference_anchor' if a['lower_projection_eligible'] else 'unknown_at_blocked_reference_anchor')
    for a,b in zip(anchors,anchors[1:]):
        if a['distance_km']<distance<b['distance_km']:
            lower=a['lower_projection_eligible'] and b['lower_projection_eligible']
            layer=a['layer_projection_eligible'] and b['layer_projection_eligible']
            fraction=(distance-a['distance_km'])/(b['distance_km']-a['distance_km'])
            values={q:a[q]+fraction*(b[q]-a[q]) if lower and (q=='model_lower_depth_m' or layer) else None for q in QUANTITIES}
            return values,[a,b],('assumed_linear_between_adjacent_model_descriptors' if lower else 'unknown_between_blocked_reference_anchors')
    return {q:None for q in QUANTITIES},[],'unknown_outside_regional_reference_geometry'


def reference_position(anchors,distance):
    for a in anchors:
        if abs(a['distance_km']-distance)<1e-8:return list(a['reference_lon_lat'])
    for a,b in zip(anchors,anchors[1:]):
        if a['distance_km']<distance<b['distance_km']:
            fraction=(distance-a['distance_km'])/(b['distance_km']-a['distance_km'])
            heading,_,metres=GEOD.inv(*a['reference_lon_lat'],*b['reference_lon_lat'])
            lon,lat,_=GEOD.fwd(*a['reference_lon_lat'],heading,metres*fraction)
            return [round(lon,6),round(lat,6)]
    return None


def paired_anchor(anchor_id,layer,eligible,layer_eligible,reasons,**context):
    return dict(id=anchor_id,model_upper_depth_m=layer['upper_depth_m'] if layer else None,
                model_lower_depth_m=layer['lower_depth_m'] if layer else None,
                model_layer_thickness_m=layer['layer_thickness_m'] if layer else None,
                source_model_connected_layer=copy.deepcopy(layer),lower_projection_eligible=bool(eligible),
                layer_projection_eligible=bool(layer_eligible),projection_block_reasons=list(reasons),**context)


def eac_cases(source,model,op):
    if source['entity_context']!='current:east-australian' or model['entity_id']!='current:east-australian':raise ValueError('EAC source identity changed')
    expected={(t,i) for t in op['eac_dates'] for i in range(7)}
    nodes={};cases=[]
    for index,node in enumerate(source['nodes']):
        key=node['source_date'],node['route_vertex_index']
        if key in nodes:raise ValueError('Duplicate EAC date/vertex')
        nodes[key]=index,node
    if set(nodes)!=expected:raise ValueError('Complete EAC date/vertex keys required')
    for day in op['eac_dates']:
        anchors=[]
        for vertex in range(7):
            index,node=nodes[day,vertex];pointer=node['source_pointers']['model']
            model_index=int(pointer.split('/')[-1]);raw=model['samples'][model_index]
            if (pointer!='/samples/'+str(model_index) or raw['snapshot_time_utc']!=day+'T00:00:00Z'
                or raw['route_vertex_index']!=vertex or raw['reference_distance_km']!=node['reference_distance_km']
                or raw['editorial_lon_lat']!=node['editorial_lon_lat']
                or raw['selected_profile_index']!=node['frozen_model_selected_profile_index']):raise ValueError('EAC source model key/selection/geometry mismatch')
            layer=node['model_primary_connected_layer'];selected=raw['selected_profile_index']
            if layer and (layer['threshold_m_s']!=.05 or layer['lower_depth_m']!=node['model_primary_lower_isotach_depth_m']):raise ValueError('EAC primary threshold mismatch')
            if selected is not None and raw['sampled_profiles'][selected]['sampled_lon_lat']!=node['selected_model_node_lon_lat']:raise ValueError('EAC selected source position mismatch')
            anchors.append(paired_anchor(f'eac-{day}-vertex-{vertex}',layer,node['conditional_lower_depth_projection_node_eligible'],node['conditional_thickness_projection_node_eligible'],node['projection_block_reasons'],
                source_vertex_index=vertex,distance_km=node['reference_distance_km'],reference_lon_lat=node['editorial_lon_lat'],
                selected_model_node_lon_lat=node['selected_model_node_lon_lat'],source_horizontal_selection_status=node['model_horizontal_selection_status'],
                source_profile_refs=[op['eac_join_file']+'#/nodes/'+str(index)],
                source_model_profile_ref=op['eac_model_file']+'#'+pointer+'/sampled_profiles/'+str(selected) if selected is not None else None,
                source_component_bearing_degrees_true=raw['downstream_reference_bearing_degrees_true'],source_surface_screen=copy.deepcopy(node['surface_screen'])))
        cases.append({'entity_id':'current:east-australian','snapshot_time_utc':day+'T00:00:00Z','primary_threshold_m_s':.05,'anchors':anchors,
                      'geometry_role':'frozen_editorial_reference_corridor_not_observed_current_axis',
                      'route_id':'east-australian-hycom2022-reference-corridor','route_file':op['eac_reference_route_file'],
                      'source_time_basis':'HYCOM00Z instantaneous2022 snapshot; eligibility also retains multi-day mapped surface component screen. Moorings remain regional context, not depth fills.',
                      'projection_gate':'Frozen EAC join gate: interior model maximum, resolved primary5cm/s lower contour and positive retained second-product surface component. Gate is not physical current validation.'})
    return cases


def kuroshio_cases(source,op):
    if source['entity_id']!='current:kuroshio':raise ValueError('Kuroshio source identity changed')
    keyed={};cases=[]
    for index,row in enumerate(source['samples']):
        key=row['snapshot_time_utc'],row['latitude_gate']
        if key in keyed:raise ValueError('Duplicate Kuroshio date/gate')
        keyed[key]=index,row
    expected={(t,lat) for t in op['kuroshio_times_utc'] for lat in op['kuroshio_latitude_gates']}
    if set(keyed)!=expected:raise ValueError('Complete Kuroshio original date/gate keys required')
    for stamp in op['kuroshio_times_utc']:
        anchors=[];distance=0.;previous=None
        for latitude in op['kuroshio_latitude_gates']:
            index,row=keyed[stamp,latitude]
            # Geometry gaps require a new operator; never silently remove a source gate.
            if row['source_axis_gate'] is None:raise ValueError('Reference gate position unavailable; no gap-skipping connector permitted')
            position=row['source_axis_gate']['point']
            if previous is not None:
                metres=GEOD.inv(*previous,*position)[2]
                if not math.isfinite(metres) or metres<=0:raise ValueError('Distinct finite gate positions required')
                distance+=metres/1000
            previous=position
            selected=row.get('selected_profile_index');layers=row.get('selected_profile_threshold_layers',[])
            matches=[layer for layer in layers if layer['threshold_m_s']==.1]
            if selected is not None and len(matches)!=1:raise ValueError('Exactly one frozen10cm/s primary layer required')
            layer=matches[0] if matches else None
            reasons=[]
            if not row['axis_geometry_query_eligible']:reasons.append('source_axis_geometry_unresolved')
            if row.get('horizontal_selection_status')!='interior_sampled_maximum_not_independently_validated_axis':reasons.append('model_maximum_at_window_edge_or_no_node')
            if not layer or layer['lower_depth_m'] is None:reasons.append('primary10cms_lower_boundary_unresolved')
            lower=not reasons;thick=lower and layer['layer_thickness_m'] is not None
            if layer and layer['lower_depth_m']!=row['primary_core_lower_descriptor']['lower_isotach_depth_m']:raise ValueError('Kuroshio frozen primary depth mismatch')
            anchors.append(paired_anchor(f'kuroshio-{stamp[:10]}-gate-{latitude:g}',layer,lower,thick,reasons,
                source_latitude_gate=latitude,distance_km=round(distance,6),reference_lon_lat=position,
                selected_model_node_lon_lat=row['sampled_profiles'][selected]['sampled_lon_lat'] if selected is not None else None,
                source_horizontal_selection_status=row.get('horizontal_selection_status'),
                source_profile_refs=[op['kuroshio_source_file']+'#/samples/'+str(index)],
                source_model_profile_ref=op['kuroshio_source_file']+'#/samples/'+str(index)+'/sampled_profiles/'+str(selected) if selected is not None else None,
                source_component_bearing_degrees_true=row['locked_reference_bearing_degrees_true'],
                source_axis_case_id=row['source_axis_case_id'],source_axis_report_pointer=row['source_axis_case_pointer']))
        cases.append({'entity_id':'current:kuroshio','snapshot_time_utc':stamp,'primary_threshold_m_s':.1,'anchors':anchors,
                      'geometry_role':'shortest_geodesic_connector_between_daily_model_axis_gates_not_observed_current_axis',
                      'route_id':'kuroshio-model-axis-gates-'+stamp[:10]+'-connector','route_file':None,
                      'source_time_basis':'HYCOM2024 instantaneous00Z velocities, sampled around same-calendar-day Wang GLORYS-derived nominal0.49m axis geometry. Daily geometry and instantaneous velocity are not simultaneous or independent observations.',
                      'projection_gate':'Interior fixed-window selected model maximum and resolved primary10cm/s lower contour; no independent named-current-axis or surface-velocity validation.'})
    return cases


def project(case,op):
    anchors=case['anchors'];validate_anchors(anchors)
    segments=[]
    for a,b in zip(anchors,anchors[1:]):
        lower=a['lower_projection_eligible'] and b['lower_projection_eligible']
        thick=a['layer_projection_eligible'] and b['layer_projection_eligible']
        segments.append({'source_anchor_ids':[a['id'],b['id']],'reference_distance_interval_km':[a['distance_km'],b['distance_km']],
                         'projection_status':'conditional_linear_reference_geometry' if lower else 'gap_no_projection',
                         'model_layer_span_projection_eligible':bool(thick),
                         'endpoint_block_reasons':[a['projection_block_reasons'],b['projection_block_reasons']],
                         'physical_current_continuity_established':False,'volume_eligible':False})
    distances={a['distance_km'] for a in anchors}|{i*50. for i in range(1,math.floor(anchors[-1]['distance_km']/50)+1)}
    samples=[]
    for distance in sorted(distances):
        values,used,status=interpolate(anchors,distance);position=reference_position(anchors,distance)
        samples.append({'distance_along_reference_route_km':distance,'nominal_reference_connector_lon_lat':position,
                        'computed_model_upper_depth_m':round(values['model_upper_depth_m'],6) if values['model_upper_depth_m'] is not None else None,
                        'computed_model_lower_depth_m':round(values['model_lower_depth_m'],6) if values['model_lower_depth_m'] is not None else None,
                        'computed_model_layer_thickness_m':round(values['model_layer_thickness_m'],6) if values['model_layer_thickness_m'] is not None else None,
                        'projected_depth_descriptor_m':10*round(values['model_lower_depth_m']/10) if values['model_lower_depth_m'] is not None else None,
                        'source_anchor_ids':[a['id'] for a in used],
                        'source_profile_refs':list(dict.fromkeys(ref for a in used for ref in a['source_profile_refs'])),
                        'source_reference_ids':[],'status':status,'depth_uncertainty_m':None,'physical_thickness_m':None,'volume_eligible':False})
    return dict(copy.deepcopy(case),id=case['entity_id'].split(':')[1]+'-hycom-'+case['snapshot_time_utc'][:10]+'-regional-depth-v1',
                status='REGIONAL_DATED_MODEL_DEPTH_AND_LAYER_SPAN_REFERENCE_SCENARIO',
                metric='projected_signed_component_lower_isotach_depth_and_model_layer_span',
                vertical_datum='local_sea_surface_positive_down',model_layer_thickness_datum='not_applicable_thickness_distance',
                coordinate_kind='distance_along_declared_regional_reference_geometry_not_measured_current_length',
                reference_connector_length_km=anchors[-1]['distance_km'],source_reference_ids=[],
                source_profile_refs=list(dict.fromkeys(ref for a in anchors for ref in a['source_profile_refs'])),
                segments=segments,samples=samples,interpolation_assumption=op['interpolation_assumption'],
                physical_thickness_m=None,uncertainty_m=None,annual_range_m=None,whole_current_length_replaced=False,
                whole_current_representative=False,model_products_are_statistically_independent=False,
                descriptor_display_rounding_m=10,derived_serialization_decimals=6,serialization_decimals_are_physical_accuracy=False,
                eligibility=copy.deepcopy(op['eligibility']),full_goal_complete=False)


def build(root=ROOT):
    read=lambda p:json.loads((root/p).read_bytes())
    op=read(OPERATOR)
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256((root/f).read_bytes()).hexdigest()!=pin:raise ValueError('Frozen projection source changed: '+f)
    if any(op['eligibility'].values()):raise ValueError('No physical promotion')
    prior=read(op['previous_projection_file']);register=read(op['depth_register_file'])
    cases=eac_cases(read(op['eac_join_file']),read(op['eac_model_file']),op)+kuroshio_cases(read(op['kuroshio_source_file']),op)
    additions=[project(case,op) for case in cases]
    projections=copy.deepcopy(prior['projections'])+additions;records=copy.deepcopy(prior['records'])
    owned={r['entity_id']:r['depth_reference_ids'] for r in register['records']}
    for row in records:
        row['depth_reference_ids']=owned[row['entity_id']][:]
        row['projection_ids']=[p['id'] for p in projections if p['entity_id']==row['entity_id']]
        row['projection_status']='regional_assumed_interpolation_available' if row['projection_ids'] else 'not_yet_projected'
    owners=sum(bool(r['projection_ids']) for r in records)
    return {'schema':'osw.current-depth-route-projections.v12','status':'REGIONAL_DATED_EAC_AND_KUROSHIO_MODEL_DEPTH_SCENARIOS',
            'generator_file':GENERATOR,'generator_sha256':hashlib.sha256((root/GENERATOR).read_bytes()).hexdigest(),
            'input_sha256':dict(op['input_sha256'],**{OPERATOR:hashlib.sha256((root/OPERATOR).read_bytes()).hexdigest()}),
            'previous25_projection_records_preserved':projections[:25]==prior['projections'],
            'counts':{'catalog_identities':len(records),'identities_with_regional_projection_scenarios':owners,
                      'identities_not_yet_projected':len(records)-owners,'regional_projection_scenarios':len(projections),
                      'source_anchor_references':prior['counts']['source_anchor_references'],
                      'new_model_profile_anchors':sum(len(p['anchors']) for p in additions),
                      'new_projection_eligible_source_nodes':sum(a['lower_projection_eligible'] for p in additions for a in p['anchors']),
                      'new_conditional_adjacent_segments':sum(s['projection_status']!='gap_no_projection' for p in additions for s in p['segments']),
                      'new_gap_segments':sum(s['projection_status']=='gap_no_projection' for p in additions for s in p['segments']),
                      'new_depth_measurements':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0,
                      'regional_reference_geometry_volume_scenarios':prior['counts']['regional_reference_geometry_volume_scenarios']},
            'interpretation':op['interpretation'],'source_definition_clarifications':[register['source_definition_clarification']],
            'regional_volume_scenario_file':prior['regional_volume_scenario_file'],
            'fitted_phase_depth_sample_spans':copy.deepcopy(prior['fitted_phase_depth_sample_spans']),
            'records':records,'projections':projections,'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}


def csv_bytes(document,root=ROOT):
    op=json.loads((root/OPERATOR).read_bytes());reader=csv.DictReader(io.StringIO((root/op['previous_projection_csv']).read_text(encoding='utf8')))
    columns=list(reader.fieldnames);rows=list(reader)
    for p in document['projections'][25:]:
        for sample in p['samples']:
            row=copy.deepcopy(sample);position=row.pop('nominal_reference_connector_lon_lat')
            row.update(projection_id=p['id'],entity_id=p['entity_id'],route_id=p['route_id'],geometry_role=p['geometry_role'],
                       metric=p['metric'],vertical_datum=p['vertical_datum'],snapshot_time_utc=p['snapshot_time_utc'],
                       longitude=position[0],latitude=position[1],primary_threshold_m_s=p['primary_threshold_m_s'],
                       model_layer_thickness_datum=p['model_layer_thickness_datum'],source_time_basis=p['source_time_basis'],
                       interpolation_assumption=p['interpolation_assumption'])
            for k,v in row.items():
                if k not in columns:columns.append(k)
                if isinstance(v,(list,dict)):row[k]=json.dumps(v,ensure_ascii=False,separators=(',',':'))
            rows.append(row)
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows)
    return out.getvalue().encode('utf8')


def main():
    result=build();out=Path('current-depth-route-projections-v12');out.mkdir(exist_ok=True)
    (out/'projections.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf8')
    (out/'projections.csv').write_bytes(csv_bytes(result));print(json.dumps(result['counts']))


if __name__=='__main__':main()
