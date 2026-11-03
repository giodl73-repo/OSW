"""Compose prior references with context-owned native model reach bounds."""
import copy,csv,io,json,math
from collections import Counter
import load_current_depth_reference_inventory_v1 as base_loader
import load_current_depth_reference_inventory_v3 as prior

checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes


def validate_native_bound(row,known,context,record):
    if row['entity_id'] not in known or row['entity_id']!=context['entity_id'] or row['entity_id']!=record['entity_id'] or row['metric']!='derived_supported_component_penetration_lower_bound' or row['vertical_datum']!='local_sea_surface_positive_down' or row['unit']!='m':raise ValueError('Known context-owned native penetration bound required')
    if row['source_statistic']!='native_surface_connected_primary_component_supported_reach' or context['source_method_family']!='classic_upper200_surface_connected_integral' or context['core_search_depth_interval_m']!=[0,200]:raise ValueError('Declared original source method family required')
    if type(row['lower_bound_m']) not in [int,float] or not math.isfinite(row['lower_bound_m']) or row['lower_bound_m']<=0 or row['lower_bound_operator']!='>=' or row['lower_bound_exclusive'] is not False or row['upper_bound_exclusive'] is not False:raise ValueError('Positive inclusive native lower bound required')
    for key in ['approximate_value_m','range_m','upper_bound_m','upper_boundary_m','lower_boundary_m','thickness_m','uncertainty_m','annual_range_m','observed_period','calendar_months','same_source_width_reference_id']:
        if row[key] is not None:raise ValueError('No exact depth,physical span,annual or volume promotion')
    for key in ['whole_current_representative','volume_eligible','physical_state_join_eligible','seasonal_playback_eligible','annual_extrema_eligible','reference_route_projection_eligible','independent_observation_count_claimed','source_missing_values_interpreted_as_bed','source_bathymetry_used','source_current_axis_independently_validated','source_native_endpoint_is_current_bottom']:
        if row[key] is not False:raise ValueError('Censored support is not a physical current boundary')
    for source,target in [('source_primary_threshold_m_s','primary_threshold_m_s'),('source_surface_component_gate_m_s','surface_component_gate_m_s'),('source_component_bearing_degrees_true','component_bearing_degrees_true'),('source_core_search_depth_interval_m','core_search_depth_interval_m')]:
        if row[source]!=context[target] or row[source]!=record[target]:raise ValueError('Original per-current threshold/frame/window/gates changed')
    fields={'lower_bound_m':'lower_bound_m','source_snapshot_time_utc':'snapshot_time_utc','source_section_id':'section_id','source_raw_profile_ref':'source_profile_ref','source_connected_layer_ref':'source_connected_layer_ref','source_sampled_lon_lat':'sampled_lon_lat','source_last_connected_native_index':'last_connected_native_index','source_last_connected_velocity_m_s':'last_connected_velocity_m_s','source_next_native_index':'next_native_index','source_next_native_depth_m':'next_native_depth_m','source_selected_column_index':'selected_column_index','source_raw_section_sha256':'source_section_sha256','source_horizontal_selection_status':'horizontal_selection_status','source_censoring_kind':'censoring_kind','source_native_domain_deep_limit_m':'native_domain_deep_limit_m','source_native_level_count':'native_level_count'}
    if not record['reach_eligible'] or row['source_snapshot_time_utc'] not in context['snapshot_times_utc']:raise ValueError('Audited original snapshot reach required')
    for source,target in fields.items():
        if row[source]!=record[target]:raise ValueError('Exact native support/provenance metadata changed')
    layer=record['primary_layer'];threshold=context['primary_threshold_m_s']
    if layer['threshold_m_s']!=threshold or layer['lower_depth_m'] is not None or layer['layer_thickness_m'] is not None or layer['upper_status']!='surface_bounded_layer' or layer['upper_depth_m']!=0 or layer['lower_last_connected_depth_m']!=row['lower_bound_m'] or row['source_primary_lower_status']!=layer['lower_status'] or record['last_connected_velocity_m_s']<=threshold or row['source_next_signed_component_m_s'] is not None or record['next_signed_component_m_s'] is not None:raise ValueError('Censoring/support cannot be repaired into a resolved boundary')
    if row['source_censoring_kind']=='missing_signed_component_level':
        if layer['lower_status']!='censored_before_missing_or_dry_level' or row['source_next_native_level_exists'] is not True or record['next_native_index']!=record['last_connected_native_index']+1 or record['next_native_depth_m']<=record['lower_bound_m']:raise ValueError('Missing-level censoring class changed')
    elif row['source_censoring_kind']=='native_vertical_domain_limit':
        if layer['lower_status']!='censored_at_sample_domain_edge' or row['source_next_native_level_exists'] is not False or record['next_native_index'] is not None or record['next_native_depth_m'] is not None or record['last_connected_native_index']!=record['native_level_count']-1 or record['lower_bound_m']!=record['native_domain_deep_limit_m']:raise ValueError('Native-domain censoring class changed')
    else:raise ValueError('Unknown source censoring class')
    if context['physical_current_bottom_established'] is not False:raise ValueError('No physical bottom interpretation')


