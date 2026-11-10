"""Preserve published coastal salinity-front foot scales without bottom promotion."""
import copy,csv,io,json,math
from collections import Counter
import load_current_depth_reference_inventory_v1 as base_loader
import load_current_depth_reference_inventory_v8 as defaults
import load_current_depth_reference_inventory_v10 as prior

checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes
SCHEMA='osw.current-depth-coastal-front-foot-addendum.v1'
CONTEXT='egcc-sutherland2008-reported-coastal-front-foot'
METRIC='reported_coastal_front_foot_depth_scale'
IDS=['jr105-2004-section1','jr105-2004-section2','oc369-2001-cape-farewell','oc380-2002-cape-farewell','oc395-2003-cape-farewell']


def source_context(facts):
    return {'entity_id':facts['entity_id'],'source_definition':copy.deepcopy(facts['source_definition']),'depth_rule':'34_isohaline_intersection_with_nearshore_seabed','source_salinity_contour_psu':34,'physical_current_bottom_established':False,'source_PDF_rehashed_in_cloud':False}


def validate_facts(facts):
    if facts['schema']!='osw.egcc-sutherland2008-coastal-front-depth-source-facts.v1' or facts['entity_id']!='current:east-greenland-coastal' or [r['id'] for r in facts['records']]!=IDS or facts['source_pdf_pages_visually_reviewed']!=[3,4,5,12,15]:raise ValueError('All five reviewed original directly owned source scales required')
    if facts['source_contours_digitized'] is not False or facts['original_raw_CTD_or_ADCP_obtained'] is not False or any(facts[k] for k in ['original_PDF_redistributed','new_reference_inventory_rows_admitted','reference_inventory_updated','new_ocean_field_requests','physical_current_bottom_established','runtime_changed','full_goal_complete']):raise ValueError('Original factual source-review stage and non-promotion required')
    for r in facts['records']:
        value=r['reported_coastal_front_foot_depth_m'];exception=r['source_survey_year']==2003
        if r['entity_id']!=facts['entity_id'] or type(value) not in (int,float) or not math.isfinite(value) or value<=0 or r['source_value_is_approximate'] is not True or r['source_depth_scale_symbol']!='h_obs' or r['source_depth_rule']!='34_isohaline_intersection_with_nearshore_seabed' or r['source_salinity_contour_psu']!=34:raise ValueError('Reported approximate coastal34front foot scale required')
        if r['source_2003_salinity_scale_does_not_contain_full_velocity_current'] is not exception or r['source_excluded_from_depth_wind_correlation'] is not exception:raise ValueError('Original2003exception must remain explicit')
        if any(r[k] is not None for k in ['exact_occupation_dates','sampled_lon_lat','paired_width_reference_id','annual_range_m','uncertainty_m','physical_layer_thickness_m']) or any(r[k] is not False for k in ['source_boundary_metric_is_physical_current_bottom','independent_observation_count_claimed','volume_eligible','route_projection_eligible']):raise ValueError('No unsupported dates,coordinates,bottom,span,uncertainty or volume')


def reference(facts,record,index,piece):
    row={k:None for k in defaults.NULL_FIELDS};row.update({k:False for k in defaults.FALSE_FIELDS})
    row.update(id='egcc-sutherland2008-'+record['id']+'-coastal-front-foot',entity_id=record['entity_id'],metric=METRIC,approximate_value_m=record['reported_coastal_front_foot_depth_m'],lower_bound_m=None,lower_bound_operator=None,unit='m',vertical_datum='local_sea_surface_positive_down',phase_label='boreal_summer_'+str(record['source_survey_year']),geographic_scope=record['source_geographic_scope'],temporal_scope=record['source_time_context'],source_definition='Author-reported h_obs depth where the34isohaline intersects the nearshore seabed;not whole EGCCbottom or vertical salinity crossing at an editorial axis.',evidence_kind='published_hydrographic_coastal_front_foot_scale',source_url=facts['source_url'],source_citation=facts['citation'],source_locator='Printedp'+str(record['source_printed_page'])+'/PDFpage'+str(record['source_pdf_page'])+';original definition printedp61.',qualification='Source approximate regional front scale from gridded hydrography and nearshore bathymetry. Different-year summer samples are not annual extrema. The2003scale does not contain the full velocity current and remains excluded from source depth-wind correlation. No physical bottom,uniform thickness,paired width or volume.',source_context_id=CONTEXT,source_file=piece['file'],source_sha256=piece['sha256'],source_pointer='/records/'+str(index),source_reported_record=copy.deepcopy(record),source_original_definition=copy.deepcopy(facts['source_definition']),source_pdf_sha256=facts['source_pdf_sha256'],source_pdf_bytes=facts['source_pdf_bytes'],source_PDF_rehashed_in_cloud=False,source_raw_CTD_or_ADCP_reanalysed=False,source_contours_digitized=False)
    return row


