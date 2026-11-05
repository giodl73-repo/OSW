"""Admit two reported Hanish mean-flow interfaces without physical-depth promotion."""
import copy,csv,io,json
import load_current_depth_reference_inventory_v34 as previous
import compiled_depth_catalog_view_v1 as compiled
from load_current_depth_reference_inventory_v1 import checked_piece,reference_csv_bytes,cell
SOURCE='research/pratt2000-hanish-reported-mean-interface-depths-v1.json'
SOURCE_SHA='864dec7100bca011199ebc37b3a94b56c01548c05a27a258a060c4d1941a52e6'
CONTEXT='red-sea-pratt2000-hanish-mean-velocity-interface'
SCHEMA='osw.current-depth-pratt2000-mean-interface-addendum.v1'
NULLS=['approximate_value_m','range_m','range_interpretation','lower_bound_m','upper_bound_m','upper_boundary_m','lower_boundary_m','thickness_m','uncertainty_m','annual_range_m','calendar_months','observed_period','same_source_width_reference_id']
FALSES=['lower_bound_exclusive','upper_bound_exclusive','whole_current_representative','volume_eligible','physical_state_join_eligible','seasonal_playback_eligible','annual_extrema_eligible','reference_route_projection_eligible','independent_observation_count_claimed','physical_current_bottom_established','independently_validated_axis','direct_physical_current_depth_measurement','physical_depth_ranking_eligible']
def references(source):
    if source['schema']!='osw.pratt2000-hanish-reported-mean-interfaces.v1' or any(source[k] is not False for k in ['runtime_changed','full_goal_complete']) or source['new_canonical_references']!=0:raise ValueError('Qualified source descriptor stage required')
    if source['source_pdf_sha256']!='611f73d277dd068c38157f0873ac532328c029b5bac8714bd9f88d1c0d094c7d':raise ValueError('Exact original paper custody')
    expected=[('red-sea-pratt2000-hanish-winter-mean-interface','winter',35),('red-sea-pratt2000-hanish-summer-mean-interface','summer',110)]
    if [(r['id'],r['source_season_label'],r['approximate_value_m']) for r in source['rows']]!=expected:raise ValueError('Exact two reported endpoints')
    rows=[]
    for i,r in enumerate(source['rows']):
        if r['entity_id']!='current:red-sea-saline-overflow' or r['metric']!='reported_monthly_mean_velocity_zero_crossing_interface_depth' or r['source_statistic']!='authors_reported_endpoint_of_monthly_mean_profile_interface_depths':raise ValueError('Owner and mean-interface statistic cannot change')
        if any(r[k] is not None for k in ['physical_current_bottom_m','thickness_m','range_m','annual_range_m','uncertainty_m','calendar_month','paired_lower_boundary_m']):raise ValueError('No unsupported physical/range/calendar fields')
        if any(r[k] is not False for k in ['whole_current_representative','physical_depth_ranking_eligible','seasonal_playback_eligible','reference_route_projection_eligible','volume_eligible']):raise ValueError('Local mean interface is not physical depth or climatology')
        row={k:None for k in NULLS};row.update({k:False for k in FALSES})
        row.update(copy.deepcopy(r))
        row.update(phase_label='authors_'+r['source_season_label']+'_monthly_mean_interface_endpoint',
            source_definition=r['source_boundary_definition'],evidence_kind='source_reported_local_monthly_mean_velocity_interface',
            source_url=source['source_url'],source_citation=source['citation'],source_locator=source['source_locator'],
            source_context_id=CONTEXT,source_file=SOURCE,source_sha256=SOURCE_SHA,source_pointer='/rows/'+str(i),
            source_descriptor=copy.deepcopy(r),source_pdf_sha256=source['source_pdf_sha256'],
            source_exact_position=None,source_quote_custody=source['source_quote_custody'],
            qualification='Reported endpoint of a monthly mean velocity zero-crossing interface at Hanish Sill. Boundary of mean is not mean individual crossings. Authors season labels do not resolve endpoint month or recurring climatology. No physical current bottom, sampling/bed-depth subtraction, thickness, route/state/volume or whole-current ranking.')
        rows.append(row)
    return rows

def context():
    return {'entity_id':'current:red-sea-saline-overflow','source_file':SOURCE,'source_sha256':SOURCE_SHA,
        'metric':'reported_monthly_mean_velocity_zero_crossing_interface_depth','source_profile_context':'April-November1996monthlymeanprofiles; authors winter/summer endpoints; exact endpoint months unresolved',
        'endpoint_months_resolved':False,'monthly_mean_interface_equals_mean_individual_interfaces':False,
        'raw_velocity_fields_inspected':False,'physical_current_bottom_established':False,
        'reported_interface_endpoints_are_annual_extrema':False,'volume_eligible':False}

def assemble(before,addendum,source):
    expected=references(source)
    if addendum['schema']!=SCHEMA or addendum['id']!='pratt2000-hanish-mean-interface-depths-v1' or addendum['evidence']!=expected or addendum['source_contexts']!={CONTEXT:context()}:raise ValueError('Exact source semantics and qualifiers')
    if any(addendum.get(k) is not False for k in ['runtime_changed','full_goal_complete']):raise ValueError('No runtime/goal promotion')
    out=copy.deepcopy(before)
    old={r['id'] for r in out['evidence']};known={r['entity_id'] for r in out['records']}
    if CONTEXT in out['source_contexts'] or any(e['id'] in old or e['entity_id'] not in known for e in expected):raise ValueError('No duplicate or unknown owner/context')
    out['evidence'].extend(copy.deepcopy(expected));out['source_contexts'][CONTEXT]=context()
    compiled.refresh(out)
    return out

def load_inventory(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v35':raise ValueError('Inventoryv35 required')
    before=previous.load_inventory(json.loads(checked_piece(manifest['previous_inventory'],reader)),reader)
    part=manifest['reference_addendum'];a=json.loads(checked_piece(part['json'],reader))
    if a['source_result']['file']!=SOURCE or a['source_result']['sha256']!=SOURCE_SHA:raise ValueError('Exact already-derived descriptor packet')
    source=json.loads(checked_piece(a['source_result'],reader));out=assemble(before,a,source)
    raw=checked_piece(part['csv'],reader);table=list(csv.DictReader(io.StringIO(raw.decode('utf8'))));fields=list(table[0])
    if len(table)!=2 or set(fields)!={k for r in a['evidence'] for k in r} or any(row!={k:cell(e.get(k)) for k in fields} for e,row in zip(a['evidence'],table)):raise ValueError('Full CSV parity')
    compiled.check_counts(out,manifest)
    if any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('No runtime/completion promotion')
    out.update(copy.deepcopy(manifest['view_metadata']));return out
