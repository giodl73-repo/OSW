"""Normalize legacy core-thickness distance metadata with explicit provenance."""
import copy
import csv
import hashlib
import io
import json
from pathlib import Path
import build_current_depth_register_v34 as previous
from build_current_depth_register_v2 import validate_reference as validate_legacy_core_reference

ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v35.json'
RULES='research/current-depth-rules-v35.json'
CORRECTIONS='research/current-depth-datum-corrections-v1.json'
OUTPUT='research/current-depth-register-v35.json'
CSV='research/current-depth-register-v35.csv'
MEMBER_OUTPUT='research/current-depth-member-index-v5.json'
MEMBERS='research/current-length-family-conventions-v1.json'
IDS=['indian-seuc-chen-2022-core-thickness-east-minimum','indian-seuc-chen-2022-core-thickness-central-maximum','indian-seuc-chen-2022-core-thickness-longitude-median']


def reference_digest(row):
    return hashlib.sha256(json.dumps(row,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def validate_reference(row,identities,metrics):
    if row['metric']!='core_vertical_thickness':return previous.validate_reference(row,identities,metrics)
    if row['vertical_datum']!='not_applicable_thickness_distance':raise ValueError('Core thickness is a distance, not a sea-surface depth')
    validate_legacy_core_reference(dict(row,vertical_datum='local_sea_surface_positive_down'),identities,metrics)


def normalize(prior,manifest):
    if [r['reference_id'] for r in manifest['corrections']]!=IDS:raise ValueError('Only the three reviewed legacy thickness rows may change')
    evidence=copy.deepcopy(prior['evidence']);by_id={r['id']:r for r in evidence}
    for correction in manifest['corrections']:
        row=by_id[correction['reference_id']]
        if reference_digest(row)!=correction['prior_reference_sha256']:raise ValueError('Prior reference context changed')
        if correction['field']!='vertical_datum' or correction['previous_value']!='local_sea_surface_positive_down' or correction['normalized_value']!='not_applicable_thickness_distance' or row['metric']!='core_vertical_thickness' or row['vertical_datum']!=correction['previous_value']:raise ValueError('Unreviewed datum correction')
        row['source_record_vertical_datum']=row['vertical_datum'];row['vertical_datum']=correction['normalized_value']
        row['normalization_file']=CORRECTIONS;row['normalization_rule_id']=correction['id']
    return evidence


def build(root=ROOT):
    read=lambda p:json.loads((root/p).read_bytes());prior=previous.build(root)
    if prior!=read(previous.OUTPUT):raise ValueError('Prior register no longer reproduces')
    source=read(SOURCE);manifest=read(CORRECTIONS);rules=read(RULES)
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v34.py',SOURCE,RULES,CORRECTIONS,MEMBERS,'research/current-depth-member-index-v4.json']:pins[p]=hashlib.sha256((root/p).read_bytes()).hexdigest()
    if source['previous_register_sha256']!=pins[previous.OUTPUT] or manifest['previous_register_sha256']!=pins[previous.OUTPUT]:raise ValueError('Prior register pin mismatch')
    for p,digest in source['source_input_sha256'].items():
        if pins[p]!=digest:raise ValueError('Source normalization input changed')
    evidence=normalize(prior,manifest);identities={r['entity_id'] for r in prior['records']}
    # Earlier generations validate their own versioned schemas in previous.build.
    # Revalidate the three transformed rows under the normalized distance rule.
    for row in evidence:
        if row['id'] in IDS:validate_reference(row,identities,rules['metric_types'])
    numeric_fields=['approximate_value_m','range_m','lower_bound_m','upper_bound_m','upper_boundary_m','lower_boundary_m','thickness_m','uncertainty_m','annual_range_m']
    if any(old.get(k)!=new.get(k) for old,new in zip(prior['evidence'],evidence) for k in numeric_fields):raise ValueError('Normalization must not change measurements')
    return {'schema':'osw.current-depth-register.v35','status':'LEGACY_CORE_THICKNESS_DATUM_NORMALIZED_WITH_PROVENANCE','rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v35.py','generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v35.py').read_bytes()).hexdigest(),'input_sha256':pins,'previous_evidence_preserved':False,'previous_evidence_numerical_values_preserved':True,'previous_evidence_id_order_preserved':[r['id'] for r in evidence]==[r['id'] for r in prior['evidence']],'metadata_correction_file':CORRECTIONS,'metadata_correction_count':3,'new_depth_references':0,'counts':copy.deepcopy(prior['counts']),'metric_counts':copy.deepcopy(prior['metric_counts']),'coverage_interpretation':prior['coverage_interpretation']+' Three legacy core_vertical_thickness records now use a thickness-distance datum in this versioned normalized view. Original source-record datum and correction provenance retained; no numerical evidence added or changed.','member_depth_index_file':MEMBER_OUTPUT,'records':copy.deepcopy(prior['records']),'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns += [p for p in ['source_record_vertical_datum','normalization_file','normalization_rule_id'] if p not in columns]
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
    return {'schema':'osw.current-depth-member-index.v5','status':'MEMBER_OWNED_REFERENCE_DISCOVERY_NOT_PARENT_MEASUREMENTS','depth_register_file':OUTPUT,'depth_register_sha256':hashlib.sha256((root/OUTPUT).read_bytes()).hexdigest(),'membership_file':MEMBERS,'membership_sha256':hashlib.sha256(member_raw).hexdigest(),'counts':{'parents':len(rows),'families':8,'systems':1,'member_links':links,'distinct_member_identities':len(all_members),'distinct_member_depth_references':len(all_refs),'parents_with_any_member_depth_evidence':sum(bool(r['linked_reference_count']) for r in rows),'parents_with_all_declared_members_referenced':sum(not r['missing_member_depth_entity_ids'] for r in rows),'new_measurements':0,'whole_route_profiles':0,'volumes':0},'interpretation':'Links retain original member ownership, metrics, dates, branch and scope in the depth register. A parent can be discoverable while its own scalar depth remains unknown. Shared children/references are deduplicated in global counts, never summed as independent measurements. Membership reuses declared catalog conventions, not a new scientific alias admission.','records':rows,'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}
