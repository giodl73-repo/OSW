"""Observed conditional REDSOX core depths and sampling-censored support bounds."""
import copy,csv,io,json
from collections import Counter
import load_current_depth_reference_inventory_v1 as base
import load_current_depth_reference_inventory_v8 as defaults
import load_current_depth_reference_inventory_v19 as prior

SCHEMA='osw.current-depth-redsox-observed-core-reach-addendum.v1'
FACTS='research/redsox-observed-depth-reference-source-facts-v1.json'
CONTEXT='redsox-rsx1-native-union-conditional-core-and-censored-reach-v2'
OWNER='current:red-sea-saline-overflow'
METRICS=('core_depth','derived_core_connected_component_penetration_lower_bound')
checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes
EXPECTED=[(8,665.197,711.235,'lower-northern-channel',1),(9,695.317,702.097,'lower-northern-channel',2),(73,414.876,442.524,'winter-section3',3),(62,424.593,453.822,'winter-section3',10)]


def validate_facts(f):
    if f['schema']!='osw.redsox-observed-depth-reference-source-facts.v1' or f['entity_id']!=OWNER or f['source_profile_cases']!=4 or f['reference_rows']!=8 or f['original_selected_profile_cases']!=17 or len(f['records'])!=4:raise ValueError('Four original source cases and eight linked metric references required')
    if f['source_review_tests_passed']!=35 or f['new_ocean_field_requests']!=0 or f['new_raw_observations']!=0 or any(f[k] for k in ['independent_observation_count_claimed','physical_current_bottom_established','runtime_changed','full_goal_complete']):raise ValueError('Audited existing observational contexts, not new independent observations or physical bottoms')
    for r,(station,core,reach,section,index) in zip(f['records'],EXPECTED):
        if r['station']!=station or r['campaign']!='RSX1' or r['entity_id']!=OWNER or r['section_id']!=section or r['source_case_pointer']!='/cases/'+str(index) or r['source_case_id']!='redsox-rsx1-'+section+'-'+str(station):raise ValueError('Exact cast identity, section and pointer required')
        if r['core_depth_m']!=core or r['supported_penetration_lower_bound_m']!=reach or r['support_start_depth_m']!=core or r['supported_penetration_lower_bound_exclusive'] is not False:raise ValueError('Exact native core and inclusive last supported native depth, not a seabed or surface-origin extent')
        if r['source_depth_basis']!='provider_reported_LADCP_zz_metres_not_independent_pressure_sensor' or r['selection_height_above_bottom_interval_m']!=[20,200] or r['velocity_threshold_m_s']!=.2 or r['salinity_inclusive_lower_threshold_psu']!=38 or not r['core_component_m_s']>.2 or not r['core_salinity_psu']>=38:raise ValueError('Preserve original component/core definition and joint screen')
        frame='fixed_southward_minus_v' if section=='lower-northern-channel' else 'right_normal_to_original_bent_section'
        group='redsox-rsx1-'+section+'-q0p2-s38-height20-200-native-union-v2'
        if r['component_reference']!=frame or r['comparison_group']!=group or r['lower_status']!='censored_at_native_velocity_sampling_end' or r['lower_boundary_depth_m'] is not None or r['native_union_path_from_core_to_sampling_end_verified'] is not True or r['all_native_hydrographic_knots_retained'] is not True:raise ValueError('Own source frame and verified joint path with sampling censor required')
        for key in ['physical_current_bottom_established','surface_connection_established','physical_cast_identity_independently_verified','sample_level_synchronization_verified','source_reference_quality_independently_verified','tidal_correction_applied','independent_observation_count_claimed','volume_eligible','annual_extrema_established','reference_route_projection_eligible']:
            if r[key] is not False:raise ValueError('No physical, identity, clock, tidal, annual or route promotion')
        for key in ['physical_layer_thickness_m','uncertainty_m','annual_range_m','volume_m3','paired_width_reference_id','observed_period','calendar_months']:
            if r[key] is not None:raise ValueError('Unknown thickness/error/annual/width/volume/common occupation remain null')


