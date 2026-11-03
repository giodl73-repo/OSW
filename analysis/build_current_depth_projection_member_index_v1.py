"""Cloud-only discovery joins; no parent depth or new physical measurement."""
import csv
import hashlib
import io
import json
from pathlib import Path
from load_current_depth_projection_inventory_v1 import load_inventory,read_parts

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-projection-member-index-operator-v1.json'
OUT=Path('current-depth-projection-member-index-v1')


def encoded(value):
    return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode('utf8')


def index_view(manifest,view,source,membership,reader):
    records={r['entity_id']:r for r in view['records']}
    conventions={r['entity_id']:(i,r) for i,r in enumerate(membership['conventions'])}
    if len(conventions)!=len(membership['conventions']):raise ValueError('Duplicate declared parent')
    if len(source['records'])!=len(conventions) or {r['entity_id'] for r in source['records']}!=set(conventions):raise ValueError('Declared parent membership changed')
    base,addenda=read_parts(manifest,reader)
    parts=[(manifest['base']['json'],base)]+[(entry['json'],data) for entry,data in zip(manifest['addenda'],addenda)]
    refs={};seen=set()
    context_keys=['snapshot_time_utc','phase_label','campaign_window','source_time_basis','branch_scope','flow_direction_context','metric','primary_threshold_m_s','method_id','comparison_group','selection_depth_interval_m','core_search_depth_interval_m','source_surface_component_gate_m_s','source_section_geometry','reference_geometry_scope','geometry_role','assumptions']
    for piece,data in parts:
        for collection in ['projections','unresolved_reference_cases']:
            for i,case in enumerate(data.get(collection,[])):
                if case['id'] in seen or case['entity_id'] not in records:raise ValueError('Duplicate case or unknown owner')
                seen.add(case['id'])
                ref={'case_id':case['id'],'owner_entity_id':case['entity_id'],'collection':collection,
                     'source_file':piece['file'],'source_sha256':piece['sha256'],'source_pointer':'/'+collection+'/'+str(i),
                     'case_scope':{k:case[k] for k in context_keys if k in case},
                     'whole_current_depth_established':False,'parent_depth_values_inherited':False}
                refs.setdefault(case['entity_id'],[]).append(ref)
    parents=[];linked=set();linked_members=set();rows=[]
    for parent in source['records']:
        entity=parent['entity_id'];i,convention=conventions[entity]
        if entity not in records or parent['identity_level']!=records[entity]['identity_level'] or parent['identity_level'] not in ['family','system']:raise ValueError('Unknown or relabeled parent identity')
        declared=convention['members'];actual=[m['entity_id'] for m in parent['members']]
        if len(set(declared))!=len(declared) or actual!=declared:raise ValueError('Declared member list/order changed')
        if parent['mapping_source_file']!='research/current-length-family-conventions-v1.json' or parent['mapping_source_pointer']!='/conventions/'+str(i):raise ValueError('Existing membership provenance changed')
        members=[]
        for m in parent['members']:
            owner=m['entity_id']
            if owner==entity or owner not in records or m['identity_level']!=records[owner]['identity_level']:raise ValueError('Unknown,recursive or relabeled member')
            member_refs=refs.get(owner,[])
            projected=[r for r in member_refs if r['collection']=='projections'];blocked=[r for r in member_refs if r['collection']=='unresolved_reference_cases']
            members.append({'entity_id':owner,'name':m['name'],'identity_level':m['identity_level'],
                            'source_depth_reference_ids':m['depth_reference_ids'],'regional_projection_refs':projected,'unresolved_reference_case_refs':blocked,
                            'status':'member_regional_cases_available' if projected else 'member_regional_cases_unresolved' if blocked else 'member_not_yet_projected'})
            linked_members.add(owner)
            for r in member_refs:
                linked.add((r['source_file'],r['source_pointer'],r['case_id']))
                rows.append({'parent_entity_id':entity,'member_entity_id':owner,**{k:r[k] for k in ['case_id','collection','source_file','source_sha256','source_pointer']},'parent_depth_m':'','parent_volume_km3':'','new_measurement':False})
        missing=[m['entity_id'] for m in members if not m['regional_projection_refs']]
        parents.append({'entity_id':entity,'name':parent['name'],'identity_level':parent['identity_level'],
                        'status':'member_discovery_only_not_parent_measurement','membership_source_file':'research/current-depth-member-index-v7.json',
                        'membership_source_pointer':'/records/'+str(len(parents)),'membership_scope_note':parent['mapping_scope_note'],
                        'members':members,'members_without_supported_regional_cases':missing,
                        'parent_depth_m':None,'parent_depth_range_m':None,'parent_volume_km3':None,'aggregation_operator':None,
                        'parent_depth_values_inherited':False,'whole_route_depth_profile_established':False,'volume_eligible':False})
    counts={'parents':len(parents),'families':sum(p['identity_level']=='family' for p in parents),'systems':sum(p['identity_level']=='system' for p in parents),
            'member_links':sum(len(p['members']) for p in parents),'distinct_member_identities':len(linked_members),
            'distinct_members_with_supported_regional_cases':sum(any(r['collection']=='projections' for r in refs.get(m,[])) for m in linked_members),
            'parents_with_any_member_regional_case':sum(any(m['regional_projection_refs'] for m in p['members']) for p in parents),
            'parents_with_all_declared_members_projected':sum(not p['members_without_supported_regional_cases'] for p in parents),
            'distinct_linked_supported_cases':len({r['case_id'] for m in linked_members for r in refs.get(m,[]) if r['collection']=='projections'}),
            'distinct_linked_unresolved_cases':len({r['case_id'] for m in linked_members for r in refs.get(m,[]) if r['collection']=='unresolved_reference_cases'}),
            'deduplicated_source_case_references':len(linked),'discovery_link_rows':len(rows),'new_measurements':0,'new_projection_cases':0,'parent_scalar_depths':0,'parent_volumes':0}
    index={'schema':'osw.current-depth-projection-member-index.v1','status':'MEMBER_OWNED_REGIONAL_CASE_DISCOVERY_NOT_PARENT_DEPTH',
           'counts':counts,'regional_projection_counts_unchanged':view['counts'],'records':parents,
           'interpretation':'Existing catalog membership links original member-owned regional cases and unresolved cases. Shared members/cases deduplicated globally. No length aggregation convention is transferred to depth;no parent scalar,range,volume or physical identity validation is inferred.',
           'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}
    family_map={p['entity_id']:p for p in parents};gaps=[]
    for record in view['records']:
        if record['projection_ids']:continue
        entity=record['entity_id'];parent=family_map.get(entity)
        kind=('declared_member_discovery_not_parent_scalar' if parent else 'family_without_declared_member_mapping' if record['identity_level']=='family' else 'system_requires_scoped_regional_components' if record['identity_level']=='system' else 'regional_model_cases_unresolved' if record['unresolved_reference_case_ids'] else 'regional_model_estimate_not_yet_collected')
        gaps.append({'entity_id':entity,'name':record['name'],'identity_level':record['identity_level'],'gap_kind':kind,
                     'own_source_depth_reference_count':len(record['depth_reference_ids']),'own_unresolved_reference_case_ids':record['unresolved_reference_case_ids'],
                     'member_discovery_available':parent is not None,
                     'members_without_supported_regional_cases':parent['members_without_supported_regional_cases'] if parent else [],
                     'parent_scalar_depth_required_by_this_index':False,'depth_m':None,'volume_km3':None})
    report={'schema':'osw.current-depth-projection-gap-audit.v1','status':'SCOPED_GAPS_WITHOUT_PARENT_SCALAR_FILL',
            'counts':{'identities_without_own_supported_regional_cases':len(gaps),'by_gap_kind':{k:sum(g['gap_kind']==k for g in gaps) for k in sorted({g['gap_kind'] for g in gaps})}},
            'regional_projection_counts_unchanged':view['counts'],'records':gaps,'runtime_changed':False,'full_goal_complete':False}
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=['parent_entity_id','member_entity_id','case_id','collection','source_file','source_sha256','source_pointer','parent_depth_m','parent_volume_km3','new_measurement'],lineterminator='\n');writer.writeheader();writer.writerows(rows)
    return index,report,out.getvalue().encode('utf8')


