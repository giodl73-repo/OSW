"""Admit regional Gulf Stream fitted descriptors from frozen section profiles."""
import copy
import csv
import hashlib
import io
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'research/current-depth-source-facts-v48.json'
RULES = 'research/current-depth-rules-v48.json'
OUTPUT = 'research/current-depth-register-v48.json'
CSV = 'research/current-depth-register-v48.csv'
MEMBER_OUTPUT = 'research/current-depth-member-index-v7.json'
GENERATOR = 'analysis/build_current_depth_register_v48.py'
SOURCE_CONTEXT_ID = 'gulf-stream-spray-2023-five-sections'
SOURCE_CONTEXT = {
    'source_url':'https://spraydata.ucsd.edu/products/gulf-stream-climatology/',
    'source_citation':'Todd and Ren(2023), doi:10.21238/S8TC9W; author correction doi:10.1038/s41558-024-02009-y.',
    'temporal_scope':'Published2015-07-16 through2023-05-30 fitted mean/two-harmonic annual cycle; phase coordinates are not instantaneous observations or monthly means.',
    'geographic_scope':'Five regional Gulf Stream fitted sections; selected mapped columns are not independently validated current axes.',
    'qualification':'Mapped regional fitted component descriptor, not whole-current depth, physical thickness, annual extrema or independent occupation. Unsampled upper10m, missing/deep support and locked reference frame retained.',
    'source_horizontal_axis_operator':'maximum_complete_signed10_to200m_trapezoidal_component_integral_with_regional_direction_sector_and_first_grid_tie',
    'resolution':'Each new reference source_context_id resolves to this register source_contexts entry. Per-profile files, pointers, SHA256, sections, coordinates, locked directions, phase labels, thresholds, native brackets and numerical values remain on the reference.'
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reference_rows(fact, raw, section, profile_sha):
    """Keep core, censored reach, relative contour and absolute contours distinct."""
    profile = raw['selected_profile']
    primary = profile['absolute_component_threshold_layers'][0]
    half = profile['half_sampled_core_component_decay']
    month = raw['calendar_month_phase']
    tag = 'mean' if month is None else f'phase-{month:02d}'
    case = 'gulf-stream-spray-2023-' + section['id'] + '-' + tag
    common = {
        'entity_id': 'current:gulf-stream', 'range_m': None, 'lower_bound_m': None,
        'lower_bound_exclusive': False, 'upper_bound_m': None, 'upper_bound_exclusive': False,
        'range_interpretation': None, 'unit': 'm', 'vertical_datum': 'local_sea_surface_positive_down',
        'upper_boundary_m': None, 'lower_boundary_m': None, 'thickness_m': None,
        'uncertainty_m': None, 'annual_range_m': None,
        'phase_label': 'fitted time mean' if month is None else f'fitted annual-cycle phase {month:02d}-15',
        'calendar_months': None if month is None else [month],
        'calendar_source_locator': None if month is None else 'Retained nominal phase key, day15; actual provider coordinate retained separately.',
        'source_context_id': SOURCE_CONTEXT_ID,
        'geographic_scope': 'Gulf Stream fitted section ' + section['id'] + '; selected mapped column.',
        'temporal_scope': '2015–2023 fitted climatology; see shared source context.',
        'evidence_kind': 'derived_published_glider_climatology',
        'source_url': 'https://spraydata.ucsd.edu/products/gulf-stream-climatology/',
        'source_citation': 'Todd and Ren(2023), doi:10.21238/S8TC9W.',
        'source_locator': 'source_profile_file#source_profile_pointer/selected_profile',
        'qualification': 'Regional fitted descriptor only; see shared source context.',
        'observed_period': None, 'source_case_id': case, 'same_source_width_reference_id': None,
        'independent_observation_count_claimed': False, 'whole_current_representative': False,
        'volume_eligible': False, 'physical_state_join_eligible': False, 'seasonal_playback_eligible': False,
        'annual_extrema_eligible': False, 'reference_route_projection_eligible': False,
        'source_profile_file': fact['source_file'], 'source_profile_sha256': profile_sha,
        'source_profile_pointer': fact['source_pointer'], 'source_section_id': section['id'],
        'source_section_definition': section, 'source_selected_lon_lat': profile['source_lon_lat'],
        'source_product_kind': raw['source_product_kind'], 'source_dataset_doi': '10.21238/S8TC9W',
        'source_documented_fit_observation_period': ['2015-07-16','2023-05-30'],
        'source_actual_provider_phase_timestamp_utc': raw['actual_provider_phase_timestamp_utc'],
        'source_nominal_phase_calendar_date': raw['nominal_phase_calendar_date'],
        'source_phase_timestamp_is_observation_date': False, 'source_is_monthly_average': False,
        'source_velocity_quantity': 'signed_component_along_native100m_mean_direction_locked_through_depth',
        'source_locked_reference_direction_at100m_degrees': profile['locked_reference_direction_at100m_degrees'],
        'source_horizontal_selection_status': raw['horizontal_selection_status'],
        'source_core_search_depth_interval_m': [10,200],
        'source_sampled_core_depth_m': primary['core_depth_m'],
        'source_sampled_core_at_shallowest_valid_level': primary['core_depth_m'] == 10,
        'source_shallowest_fitted_depth_m': 10, 'source_native_fitted_depth_spacing_m': 10,
        'source_product_deep_limit_m': 1000, 'source_product_limit_is_current_bottom': False,
        'source_fit_support_pointer': fact['source_pointer'] + '/selected_profile/source_fit_support',
        'source_component_uncertainty_is_depth_error': False,
        'source_native_grid_is_independent_observation_spacing': False,
        'source_relative_core_fraction': None, 'source_velocity_threshold_m_s': None,
        'source_native_bracketing_depths_m': None, 'source_depth_interpolation': None,
    }
    definitions = [('core','core_depth',primary['core_depth_m'],None,primary)]
    if primary['lower_depth_m'] is None and primary.get('lower_last_connected_depth_m') is not None:
        definitions.append(('reach-5cms','derived_supported_component_penetration_lower_bound',primary['lower_last_connected_depth_m'],.05,primary))
    if half and half['lower_depth_m'] is not None:
        definitions.append(('half-core','derived_relative_core_component_decay_depth',half['lower_depth_m'],half['threshold_m_s'],half))
    for layer in profile['absolute_component_threshold_layers']:
        if layer['lower_depth_m'] is not None:
            definitions.append((f"lower-{int(round(layer['threshold_m_s']*100))}cms",'derived_fitted_locked_component_isotach_depth',layer['lower_depth_m'],layer['threshold_m_s'],layer))
    rows = []
    for kind, metric, value, threshold, layer in definitions:
        row = copy.deepcopy(common)
        row.update(id=case+'-'+kind, metric=metric, approximate_value_m=value if kind=='core' else int(10*round(value/10)),
                   source_computed_depth_before_display_rounding_m=value, source_velocity_threshold_m_s=threshold,
                   source_lower_boundary_status=layer['lower_status'], source_metric_role=kind)
        if kind == 'core':
            row['source_definition'] = 'Native sampled maximum qualifying signed component within10–200m; first grid depth breaks ties. A shallow-edge maximum does not resolve the unsampled surface core.'
        elif kind == 'reach-5cms':
            row.update(approximate_value_m=None,lower_bound_m=value,lower_bound_operator='>=')
            row['source_definition'] = 'Deepest contiguous supported native level above5cm/s below the sampled upper200m core; inclusive minimum penetration, not a detected lower boundary.'
        else:
            row['source_native_bracketing_depths_m'] = layer['lower_bracket_m']
            row['source_depth_interpolation'] = 'linear_between_adjacent_finite_native_fitted_levels'
            row['source_definition'] = ('First descending half-core component crossing connected to the qualifying sampled10–200m core, depth below sea surface.' if kind=='half-core' else 'First descending absolute signed-component isotach connected to the qualifying sampled10–200m core; depth below sea surface, not physical thickness.')
            if kind == 'half-core':row['source_relative_core_fraction'] = .5
        rows.append(row)
    return rows


def source_references(op, root=ROOT):
    facts = json.loads((root/op['section_facts_file']).read_bytes())
    chunks = {f:json.loads((root/f).read_bytes()) for f in op['section_files']}
    seen=set();refs=[]
    for fact in facts['descriptors']:
        f=fact['source_file']
        if f not in chunks or fact['source_sha256']!=op['input_sha256'][f]:raise ValueError('Source section/hash changed')
        chunk=chunks[f];index=int(fact['source_pointer'].split('/')[-1]);raw=chunk['records'][index]
        if chunk['entity_context']!='current:gulf-stream' or fact['source_pointer']!='/records/'+str(index):raise ValueError('Source identity/pointer changed')
        key=raw['section_id'],raw['source_product_kind'],raw['calendar_month_phase']
        if key in seen:raise ValueError('Duplicate source section phase')
        seen.add(key)
        for k in ['section_id','source_product_kind','calendar_month_phase','actual_provider_phase_timestamp_utc','nominal_phase_calendar_date','horizontal_selection_status']:
            if fact[k]!=raw[k]:raise ValueError('Source phase context changed')
        selected=raw['selected_profile']
        if fact['selected_lon_lat']!=selected['source_lon_lat'] or fact['half_sampled_core_component_decay']!=selected['half_sampled_core_component_decay']:raise ValueError('Source descriptor changed')
        rows=reference_rows(fact,raw,chunk['section_definition'],op['input_sha256'][f])
        for row in rows:
            row.update(source_file=op['section_facts_file'],source_pointer='/descriptors/'+str(len(seen)-1),source_sha256=op['input_sha256'][op['section_facts_file']])
        refs.extend(rows)
    expected={(s,k,m) for s in op['section_ids'] for k,m in [('mean',None)]+[('annual_cycle',m) for m in range(1,13)]}
    if seen!=expected:raise ValueError('All prescribed five sections and thirteen phases required')
    if len(refs)!=210 or Counter(r['metric'] for r in refs)!=Counter({'core_depth':65,'derived_supported_component_penetration_lower_bound':65,'derived_relative_core_component_decay_depth':65,'derived_fitted_locked_component_isotach_depth':15}):raise ValueError('Frozen admission counts changed')
    return refs


def validate_context(row, expected):
    if row!=expected.get(row['id']):raise ValueError('Source-derived reference context changed')


def build(root=ROOT):
    read=lambda p:json.loads((root/p).read_bytes())
    op=read(SOURCE)
    for f,pin in op['input_sha256'].items():
        if digest(root/f)!=pin:raise ValueError('Frozen admission input changed: '+f)
    prior=read(op['previous_register_file']);refs=source_references(op,root)
    rules=read(RULES)
    if any(r['metric'] not in rules['metric_types'] for r in refs):raise ValueError('Unregistered depth metric')
    evidence=copy.deepcopy(prior['evidence']);seen={r['id'] for r in evidence}
    for i,row in enumerate(refs):
        if row['id'] in seen:raise ValueError('Duplicate reference id')
        seen.add(row['id']);evidence.append(row)
    records=copy.deepcopy(prior['records'])
    for row in records:
        row['depth_reference_ids']=[r['id'] for r in evidence if r['entity_id']==row['entity_id']]
        row['status']='scoped_depth_reference' if row['depth_reference_ids'] else 'not_yet_assessed'
    owners=sum(bool(r['depth_reference_ids']) for r in records)
    pins=dict(op['input_sha256'],**{SOURCE:digest(root/SOURCE),RULES:digest(root/RULES)})
    return {'schema':'osw.current-depth-register.v48','status':'GULF_STREAM65_CORE65_REACH65_RELATIVE_AND15_ABSOLUTE_CONTOURS',
            'rules_file':RULES,'generator_file':GENERATOR,'generator_sha256':digest(root/GENERATOR),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:491]==prior['evidence'],
            'counts':{'identities':len(records),'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,'identities_not_yet_assessed':len(records)-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Gulf Stream adds210 descriptors across65 shared fitted profiles at five regional sections. Censored5cm/s reach, upper-layer sampled core, half-core decay and15 resolved absolute contours remain separate. No full-current physical thickness or volume established.',
            'metadata_correction_file':prior.get('metadata_correction_file'),'metadata_correction_count':prior.get('metadata_correction_count',0),
            'source_definition_clarification':op['source_definition_clarification'],
            'source_contexts':{SOURCE_CONTEXT_ID:copy.deepcopy(SOURCE_CONTEXT)},
            'member_depth_index_file':MEMBER_OUTPUT,'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document, root=ROOT):
    op=json.loads((root/SOURCE).read_bytes())
    reader=csv.DictReader(io.StringIO((root/op['previous_csv_file']).read_text(encoding='utf8')))
    columns=list(reader.fieldnames);rows=list(reader)
    for raw in document['evidence'][491:]:
        for k in raw:
            if k not in columns:columns.append(k)
        row=copy.deepcopy(raw)
        for k,v in row.items():
            if isinstance(v,(list,dict)):row[k]=json.dumps(v,ensure_ascii=False,separators=(',',':'))
        rows.append(row)
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n')
    writer.writeheader();writer.writerows(rows)
    return out.getvalue().encode('utf8')


def json_bytes(document):
    # Compact serialization preserves all source values while honoring fixed per-file publication caps.
    return (json.dumps(document,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode('utf8')


def member_index(document, register_bytes, root=ROOT):
    op=json.loads((root/SOURCE).read_bytes())
    old=json.loads((root/op['previous_member_index_file']).read_bytes())
    result=copy.deepcopy(old);entities={r['entity_id']:r for r in document['records']}
    refs=set()
    for row in result['records']:
        linked=set();missing=[]
        for member in row['members']:
            member['depth_reference_ids']=entities[member['entity_id']]['depth_reference_ids'][:]
            member['status']='scoped_member_references' if member['depth_reference_ids'] else 'no_member_depth_reference'
            linked.update(member['depth_reference_ids'])
            if not member['depth_reference_ids']:missing.append(member['entity_id'])
        row['unique_linked_reference_ids']=sorted(linked);row['linked_reference_count']=len(linked)
        row['missing_member_depth_entity_ids']=missing;refs.update(linked)
    result.update(schema='osw.current-depth-member-index.v7',depth_register_file=OUTPUT,depth_register_sha256=hashlib.sha256(register_bytes).hexdigest())
    result['counts']['distinct_member_depth_references']=len(refs)
    result['counts']['parents_with_any_member_depth_evidence']=sum(bool(r['linked_reference_count']) for r in result['records'])
    result['counts']['parents_with_all_declared_members_referenced']=sum(not r['missing_member_depth_entity_ids'] for r in result['records'])
    return result


def main():
    result=build();raw=json_bytes(result)
    if len(raw)>=2500000:raise ValueError('Fixed per-file publication cap exceeded; do not raise it')
    out=Path('current-depth-register-v48');out.mkdir(exist_ok=True)
    (out/'register.json').write_bytes(raw);(out/'register.csv').write_bytes(csv_bytes(result))
    (out/'member-index.json').write_text(json.dumps(member_index(result,raw),indent=2)+'\n',encoding='utf8')
    print(json.dumps(result['counts']))


if __name__=='__main__':main()
