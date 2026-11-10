"""Preserve episodic nutrient-bearing water-mass scales as a distinct source class."""
import copy,csv,io,json
from collections import Counter
import load_current_depth_reference_inventory_v1 as base_loader
import load_current_depth_reference_inventory_v8 as prior

checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes
SCHEMA='osw.current-depth-episodic-water-mass-layer-addendum.v1'
CONTEXT='jutland-nielsen2000-atypical-gbw-pulse-upper-layer'
METRIC='reported_episodic_nutrient_bearing_water_mass_upper_layer_extent'


def source_context(facts):
    return {'entity_id':facts['entity_id'],'source_population':'nutrient_rich_German_Bight_Water_pulses','source_time_context':facts['reported_episode_upper_layer']['source_time_context'],'source_scope':facts['reported_episode_upper_layer']['source_scope'],'source_statistic':'author_reported_atypical_episode_upper_layer_scale','physical_current_bottom_established':False}


def reference(facts,piece):
    episode=facts['reported_episode_upper_layer'];row={k:None for k in prior.NULL_FIELDS};row.update({k:False for k in prior.FALSE_FIELDS})
    row.update(id='jutland-nielsen2000-atypical-gbw-pulse-upper-layer',entity_id=facts['entity_id'],metric=METRIC,range_m=copy.deepcopy(episode['reported_range_m']),range_interpretation=episode['range_is'],lower_bound_m=None,lower_bound_operator=None,unit='m',vertical_datum='local_sea_surface_positive_down',phase_label='Atypical nutrient-rich GBW pulses; especially1994and1995',geographic_scope=episode['source_scope'],temporal_scope=episode['source_time_context'],source_definition='Author-reported upper-layer scale of exceptional nutrient-rich German Bight Water transport. Not a detected Jutland velocity boundary or full-current layer thickness.',evidence_kind='original_report_prose_regional_episodic_water_mass_scale',source_url=facts['source_url'],source_citation=facts['citation'],source_locator='Adjacent prose to Table7.1,printedp67/PDFpage75.',qualification='Approximate source-reported layer scale during atypical conditions. No exact event dates,annual envelope,confidence interval,uniform current depth,paired width or volume. Seven-depth annual-mean composition table has a different population/statistic and is supporting context only.',source_context_id=CONTEXT,source_statistic='author_reported_atypical_episode_upper_layer_scale',source_population='nutrient_rich_German_Bight_Water_pulses',source_file=piece['file'],source_sha256=piece['sha256'],source_pointer='/reported_episode_upper_layer',source_episode=copy.deepcopy(episode),source_pdf_file=facts['source_pdf_file'],source_pdf_sha256=facts['source_pdf_sha256'],source_pdf_bytes=facts['source_pdf_bytes'],source_pdf_rehashed_in_cloud=False,source_annual_composition_profile_is_supporting_context_only=True)
    return row


def validate_facts(facts):
    episode=facts['reported_episode_upper_layer']
    if facts['schema']!='osw.jutland-nielsen2000-depth-profile-source-facts.v1' or facts['entity_id']!='current:jutland' or episode['metric']!='author_reported_nutrient_rich_German_Bight_Water_pulse_transport_upper_layer_extent' or episode['reported_range_m']!=[10,15] or episode['range_is']!='approximate_upper_layer_scale_not_confidence_interval_or_annual_extrema':raise ValueError('Original separately scoped episodic source scale required')
    if episode['physical_current_bottom_established'] is not False or episode['inventory_admitted'] is not False or any(facts[k] for k in ['physical_current_bottom_established','reference_inventory_updated','new_current_measurements_admitted','new_ocean_field_requests','runtime_changed','full_goal_complete']):raise ValueError('Original source-review stage must not claim admission or a bottom')
    profile=facts['source_profile']
    if profile['quantity']!='source_calculated_German_Bight_Water_fraction' or profile['source_station_id'] is not None or profile['exact_occupation_dates'] is not None or profile['independent_observation_count_claimed'] is not False:raise ValueError('Composition profile is not dated velocity observations')


def assemble(*parts):
    result=prior.assemble(*parts[:-1]);known={r['entity_id'] for r in result['records']};seen={r['id'] for r in result['evidence']}
    for a,facts in parts[-1]:
        validate_facts(facts);context=source_context(facts);expected=reference(facts,a['reviewed_source_facts'])
        if a['source_pdf_rehashed_in_cloud'] is not False or a['source_contexts']!={CONTEXT:context} or CONTEXT in result['source_contexts'] or a['evidence']!=[expected] or expected['entity_id'] not in known or expected['id'] in seen:raise ValueError('One exact directly owned episodic source reference required')
        result['source_contexts'][CONTEXT]=copy.deepcopy(context);result['evidence'].append(copy.deepcopy(expected));seen.add(expected['id'])
    for r in result['records']:r['depth_reference_ids']=[e['id'] for e in result['evidence'] if e['entity_id']==r['entity_id']]
    result['counts']=base_loader.counts_for(result['records'],result['evidence']);result['metric_counts']=dict(sorted(Counter(r['metric'] for r in result['evidence']).items()))
    return result


def read_parts(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v9':raise ValueError('Known reference inventory v9 required')
    old=[];episodes=[];seen=set()
    for part in manifest['addenda']:
        if part['id'] in seen:raise ValueError('Duplicate addendum identity')
        seen.add(part['id']);a=json.loads(checked_piece(part['json'],reader))
        if a['schema']!=SCHEMA:
            if episodes:raise ValueError('Prior source classes must precede episodic scales')
            old.append(part);continue
        if a['id']!=part['id'] or a['base_snapshot_sha256']!=manifest['base']['json']['sha256'] or a['runtime_changed'] or a['full_goal_complete']:raise ValueError('Exact source/base/admission identity required')
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));rows=list(incoming);fields=list(incoming.fieldnames)
        if len(rows)!=len(a['evidence']) or set(fields)!={k for r in a['evidence'] for k in r} or any(row!={k:base_loader.cell(raw.get(k)) for k in fields} for raw,row in zip(a['evidence'],rows)):raise ValueError('Every typed source CSV cell required')
        facts=json.loads(checked_piece(a['reviewed_source_facts'],reader));episodes.append((a,facts))
    return (*prior.read_parts({'schema':'osw.current-depth-reference-inventory.v8','base':manifest['base'],'addenda':old},reader),episodes)


def load_inventory(manifest,reader):
    result=assemble(*read_parts(manifest,reader))
    if result['counts']!=manifest['counts'] or result['metric_counts']!=manifest['metric_counts']:raise ValueError('Reference inventory counts do not reproduce')
    allowed={'schema','status','generator_file','generator_sha256','interpretation','runtime_changed','query_ui_integration_performed','full_goal_complete'}
    if not set(manifest['view_metadata'])<=allowed or any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('No runtime or completion promotion')
    result.update(copy.deepcopy(manifest['view_metadata']));result['inventory_base_file']=manifest['base']['json']['file'];result['inventory_addendum_files']=[p['json']['file'] for p in manifest['addenda']];result['member_depth_index_scope']='base_only_not_updated_for_addenda'
    return result


def combined_csv_bytes(manifest,reader):
    load_inventory(manifest,reader);first=csv.DictReader(io.StringIO(checked_piece(manifest['base']['csv'],reader).decode()));columns=list(first.fieldnames);rows=list(first)
    for part in manifest['addenda']:
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));columns.extend(k for k in incoming.fieldnames if k not in columns);rows.extend(list(incoming))
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows)
    return out.getvalue().encode()
