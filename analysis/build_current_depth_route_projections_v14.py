"""Regional supported projections with fully blocked reference cases separated."""
import copy
import csv
import hashlib
import io
import json
from pathlib import Path
from build_current_depth_route_projections_v13 import current_cases
from build_current_depth_route_projections_v12 import project

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-route-projection-operator-v14.json'
OUTPUT='research/current-depth-route-projections-v14.json'
CSV='research/current-depth-route-projections-v14.csv'
UNRESOLVED_CSV='research/current-depth-unresolved-reference-cases-v1.csv'
GENERATOR='analysis/build_current_depth_route_projections_v14.py'


def classify(case):
    if any(a['lower_projection_eligible'] for a in case['anchors']):
        return 'supported_regional_model_descriptor_scenario'
    if any(s['computed_model_lower_depth_m'] is not None for s in case['samples']):raise ValueError('Blocked case has a fabricated projected value')
    return 'all_reference_anchors_blocked_no_supported_projection'


def build(root=ROOT):
    read=lambda p:json.loads((root/p).read_bytes());op=read(OPERATOR)
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256((root/f).read_bytes()).hexdigest()!=pin:raise ValueError('Frozen source changed: '+f)
    if any(op['eligibility'].values()):raise ValueError('No physical promotion')
    prior=read(op['previous_projection_file']);register=read(op['depth_register_file'])
    additions=[];blocked=[];all_new=[]
    for file in op['current_source_files']:
        for raw in current_cases(read(file),file,op):
            case=project(raw,op);case['reference_case_status']=classify(case);all_new.append(case)
            if case['reference_case_status']=='supported_regional_model_descriptor_scenario':additions.append(case)
            else:blocked.append(case)
    projections=copy.deepcopy(prior['projections'])+additions
    unresolved=copy.deepcopy(prior.get('unresolved_reference_cases',[]))+blocked
    records=copy.deepcopy(prior['records']);owned={r['entity_id']:r['depth_reference_ids'] for r in register['records']}
    for row in records:
        row['depth_reference_ids']=owned[row['entity_id']][:]
        row['projection_ids']=[p['id'] for p in projections if p['entity_id']==row['entity_id']]
        row['unresolved_reference_case_ids']=[p['id'] for p in unresolved if p['entity_id']==row['entity_id']]
        row['projection_status']=('regional_assumed_interpolation_available' if row['projection_ids'] else
            'reference_cases_blocked_no_supported_projection' if row['unresolved_reference_case_ids'] else 'not_yet_projected')
    owners=sum(bool(r['projection_ids']) for r in records)
    only_blocked=sum(bool(r['unresolved_reference_case_ids']) and not r['projection_ids'] for r in records)
    return {'schema':'osw.current-depth-route-projections.v14','status':'SUPPORTED_REGIONAL_SCENARIOS_WITH_FULLY_BLOCKED_CASE_INVENTORY',
        'generator_file':GENERATOR,'generator_sha256':hashlib.sha256((root/GENERATOR).read_bytes()).hexdigest(),
        'input_sha256':dict(op['input_sha256'],**{OPERATOR:hashlib.sha256((root/OPERATOR).read_bytes()).hexdigest()}),
        'previous35_projection_records_preserved':projections[:35]==prior['projections'],
        'counts':{'catalog_identities':len(records),'identities_with_regional_projection_scenarios':owners,
            'identities_not_yet_projected':len(records)-owners,'identities_with_only_blocked_reference_cases':only_blocked,
            'identities_without_any_regional_reference_case':sum(not r['projection_ids'] and not r['unresolved_reference_case_ids'] for r in records),
            'regional_projection_scenarios':len(projections),'unresolved_regional_reference_cases':len(unresolved),
            'source_anchor_references':prior['counts']['source_anchor_references'],
            'new_model_reference_cases':len(all_new),'new_supported_model_scenarios':len(additions),'new_blocked_model_reference_cases':len(blocked),
            'new_model_profile_anchors':sum(len(p['anchors']) for p in all_new),
            'new_projection_eligible_source_nodes':sum(a['lower_projection_eligible'] for p in all_new for a in p['anchors']),
            'new_conditional_adjacent_segments':sum(s['projection_status']!='gap_no_projection' for p in all_new for s in p['segments']),
            'new_gap_segments':sum(s['projection_status']=='gap_no_projection' for p in all_new for s in p['segments']),
            'new_depth_measurements':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0,
            'regional_reference_geometry_volume_scenarios':prior['counts']['regional_reference_geometry_volume_scenarios']},
        'interpretation':op['interpretation'],'source_definition_clarifications':copy.deepcopy(prior['source_definition_clarifications']),
        'regional_volume_scenario_file':prior['regional_volume_scenario_file'],'fitted_phase_depth_sample_spans':copy.deepcopy(prior['fitted_phase_depth_sample_spans']),
        'unresolved_reference_cases':unresolved,'unresolved_reference_case_csv':UNRESOLVED_CSV,
        'records':records,'projections':projections,'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}


def csv_bytes(document,root=ROOT):
    op=json.loads((root/OPERATOR).read_bytes());reader=csv.DictReader(io.StringIO((root/op['previous_projection_csv']).read_text(encoding='utf8')))
    columns=list(reader.fieldnames);rows=list(reader)
    for p in document['projections'][35:]:
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


def unresolved_csv_bytes(document):
    columns=['reference_case_id','entity_id','snapshot_time_utc','reference_case_status','anchor_id','source_vertex_index',
        'reference_distance_km','reference_lon_lat','selected_model_node_lon_lat','source_native_longitude_degrees_east',
        'source_horizontal_selection_status','source_model_lower_depth_m','projected_depth_descriptor_m',
        'projection_block_reasons','source_profile_refs','source_model_profile_ref','primary_threshold_m_s','volume_eligible']
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader()
    for case in document['unresolved_reference_cases']:
        for a in case['anchors']:
            row={'reference_case_id':case['id'],'entity_id':case['entity_id'],'snapshot_time_utc':case['snapshot_time_utc'],
                 'reference_case_status':case['reference_case_status'],'anchor_id':a['id'],'source_vertex_index':a['source_vertex_index'],
                 'reference_distance_km':a['distance_km'],'source_model_lower_depth_m':a['model_lower_depth_m'],
                 'projected_depth_descriptor_m':None,'primary_threshold_m_s':case['primary_threshold_m_s'],'volume_eligible':False}
            for k in ['reference_lon_lat','selected_model_node_lon_lat','source_native_longitude_degrees_east','source_horizontal_selection_status','projection_block_reasons','source_profile_refs','source_model_profile_ref']:
                value=a[k];row[k]=json.dumps(value,separators=(',',':')) if isinstance(value,(dict,list)) else value
            writer.writerow(row)
    return out.getvalue().encode('utf8')


def main():
    result=build();out=Path('current-depth-route-projections-v14');out.mkdir(exist_ok=True)
    raw=(json.dumps(result,indent=2,allow_nan=False)+'\n').encode('utf8');csv_raw=csv_bytes(result)
    if max(len(raw),len(csv_raw))>=2500000:raise ValueError('Fixed per-file publication cap exceeded; do not raise it')
    (out/'projections.json').write_bytes(raw);(out/'projections.csv').write_bytes(csv_raw)
    (out/'unresolved-cases.csv').write_bytes(unresolved_csv_bytes(result));print(json.dumps(result['counts']))


if __name__=='__main__':main()
