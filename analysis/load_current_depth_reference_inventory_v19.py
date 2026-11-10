"""Source-named PGW salinity-core depth progression without geographic or layer inference."""
import copy,csv,io,json
from collections import Counter
import load_current_depth_reference_inventory_v1 as base
import load_current_depth_reference_inventory_v8 as defaults
import load_current_depth_reference_inventory_v18 as prior

SCHEMA='osw.current-depth-pgw-core-depth-regimes-addendum.v1'
FACTS='research/pgw-pous-2004-core-depth-regimes-source-facts-v1.json'
CONTEXT='pgw-pous-2004-source-named-core-depth-progression'
OWNER='current:persian-gulf-saline-overflow'
checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes


def validate_facts(f):
    if f['schema']!='osw.pgw-pous-core-depth-regimes-source-facts.v1' or f['entity_id']!=OWNER or f['doi']!='10.1029/2003JC002146' or f['primary_publisher_text_reviewed'] is not True or f['source_html_sha256'] is not None or f['exact_html_bytes_retained'] is not False:raise ValueError('Honest primary prose source and one direct PGW owner required')
    if f['campaign_window']!={'start':'1999-10-08','end':'1999-11-10'} or f['campaign_window_is_exact_common_occupation'] is not False:raise ValueError('Campaign window is not an exact common occupation')
    for key in ['source_figure_digitized','raw_casts_reanalysed','author_version_reacquired_in_this_admission','original_pdf_or_figure_redistributed','runtime_changed','full_goal_complete']:
        if f[key] is not False:raise ValueError('No invented source work or promotion')
    if f['new_ocean_field_requests']!=0 or f['new_raw_measurements']!=0 or len(f['records'])!=2:raise ValueError('Exactly two regional prose descriptions, no new raw measurements')
    expected=[('pgw-pous-2004-strait-shelf-core-depth-span',None,[70,120],'strait_and_northwestern_gulf_shelf_before_detachment',[]),('pgw-pous-2004-r18-r17-detached-core-depth',200,None,'r18_r17_descent_to_neutral_buoyancy',['R18','R17'])]
    for r,(name,value,span,role,sections) in zip(f['records'],expected):
        if r['id']!=name or r['entity_id']!=OWNER or r['approximate_value_m']!=value or r['range_m']!=span or r['geographic_role']!=role or r['section_ids']!=sections or r['reference_route_projection_eligible'] is not False:raise ValueError('Keep distinct source-named core depths, no midpoint or fabricated mapping')
    p=f['downstream_profile_context']
    if p['coordinate_kind']!='source_named_regions_and_relative_distances_not_georeferenced_route' or p['regional_progression']!=['strait_and_shelf','R18_R17_descent','post_R17','R14_to_R02'] or p['post_R17']['reported_core_depth_approximately_m']!=200 or p['post_R17']['reported_distance_approximately_km']!=200 or not p['post_R17']['R15_exception'] or p['R14_to_R02']['reported_distance_approximately_km']!=300 or p['R14_to_R02']['reported_core_shoaling_exclusive_upper_bound_m']!=30 or p['R14_to_R02']['absolute_endpoint_depths_m'] is not None or p['R14_to_R02']['bound_is_absolute_depth_or_annual_range'] is not False:raise ValueError('Retain source relative progression and R15 exception without invented endpoints')
    if p['R12_excluded_by_authors'] is not True or p['plotted_vertices_extracted']!=0 or p['mapped_section_positions'] is not None or any(p[k] for k in ['interpolation_performed','top_bottom_inferred_by_centering_thickness_on_core','thickness_or_width_values_joined','new_independent_observations_claimed']):raise ValueError('No curve, geographic, symmetric-layer, volume or independence inference')


def source_context(f,owner):
    if owner!=OWNER:raise ValueError('Direct PGW owner required')
    return {k:copy.deepcopy(f[k]) for k in ['entity_id','doi','source_url','source_locator','primary_publisher_text_reviewed','source_html_sha256','exact_html_bytes_retained','source_figure_digitized','raw_casts_reanalysed','campaign_window','campaign_window_is_exact_common_occupation','core_definition','downstream_profile_context','qualifications']}


def context_id(owner):
    if owner!=OWNER:raise ValueError('Direct PGW owner required')
    return CONTEXT


def reference(f,r,index,piece):
    row={k:None for k in defaults.NULL_FIELDS};row.update({k:False for k in defaults.FALSE_FIELDS})
    row.update(id=r['id'],entity_id=OWNER,metric='core_depth',unit='m',approximate_value_m=r['approximate_value_m'],range_m=copy.deepcopy(r['range_m']),range_interpretation=r['range_interpretation'],vertical_datum='local_sea_surface_positive_down',phase_label='GOGP99_source_named_regional_description',calendar_months=None,observed_period=None,geographic_scope=r['geographic_scope'],temporal_scope='GOGP99 October-November1999 campaign context; not an exact common occupation, seasonal average or annual envelope.',source_definition=f['core_definition'],evidence_kind='published_regional_salinity_core_depth_description',source_url=f['source_url'],source_citation=f['source_citation'],source_locator=r['source_locator'],qualification='Approximate source-named spatial core-depth description, not a paired top/bottom, physical thickness, uncertainty, annual range, separate independent cast or geographic route projection. Keep existing220m summary separately; no averaging or symmetric-thickness inference.',source_context_id=CONTEXT,source_file=piece['file'],source_sha256=piece['sha256'],source_pointer='/records/'+str(index),source_reported_record=copy.deepcopy(r),source_html_sha256=None,primary_publisher_text_reviewed=True,raw_casts_reanalysed=False,source_figure_digitized=False,source_geographic_role=r['geographic_role'],source_section_ids=copy.deepcopy(r['section_ids']),campaign_window=copy.deepcopy(f['campaign_window']),window_role='whole_campaign_not_exact_core_occupation',range_is_confidence_interval=False,range_is_annual_envelope=False)
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
    if manifest['schema']!='osw.current-depth-reference-inventory.v19':raise ValueError('Reference inventoryv19 required')
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
    return (*prior.read_parts({'schema':'osw.current-depth-reference-inventory.v18','base':manifest['base'],'addenda':old},reader),new)


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
