"""Load a frozen depth register plus scoped statistical-thickness addenda."""
import copy,csv,hashlib,io,json,math
from collections import Counter


def checked_piece(piece,reader):
    raw=reader(piece['file'])
    if len(raw)!=piece['bytes'] or hashlib.sha256(raw).hexdigest()!=piece['sha256']:raise ValueError('Reference piece hash/size changed: '+piece['file'])
    return raw


def cell(value):
    if isinstance(value,(list,dict)):return json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)
    return '' if value is None else str(value)


def reference_csv_bytes(evidence):
    columns=list(dict.fromkeys(k for row in evidence for k in row));out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader()
    for row in evidence:writer.writerow({k:cell(v) for k,v in row.items()})
    return out.getvalue().encode('utf8')


def counts_for(records,evidence):
    owners={r['entity_id'] for r in evidence}
    return {'identities':len(records),'depth_references':len(evidence),'identities_with_scoped_depth_reference':len(owners),'identities_not_yet_assessed':len(records)-len(owners),'whole_route_depth_profiles':0,'volume_estimates':0}


def validate_statistical_reference(row,known,contexts):
    if row['entity_id'] not in known or row['metric']!='reported_vertical_thickness' or row['source_context_id'] not in contexts:raise ValueError('Known owner,registered thickness metric and source context required')
    if row['vertical_datum']!='not_applicable_thickness_distance' or row['source_statistic']!='source_reported_mean_over_selected_active_channel_axis_casts' or row['range_kind']!='minimum_and_maximum_among_source_selected_casts':raise ValueError('Thickness statistic must retain its physical meaning')
    context=contexts[row['source_context_id']];rule=context['boundary_rules'].get(row['source_cruise'])
    if rule is None or row['source_channel'] not in ['northern','southern'] or row['source_layer_component'] not in ['bottom','interfacial','whole_plume'] or row['source_top_boundary_speed_threshold_m_s']!=rule['speed_threshold_m_s'] or row['source_top_boundary_salinity_threshold_psu']!=rule['salinity_threshold_psu'] or row['source_top_boundary_direction_departure_degrees']!=45 or row['source_active_flow_cast_selection'] is not True or row['source_layer_cast_sets_overlap'] is not True:raise ValueError('Source layer/channel/cruise boundary and cast-selection context changed')
    if row['unit']!='m' or row['source_top_boundary_operator']!='any_of_speed_less_than_cutoff_OR_direction_departure_greater_than45_OR_salinity_less_than_cutoff' or row['source_bottom_layer_top']!='velocity_maximum_above_seafloor' or row['source_interfacial_layer_extent']!='between_bottom_layer_top_and_plume_top':raise ValueError('Reported units and layer-boundary definitions must remain explicit')
    for k in ['upper_boundary_m','lower_boundary_m','thickness_m','uncertainty_m','annual_range_m','observed_period','calendar_months','same_source_width_reference_id']:
        if row[k] is not None:raise ValueError('Unresolved geometry/time/uncertainty/width cannot be promoted')
    for k in ['whole_current_representative','volume_eligible','physical_state_join_eligible','seasonal_playback_eligible','annual_extrema_eligible','reference_route_projection_eligible','independent_observation_count_claimed','range_is_confidence_interval','seasonal_common_operator_comparison_eligible']:
        if row[k] is not False:raise ValueError('Statistical source reference cannot promote whole-current claims')
    low,high=row['range_m'];mean=row['approximate_value_m']
    if any(type(x) not in [int,float] or not math.isfinite(x) for x in [low,mean,high]) or not 0<=low<=mean<=high or type(row['source_cast_count']) is not int or row['source_cast_count']<=0:raise ValueError('Finite ordered source statistics and positive cast count required')
    if row['source_reported_mean_thickness_m']!=mean or row['source_reported_minimum_thickness_m']!=low or row['source_reported_maximum_thickness_m']!=high:raise ValueError('Reported values must reconcile without converting the range')


