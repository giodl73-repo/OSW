"""Provisional local winter mean-flow reach; native sampling support is not thickness."""
import copy,csv,io,json
from collections import Counter
import load_current_depth_reference_inventory_v1 as base
import load_current_depth_reference_inventory_v8 as defaults
import load_current_depth_reference_inventory_v17 as prior

SCHEMA='osw.current-depth-alaska-winter-reach-addendum.v1'
FACTS='research/alaska-jarosz2017-winter-reach-source-facts-v1.json'
CONTEXT='alaska-jarosz2017-kayak-winter2012-2013'
OWNER='current:alaska-coastal-gulf'
TIER='PROVISIONAL_PRIMARY_INDEXED_TEXT_TRANSCRIPTION_PENDING_ORIGINAL_SOURCE_CROSSCHECK'
checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes
EXPECTED=[('B1',[7,60],62.9,'2012-10-19','2013-03-16'),('B2',[7,62],65.8,'2012-10-19','2013-03-13'),('L',[9,70],73.2,'2012-10-18','2013-03-13'),('B3',[11,93],96.9,'2012-10-19','2013-03-13')]


def validate_facts(f):
    if f['schema']!='osw.alaska-jarosz2017-winter-reach-source-facts.v1' or f['entity_id']!=OWNER or f['doi']!='10.1002/2016JC012102' or f['source_review_tier']!=TIER:raise ValueError('Direct Alaska Coastal owner and provisional primary indexed-text tier required')
    if f['primary_indexed_text_reviewed'] is not True or f['flow_attribution_reviewed'] is not True or f['mean_flow_through_sampled_column_reviewed'] is not True or f['temporary_full_and_partial_flow_reversals_reported'] is not True:raise ValueError('Sampling support alone is not current-flow evidence')
    if f['source_html_sha256'] is not None or any(f[k] for k in ['full_article_obtained','original_pdf_obtained','source_figures_visually_reviewed','raw_velocity_profiles_reanalysed','source_assets_rehashed_in_admission_cloud','physical_current_bottom_established']):raise ValueError('No invented exact article custody,figure review or physical bottom')
    if (f['reported_native_ADCP_bin_m'],f['author_resampling_m'],f['author_current_rotation_degrees_counterclockwise_from_east'],f['author_low_pass_cutoff_hours'])!=(2,1,24,40) or len(f['records'])!=4:raise ValueError('Exact four stations and source processing required')
    for r,(station,support,bed,start,end) in zip(f['records'],EXPECTED):
        if r['station']!=station or r['entity_id']!=OWNER or r['metric']!='reported_censored_mean_flow_reach' or r['unit']!='m' or r['observed_reach_m']!=support[1] or r['sampled_depth_range_m']!=support or r['site_water_depth_m']!=bed or r['observed_period']!={'start':start,'end':end}:raise ValueError('Keep station reach,sampling and bed distinct with actual deployment dates')
        if r['temporal_statistic']!='deployment_mean_not_continuous_instantaneous_flow' or r['sampling_limit_censors_unknown_flow_bottom'] is not True:raise ValueError('Mean flow and sampling censor required')
        if any(r[k] is not None for k in ['annual_range_m','uncertainty_m','physical_layer_thickness_m','paired_width_reference_id']) or any(r[k] for k in ['physical_current_bottom_established','volume_eligible','independent_seasonal_replicate_claimed']):raise ValueError('No annual/thickness/volume/independence promotion')


def context_id(owner):
    if owner!=OWNER:raise ValueError('Direct Alaska Coastal owner required')
    return CONTEXT


def source_context(f,owner):
    context_id(owner)
    return {k:copy.deepcopy(f[k]) for k in ['entity_id','source_review_tier','primary_indexed_text_reviewed','full_article_obtained','original_pdf_obtained','source_figures_visually_reviewed','reported_native_ADCP_bin_m','author_resampling_m','author_current_rotation_degrees_counterclockwise_from_east','author_low_pass_cutoff_hours','temporary_full_and_partial_flow_reversals_reported','physical_current_bottom_established']}


def reference(f,r,index,piece):
    row={k:None for k in defaults.NULL_FIELDS};row.update({k:False for k in defaults.FALSE_FIELDS})
    row.update(id='alaska-jarosz2017-'+r['id'],entity_id=OWNER,metric=r['metric'],unit='m',lower_bound_m=r['observed_reach_m'],lower_bound_exclusive=False,approximate_value_m=None,range_m=None,vertical_datum='source_reported_depth_below_sea_surface',phase_label='winter2012-2013DeploymentMean',calendar_months=None,observed_period=copy.deepcopy(r['observed_period']),station=r['station'],sampled_depth_range_m=copy.deepcopy(r['sampled_depth_range_m']),site_water_depth_m=r['site_water_depth_m'],source_position=copy.deepcopy(r['source_position']),temporal_statistic=r['temporal_statistic'],sampling_limit_censors_unknown_flow_bottom=True,geographic_scope='Shelf southeast of Kayak Island;local station '+r['station']+' within Alaska Coastal Current,not Alaska Current or Alaskan Stream.',temporal_scope='Station-specific October2012-March2013 deployment mean;temporary full/partial reversals occur. Not an annual climatology or continuous instantaneous flow.',source_definition=r['source_definition'],evidence_kind='provisional_primary_indexed_text_mean_flow_reach',source_url=f['source_url'],source_citation=f['source_citation'],source_locator='Table1 ADCP station support/dates;Section2 author processing;Section6 mean along-shelf flow paragraph and reversal paragraph;Figure9 caption text only.',qualification='Provisional primary indexed-text transcription pending original source crosscheck. OriginalHTML request403;no exact article/PDF custody or visual figure review. Inclusive observed reach,not detected bottom or site bed. No surface/bed blind-zone extrapolation,physical thickness,annual range,independent seasonal replicates,width join or volume.',source_context_id=CONTEXT,source_file=piece['file'],source_sha256=piece['sha256'],source_pointer='/records/'+str(index),source_reported_record=copy.deepcopy(r),source_review_tier=TIER,source_html_sha256=None,original_pdf_obtained=False,source_pdf_sha256=None,full_article_obtained=False,source_figures_visually_reviewed=False,source_assets_rehashed_in_admission_cloud=False,raw_velocity_profiles_reanalysed=False)
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
    if manifest['schema']!='osw.current-depth-reference-inventory.v18':raise ValueError('Reference inventoryv18 required')
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
    return (*prior.read_parts({'schema':'osw.current-depth-reference-inventory.v17','base':manifest['base'],'addenda':old},reader),new)


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
