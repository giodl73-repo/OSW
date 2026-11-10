"""Visually reviewed Ombai seasonal/core bands with current identities separate."""
import copy,csv,io,json
from collections import Counter
import load_current_depth_reference_inventory_v1 as base
import load_current_depth_reference_inventory_v8 as defaults
import load_current_depth_reference_inventory_v14 as prior

SCHEMA='osw.current-depth-ombai-observed-band-addendum.v1'
FACTS='research/ombai-sprintall2010-observed-depth-source-facts-v1.json'
checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes
EXPECTED=[('sjc-north-upper-layer','current:south-java','reported_vertical_extent',[100,150],'OMB-N',None),('sjc-north-sem-core','current:south-java','core_depth',[40,100],'OMB-N',[6,7,8,9]),('itf-north-nwm-core-band','current:indonesian-throughflow','reported_flow_depth_band',[100,250],'OMB-N',[12,1,2,3]),('itf-south-nwm-core-band','current:indonesian-throughflow','reported_flow_depth_band',[100,800],'OMB-S',[12,1,2,3])]


def validate_facts(facts):
    if facts['schema']!='osw.ombai-sprintall2010-observed-depth-source-facts.v1' or facts['doi']!='10.1016/j.dynatmoce.2010.02.006' or facts['source_pdf_pages_visually_reviewed']!=[2,3,4,5,6,7,15] or facts['source_pdf_bytes']!=3841747 or facts['source_pdf_sha256']!='27d0a4d914daedf0cda01d17c473307130b07a35e06e877c8c2b02a1969bf911':raise ValueError('Exact reviewed original paper required')
    if facts['source_pdf_redistributed'] or facts['source_contours_digitized'] or facts['raw_mooring_data_reanalysed'] or facts['source_PDF_rehashed_in_admission_cloud'] or facts['physical_current_bottom_established']:raise ValueError('No raw analysis,PDF redistribution or physical bottom promotion')
    if facts['analysis_years']!=[2004,2005,2006] or len(facts['records'])!=4:raise ValueError('Complete four-record source scope required')
    for record,(identity,owner,metric,band,station,months) in zip(facts['records'],EXPECTED):
        if [record[k] for k in ['id','entity_id','metric','range_m','station','calendar_months']]!=[identity,owner,metric,band,station,months]:raise ValueError('Exact source-specific identity,metric,band,station and phase required')
        if record['direction']!=('eastward' if owner=='current:south-java' else 'westward') or record['temporal_operator']!=('published_full_time_series_description' if identity=='sjc-north-upper-layer' else 'annual_plus_semiannual_harmonic_seasonal_cycle'):raise ValueError('Opposing currents and time operators must remain distinct')
        if any(record[k] is not None for k in ['approximate_value_m','physical_layer_thickness_m','uncertainty_m','annual_range_m','paired_width_reference_id']) or any(record[k] for k in ['physical_current_bottom_established','independent_observation_count_claimed','volume_eligible']):raise ValueError('No midpoint,thickness,uncertainty,annual extrema,width join or volume')
    if facts['source_body_sem_core_band_m']!=[40,100] or facts['source_abstract_and_discussion_sem_core_band_m']!=[50,100] or facts['alternative_core_band_is_uncertainty'] is not False or facts['seasonal_upper_eastward_flow_extent_band_m']!=[100,120]:raise ValueError('Source description differences and separate harmonic extent must remain explicit')


def context_id(owner):return 'ombai-sprintall2010-'+owner.split(':')[1]


def source_context(facts,owner):
    return {'entity_id':owner,'doi':facts['doi'],'branch_scope':'Ombai Strait South Java continuation' if owner=='current:south-java' else 'Ombai branch of Indonesian Throughflow;not a Makassar or whole-system depth','analysis_years':[2004,2005,2006],'station_metadata':copy.deepcopy(facts['stations']),'source_review_status':'EXACT_CLOUD_PDF_AND_RENDERED_PRIMARY_PAGES_REVIEWED','source_PDF_rehashed_in_admission_cloud':False,'physical_current_bottom_established':False,'raw_mooring_data_reanalysed':False,'source_body_sem_core_band_m':[40,100],'source_abstract_and_discussion_sem_core_band_m':[50,100],'description_difference_is_uncertainty':False,'separate_harmonic_upper_eastward_extent_band_m':[100,120],'deeper_SJUC_not_transferred_to_SJC_or_ITF':True}


