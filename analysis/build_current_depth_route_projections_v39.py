"""New current addendum using the frozen source-to-reference projection method."""
import math
from current_depth_search_partitions_v1 import validate_partitions,validate_section_partition
from interval_transverse_section_audit_v1 import validate_retained as validate_interval_retained
import copy
import hashlib
import json
from pathlib import Path
from build_current_depth_route_projections_v18 import reference_placeholder,INTERIOR
from build_current_depth_route_projections_v12 import GEOD,paired_anchor,project
from build_current_depth_route_projections_v15 import encoded,sample_csv_bytes
from load_current_depth_projection_inventory_v1 import read_parts,assemble,load_inventory

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-route-projection-operator-v39.json'
GENERATOR='analysis/build_current_depth_route_projections_v39.py'
INVENTORY='research/current-depth-route-projection-inventory-v25.json'
ADDENDUM='research/current-depth-route-projection-addenda/partitioned-ocean-full-sections-hycom2022-v1.json'
SAMPLES_CSV='research/current-depth-route-projection-addenda/partitioned-ocean-full-sections-hycom2022-v1.csv'


def _single_partition_cases(facts,chunks,op):
    for source in chunks.values():
        entity=source['entity_id']
        if (entity not in op['currents'] or source['schema']!='osw.partitioned-interval-transverse-depth-section.v1'
            or source['operator_file']!=op['source_operator_file']
            or source['operator_sha256']!=op['input_sha256'][op['source_operator_file']]):raise ValueError('Interval source operator/schema/owner changed')
        validate_interval_retained(source,{**op['source_audit_config'],**op['currents'][entity]})
    keyed={}
    for index,row in enumerate(facts['descriptors']):
        key=row['entity_id'],row['snapshot_time_utc'],row['section_id']
        if key in keyed:raise ValueError('Duplicate original current/date/section')
        keyed[key]=op['source_descriptor_index_map'][index],row
    expected={(entity,t,s['id']) for entity,c in op['currents'].items() for t in op['snapshot_times_utc'] for s in c['sections']}
    if set(keyed)!=expected:raise ValueError('All declared source section/date cases required')
    supported=[];blocked=[]
    for entity,config in op['currents'].items():
        for stamp in op['snapshot_times_utc']:
            anchors=[];distance=0.;previous=None
            for definition in config['sections']:
                index,row=keyed[entity,stamp,definition['id']];source=chunks[row['source_file']];diagnosis=source['diagnosis']
                selected=row['selected_column_index'];profile=source['columns'][selected] if selected is not None else None
                if (source['entity_id']!=entity or source['snapshot_time_utc']!=stamp or source['source_returned_timestamp_utc']!=stamp
                    or source['section_definition']!=definition or row['section_definition']!=definition
                    or source['component_bearing_degrees_true']!=config['component_bearing_degrees_true']
                    or row['component_bearing_degrees_true']!=config['component_bearing_degrees_true']
                    or row['source_sha256']!=op['input_sha256'][row['source_file']]
                    or row['primary_threshold_m_s']!=config['primary_threshold_m_s']
                    or row['candidate_count']!=len(source['columns'])
                    or row['local_integral_maximum_indices']!=diagnosis['local_integral_maximum_indices']
                    or diagnosis['selected_column_index']!=selected
                    or row['horizontal_selection_status']!=diagnosis['horizontal_selection_status']
                    or row['selected_column_threshold_layers']!=diagnosis['selected_column_threshold_layers']):raise ValueError('Source identity, section, frame or selection changed')
                if row['source_diagnosis_pointer']!='/diagnosis':raise ValueError('Source diagnosis pointer changed')
                layers=row['selected_column_threshold_layers'];matches=[r for r in layers if r['threshold_m_s']==config['primary_threshold_m_s']]
                if profile is not None:
                    if row['source_profile_pointer']!='/columns/'+str(selected) or row['selected_lon_lat']!=profile['sampled_lon_lat'] or len(matches)!=1:raise ValueError('Primary layer, profile pointer or position changed')
                    layer=matches[0]
                    temperatures=source['native100m_temperature_degrees_celsius']
                    actual_temperature=temperatures[selected] if temperatures is not None else None
                    if row['selected_native100m_temperature_degrees_celsius']!=actual_temperature:raise ValueError('Selected model temperature changed')
                    if config['temperature_gate'] is not None and (actual_temperature is None or actual_temperature>config['temperature_gate']['maximum_temperature_degrees_celsius']):raise ValueError('Selected model temperature gate not met')
                    if layer['lower_depth_m']!=row['primary_lower_depth_m'] or layer['layer_thickness_m']!=row['primary_layer_thickness_m']:raise ValueError('Primary source depth changed')
                    point=profile['sampled_lon_lat'];geometry_placeholder=False
                else:
                    if matches or layers or row['source_profile_pointer'] is not None or row['selected_lon_lat'] is not None or row['primary_lower_depth_m'] is not None:raise ValueError('Invented selected profile in unresolved source section')
                    layer=None;point=reference_placeholder(source,definition);geometry_placeholder=True
                if previous is not None:
                    metres=GEOD.inv(*previous,*point)[2]
                    if not math.isfinite(metres) or metres<=0:raise ValueError('Distinct finite original section positions required')
                    distance+=metres/1000
                previous=point;reasons=[]
                if profile is None:reasons.append('no_qualifying_source_column_reference_gate_midpoint_only')
                if row['horizontal_selection_status']!=INTERIOR:reasons.append('section_axis_proxy_not_interior_bracketed')
                if layer is None or layer['lower_depth_m'] is None:reasons.append('primary_lower_boundary_censored_or_unresolved')
                lower=not reasons;span=lower and layer['layer_thickness_m'] is not None
                anchors.append(paired_anchor(entity.split(':')[1]+'-'+op['active_search_partition_id']+'-partitioned-ocean'+str(config['selection_depth_interval_m'][0])+'_'+str(config['selection_depth_interval_m'][1])+'-'+stamp[:10]+'-'+definition['id'],layer,lower,span,reasons,
                    source_section_id=definition['id'],distance_km=round(distance,6),reference_lon_lat=point,
                    reference_geometry_is_unselected_gate_midpoint=geometry_placeholder,
                    selected_model_node_lon_lat=profile['sampled_lon_lat'] if profile else None,
                    source_component_bearing_degrees_true=config['component_bearing_degrees_true'],
                    source_horizontal_selection_status=row['horizontal_selection_status'],
                    source_profile_refs=[op['source_facts_file']+'#/descriptors/'+str(index)],
                    source_model_profile_ref=row['source_file']+'#'+row['source_profile_pointer'] if profile else None,
                    source_connected_diagnosis_ref=row['source_file']+'#/diagnosis/selected_column_threshold_layers/'+str(layers.index(layer)) if layer else None,
                    source_section_definition=definition,source_candidate_count=row['candidate_count'],
                    source_local_integral_maximum_indices=row['local_integral_maximum_indices'],
                    source_selected_native100m_temperature_degrees_celsius=row['selected_native100m_temperature_degrees_celsius']))
            raw={'entity_id':entity,'snapshot_time_utc':stamp,'primary_threshold_m_s':config['primary_threshold_m_s'],'anchors':anchors,
                'geometry_role':'regional_reference_connector_between_selected_model_columns_with_explicit_unselected_gate_midpoint_placeholders',
                'route_id':entity.split(':')[1]+'-'+op['active_search_partition_id']+'-regional-reference-'+stamp[:10],'route_file':None,
                'search_partition_id':op['active_search_partition_id'],'search_partition_kind':'editorial_latitude_search_context',
                'front_or_water_mass_classification_performed':False,'persistent_jet_identity_validated':False,'cross_partition_interpolation_permitted':False,
                'source_time_basis':'HYCOM instantaneous March/June/September/December15,2022 00Z;quarterly probes,not seasonal means or annual envelopes.',
                'projection_gate':'Interior maximum of complete finite declared declared directional interval without surface qualification;resolved declared primary lower contour;axis identity remains unvalidated.',
                'selection_depth_interval_m':config['selection_depth_interval_m'],'core_search_depth_interval_m':config['core_search_depth_interval_m'],'source_surface_component_gate_m_s':None,
                'canonical_route_replaced':False,'canonical_route_extrapolation_performed':False,'reference_geometry_scope':'independent_regional_connector_between_original_sections',
                'method_id':'interval_'+str(config['selection_depth_interval_m'][0])+'_'+str(config['selection_depth_interval_m'][1])+'-no-surface-gate-v1','comparison_group':'model_interval_'+str(config['selection_depth_interval_m'][0])+'_'+str(config['selection_depth_interval_m'][1])+'_no_surface_gate',
                'source_component_reference_frame':'fixed_geographic_'+str(config['component_bearing_degrees_true'])+'degree_true_held_through_depth',
                'branch_scope':config['branch_scope'],'temperature_gate':config['temperature_gate']}
            case=project(raw,op);case['id']=entity.split(':')[1]+'-'+op['active_search_partition_id']+'-partitioned-ocean'+str(config['selection_depth_interval_m'][0])+'_'+str(config['selection_depth_interval_m'][1])+'-'+stamp[:10]+'-component'+str(config['component_bearing_degrees_true'])+'-v1'
            for sample in case['samples']:
                sample.update(search_partition_id=op['active_search_partition_id'],search_partition_kind='editorial_latitude_search_context',front_or_water_mass_classification_performed=False)
            if any(a['lower_projection_eligible'] for a in anchors):supported.append(case)
            else:
                case['status']='UNRESOLVED_REGIONAL_REFERENCE_CASE_NO_SUPPORTED_PRIMARY_DEPTH'
                blocked.append(case)
    return supported,blocked



