"""Regional Atlantic model depth scenarios from frozen three-current profiles."""
import copy
import csv
import hashlib
import io
import json
from pathlib import Path
from build_current_depth_route_projections_v12 import paired_anchor, project

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-route-projection-operator-v13.json'
OUTPUT='research/current-depth-route-projections-v13.json'
CSV='research/current-depth-route-projections-v13.csv'
GENERATOR='analysis/build_current_depth_route_projections_v13.py'


def current_cases(source,source_file,op):
    case=source['current_case'];entity=case['entity_id']
    if entity!=source['entity_id'] or entity!='current:'+case['current_id']:raise ValueError('Exact source current owner required')
    keyed={}
    for index,row in enumerate(source['samples']):
        key=row['snapshot_time_utc'],row['route_vertex_index']
        if key in keyed:raise ValueError('Duplicate source current date/vertex')
        keyed[key]=index,row
    expected={(t,i) for t in op['snapshot_times_utc'] for i in range(case['expected_route_vertices'])}
    if set(keyed)!=expected:raise ValueError('All original source date/vertex cases required')
    cases=[]
    for stamp in op['snapshot_times_utc']:
        anchors=[]
        for vertex in range(case['expected_route_vertices']):
            index,row=keyed[stamp,vertex];selected=row['selected_profile_index']
            matches=[r for r in row['selected_profile_threshold_layers'] if r['threshold_m_s']==case['primary_threshold_m_s']]
            if selected is not None and len(matches)!=1:raise ValueError('One same-node primary threshold layer required')
            layer=matches[0] if matches else None
            if selected is not None and row['primary_core_lower_descriptor']['threshold_m_s']!=case['primary_threshold_m_s']:raise ValueError('Frozen source primary threshold mismatch')
            if layer and layer['lower_depth_m']!=row['primary_core_lower_descriptor']['lower_isotach_depth_m']:raise ValueError('Frozen source primary lower depth mismatch')
            reasons=[]
            if row['horizontal_selection_status']!='interior_sampled_maximum_not_independently_validated_axis':reasons.append('window_edge_or_no_qualifying_model_node')
            if not layer or layer['lower_depth_m'] is None:reasons.append('primary_lower_boundary_unresolved')
            lower=not reasons;thick=lower and layer['layer_thickness_m'] is not None
            anchors.append(paired_anchor(case['current_id']+'-'+stamp[:10]+'-vertex-'+str(vertex),layer,lower,thick,reasons,
                source_vertex_index=vertex,distance_km=row['reference_distance_km'],reference_lon_lat=row['editorial_lon_lat'],
                selected_model_node_lon_lat=row['sampled_profiles'][selected]['sampled_lon_lat'] if selected is not None else None,
                source_native_longitude_degrees_east=row['sampled_profiles'][selected]['native_source_longitude_degrees_east'] if selected is not None else None,
                source_horizontal_selection_status=row['horizontal_selection_status'],source_profile_refs=[source_file+'#/samples/'+str(index)],
                source_model_profile_ref=source_file+'#/samples/'+str(index)+'/sampled_profiles/'+str(selected) if selected is not None else None,
                source_component_bearing_degrees_true=row['locked_reference_bearing_degrees_true']))
        cases.append({'entity_id':entity,'snapshot_time_utc':stamp,'primary_threshold_m_s':case['primary_threshold_m_s'],'anchors':anchors,
            'geometry_role':'frozen_editorial_reference_corridor_not_observed_current_axis',
            'route_id':case['current_id']+'-hycom2022-reference-corridor','route_file':source['route_file'],
            'source_time_basis':'HYCOM2022 instantaneous00Z velocity sampled around an undated editorial corridor, not monthly mean or independently observed current axis.',
            'projection_gate':'Interior fixed-window selected model maximum and resolved per-object primary contour. No second-product surface screen or independent current-axis validation.',
            'secondary_product_surface_screen_performed':False,'source_current_scope':case['scope']})
    return cases


