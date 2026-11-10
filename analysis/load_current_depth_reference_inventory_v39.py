"""Admit interior censored model-component support, never resolved contours."""
import copy,csv,io,json,math
import load_current_depth_reference_inventory_v38 as previous
import compiled_depth_catalog_view_v1 as compiled
from load_current_depth_reference_inventory_v1 import checked_piece,reference_csv_bytes,cell
SOURCE='research/norkyst-jutland-dated-depth-anchors-v1.json'
SOURCE_SHA='ec85c2f4e778c44116eaeec4f344df237a7f96dfee8fd91615560045df950365'
CONTEXT='jutland-norkyst2024-interior-censored-component-support'
SCHEMA='osw.current-depth-jutland-model-support-addendum.v1'
ADDENDUM_ID='jutland-norkyst2024-interior-censored-support-v1'
NULLS=previous.NULLS
FALSES=previous.FALSES

def qualified(source):
    if source.get('schema')!='osw.norkyst-jutland-dated-regional-depth-anchors.v1' or source.get('entity_id')!='current:jutland':raise ValueError('Exact derived Jutland source packet required')
    rows=source['rows']
    if len(rows)!=12 or len({r['case_index'] for r in rows})!=12:raise ValueError('All twelve unique source cases required')
    dates={'2024-03-15','2024-06-15','2024-09-15','2024-12-15'}
    sections={'hanstholm-search-cut','north-jutland-midcoast-search-cut','hirtshals-search-cut'}
    if {(r['date'],r['section_id']) for r in rows}!={(d,s) for d in dates for s in sections} or any(r['time_utc']!=r['date']+'T12:00:00Z' for r in rows):raise ValueError('Exact twelve original section/noon snapshot pairs required')
    selected=[];excluded=[]
    for i,r in enumerate(rows):
        layer=r['primary_component_layer'];bound=r['primary_connected_depth_lower_bound_m']
        if r['entity_id']!='current:jutland' or r['component_bearing_degrees_true']!=45 or r['primary_threshold_m_s']!=.1 or r['selection_interval_m']!=[0,25]:raise ValueError('Original owner, component, threshold and selection window cannot change')
        if r['source_vertical_sampling']!='provider_interpolated_fixed_z_not_native_ROMS_s_layers' or r['salinity_gate_applied'] is not False or r['physical_current_identity_independently_verified'] is not False:raise ValueError('Preserve conditional fixed-z model source class')
        if layer['threshold_m_s']!=.1 or layer['lower_status']!='censored_before_missing_or_dry_level' or layer['lower_depth_m'] is not None or layer['layer_thickness_m'] is not None or r['primary_lower_component_contour_depth_m'] is not None or r['conditional_component_span_m'] is not None:raise ValueError('Unresolved lower contour and thickness must stay null')
        if r['regional_axis_proxy_lower_contour_anchor_eligible'] is not False or r['physical_current_bottom_established'] is not False or any(r[k] is not None for k in ['physical_thickness_m','volume_m3','annual_range_m']) or any(r[k] is not False for k in ['whole_current_representative','width_join_eligible','volume_eligible']):raise ValueError('No contour, physical or geometry promotion')
        if type(bound) not in (int,float) or not math.isfinite(bound) or bound<=0 or bound!=layer['lower_last_connected_depth_m'] or layer['core_velocity_m_s']<.1:raise ValueError('Positive retained connected sampling support required')
        if r['horizontal_axis_proxy_interior'] is True:
            if r['horizontal_selection_status']!='interior_section_integral_maximum_with_finite_neighbors_not_independently_validated_axis' or bound not in [25,50,65]:raise ValueError('Exact interior support class required')
            selected.append((i,r))
        elif r['horizontal_axis_proxy_interior'] is False and r['horizontal_selection_status']=='section_gate_edge_maximum_axis_unresolved':excluded.append((i,r))
        else:raise ValueError('Unknown horizontal qualification')
    if len(selected)!=11 or len(excluded)!=1:raise ValueError('Eleven interior bounds and one unresolved edge required')
    return selected,excluded

