"""Append source Bjornoya mean-core depth and paired area."""
import csv, hashlib, io, json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v38 as previous
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v39.json'
RULES='research/current-depth-rules-v39.json'
OUTPUT='research/current-depth-register-v39.json'
CSV='research/current-depth-register-v39.csv'
MEMBER_OUTPUT='research/current-depth-member-index-v6.json'
MEMBERS='research/current-length-family-conventions-v1.json'
validate_reference=previous.validate_reference
EXPECTED_REFERENCES = {'nwasc-baumann-2026-bjornoya-core-bottom': {'id': 'nwasc-baumann-2026-bjornoya-core-bottom', 'entity_id': 'current:norwegian-atlantic-slope', 'metric': 'core_lower_boundary_depth', 'approximate_value_m': 580, 'range_m': None, 'lower_bound_m': None, 'lower_bound_exclusive': False, 'upper_bound_m': None, 'upper_bound_exclusive': False, 'range_interpretation': None, 'unit': 'm', 'vertical_datum': 'local_sea_surface_positive_down', 'upper_boundary_m': None, 'lower_boundary_m': None, 'thickness_m': None, 'uncertainty_m': None, 'annual_range_m': None, 'phase_label': None, 'calendar_months': None, 'geographic_scope': 'Bjørnøya hydrographic section in the source’s broad high-latitude NwASC continuation. No point longitude or exact core-axis position assigned.', 'temporal_scope': '1993–2022 hydrographic/altimetry mean;53 unevenly sampled Bjørnøya transects, with seasonal bias. Static mean mask, not an instantaneous or quarterly depth series.', 'source_definition': 'Approximate maximum depth of the Atlantic-Water core selected by descending absolute geostrophic velocity until50% of section mean transport is represented.', 'evidence_kind': 'published_hydrographic_mean_core', 'source_url': 'https://os.copernicus.org/articles/22/17/2026/', 'source_citation': 'Baumann et al.(2026), Reduced cooling in the Norwegian Atlantic Slope Current, Ocean Science22:17–29, doi:10.5194/os-22-17-2026.', 'source_locator': 'Section2.1.2 final spatial-extent paragraph and original Figure3d, printed21/PDF5; Section2.1 sampling; Section2.3 source core areas.', 'qualification': 'Maximum static mask depth is not a full-current bottom or uniform thickness.50m is an imposed surface exclusion. Do not inherit Svinøy1500m or Gimsøy2500m lateral cutoff at Bjørnøya; no numerical Bjørnøya isobath cutoff is established. Source mean-mask cell areas slightly overestimate geometric area by ignoring topographic cell cuts. Quarterly interpolation oversamples the sparse section and supplies no seasonal mask-depth data. Source broad NwASC geography may overlap names used for West Spitsbergen flow; no independent duplicate component volume or identity inheritance. BSO uses a different salinity ranking and remains excluded from velocity-ranked core pairing.', 'observed_period': None, 'source_case_id': 'nwasc-baumann-2026-bjornoya-mean-mask', 'same_source_width_reference_id': None, 'independent_observation_count_claimed': False, 'whole_current_representative': False, 'volume_eligible': False, 'physical_state_join_eligible': False, 'seasonal_playback_eligible': False, 'annual_extrema_eligible': False, 'climatology_years': [1993, 2022], 'section_name': 'Bjornoya', 'core_definition': {'absolute_salinity_min_g_kg': 35.16, 'salinity_operator': '>=', 'excluded_surface_upper_depth_m': 50, 'shoreward_isobath_m': None, 'fraction_of_mean_transport': 0.5, 'ranking': 'decreasing_absolute_geostrophic_velocity', 'static_mean_mask': True}, 'source_section_transect_count': 53, 'source_cross_section_area_km2': 17, 'source_area_is_approximate': True, 'source_area_geometry': 'Rectangular midpoint cells of static mean transport-selected core; topographic partial-cell cuts are not resolved.', 'source_area_uncertainty_km2': None, 'source_lateral_cutoff_policy': 'No numerical SI/GI isobath cutoff inherited at Bjornoya', 'source_quarterly_interpolation_is_depth_series': False, 'reference_route_projection_eligible': False}}


