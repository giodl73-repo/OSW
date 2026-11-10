"""Cloud-only case-scope audit and collection queue; no depth measurements."""
import copy,csv,hashlib,io,json
from collections import Counter
from pathlib import Path
import build_current_depth_projection_member_index_v2 as frozen_members
from load_current_depth_projection_inventory_v1 import load_inventory,read_parts
from load_current_depth_reference_inventory_v2 import load_inventory as load_references

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-collection-priorities-operator-v1.json'
SCOPE_KEYS=['snapshot_time_utc','phase_label','campaign_window','source_time_basis','source_product_kind','source_period_key','branch_scope','flow_direction_context','metric','primary_threshold_m_s','method_id','comparison_group','selection_depth_interval_m','core_search_depth_interval_m','source_surface_component_gate_m_s','source_section_geometry','reference_geometry_scope','geometry_role','coordinate_kind','assumptions','projection_gate','diagnostic_context_id','vertical_contexts_are_additive','contexts_are_independent_observations','source_mean_context','temporal_operator_class','nominal_provider_period','snapshot_is_applicable','field_geometry_kind','axis_selection_applied','mean_is_mean_of_instantaneous_depths','current_identity_independently_validated','primary_detached_layer_required','independent_latitude_context_required','independent_latitude_context_deg_n','cross_section_is_physical_current_width']


def encoded(value):return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode('utf8')


def case_references(manifest,reader):
    base,addenda=read_parts(manifest,reader);pieces=[(manifest['base']['json'],base)]+[(part['json'],data) for part,data in zip(manifest['addenda'],addenda)];refs=[];seen=set()
    for piece,data in pieces:
        for collection in ['projections','unresolved_reference_cases']:
            for i,case in enumerate(data.get(collection,[])):
                if case['id'] in seen:raise ValueError('Duplicate regional case')
                seen.add(case['id']);refs.append((case,{'case_id':case['id'],'owner_entity_id':case['entity_id'],'collection':collection,'source_file':piece['file'],'source_sha256':piece['sha256'],'source_pointer':'/'+collection+'/'+str(i),'case_scope':{k:copy.deepcopy(case[k]) for k in SCOPE_KEYS if k in case}}))
    return refs


def is_field_section(case):
    kind=case.get('field_geometry_kind')
    if kind is not None and kind not in ['native_zonal_mean_field_section_not_along_current_axis','native_meridional_mean_field_section_not_along_current_axis']:raise ValueError('Unknown explicit field geometry cannot become a route case')
    return kind is not None


def case_summary(case,ref,length):
    field=is_field_section(case);selected=length['selected_route_id'];same=not field and selected is not None and case.get('route_id')==selected and case.get('route_file')==length['record_file']
    anchors=case.get('anchors',[]);explicit=[a for a in anchors if 'lower_projection_eligible' in a];segments=case.get('segments',[])
    if any(type(a['lower_projection_eligible']) is not bool for a in explicit):raise ValueError('Explicit lower eligibility must remain Boolean')
    return {**copy.deepcopy(ref),'geometry_class':'sampled_qualified_mean_cross_section' if field else 'regional_reference_case_geometry','declared_length_route_key_match':same,'route_relation':'cross_section_not_along_current_route' if field else 'no_selected_length_route' if selected is None else 'same_declared_route_key_unvalidated_extent' if same else 'different_or_undocumented_reference_geometry','source_route_id':case.get('route_id'),'source_route_file':case.get('route_file'),'anchor_occurrence_count':len(anchors),'anchors_with_explicit_lower_eligibility':len(explicit),'eligible_lower_anchor_occurrences':sum(a['lower_projection_eligible'] for a in explicit),'legacy_or_other_metric_anchor_occurrences':len(anchors)-len(explicit),'supported_adjacent_segment_occurrences':sum(s['projection_status']!='gap_no_projection' for s in segments),'gap_segment_occurrences':sum(s['projection_status']=='gap_no_projection' for s in segments),'legacy_reported_reference_fraction':case.get('interpolated_editorial_route_fraction'),'legacy_fraction_interpretation':case.get('fraction_interpretation'),'full_current_route_depth_coverage_established':False,'canonical_route_length_fraction_computed':None,'independent_observation_count_claimed':False}


