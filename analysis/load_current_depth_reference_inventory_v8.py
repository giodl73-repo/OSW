"""Admit audited interval-core minimum reaches without promoting current bottoms."""
import copy,csv,io,json
from collections import Counter
import load_current_depth_reference_inventory_v1 as base_loader
import load_current_depth_reference_inventory_v7 as prior

checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes
METRIC='derived_core_connected_component_penetration_lower_bound'
SCHEMA='osw.current-depth-interval-core-reach-addendum.v1'
NULL_FIELDS=['approximate_value_m','range_m','range_interpretation','upper_bound_m','upper_boundary_m','lower_boundary_m','thickness_m','uncertainty_m','annual_range_m','calendar_months','observed_period','same_source_width_reference_id']
FALSE_FIELDS=['lower_bound_exclusive','upper_bound_exclusive','whole_current_representative','volume_eligible','physical_state_join_eligible','seasonal_playback_eligible','annual_extrema_eligible','reference_route_projection_eligible','independent_observation_count_claimed','physical_current_bottom_established','independently_validated_axis','water_mass_identity_established']


def context_id(record):
    return record['study_id']+'-'+record['entity_id'].split(':',1)[1]+'-original-interval-core-reach'


def source_context(record):
    keys=['entity_id','study_id','branch_scope','primary_threshold_m_s','component_bearing_degrees_true','selection_depth_interval_m','core_search_depth_interval_m','surface_component_gate_m_s']
    return {**{k:copy.deepcopy(record[k]) for k in keys},'support_start':'original_primary_core','physical_current_bottom_established':False}


def reference(record,pointer,source):
    row={k:None for k in NULL_FIELDS};row.update({k:False for k in FALSE_FIELDS})
    row.update(id='interval-core-reach-'+record['study_id']+'-'+record['entity_id'].split(':',1)[1]+'-'+record['snapshot_time_utc'][:10]+'-'+record['section_id'],entity_id=record['entity_id'],metric=METRIC,lower_bound_m=record['lower_bound_m'],lower_bound_operator='>=',unit='m',vertical_datum='local_sea_surface_positive_down',phase_label=record['snapshot_time_utc'],geographic_scope=record['branch_scope'],temporal_scope='Single original 2022 quarterly snapshot; not a seasonal mean, annual range or observed date.',source_definition='Deepest native sampled depth connected to the original interval-selected primary component core above the original threshold. Minimum depth coordinate, not layer thickness or physical current bottom.',evidence_kind='audited_native_model_interval_primary_core_connected_minimum_reach',source_url='https://www.hycom.org/dataserver/gofs-3pt1/analysis',source_citation='Retained GOFS3.1 HYCOM2022 native section fields; original interval selection and primary component threshold retained.',source_locator=record['source_profile_ref'],qualification='Regional fixed-component model context with unvalidated axis and water-mass identity. Missing next level is not zero or seabed. Detached upper boundaries remain detached. No physical depth, uniform span, volume or whole-route inference.',source_context_id=context_id(record),source_contiguous_support_start='original_primary_core',source_file=source['file'],source_sha256=source['sha256'],source_pointer=pointer,source_audit_record=copy.deepcopy(record))
    return row


def eligible_records(report):
    if report['schema']!='osw.interval-core-connected-reach-audit.v1' or report['new_ocean_field_requests']!=0 or report['new_reference_inventory_rows_admitted']!=0 or any(report[k] for k in ['reference_inventory_updated','physical_current_bottom_established','runtime_changed','full_goal_complete']):raise ValueError('Original source audit stage and non-promotion required')
    eligible=[]
    for si,study in enumerate(report['studies']):
        if study['original_projections_and_gaps_unchanged'] is not True:raise ValueError('Original selection must reproduce unchanged')
        for ri,r in enumerate(study['records']):
            if not r['reach_eligible']:continue
            p=r['primary_layer'];core=r['core_native_index'];last=r['last_connected_native_index'];n=r['source_native_level_count']
            if r['study_id']!=study['study_id'] or r['horizontal_selection_status']!='interior_section_integral_maximum_with_finite_neighbors_not_independently_validated_axis' or r['lower_bound_operator']!='>=' or not 0<=core<=last<n or r['lower_bound_m']<=0 or r['lower_bound_m']<r['core_depth_m']:raise ValueError('Original interior core and positive connected minimum required')
            if p['core_index']!=core or p['core_depth_m']!=r['core_depth_m'] or p['core_velocity_m_s']!=r['core_velocity_m_s'] or p['lower_depth_m'] is not None or p['layer_thickness_m'] is not None or r['physical_current_bottom_established'] is not False or r['physical_layer_thickness_m'] is not None:raise ValueError('Original unresolved layer must remain unresolved')
            if p['threshold_m_s']!=r['primary_threshold_m_s'] or min(r['core_velocity_m_s'],r['last_connected_velocity_m_s'])<=r['primary_threshold_m_s'] or r['surface_component_gate_m_s'] is not None:raise ValueError('Original threshold, core and null surface gate required')
            if r['source_surface_connection_established'] is not (p['upper_status']=='surface_bounded_layer' and p['upper_depth_m']==0):raise ValueError('Detached upper boundary cannot become surface connected')
            if p['lower_last_connected_depth_m']!=r['lower_bound_m'] or not r['core_search_depth_interval_m'][0]<=r['core_depth_m']<=r['core_search_depth_interval_m'][1]:raise ValueError('Original core window and last native depth required')
            if r['censoring_kind']=='missing_signed_component_level':
                if p['lower_status']!='censored_before_missing_or_dry_level' or r['next_native_index']!=last+1 or not last+1<n or r['next_native_depth_m']<=r['lower_bound_m'] or r['next_signed_component_m_s'] is not None:raise ValueError('Missing next native sample must remain missing')
            elif r['censoring_kind']=='native_vertical_domain_limit':
                if p['lower_status']!='censored_at_sample_domain_edge' or last!=n-1 or r['lower_bound_m']!=r['source_native_domain_deep_limit_m'] or any(r[k] is not None for k in ['next_native_index','next_native_depth_m','next_signed_component_m_s']):raise ValueError('Domain end requires final native sample')
            else:raise ValueError('Known unresolved censoring class required')
            eligible.append(('/studies/'+str(si)+'/records/'+str(ri),r))
    if len(eligible)!=report['eligible_core_connected_reach_bounds']:raise ValueError('Audit bound count mismatch')
    return eligible


