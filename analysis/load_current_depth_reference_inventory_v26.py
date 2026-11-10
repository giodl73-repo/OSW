"""Benguela published pressure boundary, preserving hybrid reconstruction and native units."""
import copy,csv,io,json
from collections import Counter
import load_current_depth_reference_inventory_v25 as prior
import load_current_depth_reference_inventory_v1 as base
import load_current_depth_reference_inventory_v8 as defaults
SCHEMA='osw.current-depth-benguela-kersale2019-mean-pressure-addendum.v1'
FACTS='research/benguela-kersale2019-mean-pressure-source-facts-v1.json'
TIER='PRIMARY_PUBLISHER_RENDERED_TEXT_REVIEW_NO_RAW_ASSET_CUSTODY'
CONTEXT='benguela-kersale2019-34p5s-mean-pressure-boundary'
checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes


def validate_facts(f):
    if f['schema']!='osw.benguela-kersale2019-mean-pressure-source-facts.v1' or f['doi']!='10.1029/2018JC014554' or f['source_url']!='https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2018JC014554' or f['source_review_tier']!=TIER:raise ValueError('Exact primary source and custody tier required')
    expected={'id':'benguela-kersale2019-34p5s-mean-lower-pressure-extent','entity_id':'current:benguela','metric':'reported_mean_geostrophic_flow_lower_pressure_extent','approximate_value_dbar':1270,'unit':'dbar','source_latitude_degrees_north':-34.5,'source_longitude_band_degrees_east':[11,17.5],'source_flow_direction':'northward','source_statistic':'reported_observation_period_mean_reconstructed_geostrophic_section','source_locator':'Section3.2 firstparagraph and Figure4a; Section3.3 reuses1270dbar as transport split.','branch_scope':'steady_Benguela_mean_flow_P5_to_P1_not_entire_system'}
    if f['records']!=[expected] or not f['publisher_rendered_full_text_reviewed']:raise ValueError('One scoped published pressure boundary; no duplicate transport split or DEBC owner')
    methods={'velocity_field':'absolute_meridional_geostrophic_CPIES_GEM_reconstruction','temporal_reference':'source_observation_period_mean','time_mean_reference_velocity':'OFES36year_model_at1500dbar','time_varying_reference_velocity':'bottom_pressure_gradients','direct_full_column_velocity_observation':False,'wind_driven_Ekman_velocity_included':False,'horizontal_support':'averages_between_CPIES_pairs','published_mean_boundary_is_mean_instantaneous_boundary':False,'native_profile_QC_independently_verified':False}
    if f['methods']!=methods or f['reported_observational_months']!=['2013-09','2015-07']:raise ValueError('Hybrid source reconstruction and observation months cannot be promoted')
    for k in ['exact_html_bytes_retained','source_figures_visually_reviewed','raw_velocity_profiles_reanalysed','exact_common_averaging_endpoints_resolved','calendar_annual_or_climatological_mean','physical_current_bottom_established','runtime_changed','full_goal_complete']:
        if f[k] is not False:raise ValueError('No unsupported custody/physical/seasonal claims')
    if f['source_html_sha256'] is not None or f['source_pdf_sha256'] is not None or f['new_ocean_field_requests']!=0:raise ValueError('No raw custody or new field acquisition')


def reference(f,piece):
    validate_facts(f);record=f['records'][0]
    row={k:None for k in defaults.NULL_FIELDS};row.update({k:False for k in defaults.FALSE_FIELDS})
    row.update(id=record['id'],entity_id=record['entity_id'],metric=record['metric'],unit='dbar',approximate_value_dbar=1270,
      vertical_datum='source_reported_sea_pressure_dbar_not_metric_depth',phase_label='reported_Sep2013_Jul2015_mean',
      geographic_scope='SAMBA-East34.5S,11-17.5E,P5-P1 steadyBenguela meanflow; not full current route.',
      temporal_scope='Source-labelled September2013-July2015 mean,approximately23months; exact common endpoints unresolved.',
      source_definition='Approximate lower pressure extent of mean northward reconstructed geostrophic flow, also reused as transport integration split; count once.',
      evidence_kind='primary_published_observation_and_model_referenced_mean_geostrophic_pressure_boundary',source_url=f['source_url'],source_citation=f['source_citation'],source_locator=record['source_locator'],
      qualification='Pressure is not metric depth. CPIES-GEM field uses OFES mean reference velocity and bottom-pressure variability; excludes Ekman flow. Mean contour is not mean instantaneous boundary or physical thickness.',
      source_context_id=CONTEXT,source_file=piece['file'],source_sha256=piece['sha256'],source_pointer='/records/0',source_reported_record=copy.deepcopy(record),
      source_review_tier=TIER,source_methods=copy.deepcopy(f['methods']),source_statistic=record['source_statistic'],source_branch_scope=record['branch_scope'],
      source_observational_months=copy.deepcopy(f['reported_observational_months']),source_sampled_lon_lat=None,
      source_section_latitude_degrees_north=-34.5,source_section_longitude_band_degrees_east=[11,17.5],
      pressure_to_depth_conversion_applied=False,approximate_value_pressure_unit='dbar',source_mean_field_boundary_is_mean_instantaneous_boundary=False,
      source_exact_averaging_endpoints_resolved=False,source_html_sha256=None,source_pdf_sha256=None,
      publisher_rendered_full_text_reviewed=True,source_figures_visually_reviewed=False,raw_velocity_profiles_reanalysed=False,
      direct_current_depth_measurement=False,physical_depth_ranking_eligible=False,source_upper_to_lower_pair_is_physical_thickness=False)
    return row


