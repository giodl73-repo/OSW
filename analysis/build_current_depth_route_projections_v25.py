"""Cloud-only interval reanalysis of immutable WSC source profiles and additive join."""
import copy
import hashlib
import json
import math
from pathlib import Path
from interval_depth_diagnostic_v1 import diagnose,INTERIOR
from latitude_depth_section_geometry_v1 import validate_retained
from build_current_depth_route_projections_v12 import GEOD,paired_anchor,project
from build_current_depth_route_projections_v18 import reference_placeholder
from build_current_depth_route_projections_v15 import encoded,sample_csv_bytes
from load_current_depth_projection_inventory_v1 import read_parts,load_inventory,assemble

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-route-projection-operator-v25.json'
GENERATOR='analysis/build_current_depth_route_projections_v25.py'
REPORT='research/wsc-interval20-500-depth-reanalysis-v1.json'
INVENTORY='research/current-depth-route-projection-inventory-v11.json'
ADDENDUM='research/current-depth-route-projection-addenda/wsc-interval20-500-hycom2022-v1.json'
SAMPLES_CSV='research/current-depth-route-projection-addenda/wsc-interval20-500-hycom2022-v1.csv'


def validate_operator(op):
    if (op['selection_depth_interval_m']!=[20,500] or op['core_search_depth_interval_m']!=[20,500]
        or op['surface_component_gate_m_s'] is not None or op['primary_threshold_m_s']!=.1
        or op['component_bearing_degrees_true']!=0 or op['entity_id']!='current:west-spitsbergen'
        or op['thresholds_m_s']!=[.05,.1,.2]
        or any(op['eligibility'].values())):raise ValueError('Frozen interval20–500 diagnostic definition changed')


def derive_report(chunks,oldop,op):
    validate_operator(op)
    if (op['snapshot_times_utc']!=oldop['snapshot_times_utc']
        or op['sections']!=[s for s in oldop['sections'] if s['entity_id']==op['entity_id']]):
        raise ValueError('Original horizontal gates and dates must remain unchanged')
    expected={(t,s['id']) for t in op['snapshot_times_utc'] for s in op['sections']}
    actual={(s['snapshot_time_utc'],s['section_definition']['id']) for s in chunks.values()}
    if len(chunks)!=16 or actual!=expected:raise ValueError('Every original WSC section/date required')
    indexed={(s['snapshot_time_utc'],s['section_definition']['id']):(f,s) for f,s in chunks.items()}
    rows=[];pairs=0
    for stamp in op['snapshot_times_utc']:
        for definition in op['sections']:
            file,source=indexed[stamp,definition['id']]
            if (source['entity_id']!=op['entity_id'] or source['section_definition']!=definition
                or source['operator_file']!=op['source_operator_file']
                or source['operator_sha256']!=op['input_sha256'][op['source_operator_file']]
                or source['component_bearing_degrees_true']!=0):raise ValueError('Original source identity/frame/geometry changed')
            validate_retained(source,{**oldop,**oldop['currents'][op['entity_id']]})
            if (len(source['depth_levels_m'])!=40 or source['depth_levels_m'][0]!=0
                or source['depth_levels_m'][-1]!=5000):raise ValueError('Original full-depth support required')
            pairs+=40*len(source['columns'])
            if pairs>op['maximum_total_cell_pairs'] or pairs*16>op['maximum_total_decoded_velocity_bytes']:
                raise ValueError('Retained profile reanalysis budget exceeded')
            result=diagnose(source['depth_levels_m'],[p['signed_reference_component_m_s'] for p in source['columns']],op)
            rows.append({'entity_id':op['entity_id'],'snapshot_time_utc':stamp,'section_definition':definition,
                'source_file':file,'source_sha256':op['input_sha256'][file],'source_column_count':len(source['columns']),
                'original_surface_diagnosis_ref':file+'#/diagnosis','original_surface_selected_column_index':source['diagnosis']['selected_column_index'],
                'original_surface_selection_status':source['diagnosis']['horizontal_selection_status'],
                'diagnosis':result,'new_independent_observations':0})
    return {'schema':'osw.wsc-interval20-500-depth-reanalysis.v1','status':'SEPARATE_INTERVAL_DIAGNOSTIC_OF_RETAINED_MODEL_PROFILES',
        'operator_file':OPERATOR,'selection_depth_interval_m':[20,500],'core_search_depth_interval_m':[20,500],
        'primary_threshold_m_s':.1,'surface_component_gate_m_s':None,'component_bearing_degrees_true':0,
        'source_profile_count':sum(s['source_column_count'] for s in rows),'processed_velocity_cell_pairs':pairs,
        'new_provider_field_reads':0,'new_independent_observations':0,'sections':rows,
        'same_model_profiles_as_surface_diagnostic':True,'diagnostics_are_statistically_independent':False,
        'original_surface_cases_replaced':False,'physical_current_thickness_established':False,'full_goal_complete':False}


