"""Compose already-admitted, hash-pinned catalog entries; never replay fields."""
import copy,csv,io,json
from collections import Counter
from load_current_depth_reference_inventory_v1 import checked_piece,counts_for,cell
from current_depth_cast_time_view_v29 import corrected

STATUS_STAGES={'redsox-published-plume-thickness-v1','pgw-pous-2004-regional-core-thickness-v1',
    'florida-primary-censored-penetration-v1','malvinas-eacc-primary-censored-penetration-v1'}

def refresh(view,update_status=False):
    for r in view['records']:
        r['depth_reference_ids']=[e['id'] for e in view['evidence'] if e['entity_id']==r['entity_id']]
        if update_status:r['status']='scoped_depth_reference' if r['depth_reference_ids'] else 'not_yet_assessed'
    view['counts']=counts_for(view['records'],view['evidence'])
    view['metric_counts']=dict(sorted(Counter(r['metric'] for r in view['evidence']).items()))
    view['coordinate_unit_counts']=dict(sorted(Counter(r['unit'] for r in view['evidence']).items()))

def check_counts(view,manifest):
    for k in ['counts','metric_counts','coordinate_unit_counts']:
        if view[k]!=manifest[k]:raise ValueError('Compiled catalog coverage/count mismatch: '+k)

def append(view,part,reader,base_sha=None):
    a=json.loads(checked_piece(part['json'],reader))
    if a['id']!=part['id'] or a.get('runtime_changed') is not False or a.get('full_goal_complete') is not False:
        raise ValueError('Exact already-admitted descriptor identity required')
    if base_sha is not None and a['base_snapshot_sha256']!=base_sha:raise ValueError('Exact compiled base snapshot required')
    rows=list(csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode('utf8'))))
    fields=list(rows[0]) if rows else []
    if len(rows)!=len(a['evidence']) or set(fields)!={k for e in a['evidence'] for k in e} or any(row!={k:cell(e.get(k)) for k in fields} for e,row in zip(a['evidence'],rows)):
        raise ValueError('Compiled JSON/CSV descriptor parity required')
    old={e['id'] for e in view['evidence']};known={r['entity_id'] for r in view['records']}
    if len({e['id'] for e in a['evidence']})!=len(a['evidence']) or any(e['id'] in old or e['entity_id'] not in known for e in a['evidence']):
        raise ValueError('Duplicate reference or unknown compiled owner')
    if set(view['source_contexts'])&set(a['source_contexts']):raise ValueError('Compiled context overwrite forbidden')
    view['evidence'].extend(copy.deepcopy(a['evidence']));view['source_contexts'].update(copy.deepcopy(a['source_contexts']))
    refresh(view,part['id'] in STATUS_STAGES)

def load_inventory(manifest,reader):
    schema=manifest['schema']
    if schema=='osw.current-depth-reference-inventory.v28':
        view=json.loads(checked_piece(manifest['base']['json'],reader))
        base_rows=list(csv.DictReader(io.StringIO(checked_piece(manifest['base']['csv'],reader).decode('utf8'))))
        if [r['id'] for r in base_rows]!=[r['id'] for r in view['evidence']]:raise ValueError('Frozen base CSV identity/order mismatch')
        if counts_for(view['records'],view['evidence'])!=view['counts']:raise ValueError('Compiled base count mismatch')
        view.setdefault('source_contexts',{});seen=set()
        for part in manifest['addenda']:
            if part['id'] in seen:raise ValueError('Duplicate compiled addendum')
            seen.add(part['id']);append(view,part,reader,manifest['base']['json']['sha256'])
        view['inventory_base_file']=manifest['base']['json']['file']
        view['inventory_addendum_files']=[p['json']['file'] for p in manifest['addenda']]
        view['member_depth_index_scope']='base_only_not_updated_for_addenda'
    elif schema=='osw.current-depth-reference-inventory.v29':
        view=load_inventory(json.loads(checked_piece(manifest['previous_inventory'],reader)),reader)
        view=corrected(view,json.loads(checked_piece(manifest['temporal_semantics_correction'],reader)))
        view['temporal_semantics_correction_file']=manifest['temporal_semantics_correction']['file']
    elif schema=='osw.current-depth-reference-inventory.v30':
        view=load_inventory(json.loads(checked_piece(manifest['previous_inventory'],reader)),reader)
        append(view,manifest['reference_addendum'],reader)
    else:raise ValueError('Only admitted v28/v29/v30 compiled manifest forms supported')
    check_counts(view,manifest)
    if any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('No runtime/completion promotion')
    view.update(copy.deepcopy(manifest['view_metadata']))
    return view