def assemble(*parts):
    result=prior.assemble(*parts[:-1]);seen={r['id'] for r in result['evidence']}
    if len(parts[-1])!=1:raise ValueError('Exactly one pressure-source addendum')
    a,f=parts[-1][0];validate_facts(f);expected=reference(f,a['reviewed_source_facts'])
    if a['evidence']!=[expected] or a['source_contexts']!={CONTEXT:f} or CONTEXT in result['source_contexts'] or expected['id'] in seen:raise ValueError('No changed pressure units/methods/physical gates or duplicate source')
    result['evidence'].append(copy.deepcopy(expected));result['source_contexts'][CONTEXT]=copy.deepcopy(f)
    for r in result['records']:r['depth_reference_ids']=[e['id'] for e in result['evidence'] if e['entity_id']==r['entity_id']]
    result['counts']=base.counts_for(result['records'],result['evidence']);result['metric_counts']=dict(sorted(Counter(r['metric'] for r in result['evidence']).items()));result['coordinate_unit_counts']=dict(sorted(Counter(r['unit'] for r in result['evidence']).items()));return result


def read_parts(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v26':raise ValueError('Inventoryv26 required')
    old=[];new=[];seen=set()
    for part in manifest['addenda']:
        if part['id'] in seen:raise ValueError('Duplicate addendum')
        seen.add(part['id']);a=json.loads(checked_piece(part['json'],reader))
        if a['schema']!=SCHEMA:
            if new:raise ValueError('Old source classes must precede new source')
            old.append(part);continue
        if a['id']!=part['id'] or a['base_snapshot_sha256']!=manifest['base']['json']['sha256'] or a['runtime_changed'] or a['full_goal_complete'] or a['reviewed_source_facts']['file']!=FACTS:raise ValueError('Exact base/source and no promotion')
        facts=json.loads(checked_piece(a['reviewed_source_facts'],reader));incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));rows=list(incoming);fields=list(incoming.fieldnames)
        if len(rows)!=len(a['evidence']) or set(fields)!={k for r in a['evidence'] for k in r} or any(row!={k:base.cell(raw.get(k)) for k in fields} for raw,row in zip(a['evidence'],rows)):raise ValueError('Typed JSON/CSV cell disagreement')
        new.append((a,facts))
    if len(new)!=1:raise ValueError('Exactly one new source addendum required')
    return (*prior.read_parts({'schema':'osw.current-depth-reference-inventory.v25','base':manifest['base'],'addenda':old},reader),new)


def load_inventory(manifest,reader):
    result=assemble(*read_parts(manifest,reader))
    if result['counts']!=manifest['counts'] or result['metric_counts']!=manifest['metric_counts'] or result['coordinate_unit_counts']!=manifest['coordinate_unit_counts']:raise ValueError('Every reference count must reproduce')
    allowed={'schema','status','generator_file','generator_sha256','interpretation','runtime_changed','query_ui_integration_performed','full_goal_complete'}
    if not set(manifest['view_metadata'])<=allowed or any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('No runtime/completion promotion')
    result.update(copy.deepcopy(manifest['view_metadata']));result['inventory_base_file']=manifest['base']['json']['file'];result['inventory_addendum_files']=[p['json']['file'] for p in manifest['addenda']];result['member_depth_index_scope']='base_only_not_updated_for_addenda';return result
