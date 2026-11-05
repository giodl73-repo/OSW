"""Add one dated local Toulon depth from its retained descriptor, no source replay."""
import copy,csv,io,json
import load_current_depth_reference_inventory_v35 as previous
import compiled_depth_catalog_view_v1 as compiled
from load_current_depth_reference_inventory_v1 import checked_piece,reference_csv_bytes,cell
SOURCE='research/northern-toulon-2011-depth-descriptors-v1.json'
SOURCE_SHA='c795a8db6cc5a38989490399bac499b688bc61f9d975022d36076ce012c3c73c'
CONTEXT='northern-mediterranean-toulon-2011-transect1-geostrophic-depth'
SCHEMA='osw.current-depth-northern-toulon-dated-local-addendum.v1'
NULLS=previous.NULLS
FALSES=previous.FALSES
def references(source):
    if source['schema']!='osw.northern-toulon-2011-depth-descriptors.v1' or source['canonical_reference_admitted'] is not False:raise ValueError('Qualified source stage required')
    if source['raw_sha256']!='cd14be6aaaefaa257b862db93e97f603828c898145841b65e90a60e47f95b526' or source['source_doi']!='10.5194/os-14-689-2018':raise ValueError('Exact primary custody required')
    if len(source['rows'])!=1:raise ValueError('One local reported result only')
    r=source['rows'][0]
    if (r['id'],r['entity_id'],r['metric'],r['approximate_value'],r['unit'])!=('northern-mediterranean-berta2018-toulon-t1-20111202-04-reported-depth','current:northern-mediterranean','reported_local_geostrophic_current_lower_extent',175,'m'):raise ValueError('Exact local result and owner required')
    if (r['observation_start'],r['observation_end'],r['calendar_month'],r['hydrographic_regime'])!=('2011-12-02','2011-12-04',12,'source_described_persistent_late_summer_conditions'):raise ValueError('December date distinct from persistent late-summer conditions')
    if r['source_statistic']!='author_reported_approximate_transect_extent' or r['velocity_component']!='zonal_geostrophic_from_glider_hydrography':raise ValueError('Reported geostrophic statistic required')
    if any(r[k] is not None for k in ['source_velocity_cutoff_m_s','exact_position','uncertainty_m','annual_range_m','thickness_m','volume_m3']) or any(r['eligibility'].values()):raise ValueError('No borrowed boundary, envelope, physical or volume promotion')
    if not r['qualification'] or not source['caveats']:raise ValueError('Source qualifications required')
    row={k:None for k in NULLS};row.update({k:False for k in FALSES});row.update(copy.deepcopy(r))
    row.update(approximate_value_m=r['approximate_value'],phase_label='dated_local_transect_not_recurring_season',source_definition='Author-reported approximate local NC depth in zonal geostrophic velocity discussion; exact cutoff unresolved',evidence_kind='source_reported_dated_local_geostrophic_current_extent',source_url=source['source_url'],source_citation=source['source_attribution'],source_locator=source['source_locator'],source_context_id=CONTEXT,source_file=SOURCE,source_sha256=SOURCE_SHA,source_pointer='/rows/0',source_descriptor=copy.deepcopy(r),source_raw_sha256=source['raw_sha256'],source_qualifications=copy.deepcopy(source['caveats']))
    return [row]
def context():
    return {'entity_id':'current:northern-mediterranean','source_file':SOURCE,'source_sha256':SOURCE_SHA,'metric':'reported_local_geostrophic_current_lower_extent','observation_start':'2011-12-02','observation_end':'2011-12-04','local_section':'Toulon glider Transect1','calendar_month':12,'hydrographic_regime':'persistent_late_summer_conditions','exact_velocity_cutoff_established':False,'native_velocity_fields_reconstructed':False,'physical_current_bottom_established':False,'volume_eligible':False}
def assemble(before,addendum,source):
    expected=references(source)
    if addendum['schema']!=SCHEMA or addendum['id']!='northern-toulon-2011-dated-local-depth-v1' or addendum['evidence']!=expected or addendum['source_contexts']!={CONTEXT:context()}:raise ValueError('Exact source semantics and qualifications')
    if any(addendum.get(k) is not False for k in ['runtime_changed','full_goal_complete']):raise ValueError('No runtime or completion promotion')
    out=copy.deepcopy(before);old={r['id'] for r in out['evidence']};known={r['entity_id'] for r in out['records']}
    if CONTEXT in out['source_contexts'] or any(e['id'] in old or e['entity_id'] not in known for e in expected):raise ValueError('Duplicate or unknown owner/context')
    out['evidence'].extend(copy.deepcopy(expected));out['source_contexts'][CONTEXT]=context();compiled.refresh(out);return out
def load_inventory(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v36':raise ValueError('Inventoryv36 required')
    before=previous.load_inventory(json.loads(checked_piece(manifest['previous_inventory'],reader)),reader)
    part=manifest['reference_addendum'];a=json.loads(checked_piece(part['json'],reader))
    if a['source_result']['file']!=SOURCE or a['source_result']['sha256']!=SOURCE_SHA:raise ValueError('Exact derived descriptor packet')
    source=json.loads(checked_piece(a['source_result'],reader));out=assemble(before,a,source)
    table=list(csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode('utf8'))));fields=list(table[0])
    if len(table)!=1 or set(fields)!={k for r in a['evidence'] for k in r} or any(row!={k:cell(e.get(k)) for k in fields} for e,row in zip(a['evidence'],table)):raise ValueError('Full CSV parity')
    compiled.check_counts(out,manifest)
    if any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('No runtime/completion promotion')
    out.update(copy.deepcopy(manifest['view_metadata']));return out