def full_section_cases(facts,chunks,op):
    grouped=validate_partitions(op)
    for entity,c in op['currents'].items():
        if c['sections']!=[s for s in op['sections'] if s['entity_id']==entity]:raise ValueError('Canonical current section list differs from partition plan')
    expected={(s['entity_id'],stamp,s['id']) for stamp in op['snapshot_times_utc'] for s in op['sections']}
    keys=[(r['entity_id'],r['snapshot_time_utc'],r['section_id']) for r in facts['descriptors']]
    files=[r['source_file'] for r in facts['descriptors']]
    if len(keys)!=len(set(keys)) or set(keys)!=expected or len(files)!=len(set(files)) or set(files)!=set(chunks) or set(files)!=set(op['section_files']):raise ValueError('Every original partition section/date and source chunk required exactly once')
    eligible_native={}
    for row in facts['descriptors']:
        source=chunks[row['source_file']];key=validate_section_partition(source,op)
        if row['search_partition_id']!=key or row['section_definition']!=source['section_definition']:raise ValueError('Descriptor partition differs from exact retained source')
        if row['selected_column_index'] is not None and row['horizontal_selection_status']==INTERIOR and row['primary_lower_depth_m'] is not None:
            column=source['columns'][row['selected_column_index']]
            native=(row['entity_id'],row['snapshot_time_utc'],column['global_longitude_index'],column['global_latitude_index'])
            if native in eligible_native and eligible_native[native]!=key:raise ValueError('One native profile cannot be eligible in two search partitions')
            eligible_native[native]=key
    supported=[];blocked=[]
    for key,definitions in grouped.items():
        partition=op['search_partitions'][key];entity=partition['entity_id']
        rows=[(i,row) for i,row in enumerate(facts['descriptors']) if row['search_partition_id']==key]
        sub=copy.deepcopy(op);sub['active_search_partition_id']=key
        sub['source_descriptor_index_map']=[i for i,row in rows]
        sub['currents']={entity:{**op['currents'][entity],'sections':definitions,
            'branch_scope':op['currents'][entity]['branch_scope']+' Search partition: '+partition['scope']}}
        sub['section_files']=[row['source_file'] for i,row in rows]
        regional_facts={**facts,'descriptors':[row for i,row in rows]}
        regional_chunks={row['source_file']:chunks[row['source_file']] for i,row in rows}
        a,b=_single_partition_cases(regional_facts,regional_chunks,sub)
        supported.extend(a);blocked.extend(b)
    return supported,blocked