def cases_from_report(report,chunks,oldop,op):
    numerical={k:v for k,v in report.items() if k not in ['operator_sha256','input_sha256']}
    if (numerical!=derive_report(chunks,oldop,op)
        or ('input_sha256' in report and report['input_sha256']!=op['input_sha256'])):
        raise ValueError('Derived diagnostic/provenance does not reproduce')
    supported=[];blocked=[]
    for stamp in op['snapshot_times_utc']:
        anchors=[];distance=0.;previous=None
        for index,row in enumerate(report['sections']):
            if row['snapshot_time_utc']!=stamp:continue
            source=chunks[row['source_file']];definition=row['section_definition'];diagnosis=row['diagnosis']
            selected=diagnosis['selected_column_index'];profile=source['columns'][selected] if selected is not None else None
            layers=diagnosis['selected_column_threshold_layers'];matches=[l for l in layers if l['threshold_m_s']==.1]
            if (profile is not None and len(matches)!=1) or (profile is None and layers):raise ValueError('Primary interval layer mismatch')
            layer=matches[0] if matches else None
            point=profile['sampled_lon_lat'] if profile else reference_placeholder(source,definition)
            if previous is not None:
                metres=GEOD.inv(*previous,*point)[2]
                if not math.isfinite(metres) or metres<=0:raise ValueError('Distinct finite original reference positions required')
                distance+=metres/1000
            previous=point;reasons=[]
            if profile is None:reasons.append('no_qualifying_interval_column_unsampled_midpoint_only')
            if diagnosis['horizontal_selection_status']!=INTERIOR:reasons.append('interval_selection_not_interior_bracketed')
            if layer is None or layer['lower_depth_m'] is None:reasons.append('primary_lower_boundary_censored_or_unresolved')
            lower=not reasons;span=lower and layer['layer_thickness_m'] is not None
            anchors.append(paired_anchor('wsc-interval20-500-'+stamp[:10]+'-'+definition['id'],layer,lower,span,reasons,
                source_section_id=definition['id'],distance_km=round(distance,6),reference_lon_lat=point,
                reference_geometry_is_unselected_gate_midpoint=profile is None,
                selected_model_node_lon_lat=profile['sampled_lon_lat'] if profile else None,
                source_component_bearing_degrees_true=0,source_horizontal_selection_status=diagnosis['horizontal_selection_status'],
                source_profile_refs=[REPORT+'#/sections/'+str(index)],
                source_model_profile_ref=row['source_file']+'#/columns/'+str(selected) if profile else None,
                source_connected_diagnosis_ref=REPORT+'#/sections/'+str(index)+'/diagnosis/selected_column_threshold_layers/'+str(layers.index(layer)) if layer else None,
                source_section_definition=definition,source_candidate_count=row['source_column_count'],
                source_local_integral_maximum_indices=diagnosis['local_integral_maximum_indices'],
                original_surface_diagnosis_ref=row['original_surface_diagnosis_ref'],
                original_surface_selected_column_index=row['original_surface_selected_column_index']))
        raw={'entity_id':op['entity_id'],'snapshot_time_utc':stamp,'primary_threshold_m_s':.1,'anchors':anchors,
            'geometry_role':'regional_reference_connectors_between_interval_selected_columns_with_explicit_gaps',
            'route_id':'wsc-interval20-500-reference-'+stamp[:10],'route_file':None,
            'source_time_basis':'Retained HYCOM January/July15,2022 00Z snapshots; no new provider fields or independent observations.',
            'projection_gate':'Interior maximum of complete finite20–500m northward integral; resolved primary10cm/s lower contour.',
            'source_component_reference_frame':'fixed_geographic_0degree_true_held_through_depth',
            'branch_scope':op['branch_scope'],'temperature_gate':None,'source_surface_component_gate_m_s':None,
            'selection_depth_interval_m':[20,500],'core_search_depth_interval_m':[20,500],
            'method_id':'wsc-interval20-500-no-surface-gate-v1','comparison_group':'model_interval20_500_no_surface_gate',
            'original_surface_cases_replaced':False,'same_source_as_surface_diagnostic':True}
        case=project(raw,op);case['id']='west-spitsbergen-interval20-500-'+stamp[:10]+'-component0-v1'
        if any(a['lower_projection_eligible'] for a in anchors):supported.append(case)
        else:
            case['status']='UNRESOLVED_REGIONAL_REFERENCE_CASE_NO_SUPPORTED_PRIMARY_DEPTH';blocked.append(case)
    return supported,blocked


