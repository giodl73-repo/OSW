"""Deduplicated northward coastal reference and spatial-depth addendum."""
import copy,csv,hashlib,io,json
from collections import Counter
import load_current_depth_reference_inventory_v1 as base_loader
import load_current_depth_reference_inventory_v12 as prior
import reproduce_ncc_north_depth_sections_v1 as native

SCHEMA='osw.current-depth-ncc-north-joint-addendum.v1'
CONTEXT='ncc-north-61p5-62p25n-hycom2022-original-core'
METRIC=prior.METRIC
checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes


def source_context():return {'entity_id':native.source.OWNER,'component_bearing_degrees_true':0,'velocity_threshold_m_s':.1,'practical_salinity_exclusive_upper_threshold':35,'support_start':'original_velocity_core_no_reselection','geographic_scope':'New editorial61.5N[3,7]E and62.25N[3.5,8.5]E gates;not published current edges or full-route coverage.','time_operator':'original_quarterly_instantaneous_snapshots_not_annual_envelope','independently_validated_axis':False,'physical_current_bottom_established':False}


def reference(case,a):
    row=prior.reference(case,a);r=case['original'];row.update(id='ncc-north-fresh-'+r['snapshot_time_utc'][:10]+'-'+r['section_id'],source_context_id=CONTEXT,evidence_kind='reproduced_northward_joint_native_section_conditional_fresh_component_crossing',source_locator=case['profile_piece']['file']+'#/fresh_component_classification/lower',source_pointer='/fresh_component_classification/lower',source_citation='GOFS3.1expt93.0 paired uv3z/ts3z2022native sections;original northward0-100mvelocity-core selection followed by conditional practicalS35classification.',source_definition='Finite adjacent native lower exit from unchanged original-core-connected fresh/component predicate in new northward regional sections;not physical current bottom.')
    return row


def admission(before,bundle,a):
    cases=native.reproduce(bundle);curtains=native.curtains(cases,bundle);rows=[];outcomes=[]
    old_files={(r.get('source_original_audit_record') or {}).get('source_section_file') for r in before['evidence']};old_keys={tuple((r.get('source_original_audit_record') or {}).get(k) for k in ['entity_id','snapshot_time_utc','section_id']) for r in before['evidence'] if r['metric']==METRIC}
    for case,curtain in zip(cases,curtains):
        c=case['classification'];r=case['original'];lower=c.get('lower') or {};key=(r['entity_id'],r['snapshot_time_utc'],r['section_id'])
        if r['source_section_file'] in old_files or key in old_keys:raise ValueError('Previously admitted native case cannot be duplicated')
        row=None
        if c['status']=='conditional_fresh_component_core_supported' and lower.get('status')=='adjacent_native_joint_predicate_crossing' and lower.get('boundary_depth_m') is not None:row=reference(case,a);rows.append(row)
        outcomes.append({'source_case':copy.deepcopy(r),'classification':copy.deepcopy(c),'reference_id':row['id'] if row else None,'admission_status':'NEW_CONDITIONAL_DESCRIPTOR_ADMITTED' if row else 'UNRESOLVED_OR_CENSORED_NO_REFERENCE','curtain':curtain})
    columns=[column for c in curtains for column in c['columns']];runs=[run for column in columns for run in column['connected_depth_runs']]
    report={'schema':'osw.ncc-north-depth-reference-spatial-admission.v1','operator_file':a['operator_file'],'operator_sha256':a['operator_sha256'],'input_sha256':a['input_sha256'],'source_report':copy.deepcopy(a['derived_source_report']),'records':outcomes,'counts':{'original_cases_reproduced':len(cases),'new_reference_count':len(rows),'depth_curtains':sum(bool(c['columns']) for c in curtains),'unclassified_cases':sum(not c['columns'] for c in curtains),'native_columns_retained':len(columns),'seed_connected_columns':sum(bool(c['connected_depth_runs']) for c in columns),'seed_connected_native_nodes':sum(c['connected_native_node_count'] for c in curtains),'connected_vertical_runs':len(runs),'multiple_run_columns':sum(len(c['connected_depth_runs'])>1 for c in columns),'lower_boundary_status_counts':dict(Counter(r['lower']['status'] for r in runs)),'laterally_censored_sections':sum(any(column['touches_lateral_sampling_edge'] for column in c['columns']) for c in curtains)},'new_ocean_field_requests':0,'old_source_fields_replayed':False,'source_coordinate_pairing_rechecked_against_remote_grid':False,'physical_current_bottom_established':False,'physical_layer_thickness_established':False,'physical_width_established':False,'cross_section_area_established':False,'volume_established':False,'annual_extrema_established':False,'runtime_changed':False,'full_goal_complete':False}
    return rows,report


