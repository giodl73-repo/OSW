"""Primary-abstract Rim evidence; pressure observations never masquerade as metres."""
import copy,csv,io,json
from collections import Counter
import load_current_depth_reference_inventory_v1 as base
import load_current_depth_reference_inventory_v8 as defaults
import load_current_depth_reference_inventory_v16 as prior

SCHEMA='osw.current-depth-rim-native-vertical-addendum.v1'
FACTS='research/rim-oguz1999-native-vertical-source-facts-v1.json'
CONTEXT='rim-oguz1999-western-black-sea-april1993'
checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes


def validate_facts(f):
    if f['schema']!='osw.rim-oguz1999-native-vertical-source-facts.v1' or f['entity_id']!='current:black-sea-rim' or f['doi']!='10.1016/S0967-0637(99)00028-X' or f['source_html_sha256']!='ec93ee5e91856d0d7b906416df906fc4d04f59b5c88345847d4a27fe3bc032de' or f['source_html_bytes']!=56703:raise ValueError('Exact primary institutional abstract required')
    if f['source_review_tier']!='PRIMARY_INSTITUTIONAL_ABSTRACT_REVIEWED_FULL_ARTICLE_NOT_REVIEWED' or f['survey_month']!='1993-04' or f['source_abstract_text_reviewed'] is not True:raise ValueError('Original observed month and limited review tier required')
    if any(f[k] for k in ['full_article_obtained','original_pdf_obtained','source_figures_visually_reviewed','raw_CTD_ADCP_reanalysed','pressure_to_depth_conversion_performed','pressure_datum_independently_verified','source_assets_rehashed_in_admission_cloud','physical_current_bottom_established']):raise ValueError('No invented full-text/figure review,pressure conversion or physical depth inference')
    if f['assumed_latitude_degrees_north'] is not None or len(f['records'])!=2:raise ValueError('No invented latitude;exactly two native-coordinate descriptions required')
    transition,pressure=f['records']
    if transition['id']!='observed-layer-transition' or transition['metric']!='reported_local_flow_regime_transition_depth_band' or transition['unit']!='m' or transition['range_m']!=[100,200] or transition['approximate_value_m'] is not None or transition['approximate_value_dbar'] is not None:raise ValueError('Native metre transition band required')
    if pressure['id']!='censored-pressure-reach' or pressure['metric']!='reported_censored_flow_pressure_reach' or pressure['unit']!='dbar' or pressure['approximate_value_dbar']!=350 or pressure['approximate_value_m'] is not None or pressure['range_m'] is not None or pressure['sampling_limit_censors_unknown_flow_bottom'] is not True:raise ValueError('Approximate native pressure reach,not350m or a detected bottom')
    for r in f['records']:
        if r['entity_id']!=f['entity_id'] or any(r[k] is not None for k in ['annual_range_m','uncertainty_m','physical_layer_thickness_m','paired_width_reference_id']) or any(r[k] for k in ['physical_current_bottom_established','volume_eligible','independent_observation_count_claimed']):raise ValueError('Direct owner and no uncertainty,thickness,annual or volume promotion required')


def context_id(owner):
    if owner!='current:black-sea-rim':raise ValueError('Direct Rim owner required')
    return CONTEXT


def source_context(f,owner):
    context_id(owner)
    return {'entity_id':owner,'survey_month':'1993-04','region':'western Black Sea continental slope jet','source_review_tier':f['source_review_tier'],'full_article_obtained':False,'original_pdf_obtained':False,'source_figures_visually_reviewed':False,'reported_transition_depth_band_m':[100,200],'reported_flow_pressure_reach_approx_dbar':350,'pressure_sampling_limit_is_current_bottom':False,'pressure_datum_independently_verified':False,'assumed_latitude_degrees_north':None,'pressure_to_depth_conversion_performed':False,'physical_current_bottom_established':False,'raw_CTD_ADCP_reanalysed':False}


def reference(f,r,index,piece):
    row={k:None for k in defaults.NULL_FIELDS};row.update({k:False for k in defaults.FALSE_FIELDS})
    pressure=r['unit']=='dbar'
    row.update(id='rim-oguz1999-'+r['id'],entity_id=f['entity_id'],metric=r['metric'],unit=r['unit'],approximate_value_m=None,approximate_value_dbar=r['approximate_value_dbar'],range_m=copy.deepcopy(r['range_m']),range_interpretation=None if pressure else 'Source local pycnocline/flow-regime transition interval;not full layer thickness,seasonal range or uncertainty.',vertical_datum='source_reported_pressure_dbar_datum_not_independently_verified' if pressure else 'source_reported_depth_below_sea_surface',phase_label='April1993westernBlackSeaSurvey',calendar_months=None,observed_period={'survey_month':'1993-04'},geographic_scope='Western Black Sea continental-slope Rim jet during April1993;not a basin-wide or whole-route depth.',temporal_scope='Primary study abstract describes the April1993 CTD/ADCP survey;publication1999 is not the observation year or seasonal climatology.',source_definition=r['source_definition'],evidence_kind='primary_institutional_abstract_reported_observation',source_url=f['source_url'],source_citation=f['source_citation'],source_locator='OpenMETU institutional record primary abstract,vertical two-layer structure paragraph.',qualification='Primary abstract reviewed;full article/methods and original figures not reviewed. Native approximately350dbar is an ADCP-censored flow observation with unknown deeper extent,not350m or an exact bottom. No assumed latitude,pressure conversion,physical thickness,annual range,width join or volume. Distinct from the undated250–300m near-halt synthesis.',source_context_id=CONTEXT,source_file=piece['file'],source_sha256=piece['sha256'],source_pointer='/records/'+str(index),source_reported_record=copy.deepcopy(r),source_review_tier=f['source_review_tier'],source_html_sha256=f['source_html_sha256'],original_pdf_obtained=False,source_pdf_sha256=None,full_article_obtained=False,pressure_to_depth_conversion_performed=False,pressure_datum_independently_verified=False,source_assets_rehashed_in_admission_cloud=False,raw_CTD_ADCP_reanalysed=False)
    return row


def assemble(*parts):
    result=prior.assemble(*parts[:-1]);seen={r['id'] for r in result['evidence']}
    for a,f in parts[-1]:
        validate_facts(f);expected=[reference(f,r,i,a['reviewed_source_facts']) for i,r in enumerate(f['records'])];contexts={CONTEXT:source_context(f,'current:black-sea-rim')}
        if a['evidence']!=expected or a['source_contexts']!=contexts or CONTEXT in result['source_contexts'] or any(r['id'] in seen for r in expected):raise ValueError('Exact native-coordinate rows and unique context required')
        seen.update(r['id'] for r in expected);result['evidence'].extend(copy.deepcopy(expected));result['source_contexts'].update(copy.deepcopy(contexts))
    for r in result['records']:r['depth_reference_ids']=[e['id'] for e in result['evidence'] if e['entity_id']==r['entity_id']]
    result['counts']=base.counts_for(result['records'],result['evidence']);result['metric_counts']=dict(sorted(Counter(r['metric'] for r in result['evidence']).items()));result['coordinate_unit_counts']=dict(sorted(Counter(r['unit'] for r in result['evidence']).items()));return result


def read_parts(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v17':raise ValueError('Reference inventoryv16 required')
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
    return (*prior.read_parts({'schema':'osw.current-depth-reference-inventory.v16','base':manifest['base'],'addenda':old},reader),new)


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