def build(root=ROOT):
    reader=lambda f:(root/f).read_bytes();read=lambda f:json.loads(reader(f));op=read(OPERATOR);validate_operator(op)
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(f)).hexdigest()!=pin:raise ValueError('Frozen input changed: '+f)
    chunks={f:read(f) for f in op['section_files']};oldop=read(op['source_operator_file'])
    report=derive_report(chunks,oldop,op);report.update(operator_sha256=hashlib.sha256(reader(OPERATOR)).hexdigest(),input_sha256=op['input_sha256'])
    # Validate the numerical and original-source portion without circular output hashes.
    diagnosis_report={k:v for k,v in report.items() if k not in ['operator_sha256','input_sha256']}
    projections,blocked=cases_from_report(diagnosis_report,chunks,oldop,op)
    previous=read(op['previous_inventory_file']);base,prior_addenda=read_parts(previous,reader);load_inventory(previous,reader)
    piece=lambda f,raw:{'file':f,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    report_raw=encoded(report)
    addendum={'schema':'osw.current-depth-route-projection-addendum.v1','id':'wsc-interval20-500-hycom2022-v1',
        'base_snapshot_sha256':previous['base']['json']['sha256'],'operator_file':OPERATOR,'operator_sha256':report['operator_sha256'],
        'input_sha256':op['input_sha256'],'derived_source_report':piece(REPORT,report_raw),
        'projections':projections,'unresolved_reference_cases':blocked,
        'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}
    add_raw=encoded(addendum);csv_raw=sample_csv_bytes(projections,reader(previous['base']['csv']['file']))
    pieces={REPORT:report_raw,ADDENDUM:add_raw,SAMPLES_CSV:csv_raw}
    manifest=copy.deepcopy(previous);manifest['addenda'].append({'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(SAMPLES_CSV,csv_raw)})
    manifest['counts']=assemble(base,prior_addenda+[addendum])['counts']
    manifest['view_metadata'].update(schema='osw.current-depth-route-projections.v25',generator_file=GENERATOR,
        generator_sha256=hashlib.sha256(reader(GENERATOR)).hexdigest(),interpretation=op['interpretation'])
    pieces[INVENTORY]=encoded(manifest);result=load_inventory(manifest,lambda f:pieces[f] if f in pieces else reader(f))
    return manifest,addendum,pieces,result,report


def main():
    manifest,addendum,pieces,result,report=build();out=Path('current-depth-route-projections-v25');out.mkdir(exist_ok=True)
    for file,name in [(REPORT,'report.json'),(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(SAMPLES_CSV,'samples.csv')]:
        if len(pieces[file])>=2500000:raise ValueError('Fixed publication cap exceeded')
        (out/name).write_bytes(pieces[file])
    print(json.dumps({'inventory_counts':result['counts'],'reanalysis_source_profiles':report['source_profile_count'],
        'interval_primary_eligible_nodes':sum(a['lower_projection_eligible'] for c in addendum['projections'] for a in c['anchors']),
        'new_provider_field_reads':0,'new_independent_observations':0}))


if __name__=='__main__':main()
