"""Admit five source-reported spatial Oman plume descriptors without source replay."""
import copy,csv,io,json
import compiled_depth_catalog_view_v2 as previous
import compiled_depth_catalog_view_v1 as compiled
from load_current_depth_reference_inventory_v1 import checked_piece,reference_csv_bytes,cell
SOURCE='research/oman-2025-published-depth-descriptors-v1.json'
SOURCE_SHA='2fbdc8303c4a09e77d3d28597e74d00b013992ef07b050f996a47a4bd6645232'
CONTEXT='oman-2025-pag-main-plume-fraction-030-spatial-descriptors'
SCHEMA='osw.current-depth-oman-published-plume-addendum.v1'
NULLS=['approximate_value_m','range_m','range_interpretation','lower_bound_m','upper_bound_m','upper_boundary_m','lower_boundary_m','thickness_m','uncertainty_m','annual_range_m','calendar_months','observed_period','same_source_width_reference_id']
FALSES=['lower_bound_exclusive','upper_bound_exclusive','whole_current_representative','volume_eligible','physical_state_join_eligible','seasonal_playback_eligible','annual_extrema_eligible','reference_route_projection_eligible','independent_observation_count_claimed','physical_current_bottom_established','independently_validated_axis','direct_physical_current_depth_measurement','physical_depth_ranking_eligible']
def references(source):
    if source['schema']!='osw.oman-2025-published-depth-descriptors.v1' or any(source['eligibility'].values()):raise ValueError('Unpromoted published descriptors required')
    if source['raw_sha256']!='9c81ec9d34f91180f145f607462b5ae6eaa8a457b7ffe77735e35e38eef8f6ad' or source['source_doi']!='10.5194/os-22-3369-2026':raise ValueError('Exact qualified source')
    wanted=[('oman-2025-stable-shelf-plume-top','reported_water_mass_plume_upper_boundary_depth',50,100,'source_reported_regional_spatial_range'),('oman-2025-central-plume-top','reported_water_mass_plume_upper_boundary_depth',None,170,'source_reported_regional_spatial_maximum'),('oman-2025-southern-plume-top','reported_water_mass_plume_upper_boundary_depth',130,140,'source_reported_approximate_regional_spatial_range'),('oman-2025-stable-shelf-plume-thickness','reported_water_mass_plume_thickness',10,30,'source_reported_regional_spatial_range'),('oman-2025-lower-shelf-plume-thickness','reported_water_mass_plume_thickness',None,200,'source_reported_regional_spatial_maximum')]
    if [(r['id'],r['metric'],r['minimum_m'],r['maximum_m'],r['statistic']) for r in source['rows']]!=wanted:raise ValueError('Five exact spatial descriptors required')
    rows=[]
    for i,r in enumerate(source['rows']):
        if r['current_id']!='current:persian-gulf-saline-overflow' or r['selection_fraction']!=0.3 or (r['survey_start'],r['survey_end'])!=('2025-07-09','2025-07-18'):raise ValueError('Owner/selection/survey scope changed')
        if any(r[k] is not None for k in ['value_m','exact_position','lower_boundary_depth_m','uncertainty_m','annual_depth_range','whole_route_depth_m','volume_m3']):raise ValueError('No unsupported boundary/uncertainty/time/volume')
        e={k:None for k in NULLS};e.update({k:False for k in FALSES})
        e.update(id=r['id'],entity_id=r['current_id'],metric=r['metric'],unit='m',
          range_m=[r['minimum_m'],r['maximum_m']] if r['minimum_m'] is not None else None,
          range_interpretation='source_reported_spatial_range_within_single_survey_not_temporal_or_uncertainty' if r['minimum_m'] is not None else None,
          approximate_value_m=r['maximum_m'] if r['minimum_m'] is None else None,
          source_statistic=r['statistic'],source_reported_spatial_minimum_m=r['minimum_m'],source_reported_spatial_maximum_m=r['maximum_m'],
          geographic_scope=r['region'],temporal_scope='Regional hydrographic mapping during9-18July2025; no recurring calendar, annual or seasonal range.',
          phase_label='July2025survey_spatial_descriptor',source_survey_window=[r['survey_start'],r['survey_end']],
          vertical_datum='not_applicable_thickness_distance' if r['metric'].endswith('thickness') else r['vertical_datum'],
          source_definition='Published upper-depth or thickness descriptor of composite-tracer P/AG water fraction>=0.3; core>=0.55 is distinct.',
          evidence_kind='source_reported_regional_hydrographic_plume_spatial_descriptor',source_url=source['source_url'],source_citation=source['source_attribution'],source_locator=r['source_section'],
          source_context_id=CONTEXT,source_file=SOURCE,source_sha256=SOURCE_SHA,source_pointer='/rows/'+str(i),
          source_selection_fraction=0.3,source_distinct_core_fraction=0.55,source_exact_position=None,
          source_descriptor=copy.deepcopy(r),source_caveats=copy.deepcopy(source['caveats']),
          qualification='Spatial descriptors of one hydrographic survey, not paired station boundaries, velocity-defined current extent, seasonal climatology, errors or whole-route thickness. Scalar field for a maximum retains source_statistic; never treat it as typical depth or zero-based range. No bottom from adding unmatched maxima; CTD51/52profile discrepancy unresolved; raw restricted data not inspected.')
        rows.append(e)
    return rows

