"""Add one local Azores reanalysis mean extent, without source replay."""
import copy,csv,io,json
import load_current_depth_reference_inventory_v36 as previous
import compiled_depth_catalog_view_v1 as compiled
from load_current_depth_reference_inventory_v1 import checked_piece,reference_csv_bytes,cell
SOURCE='research/azores-ibi-mean-depth-descriptors-v1.json'
SOURCE_SHA='d216404f99c932eeb82a7f8341f348e09b1da1cfc7db2b83f0be18fe1da9815e'
CONTEXT='azores-ibi-1993-2021-mean-section-depth'
SCHEMA='osw.current-depth-azores-ibi-mean-local-addendum.v1'
NULLS=previous.NULLS
FALSES=previous.FALSES
def references(source):
    if source['schema']!='osw.azores-ibi-mean-depth-descriptors.v1' or source['canonical_reference_admitted'] is not False:raise ValueError('Qualified source stage required')
    if source['raw_sha256']!='a37fdc1ffc22a5ae83a73a0d32af6f583d206ee15756bad39df8a8f8b4373cbc' or source['source_doi']!='10.5194/sp-4-osr8-5-2024':raise ValueError('Exact primary custody required')
    if len(source['rows'])!=1:raise ValueError('One local reported result only')
    r=source['rows'][0]
    if (r['id'],r['entity_id'],r['metric'],r['approximate_value'],r['unit'])!=('azores-pascual-collar2024-ma-ibi-rea-mean-upper-layer-extent','current:azores','reported_reanalysis_mean_current_upper_layer_extent',600,'m'):raise ValueError('Exact local result and owner required')
    if (r['source_product'],r['source_mean_period'],r['source_section'])!=('IBI-REA',[1993,2021],'MA_north_of_Madeira'):raise ValueError('Mean product, period and local section required')
    if r['source_direction_consistency']!='unresolved_conflicting_primary_labels' or r['omi_boundary_is_fixed_at_reported_extent'] is not False:raise ValueError('Direction conflict and dynamic density windows retained')
    if r['source_statistic']!='author_reported_approximate_extent_of_long_term_mean_section' or r['velocity_component']!='source_section_transverse_velocity_in_long_term_reanalysis_mean':raise ValueError('Reported reanalysis mean statistic required')
    if any(r[k] is not None for k in ['source_velocity_cutoff_m_s','exact_position','uncertainty_m','annual_range_m','thickness_m','volume_m3','observation_start','observation_end','calendar_month']) or any(r['eligibility'].values()):raise ValueError('No unsupported boundary, date, range, physical or volume promotion')
    if not r['qualification'] or not source['caveats']:raise ValueError('Source qualifications required')
    row={k:None for k in NULLS};row.update({k:False for k in FALSES});row.update(copy.deepcopy(r))
    row.update(approximate_value_m=r['approximate_value'],phase_label='long_term_reanalysis_mean_not_individual_boundary_mean',source_definition='Author-reported approximate600m upper-layer reach in IBI-REA1993-2021mean MA transverse velocity section; exact cutoff unresolved and density-based OMI windows distinct',evidence_kind='source_reported_local_reanalysis_mean_current_extent',source_url=source['source_url'],source_citation=source['source_attribution'],source_locator=source['source_locator'],source_context_id=CONTEXT,source_file=SOURCE,source_sha256=SOURCE_SHA,source_pointer='/rows/0',source_descriptor=copy.deepcopy(r),source_raw_sha256=source['raw_sha256'],source_qualifications=copy.deepcopy(source['caveats']))
    return [row]
def context():
    return {'entity_id':'current:azores','source_file':SOURCE,'source_sha256':SOURCE_SHA,'metric':'reported_reanalysis_mean_current_upper_layer_extent','source_product':'IBI-REA','source_mean_period':[1993,2021],'local_section':'MA north of Madeira','source_direction_consistency':'unresolved_conflicting_primary_labels','omi_boundary_is_fixed_at_reported_extent':False,'exact_velocity_cutoff_established':False,'native_velocity_fields_reconstructed':False,'physical_current_bottom_established':False,'volume_eligible':False}
def assemble(before,addendum,source):
    expected=references(source)
    if addendum['schema']!=SCHEMA or addendum['id']!='azores-ibi-1993-2021-mean-section-depth-v1' or addendum['evidence']!=expected or addendum['source_contexts']!={CONTEXT:context()}:raise ValueError('Exact source semantics and qualifications')
    if any(addendum.get(k) is not False for k in ['runtime_changed','full_goal_complete']):raise ValueError('No runtime or completion promotion')
    out=copy.deepcopy(before);old={r['id'] for r in out['evidence']};known={r['entity_id'] for r in out['records']}
    if CONTEXT in out['source_contexts'] or any(e['id'] in old or e['entity_id'] not in known for e in expected):raise ValueError('Duplicate or unknown owner/context')
    out['evidence'].extend(copy.deepcopy(expected));out['source_contexts'][CONTEXT]=context();compiled.refresh(out);return out
def load_inventory(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v37':raise ValueError('Inventoryv37 required')
    before=previous.load_inventory(json.loads(checked_piece(manifest['previous_inventory'],reader)),reader)
    part=manifest['reference_addendum'];a=json.loads(checked_piece(part['json'],reader))
    if a['source_result']['file']!=SOURCE or a['source_result']['sha256']!=SOURCE_SHA:raise ValueError('Exact derived descriptor packet')
    source=json.loads(checked_piece(a['source_result'],reader));out=assemble(before,a,source)
    table=list(csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode('utf8'))));fields=list(table[0])
    if len(table)!=1 or set(fields)!={k for r in a['evidence'] for k in r} or any(row!={k:cell(e.get(k)) for k in fields} for e,row in zip(a['evidence'],table)):raise ValueError('Full CSV parity')
    compiled.check_counts(out,manifest)
    if any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('No runtime/completion promotion')
    out.update(copy.deepcopy(manifest['view_metadata']));return out
