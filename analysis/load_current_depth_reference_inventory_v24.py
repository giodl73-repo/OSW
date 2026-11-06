"""Published Indian EUC event cores with explicit smoothed-analysis qualifications."""
import copy,csv,io,json
from collections import Counter
import load_current_depth_reference_inventory_v1 as base
import load_current_depth_reference_inventory_v8 as defaults
import load_current_depth_reference_inventory_v23 as prior
SCHEMA='osw.current-depth-indian-euc-iskandar2009-core-depth-addendum.v1'
FACTS='research/indian-euc-iskandar2009-published-core-depth-source-facts-v1.json'
CONTEXT='indian-euc-iskandar2009-published-event-core-depths'
OWNER='current:indian-equatorial-undercurrent'
checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes


def validate_facts(f):
    if f['schema']!='osw.indian-euc-iskandar2009-published-core-depth-source-facts.v1' or f['entity_id']!=OWNER or f['doi']!='10.1029/2008JC005188':raise ValueError('Exact primary source and owner required')
    if f['source_url']!='https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2008JC005188' or f['reported_nominal_site_lon_lat']!=[90,0]:raise ValueError('Original source and nominal site required')
    for k in ['exact_html_bytes_retained','raw_adcp_records_obtained','figures_digitized','actual_deployment_coordinates_independently_resolved','physical_current_bottom_established','runtime_changed','full_goal_complete']:
        if f[k] is not False:raise ValueError('No physical/raw-source/position promotion')
    if f['source_html_sha256'] is not None or f['new_ocean_field_requests']!=0 or f['new_raw_measurements']!=0:raise ValueError('Published factual transcription only')
    if f['primary_sections_reviewed']!=['Section2 paragraph7 and Table1','Section4 paragraph17 and Table2','Figure6 caption']:raise ValueError('Exact reviewed section/table/filter context required')
    m=f['reported_methods']
    fixed={'instrument':'upward_looking_subsurface_ADCP','record_interval':'daily','reported_vertical_interval_m':10,
           'analysis_depth_interval_m':[40,300],'source_record_dates':['2000-11-14','2006-12-02'],'figure6_running_mean_days':31,
           'table_specific_filter_separately_explicit':False,'reported_quality_flags':None,
           'within_window_numeric_coverage_independently_verified':False,'original_ensemble_interval_resolved':False,
           'original_vertical_interval_is_depth_uncertainty':False}
    if any(m[k]!=v for k,v in fixed.items()):raise ValueError('Original sampling and unresolved temporal/quality context required')
    expected=[('2001-04-26', 63, 110, 'boreal_winter'), ('2002-04-15', 91, 110, 'boreal_winter'), ('2003-04-02', 91, 100, 'boreal_winter'), ('2004-02-27', 85, 120, 'boreal_winter'), ('2005-04-15', 69, 140, 'boreal_winter'), ('2006-03-18', 74, 110, 'boreal_winter'), ('2001-09-18', 34, 130, 'boreal_summer'), ('2002-10-09', 63, 120, 'boreal_summer'), ('2004-11-02', 96, 100, 'boreal_summer'), ('2005-08-11', 64, 160, 'boreal_summer'), ('2006-11-09', 96, 70, 'boreal_summer')]
    actual=[(r['event_date'],r['reported_eastward_speed_cm_s'],r['approximate_value_m'],r['source_season_label']) for r in f['records']]
    if actual!=expected:raise ValueError('All and only eleven dated published event core pairs required')
    for r in f['records']:
        if r['id']!='indian-euc-iskandar2009-'+r['event_date']+'-published-core' or r['statistic']!='published_event_eastward_velocity_maximum_core_depth' or not r['source_locator'].startswith('Table2 ') or r['source_IOD_footnote']!=(r['event_date']=='2006-11-09'):raise ValueError('Exact dates/author seasons/statistics/footnote required')
    if f['non_numeric_source_outcomes']!=[{'source_season_label':'boreal_summer','year':2003,'source_outcome':'author_reports_no_EUC_in_that_season','depth_m':None,'numerical_depth_reference_admitted':False,'independently_reproduced':False,'source_locator':'Table2 boreal summer2003 row'}]:raise ValueError('Qualitative absence cannot become a numerical zero or independently reproduced result')


def context_id(owner):
    if owner!=OWNER:raise ValueError('One direct owner required')
    return CONTEXT


def source_context(f,owner):
    context_id(owner)
    return {k:copy.deepcopy(v) for k,v in f.items() if k!='records'}


def reference(f,r,index,piece):
    row={k:None for k in defaults.NULL_FIELDS};row.update({k:False for k in defaults.FALSE_FIELDS})
    date=r['event_date']
    row.update(id=r['id'],entity_id=OWNER,metric='core_depth',unit='m',approximate_value_m=r['approximate_value_m'],
       vertical_datum='source_reported_depth_below_sea_surface_positive_down',phase_label=date+' '+r['source_season_label'],
       geographic_scope='Eastern equatorial Indian Ocean; reported nominal ADCP site0N90E. Actual deployment coordinates and current axis unresolved.',
       temporal_scope='Published event maximum dated'+date+' in31day-smoothed analysis context; exact Table2 filter/window endpoints and UTC hour not separately stated. Not a daily snapshot, climatology or annual range.',
       source_definition='Published depth at the event maximum of the eastward velocity component in the sampled thermocline.',
       evidence_kind='published_observed_ADCP_event_maximum_core_depth',source_url=f['source_url'],source_citation=f['source_citation'],source_locator=r['source_locator'],
       qualification='Core depth is not current bottom or thickness. Figure6 smoothing context is reported; table-specific averaging details unresolved. One correlated mooring record; no independent profile reconstruction, temporal extrema, uncertainty or volume claim.',
       source_context_id=CONTEXT,source_file=piece['file'],source_sha256=piece['sha256'],source_pointer='/records/'+str(index),
       source_reported_record=copy.deepcopy(r),source_event_date=date,source_snapshot_time_utc=None,source_statistic=r['statistic'],
       source_eastward_speed_cm_s=r['reported_eastward_speed_cm_s'],source_component_bearing_degrees_true=90,
       source_author_season_label=r['source_season_label'],source_nominal_lon_lat=[90,0],source_sampled_lon_lat=None,
       source_position_role='paper_reported_nominal_mooring_not_actual_deployment_or_current_axis',source_vertical_interval_m=10,
       source_figure6_running_mean_days=31,source_table_specific_filter_separately_explicit=False,source_exact_mean_period_resolved=False,
       source_mean_is_mean_of_instantaneous_core_depths=False,source_within_window_numeric_coverage_verified=False,
       source_QC_flags=None,source_html_sha256=None,source_figure_digitized=False,
       direct_velocity_core_observation=True,direct_current_depth_measurement=False,physical_depth_ranking_eligible=False,
       full_water_column_core_established=False,physical_current_bottom_established=False,
       independent_observation_count_claimed=False,reference_route_projection_eligible=False,volume_eligible=False,
       physical_state_join_eligible=False,seasonal_playback_eligible=False,annual_extrema_eligible=False,
       operational_NOAA_daily_context_gate_applied=False)
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
    if manifest['schema']!='osw.current-depth-reference-inventory.v24':raise ValueError('Reference inventoryv24 required')
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
    return (*prior.read_parts({'schema':'osw.current-depth-reference-inventory.v23','base':manifest['base'],'addenda':old},reader),new)


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
