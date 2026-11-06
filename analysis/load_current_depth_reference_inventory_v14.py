"""Provisional primary-text flow-transition bands; never physical bottom depths."""
import copy,csv,io,json
from collections import Counter
import load_current_depth_reference_inventory_v1 as base
import load_current_depth_reference_inventory_v8 as defaults
import load_current_depth_reference_inventory_v13 as prior

SCHEMA='osw.current-depth-loop-reported-transition-addendum.v1'
CONTEXT='loop-welsh2009-local-progressive-vector-transition'
METRIC='reported_local_flow_regime_transition_depth_band'
FACTS='research/loop-welsh2009-local-transition-depth-source-facts-v1.json'
checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes


def validate_facts(facts):
    if facts['schema']!='osw.loop-welsh2009-local-transition-depth-source-facts.v1' or facts['entity_id']!='current:loop' or facts['review_status']!='PROVISIONAL_PRIMARY_INDEXED_TEXT_TRANSCRIPTION_PENDING_VISUAL_CROSSCHECK':raise ValueError('Exact provisional source identity and review tier required')
    if facts['source_pdf_bytes_verified'] is not False or facts['source_pdf_sha256'] is not None or facts['source_pdf_pages_visually_reviewed']!=[] or facts['source_numeric_contours_digitized'] is not False or facts['raw_mooring_data_reanalysed'] is not False:raise ValueError('Do not claim unperformed PDF custody,visual review or analysis')
    if facts['primary_indexed_source_text_reviewed'] is not True or facts['nominal_source_site_lon_lat']!=[-87,25.5] or facts['source_report_number']!='OCS Study MMS 2009-050':raise ValueError('Original reported nominal site/report context required')
    expected=[('deployment-4',[750,875],['2005-05-30','2006-02-12'],'primarily_eastern_side_of_Loop_Current'),('deployment-5',[775,1015],['2006-06-18','2007-03-20'],'primarily_western_side_of_Loop_Current')]
    if len(facts['records'])!=2:raise ValueError('Exactly two original diagnostic records required')
    for record,(identity,band,window,side) in zip(facts['records'],expected):
        if record['id']!=identity or record['reported_transition_depth_band_m']!=band or record['diagnostic_common_record_dates']!=window or record['relative_Loop_Current_position']!=side or record['diagnostic']!='progressive_current_vector_comparison' or record['printed_page']!=42 or record['source_pdf_page']!=54 or record['date_caption_pdf_page']!=56:raise ValueError('Exact method-specific reported bands and common-record windows required')
        if record['physical_current_bottom_established'] or record['annual_extrema_established'] or record['independent_observation_count_claimed'] or record['volume_eligible'] or record['uncertainty_m'] is not None or record['physical_layer_thickness_m'] is not None:raise ValueError('No physical,annual,uncertainty,independence or volume promotion')
    if facts['alternate_deployment5_ellipse_transition_band_m']!=[786,1090] or facts['alternate_diagnostic_band_is_uncertainty'] is not False:raise ValueError('Different ellipse diagnostic is context,not uncertainty or an independent measurement')


def source_context(facts):
    return {'entity_id':'current:loop','source_report_number':facts['source_report_number'],'nominal_source_site_lon_lat':facts['nominal_source_site_lon_lat'],'site_precision':'rounded nominal location reported in introduction; not a new geospatial join','diagnostic':'progressive_current_vector_comparison','feature_scope':'local upper/lower circulation transition under Loop Current and ring influence; no individual ring measurement','review_status':facts['review_status'],'source_pdf_bytes_verified':False,'source_pdf_pages_visually_reviewed':[],'physical_current_bottom_established':False,'alternate_deployment5_ellipse_transition_band_m':[786,1090],'alternate_diagnostic_is_uncertainty':False}


