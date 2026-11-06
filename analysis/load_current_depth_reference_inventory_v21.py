"""Indirect current-associated bedform depth context, with no physical promotion."""
import copy,csv,io,json
from collections import Counter
import load_current_depth_reference_inventory_v1 as base
import load_current_depth_reference_inventory_v8 as defaults
import load_current_depth_reference_inventory_v20 as prior

SCHEMA='osw.current-depth-jutland-bedform-depth-addendum.v1'
FACTS='research/jutland-kuijpers1993-bedform-depth-source-facts-v1.json'
CONTEXT='jutland-kuijpers1993-indirect-bedform-depth-context'
OWNER='current:jutland'
checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes


def validate_facts(f):
    if f['schema']!='osw.jutland-kuijpers1993-bedform-depth-source-facts.v1' or f['entity_id']!=OWNER or f['doi']!='10.1016/0025-3227(93)90131-E' or f['primary_publisher_abstract_reviewed'] is not True:raise ValueError('Original abstract and direct named owner required')
    for key in ['full_article_reviewed','exact_html_bytes_retained','physical_current_bottom_established','direct_current_depth_measurement','source_figure_digitized','raw_survey_data_reanalysed','original_pdf_or_figure_redistributed','runtime_changed','full_goal_complete']:
        if f[key] is not False:raise ValueError('No source-work or physical promotion')
    if f['source_html_sha256'] is not None or f['new_ocean_field_requests']!=0 or f['new_raw_measurements']!=0 or len(f['records'])!=1:raise ValueError('One indirect reference, no invented source custody or raw observations')
    c=f['reported_context']
    if c['source_method']!='side_scan_sonar_surveys_and_bedform_interpretation' or c['sites']!=['off_Hanstholm','off_Hirtshals'] or c['reported_bedform_field_water_depth_extent_m']!=70 or c['exact_survey_dates'] is not None:raise ValueError('Combined original survey context and unknown dates required')
    for key in ['depth_datum_independently_resolved','site_specific_depth_extents_separately_reported_in_reviewed_abstract','direct_velocity_profile_available','core_to_seabed_vertical_connectivity_established']:
        if c[key] is not False:raise ValueError('No site, datum, velocity or vertical-connectivity invention')
    if c['active_bedforms_interpretation_reported'] is not True or c['Jutland_current_association_explicit_in_abstract'] is not True:raise ValueError('Author interpretation and explicit named-current association required')
    row=f['records'][0]
    if row['id']!='jutland-kuijpers1993-current-associated-bedform-water-depth-extent' or row['entity_id']!=OWNER or row['metric']!='current_associated_bedform_field_water_depth_extent' or row['approximate_value_m']!=70 or row['range_m'] is not None or row['reference_route_projection_eligible'] is not False:raise ValueError('Indirect bedform water-depth role only')


def source_context(f,owner):
    if owner!=OWNER:raise ValueError('One direct owner required')
    return {k:copy.deepcopy(f[k]) for k in ['entity_id','doi','source_url','source_locator','source_access','primary_publisher_abstract_reviewed','full_article_reviewed','exact_html_bytes_retained','source_html_sha256','reported_context','qualifications']}


def context_id(owner):
    if owner!=OWNER:raise ValueError('One direct owner required')
    return CONTEXT


def reference(f,r,index,piece):
    row={k:None for k in defaults.NULL_FIELDS};row.update({k:False for k in defaults.FALSE_FIELDS})
    row.update(id=r['id'],entity_id=OWNER,metric=r['metric'],unit='m',approximate_value_m=70,vertical_datum='source_reported_water_depth_datum_unspecified',phase_label='undated_survey_context_reported_in1993',geographic_scope=r['geographic_scope'],temporal_scope='Survey dates unresolved in reviewed publisher abstract; publication year is not an occupation date.',source_definition='Reported water-depth extent of current-associated bedforms, an indirect regional bottom-flow context; not a current layer or velocity contour.',evidence_kind='published_sonar_bedform_depth_context_with_author_current_association',source_url=f['source_url'],source_citation=f['source_citation'],source_locator=f['source_locator'],qualification='One combined survey-scope indirect context. No site-specific70m assignment, direct velocity profile, surface-to-bed connectivity, current thickness/bottom, uncertainty, annual range or paired volume geometry.',source_context_id=CONTEXT,source_file=piece['file'],source_sha256=piece['sha256'],source_pointer='/records/0',source_reported_record=copy.deepcopy(r),primary_publisher_abstract_reviewed=True,full_article_reviewed=False,direct_current_depth_measurement=False,physical_depth_ranking_eligible=False,core_to_seabed_vertical_connectivity_established=False,bedform_height_m=None,source_geographic_geometry=None,source_survey_dates=None,source_html_sha256=None,raw_survey_data_reanalysed=False,source_figure_digitized=False)
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
    if manifest['schema']!='osw.current-depth-reference-inventory.v21':raise ValueError('Reference inventoryv21 required')
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
    return (*prior.read_parts({'schema':'osw.current-depth-reference-inventory.v20','base':manifest['base'],'addenda':old},reader),new)


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