def context_id(owner):
    if owner!=OWNER:raise ValueError('Only original Red Sea overflow context owner required')
    return CONTEXT


def source_context(f,owner):
    context_id(owner)
    return {k:copy.deepcopy(f[k]) for k in ['entity_id','source_url','source_citation','source_review_file','source_review_sha256','source_report_pins','source_profile_cases','reference_rows','original_selected_profile_cases','source_review_tests_passed','method_scope','qualifications']}


def reference(f,r,index,piece,metric):
    if metric not in METRICS:raise ValueError('Explicit core or inclusive censored reach metric required')
    row={k:None for k in defaults.NULL_FIELDS};row.update({k:False for k in defaults.FALSE_FIELDS})
    core=metric=='core_depth';suffix='core-depth' if core else 'supported-penetration-lower-bound'
    row.update(id=r['source_case_id']+'-'+suffix+'-v1',entity_id=OWNER,metric=metric,unit='m',approximate_value_m=r['core_depth_m'] if core else None,lower_bound_m=None if core else r['supported_penetration_lower_bound_m'],lower_bound_exclusive=False,range_m=None,vertical_datum='provider_reported_LADCP_depth_positive_down_metres',phase_label='RSX1_winter2001_processed_profile_'+str(r['station']),calendar_months=None,observed_period=None,geographic_scope='Dated local '+r['section_id']+' source station '+str(r['station'])+' in the REDSOX Red Sea outflow context; source-associated conditional classification, not whole-current identity.',temporal_scope='Processed distributed winter2001 source profile with separate LADCP header/CTD start timestamps; not an instantaneous common cast-time proof, survey mean or annual envelope.',source_definition='Native greatest signed component core in original20-200m-above-bed positive interval, conditional on same-coreq>0.2/S>=38.' if core else 'Deepest native velocity sample continuously supported from the same core under piecewise source-adjacentq>0.2/S>=38; deeper endpoint unobserved, not surface-connected penetration or a physical bottom.',evidence_kind='derived_observed_conditional_velocity_core_depth' if core else 'derived_observed_conditional_joint_support_inclusive_reach',source_url=f['source_url'],source_citation=f['source_citation'],source_locator=r['source_report_file']+'#'+r['source_case_pointer'],qualification='Provider station association and source-reported depths retained; independent cast/synchronization/reference/current identity unverified. Sampling-end censor is not seabed/current bottom; no physical thickness, uncertainty, annual range, independent observation count, paired width or volume.',source_context_id=CONTEXT,source_file=piece['file'],source_sha256=piece['sha256'],source_pointer='/records/'+str(index)+('/core_depth_m' if core else '/supported_penetration_lower_bound_m'),source_case_id=r['source_case_id'],source_report_file=r['source_report_file'],source_report_sha256=r['source_report_sha256'],source_case_pointer=r['source_case_pointer'],source_profile_core_depth_m=r['core_depth_m'],support_start_depth_m=r['core_depth_m'],surface_connection_established=False,source_depth_basis=r['source_depth_basis'],source_position_lon_lat=copy.deepcopy(r['position_lon_lat']),source_velocity_header_time_utc=r['source_velocity_header_time_utc'],source_ctd_start_time_utc=r['source_ctd_start_time_utc'],source_temporal_operator='distributed_processed_profile_with_distinct_header_and_start_times_not_instantaneous_or_mean',component_reference=r['component_reference'],section_bearing_degrees_true=r['section_bearing_degrees_true'],source_hydrographic_depth_operator=r['source_hydrographic_depth_operator'],comparison_group=r['comparison_group'],selection_height_above_bottom_interval_m=[20,200],velocity_threshold_m_s=.2,salinity_inclusive_lower_threshold_psu=38,core_component_m_s=r['core_component_m_s'],core_salinity_psu=r['core_salinity_psu'],source_lower_status=r['lower_status'],source_lower_boundary_depth_m=None,source_upper_crossing_context=copy.deepcopy(r['upper_crossing_context']),physical_cast_identity_independently_verified=False,sample_level_synchronization_verified=False,source_reference_quality_independently_verified=False,tidal_correction_applied=False,range_is_confidence_interval=False,range_is_annual_envelope=False)
    return row


