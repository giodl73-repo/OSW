"""Retain author regional Atlantic cSEC depth and member-owned discovery."""
import csv, hashlib, io, json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v31 as previous
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v32.json'
RULES='research/current-depth-rules-v32.json'
OUTPUT='research/current-depth-register-v32.json'
CSV='research/current-depth-register-v32.csv'
MEMBER_OUTPUT='research/current-depth-member-index-v2.json'
MEMBERS='research/current-length-family-conventions-v1.json'
validate_reference=previous.validate_reference


def validate_context(row,root=ROOT):
    expected={'id': 'atlantic-sec-assuncao-2023-regional100m-extent', 'entity_id': 'current:atlantic-south-equatorial', 'metric': 'reported_vertical_extent', 'approximate_value_m': 100, 'range_m': None, 'lower_bound_m': None, 'lower_bound_exclusive': False, 'upper_bound_m': None, 'upper_bound_exclusive': False, 'range_interpretation': None, 'unit': 'm', 'vertical_datum': 'local_sea_surface_positive_down', 'upper_boundary_m': None, 'lower_boundary_m': None, 'thickness_m': None, 'uncertainty_m': None, 'annual_range_m': None, 'phase_label': None, 'calendar_months': None, 'geographic_scope': 'Offshore South Equatorial Current System along the Fernando de Noronha chain, northeast Brazil; central SEC branch in Figure1, distinct from coastal NBC/NBUC and eastward SEUC. Regional multi-station support, not an exact axis/profile coordinate.', 'temporal_scope': 'ABRACOS1 September–October2015 austral spring and ABRACOS2 April–May2017 austral autumn, RV Antea. One author regional description across the two survey comparisons, not two independent depth measurements or an annual climatology.', 'source_definition': 'Author regional approximate extent of westward surface cSEC down to100m. Numerical value from Results3.1 prose, not a zero-crossing digitized from current-speed magnitude.', 'evidence_kind': 'published_observed_regional_summary', 'source_url': 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0284953', 'source_citation': 'Assunção et al.(2023), Fine-scale vertical relationships between environmental conditions and sound scattering layers in the Southwestern Tropical Atlantic, PLOS ONE18(8):e0284953, doi:10.1371/journal.pone.0284953.', 'source_locator': 'Results3.1 printed/PDF8 second paragraph and Figure4F/caption; Figure1 and Methods2.1 printed/PDF3–4 for identity, survey periods, regional sampling and SADCP averaging.', 'qualification': 'One regional rounded depth summary. No exact lower boundary or100m physical thickness: SADCP nominal support starts15m, and Figure4F shows current magnitude without zonal sign. Direction/identity and100m come from prose.15–700m instrument range and500m displayed ADCP limit are not current boundaries. Shaded standard deviations describe velocity profiles, not depth uncertainty. Autumn2017 stronger cSEC and spring2015 stronger SEUC are qualitative source comparisons, not depth extrema or a seasonal depth envelope. Do not inherit NBUC140–320m, shear40–140m or320–450m, epipelagic200m, CTD1000m, acoustic backscatter layers or their thresholds. No whole-route projection, width join or volume.', 'observed_period': None, 'source_case_id': 'atlantic-sec-assuncao-2023-abracos-regional-comparison', 'same_source_width_reference_id': None, 'independent_observation_count_claimed': False, 'whole_current_representative': False, 'volume_eligible': False, 'physical_state_join_eligible': False, 'seasonal_playback_eligible': False, 'annual_extrema_eligible': False, 'source_current_name': 'central_branch_South_Equatorial_Current_cSEC', 'branch_section_scope': 'Fernando_de_Noronha_chain_offshore_SECS', 'temporal_operator': 'author_regional_summary_across_two_noncontemporaneous_surveys', 'source_survey_periods': [{'survey': 'ABRACOS1', 'start_month': '2015-09', 'end_month': '2015-10', 'austral_season': 'spring'}, {'survey': 'ABRACOS2', 'start_month': '2017-04', 'end_month': '2017-05', 'austral_season': 'autumn'}], 'source_research_vessel': 'Antea', 'source_ADCP_frequency_kHz': 75, 'reported_velocity_sampling_domain_m': [15, 700], 'source_displayed_ADCP_limit_m': 500, 'station_profile_averaging_definition': 'mean_velocity_within_source_reported_0.02_degree_circle_around_each_CTD_profile', 'source_figure4_velocity_quantity': 'current_speed_magnitude_not_signed_zonal_velocity', 'depth_basis': 'source_prose_regional_westward_surface_current_extent', 'source_access_scope': 'original_publisher_PDF_prose_methods_and_figures', 'reference_route_projection_eligible': False}
    immutable=['entity_id','metric','evidence_kind','source_case_id','approximate_value_m','source_current_name','branch_section_scope','temporal_operator','source_survey_periods','source_research_vessel','source_ADCP_frequency_kHz','reported_velocity_sampling_domain_m','source_displayed_ADCP_limit_m','station_profile_averaging_definition','source_figure4_velocity_quantity','depth_basis','source_access_scope','reference_route_projection_eligible','same_source_width_reference_id','independent_observation_count_claimed']
    for key in immutable:
        if row.get(key)!=expected[key]:raise ValueError('Source context changed: '+key)
    for key in ['range_m','lower_bound_m','upper_bound_m','upper_boundary_m','lower_boundary_m','thickness_m','uncertainty_m','annual_range_m','calendar_months','climatology_years','section_sampling_window','section_sampling_month','section_latitude_degrees_north','section_nominal_longitude_degrees_east','observed_period','phase_label']:
        if row.get(key) is not None:raise ValueError('No exact boundary, axis, continuous period or seasonal depth envelope established')


def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v31.py',RULES,SOURCE,MEMBERS,'research/current-depth-member-index-v1.json']:
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
    return {'schema':'osw.current-depth-register.v32','status':'ATLANTIC_CENTRAL_SEC_REGIONAL_DEPTH_AND_UPDATED_MEMBER_DISCOVERY',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v32.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v32.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Atlantic central SEC gains one author regional100m extent reference across two surveys. Survey seasons do not establish annual depth extrema or a whole-route profile. Updated member discovery retains child ownership without parent depth aggregation.',
            'member_depth_index_file':MEMBER_OUTPUT,'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns += [p for p in ['source_survey_periods', 'source_ADCP_frequency_kHz', 'source_displayed_ADCP_limit_m', 'station_profile_averaging_definition', 'source_figure4_velocity_quantity', 'source_citation', 'range_interpretation', 'upper_boundary_m', 'lower_boundary_m', 'thickness_m', 'uncertainty_m', 'annual_range_m', 'calendar_months', 'observed_period', 'independent_observation_count_claimed', 'whole_current_representative', 'volume_eligible', 'physical_state_join_eligible', 'seasonal_playback_eligible', 'annual_extrema_eligible','source_research_vessel','source_STF_bracketing_latitude_range_degrees_north','source_STF_bracket_longitude_degrees_east','source_depth_phrase','source_speed_context_cm_s','geostrophic_reference_definition','source_table2_reference_depth_summary_m','source_table2_reference_flag','figure5_reference_policy','source_site_id'] if p not in columns]
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
    return {'schema':'osw.current-depth-member-index.v2','status':'MEMBER_OWNED_REFERENCE_DISCOVERY_NOT_PARENT_MEASUREMENTS','depth_register_file':OUTPUT,'depth_register_sha256':hashlib.sha256((root/OUTPUT).read_bytes()).hexdigest(),'membership_file':MEMBERS,'membership_sha256':hashlib.sha256(member_raw).hexdigest(),'counts':{'parents':len(rows),'families':8,'systems':1,'member_links':links,'distinct_member_identities':len(all_members),'distinct_member_depth_references':len(all_refs),'parents_with_any_member_depth_evidence':sum(bool(r['linked_reference_count']) for r in rows),'parents_with_all_declared_members_referenced':sum(not r['missing_member_depth_entity_ids'] for r in rows),'new_measurements':0,'whole_route_profiles':0,'volumes':0},'interpretation':'Links retain original member ownership, metrics, dates, branch and scope in the depth register. A parent can be discoverable while its own scalar depth remains unknown. Shared children/references are deduplicated in global counts, never summed as independent measurements. Membership reuses declared catalog conventions, not a new scientific alias admission.','records':rows,'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}