def build(root=ROOT):
    reader=lambda p:(root/p).read_bytes();read=lambda p:json.loads(reader(p));op=read(OPERATOR)
    for p,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(p)).hexdigest()!=pin:raise ValueError('Frozen source changed: '+p)
    if any(op['eligibility'].values()):raise ValueError('No physical promotion')
    previous=read(op['previous_inventory_file']);base,prior_addenda=read_parts(previous,reader)
    load_inventory(previous,reader)
    projections,blocked=full_section_cases(read(op['source_facts_file']),{p:read(p) for p in op['section_files']},op)
    for case in projections+blocked:case['source_surface_component_gate_m_s']=op['currents'][case['entity_id']]['surface_component_gate_m_s']
    addendum={'schema':'osw.current-depth-route-projection-addendum.v1','id':'partitioned-ocean-full-sections-hycom2022-v1',
        'base_snapshot_sha256':previous['base']['json']['sha256'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256(reader(OPERATOR)).hexdigest(),
        'input_sha256':op['input_sha256'],'projections':projections,'unresolved_reference_cases':blocked,
        'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}
    add_raw=encoded(addendum);csv_raw=sample_csv_bytes(projections,reader(previous['base']['csv']['file']))
    pieces={ADDENDUM:add_raw,SAMPLES_CSV:csv_raw}
    piece=lambda f,raw:{'file':f,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    manifest=copy.deepcopy(previous);manifest['addenda'].append({'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(SAMPLES_CSV,csv_raw)})
    manifest['counts']=assemble(base,prior_addenda+[addendum])['counts']
    manifest['view_metadata'].update(schema='osw.current-depth-route-projections.v39',status='REGIONAL_DEPTH_BASE_PLUS_PINNED_CURRENT_ADDENDA',generator_file=GENERATOR,generator_sha256=hashlib.sha256(reader(GENERATOR)).hexdigest(),interpretation=op['interpretation'])
    pieces[INVENTORY]=encoded(manifest)
    result=load_inventory(manifest,lambda p:pieces[p] if p in pieces else reader(p))
    return manifest,addendum,pieces,result


def main():
    manifest,addendum,pieces,result=build();out=Path('current-depth-route-projections-v39');out.mkdir(exist_ok=True)
    for path,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(SAMPLES_CSV,'samples.csv')]:
        if len(pieces[path])>=2500000:raise ValueError('Fixed per-file publication cap exceeded')
        (out/name).write_bytes(pieces[path])
    print(json.dumps(result['counts']))


if __name__=='__main__':main()
