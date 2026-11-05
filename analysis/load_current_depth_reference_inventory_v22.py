"""Published Tsushima sampled-core depths with explicit observation operators."""
import copy,csv,io,json
from collections import Counter
import load_current_depth_reference_inventory_v1 as base
import load_current_depth_reference_inventory_v8 as defaults
import load_current_depth_reference_inventory_v21 as prior

SCHEMA='osw.current-depth-tsushima-takikawa2014-core-depth-addendum.v1'
FACTS='research/tsushima-takikawa2021-observed-core-depth-source-facts-v1.json'
CONTEXT='tsushima-takikawa2014-observed-sampled-core-depths'
OWNER='current:tsushima'
checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes


def validate_facts(f):
    if f['schema']!='osw.tsushima-takikawa2021-observed-core-depth-source-facts.v1' or f['entity_id']!=OWNER or f['doi']!='10.1029/2020JC017141':raise ValueError('Original named current and primary paper required')
    if f['source_url']!='https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2020JC017141' or f['primary_sections_reviewed']!=['2 Observations and Data Processing','3 Results','Data Availability Statement']:raise ValueError('Exact reviewed primary sections required')
    for key in ['exact_html_bytes_retained','raw_adcp_records_obtained','figures_digitized','station_coordinates_independently_resolved','physical_current_bottom_established','runtime_changed','full_goal_complete']:
        if f[key] is not False:raise ValueError('No invented source custody, raw-profile work or physical promotion')
    if f['source_html_sha256'] is not None or f['new_ocean_field_requests']!=0 or f['new_raw_measurements']!=0:raise ValueError('Published factual transcription only')
    m=f['reported_methods']
    if m['instrument']!='bottom_mounted_Teledyne_WH_Sentinel_300kHz_ADCP' or m['original_ensemble_minutes']!=10 or m['reported_percent_good_requirement']!='greater_than75percent' or m['reported_hourly_averaging'] is not True:raise ValueError('Original ADCP ensemble and quality context required')
    if m['reported_removed_tidal_constituents']!=['Q1','O1','K1','mu2','N2','M2','S2'] or m['vertical_bin_interval_m_by_station']!={'C1':2,'C2':4,'C3':8,'C4':8,'C5':8} or m['reported_near_surface_unsampled_depth_m']!={'C1-C4':16,'C5':40}:raise ValueError('Original vertical sampling and tide removal required')
    if m['exact_station_deployment_dates_resolved'] is not False or m['velocity_error_index_is_depth_error'] is not False:raise ValueError('No dates or depth-error invention')
    expected=[('june17-c2-sampled-core','C2','reported_detided_profile_core_at_deployment','2014-06-17',41,26.5,'northeastward_to_eastward','first_branch'),
              ('june17-c4-sampled-core','C4','reported_detided_profile_core_at_deployment','2014-06-17',39,18.2,'northeastward_to_eastward','second_branch'),
              ('july22-c3-sampled-core','C3','reported_detided_profile_core_at_recovery','2014-07-22',37,28.1,None,'single_broad_core_across_C2_C4_branch_identity_unresolved'),
              ('c2-deployment-mean-sampled-core','C2','reported_station_deployment_mean_profile_maximum',None,61,31.1,'north_northeastward','mean_northeastward_core_in_C2_C3_region'),
              ('c3-deployment-mean-sampled-core','C3','reported_station_deployment_mean_profile_maximum',None,27,27.1,'east_northeastward','mean_northeastward_core_in_C2_C3_region')]
    actual=[(r['id'].removeprefix('tsushima-takikawa2014-'),r['station'],r['statistic'],r['observation_date'],r['approximate_value_m'],r['reported_current_speed_cm_s'],r['reported_direction'],r['branch_context']) for r in f['records']]
    if actual!=expected or any(not r['id'].startswith('tsushima-takikawa2014-') or not r['source_locator'].startswith('Section3') for r in f['records']):raise ValueError('Five exact station/date/statistic/core pairs required')


def source_context(f,owner):
    if owner!=OWNER:raise ValueError('One direct named owner required')
    return {k:copy.deepcopy(f[k]) for k in ['entity_id','doi','source_url','source_access','primary_sections_reviewed','exact_html_bytes_retained','source_html_sha256','reported_methods','qualifications','raw_adcp_records_obtained','figures_digitized','station_coordinates_independently_resolved']}