def assemble(*parts):
    result=prior.assemble(*parts[:-1]);seen={r['id'] for r in result['evidence']}
    for a,f in parts[-1]:
        validate_facts(f);expected=[reference(f,r,i,a['reviewed_source_facts'],metric) for i,r in enumerate(f['records']) for metric in METRICS];contexts={CONTEXT:source_context(f,OWNER)}
        if a['evidence']!=expected or a['source_contexts']!=contexts or CONTEXT in result['source_contexts'] or any(r['id'] in seen for r in expected):raise ValueError('Exact station rows and unique source context required')
        seen.update(r['id'] for r in expected);result['evidence'].extend(copy.deepcopy(expected));result['source_contexts'].update(copy.deepcopy(contexts))
    for r in result['records']:r['depth_reference_ids']=[e['id'] for e in result['evidence'] if e['entity_id']==r['entity_id']]
    result['counts']=base.counts_for(result['records'],result['evidence']);result['metric_counts']=dict(sorted(Counter(r['metric'] for r in result['evidence']).items()));result['coordinate_unit_counts']=dict(sorted(Counter(r['unit'] for r in result['evidence']).items()));return result

def read_parts(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v20':raise ValueError('Reference inventoryv20 required')
    old=[];new=[];seen=set()
    for part in manifest['addenda']:
        if part['id'] in seen:raise ValueError('Duplicate addendum identity')
        seen.add(part['id']);a=json.loads(checked_piece(part['json'],reader))
        if a['schema']!=SCHEMA:
            if new:raise ValueError('Original source classes must precede new source')
            old.append(part);continue
        if a['id']!=part['id'] or a['base_snapshot_sha256']!=manifest['base']['json']['sha256'] or a['runtime_changed'] or a['full_goal_complete'] or a['reviewed_source_facts']['file']!=FACTS:raise ValueError('Exact source,base and non-promotion required')
        facts=json.loads(checked_piece(a['reviewed_source_facts'],reader));incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));rows=list(incoming);fields=list(incoming.fieldnames)
        if len(rows)!=len(a['evidence']) or set(fields)!={k for r in a['evidence'] for k in r} or any(row!={k:base.cell(raw.get(k)) for k in fields} for raw,row in zip(a['evidence'],rows)):raise ValueError('Every exact typed JSON/CSV cell required')
        new.append((a,facts))
    if len(new)!=1:raise ValueError('Exactly one new source addendum required')
    return (*prior.read_parts({'schema':'osw.current-depth-reference-inventory.v19','base':manifest['base'],'addenda':old},reader),new)


def load_inventory(manifest,reader):
    result=assemble(*read_parts(manifest,reader))
    if result['counts']!=manifest['counts'] or result['metric_counts']!=manifest['metric_counts'] or result['coordinate_unit_counts']!=manifest['coordinate_unit_counts']:raise ValueError('Every reference count must reproduce')
    allowed={'schema','status','generator_file','generator_sha256','interpretation','runtime_changed','query_ui_integration_performed','full_goal_complete'}
    if not set(manifest['view_metadata'])<=allowed or any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('No runtime or completion promotion')
    result.update(copy.deepcopy(manifest['view_metadata']));result['inventory_base_file']=manifest['base']['json']['file'];result['inventory_addendum_files']=[p['json']['file'] for p in manifest['addenda']];result['member_depth_index_scope']='base_only_not_updated_for_addenda';return result


def combined_csv_bytes(manifest,reader):
    load_inventory(manifest,reader);first=csv.DictReader(io.StringIO(checked_piece(manifest['base']['csv'],reader).decode()));columns=list(first.fieldnames);rows=list(first)
    for part in manifest['addenda']:
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));columns.extend(k for k in incoming.fieldnames if k not in columns);rows.extend(list(incoming))
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows);return out.getvalue().encode()
