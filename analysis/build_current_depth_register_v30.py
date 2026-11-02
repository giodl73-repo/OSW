"""Retain regional Spitsbergen reach and member-owned depth discovery links."""
import csv, hashlib, io, json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v29 as previous
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v30.json'
RULES='research/current-depth-rules-v30.json'
OUTPUT='research/current-depth-register-v30.json'
CSV='research/current-depth-register-v30.csv'
MEMBER_OUTPUT='research/current-depth-member-index-v1.json'
MEMBERS='research/current-length-family-conventions-v1.json'
validate_reference=previous.validate_reference

def validate_context(row,root=ROOT):
    required={'entity_id':'current:spitsbergen-atlantic','metric':'reported_vertical_extent','evidence_kind':'institutional_observed_survey_summary','source_case_id':'spitsbergen-atlantic-defrost-2016-s1-NW-survey','lower_bound_m':50,'lower_bound_operator':'>','lower_bound_exclusive':True,'depth_basis':'source_reported_flow_behavior_below_depth_within_sampling_domain','source_current_name':'regional_NW_flow_associated_with_West_Spitsbergen_Current','current_identity_assignment':'conditional_regional_NOAA_name_mapping_not_global_synonym','identity_definition_url':'https://tidesandcurrents.noaa.gov/glossary.html','source_site_id':'S1_neighborhood','source_site_coordinates_degrees_minutes':{'latitude_north':[76,26.288],'longitude_east':[13,56.907]},'site_coordinate_role':'mooring_anchor_for_survey_neighborhood','survey_window':{'start':'2016-06-21T15:00:00Z','end':'2016-06-23T02:00:00Z'},'phase_label':'boreal_summer','temporal_operator':'source_twenty_minute_profile_means_during_regional_survey','reported_velocity_sampling_domain_m':[23,300],'source_depth_bin_spacing_m':4,'profile_averaging_minutes':20,'source_speed_description_cm_s':[10,20],'branch_section_scope':'southwest_Spitsbergen_S1_regional_NW_flow','reference_route_projection_eligible':False,'source_access_scope':'primary_institutional_project_report_HTML','same_source_width_reference_id':None,'independent_observation_count_claimed':False}
    for k,v in required.items():
        if row.get(k)!=v:raise ValueError('Source context changed: '+k)
    for k in ['section_sampling_month','section_sampling_window','calendar_months','climatology_years','section_latitude_degrees_north','section_longitude_degrees_east']:
        if row.get(k) is not None:raise ValueError('Regional survey does not establish exact section position/date or climatology')

def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v29.py',RULES,SOURCE,'research/current-length-family-conventions-v1.json']:
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
    return {'schema':'osw.current-depth-register.v30','status':'REGIONAL_SPITSBERGEN_REACH_AND_MEMBER_DEPTH_DISCOVERY',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v30.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v30.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Regional southwest Spitsbergen reach below50m retains conditional name mapping and sampling support. Separate member discovery links do not add parent measurements, numerical family depths, route profiles or volumes.',
            'member_depth_index_file':MEMBER_OUTPUT,'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns += [p for p in ['current_identity_assignment','identity_definition_url','source_site_coordinates_degrees_minutes','site_coordinate_role','survey_window','reported_velocity_sampling_domain_m','source_depth_bin_spacing_m','profile_averaging_minutes','source_speed_description_cm_s'] if p not in columns]
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
    return {'schema':'osw.current-depth-member-index.v1','status':'MEMBER_OWNED_REFERENCE_DISCOVERY_NOT_PARENT_MEASUREMENTS','depth_register_file':OUTPUT,'depth_register_sha256':hashlib.sha256((root/OUTPUT).read_bytes()).hexdigest(),'membership_file':MEMBERS,'membership_sha256':hashlib.sha256(member_raw).hexdigest(),'counts':{'parents':len(rows),'families':8,'systems':1,'member_links':links,'distinct_member_identities':len(all_members),'distinct_member_depth_references':len(all_refs),'parents_with_any_member_depth_evidence':sum(bool(r['linked_reference_count']) for r in rows),'parents_with_all_declared_members_referenced':sum(not r['missing_member_depth_entity_ids'] for r in rows),'new_measurements':0,'whole_route_profiles':0,'volumes':0},'interpretation':'Links retain original member ownership, metrics, dates, branch and scope in the depth register. A parent can be discoverable while its own scalar depth remains unknown. Shared children/references are deduplicated in global counts, never summed as independent measurements. Membership reuses declared catalog conventions, not a new scientific alias admission.','records':rows,'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}
