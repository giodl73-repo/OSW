"""Compose published cast statistics and approximate hydrographic descriptions."""
import copy,csv,io,json,math
from collections import Counter
import load_current_depth_reference_inventory_v1 as prior

checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes


def validate_regional_reference(row,known,contexts):
    if row['entity_id'] not in known or row['metric']!='reported_vertical_thickness' or row['source_context_id'] not in contexts:raise ValueError('Known owner,thickness metric and source context required')
    if row['source_statistic']!='source_approximate_regional_description' or row['source_cast_count'] is not None or row['vertical_datum']!='not_applicable_thickness_distance' or row['unit']!='m':raise ValueError('Approximate prose cannot become a cast mean or sea-surface depth')
    context=contexts[row['source_context_id']]
    if row['source_core_boundary_equation']!=context['boundary_equation'] or row['source_core_boundary_equation']!='(S_max+S_env)/2' or row['source_velocity_boundary_m_s'] is not None or row['source_layer_identity']!='half_salinity_contrast_PGW_core' or row['source_width_thickness_boundary_definition_shared'] is not True:raise ValueError('Hydrographic core definition must remain distinct from a velocity envelope')
    if row['source_section_ids'] not in [['R18'],['R17']] or not row['source_geographic_role'] or row['source_section_positions_reconstructed'] is not False:raise ValueError('Source regional section scope must remain explicit')
    for k in ['upper_boundary_m','lower_boundary_m','thickness_m','uncertainty_m','annual_range_m','observed_period','calendar_months','same_source_width_reference_id','source_reported_mean_thickness_m','source_reported_minimum_thickness_m','source_reported_maximum_thickness_m']:
        if row[k] is not None:raise ValueError('Unreported bounds,cast statistics,dates,width or uncertainty cannot be inferred')
    for k in ['whole_current_representative','volume_eligible','physical_state_join_eligible','seasonal_playback_eligible','annual_extrema_eligible','reference_route_projection_eligible','independent_observation_count_claimed','range_is_confidence_interval','seasonal_common_operator_comparison_eligible']:
        if row[k] is not False:raise ValueError('Regional source description cannot promote global/annual/volume claims')
    number=lambda value:type(value) in [int,float] and math.isfinite(value) and value>=0
    value=row['approximate_value_m'];span=row['range_m']
    if value is None:
        if not isinstance(span,list) or len(span)!=2 or not all(number(x) for x in span) or span[0]>=span[1] or row['range_kind']!='author_approximate_regional_span' or row['source_value_qualifier']!='on_order_of':raise ValueError('Author approximate span required without an invented midpoint')
    elif not number(value) or span is not None or row['range_kind'] is not None or row['source_value_qualifier']!='approximately':raise ValueError('One approximate source value,not a sampled range or exact boundary')


def assemble(base,statistical,regional):
    result=prior.assemble(base,statistical);known={r['entity_id'] for r in result['records']};seen={r['id'] for r in result['evidence']};contexts=result['source_contexts']
    for addendum in regional:
        if set(contexts)&set(addendum['source_contexts']):raise ValueError('Source context overwrite forbidden')
        contexts.update(copy.deepcopy(addendum['source_contexts']))
        for row in addendum['evidence']:
            if row['id'] in seen:raise ValueError('Duplicate source reference')
            validate_regional_reference(row,known,contexts);seen.add(row['id']);result['evidence'].append(copy.deepcopy(row))
    for record in result['records']:
        record['depth_reference_ids']=[r['id'] for r in result['evidence'] if r['entity_id']==record['entity_id']];record['status']='scoped_depth_reference' if record['depth_reference_ids'] else 'not_yet_assessed'
    result['counts']=prior.counts_for(result['records'],result['evidence']);result['metric_counts']=dict(sorted(Counter(r['metric'] for r in result['evidence']).items()))
    return result


def read_parts(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v2':raise ValueError('Known reference inventory v2 schema required')
    statistical_parts=[];regional=[];seen=set()
    for part in manifest['addenda']:
        if part['id'] in seen:raise ValueError('Duplicate addendum identity')
        seen.add(part['id']);addendum=json.loads(checked_piece(part['json'],reader))
        if addendum['schema']=='osw.current-depth-statistical-thickness-addendum.v1':
            if regional:raise ValueError('Frozen statistical pieces must precede regional additions')
            statistical_parts.append(part);continue
        if addendum['schema']!='osw.current-depth-regional-description-addendum.v1' or addendum['id']!=part['id'] or addendum['base_snapshot_sha256']!=manifest['base']['json']['sha256'] or addendum['runtime_changed'] or addendum['full_goal_complete']:raise ValueError('Regional description schema/base/claims changed')
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode('utf8')));rows=list(incoming);fields=list(incoming.fieldnames)
        if len(rows)!=len(addendum['evidence']) or set(fields)!={k for r in addendum['evidence'] for k in r}:raise ValueError('All and only regional CSV fields/rows required')
        for raw,row in zip(addendum['evidence'],rows):
            if row!={k:prior.cell(raw.get(k)) for k in fields}:raise ValueError('Regional CSV cells do not match JSON source references')
        regional.append(addendum)
    legacy={'schema':'osw.current-depth-reference-inventory.v1','base':manifest['base'],'addenda':statistical_parts}
    base,statistical=prior.read_parts(legacy,reader)
    return base,statistical,regional


def load_inventory(manifest,reader):
    base,statistical,regional=read_parts(manifest,reader);result=assemble(base,statistical,regional)
    if result['counts']!=manifest['counts'] or result['metric_counts']!=manifest['metric_counts']:raise ValueError('Combined reference inventory counts do not reproduce')
    allowed={'schema','status','generator_file','generator_sha256','interpretation','runtime_changed','query_ui_integration_performed','full_goal_complete'}
    if not set(manifest['view_metadata'])<=allowed or any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('View cannot overwrite collections or promote runtime/completion')
    result.update(copy.deepcopy(manifest['view_metadata']));result['inventory_base_file']=manifest['base']['json']['file'];result['inventory_addendum_files']=[p['json']['file'] for p in manifest['addenda']];result['member_depth_index_scope']='base_only_not_updated_for_addenda'
    return result


def combined_csv_bytes(manifest,reader):
    load_inventory(manifest,reader);first=csv.DictReader(io.StringIO(checked_piece(manifest['base']['csv'],reader).decode('utf8')));columns=list(first.fieldnames);rows=list(first)
    for part in manifest['addenda']:
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode('utf8')));columns.extend(k for k in incoming.fieldnames if k not in columns);rows.extend(list(incoming))
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows)
    return out.getvalue().encode('utf8')