def reference(facts,record,index,piece):
    row={k:None for k in defaults.NULL_FIELDS};row.update({k:False for k in defaults.FALSE_FIELDS})
    row.update(id='ombai-sprintall2010-'+record['id'],entity_id=record['entity_id'],metric=record['metric'],range_m=copy.deepcopy(record['range_m']),range_interpretation=record['range_interpretation'],unit='m',vertical_datum='source_reported_depth_below_sea_surface',phase_label=record['phase_label'],calendar_months=copy.deepcopy(record['calendar_months']),observed_period={'analysis_years':[2004,2005,2006]},geographic_scope=record['station']+';Ombai Strait;'+('South Java Current continuation' if record['entity_id']=='current:south-java' else 'local Indonesian Throughflow outflow branch'),temporal_scope=record['temporal_operator']+' from the 2004–2006 INSTANT record;not annual extrema or a new independent occupation.',source_definition=record['source_definition'],evidence_kind='published_direct_mooring_flow_description' if record['temporal_operator']=='published_full_time_series_description' else 'published_direct_mooring_harmonic_seasonal_flow_band',source_url=facts['source_url'],source_citation=facts['source_citation'],source_locator=record['source_locator'],qualification='Local source-reported flow/core depth band,not a sharp physical current bottom or uniform thickness. Preserve eastward SJC versus westward ITF and distinct deeper SJUC. Main-text SEM core40–100m differs from abstract/discussion50–100m;neither is an uncertainty interval. No width or volume join.',source_context_id=context_id(record['entity_id']),source_file=piece['file'],source_sha256=piece['sha256'],source_pointer='/records/'+str(index),source_reported_record=copy.deepcopy(record),source_pdf_sha256=facts['source_pdf_sha256'],source_pdf_bytes=facts['source_pdf_bytes'],source_pdf_pages_visually_reviewed=copy.deepcopy(facts['source_pdf_pages_visually_reviewed']),source_PDF_rehashed_in_admission_cloud=False,source_contours_digitized=False,raw_mooring_data_reanalysed=False)
    return row


def assemble(*parts):
    result=prior.assemble(*parts[:-1]);seen={r['id'] for r in result['evidence']};known={r['entity_id'] for r in result['records']}
    for addendum,facts in parts[-1]:
        validate_facts(facts);expected=[reference(facts,r,i,addendum['reviewed_source_facts']) for i,r in enumerate(facts['records'])];contexts={context_id(owner):source_context(facts,owner) for owner in ['current:south-java','current:indonesian-throughflow']}
        if addendum['evidence']!=expected or addendum['source_contexts']!=contexts or set(contexts)&set(result['source_contexts']):raise ValueError('Exact source bands and unique owner contexts required')
        if any(r['id'] in seen or r['entity_id'] not in known for r in expected):raise ValueError('Unique references and known direct owners required')
        seen.update(r['id'] for r in expected);result['evidence'].extend(copy.deepcopy(expected));result['source_contexts'].update(copy.deepcopy(contexts))
    for record in result['records']:record['depth_reference_ids']=[e['id'] for e in result['evidence'] if e['entity_id']==record['entity_id']]
    result['counts']=base.counts_for(result['records'],result['evidence']);result['metric_counts']=dict(sorted(Counter(r['metric'] for r in result['evidence']).items()));return result


def read_parts(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v15':raise ValueError('Reference inventoryv15 required')
    old=[];new=[];seen=set()
    for part in manifest['addenda']:
        if part['id'] in seen:raise ValueError('Duplicate addendum identity')
        seen.add(part['id']);a=json.loads(checked_piece(part['json'],reader))
        if a['schema']!=SCHEMA:
            if new:raise ValueError('Original source classes must precede new source')
            old.append(part);continue
        if a['id']!=part['id'] or a['base_snapshot_sha256']!=manifest['base']['json']['sha256'] or a['runtime_changed'] or a['full_goal_complete'] or a['reviewed_source_facts']['file']!=FACTS:raise ValueError('Exact source,original base and non-promotion required')
        facts=json.loads(checked_piece(a['reviewed_source_facts'],reader));incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));rows=list(incoming);fields=list(incoming.fieldnames)
        if len(rows)!=len(a['evidence']) or set(fields)!={k for r in a['evidence'] for k in r} or any(row!={k:base.cell(raw.get(k)) for k in fields} for raw,row in zip(a['evidence'],rows)):raise ValueError('Every exact typed JSON/CSV cell required')
        new.append((a,facts))
    if len(new)!=1:raise ValueError('Exactly one new source addendum required')
    return (*prior.read_parts({'schema':'osw.current-depth-reference-inventory.v14','base':manifest['base'],'addenda':old},reader),new)


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