def build(root=ROOT):
    reader=lambda p:(root/p).read_bytes();op=json.loads(reader(OPERATOR))
    if any(op['eligibility'].values()):raise ValueError('No parent measurement or runtime promotion')
    for p,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(p)).hexdigest()!=pin:raise ValueError('Pinned discovery input changed: '+p)
    manifest=json.loads(reader(op['projection_inventory_file']));source=json.loads(reader(op['member_reference_index_file']));membership=json.loads(reader(op['membership_file']))
    if source['membership_sha256']!=op['input_sha256'][op['membership_file']] or source['depth_register_sha256']!=op['input_sha256'][source['depth_register_file']]:raise ValueError('Existing member source register/membership pins changed')
    view=load_inventory(manifest,reader)
    index,report,csv_raw=index_view(manifest,view,source,membership,reader)
    for data in [index,report]:data.update(operator_file=OPERATOR,operator_sha256=hashlib.sha256(reader(OPERATOR)).hexdigest(),input_sha256=op['input_sha256'])
    return index,report,{'member-index.json':encoded(index),'gap-audit.json':encoded(report),'member-case-links.csv':csv_raw}


def main():
    index,report,pieces=build();OUT.mkdir(exist_ok=True)
    for name,raw in pieces.items():
        if len(raw)>=2500000:raise ValueError('Fixed per-file cap exceeded')
        (OUT/name).write_bytes(raw)
    print(json.dumps({'member_counts':index['counts'],'gap_counts':report['counts']}))


if __name__=='__main__':main()
