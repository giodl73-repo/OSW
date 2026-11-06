"""Append regional Gulf Stream deep presence without inferring a bottom."""
import csv, hashlib, io, json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v36 as previous
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v37.json'
RULES='research/current-depth-rules-v37.json'
OUTPUT='research/current-depth-register-v37.json'
CSV='research/current-depth-register-v37.csv'
MEMBER_OUTPUT='research/current-depth-member-index-v6.json'
MEMBERS='research/current-length-family-conventions-v1.json'
validate_reference=previous.validate_reference
EXPECTED_REFERENCES = {'gulf-stream-johns-1995-68w-deep-presence': {'id': 'gulf-stream-johns-1995-68w-deep-presence', 'entity_id': 'current:gulf-stream', 'metric': 'reported_vertical_extent', 'approximate_value_m': None, 'range_m': None, 'lower_bound_m': 3500, 'lower_bound_exclusive': False, 'upper_bound_m': None, 'upper_bound_exclusive': False, 'range_interpretation': None, 'unit': 'm', 'vertical_datum': 'local_sea_surface_positive_down', 'upper_boundary_m': None, 'lower_boundary_m': None, 'thickness_m': None, 'uncertainty_m': None, 'annual_range_m': None, 'phase_label': None, 'calendar_months': None, 'geographic_scope': 'Gulf Stream near 68W; regional SYNOP array, without an exact latitude or current-axis position assigned.', 'temporal_scope': 'June 1988–August 1990 array deployment; stream-coordinate mean, not a seasonal or instantaneous section.', 'source_definition': 'Deep downstream extension reported at 3500 m. Presence at this level supports an inclusive minimum reach, not a located lower boundary.', 'evidence_kind': 'published_mooring_stream_coordinate_summary', 'source_url': 'https://agupubs.onlinelibrary.wiley.com/doi/10.1029/94JC02497', 'source_citation': 'Johns, Shay, Bane and Watts (1995), J.Geophys.Res.100(C1):817–838, doi:10.1029/94JC02497.', 'source_locator': 'Primary publisher abstract: deployment and stream-coordinate method in opening sentences; deep extension in results paragraph.', 'qualification': 'Local reach only. The 130 km width and 3–4 cm/s speeds describe the deep extension at 3500 m, not a surface or whole-current width. No detected bottom, continuous filled layer, uniform thickness, annual envelope, independent repeat, cross-sectional area or volume is established. Stream-coordinate averaging differs from a fixed Eulerian mean; adjacent westward recirculations are separate. Full methods and original figure pixels were not reviewed.', 'observed_period': None, 'source_case_id': 'gulf-stream-johns-1995-synop68w-stream-coordinate-mean', 'same_source_width_reference_id': None, 'independent_observation_count_claimed': False, 'whole_current_representative': False, 'volume_eligible': False, 'physical_state_join_eligible': False, 'seasonal_playback_eligible': False, 'annual_extrema_eligible': False, 'lower_bound_operator': '>=', 'depth_basis': 'inclusive_reach_from_source_reported_flow_presence_at_depth', 'section_nominal_longitude_degrees_east': -68, 'section_latitude_degrees_north': None, 'source_deployment_month_bounds': ['1988-06', '1990-08'], 'source_mooring_count': 13, 'temporal_operator': 'source_stream_coordinate_mean', 'velocity_frame': 'local_downstream_rotated_and_relative_cross_stream_position_averaged', 'source_access_scope': 'primary_publisher_abstract', 'reference_route_projection_eligible': False, 'reference_route_scope_relation': 'regional_array_without_exact_route_anchor_or_detected_bottom', 'source_deep_level_width_km': 130, 'source_deep_level_speed_range_cm_s': [3, 4], 'source_deep_level_context_depth_m': 3500, 'source_deep_level_width_is_whole_current_width': False}}


def validate_context(row,root=ROOT):
    clean={k:v for k,v in row.items() if k not in ['source_file','source_pointer','source_sha256']}
    if clean!=EXPECTED_REFERENCES.get(row['id']):raise ValueError('Unreviewed Gulf Stream deep presence, averaging frame or scope')


