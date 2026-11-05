"""One scoped published Labrador mean extent, independent of deep DWBC."""
import copy,csv,io,json
from collections import Counter
import load_current_depth_reference_inventory_v26 as prior
import load_current_depth_reference_inventory_v1 as base
import load_current_depth_reference_inventory_v8 as defaults
SCHEMA='osw.current-depth-labrador-handmann2018-mean-extent-addendum.v1'
FACTS='research/labrador-handmann2018-mean-extent-source-facts-v1.json'
TIER='PRIMARY_PUBLISHER_RENDERED_TEXT_REVIEW_NO_RAW_ASSET_CUSTODY'
CONTEXT='labrador-handmann2018-53n-observed-mean-extent'
checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes
EXPECTED_FACTS={'schema': 'osw.labrador-handmann2018-mean-extent-source-facts.v1', 'doi': '10.1002/2017JC013702', 'source_url': 'https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2017JC013702', 'source_citation': 'Handmann,P.,Fischer,J.,Visbeck,M.,Karstensen,J.,Biastoch,A.,Boning,C.,and Patara,L.(2018),The Deep Western Boundary Current in the Labrador Sea From Observations and a High-Resolution Model,JGR Oceans123,2829-2850,doi10.1002/2017JC013702.', 'source_review_tier': 'PRIMARY_PUBLISHER_RENDERED_TEXT_REVIEW_NO_RAW_ASSET_CUSTODY', 'publisher_rendered_full_text_reviewed': True, 'source_html_sha256': None, 'source_pdf_sha256': None, 'source_figures_visually_reviewed': False, 'raw_velocity_profiles_reanalysed': False, 'new_ocean_field_requests': 0, 'source_access': 'Publisher-rendered article text reviewed2026-11-05; Sections2.1 and3.1,Figure2caption. No original HTML/PDF byte custody or figure digitization.', 'records': [{'id': 'labrador-handmann2018-53n-observed-mean-vertical-extent', 'entity_id': 'current:labrador', 'metric': 'reported_vertical_extent', 'approximate_value_m': 500, 'unit': 'm', 'source_section_latitude_degrees_north': 53, 'source_statistic': 'published_observed_mean_section_description', 'source_period_years': [1997, 2014], 'source_locator': 'Section3.1 opening paragraph; Figure2a caption; Section2.1 observation-period description.', 'branch_scope': 'shallow_Labrador_Current_at_53N_distinct_from_deep_DWBC'}], 'methods': {'observational_basis': 'LADCP_and_mooring_mean_velocity_section', 'source_mean_period_years': [1997, 2014], 'source_statistic_is_mean_individual_boundary_depth': False, 'fixed_velocity_threshold_specified_for_500m_extent': False, 'independent_boundary_recalculation_performed': False, 'VIKING20_model_value_admitted_as_second_observation': False, 'deep_DWBC_assigned_to_Labrador_Current': False}, 'exact_averaging_endpoints_resolved': False, 'physical_current_bottom_established': False, 'seasonal_extrema_established': False, 'runtime_changed': False, 'full_goal_complete': False}


def validate_facts(f):
    if f!=EXPECTED_FACTS:raise ValueError('Exact reviewed regional observed-mean definition and custody tier required')


def reference(f,piece):
    validate_facts(f);record=f['records'][0]
    row={k:None for k in defaults.NULL_FIELDS};row.update({k:False for k in defaults.FALSE_FIELDS})
    row.update(id=record['id'],entity_id=record['entity_id'],metric=record['metric'],unit='m',approximate_value_m=500,
      vertical_datum='source_reported_depth_below_surface_exact_datum_unresolved',
      phase_label='published_1997_2014_observed_mean_section',
      geographic_scope='Labrador shelfbreak boundary current at53N, shallow Labrador Current component; no whole-route coverage.',
      temporal_scope='Mean section from LADCP and mooring observations1997-2014; exact averaging endpoints unresolved.',
      source_definition='Author-described approximate vertical reach of the shallow Labrador Current in the observed mean velocity section. No explicit velocity cutoff for this500m description.',
      evidence_kind='primary_published_observed_mean_section_description',source_url=f['source_url'],source_citation=f['source_citation'],source_locator=record['source_locator'],
      qualification='Regional approximate mean-flow extent, separate from underlying LSW and deep DWBC. Not a fixed-isotach crossing, instantaneous physical bottom, mean of individual boundary depths, seasonal range or uncertainty.',
      source_context_id=CONTEXT,source_file=piece['file'],source_sha256=piece['sha256'],source_pointer='/records/0',source_reported_record=copy.deepcopy(record),
      source_review_tier=TIER,source_methods=copy.deepcopy(f['methods']),source_statistic=record['source_statistic'],source_branch_scope=record['branch_scope'],
      source_period_years=[1997,2014],source_sampled_lon_lat=None,source_section_latitude_degrees_north=53,
      source_mean_field_boundary_is_mean_instantaneous_boundary=False,source_exact_averaging_endpoints_resolved=False,
      source_html_sha256=None,source_pdf_sha256=None,publisher_rendered_full_text_reviewed=True,
      source_figures_visually_reviewed=False,raw_velocity_profiles_reanalysed=False,
      direct_current_depth_measurement=False,physical_depth_ranking_eligible=False,
      source_upper_to_lower_pair_is_physical_thickness=False,source_fixed_velocity_threshold_m_s=None)
    return row


def assemble(*parts):
    result=prior.assemble(*parts[:-1]);seen={r['id'] for r in result['evidence']}
    if len(parts[-1])!=1:raise ValueError('Exactly one Labrador-source addendum')
    a,f=parts[-1][0];validate_facts(f);expected=reference(f,a['reviewed_source_facts'])
    if a['evidence']!=[expected] or a['source_contexts']!={CONTEXT:f} or CONTEXT in result['source_contexts'] or expected['id'] in seen:raise ValueError('No changed Labrador metric/methods/physical gates or duplicate source')
    result['evidence'].append(copy.deepcopy(expected));result['source_contexts'][CONTEXT]=copy.deepcopy(f)
    for r in result['records']:r['depth_reference_ids']=[e['id'] for e in result['evidence'] if e['entity_id']==r['entity_id']]
    result['counts']=base.counts_for(result['records'],result['evidence']);result['metric_counts']=dict(sorted(Counter(r['metric'] for r in result['evidence']).items()));result['coordinate_unit_counts']=dict(sorted(Counter(r['unit'] for r in result['evidence']).items()));return result


def read_parts(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v27':raise ValueError('Inventoryv27 required')
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
    return (*prior.read_parts({'schema':'osw.current-depth-reference-inventory.v26','base':manifest['base'],'addenda':old},reader),new)


def load_inventory(manifest,reader):
    result=assemble(*read_parts(manifest,reader))
    if result['counts']!=manifest['counts'] or result['metric_counts']!=manifest['metric_counts'] or result['coordinate_unit_counts']!=manifest['coordinate_unit_counts']:raise ValueError('Every reference count must reproduce')
    allowed={'schema','status','generator_file','generator_sha256','interpretation','runtime_changed','query_ui_integration_performed','full_goal_complete'}
    if not set(manifest['view_metadata'])<=allowed or any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('No runtime/completion promotion')
    result.update(copy.deepcopy(manifest['view_metadata']));result['inventory_base_file']=manifest['base']['json']['file'];result['inventory_addendum_files']=[p['json']['file'] for p in manifest['addenda']];result['member_depth_index_scope']='base_only_not_updated_for_addenda';return result
