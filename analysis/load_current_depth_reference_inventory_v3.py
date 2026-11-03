"""Compose prior references with audited censored primary penetration bounds."""
import copy,csv,io,json,math
from collections import Counter
import load_current_depth_reference_inventory_v1 as base_loader
import load_current_depth_reference_inventory_v2 as prior

checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes


def validate_bound(row,known,context,record):
    if row['entity_id'] not in known or row['entity_id']!='current:florida' or row['metric']!='derived_supported_component_penetration_lower_bound' or row['vertical_datum']!='local_sea_surface_positive_down' or row['unit']!='m':raise ValueError('Known Florida primary penetration-bound metric required')
    if type(row['lower_bound_m']) not in [int,float] or not math.isfinite(row['lower_bound_m']) or row['lower_bound_m']<=0 or row['lower_bound_operator']!='>=' or row['lower_bound_exclusive'] is not False:raise ValueError('Positive inclusive native supported-reach bound required')
    for key in ['approximate_value_m','range_m','upper_bound_m','upper_boundary_m','lower_boundary_m','thickness_m','uncertainty_m','annual_range_m','observed_period','calendar_months','same_source_width_reference_id']:
        if row[key] is not None:raise ValueError('Censored reach cannot become a resolved depth,range,physical span or volume')
    for key in ['whole_current_representative','volume_eligible','physical_state_join_eligible','seasonal_playback_eligible','annual_extrema_eligible','reference_route_projection_eligible','independent_observation_count_claimed','source_missing_values_interpreted_as_bed','source_bathymetry_used','source_current_axis_independently_validated']:
        if row[key] is not False:raise ValueError('Unreviewed bound/physical promotion')
    if row['source_statistic']!='native_surface_connected_primary_component_supported_reach' or row['source_primary_threshold_m_s']!=.1 or row['source_surface_component_gate_m_s']!=.05 or row['source_component_bearing_degrees_true']!=0 or row['source_core_search_depth_interval_m']!=[0,200] or row['source_primary_lower_status']!='censored_before_missing_or_dry_level':raise ValueError('Original primary/frame/window/censoring rules must be retained')
    if not record['reach_eligible'] or row['lower_bound_m']!=record['lower_bound_m'] or row['source_snapshot_time_utc']!=record['snapshot_time_utc'] or row['source_section_id']!=record['section_id'] or row['source_raw_profile_ref']!=record['source_profile_ref'] or row['source_connected_layer_ref']!=record['source_connected_layer_ref'] or row['source_sampled_lon_lat']!=record['sampled_lon_lat']:raise ValueError('Bound must match its exact audited source record')
    for source,target in [('source_last_connected_native_index','last_connected_native_index'),('source_last_connected_velocity_m_s','last_connected_velocity_m_s'),('source_next_native_depth_m','next_native_depth_m'),('source_selected_column_index','selected_column_index'),('source_raw_section_sha256','source_section_sha256'),('source_horizontal_selection_status','horizontal_selection_status')]:
        if row[source]!=record[target]:raise ValueError('Original native support/selection metadata changed')
    if row['source_next_signed_component_m_s'] is not None or row['upper_bound_exclusive'] is not False:raise ValueError('No invented next signed value or upper boundary')
    layer=record['primary_layer']
    if layer['lower_depth_m'] is not None or layer['layer_thickness_m'] is not None or layer['upper_status']!='surface_bounded_layer' or layer['upper_depth_m']!=0 or layer['lower_status']!=row['source_primary_lower_status'] or layer['lower_last_connected_depth_m']!=row['lower_bound_m'] or record['last_connected_velocity_m_s']<=.1 or record['next_signed_component_m_s'] is not None or record['next_native_depth_m']<=record['lower_bound_m']:raise ValueError('Source support/censoring cannot be repaired into a boundary')
    if context['primary_threshold_m_s']!=.1 or context['physical_current_bottom_established'] is not False:raise ValueError('Source-bound context changed')


