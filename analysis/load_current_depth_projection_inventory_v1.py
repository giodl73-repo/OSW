"""Read a pinned projection base plus small immutable addenda."""
import copy
import csv
import hashlib
import io
import json


def checked_piece(piece,reader):
    raw=reader(piece['file'])
    if hashlib.sha256(raw).hexdigest()!=piece['sha256'] or len(raw)!=piece['bytes']:raise ValueError('Inventory piece hash/size changed: '+piece['file'])
    return raw


def assemble(base,addenda):
    result=copy.deepcopy(base);known={r['entity_id'] for r in base['records']}
    projections=result['projections'];blocked=result.get('unresolved_reference_cases',[])
    seen={r['id'] for r in projections+blocked}
    if len(seen)!=len(projections)+len(blocked):raise ValueError('Duplicate base reference case')
    fresh=[];fresh_blocked=[]
    for addendum in addenda:
        for key,target,is_blocked in [('projections',fresh,False),('unresolved_reference_cases',fresh_blocked,True)]:
            for case in addendum.get(key,[]):
                if case['id'] in seen or case['entity_id'] not in known:raise ValueError('Duplicate case or unknown current owner')
                if any(case['eligibility'].values()) or case['physical_thickness_m'] is not None:raise ValueError('Unreviewed physical promotion in regional addendum')
                supported=any(a['lower_projection_eligible'] for a in case['anchors'])
                if supported==is_blocked:raise ValueError('Unsupported case in projection collection or supported case marked blocked')
                seen.add(case['id']);target.append(copy.deepcopy(case))
    projections.extend(fresh);blocked.extend(fresh_blocked);result['unresolved_reference_cases']=blocked
    for row in result['records']:
        row['projection_ids']=[p['id'] for p in projections if p['entity_id']==row['entity_id']]
        row['unresolved_reference_case_ids']=[p['id'] for p in blocked if p['entity_id']==row['entity_id']]
        row['projection_status']=('regional_assumed_interpolation_available' if row['projection_ids'] else
            'reference_cases_blocked_no_supported_projection' if row['unresolved_reference_case_ids'] else 'not_yet_projected')
    owners=sum(bool(r['projection_ids']) for r in result['records'])
    counts={k:v for k,v in base['counts'].items() if not k.startswith('new_')}
    counts.update(identities_with_regional_projection_scenarios=owners,identities_not_yet_projected=len(known)-owners,
        identities_with_only_blocked_reference_cases=sum(bool(r['unresolved_reference_case_ids']) and not r['projection_ids'] for r in result['records']),
        identities_without_any_regional_reference_case=sum(not r['unresolved_reference_case_ids'] and not r['projection_ids'] for r in result['records']),
        regional_projection_scenarios=len(projections),unresolved_regional_reference_cases=len(blocked),
        new_model_reference_cases=len(fresh)+len(fresh_blocked),new_supported_model_scenarios=len(fresh),new_blocked_model_reference_cases=len(fresh_blocked),
        new_model_profile_anchors=sum(len(p['anchors']) for p in fresh+fresh_blocked),
        new_projection_eligible_source_nodes=sum(a['lower_projection_eligible'] for p in fresh+fresh_blocked for a in p['anchors']),
        new_conditional_adjacent_segments=sum(s['projection_status']!='gap_no_projection' for p in fresh+fresh_blocked for s in p['segments']),
        new_gap_segments=sum(s['projection_status']=='gap_no_projection' for p in fresh+fresh_blocked for s in p['segments']),new_depth_measurements=0)
    result['counts']=counts
    return result


def read_parts(manifest,reader):
    if manifest['schema']!='osw.current-depth-route-projection-inventory.v1':raise ValueError('Unknown inventory schema')
    base=json.loads(checked_piece(manifest['base']['json'],reader));addenda=[];part_ids=set()
    checked_piece(manifest['base']['csv'],reader)
    if manifest['base'].get('unresolved_csv'):checked_piece(manifest['base']['unresolved_csv'],reader)
    for part in manifest['addenda']:
        if part['id'] in part_ids:raise ValueError('Repeated addendum ID')
        part_ids.add(part['id']);addendum=json.loads(checked_piece(part['json'],reader))
        if (addendum['schema']!='osw.current-depth-route-projection-addendum.v1'
            or addendum['id']!=part['id']
            or addendum['base_snapshot_sha256']!=manifest['base']['json']['sha256']):raise ValueError('Addendum base/schema mismatch')
        checked_piece(part['csv'],reader);addenda.append(addendum)
    return base,addenda


def load_inventory(manifest,reader):
    base,addenda=read_parts(manifest,reader);result=assemble(base,addenda)
    if result['counts']!=manifest['counts']:raise ValueError('Inventory coverage counts do not reproduce')
    allowed={'schema','status','generator_file','generator_sha256','interpretation','runtime_changed','query_ui_integration_performed','full_goal_complete'}
    if not set(manifest['view_metadata'])<=allowed:raise ValueError('Manifest metadata cannot overwrite scientific collections')
    if any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('Unreviewed integration/completion claim')
    result.update(copy.deepcopy(manifest['view_metadata']))
    result['inventory_base_file']=manifest['base']['json']['file']
    result['inventory_addendum_files']=[p['json']['file'] for p in manifest['addenda']]
    all_pieces=list(manifest['base'].values())+[piece for p in manifest['addenda'] for piece in [p['json'],p['csv']]]
    result['inventory_piece_sha256']={p['file']:p['sha256'] for p in all_pieces}
    result['inventory_source_input_sha256']={p:pin for a in addenda for p,pin in a['input_sha256'].items()}
    return result


def combined_csv_bytes(manifest,reader):
    base,addenda=read_parts(manifest,reader)
    first=csv.DictReader(io.StringIO(checked_piece(manifest['base']['csv'],reader).decode('utf8')))
    columns=list(first.fieldnames);rows=list(first)
    for part,addendum in zip(manifest['addenda'],addenda):
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode('utf8')))
        appended=list(incoming);ids={r['id'] for r in addendum['projections']}
        if {r['projection_id'] for r in appended}!=ids:raise ValueError('Addendum CSV projection IDs disagree with its JSON')
        if len(appended)!=sum(len(p['samples']) for p in addendum['projections']):raise ValueError('Addendum CSV sample count changed')
        columns.extend(k for k in incoming.fieldnames if k not in columns);rows.extend(appended)
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows)
    return out.getvalue().encode('utf8')