def build(root=ROOT):
    read=lambda p:json.loads((root/p).read_bytes());op=read(OPERATOR)
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256((root/f).read_bytes()).hexdigest()!=pin:raise ValueError('Frozen source changed: '+f)
    if any(op['eligibility'].values()):raise ValueError('No physical promotion')
    prior=read(op['previous_projection_file']);register=read(op['depth_register_file'])
    cases=[]
    for f in op['current_source_files']:cases.extend(current_cases(read(f),f,op))
    additions=[project(case,op) for case in cases];projections=copy.deepcopy(prior['projections'])+additions
    records=copy.deepcopy(prior['records']);owned={r['entity_id']:r['depth_reference_ids'] for r in register['records']}
    for row in records:
        row['depth_reference_ids']=owned[row['entity_id']][:]
        row['projection_ids']=[r['id'] for r in projections if r['entity_id']==row['entity_id']]
        row['projection_status']='regional_assumed_interpolation_available' if row['projection_ids'] else 'not_yet_projected'
    owners=sum(bool(r['projection_ids']) for r in records)
    return {'schema':'osw.current-depth-route-projections.v13','status':'REGIONAL_ATLANTIC_THREE_CURRENT_MODEL_DEPTH_SCENARIOS',
        'generator_file':GENERATOR,'generator_sha256':hashlib.sha256((root/GENERATOR).read_bytes()).hexdigest(),
        'input_sha256':dict(op['input_sha256'],**{OPERATOR:hashlib.sha256((root/OPERATOR).read_bytes()).hexdigest()}),
        'previous29_projection_records_preserved':projections[:29]==prior['projections'],
        'counts':{'catalog_identities':len(records),'identities_with_regional_projection_scenarios':owners,'identities_not_yet_projected':len(records)-owners,
            'regional_projection_scenarios':len(projections),'source_anchor_references':prior['counts']['source_anchor_references'],
            'new_model_profile_anchors':sum(len(p['anchors']) for p in additions),
            'new_projection_eligible_source_nodes':sum(a['lower_projection_eligible'] for p in additions for a in p['anchors']),
            'new_conditional_adjacent_segments':sum(s['projection_status']!='gap_no_projection' for p in additions for s in p['segments']),
            'new_gap_segments':sum(s['projection_status']=='gap_no_projection' for p in additions for s in p['segments']),
            'new_depth_measurements':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0,
            'regional_reference_geometry_volume_scenarios':prior['counts']['regional_reference_geometry_volume_scenarios']},
        'interpretation':op['interpretation'],'source_definition_clarifications':copy.deepcopy(prior['source_definition_clarifications']),
        'regional_volume_scenario_file':prior['regional_volume_scenario_file'],'fitted_phase_depth_sample_spans':copy.deepcopy(prior['fitted_phase_depth_sample_spans']),
        'records':records,'projections':projections,'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}


def csv_bytes(document,root=ROOT):
    op=json.loads((root/OPERATOR).read_bytes());reader=csv.DictReader(io.StringIO((root/op['previous_projection_csv']).read_text(encoding='utf8')))
    columns=list(reader.fieldnames);rows=list(reader)
    for p in document['projections'][29:]:
        for sample in p['samples']:
            row=copy.deepcopy(sample);position=row.pop('nominal_reference_connector_lon_lat')
            row.update(projection_id=p['id'],entity_id=p['entity_id'],route_id=p['route_id'],geometry_role=p['geometry_role'],
                metric=p['metric'],vertical_datum=p['vertical_datum'],snapshot_time_utc=p['snapshot_time_utc'],
                longitude=position[0],latitude=position[1],primary_threshold_m_s=p['primary_threshold_m_s'],
                model_layer_thickness_datum=p['model_layer_thickness_datum'],source_time_basis=p['source_time_basis'],interpolation_assumption=p['interpolation_assumption'])
            for k,v in row.items():
                if k not in columns:columns.append(k)
                if isinstance(v,(list,dict)):row[k]=json.dumps(v,ensure_ascii=False,separators=(',',':'))
            rows.append(row)
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows)
    return out.getvalue().encode('utf8')


def main():
    result=build();out=Path('current-depth-route-projections-v13');out.mkdir(exist_ok=True)
    (out/'projections.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf8')
    (out/'projections.csv').write_bytes(csv_bytes(result));print(json.dumps(result['counts']))


if __name__=='__main__':main()
