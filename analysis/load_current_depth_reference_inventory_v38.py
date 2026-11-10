"""Add one review-reported entering Atlantic-water layer thickness range."""
import copy,csv,io,json
import load_current_depth_reference_inventory_v37 as previous
import compiled_depth_catalog_view_v1 as compiled
from load_current_depth_reference_inventory_v1 import checked_piece,reference_csv_bytes,cell
SOURCE='research/norwegian-rudels2026-aw-layer-descriptors-v1.json'
SOURCE_SHA='584b4adbaf9867104e691d9f3d8a562c324f6e5b16deeb3d01bce8636c60264f'
CONTEXT='norwegian-rudels2026-entering-aw-layer-thickness'
SCHEMA='osw.current-depth-norwegian-aw-layer-addendum.v1'
NULLS=previous.NULLS
FALSES=previous.FALSES
def references(source):
    if source['schema']!='osw.norwegian-rudels2026-aw-layer-descriptors.v1' or source['canonical_reference_admitted'] is not False:raise ValueError('Qualified source stage required')
    if source['raw_sha256']!='97e66a9b773f77af0dd0194e9577adf8db88e9abb138274bce276614f4bde8b4' or source['source_doi']!='10.5194/os-22-3287-2026':raise ValueError('Exact primary custody required')
    if len(source['rows'])!=1:raise ValueError('One review layer range only')
    r=source['rows'][0]
    if (r['id'],r['entity_id'],r['metric'],r['unit'])!=('norwegian-rudels-carmack2026-entering-atlantic-water-layer-thickness','current:norwegian','reported_advected_atlantic_water_layer_thickness','m'):raise ValueError('Exact parent owner and water-mass thickness metric')
    if r['water_mass_thickness_range_m']!=[300,400] or r['approximate_value'] is not None:raise ValueError('Reported range not a point depth')
    if r['evidence_kind']!='published_review_synthesis' or r['independent_direct_observation'] is not False or r['branch_assignment_performed'] is not False:raise ValueError('Review and parent scope preserved')
    if any(r[k] is not None for k in ['calendar_month','observation_start','observation_end','annual_range_m','uncertainty_m','upper_boundary_m','lower_boundary_m','thickness_m','volume_m3']) or any(r['eligibility'].values()):raise ValueError('No physical boundary, seasonal or volume promotion')
    if not r['qualification'] or not source['caveats']:raise ValueError('Source qualifications required')
    row={k:None for k in NULLS};row.update({k:False for k in FALSES});row.update(copy.deepcopy(r))
    row.update(range_m=copy.deepcopy(r['water_mass_thickness_range_m']),phase_label='undated_review_description_not_seasonal_or_observed_profile',source_definition='Review-reported300-400m thickness of Atlantic-water layer entering Norwegian Sea; no current top/bottom pair or physical current thickness',source_metric_role='advected_water_mass_layer_not_current_depth_below_surface',source_url=source['source_url'],source_citation=source['source_attribution'],source_locator=source['source_locator'],source_context_id=CONTEXT,source_file=SOURCE,source_sha256=SOURCE_SHA,source_pointer='/rows/0',source_descriptor=copy.deepcopy(r),source_raw_sha256=source['raw_sha256'],source_qualifications=copy.deepcopy(source['caveats']))
    return [row]
def context():
    return {'entity_id':'current:norwegian','source_file':SOURCE,'source_sha256':SOURCE_SHA,'metric':'reported_advected_atlantic_water_layer_thickness','water_mass':'Atlantic water entering Norwegian Sea','evidence_kind':'published_review_synthesis','observation_date_resolved':False,'parent_context_copied_to_branches':False,'physical_current_bottom_established':False,'physical_current_thickness_established':False,'volume_eligible':False}
def assemble(before,addendum,source):
    expected=references(source)
    if addendum['schema']!=SCHEMA or addendum['id']!='norwegian-rudels2026-entering-aw-layer-thickness-v1' or addendum['evidence']!=expected or addendum['source_contexts']!={CONTEXT:context()}:raise ValueError('Exact source semantics and qualifications')
    if any(addendum.get(k) is not False for k in ['runtime_changed','full_goal_complete']):raise ValueError('No runtime or completion promotion')
    out=copy.deepcopy(before);old={r['id'] for r in out['evidence']};known={r['entity_id'] for r in out['records']}
    if CONTEXT in out['source_contexts'] or any(e['id'] in old or e['entity_id'] not in known for e in expected):raise ValueError('Duplicate or unknown owner/context')
    out['evidence'].extend(copy.deepcopy(expected));out['source_contexts'][CONTEXT]=context();compiled.refresh(out);return out
def load_inventory(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v38':raise ValueError('Inventoryv38 required')
    before=previous.load_inventory(json.loads(checked_piece(manifest['previous_inventory'],reader)),reader)
    part=manifest['reference_addendum'];a=json.loads(checked_piece(part['json'],reader))
    if a['source_result']['file']!=SOURCE or a['source_result']['sha256']!=SOURCE_SHA:raise ValueError('Exact derived descriptor packet')
    source=json.loads(checked_piece(a['source_result'],reader));out=assemble(before,a,source)
    table=list(csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode('utf8'))));fields=list(table[0])
    if len(table)!=1 or set(fields)!={k for r in a['evidence'] for k in r} or any(row!={k:cell(e.get(k)) for k in fields} for e,row in zip(a['evidence'],table)):raise ValueError('Full CSV parity')
    compiled.check_counts(out,manifest)
    if any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('No runtime/completion promotion')
    out.update(copy.deepcopy(manifest['view_metadata']));return out
