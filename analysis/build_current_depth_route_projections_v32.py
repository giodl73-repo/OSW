"""Cloud-only interval reanalysis of retained Pacific SEC components for Pacific SSCC and additive join."""
import copy
import hashlib
import json
import math
from pathlib import Path
from interval_depth_diagnostic_v1 import diagnose,INTERIOR
from acquire_zonal_current_depth_sections_v1 import validate_retained
from sample_eac_hycom_route_depth_v1 import along_velocity
from build_current_depth_route_projections_v12 import GEOD,paired_anchor,project
from build_current_depth_route_projections_v18 import reference_placeholder
from build_current_depth_route_projections_v15 import encoded,sample_csv_bytes
from load_current_depth_projection_inventory_v1 import read_parts,load_inventory,assemble

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-route-projection-operator-v32.json'
GENERATOR='analysis/build_current_depth_route_projections_v32.py'
REPORT='research/pacific-sscc-interval100-400-depth-reanalysis-v1.json'
INVENTORY='research/current-depth-route-projection-inventory-v18.json'
ADDENDUM='research/current-depth-route-projection-addenda/pacific-sscc-interval100-400-hycom2022-v1.json'
SAMPLES_CSV='research/current-depth-route-projection-addenda/pacific-sscc-interval100-400-hycom2022-v1.csv'


def validate_operator(op):
    if (op['selection_depth_interval_m']!=[100,400] or op['core_search_depth_interval_m']!=[100,400]
        or op['surface_component_gate_m_s'] is not None or op['primary_threshold_m_s']!=.1
        or op['component_bearing_degrees_true']!=90 or op['entity_id']!='current:pacific-south-subsurface-countercurrent'
        or op['source_entity_id']!='current:pacific-south-equatorial' or op['source_component_bearing_degrees_true']!=270
        or op['analysis_latitude_gate_degrees_north']!=[-5.5,-3]
        or op['thresholds_m_s']!=[.05,.1,.2]
        or op['maximum_total_cell_pairs']!=250000 or op['maximum_total_decoded_velocity_bytes']!=7000000
        or any(op['eligibility'].values())):raise ValueError('Declared Pacific SSCC counterflow diagnostic definition changed')


def recompute_subset(source,op):
    validate_operator(op)
    latitudes=[c['sampled_lon_lat'][1] for c in source['columns']]
    if any(not math.isfinite(y) for y in latitudes) or any(b<=a for a,b in zip(latitudes,latitudes[1:])):
        raise ValueError('Increasing original native latitude columns required')
    south,north=op['analysis_latitude_gate_degrees_north']
    indices=[i for i,y in enumerate(latitudes) if south<=y<=north]
    if not 3<=len(indices)<=150 or indices!=list(range(indices[0],indices[-1]+1)):
        raise ValueError('Bounded contiguous original column subset required')
    profiles=[]
    for i in indices:
        column=source['columns'][i];u=column['eastward_velocity_m_s'];v=column['northward_velocity_m_s']
        if len(u)!=len(v) or len(u)!=len(source['depth_levels_m']):raise ValueError('Original component profile size changed')
        result=[]
        for east,northward in zip(u,v):
            if east is None or northward is None:result.append(None);continue
            if (type(east) not in (int,float) or type(northward) not in (int,float)
                or not math.isfinite(east) or not math.isfinite(northward)):raise ValueError('Finite original components or explicit nulls required')
            result.append(along_velocity(east,northward,90))
        profiles.append(result)
    return indices,profiles


