"""Keep observed-pair direction-change scenarios distinct from physical depths."""
import copy,csv,io,json,math
from collections import Counter
import load_current_depth_reference_inventory_v1 as base_loader
import load_current_depth_reference_inventory_v4 as prior
from derive_tsushima_observed_pair_depth_v1 import derive_pair

checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes
CONTEXT='tsushima-matsuyama1980-common19day-observed-pair-linear-scenarios'


def validate_row(row,record,context,known):
    if row['entity_id']!='current:tsushima' or row['entity_id'] not in known or record['entity_id']!=row['entity_id'] or context['entity_id']!=row['entity_id'] or row['source_context_id']!=CONTEXT or row['metric']!='derived_two_level_mean_direction_change_depth_scenario':raise ValueError('Known source-specific campaign scenario owner required')
    if row['unit']!='m' or row['vertical_datum']!='local_sea_surface_positive_down' or row['source_statistic']!='source_reported_common_period_mean_signed_alongshore_component_U' or row['source_interpolation_assumption']!='linear_between_two_reported_campaign_means':raise ValueError('Declared units,statistic and interpolation scenario required')
    if context['source_method_family']!='two_level_observed_campaign_mean_linear_direction_change_scenario' or context['physical_current_bottom_established'] is not False:raise ValueError('No source-context physical bottom promotion')
    recomputed=derive_pair(record['source_row'])
    if any(record[k]!=v for k,v in recomputed.items()):raise ValueError('Report must retain the original signed-pair interpolation rule')
    if type(row['approximate_value_m']) not in [int,float] or not math.isfinite(row['approximate_value_m']) or not record['eligible'] or row['approximate_value_m']!=record['linear_scenario_depth_m']:raise ValueError('Exact audited conditional scenario value required')
    for key in ['range_m','lower_bound_m','lower_bound_operator','upper_bound_m','upper_boundary_m','lower_boundary_m','thickness_m','uncertainty_m','annual_range_m','calendar_months','same_source_width_reference_id','source_sampled_lon_lat']:
        if row[key] is not None:raise ValueError('No physical boundary,annual range,coordinate or volume promotion')
    for key in ['whole_current_representative','volume_eligible','physical_state_join_eligible','seasonal_playback_eligible','annual_extrema_eligible','reference_route_projection_eligible','independent_observation_count_claimed','physical_current_bottom_established','source_zero_crossing_uniqueness_established','source_raw_profile_reconstructed']:
        if row[key] is not False:raise ValueError('Sparse observed means do not establish a physical current profile')
    if row['source_observed_pair']!=record['source_row'] or row['source_open_direction_change_bracket_m']!=record['open_depth_bracket_m'] or row['observed_period']!=record['table_mean_period'] or row['observed_period']!=context['table_mean_period']:raise ValueError('Exact source pair,bracket and common averaging period required')
    if row['source_bracket_endpoints_excluded'] is not True or not row['source_open_direction_change_bracket_m'][0]<row['approximate_value_m']<row['source_open_direction_change_bracket_m'][1]:raise ValueError('Strictly open original direction-change bracket required')
    for target,source in [('source_facts_file','source_facts_file'),('source_facts_pointer','source_pointer'),('source_facts_sha256','source_facts_sha256')]:
        if row[target]!=record[source]:raise ValueError('Exact observed source-facts provenance required')