def references(source):
    selected,_=qualified(source);result=[]
    for i,r in selected:
        row={k:None for k in NULLS};row.update({k:False for k in FALSES})
        row.update(id=f"jutland-norkyst2024-c{r['case_index']:02d}-component45-support-bound",entity_id='current:jutland',
            metric='derived_supported_component_penetration_lower_bound',unit='m',lower_bound_m=r['primary_connected_depth_lower_bound_m'],lower_bound_exclusive=False,
            vertical_datum='retained_model_fixed_z_positive_depth_datum_not_independently_reverified',
            phase_label='model_snapshot_'+r['time_utc'],model_snapshot_time_utc=r['time_utc'],
            geographic_scope='Selected northern Jutland-region model column at '+r['section_id']+'; not the full named-current route.',
            temporal_scope='One dated NorKyst noon snapshot; four2024 probes do not establish a seasonal envelope.',
            evidence_kind='model_derived_conditional_directional_component_sampling_support',
            source_definition='Inclusive deepest connected sampled fixed-z level supporting the selected45degree component at0.1m/s; deeper extent unresolved.',
            source_url='https://gmd.copernicus.org/articles/19/2785/2026/',source_citation='NorKyst model product; exact retained2024 source cases and validated OSW dated-depth descriptor audit.',
            source_locator='Retained dated-depth anchors, row '+str(i)+'; original case '+str(r['case_index']),
            source_file=SOURCE,source_sha256=SOURCE_SHA,source_pointer='/rows/'+str(i),source_context_id=CONTEXT,
            sampled_position_lon_lat=copy.deepcopy(r['selected_position_lon_lat']),source_case_id=r['case_index'],
            source_descriptor=copy.deepcopy(r),source_raw_file=r['source_raw_file'],source_raw_sha256=r['source_raw_sha256'],
            source_component_bearing_degrees_true=45,primary_threshold_m_s=.1,
            resolved_lower_contour_eligible=False,censored_component_support_reference_eligible=True,
            current_identity_independently_validated=False,physical_current_identity_independently_verified=False,
            qualification='Conditional directional-component model support only. Interior section maximum is not independently validated current identity or axis. Fixed-z sampling is provider interpolation, not native ROMS resolution. Missing/dry deeper levels censor support; no seabed/current bottom, finite contour, thickness, annual range, between-anchor interpolation, width join or volume inferred.')
        result.append(row)
    return result

def context(source):
    _,excluded=qualified(source)
    return {'entity_id':'current:jutland','source_file':SOURCE,'source_sha256':SOURCE_SHA,
        'quantity':'inclusive_conditional_model_component_depth_support_not_lower_boundary',
        'component_bearing_degrees_true':45,'primary_threshold_m_s':.1,'selection_interval_m':[0,25],
        'between_anchor_or_time_interpolation_performed':False,'physical_current_identity_independently_validated':False,
        'resolved_lower_contours_admitted':0,'physical_thicknesses_admitted':0,'new_direct_observations':0,
        'unadmitted_edge_cases':[{'source_pointer':'/rows/'+str(i),'source_descriptor':copy.deepcopy(r),'status':'EDGE_SELECTION_REMAINS_UNRESOLVED_NOT_A_DEPTH_REFERENCE'} for i,r in excluded]}

def assemble(before,addendum,source):
    expected=references(source)
    if addendum['schema']!=SCHEMA or addendum['id']!=ADDENDUM_ID or addendum['evidence']!=expected or addendum['source_contexts']!={CONTEXT:context(source)}:raise ValueError('Exact scoped support references and excluded edge required')
    if any(addendum.get(k) is not False for k in ['runtime_changed','full_goal_complete']):raise ValueError('No runtime/completion promotion')
    out=copy.deepcopy(before);old={r['id'] for r in out['evidence']};known={r['entity_id'] for r in out['records']}
    if CONTEXT in out['source_contexts'] or any(e['id'] in old or e['entity_id'] not in known for e in expected):raise ValueError('Duplicate context/reference or unknown owner')
    out['evidence'].extend(expected);out['source_contexts'][CONTEXT]=context(source);compiled.refresh(out);return out

def load_inventory(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v39':raise ValueError('Inventoryv39 required')
    before=previous.load_inventory(json.loads(checked_piece(manifest['previous_inventory'],reader)),reader)
    part=manifest['reference_addendum'];a=json.loads(checked_piece(part['json'],reader))
    if a['source_result']['file']!=SOURCE or a['source_result']['sha256']!=SOURCE_SHA:raise ValueError('Exact already-derived source packet required')
    source=json.loads(checked_piece(a['source_result'],reader));out=assemble(before,a,source)
    rows=list(csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode('utf8'))));fields=list(rows[0])
    if len(rows)!=11 or set(fields)!={k for r in a['evidence'] for k in r} or any(row!={k:cell(e.get(k)) for k in fields} for e,row in zip(a['evidence'],rows)):raise ValueError('Complete11-row CSV/JSON parity required')
    compiled.check_counts(out,manifest)
    if any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('No runtime/completion promotion')
    out.update(copy.deepcopy(manifest['view_metadata']));return out
