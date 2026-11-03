"""Reported year-filtered NEC/NEUC depths at one actual mooring; no bottom inference."""
import copy,csv,io,json
from collections import Counter
import load_current_depth_reference_inventory_v1 as base
import load_current_depth_reference_inventory_v8 as defaults
import load_current_depth_reference_inventory_v15 as prior

SCHEMA='osw.current-depth-nec-huang2022-filtered-depth-addendum.v1'
FACTS='research/nec-huang2022-filtered-depth-source-facts-v1.json'
checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes
EXPECTED=[('nec-upper-reach','current:pacific-north-equatorial','reported_vertical_extent',200,None,None,None),('nec-2017-12-core','current:pacific-north-equatorial','core_depth',70,'2017-12',None,-.25),('nec-2021-03-core','current:pacific-north-equatorial','core_depth',90,'2021-03',None,-.22),('neuc-2016-2017-core','current:pacific-north-equatorial-undercurrent','core_depth',430,None,['2016-03','2017-04'],.14),('neuc-2019-2020-core','current:pacific-north-equatorial-undercurrent','core_depth',400,None,['2019-06','2020-06'],.10)]


def validate_facts(f):
    if f['schema']!='osw.nec-huang2022-filtered-depth-source-facts.v1' or f['doi']!='10.3389/fmars.2022.979442' or f['source_station_lon_lat']!=[130,8.5] or f['source_station_acquisition_dates']!=['2015-09-26','2021-12-27']:raise ValueError('Exact actual8.5N130E mooring context required')
    if f['source_html_sha256']!='0b0739061ff2bb8beedcac1f2909b5953b3b397d44c9f9507f58dea1cd1b7519' or f['source_html_bytes']!=929434 or f['source_figure2_sha256']!='4c8ca9bddc598e64a2af2f32929af9cdd6de1b28628da19ec944a8e9d9bf95ee' or f['source_figure2_bytes']!=345888 or f['source_figure2_visually_reviewed'] is not True:raise ValueError('Exact primary HTML and visually reviewed original figure required')
    if f['temporal_filter']!={'kind':'one_year_moving_average_low_pass','discarded_endpoint_months':[6,5]} or f['source_native_ADCP_bin_size_m']!=8 or f['source_vertical_interpolation_spacing_m']!=10 or f['source_excluded_depths_shallower_than_m']!=40 or f['source_ADCP_support_upper_limit_m']!=900:raise ValueError('Original year filter,endpoint exclusions and sampling/processing support required')
    if any(f[k] for k in ['original_pdf_obtained','source_assets_rehashed_in_admission_cloud','raw_mooring_data_reanalysed','source_figure_digitized','physical_current_bottom_established','source_assets_redistributed']):raise ValueError('No invented PDF custody,raw analysis,digitization or physical promotion')
    if len(f['records'])!=5:raise ValueError('All five directly reported source cases required')
    for r,(identity,owner,metric,value,month,interval,velocity) in zip(f['records'],EXPECTED):
        if [r[k] for k in ['id','entity_id','metric','approximate_value_m','event_month','reported_interval_months','reported_zonal_velocity_m_s']]!=[identity,owner,metric,value,month,interval,velocity]:raise ValueError('Exact source owner,metric,depth and reported timing required')
        if r['direction']!=('eastward' if 'undercurrent' in owner else 'westward') or r['calendar_months'] is not None:raise ValueError('Opposing currents and event timing cannot become seasonal climatology')
        if any(r[k] is not None for k in ['range_m','annual_range_m','uncertainty_m','physical_layer_thickness_m','paired_width_reference_id']) or any(r[k] for k in ['instantaneous_observation_claimed','independent_observation_count_claimed','physical_current_bottom_established','volume_eligible']):raise ValueError('No extrema,uncertainty,thickness,instantaneous or volume promotion')


def context_id(owner):return 'huang2022-8p5n130e-'+owner.split(':')[1]


def source_context(f,owner):
    return {'entity_id':owner,'source_station_lon_lat':[130,8.5],'source_station_acquisition_dates':f['source_station_acquisition_dates'],'temporal_filter':f['temporal_filter'],'source_native_ADCP_bin_size_m':8,'source_vertical_interpolation_spacing_m':10,'source_excluded_depths_shallower_than_m':40,'source_ADCP_support_upper_limit_m':900,'sampling_support_is_current_boundary':False,'source_density_partition_sigma_theta_kg_m3':26.8,'density_partition_converted_to_meters':False,'source_review_status':'EXACT_CLOUD_PRIMARY_HTML_AND_ORIGINAL_FIGURE_REVIEWED','original_pdf_obtained':False,'source_assets_rehashed_in_admission_cloud':False,'raw_mooring_data_reanalysed':False,'physical_current_bottom_established':False,'source_station_is_actual_native_8p5n_not_WOA_shifted_other_latitudes':True}