def context_id(owner):
    if owner!=OWNER:raise ValueError('One direct owner required')
    return CONTEXT


def reference(f,r,index,piece):
    row={k:None for k in defaults.NULL_FIELDS};row.update({k:False for k in defaults.FALSE_FIELDS})
    date=r['observation_date'];mean=date is None
    row.update(id=r['id'],entity_id=OWNER,metric='core_depth',unit='m',approximate_value_m=r['approximate_value_m'],vertical_datum='source_reported_depth_below_sea_surface_positive_down',phase_label=(date if date else 'station_deployment_mean_midJune_lateJuly2014'),geographic_scope='Southwestern Japan Sea shelf, Tsushima Warm Current, station'+r['station']+'; '+r['branch_context']+'. Exact coordinates unresolved.',temporal_scope=('Station-specific37-39day deployment context in midJune-lateJuly2014; exact averaging endpoints unresolved.' if mean else 'Dated detided profile discussed in text; exact UTC hour unresolved. Not a daily mean or seasonal climatology.'),source_definition='Depth of the current-speed maximum reported in a sampled ADCP profile; unsampled surface can contain a different full-column maximum.',evidence_kind='published_observed_ADCP_sampled_profile_core_depth',source_url=f['source_url'],source_citation=f['source_citation'],source_locator=r['source_locator'],qualification='Core depth only; no lower boundary, surface-connected penetration, thickness, depth uncertainty, annual range or compatible volume geometry. Profiles from one campaign are correlated.',source_context_id=CONTEXT,source_file=piece['file'],source_sha256=piece['sha256'],source_pointer='/records/'+str(index),source_reported_record=copy.deepcopy(r),source_station=r['station'],source_observation_date=date,source_snapshot_time_utc=None,source_statistic=r['statistic'],source_speed_cm_s=r['reported_current_speed_cm_s'],source_direction=r['reported_direction'],source_branch_context=r['branch_context'],source_bin_interval_m=f['reported_methods']['vertical_bin_interval_m_by_station'][r['station']],source_near_surface_unsampled_depth_m=16,source_sampled_lon_lat=None,source_html_sha256=None,source_mean_is_mean_of_instantaneous_core_depths=False,source_exact_mean_period_resolved=False,full_water_column_core_established=False,direct_velocity_core_observation=True,direct_current_depth_measurement=False,physical_depth_ranking_eligible=False,physical_current_bottom_established=False,core_to_seabed_vertical_connectivity_established=False,source_figure_digitized=False,independent_observation_count_claimed=False,reference_route_projection_eligible=False,volume_eligible=False,physical_state_join_eligible=False,seasonal_playback_eligible=False,annual_extrema_eligible=False)
    return row


def assemble(*parts):
    result=prior.assemble(*parts[:-1]);seen={r['id'] for r in result['evidence']}
    for a,f in parts[-1]:
        validate_facts(f);expected=[reference(f,r,i,a['reviewed_source_facts']) for i,r in enumerate(f['records'])];contexts={CONTEXT:source_context(f,OWNER)}
        if a['evidence']!=expected or a['source_contexts']!=contexts or CONTEXT in result['source_contexts'] or any(r['id'] in seen for r in expected):raise ValueError('Exact station rows and unique source context required')
        seen.update(r['id'] for r in expected);result['evidence'].extend(copy.deepcopy(expected));result['source_contexts'].update(copy.deepcopy(contexts))
    for r in result['records']:r['depth_reference_ids']=[e['id'] for e in result['evidence'] if e['entity_id']==r['entity_id']]
    result['counts']=base.counts_for(result['records'],result['evidence']);result['metric_counts']=dict(sorted(Counter(r['metric'] for r in result['evidence']).items()));result['coordinate_unit_counts']=dict(sorted(Counter(r['unit'] for r in result['evidence']).items()));return result

def read_parts(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v22':raise ValueError('Reference inventoryv22 required')
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
    return (*prior.read_parts({'schema':'osw.current-depth-reference-inventory.v21','base':manifest['base'],'addenda':old},reader),new)


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
