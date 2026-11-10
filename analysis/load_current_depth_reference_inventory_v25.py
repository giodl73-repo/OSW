"""Provisional primary published mean-section bounds with source processing retained."""
import copy,csv,io,json
from collections import Counter
import load_current_depth_reference_inventory_v1 as base
import load_current_depth_reference_inventory_v8 as defaults
import load_current_depth_reference_inventory_v24 as prior
SCHEMA='osw.current-depth-sun2023-143e-mean-boundary-addendum.v1'
FACTS='research/sun2023-143e-published-mean-boundary-source-facts-v1.json'
OWNERS=('current:pacific-south-equatorial','current:pacific-equatorial-undercurrent','current:pacific-north-equatorial-countercurrent','current:pacific-north-equatorial-undercurrent')
TIER='PROVISIONAL_PRIMARY_INDEXED_TEXT_TRANSCRIPTION_PENDING_ORIGINAL_SOURCE_CROSSCHECK'
checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes


def validate_facts(f):
    if f['schema']!='osw.sun2023-143e-published-mean-boundary-source-facts.v1' or f['doi']!='10.1175/JPO-D-22-0210.1' or f['source_url']!='https://journals.ametsoc.org/view/journals/phoc/53/10/JPO-D-22-0210.1.xml' or f['source_review_tier']!=TIER:raise ValueError('Exact primary indexed source and provisional tier required')
    for k in ['full_article_obtained','exact_html_bytes_retained','original_pdf_obtained','source_figures_visually_reviewed','figures_digitized','raw_velocity_profiles_reanalysed','exact_common_averaging_endpoints_resolved','calendar_annual_or_climatological_mean','physical_current_bottom_established','runtime_changed','full_goal_complete']:
        if f[k] is not False:raise ValueError('No invented custody/processing/time/physical promotion')
    if f['source_html_sha256'] is not None or f['source_pdf_sha256'] is not None or f['new_ocean_field_requests']!=0 or f['new_raw_measurements']!=0:raise ValueError('Published transcription only')
    if f['source_longitude_degrees_east']!=143 or f['reported_observational_months']!=['2016-01','2017-02']:raise ValueError('Exact regional observation window required')
    expected_methods={'mooring_count': 17, 'mooring_latitude_domain_degrees_north': [0, 22], 'ADCP_frequency_kHz': 75, 'ADCP_bins': 37, 'ADCP_native_bin_interval_m': 16, 'ADCP_record_interval_minutes': 30, 'ADCP_first_minute_average_per_record': True, 'deep_RCM_nominal_vertical_spacing_m': 1000, 'hourly_average_before_filter': True, 'interpolated_vertical_spacing_m': 5, 'interpolated_meridional_spacing_degrees': 0.25, 'native_meridional_spacing_by_band': [{'latitude_interval': [0, 16], 'spacing_degrees': 2}, {'latitude_interval': [16, 20], 'spacing_degrees': 1}, {'latitude_interval': [20, 22], 'spacing_degrees': 0.5}], 'lowpass_kind': 'fourth_order_Butterworth', 'latitude_dependent_lowpass_cutoff_hours': [{'latitude_interval': [0, 4], 'hours': 360}, {'latitude_interval': [6, 8], 'hours': 144}, {'latitude_interval': [10, 22], 'hours': 96}], 'daily_average_after_lowpass': True, 'unsampled_upper_layer_m': [0, 50], 'upper_layer_filled_using': 'linear_interpolation_altimeter_geostrophic_and_uppermost_ADCP', 'meridional_linear_interpolation': True, 'native_point_coverage_or_source_QC_independently_verified': False, 'processed_mooring_data_access': 'contact_corresponding_author_no_direct_dataset_link_reviewed'}
    if f['methods']!=expected_methods:raise ValueError('Native/interpolated resolution, altimetry, latitude-dependent filters and source data access must stay exact')
    expected=[('sec-mean-lower', 'current:pacific-south-equatorial', 'lower_flow_boundary_depth', 90, [0, 4], 'westward', 'equatorial_SEC'), ('euc-mean-upper', 'current:pacific-equatorial-undercurrent', 'upper_flow_boundary_depth', 100, [0, 4], 'eastward', 'equatorial_EUC'), ('euc-mean-lower', 'current:pacific-equatorial-undercurrent', 'lower_flow_boundary_depth', 300, [0, 4], 'eastward', 'equatorial_EUC'), ('necc-mean-upper-layer-extent', 'current:pacific-north-equatorial-countercurrent', 'reported_vertical_extent', 150, [3, 8], 'eastward', 'upper_NECC'), ('neuc-middle-jet-mean-upper', 'current:pacific-north-equatorial-undercurrent', 'upper_flow_boundary_depth', 350, [11, 15], 'eastward', 'middle_NEUC_jet_only')]
    actual=[(r['id'].removeprefix('sun2023-143e-'),r['entity_id'],r['metric'],r['approximate_value_m'],r['reported_latitude_band_degrees_north'],r['source_zonal_flow_direction'],r['source_branch_scope']) for r in f['records']]
    if actual!=expected:raise ValueError('All and only five exact mean boundary/extent pairs and owners required')
    for r in f['records']:
        if r['id']!='sun2023-143e-'+r['id'].removeprefix('sun2023-143e-') or r['source_statistic']!='reported_observational_period_mean_section' or not r['source_locator'].startswith('Section3 '):raise ValueError('Original statistic/locator required')
    if f['unadmitted_candidates']!=[{'id': 'neuc-deep-reach', 'source_claim_at_least_depth_m': 3000, 'numeric_reference_admitted': False, 'reason': 'Section3 deep claim conflicts with Section5 lack of statistically significant off-equatorial3000m means. Sparse deep meters/interpolation do not establish continuous named-current membership or a bottom. Retain for original-source/profile crosscheck.'}, {'id': 'stcc-nicc-nesc-eic-and-unnamed-abyssal-flows', 'numeric_reference_admitted': False, 'reason': 'Distinct source currents/branches without separately resolved owners in this catalog batch. STCC is not NSCC, and separate deep eastward flow is not a full-thickness STCC. No forced mapping.'}]:raise ValueError('Uncertain deep claim and distinct unmapped current identities remain unadmitted')