def assemble(base,addenda):
    result=copy.deepcopy(base);records=result['records'];evidence=result['evidence'];known={r['entity_id'] for r in records};seen={r['id'] for r in evidence};contexts=result.setdefault('source_contexts',{})
    if len(known)!=len(records) or len(seen)!=len(evidence) or any(r['entity_id'] not in known for r in evidence):raise ValueError('Duplicate base identity/reference or unknown owner')
    if counts_for(records,evidence)!=base['counts']:raise ValueError('Base coverage does not reproduce')
    for record in records:
        if record['depth_reference_ids']!=[r['id'] for r in evidence if r['entity_id']==record['entity_id']]:raise ValueError('Base reference ownership does not reproduce')
    for addendum in addenda:
        if set(contexts)&set(addendum['source_contexts']):raise ValueError('Source context overwrite forbidden')
        contexts.update(copy.deepcopy(addendum['source_contexts']))
        for ref in addendum['evidence']:
            if ref['id'] in seen:raise ValueError('Duplicate depth reference')
            validate_statistical_reference(ref,known,contexts);seen.add(ref['id']);evidence.append(copy.deepcopy(ref))
    for record in records:
        record['depth_reference_ids']=[r['id'] for r in evidence if r['entity_id']==record['entity_id']]
        record['status']='scoped_depth_reference' if record['depth_reference_ids'] else 'not_yet_assessed'
    result['counts']=counts_for(records,evidence);result['metric_counts']=dict(sorted(Counter(r['metric'] for r in evidence).items()))
    return result


def read_parts(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v1':raise ValueError('Known reference inventory schema required')
    base=json.loads(checked_piece(manifest['base']['json'],reader));first=csv.DictReader(io.StringIO(checked_piece(manifest['base']['csv'],reader).decode('utf8')));base_rows=list(first)
    if [r['id'] for r in base_rows]!=[r['id'] for r in base['evidence']]:raise ValueError('Frozen base CSV reference order/IDs changed')
    addenda=[];seen=set()
    for part in manifest['addenda']:
        if part['id'] in seen:raise ValueError('Duplicate addendum identity')
        seen.add(part['id']);a=json.loads(checked_piece(part['json'],reader))
        if a['schema']!='osw.current-depth-statistical-thickness-addendum.v1' or a['id']!=part['id'] or a['base_snapshot_sha256']!=manifest['base']['json']['sha256'] or a['runtime_changed'] or a['full_goal_complete']:raise ValueError('Addendum schema/base/claim mismatch')
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode('utf8')));rows=list(incoming);fields=list(incoming.fieldnames)
        if len(rows)!=len(a['evidence']) or set(fields)!={k for r in a['evidence'] for k in r}:raise ValueError('All and only reference CSV fields/rows required')
        for raw,row in zip(a['evidence'],rows):
            if row!={k:cell(raw.get(k)) for k in fields}:raise ValueError('Addendum CSV cells do not match JSON source references')
        addenda.append(a)
    return base,addenda


def load_inventory(manifest,reader):
    base,addenda=read_parts(manifest,reader);result=assemble(base,addenda)
    if result['counts']!=manifest['counts'] or result['metric_counts']!=manifest['metric_counts']:raise ValueError('Reference inventory counts do not reproduce')
    allowed={'schema','status','generator_file','generator_sha256','interpretation','runtime_changed','query_ui_integration_performed','full_goal_complete'}
    if not set(manifest['view_metadata'])<=allowed or any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('View metadata cannot overwrite collections or promote runtime/completion')
    result.update(copy.deepcopy(manifest['view_metadata']));result['inventory_base_file']=manifest['base']['json']['file'];result['inventory_addendum_files']=[p['json']['file'] for p in manifest['addenda']]
    return result


def combined_csv_bytes(manifest,reader):
    load_inventory(manifest,reader)
    first=csv.DictReader(io.StringIO(checked_piece(manifest['base']['csv'],reader).decode('utf8')));columns=list(first.fieldnames);rows=list(first)
    for part in manifest['addenda']:
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode('utf8')));columns.extend(k for k in incoming.fieldnames if k not in columns);rows.extend(list(incoming))
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows)
    return out.getvalue().encode('utf8')