def assemble(*parts):
    result=prior.assemble(*parts[:-1]);known={r['entity_id'] for r in result['records']};seen={r['id'] for r in result['evidence']}
    for a,facts in parts[-1]:
        validate_facts(facts);expected=[reference(facts,r,i,a['reviewed_source_facts']) for i,r in enumerate(facts['records'])]
        if a['source_contexts']!={CONTEXT:source_context(facts)} or CONTEXT in result['source_contexts'] or a['evidence']!=expected or a['source_PDF_rehashed_in_cloud'] is not False:raise ValueError('Exact reviewed context and all five reported scales required')
        for row in expected:
            if row['id'] in seen or row['entity_id'] not in known:raise ValueError('Unique known direct owner required')
            seen.add(row['id'])
        result['source_contexts'][CONTEXT]=source_context(facts);result['evidence'].extend(copy.deepcopy(expected))
    for r in result['records']:r['depth_reference_ids']=[e['id'] for e in result['evidence'] if e['entity_id']==r['entity_id']]
    result['counts']=base_loader.counts_for(result['records'],result['evidence']);result['metric_counts']=dict(sorted(Counter(r['metric'] for r in result['evidence']).items()));return result


def read_parts(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v11':raise ValueError('Known reference inventory v11 required')
    old=[];front=[];seen=set()
    for part in manifest['addenda']:
        if part['id'] in seen:raise ValueError('Duplicate addendum identity')
        seen.add(part['id']);a=json.loads(checked_piece(part['json'],reader))
        if a['schema']!=SCHEMA:
            if front:raise ValueError('Prior source classes must precede front scales')
            old.append(part);continue
        if a['id']!=part['id'] or a['base_snapshot_sha256']!=manifest['base']['json']['sha256'] or a['runtime_changed'] or a['full_goal_complete']:raise ValueError('Exact source/base/admission identity required')
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));rows=list(incoming);fields=list(incoming.fieldnames)
        if len(rows)!=len(a['evidence']) or set(fields)!={k for r in a['evidence'] for k in r} or any(row!={k:base_loader.cell(raw.get(k)) for k in fields} for raw,row in zip(a['evidence'],rows)):raise ValueError('All exact typed source JSON/CSVcells required')
        facts=json.loads(checked_piece(a['reviewed_source_facts'],reader));front.append((a,facts))
    return (*prior.read_parts({'schema':'osw.current-depth-reference-inventory.v10','base':manifest['base'],'addenda':old},reader),front)


def load_inventory(manifest,reader):
    result=assemble(*read_parts(manifest,reader))
    if result['counts']!=manifest['counts'] or result['metric_counts']!=manifest['metric_counts']:raise ValueError('Reference counts do not reproduce')
    allowed={'schema','status','generator_file','generator_sha256','interpretation','runtime_changed','query_ui_integration_performed','full_goal_complete'}
    if not set(manifest['view_metadata'])<=allowed or any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('No runtime or completion promotion')
    result.update(copy.deepcopy(manifest['view_metadata']));result['inventory_base_file']=manifest['base']['json']['file'];result['inventory_addendum_files']=[p['json']['file'] for p in manifest['addenda']];result['member_depth_index_scope']='base_only_not_updated_for_addenda';return result


def combined_csv_bytes(manifest,reader):
    load_inventory(manifest,reader);first=csv.DictReader(io.StringIO(checked_piece(manifest['base']['csv'],reader).decode()));columns=list(first.fieldnames);rows=list(first)
    for part in manifest['addenda']:
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));columns.extend(k for k in incoming.fieldnames if k not in columns);rows.extend(list(incoming))
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows);return out.getvalue().encode()