def context_id(owner):
    if owner not in OWNERS:raise ValueError('Only four actual named current owners admitted')
    return 'sun2023-143e-'+owner.split(':')[1]+'-published-mean-boundaries'


def source_context(f,owner):
    context_id(owner)
    return {**{k:copy.deepcopy(v) for k,v in f.items() if k!='records'},'entity_id':owner,
            'record_ids':[r['id'] for r in f['records'] if r['entity_id']==owner]}


def reference(f,r,index,piece):
    row={k:None for k in defaults.NULL_FIELDS};row.update({k:False for k in defaults.FALSE_FIELDS})
    row.update(id=r['id'],entity_id=r['entity_id'],metric=r['metric'],unit='m',approximate_value_m=r['approximate_value_m'],
      vertical_datum='source_reported_depth_below_sea_surface_positive_down',phase_label='source_observational_period_mean_Jan2016_Feb2017',
      geographic_scope='Published143E section within latitude band'+str(r['reported_latitude_band_degrees_north'])+'N; '+r['source_branch_scope']+'. Not a point deployment or full route.',
      temporal_scope='Mean of source observation period labelled January2016-February2017, approximately13months; exact common endpoints unresolved. Not a calendar-year mean or climatology.',
      source_definition='Author-reported '+r['metric']+' of the processed mean zonal velocity section; not an independently reanalysed physical boundary.',
      evidence_kind='provisional_primary_indexed_text_observation_based_mean_section_boundary',source_url=f['source_url'],source_citation=f['source_citation'],source_locator=r['source_locator'],
      qualification='Provisional indexed primary transcription pending original-source crosscheck. Native16m bins and sparse moorings differ from interpolated5m/0.25degree grid; upper50m uses altimetry. Mean contour/extent is not instantaneous current thickness, uncertainty, annual range or compatible volume geometry. EUC lateral interpolation and ENSO context retained.',
      source_context_id=context_id(r['entity_id']),source_file=piece['file'],source_sha256=piece['sha256'],source_pointer='/records/'+str(index),source_reported_record=copy.deepcopy(r),
      source_review_tier=TIER,source_methods=copy.deepcopy(f['methods']),source_branch_scope=r['source_branch_scope'],source_zonal_flow_direction=r['source_zonal_flow_direction'],
      source_section_longitude_degrees_east=143,source_section_latitude_band_degrees_north=copy.deepcopy(r['reported_latitude_band_degrees_north']),
      source_sampled_lon_lat=None,source_statistic=r['source_statistic'],source_observational_months=copy.deepcopy(f['reported_observational_months']),
      source_exact_averaging_endpoints_resolved=False,source_within_period_numeric_coverage_verified=False,source_interpolated_grid_is_native_resolution=False,
      source_mean_field_boundary_is_mean_instantaneous_boundary=False,source_QC_flags=None,source_html_sha256=None,source_pdf_sha256=None,
      full_article_obtained=False,source_figures_visually_reviewed=False,raw_velocity_profiles_reanalysed=False,
      direct_current_depth_measurement=False,physical_depth_ranking_eligible=False,physical_current_bottom_established=False,
      independent_observation_count_claimed=False,reference_route_projection_eligible=False,volume_eligible=False,
      physical_state_join_eligible=False,seasonal_playback_eligible=False,annual_extrema_eligible=False,
      source_upper_to_lower_pair_is_physical_thickness=False)
    return row