def reference(facts,record,index,piece):
    row={k:None for k in defaults.NULL_FIELDS};row.update({k:False for k in defaults.FALSE_FIELDS})
    row.update(id='loop-welsh2009-'+record['id']+'-local-transition-band',entity_id='current:loop',metric=METRIC,unit='m',vertical_datum='source_reported_depth_below_sea_surface',range_m=copy.deepcopy(record['reported_transition_depth_band_m']),range_interpretation='reported local vertical flow-regime transition interval; not annual extrema,statistical uncertainty or whole-layer thickness',phase_label=record['id'],observed_period=copy.deepcopy(record['diagnostic_common_record_dates']),geographic_scope='One eastern Gulf of Mexico mooring,nominal25.5N87W;regional Loop Current/ring-influenced context.',temporal_scope='Progressive-vector longest-common-record window from figure3-7 caption;not the full deployment interval or seasonal climatology.',source_definition='Published interpretation of a local change from upper to lower circulation using progressive current vectors;not a sharp physical current bottom.',evidence_kind='provisional_primary_report_text_local_flow_regime_transition_band',source_url=facts['source_url'],source_citation=facts['source_citation'],source_locator='Section3.3,printedp42/PDFpage54;figure3-7 common-record dates printedp44/PDFpage56.',qualification='Primary indexed text reviewed;exact PDF bytes and rendered pages not verified because bounded custody attempt exceeded7MB. Local flow includes Loop Current and ring influence. Different ellipse diagnostic is not an error bar or independent observation. No uniform thickness,annual range,whole-route or volume inference.',source_context_id=CONTEXT,source_file=piece['file'],source_sha256=piece['sha256'],source_pointer='/records/'+str(index),source_reported_record=copy.deepcopy(record),source_review_status=facts['review_status'],source_pdf_bytes_verified=False,source_pdf_sha256=None,source_pdf_pages_visually_reviewed=[],raw_mooring_data_reanalysed=False)
    return row


def assemble(*parts):
    result=prior.assemble(*parts[:-1]);seen={r['id'] for r in result['evidence']}
    for addendum,facts in parts[-1]:
        validate_facts(facts);expected=[reference(facts,r,i,addendum['reviewed_source_facts']) for i,r in enumerate(facts['records'])]
        if addendum['evidence']!=expected or addendum['source_contexts']!={CONTEXT:source_context(facts)} or CONTEXT in result['source_contexts']:raise ValueError('Exact source bands and unique context required')
        if any(r['id'] in seen for r in expected) or 'current:loop' not in {r['entity_id'] for r in result['records']}:raise ValueError('Unique known direct owner required')
        seen.update(r['id'] for r in expected);result['evidence'].extend(copy.deepcopy(expected));result['source_contexts'][CONTEXT]=source_context(facts)
    for record in result['records']:record['depth_reference_ids']=[e['id'] for e in result['evidence'] if e['entity_id']==record['entity_id']]
    result['counts']=base.counts_for(result['records'],result['evidence']);result['metric_counts']=dict(sorted(Counter(r['metric'] for r in result['evidence']).items()));return result


def read_parts(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v14':raise ValueError('Reference inventoryv14 required')
    old=[];new=[];seen=set()
    for part in manifest['addenda']:
        if part['id'] in seen:raise ValueError('Duplicate addendum identity')
        seen.add(part['id']);a=json.loads(checked_piece(part['json'],reader))
        if a['schema']!=SCHEMA:
            if new:raise ValueError('Original source classes must precede new source')
            old.append(part);continue
        if a['id']!=part['id'] or a['base_snapshot_sha256']!=manifest['base']['json']['sha256'] or a['runtime_changed'] or a['full_goal_complete'] or a['reviewed_source_facts']['file']!=FACTS:raise ValueError('Original base,exact source and non-promotion required')
        facts=json.loads(checked_piece(a['reviewed_source_facts'],reader));incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));rows=list(incoming);fields=list(incoming.fieldnames)
        if len(rows)!=len(a['evidence']) or set(fields)!={k for r in a['evidence'] for k in r} or any(row!={k:base.cell(raw.get(k)) for k in fields} for raw,row in zip(a['evidence'],rows)):raise ValueError('Every exact typed JSON/CSV cell required')
        new.append((a,facts))
    if len(new)!=1:raise ValueError('Exactly one new source addendum required')
    return (*prior.read_parts({'schema':'osw.current-depth-reference-inventory.v13','base':manifest['base'],'addenda':old},reader),new)


def load_inventory(manifest,reader):
    result=assemble(*read_parts(manifest,reader))
    if result['counts']!=manifest['counts'] or result['metric_counts']!=manifest['metric_counts']:raise ValueError('All reference counts must reproduce')
    allowed={'schema','status','generator_file','generator_sha256','interpretation','runtime_changed','query_ui_integration_performed','full_goal_complete'}
    if not set(manifest['view_metadata'])<=allowed or any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('No runtime or completion promotion')
    result.update(copy.deepcopy(manifest['view_metadata']));result['inventory_base_file']=manifest['base']['json']['file'];result['inventory_addendum_files']=[p['json']['file'] for p in manifest['addenda']];result['member_depth_index_scope']='base_only_not_updated_for_addenda';return result


def combined_csv_bytes(manifest,reader):
    load_inventory(manifest,reader);first=csv.DictReader(io.StringIO(checked_piece(manifest['base']['csv'],reader).decode()));columns=list(first.fieldnames);rows=list(first)
    for part in manifest['addenda']:
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));columns.extend(k for k in incoming.fieldnames if k not in columns);rows.extend(list(incoming))
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows);return out.getvalue().encode()