def derive_report(chunks,oldop,op):
    validate_operator(op)
    original=[s for s in oldop['sections'] if s['entity_id']==op['source_entity_id'] and s['longitude_degrees_east'] in [-140,-130,-120]]
    if (op['snapshot_times_utc']!=oldop['snapshot_times_utc'] or op['sections']!=list(reversed(original))
        or [s['longitude_degrees_east'] for s in op['sections']]!=[-140,-130,-120]
        or any(s['latitude_gate_degrees_north']!=[-5.5,-.5] for s in original)):
        raise ValueError('Original source sections and dates must be pinned and ordered eastward')
    expected={(t,s['id']) for t in op['snapshot_times_utc'] for s in op['sections']}
    actual={(s['snapshot_time_utc'],s['section_definition']['id']) for s in chunks.values()}
    if len(chunks)!=6 or actual!=expected:raise ValueError('All six original Pacific SEC source sections required')
    indexed={(s['snapshot_time_utc'],s['section_definition']['id']):(f,s) for f,s in chunks.items()}
    rows=[];source_pairs=0;subset_pairs=0
    for stamp in op['snapshot_times_utc']:
        for definition in op['sections']:
            file,source=indexed[stamp,definition['id']]
            if (source['entity_id']!=op['source_entity_id'] or source['section_definition']!=definition
                or source['operator_file']!=op['source_operator_file']
                or source['operator_sha256']!=op['input_sha256'][op['source_operator_file']]
                or source['component_bearing_degrees_true']!=270
                or source['snapshot_time_utc']!=source['source_returned_timestamp_utc']):
                raise ValueError('Original source identity/frame/geometry/time changed')
            validate_retained(source,{**oldop,**oldop['currents'][op['source_entity_id']]})
            z=source['depth_levels_m']
            if len(z)!=40 or z[0]!=0 or z[-1]!=5000:raise ValueError('Original full native depth support required')
            indices,profiles=recompute_subset(source,op)
            source_pairs+=len(z)*len(source['columns']);subset_pairs+=len(z)*len(indices)
            if source_pairs+subset_pairs>op['maximum_total_cell_pairs'] or (source_pairs+subset_pairs)*16>op['maximum_total_decoded_velocity_bytes']:
                raise ValueError('Full-source audit plus subset reanalysis budget exceeded')
            result=diagnose(z,profiles,op);selected=result['selected_column_index']
            source_index=indices[selected] if selected is not None else None
            rows.append({'entity_id':op['entity_id'],'source_entity_id':op['source_entity_id'],
                'snapshot_time_utc':stamp,'section_definition':definition,
                'analysis_latitude_gate_degrees_north':[-5.5,-3],
                'source_file':file,'source_sha256':op['input_sha256'][file],
                'source_column_count':len(source['columns']),'subset_column_indices':indices,
                'selected_source_column_index':source_index,
                'source_component_bearing_degrees_true':270,'derived_component_bearing_degrees_true':90,
                'selected_recomputed_reference_component_m_s':profiles[selected] if selected is not None else None,
                'original_surface_diagnosis_ref':file+'#/diagnosis',
                'original_surface_selected_column_index':source['diagnosis']['selected_column_index'],
                'original_surface_selection_status':source['diagnosis']['horizontal_selection_status'],
                'diagnosis':result,'new_independent_observations':0})
    return {'schema':'osw.pacific-sscc-interval100-400-depth-reanalysis.v1',
        'status':'SEPARATE_COUNTERFLOW_INTERVAL_DIAGNOSTIC_OF_RETAINED_MODEL_COMPONENTS',
        'operator_file':OPERATOR,'selection_depth_interval_m':[100,400],'core_search_depth_interval_m':[100,400],
        'primary_threshold_m_s':.1,'surface_component_gate_m_s':None,'component_bearing_degrees_true':90,
        'source_entity_id':op['source_entity_id'],'entity_id':op['entity_id'],
        'source_profile_count':sum(r['source_column_count'] for r in rows),
        'subset_profile_count':sum(len(r['subset_column_indices']) for r in rows),
        'audited_source_velocity_cell_pairs':source_pairs,'recomputed_subset_velocity_cell_pairs':subset_pairs,
        'processed_velocity_cell_pairs':source_pairs+subset_pairs,
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
            selected=diagnosis['selected_column_index'];source_index=row['selected_source_column_index'];profile=source['columns'][source_index] if source_index is not None else None
            layers=diagnosis['selected_column_threshold_layers'];matches=[l for l in layers if l['threshold_m_s']==.1]
            if (profile is not None and len(matches)!=1) or (profile is None and layers):raise ValueError('Primary interval layer mismatch')
            layer=matches[0] if matches else None
            point=profile['sampled_lon_lat'] if profile else reference_placeholder(source,{**definition,'latitude_gate_degrees_north':op['analysis_latitude_gate_degrees_north']})
            if previous is not None:
                metres=GEOD.inv(*previous,*point)[2]
                if not math.isfinite(metres) or metres<=0:raise ValueError('Distinct finite original reference positions required')
                distance+=metres/1000
            previous=point;reasons=[]
            if profile is None:reasons.append('no_qualifying_interval_column_unsampled_midpoint_only')
            if diagnosis['horizontal_selection_status']!=INTERIOR:reasons.append('interval_selection_not_interior_bracketed')
            if layer is None or layer['lower_depth_m'] is None:reasons.append('primary_lower_boundary_censored_or_unresolved')
            lower=not reasons;span=lower and layer['layer_thickness_m'] is not None
            anchors.append(paired_anchor('pacific-sscc-interval100-400-'+stamp[:10]+'-'+definition['id'],layer,lower,span,reasons,
                source_section_id=definition['id'],distance_km=round(distance,6),reference_lon_lat=point,
                reference_geometry_is_unselected_gate_midpoint=profile is None,
                selected_model_node_lon_lat=profile['sampled_lon_lat'] if profile else None,
                source_component_bearing_degrees_true=90,source_horizontal_selection_status=diagnosis['horizontal_selection_status'],
                source_profile_refs=[REPORT+'#/sections/'+str(index)],
                source_model_profile_ref=row['source_file']+'#/columns/'+str(source_index) if profile else None,
                source_connected_diagnosis_ref=REPORT+'#/sections/'+str(index)+'/diagnosis/selected_column_threshold_layers/'+str(layers.index(layer)) if layer else None,
                source_section_definition=definition,source_candidate_count=len(row['subset_column_indices']),
                source_original_component_bearing_degrees_true=270,source_original_entity_id=op['source_entity_id'],
                source_analysis_latitude_gate_degrees_north=op['analysis_latitude_gate_degrees_north'],
                source_derived_component_ref=REPORT+'#/sections/'+str(index)+'/selected_recomputed_reference_component_m_s' if profile else None,
                source_local_integral_maximum_indices=diagnosis['local_integral_maximum_indices'],
                original_surface_diagnosis_ref=row['original_surface_diagnosis_ref'],
                original_surface_selected_column_index=row['original_surface_selected_column_index']))
        raw={'entity_id':op['entity_id'],'snapshot_time_utc':stamp,'primary_threshold_m_s':.1,'anchors':anchors,
            'geometry_role':'regional_reference_connectors_between_interval_selected_columns_with_explicit_gaps',
            'route_id':'pacific-sscc-interval100-400-reference-'+stamp[:10],'route_file':None,
            'source_time_basis':'Retained HYCOM January/July15,2022 00Z snapshots; no new provider fields or independent observations.',
            'projection_gate':'Interior maximum of complete finite100–400m eastward integral in declared5.5–3S subset; resolved primary10cm/s lower contour.',
            'source_component_reference_frame':'fixed_geographic_90degree_true_held_through_depth',
            'branch_scope':op['branch_scope'],'temperature_gate':None,'source_surface_component_gate_m_s':None,
            'selection_depth_interval_m':[100,400],'core_search_depth_interval_m':[100,400],
            'method_id':'pacific-sscc-interval100-400-no-surface-gate-v1','comparison_group':'model_primary_sscc_interval100_400_no_surface_gate',
            'original_surface_cases_replaced':False,'same_source_as_surface_diagnostic':True}
        case=project(raw,op);case['id']='pacific-sscc-interval100-400-'+stamp[:10]+'-component90-v1'
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
    addendum={'schema':'osw.current-depth-route-projection-addendum.v1','id':'pacific-sscc-interval100-400-hycom2022-v1',
        'base_snapshot_sha256':previous['base']['json']['sha256'],'operator_file':OPERATOR,'operator_sha256':report['operator_sha256'],
        'input_sha256':op['input_sha256'],'derived_source_report':piece(REPORT,report_raw),
        'projections':projections,'unresolved_reference_cases':blocked,
        'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}
    add_raw=encoded(addendum);csv_raw=sample_csv_bytes(projections,reader(previous['base']['csv']['file']))
    pieces={REPORT:report_raw,ADDENDUM:add_raw,SAMPLES_CSV:csv_raw}
    manifest=copy.deepcopy(previous);manifest['addenda'].append({'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(SAMPLES_CSV,csv_raw)})
    manifest['counts']=assemble(base,prior_addenda+[addendum])['counts']
    manifest['view_metadata'].update(schema='osw.current-depth-route-projections.v32',generator_file=GENERATOR,
        generator_sha256=hashlib.sha256(reader(GENERATOR)).hexdigest(),interpretation=op['interpretation'])
    pieces[INVENTORY]=encoded(manifest);result=load_inventory(manifest,lambda f:pieces[f] if f in pieces else reader(f))
    return manifest,addendum,pieces,result,report


def main():
    manifest,addendum,pieces,result,report=build();out=Path('current-depth-route-projections-v32');out.mkdir(exist_ok=True)
    for file,name in [(REPORT,'report.json'),(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(SAMPLES_CSV,'samples.csv')]:
        if len(pieces[file])>=2500000:raise ValueError('Fixed publication cap exceeded')
        (out/name).write_bytes(pieces[file])
    print(json.dumps({'inventory_counts':result['counts'],'reanalysis_source_profiles':report['source_profile_count'],
        'interval_primary_eligible_nodes':sum(a['lower_projection_eligible'] for c in addendum['projections'] for a in c['anchors']),
        'new_provider_field_reads':0,'new_independent_observations':0}))


if __name__=='__main__':main()