def validate_context(row,root=ROOT):
    clean={k:v for k,v in row.items() if k not in ['source_file','source_pointer','source_sha256']}
    if clean!=EXPECTED_REFERENCES.get(row['id']):raise ValueError('Unreviewed Bjornoya mean-core definition, area or scope')


def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v38.py',RULES,SOURCE,MEMBERS,MEMBER_OUTPUT]:
        pins[p]=hashlib.sha256((root/p).read_bytes()).hexdigest()
    source=json.loads((root/SOURCE).read_bytes());rules=json.loads((root/RULES).read_bytes())
    if source['previous_register_sha256']!=pins[previous.OUTPUT]:raise ValueError('Prior pin mismatch')
    for p,digest in source['source_input_sha256'].items():
        if pins[p]!=digest:raise ValueError('Retained source XML changed')
    evidence=list(prior['evidence']);seen={r['id'] for r in evidence};identities={r['entity_id'] for r in prior['records']}
    for i,row in enumerate(source['references']):
        validate_reference(row,identities,rules['metric_types']);validate_context(row,root)
        if row['id'] in seen:raise ValueError('Duplicate source reference')
        seen.add(row['id']);evidence.append(dict(row,source_file=SOURCE,source_pointer=f'/references/{i}',source_sha256=pins[SOURCE]))
    records=[]
    for raw in prior['records']:
        row=dict(raw);row['depth_reference_ids']=[r['id'] for r in evidence if r['entity_id']==row['entity_id']]
        row['status']='scoped_depth_reference' if row['depth_reference_ids'] else 'not_yet_assessed';records.append(row)
    owners=sum(bool(r['depth_reference_ids']) for r in records)
    return {'schema':'osw.current-depth-register.v39','status':'NWASC_BJORNOYA_STATIC_CORE_DEPTH_AND_AREA',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v39.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v39.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Bjornoya580m is a static AW transport-ranked core-mask maximum, paired with an approximate17km2 section area. It does not inherit southern-section isobath cutoffs, a physical top/bottom, seasonal depth series or whole-current volume.',
            'metadata_correction_file':prior.get('metadata_correction_file'),'metadata_correction_count':prior.get('metadata_correction_count',0),'member_depth_index_file':MEMBER_OUTPUT,'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns += [p for p in ['source_area_is_approximate', 'source_area_geometry', 'source_area_uncertainty_km2', 'source_lateral_cutoff_policy', 'source_quarterly_interpolation_is_depth_series', 'source_section_transect_count','source_cross_section_area_km2', 'source_cross_section_area_role', 'source_distance_offshore_km', 'source_distance_offshore_is_current_width', 'source_model_grid_rotation_clockwise_degrees', 'source_signed_alongshore_isotach_m_s', 'model_simulation_period', 'source_record_vertical_datum', 'normalization_file', 'normalization_rule_id','core_latitude_relation', 'source_ship_section_count', 'source_ship_section_year_bounds', 'surface_mean_completion', 'section_latitude_degrees_north','source_record_period', 'source_record_period_has_gaps', 'comparison_products', 'ADCP_velocities_assimilated_in_ECCOv4r4', 'source_raw_ADCP_bin_size_m', 'source_raw_ADCP_sampling_seconds', 'source_processed_ADCP_level_spacing_m', 'source_study_velocity_averaging_hours','source_survey_periods', 'source_ADCP_frequency_kHz', 'source_displayed_ADCP_limit_m', 'station_profile_averaging_definition', 'source_figure4_velocity_quantity', 'source_citation', 'range_interpretation', 'upper_boundary_m', 'lower_boundary_m', 'thickness_m', 'uncertainty_m', 'annual_range_m', 'calendar_months', 'observed_period', 'independent_observation_count_claimed', 'whole_current_representative', 'volume_eligible', 'physical_state_join_eligible', 'seasonal_playback_eligible', 'annual_extrema_eligible','source_research_vessel','source_STF_bracketing_latitude_range_degrees_north','source_STF_bracket_longitude_degrees_east','source_depth_phrase','source_speed_context_cm_s','geostrophic_reference_definition','source_table2_reference_depth_summary_m','source_table2_reference_flag','figure5_reference_policy','source_site_id'] if p not in columns]
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')