def assemble(base,statistical,regional,old_bounds,native_bounds):
    result=prior.assemble(base,statistical,regional,old_bounds);known={r['entity_id'] for r in result['records']};seen={r['id'] for r in result['evidence']};contexts=result['source_contexts']
    for a,report in native_bounds:
        if set(contexts)&set(a['source_contexts']):raise ValueError('Source context overwrite forbidden')
        contexts.update(copy.deepcopy(a['source_contexts']))
        for row in a['evidence']:
            if row['id'] in seen or row['source_context_id'] not in contexts:raise ValueError('Duplicate reference or unknown source context')
            i=int(row['source_pointer'].split('/')[-1])
            if row['source_pointer']!='/records/'+str(i) or row['source_file']!=a['derived_source_report']['file'] or row['source_sha256']!=a['derived_source_report']['sha256']:raise ValueError('Exact source-report pointer/hash required')
            validate_native_bound(row,known,contexts[row['source_context_id']],report['records'][i]);seen.add(row['id']);result['evidence'].append(copy.deepcopy(row))
    for record in result['records']:
        record['depth_reference_ids']=[r['id'] for r in result['evidence'] if r['entity_id']==record['entity_id']];record['status']='scoped_depth_reference' if record['depth_reference_ids'] else 'not_yet_assessed'
    result['counts']=base_loader.counts_for(result['records'],result['evidence']);result['metric_counts']=dict(sorted(Counter(r['metric'] for r in result['evidence']).items()))
    return result


def read_parts(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v4':raise ValueError('Known reference inventory v4 required')
    old=[];native=[];seen=set()
    for part in manifest['addenda']:
        if part['id'] in seen:raise ValueError('Duplicate addendum identity')
        seen.add(part['id']);a=json.loads(checked_piece(part['json'],reader))
        if a['schema'] in ['osw.current-depth-statistical-thickness-addendum.v1','osw.current-depth-regional-description-addendum.v1','osw.current-depth-supported-penetration-addendum.v1']:
            if native:raise ValueError('Prior source classes must precede native contexts')
            old.append(part);continue
        if a['schema']!='osw.current-depth-native-primary-penetration-addendum.v1' or a['id']!=part['id'] or a['base_snapshot_sha256']!=manifest['base']['json']['sha256'] or a['runtime_changed'] or a['full_goal_complete']:raise ValueError('Native-bound addendum schema/base/claim mismatch')
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));rows=list(incoming);fields=list(incoming.fieldnames)
        if len(rows)!=len(a['evidence']) or set(fields)!={k for r in a['evidence'] for k in r}:raise ValueError('All native-bound CSV fields/rows required')
        for raw,row in zip(a['evidence'],rows):
            if row!={k:base_loader.cell(raw.get(k)) for k in fields}:raise ValueError('Native-bound CSV cells differ from JSON')
        report=json.loads(checked_piece(a['derived_source_report'],reader));pointers=[r['source_pointer'] for r in a['evidence']];expected={'/records/'+str(i) for i,r in enumerate(report['records']) if r['reach_eligible']}
        if report['schema']!='osw.native-primary-censored-penetration-source-report.v1' or report['physical_current_bottom_established'] or report['source_missing_values_interpreted_as_bed'] or report['interpolation_performed'] or report['source_audit']['new_field_requests']!=0 or len(set(pointers))!=len(pointers) or set(pointers)!=expected or len(pointers)!=report['admitted_supported_reach_bounds']:raise ValueError('All and only audited native reach bounds required')
        native.append((a,report))
    base,statistical,regional,old_bounds=prior.read_parts({'schema':'osw.current-depth-reference-inventory.v3','base':manifest['base'],'addenda':old},reader)
    return base,statistical,regional,old_bounds,native


def load_inventory(manifest,reader):
    result=assemble(*read_parts(manifest,reader))
    if result['counts']!=manifest['counts'] or result['metric_counts']!=manifest['metric_counts']:raise ValueError('Reference inventory counts do not reproduce')
    allowed={'schema','status','generator_file','generator_sha256','interpretation','runtime_changed','query_ui_integration_performed','full_goal_complete'}
    if not set(manifest['view_metadata'])<=allowed or any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('No collection overwrite/runtime/completion promotion')
    result.update(copy.deepcopy(manifest['view_metadata']));result['inventory_base_file']=manifest['base']['json']['file'];result['inventory_addendum_files']=[p['json']['file'] for p in manifest['addenda']];result['member_depth_index_scope']='base_only_not_updated_for_addenda'
    return result


def combined_csv_bytes(manifest,reader):
    load_inventory(manifest,reader);first=csv.DictReader(io.StringIO(checked_piece(manifest['base']['csv'],reader).decode()));columns=list(first.fieldnames);rows=list(first)
    for part in manifest['addenda']:
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));columns.extend(k for k in incoming.fieldnames if k not in columns);rows.extend(list(incoming))
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows)
    return out.getvalue().encode()