def assemble(base,statistical,regional,old_bounds,native_bounds,observed_pairs):
    result=prior.assemble(base,statistical,regional,old_bounds,native_bounds);known={r['entity_id'] for r in result['records']};seen={r['id'] for r in result['evidence']}
    for a,report in observed_pairs:
        if set(a['source_contexts'])!={CONTEXT} or CONTEXT in result['source_contexts']:raise ValueError('Unique source-specific paired-observation context required')
        context=a['source_contexts'][CONTEXT];result['source_contexts'][CONTEXT]=copy.deepcopy(context)
        for row in a['evidence']:
            i=int(row['source_pointer'].split('/')[-1])
            if row['id'] in seen or not 0<=i<len(report['records']) or row['source_pointer']!='/records/'+str(i) or row['source_file']!=a['derived_source_report']['file'] or row['source_sha256']!=a['derived_source_report']['sha256']:raise ValueError('Unique exact audited report provenance required')
            validate_row(row,report['records'][i],context,known);seen.add(row['id']);result['evidence'].append(copy.deepcopy(row))
    for record in result['records']:record['depth_reference_ids']=[r['id'] for r in result['evidence'] if r['entity_id']==record['entity_id']]
    result['counts']=base_loader.counts_for(result['records'],result['evidence']);result['metric_counts']=dict(sorted(Counter(r['metric'] for r in result['evidence']).items()))
    return result


def read_parts(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v5':raise ValueError('Known reference inventory v5 required')
    old=[];pairs=[];seen=set()
    for part in manifest['addenda']:
        if part['id'] in seen:raise ValueError('Duplicate addendum identity')
        seen.add(part['id']);a=json.loads(checked_piece(part['json'],reader))
        if a['schema']!='osw.current-depth-two-level-direction-change-addendum.v1':
            if pairs:raise ValueError('Earlier evidence classes must precede observed-pair scenarios')
            old.append(part);continue
        if a['id']!=part['id'] or a['base_snapshot_sha256']!=manifest['base']['json']['sha256'] or a['runtime_changed'] or a['full_goal_complete']:raise ValueError('Observed-pair source/base/promotion mismatch')
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));rows=list(incoming);fields=list(incoming.fieldnames)
        if len(rows)!=len(a['evidence']) or set(fields)!={k for r in a['evidence'] for k in r}:raise ValueError('Every source-specific CSV field and row required')
        for raw,row in zip(a['evidence'],rows):
            if row!={k:base_loader.cell(raw.get(k)) for k in fields}:raise ValueError('Scenario CSV differs from JSON')
        report=json.loads(checked_piece(a['derived_source_report'],reader));pointers=[r['source_pointer'] for r in a['evidence']];expected={'/records/'+str(i) for i,r in enumerate(report['records']) if r['eligible']}
        if report['schema']!='osw.tsushima-two-level-mean-direction-change-source-report.v1' or any(report[k] for k in ['physical_current_bottom_established','zero_crossing_uniqueness_established','raw_profile_reconstructed','station_geometry_invented','runtime_changed','full_goal_complete']) or report['new_ocean_field_requests']!=0 or len(set(pointers))!=len(pointers) or set(pointers)!=expected or len(pointers)!=report['eligible_scenario_count']:raise ValueError('All and only audited conditional scenarios required')
        pairs.append((a,report))
    return (*prior.read_parts({'schema':'osw.current-depth-reference-inventory.v4','base':manifest['base'],'addenda':old},reader),pairs)


def load_inventory(manifest,reader):
    result=assemble(*read_parts(manifest,reader))
    if result['counts']!=manifest['counts'] or result['metric_counts']!=manifest['metric_counts']:raise ValueError('Reference counts do not reproduce')
    allowed={'schema','status','generator_file','generator_sha256','interpretation','runtime_changed','query_ui_integration_performed','full_goal_complete'}
    if not set(manifest['view_metadata'])<=allowed or any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('No runtime or physical-goal completion promotion')
    result.update(copy.deepcopy(manifest['view_metadata']));result['inventory_base_file']=manifest['base']['json']['file'];result['inventory_addendum_files']=[p['json']['file'] for p in manifest['addenda']];result['member_depth_index_scope']='base_only_not_updated_for_addenda'
    return result


def combined_csv_bytes(manifest,reader):
    load_inventory(manifest,reader);first=csv.DictReader(io.StringIO(checked_piece(manifest['base']['csv'],reader).decode()));columns=list(first.fieldnames);rows=list(first)
    for part in manifest['addenda']:
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));columns.extend(k for k in incoming.fieldnames if k not in columns);rows.extend(list(incoming))
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows)
    return out.getvalue().encode()