def assemble(base,statistical,regional,bounds):
    result=prior.assemble(base,statistical,regional);known={r['entity_id'] for r in result['records']};seen={r['id'] for r in result['evidence']};contexts=result['source_contexts']
    for addendum,report in bounds:
        if set(contexts)&set(addendum['source_contexts']):raise ValueError('Source context overwrite forbidden')
        contexts.update(copy.deepcopy(addendum['source_contexts']))
        for row in addendum['evidence']:
            if row['id'] in seen or row['source_context_id'] not in contexts:raise ValueError('Duplicate bound or unknown source context')
            pointer=row['source_pointer'];index=int(pointer.split('/')[-1])
            if pointer!='/records/'+str(index) or row['source_file']!=addendum['derived_source_report']['file'] or row['source_sha256']!=addendum['derived_source_report']['sha256']:raise ValueError('Exact derived source-report pointer/hash required')
            validate_bound(row,known,contexts[row['source_context_id']],report['records'][index]);seen.add(row['id']);result['evidence'].append(copy.deepcopy(row))
    for record in result['records']:
        record['depth_reference_ids']=[r['id'] for r in result['evidence'] if r['entity_id']==record['entity_id']];record['status']='scoped_depth_reference' if record['depth_reference_ids'] else 'not_yet_assessed'
    result['counts']=base_loader.counts_for(result['records'],result['evidence']);result['metric_counts']=dict(sorted(Counter(r['metric'] for r in result['evidence']).items()))
    return result


def read_parts(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v3':raise ValueError('Known reference inventory v3 schema required')
    old_parts=[];bounds=[];seen=set()
    for part in manifest['addenda']:
        if part['id'] in seen:raise ValueError('Repeated addendum identity')
        seen.add(part['id']);a=json.loads(checked_piece(part['json'],reader))
        if a['schema'] in ['osw.current-depth-statistical-thickness-addendum.v1','osw.current-depth-regional-description-addendum.v1']:
            if bounds:raise ValueError('Prior source classes must precede bound addenda')
            old_parts.append(part);continue
        if a['schema']!='osw.current-depth-supported-penetration-addendum.v1' or a['id']!=part['id'] or a['base_snapshot_sha256']!=manifest['base']['json']['sha256'] or a['runtime_changed'] or a['full_goal_complete']:raise ValueError('Bound addendum source/base/schema/claim mismatch')
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));rows=list(incoming);fields=list(incoming.fieldnames)
        if len(rows)!=len(a['evidence']) or set(fields)!={k for row in a['evidence'] for k in row}:raise ValueError('All bound CSV fields and rows required')
        for raw,row in zip(a['evidence'],rows):
            if row!={k:base_loader.cell(raw.get(k)) for k in fields}:raise ValueError('Bound CSV cells differ from source references')
        report=json.loads(checked_piece(a['derived_source_report'],reader))
        if report['schema']!='osw.florida-primary-censored-penetration-source-report.v1' or report['physical_current_bottom_established'] or report['source_missing_values_interpreted_as_bed'] or report['interpolation_performed'] or report['source_audit']['new_field_requests']!=0:raise ValueError('Scoped source-bound report required')
        pointers=[r['source_pointer'] for r in a['evidence']];expected={'/records/'+str(i) for i,r in enumerate(report['records']) if r['reach_eligible']}
        if len(pointers)!=len(set(pointers)) or set(pointers)!=expected or len(pointers)!=report['admitted_supported_reach_bounds']:raise ValueError('All and only unique audited reach records required')
        bounds.append((a,report))
    legacy={'schema':'osw.current-depth-reference-inventory.v2','base':manifest['base'],'addenda':old_parts};base,statistical,regional=prior.read_parts(legacy,reader)
    return base,statistical,regional,bounds


def load_inventory(manifest,reader):
    base,statistical,regional,bounds=read_parts(manifest,reader);result=assemble(base,statistical,regional,bounds)
    if result['counts']!=manifest['counts'] or result['metric_counts']!=manifest['metric_counts']:raise ValueError('Reference inventory counts do not reproduce')
    allowed={'schema','status','generator_file','generator_sha256','interpretation','runtime_changed','query_ui_integration_performed','full_goal_complete'}
    if not set(manifest['view_metadata'])<=allowed or any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('View cannot overwrite source collections or promote completion')
    result.update(copy.deepcopy(manifest['view_metadata']));result['inventory_base_file']=manifest['base']['json']['file'];result['inventory_addendum_files']=[p['json']['file'] for p in manifest['addenda']];result['member_depth_index_scope']='base_only_not_updated_for_addenda'
    return result


def combined_csv_bytes(manifest,reader):
    load_inventory(manifest,reader);first=csv.DictReader(io.StringIO(checked_piece(manifest['base']['csv'],reader).decode()));columns=list(first.fieldnames);rows=list(first)
    for part in manifest['addenda']:
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));columns.extend(k for k in incoming.fieldnames if k not in columns);rows.extend(list(incoming))
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows)
    return out.getvalue().encode()