def reference(f,r,index,piece):
    row={k:None for k in defaults.NULL_FIELDS};row.update({k:False for k in defaults.FALSE_FIELDS})
    period={'event_month':r['event_month']} if r['event_month'] else {'start_month':r['reported_interval_months'][0],'end_month':r['reported_interval_months'][1]} if r['reported_interval_months'] else None
    row.update(id='huang2022-8p5n130e-'+r['id'],entity_id=r['entity_id'],metric=r['metric'],approximate_value_m=r['approximate_value_m'],unit='m',vertical_datum='source_reported_depth_below_sea_surface',phase_label=r['id'],calendar_months=None,observed_period=period,geographic_scope='Actual mooring8.5N130E in northwestern Pacific;local NEC/NEUC context,not the whole current or other-latitude corrected series.',temporal_scope='Published one-year moving-average velocity description;first6andlast5months discarded. Event labels or intervals are author-reported filtered timing,not instantaneous observations,seasonal means or annual extrema.',source_definition=r['source_definition'],evidence_kind='published_one_year_filtered_mooring_flow_extent' if r['metric']=='reported_vertical_extent' else 'published_one_year_filtered_mooring_velocity_core_depth',source_url=f['source_url'],source_citation=f['source_citation'],source_locator='Results/Mean structure of NEC/NEUC,paragraphs describing8.5N;Figure2E andcaption. Data and method/Table1 for acquisition,filter and sampling support.',qualification='200m describes energetic upper westward flow;70/90/430/400m are source velocity-maximum depths. Sampling excludes shallower than40m and ends near900m;these are not current boundaries. Do not combine dated cores into an annual range,derive thickness or volume,or transfer deeper current-meter support to this flow.',source_context_id=context_id(r['entity_id']),source_file=piece['file'],source_sha256=piece['sha256'],source_pointer='/records/'+str(index),source_reported_record=copy.deepcopy(r),source_temporal_filter=copy.deepcopy(f['temporal_filter']),source_station_acquisition_dates=copy.deepcopy(f['source_station_acquisition_dates']),source_html_sha256=f['source_html_sha256'],source_figure2_sha256=f['source_figure2_sha256'],source_figure2_visually_reviewed=True,original_pdf_obtained=False,source_pdf_sha256=None,source_assets_rehashed_in_admission_cloud=False,raw_mooring_data_reanalysed=False)
    return row


def assemble(*parts):
    result=prior.assemble(*parts[:-1]);seen={r['id'] for r in result['evidence']};known={r['entity_id'] for r in result['records']}
    for a,f in parts[-1]:
        validate_facts(f);expected=[reference(f,r,i,a['reviewed_source_facts']) for i,r in enumerate(f['records'])];contexts={context_id(owner):source_context(f,owner) for owner in ['current:pacific-north-equatorial','current:pacific-north-equatorial-undercurrent']}
        if a['evidence']!=expected or a['source_contexts']!=contexts or set(contexts)&set(result['source_contexts']):raise ValueError('Exact source rows and unique owner contexts required')
        if any(r['id'] in seen or r['entity_id'] not in known for r in expected):raise ValueError('Unique known direct-owner references required')
        seen.update(r['id'] for r in expected);result['evidence'].extend(copy.deepcopy(expected));result['source_contexts'].update(copy.deepcopy(contexts))
    for r in result['records']:r['depth_reference_ids']=[e['id'] for e in result['evidence'] if e['entity_id']==r['entity_id']]
    result['counts']=base.counts_for(result['records'],result['evidence']);result['metric_counts']=dict(sorted(Counter(r['metric'] for r in result['evidence']).items()));return result


def read_parts(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v16':raise ValueError('Reference inventoryv16 required')
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
    return (*prior.read_parts({'schema':'osw.current-depth-reference-inventory.v15','base':manifest['base'],'addenda':old},reader),new)


def load_inventory(manifest,reader):
    result=assemble(*read_parts(manifest,reader))
    if result['counts']!=manifest['counts'] or result['metric_counts']!=manifest['metric_counts']:raise ValueError('Every reference count must reproduce')
    allowed={'schema','status','generator_file','generator_sha256','interpretation','runtime_changed','query_ui_integration_performed','full_goal_complete'}
    if not set(manifest['view_metadata'])<=allowed or any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('No runtime or completion promotion')
    result.update(copy.deepcopy(manifest['view_metadata']));result['inventory_base_file']=manifest['base']['json']['file'];result['inventory_addendum_files']=[p['json']['file'] for p in manifest['addenda']];result['member_depth_index_scope']='base_only_not_updated_for_addenda';return result


def combined_csv_bytes(manifest,reader):
    load_inventory(manifest,reader);first=csv.DictReader(io.StringIO(checked_piece(manifest['base']['csv'],reader).decode()));columns=list(first.fieldnames);rows=list(first)
    for part in manifest['addenda']:
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));columns.extend(k for k in incoming.fieldnames if k not in columns);rows.extend(list(incoming))
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows);return out.getvalue().encode()