def assemble(*parts):
    result=prior.assemble(*parts[:-1]);known={r['entity_id'] for r in result['records']};seen={r['id'] for r in result['evidence']}
    for a,bundle in parts[-1]:
        rows,report=admission(result,bundle,a)
        if a['evidence']!=rows or a['source_contexts']!={CONTEXT:source_context()} or CONTEXT in result['source_contexts'] or bundle['spatial_admission_report']!=report:raise ValueError('All-and-only new references and exact spatial outcomes required')
        for row in rows:
            if row['id'] in seen or row['entity_id'] not in known:raise ValueError('Unique known direct owner required')
            seen.add(row['id'])
        result['evidence'].extend(copy.deepcopy(rows));result['source_contexts'].update(copy.deepcopy(a['source_contexts']))
    for r in result['records']:r['depth_reference_ids']=[e['id'] for e in result['evidence'] if e['entity_id']==r['entity_id']]
    result['counts']=base_loader.counts_for(result['records'],result['evidence']);result['metric_counts']=dict(sorted(Counter(r['metric'] for r in result['evidence']).items()));return result


def read_parts(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v13':raise ValueError('Known reference inventory v13 required')
    old=[];cohorts=[];seen=set()
    for part in manifest['addenda']:
        if part['id'] in seen:raise ValueError('Duplicate addendum identity')
        seen.add(part['id']);a=json.loads(checked_piece(part['json'],reader))
        if a['schema']!=SCHEMA:
            if cohorts:raise ValueError('Prior source classes must precede new northward cohort')
            old.append(part);continue
        if a['id']!=part['id'] or a['base_snapshot_sha256']!=manifest['base']['json']['sha256'] or a['runtime_changed'] or a['full_goal_complete']:raise ValueError('Original base and non-promotion required')
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));rows=list(incoming);fields=list(incoming.fieldnames)
        if len(rows)!=len(a['evidence']) or set(fields)!={k for r in a['evidence'] for k in r} or any(row!={k:base_loader.cell(raw.get(k)) for k in fields} for raw,row in zip(a['evidence'],rows)):raise ValueError('Every exact typed source JSON/CSVcell required')
        if a['source_operator']['file']!=native.OPERATOR or a['derived_source_report']['file']!=native.REPORT:raise ValueError('Exact new-cohort source paths required')
        checked_piece(a['source_operator'],reader);checked_piece(a['derived_source_report'],reader);bundle=native.read_bundle(reader);bundle['spatial_admission_report']=json.loads(checked_piece(a['spatial_admission_report'],reader));cohorts.append((a,bundle))
    return (*prior.read_parts({'schema':'osw.current-depth-reference-inventory.v12','base':manifest['base'],'addenda':old},reader),cohorts)


def load_inventory(manifest,reader):
    result=assemble(*read_parts(manifest,reader))
    if result['counts']!=manifest['counts'] or result['metric_counts']!=manifest['metric_counts']:raise ValueError('Reference counts do not reproduce')
    allowed={'schema','status','generator_file','generator_sha256','interpretation','runtime_changed','query_ui_integration_performed','full_goal_complete'}
    if not set(manifest['view_metadata'])<=allowed or any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('No runtime or completion promotion')
    result.update(copy.deepcopy(manifest['view_metadata']));result['inventory_base_file']=manifest['base']['json']['file'];result['inventory_addendum_files']=[p['json']['file'] for p in manifest['addenda']];result['member_depth_index_scope']='base_only_not_updated_for_addenda';return result


def combined_csv_bytes(manifest,reader):
    load_inventory(manifest,reader);first=csv.DictReader(io.StringIO(checked_piece(manifest['base']['csv'],reader).decode()));columns=list(first.fieldnames);rows=list(first)
    for part in manifest['addenda']:
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));columns.extend(k for k in incoming.fieldnames if k not in columns);rows.extend(list(incoming))
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows);return out.getvalue().encode()