def build_audit(manifest,view,references,length_register,member_source,membership,reader):
    model_records={r['entity_id']:r for r in view['records']};source_records={r['entity_id']:r for r in references['records']};length_records={r['entity_id']:r for r in length_register['records']}
    if len(model_records)!=len(view['records']) or len(source_records)!=len(references['records']) or len(length_records)!=len(length_register['records']) or set(model_records)!=set(source_records) or set(model_records)!=set(length_records):raise ValueError('Exactly matching catalog identity sets required')
    member_index,gaps,csv_raw=frozen_members.index_view(manifest,view,member_source,membership,reader);case_refs=case_references(manifest,reader);by_id={c['id']:(c,ref) for c,ref in case_refs};by_owner={owner:[] for owner in model_records}
    for case,ref in case_refs:
        if case['entity_id'] not in by_owner:raise ValueError('Unknown regional case owner')
        by_owner[case['entity_id']].append(case_summary(case,ref,length_records[case['entity_id']]))
    for parent in member_index['records']:
        for member in parent['members']:
            member['source_depth_reference_ids']=copy.deepcopy(source_records[member['entity_id']]['depth_reference_ids'])
            for ref in member['regional_projection_refs']+member['unresolved_reference_case_refs']:ref['case_scope']=copy.deepcopy(by_id[ref['case_id']][1]['case_scope'])
    member_index.update(revision=3,member_source_reference_inventory_file='research/current-depth-reference-inventory-v2.json',member_reference_ids_refreshed_from_current_inventory=True,case_scope_interpretation='Member support includes qualified mean cross-sections as well as other regional cases. These are not complete routes or inherited parent depths.')
    parents={p['entity_id']:p for p in member_index['records']}
    for row in gaps['records']:row['own_source_depth_reference_count']=len(source_records[row['entity_id']]['depth_reference_ids'])
    gaps.update(revision=3,reference_inventory_file='research/current-depth-reference-inventory-v2.json')
    records=[]
    for original in view['records']:
        owner=original['entity_id'];cases=by_owner[owner];supported=[c for c in cases if c['collection']=='projections'];blocked=[c for c in cases if c['collection']=='unresolved_reference_cases'];fields=[c for c in supported if c['geometry_class']=='sampled_qualified_mean_cross_section'];regional=[c for c in supported if c not in fields];segments=sum(c['supported_adjacent_segment_occurrences'] for c in regional);gap_segments=sum(c['gap_segment_occurrences'] for c in regional)
        if owner in parents:priority='declared_member_discovery_not_parent_scalar';action='Collect and validate member-specific route/time support; do not inherit or average parent depth.'
        elif not supported and original['identity_level']=='system':priority='system_scope_requires_component_or_identity_support';action='Resolve scoped component or continuity identity first; do not manufacture one system-wide scalar depth.'
        elif not supported:priority='regional_cases_unresolved' if blocked else 'no_own_supported_regional_case';action='Resolve current identity and a compatible depth metric, then collect scoped regional profiles under a predeclared method.'
        elif not regional:priority='cross_sections_without_along_current_profile';action='Collect or independently validate along-current geometry and depth anchors; retain existing field cross-sections separately.'
        elif not segments and all(c['anchors_with_explicit_lower_eligibility']>0 for c in regional):priority='regional_points_without_supported_adjacent_segments';action='Collect missing adjacent profile support without replacing rejected anchors or bridging gaps.'
        elif gap_segments:priority='regional_profiles_with_explicit_gaps';action='Collect missing spatial/vertical support for the recorded gap locations; preserve primary thresholds and all rejected anchors.'
        else:priority='regional_extent_and_time_validation_still_required';action='Compare declared route scope and source time/metric definitions before extending spatial or seasonal coverage.'
        rank={'no_own_supported_regional_case':1,'regional_cases_unresolved':1,'cross_sections_without_along_current_profile':2,'regional_points_without_supported_adjacent_segments':3,'regional_profiles_with_explicit_gaps':4,'regional_extent_and_time_validation_still_required':5,'declared_member_discovery_not_parent_scalar':6,'system_scope_requires_component_or_identity_support':6}[priority]
        length=length_records[owner];records.append({'entity_id':owner,'name':original['name'],'identity_level':original['identity_level'],'source_depth_reference_count':len(source_records[owner]['depth_reference_ids']),'supported_regional_case_count':len(supported),'unresolved_regional_case_count':len(blocked),'supported_mean_cross_section_count':len(fields),'other_supported_regional_case_count':len(regional),'regional_supported_adjacent_segment_occurrences':segments,'regional_gap_segment_occurrences':gap_segments,'length_route_convention':{k:copy.deepcopy(length[k]) for k in ['selected_route_id','record_file','method','scope']},'cases':cases,'priority_kind':priority,'collection_priority_rank':rank,'next_collection_action':action,'depth_m':None,'annual_depth_range_m':None,'volume_km3':None,'full_current_route_depth_coverage_established':False,'canonical_route_length_fraction_computed':None,'regional_cases_are_independent_observations':False})
    if len(case_refs)!=len(view['projections'])+len(view['unresolved_reference_cases']):raise ValueError('All supported and blocked case references must be retained')
    audit={'schema':'osw.current-depth-collection-priorities.v1','status':'SCOPED_ROUTE_TIME_AND_METRIC_COLLECTION_QUEUE_NOT_FULL_ROUTE_COVERAGE','counts':{'catalog_identities':len(records),'regional_case_references':len(case_refs),'supported_regional_cases':len(view['projections']),'unresolved_regional_cases':len(view['unresolved_reference_cases']),'priorities':dict(sorted(Counter(r['priority_kind'] for r in records).items())),'full_current_route_depth_coverage_established':0,'new_measurements':0,'new_projection_cases':0},'model_projection_counts_unchanged':view['counts'],'reference_counts_unchanged':references['counts'],'records':records,'interpretation':'Route-key equality is a provenance link, not a geometric coverage test. Cross-sections do not establish along-current profiles. Exact case scope/time/mean/branch/method flags remain attached. Counts are case/anchor/segment occurrences, not independent observations or geographic coverage fractions. All whole-current depth/annual/volume values remain unknown.','runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}
    incoming=csv.DictReader(io.StringIO(csv_raw.decode()));fields=list(incoming.fieldnames)+['case_scope_json'];link_rows=list(incoming)
    for row in link_rows:row['case_scope_json']=json.dumps(by_id[row['case_id']][1]['case_scope'],ensure_ascii=False,separators=(',',':'),allow_nan=False)
    links=io.StringIO(newline='');writer=csv.DictWriter(links,fieldnames=fields,lineterminator='\n');writer.writeheader();writer.writerows(link_rows)
    queue=io.StringIO(newline='');fields=['entity_id','name','identity_level','priority_kind','collection_priority_rank','source_depth_reference_count','supported_regional_case_count','unresolved_regional_case_count','supported_mean_cross_section_count','other_supported_regional_case_count','regional_supported_adjacent_segment_occurrences','regional_gap_segment_occurrences','next_collection_action'];writer=csv.DictWriter(queue,fieldnames=fields,lineterminator='\n');writer.writeheader();writer.writerows({k:r[k] for k in fields} for r in sorted(records,key=lambda r:(r['collection_priority_rank'],r['entity_id'])))
    return member_index,gaps,audit,links.getvalue().encode(),queue.getvalue().encode()


def build(root=ROOT):
    reader=lambda f:(root/f).read_bytes();read=lambda f:json.loads(reader(f));op=read(OPERATOR)
    if any(op['eligibility'].values()):raise ValueError('No new measurement,full-route,parent,volume or runtime promotion')
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(f)).hexdigest()!=pin:raise ValueError('Pinned collection-audit input changed: '+f)
    manifest=read(op['projection_inventory_file']);view=load_inventory(manifest,reader);references=load_references(read(op['reference_inventory_file']),reader)
    source=read(op['member_reference_index_file']);membership=read(op['membership_file'])
    if source['membership_sha256']!=op['input_sha256'][op['membership_file']] or source['depth_register_sha256']!=op['input_sha256'][source['depth_register_file']]:raise ValueError('Existing member provenance changed')
    index,gaps,audit,links,queue=build_audit(manifest,view,references,read(op['length_register_file']),source,membership,reader)
    for value in [index,gaps,audit]:value.update(operator_file=OPERATOR,operator_sha256=hashlib.sha256(reader(OPERATOR)).hexdigest(),input_sha256=op['input_sha256'])
    pieces={'member-index.json':encoded(index),'gap-audit.json':encoded(gaps),'collection-priorities.json':encoded(audit),'member-case-links.csv':links,'collection-priorities.csv':queue}
    if any(len(raw)>=2500000 for raw in pieces.values()):raise ValueError('Fixed per-file cap exceeded')
    return index,gaps,audit,pieces


def main():
    index,gaps,audit,pieces=build();out=Path('current-depth-collection-priorities-v1');out.mkdir(exist_ok=True)
    for name,raw in pieces.items():(out/name).write_bytes(raw)
    print(json.dumps({'member_counts':index['counts'],'gap_counts':gaps['counts'],'collection_counts':audit['counts']}))


if __name__=='__main__':main()