def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v36.py',RULES,SOURCE,MEMBERS,'research/current-depth-member-index-v5.json']:
        pins[p]=hashlib.sha256((root/p).read_bytes()).hexdigest()
    source=json.loads((root/SOURCE).read_bytes());rules=json.loads((root/RULES).read_bytes())
    if source['previous_register_sha256']!=pins[previous.OUTPUT]:raise ValueError('Prior pin mismatch')
    for p,digest in source['source_input_sha256'].items():
        if pins[p]!=digest:raise ValueError('Retained source XML changed')
    evidence=list(prior['evidence']);seen={r['id'] for r in evidence};identities={r['entity_id'] for r in prior['records']}
    for i,row in enumerate(source['references']):
        validate_reference(row,identities,rules['metric_types']);validate_context(row,root)
        if row['id'] in seen:raise ValueError('Duplicate source reference')
        seen.add(row['id']);evidence.append(dict(row,source_file=SOURCE,source_pointer=f'/references/{i}',source_sha256=pins[SOURCE]))
    records=[]
    for raw in prior['records']:
        row=dict(raw);row['depth_reference_ids']=[r['id'] for r in evidence if r['entity_id']==row['entity_id']]
        row['status']='scoped_depth_reference' if row['depth_reference_ids'] else 'not_yet_assessed';records.append(row)
    owners=sum(bool(r['depth_reference_ids']) for r in records)
    return {'schema':'osw.current-depth-register.v37','status':'GULF_STREAM_REGIONAL_DEEP_PRESENCE_NOT_BOTTOM',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v37.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v37.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Gulf Stream deep presence near68W is an inclusive local reach bound from a stream-coordinate mean, not a bottom or thickness. Parent system discovery retains member ownership without assigning a scalar system depth.',
            'metadata_correction_file':prior.get('metadata_correction_file'),'metadata_correction_count':prior.get('metadata_correction_count',0),'member_depth_index_file':MEMBER_OUTPUT,'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns += [p for p in ['source_deployment_month_bounds', 'source_mooring_count', 'velocity_frame', 'source_deep_level_width_km', 'source_deep_level_speed_range_cm_s', 'source_deep_level_context_depth_m', 'source_deep_level_width_is_whole_current_width', 'depth_basis', 'source_access_scope', 'reference_route_scope_relation','source_cross_section_area_km2', 'source_cross_section_area_role', 'source_distance_offshore_km', 'source_distance_offshore_is_current_width', 'source_model_grid_rotation_clockwise_degrees', 'source_signed_alongshore_isotach_m_s', 'model_simulation_period', 'source_record_vertical_datum', 'normalization_file', 'normalization_rule_id','core_latitude_relation', 'source_ship_section_count', 'source_ship_section_year_bounds', 'surface_mean_completion', 'section_latitude_degrees_north','source_record_period', 'source_record_period_has_gaps', 'comparison_products', 'ADCP_velocities_assimilated_in_ECCOv4r4', 'source_raw_ADCP_bin_size_m', 'source_raw_ADCP_sampling_seconds', 'source_processed_ADCP_level_spacing_m', 'source_study_velocity_averaging_hours','source_survey_periods', 'source_ADCP_frequency_kHz', 'source_displayed_ADCP_limit_m', 'station_profile_averaging_definition', 'source_figure4_velocity_quantity', 'source_citation', 'range_interpretation', 'upper_boundary_m', 'lower_boundary_m', 'thickness_m', 'uncertainty_m', 'annual_range_m', 'calendar_months', 'observed_period', 'independent_observation_count_claimed', 'whole_current_representative', 'volume_eligible', 'physical_state_join_eligible', 'seasonal_playback_eligible', 'annual_extrema_eligible','source_research_vessel','source_STF_bracketing_latitude_range_degrees_north','source_STF_bracket_longitude_degrees_east','source_depth_phrase','source_speed_context_cm_s','geostrophic_reference_definition','source_table2_reference_depth_summary_m','source_table2_reference_flag','figure5_reference_policy','source_site_id'] if p not in columns]
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')


def build_member_index(document,root=ROOT):
    source=json.loads((root/SOURCE).read_bytes())
    member_raw=(root/MEMBERS).read_bytes()
    if hashlib.sha256(member_raw).hexdigest()!=source['member_index_policy']['mapping_sha256']:raise ValueError('Member convention pin mismatch')
    conventions=json.loads(member_raw)['conventions']
    entities={r['entity_id']:r for r in document['records']}
    references={r['id']:r for r in document['evidence']}
    if len(references)!=len(document['evidence']):raise ValueError('Duplicate depth reference')
    rows=[];all_refs=set();all_members=set();parents=set();links=0
    for convention in conventions:
        parent_id=convention['entity_id']
        if parent_id in parents or parent_id not in entities:raise ValueError('Duplicate or unknown parent')
        parents.add(parent_id);parent=entities[parent_id]
        if parent['identity_level'] not in ['family','system']:raise ValueError('Parent is not family/system')
        if any(parent.get(k) is not None for k in ['whole_route_depth_m','annual_depth_range_m','volume_km3']):raise ValueError('No scalar parent depth/volume admitted')
        member_ids=convention['members']
        if not member_ids or len(member_ids)!=len(set(member_ids)) or parent_id in member_ids:raise ValueError('Invalid member list')
        members=[];parent_refs=set();missing=[]
        for member_id in member_ids:
            if member_id not in entities or entities[member_id]['identity_level'] not in ['current','segment','system']:raise ValueError('Unknown or invalid member')
            if parent['identity_level']=='family' and entities[member_id]['identity_level']!='current':raise ValueError('Family member is not a basin current')
            member=entities[member_id];ids=member['depth_reference_ids']
            if len(ids)!=len(set(ids)):raise ValueError('Repeated member depth reference')
            for reference_id in ids:
                if reference_id not in references or references[reference_id]['entity_id']!=member_id:raise ValueError('Member reference ownership mismatch')
            parent_refs.update(ids);all_refs.update(ids);all_members.add(member_id);links+=1
            if not ids:missing.append(member_id)
            members.append({'entity_id':member_id,'name':member['name'],'identity_level':member['identity_level'],'depth_reference_ids':list(ids),'status':'scoped_member_references' if ids else 'no_member_depth_reference','current_card_url':member['current_card_url']})
        rows.append({'entity_id':parent_id,'name':parent['name'],'identity_level':parent['identity_level'],'status':'linked_member_evidence_not_parent_depth','mapping_source_file':MEMBERS,'mapping_source_pointer':'/conventions/'+str(len(rows)),'mapping_scope_note':convention['scope_note'],'members':members,'missing_member_depth_entity_ids':missing,'unique_linked_reference_ids':sorted(parent_refs),'linked_reference_count':len(parent_refs),'aggregation_operator':None,'parent_depth_m':None,'parent_depth_range_m':None,'parent_volume_km3':None,'new_measurement_count':0,'whole_route_profile_established':False,'volume_eligible':False})
    if len(rows)!=9 or sum(r['identity_level']=='family' for r in rows)!=8:raise ValueError('Expected eight declared families and strict Gulf Stream System')
    return {'schema':'osw.current-depth-member-index.v6','status':'MEMBER_OWNED_REFERENCE_DISCOVERY_NOT_PARENT_MEASUREMENTS','depth_register_file':OUTPUT,'depth_register_sha256':hashlib.sha256((root/OUTPUT).read_bytes()).hexdigest(),'membership_file':MEMBERS,'membership_sha256':hashlib.sha256(member_raw).hexdigest(),'counts':{'parents':len(rows),'families':8,'systems':1,'member_links':links,'distinct_member_identities':len(all_members),'distinct_member_depth_references':len(all_refs),'parents_with_any_member_depth_evidence':sum(bool(r['linked_reference_count']) for r in rows),'parents_with_all_declared_members_referenced':sum(not r['missing_member_depth_entity_ids'] for r in rows),'new_measurements':0,'whole_route_profiles':0,'volumes':0},'interpretation':'Links retain original member ownership, metrics, dates, branch and scope in the depth register. A parent can be discoverable while its own scalar depth remains unknown. Shared children/references are deduplicated in global counts, never summed as independent measurements. Membership reuses declared catalog conventions, not a new scientific alias admission.','records':rows,'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}