def assemble(base,statistical,regional,old_bounds,native_bounds,pairs,area_means,noncore,interval_bounds):
    result=prior.assemble(base,statistical,regional,old_bounds,native_bounds,pairs,area_means,noncore);known={r['entity_id'] for r in result['records']};seen={r['id'] for r in result['evidence']}
    for a,report in interval_bounds:
        eligible=eligible_records(report);contexts={context_id(r):source_context(r) for _,r in eligible}
        if contexts!=a['source_contexts'] or set(contexts)&set(result['source_contexts']):raise ValueError('Exact uniquely owned original interval contexts required')
        expected=[reference(r,p,a['derived_source_report']) for p,r in eligible]
        if a['evidence']!=expected:raise ValueError('All and only exact eligible source records and limitations required')
        for row in expected:
            if row['id'] in seen or row['entity_id'] not in known:raise ValueError('Unique known direct owner required')
            seen.add(row['id'])
        result['source_contexts'].update(copy.deepcopy(contexts));result['evidence'].extend(copy.deepcopy(expected))
    for r in result['records']:r['depth_reference_ids']=[x['id'] for x in result['evidence'] if x['entity_id']==r['entity_id']]
    result['counts']=base_loader.counts_for(result['records'],result['evidence']);result['metric_counts']=dict(sorted(Counter(r['metric'] for r in result['evidence']).items()))
    return result


def read_parts(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v8':raise ValueError('Known reference inventory v8 required')
    old=[];bounds=[];seen=set()
    for part in manifest['addenda']:
        if part['id'] in seen:raise ValueError('Duplicate addendum identity')
        seen.add(part['id']);a=json.loads(checked_piece(part['json'],reader))
        if a['schema']!=SCHEMA:
            if bounds:raise ValueError('Prior source classes must precede interval bounds')
            old.append(part);continue
        if a['id']!=part['id'] or a['base_snapshot_sha256']!=manifest['base']['json']['sha256'] or a['runtime_changed'] or a['full_goal_complete']:raise ValueError('Original base and admission identity required')
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));rows=list(incoming);fields=list(incoming.fieldnames)
        if len(rows)!=len(a['evidence']) or set(fields)!={k for r in a['evidence'] for k in r} or any(row!={k:base_loader.cell(raw.get(k)) for k in fields} for raw,row in zip(a['evidence'],rows)):raise ValueError('All exact typed JSON/CSV cells required')
        report=json.loads(checked_piece(a['derived_source_report'],reader));bounds.append((a,report))
    return (*prior.read_parts({'schema':'osw.current-depth-reference-inventory.v7','base':manifest['base'],'addenda':old},reader),bounds)


def load_inventory(manifest,reader):
    result=assemble(*read_parts(manifest,reader))
    if result['counts']!=manifest['counts'] or result['metric_counts']!=manifest['metric_counts']:raise ValueError('Reference inventory counts do not reproduce')
    allowed={'schema','status','generator_file','generator_sha256','interpretation','runtime_changed','query_ui_integration_performed','full_goal_complete'}
    if not set(manifest['view_metadata'])<=allowed or any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('No runtime or goal completion promotion')
    result.update(copy.deepcopy(manifest['view_metadata']));result['inventory_base_file']=manifest['base']['json']['file'];result['inventory_addendum_files']=[p['json']['file'] for p in manifest['addenda']];result['member_depth_index_scope']='base_only_not_updated_for_addenda'
    return result


def combined_csv_bytes(manifest,reader):
    load_inventory(manifest,reader);first=csv.DictReader(io.StringIO(checked_piece(manifest['base']['csv'],reader).decode()));columns=list(first.fieldnames);rows=list(first)
    for part in manifest['addenda']:
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));columns.extend(k for k in incoming.fieldnames if k not in columns);rows.extend(list(incoming))
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows)
    return out.getvalue().encode()