def assemble(*parts):
    result=prior.assemble(*parts[:-1]);seen={r['id'] for r in result['evidence']}
    for a,f in parts[-1]:
        validate_facts(f);expected=[reference(f,r,i,a['reviewed_source_facts']) for i,r in enumerate(f['records'])];contexts={context_id(owner):source_context(f,owner) for owner in OWNERS}
        if a['evidence']!=expected or a['source_contexts']!=contexts or any(k in result['source_contexts'] for k in contexts) or any(r['id'] in seen for r in expected):raise ValueError('Exact station rows and unique source context required')
        seen.update(r['id'] for r in expected);result['evidence'].extend(copy.deepcopy(expected));result['source_contexts'].update(copy.deepcopy(contexts))
    for r in result['records']:r['depth_reference_ids']=[e['id'] for e in result['evidence'] if e['entity_id']==r['entity_id']]
    result['counts']=base.counts_for(result['records'],result['evidence']);result['metric_counts']=dict(sorted(Counter(r['metric'] for r in result['evidence']).items()));result['coordinate_unit_counts']=dict(sorted(Counter(r['unit'] for r in result['evidence']).items()));return result

def read_parts(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v25':raise ValueError('Reference inventoryv25 required')
    old=[];new=[];seen=set()
    for part in manifest['addenda']:
        if part['id'] in seen:raise ValueError('Duplicate addendum identity')
        seen.add(part['id']);a=json.loads(checked_piece(part['json'],reader))
        if a['schema']!=SCHEMA:
            if new:raise ValueError('Original source classes must precede new source')
            old.append(part);continue
        if a['id']!=part['id'] or a['base_snapshot_sha256']!=manifest['base']['json']['sha256'] or a['runtime_changed'] or a['full_goal_complete'] or a['reviewed_source_facts']['file']!=FACTS:raise ValueError('Exact source,base and non-promotion required')
        facts=json.loads(checked_piece(a['reviewed_source_facts'],reader));incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));rows=list(incoming);fields=list(incoming.fieldnames)
        if len(rows)!=len(a['evidence']) or set(fields)!={k for r in a['evidence'] for k in r} or any(row!={k:base.cell(raw.get(k)) for k in fields} for raw,row in zip(a['evidence'],rows)):raise ValueError('Every exact typed JSON/CSV cell required')
        new.append((a,facts))
    if len(new)!=1:raise ValueError('Exactly one new source addendum required')
    return (*prior.read_parts({'schema':'osw.current-depth-reference-inventory.v24','base':manifest['base'],'addenda':old},reader),new)


def load_inventory(manifest,reader):
    result=assemble(*read_parts(manifest,reader))
    if result['counts']!=manifest['counts'] or result['metric_counts']!=manifest['metric_counts'] or result['coordinate_unit_counts']!=manifest['coordinate_unit_counts']:raise ValueError('Every reference count must reproduce')
    allowed={'schema','status','generator_file','generator_sha256','interpretation','runtime_changed','query_ui_integration_performed','full_goal_complete'}
    if not set(manifest['view_metadata'])<=allowed or any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('No runtime or completion promotion')
    result.update(copy.deepcopy(manifest['view_metadata']));result['inventory_base_file']=manifest['base']['json']['file'];result['inventory_addendum_files']=[p['json']['file'] for p in manifest['addenda']];result['member_depth_index_scope']='base_only_not_updated_for_addenda';return result


def combined_csv_bytes(manifest,reader):
    load_inventory(manifest,reader);first=csv.DictReader(io.StringIO(checked_piece(manifest['base']['csv'],reader).decode()));columns=list(first.fieldnames);rows=list(first)
    for part in manifest['addenda']:
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));columns.extend(k for k in incoming.fieldnames if k not in columns);rows.extend(list(incoming))
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows);return out.getvalue().encode()
