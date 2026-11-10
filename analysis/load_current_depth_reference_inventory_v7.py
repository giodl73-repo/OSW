"""Keep source-selected non-core water-mass extents distinct from core/bottoms."""
import copy,csv,io,json
from collections import Counter
import load_current_depth_reference_inventory_v1 as base_loader
import load_current_depth_reference_inventory_v6 as prior

checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes
CONTEXT='nwasc-baumann1993-2022-selected-noncore'


def validate_row(row,record,context,known):
    if row['entity_id']!='current:norwegian-atlantic-slope' or row['entity_id'] not in known or row['entity_id']!=record['entity_id'] or row['entity_id']!=context['entity_id'] or row['source_context_id']!=CONTEXT or row['metric']!='reported_selected_noncore_water_mass_lower_extent':raise ValueError('Separately owned selected non-core extent required')
    if row['source_statistic']!='source_reported_static_mean_selected_noncore_lower_extent' or row['source_population_role']!='non_core_selected_Atlantic_Water' or context['source_population_role']!=row['source_population_role'] or row['unit']!='m' or row['vertical_datum']!='local_sea_surface_positive_down':raise ValueError('Original non-core population and depth metric required')
    if row['approximate_value_m']!=record['reported_noncore_lower_extent_m'] or row['approximate_value_m']<=record['source_core_lower_extent_m']:raise ValueError('Source non-core extent cannot become core or another depth')
    for key in ['range_m','lower_bound_m','lower_bound_operator','upper_bound_m','upper_boundary_m','lower_boundary_m','thickness_m','uncertainty_m','annual_range_m','calendar_months','observed_period','same_source_width_reference_id','source_sampled_lon_lat']:
        if row[key] is not None:raise ValueError('No physical boundary,span,annual,coordinate or volume promotion')
    for key in ['whole_current_representative','volume_eligible','physical_state_join_eligible','seasonal_playback_eligible','annual_extrema_eligible','reference_route_projection_eligible','independent_observation_count_claimed','physical_current_bottom_established','source_core_comparison_is_error_bar']:
        if row[key] is not False:raise ValueError('Selected non-core extent is not a whole-current depth')
    fields={'source_section_id':'section_id','source_figure_panel':'source_figure_panel','source_existing_core_reference_id':'existing_core_reference_id','source_core_lower_extent_m':'source_core_lower_extent_m','source_shoreward_isobath_gate_m':'shoreward_isobath_gate_m','source_xml_file':'source_xml_file','source_xml_paragraph_index':'source_xml_paragraph_index','source_xml_normalized_paragraph_sha256':'source_xml_normalized_paragraph_sha256','source_selection':'source_selection','source_mean_definition_years':'source_mean_definition_years'}
    if row['source_selection']!=context['source_selection'] or row['source_mean_definition_years']!=context['source_mean_definition_years'] or context['physical_current_bottom_established'] is not False:raise ValueError('Static source definition cannot be reinterpreted')
    for target,source in fields.items():
        if row[target]!=record[source]:raise ValueError('Exact section/population/XML source provenance required')


def assemble(base,statistical,regional,old_bounds,native_bounds,pairs,area_means,noncore):
    result=prior.assemble(base,statistical,regional,old_bounds,native_bounds,pairs,area_means);known={r['entity_id'] for r in result['records']};seen={r['id'] for r in result['evidence']}
    for a,report in noncore:
        if set(a['source_contexts'])!={CONTEXT} or CONTEXT in result['source_contexts']:raise ValueError('Unique selected non-core context required')
        context=a['source_contexts'][CONTEXT];result['source_contexts'][CONTEXT]=copy.deepcopy(context)
        for row in a['evidence']:
            i=int(row['source_pointer'].split('/')[-1])
            if row['id'] in seen or not 0<=i<len(report['records']) or row['source_pointer']!='/records/'+str(i) or row['source_file']!=a['derived_source_report']['file'] or row['source_sha256']!=a['derived_source_report']['sha256']:raise ValueError('Unique exact source-report pointer/hash required')
            validate_row(row,report['records'][i],context,known);seen.add(row['id']);result['evidence'].append(copy.deepcopy(row))
    for record in result['records']:record['depth_reference_ids']=[r['id'] for r in result['evidence'] if r['entity_id']==record['entity_id']]
    result['counts']=base_loader.counts_for(result['records'],result['evidence']);result['metric_counts']=dict(sorted(Counter(r['metric'] for r in result['evidence']).items()))
    return result


def read_parts(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v7':raise ValueError('Known reference inventory v7 required')
    old=[];noncore=[];seen=set()
    for part in manifest['addenda']:
        if part['id'] in seen:raise ValueError('Duplicate addendum identity')
        seen.add(part['id']);a=json.loads(checked_piece(part['json'],reader))
        if a['schema']!='osw.current-depth-selected-noncore-extent-addendum.v1':
            if noncore:raise ValueError('Earlier source classes must precede non-core extents')
            old.append(part);continue
        if a['id']!=part['id'] or a['base_snapshot_sha256']!=manifest['base']['json']['sha256'] or a['runtime_changed'] or a['full_goal_complete']:raise ValueError('Non-core source/base/promotion mismatch')
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));rows=list(incoming);fields=list(incoming.fieldnames)
        if len(rows)!=len(a['evidence']) or set(fields)!={k for r in a['evidence'] for k in r}:raise ValueError('All non-core CSV cells/rows required')
        for raw,row in zip(a['evidence'],rows):
            if row!={k:base_loader.cell(raw.get(k)) for k in fields}:raise ValueError('Non-core CSV differs from JSON')
        report=json.loads(checked_piece(a['derived_source_report'],reader));pointers=[r['source_pointer'] for r in a['evidence']]
        if report['schema']!='osw.nwasc-selected-noncore-depth-source-report.v1' or any(report[k] for k in ['curated_transects_obtained','physical_current_bottom_established','runtime_changed','full_goal_complete']) or report['new_ocean_field_requests']!=0 or len(set(pointers))!=len(pointers) or set(pointers)!={'/records/'+str(i) for i in range(len(report['records']))}:raise ValueError('All and only audited explicit non-core extents required')
        noncore.append((a,report))
    return (*prior.read_parts({'schema':'osw.current-depth-reference-inventory.v6','base':manifest['base'],'addenda':old},reader),noncore)


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
