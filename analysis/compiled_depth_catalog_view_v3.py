"""Read already-admitted v28-v40 catalog packets, never native science provenance."""
import copy,csv,io,json
from collections import Counter
from load_current_depth_reference_inventory_v1 import checked_piece,counts_for,cell
METRIC='derived_local_fixed_reference_direction_component_isotach_depth'
REMOVE='metric_frame_is_instantaneous_sample_not_climatology'
STATUS_STAGES={'redsox-published-plume-thickness-v1','pgw-pous-2004-regional-core-thickness-v1','florida-primary-censored-penetration-v1','malvinas-eacc-primary-censored-penetration-v1'}


def corrections():
    return {'schema':'osw.a20-cast-temporal-semantics-correction.v1','metric':METRIC,
        'reference_ids':['gulf-stream-a20-2021-cast-'+s+'-local-frame-'+str(t)+'cms' for s in ['014','015','016'] for t in [5,10,20]],
        'remove_field':REMOVE,'set_fields':{'metric_frame_is_cast_specific_not_climatology':True,
            'source_frame_is_mathematical_instant':False,'source_actual_cast_duration_resolved':False,
            'source_cast_timestamp_role':'provider_nominal_profile_datetime_not_per_depth_measurement_time'},
        'temporal_scope_template':'Processed LADCP cast {datetime}; finite cast duration may combine downcast/upcast measurements. No climatological mean,seasonal phase or annual range.',
        'scientific_depth_values_changed':False,'runtime_changed':False,'full_goal_complete':False}

def corrected(view,correction):
    if correction!=corrections():raise ValueError('Only the exact cast-time terminology correction is permitted')
    out=copy.deepcopy(view);seen=set()
    for row in out['evidence']:
        if row['id'] not in correction['reference_ids']:continue
        if row['metric']!=METRIC or row.get(REMOVE) is not True:raise ValueError('Exact previous local-proxy field required')
        seen.add(row['id']);del row[REMOVE]
        row.update(copy.deepcopy(correction['set_fields']))
        row['temporal_scope']=correction['temporal_scope_template'].format(datetime=row['source_cast_datetime_utc'])
    if seen!=set(correction['reference_ids']):raise ValueError('Exactly nine existing references, no additions/removals')
    if out['counts']!=view['counts']:raise ValueError('No reference-count changes')
    return out

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

def load_legacy(manifest,reader):
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

def metadata_only(manifest):
    allowed={'schema','status','generator_file','generator_sha256','interpretation','runtime_changed','query_ui_integration_performed','full_goal_complete'}
    if not set(manifest['view_metadata'])<=allowed or any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('View metadata cannot shadow catalog data or promote runtime/completion')


def verify_calendar(view,series,raw_csv):
    owner=series['entity_id'];known={e['id']:e for e in view['evidence']};rows=series['months'];counts=series['counts']
    if owner not in {r['entity_id'] for r in view['records']} or series['schema']!='osw.leeuwin-monthly-depth-support-series.v2' or series['site_id']!='WATR50' or len(rows)!=12 or {r['month'] for r in rows}!=set(range(1,13)) or counts!={'calendar_months':12,'finite_boundary_descriptors':9,'censored_support_months':3,'unknown_boundary_months':3}:raise ValueError('Exact admitted twelve-month Leeuwin9finite3censored calendar required')
    if series['annual_depth_range_m'] is not None or series['seasonal_interpolation_performed'] is not False or series['physical_current_bottom_established'] is not False or series['physical_thickness_m'] is not None or series['volume_m3'] is not None:raise ValueError('No finite annual/physical depth or volume promotion')
    used=set();finite=0;censored=0
    for row in rows:
        boundary=row['boundary_reference_id'];support=row['support_reference_id']
        if (boundary is None)==(support is None) or row['sampling_limit_is_boundary'] is not False or row['physical_uncertainty_m'] is not None:raise ValueError('Exactly one boundary or censor-support reference, never physical uncertainty')
        ref=boundary or support
        if ref in used or ref not in known or known[ref]['entity_id']!=owner:raise ValueError('Unique known calendar reference with exact canonical ownership required')
        used.add(ref)
        if boundary is None:
            censored+=1
            if row['display_boundary_depth_m'] is not None or row['computed_zero_crossing_depth_m'] is not None or row['support_lower_bound_m'] is None:raise ValueError('Censor support cannot become a finite monthly boundary')
        else:
            finite+=1
            if row['display_boundary_depth_m']!=known[ref]['approximate_value_m'] or row['computed_zero_crossing_depth_m']!=known[ref]['computed_zero_crossing_depth_m'] or row['support_lower_bound_m'] is not None:raise ValueError('Exact admitted finite boundary descriptor required')
    if (finite,censored)!=(9,3):raise ValueError('Nine boundary and three support months required')
    incoming=list(csv.DictReader(io.StringIO(raw_csv.decode('utf8'))));fields=list(incoming[0]) if incoming else []
    if len(incoming)!=12 or set(fields)!={k for row in rows for k in row} or any(row!={k:cell(e.get(k)) for k in fields} for e,row in zip(rows,incoming)):raise ValueError('Complete admitted calendar JSON/CSV parity required')


def load_inventory(manifest,reader):
    metadata_only(manifest);schema=manifest['schema']
    if schema in {'osw.current-depth-reference-inventory.v28','osw.current-depth-reference-inventory.v29','osw.current-depth-reference-inventory.v30'}:return load_legacy(manifest,reader)
    allowed={'osw.current-depth-reference-inventory.v'+str(v) for v in range(33,41)}
    if schema not in allowed:raise ValueError('Only already-admitted v28/v29/v30/v33-v40 catalog forms supported')
    view=load_inventory(json.loads(checked_piece(manifest['previous_inventory'],reader)),reader)
    append(view,manifest['reference_addendum'],reader)
    if schema=='osw.current-depth-reference-inventory.v33':
        missing=json.loads(checked_piece(manifest['unresolved_contexts'],reader))
        if len(missing['contexts'])!=3 or any(c['lower_depth_m'] is not None or c['canonical_reference_admitted'] is not False for c in missing['contexts']):raise ValueError('Three P06 null unresolved contexts remain outside admitted entries')
    if schema=='osw.current-depth-reference-inventory.v40':
        pieces=manifest['calendar_series'];series=json.loads(checked_piece(pieces['json'],reader));verify_calendar(view,series,checked_piece(pieces['csv'],reader))
        existing=view.setdefault('calendar_depth_series',[])
        if any(s['entity_id']==series['entity_id'] and s['site_id']==series['site_id'] for s in existing):raise ValueError('Duplicate canonical calendar site')
        existing.append(copy.deepcopy(series))
    check_counts(view,manifest);view.update(copy.deepcopy(manifest['view_metadata']));return view