def context():
    return {'entity_id':'current:persian-gulf-saline-overflow','source_file':SOURCE,'source_sha256':SOURCE_SHA,'survey_window':['2025-07-09','2025-07-18'],'selection_fraction':0.3,'distinct_core_fraction':0.55,'paper_profile_count':51,'restricted_repository_profile_count':52,'profile_count_discrepancy_resolved':False,'raw_CTD_fields_inspected':False,'paired_station_boundaries_established':False,'physical_current_bottom_established':False,'volume_eligible':False}

def assemble(before,addendum,source):
    expected=references(source)
    if addendum['schema']!=SCHEMA or addendum['id']!='oman-2025-published-plume-descriptors-v1' or addendum['evidence']!=expected or addendum['source_contexts']!={CONTEXT:context()}:raise ValueError('Exact source semantics and qualifiers')
    if any(addendum.get(k) is not False for k in ['runtime_changed','full_goal_complete']):raise ValueError('No runtime/goal promotion')
    out=copy.deepcopy(before)
    old={r['id'] for r in out['evidence']};known={r['entity_id'] for r in out['records']}
    if CONTEXT in out['source_contexts'] or any(e['id'] in old or e['entity_id'] not in known for e in expected):raise ValueError('No duplicate or unknown owner/context')
    out['evidence'].extend(copy.deepcopy(expected));out['source_contexts'][CONTEXT]=context()
    compiled.refresh(out)
    return out

def load_inventory(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v34':raise ValueError('Inventoryv34 required')
    before=previous.load_inventory(json.loads(checked_piece(manifest['previous_inventory'],reader)),reader)
    part=manifest['reference_addendum'];a=json.loads(checked_piece(part['json'],reader))
    if a['source_result']['file']!=SOURCE or a['source_result']['sha256']!=SOURCE_SHA:raise ValueError('Exact already-derived descriptor packet')
    source=json.loads(checked_piece(a['source_result'],reader));out=assemble(before,a,source)
    raw=checked_piece(part['csv'],reader);table=list(csv.DictReader(io.StringIO(raw.decode('utf8'))));fields=list(table[0])
    if len(table)!=5 or set(fields)!={k for r in a['evidence'] for k in r} or any(row!={k:cell(e.get(k)) for k in fields} for e,row in zip(a['evidence'],table)):raise ValueError('Full CSV parity')
    compiled.check_counts(out,manifest)
    if any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('No runtime/completion promotion')
    out.update(copy.deepcopy(manifest['view_metadata']));return out
