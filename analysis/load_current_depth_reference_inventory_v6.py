"""Compose source-reported Jutland water-inventory means with earlier classes."""
import copy,csv,io,json
from collections import Counter
import load_current_depth_reference_inventory_v1 as base_loader
import load_current_depth_reference_inventory_v5 as prior

checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes
CONTEXT='jutland-aure1989-salinity-selected-regional-water-inventory'


def validate_row(row,report,context,known):
    if row['entity_id']!='current:jutland' or row['entity_id'] not in known or row['entity_id']!=report['entity_id'] or row['entity_id']!=context['entity_id'] or row['source_context_id']!=CONTEXT or row['metric']!='reported_salinity_selected_area_mean_water_depth':raise ValueError('Source-specific Jutland area-mean depth owner required')
    if row['source_statistic']!=report['source_statistic'] or row['source_statistic']!='source_reported_Ha_Vtot_divided_by_Atot' or row['approximate_value_m']!=22 or row['approximate_value_m']!=report['reported_value_m'] or row['unit']!='m' or row['vertical_datum']!='not_applicable_volume_area_ratio_distance':raise ValueError('Published rounded inventory mean required')
    for key in ['range_m','lower_bound_m','lower_bound_operator','upper_bound_m','upper_boundary_m','lower_boundary_m','thickness_m','uncertainty_m','annual_range_m','calendar_months','observed_period','same_source_width_reference_id','source_sampled_lon_lat']:
        if row[key] is not None:raise ValueError('No boundary,annual,uncertainty,station or volume promotion')
    for key in ['whole_current_representative','volume_eligible','physical_state_join_eligible','seasonal_playback_eligible','annual_extrema_eligible','reference_route_projection_eligible','independent_observation_count_claimed','physical_current_bottom_established','source_value_replaced_by_computed_quotient','source_rounding_is_uncertainty']:
        if row[key] is not False:raise ValueError('Regional inventory mean is not a physical current profile')
    for target,source in [('source_selection','source_selection'),('geographic_scope','geographic_scope'),('source_cruise_window','source_cruise_window'),('source_reported_total_water_volume','reported_total_water_volume'),('source_reported_total_area','reported_total_area'),('source_facts_file','source_facts_file'),('source_facts_sha256','source_facts_sha256')]:
        if row[target]!=report[source]:raise ValueError('Exact salinity/domain/cruise/statistic provenance required')
    if row['source_facts_pointer']!='/reported_average_water_depth_Ha_m' or context['source_average_depth_definition']!='Ha=Vtot/Atot' or context['source_selection']!=report['source_selection'] or context['physical_current_bottom_established'] is not False:raise ValueError('No source metric or boundary substitution')


def assemble(base,statistical,regional,old_bounds,native_bounds,pairs,area_means):
    result=prior.assemble(base,statistical,regional,old_bounds,native_bounds,pairs);known={r['entity_id'] for r in result['records']};seen={r['id'] for r in result['evidence']}
    for a,report in area_means:
        if set(a['source_contexts'])!={CONTEXT} or CONTEXT in result['source_contexts'] or len(a['evidence'])!=1:raise ValueError('One unique source-specific inventory statistic required')
        context=a['source_contexts'][CONTEXT];row=a['evidence'][0]
        if row['id'] in seen or row['source_pointer']!='/reported_value_m' or row['source_file']!=a['derived_source_report']['file'] or row['source_sha256']!=a['derived_source_report']['sha256']:raise ValueError('Exact unique source-report provenance required')
        validate_row(row,report,context,known);result['source_contexts'][CONTEXT]=copy.deepcopy(context);result['evidence'].append(copy.deepcopy(row));seen.add(row['id'])
    for record in result['records']:record['depth_reference_ids']=[r['id'] for r in result['evidence'] if r['entity_id']==record['entity_id']]
    result['counts']=base_loader.counts_for(result['records'],result['evidence']);result['metric_counts']=dict(sorted(Counter(r['metric'] for r in result['evidence']).items()))
    return result


def read_parts(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v6':raise ValueError('Known reference inventory v6 required')
    old=[];means=[];seen=set()
    for part in manifest['addenda']:
        if part['id'] in seen:raise ValueError('Duplicate addendum identity')
        seen.add(part['id']);a=json.loads(checked_piece(part['json'],reader))
        if a['schema']!='osw.current-depth-salinity-selected-area-mean-addendum.v1':
            if means:raise ValueError('Prior source classes must precede area means')
            old.append(part);continue
        if a['id']!=part['id'] or a['base_snapshot_sha256']!=manifest['base']['json']['sha256'] or a['runtime_changed'] or a['full_goal_complete']:raise ValueError('Source/base/promotion mismatch')
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));rows=list(incoming);fields=list(incoming.fieldnames)
        if len(rows)!=len(a['evidence']) or set(fields)!={k for r in a['evidence'] for k in r}:raise ValueError('All area-mean CSV fields/rows required')
        for raw,row in zip(a['evidence'],rows):
            if row!={k:base_loader.cell(raw.get(k)) for k in fields}:raise ValueError('CSV differs from area-mean JSON')
        report=json.loads(checked_piece(a['derived_source_report'],reader))
        if report['schema']!='osw.jutland-area-mean-depth-source-report.v1' or any(report[k] for k in ['physical_current_bottom_established','new_OSW_volume_estimate','runtime_changed','full_goal_complete']) or report['new_ocean_field_requests']!=0 or report['arithmetic_check']['reported_value_replaced'] or report['arithmetic_check']['rounding_is_uncertainty']:raise ValueError('Source statistic cannot promote physical depth/volume')
        means.append((a,report))
    return (*prior.read_parts({'schema':'osw.current-depth-reference-inventory.v5','base':manifest['base'],'addenda':old},reader),means)


def load_inventory(manifest,reader):
    result=assemble(*read_parts(manifest,reader))
    if result['counts']!=manifest['counts'] or result['metric_counts']!=manifest['metric_counts']:raise ValueError('Reference inventory counts do not reproduce')
    allowed={'schema','status','generator_file','generator_sha256','interpretation','runtime_changed','query_ui_integration_performed','full_goal_complete'}
    if not set(manifest['view_metadata'])<=allowed or any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('No runtime/goal completion promotion')
    result.update(copy.deepcopy(manifest['view_metadata']));result['inventory_base_file']=manifest['base']['json']['file'];result['inventory_addendum_files']=[p['json']['file'] for p in manifest['addenda']];result['member_depth_index_scope']='base_only_not_updated_for_addenda'
    return result


def combined_csv_bytes(manifest,reader):
    load_inventory(manifest,reader);first=csv.DictReader(io.StringIO(checked_piece(manifest['base']['csv'],reader).decode()));columns=list(first.fieldnames);rows=list(first)
    for part in manifest['addenda']:
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));columns.extend(k for k in incoming.fieldnames if k not in columns);rows.extend(list(incoming))
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows)
    return out.getvalue().encode()
