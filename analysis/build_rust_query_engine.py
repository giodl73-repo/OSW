"""Compile the same pinned Rust engine for local CLI and browser WASM."""
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST='rust/osw-query/Cargo.toml'

def main():
    if shutil.disk_usage(ROOT).free < 512*1024*1024:
        raise SystemExit('Need at least512MiB free before formatting/building the query engine; existing sources are left untouched.')
    # Embedded scientific reports make incremental caches large; default to a
    # bounded build while retaining an explicit caller override.
    os.environ.setdefault('CARGO_INCREMENTAL','0')
    os.environ.setdefault('CARGO_BUILD_JOBS','1')
    for args in [['cargo','fmt','--manifest-path',MANIFEST],
                 ['cargo','test','--offline','--locked','--manifest-path',MANIFEST],
                 ['cargo','build','--offline','--locked','--manifest-path',MANIFEST]]:
        subprocess.run(args,cwd=ROOT,check=True)
    cli=ROOT/'rust/osw-query/target/debug'/('osw-query-cli.exe' if os.name=='nt' else 'osw-query-cli')
    subprocess.run([str(cli),str(ROOT/'almanac/query-data.json'),'--atlas'],cwd=ROOT,stdout=subprocess.DEVNULL,check=True)
    print('Checked native atlas snapshot against the generated bundle')
    subprocess.run(['cargo','rustc','--offline','--locked','--release','--target','wasm32-unknown-unknown','--lib','--crate-type','cdylib','--manifest-path',MANIFEST],cwd=ROOT,check=True)
    target=ROOT/'almanac/query-engine.wasm'
    shutil.copyfile(ROOT/'rust/osw-query/target/wasm32-unknown-unknown/release/osw_query.wasm',target)
    paths=['rust/osw-query/Cargo.toml','rust/osw-query/Cargo.lock','rust/osw-query/src/lib.rs','rust/osw-query/src/map.rs','rust/osw-query/src/spatial.rs','rust/osw-query/src/workspace.rs','rust/osw-query/src/rebase.rs','rust/osw-query/src/main.rs',
           'rust/osw-query/src/svg.rs','rust/osw-query/src/temporal.rs','rust/osw-query/src/seasonal.rs','rust/osw-query/src/samples.rs','rust/osw-query/src/charts.rs','rust/osw-query/src/planning.rs','rust/osw-query/src/loop_diagnostics.rs','rust/osw-query/src/network.rs','rust/osw-query/src/taxonomy.rs','figures/ocean-motion-dashboard-ground.svg','almanac/query-engine.wasm','almanac/query-data.json']
    paths.extend(['rust/osw-query/src/current_sections.rs','research/agulhas-asca-100m-query-contract.json'])
    paths.extend(['research/radenac-ngcc-2016-journal-integrity-contract.json','analysis/radenac_hal_source.py'])
    paths.append('rust/osw-query/src/basin_spans.rs')
    paths.append('rust/osw-query/src/observed_spans.rs')
    paths.append('rust/osw-query/src/nordic_widths.rs')
    paths.append('rust/osw-query/src/dashboard.rs')
    paths.append('rust/osw-query/src/dashboard_map.rs')
    paths.append('rust/osw-query/src/dashboard_beck.rs')
    paths.append('rust/osw-query/src/seasons_data.rs')
    paths.append('rust/osw-query/src/object_view.rs')
    paths.append('rust/osw-query/src/eddy_recurrence.rs')
    paths.append('rust/osw-query/src/object_plot.rs')
    paths.append('rust/osw-query/src/atlas_data.rs')
    paths.append('rust/osw-query/src/qualitative_calendar.rs')
    paths.append('rust/osw-query/src/atlantic_euc_sections.rs')
    paths.extend(['rust/osw-query/src/antilles_cruise_spans.rs','research/antilles-cainzos-2023-cruise-section-spans.json'])
    paths.extend(['rust/osw-query/src/model_axis_spread.rs','research/pacific-necc-chen-2016-axis-spread-scale-scope-audit.json'])
    paths.append('rust/osw-query/src/proposed_widths.rs')
    paths.extend(['rust/osw-query/src/stream_tube_widths.rs','rust/osw-query/src/selected_core_widths.rs',
                  'research/west-spitsbergen-dundas-2026-selected-core-width-scope-audit.json',
                  'research/source-data/dundas-fer-wsc-2026/figure.json'])
    paths.extend(['rust/osw-query/src/current_length_bounds.rs','analysis/north_atlantic_gate_bound.py','research/north-atlantic-nominal-gate-bound.json','figures/north-atlantic-nominal-gate-bound.svg'])
    paths.extend(['rust/osw-query/src/nwasc_admission.rs','analysis/nwasc_working_admission.py','research/norwegian-atlantic-slope-working-admission.json','research/ocean-current-effective-catalogue.json','research/ocean-current-live-measurements.json','plans/nwasc-working-admission-protocol-v1.md','research/source-data/orvik-niiler-ices-2001/acquisition.json','figures/norwegian-atlantic-slope-admitted-dimensions.svg'])
    paths.extend(['rust/osw-query/src/hansen_asar_widths.rs','analysis/hansen_asar_widths.py','research/hansen-2011-asar-surface-width-admissions.json','research/ocean-current-measurements-asar-edition.json','plans/hansen-asar-width-admission-protocol-v1.md','research/source-data/hansen-asar-2011/acquisition.json','figures/hansen-2011-asar-surface-widths.svg'])
    paths.extend(['rust/osw-query/src/nwasc_reference_route.rs','analysis/nwasc_source_anchor_route.py','research/nwasc-source-anchor-reference-route.json','research/nwasc-source-anchor-reference-route-input.json','plans/nwasc-source-anchor-route-protocol-v1.md','figures/nwasc-source-anchor-reference-route.svg'])
    paths.extend(['rust/osw-query/src/neuc_glider_widths.rs','analysis/neuc_glider_widths.py','research/neuc-glider-2015-width-source-input.json','research/neuc-glider-2015-source-review.json','research/neuc-glider-2015-width-admissions.json','research/ocean-current-measurements-neuc-edition.json','plans/neuc-glider-width-admission-protocol-v1.md','figures/neuc-glider-2015-width-ranges.svg'])
    paths.extend(['rust/osw-query/src/aleutian_onishi_width.rs','analysis/aleutian_onishi_width.py','research/aleutian-onishi-2001-width-input.json','research/aleutian-onishi-2001-width-admission.json','research/aleutian-onishi-2001-width-contract.json','research/ocean-current-measurements-aleutian-edition.json','research/source-data/onishi-aleutian-2001/acquisition.json','plans/aleutian-onishi-width-admission-protocol-v1.md','figures/aleutian-onishi-2001-width-constraint.svg'])
    paths.append('rust/osw-query/src/abstract_regional_widths.rs')
    paths.append('rust/osw-query/src/astrid_scales.rs')
    paths.append('rust/osw-query/src/eddy_source_panels.rs')
    paths.append('rust/osw-query/src/ursa_contour.rs')
    paths.append('rust/osw-query/src/ring_radii.rs')
    paths.append('rust/osw-query/src/somali_width.rs')
    paths.append('rust/osw-query/src/guinea_width.rs')
    paths.append('rust/osw-query/src/original_regional_widths.rs')
    paths.extend(['rust/osw-query/src/current_width_source_reviews.rs','research/southern-current-width-source-limitations-audit.json'])
    paths.extend(['rust/osw-query/src/portugal_section_span.rs','research/portugal-perez-2013-orca-section-span-scope-audit.json'])
    paths.append('research/gulf-stream-published-width-definitions-scope-audit.json')
    paths.append('research/loop-uhlhorn-2008-core-width-scope-audit.json')
    paths.append('research/south-pacific-stramma-1995-width-constraint-scope-audit.json')
    paths.append('research/south-atlantic-stramma-1990-secondary-band-scope-audit.json')
    paths.append('rust/osw-query/src/dwbc_float_composite.rs')
    paths.extend(['rust/osw-query/src/published_transports.rs','rust/osw-query/src/pacific_neuc_breadths.rs'])
    paths.extend(['rust/osw-query/src/coastal_composite_widths.rs','figures/schubert-aacc-2021-source-sections.png'])
    paths.append('rust/osw-query/src/modal_decay_widths.rs')
    paths.append('rust/osw-query/src/observed_sections.rs')
    paths.append('rust/osw-query/src/cartography.rs')
    paths.append('rust/osw-query/src/norkyst_data.rs')
    paths.append('rust/osw-query/src/movies.rs')
    paths.append('rust/osw-query/src/model_sections.rs')
    paths.append('rust/osw-query/src/mooring_velocity.rs')
    paths.append('rust/osw-query/src/loop_recorded.rs')
    paths.append('rust/osw-query/src/index_bifurcation.rs')
    paths.extend(['rust/osw-query/src/index_store.rs','rust/osw-query/src/index_noaa.rs','rust/osw-query/src/index_support.rs','rust/osw-query/src/index_map.rs','almanac/index-catalog.json','almanac/index-data.json.gz'])
    paths.extend(['rust/osw-query/src/current_research_evidence.rs','research/current-research-evidence-registry.json',
                  'research/indian-secc-eof-classification-feasibility.json','research/redsox-lower-nc-dated-section-diagnostic.json',
                  'research/source-data/norkyst-ingoy-months-2024/section-diagnostic-year.json',
                  'research/pacific-necc-paired-vector-direction-evidence.json',
                  'research/aleutian-p14n-1993-observed-vector-section.json',
                  'research/aleutian-p14n-1993-hydrography-correspondence.json',
                  'research/aleutian-p14n-1993-component-spans.json',
                  'research/aleutian-p14n-1993-underway-averages.json',
                  'research/aleutian-p14n-1993-underway-averages-figure.json',
                  'research/aleutian-p14n-1993-run-composite.json',
                  'research/aleutian-p14n-1993-run-composite-figure.json'])
    paths.extend(['rust/osw-query/src/measurement_scope.rs','research/current-measurement-object-scope-index.json'])
    paths.extend(['rust/osw-query/src/kuroshio_filtered_width.rs','research/kuroshio-ecs-filtered-width-time-series.json',
                  'research/kuroshio-ecs-filtered-width-time-series-figure.json',
                  'research/source-data/kuroshio-liu-gan-2012/figure7a-time-extraction.json','analysis/kuroshio_filtered_width.py'])
    paths.extend(['rust/osw-query/src/asca_component_spans.rs','research/agulhas-asca-100m-dated-component-spans.json',
                  'research/agulhas-asca-100m-dated-component-spans-figure.json','analysis/asca_component_spans.py'])
    paths.extend(['rust/osw-query/src/eac_source_fields.rs','research/eac-csiro-v23-100m-source-quality.json',
                  'research/eac-csiro-v23-100m-source-query-contract.json','research/eac-csiro-v23-100m-source-fields-figure.json',
                  'analysis/eac_source_fields.py'])
    paths.extend(['rust/osw-query/src/eac_core_spans.rs','research/eac-csiro-100m-section-core-spans-summary.json',
                  'research/eac-csiro-100m-section-core-spans-figure.json','analysis/eac_core_spans.py'])
    paths.extend(['rust/osw-query/src/south_australian_context.rs','analysis/south_australian_flow_context.py',
                  'research/south-australian-hycom-2d-flow-context-scene.json'])
    paths.append('research/source-data/loop-durante-2026-v0/quality.json')
    paths.extend(['analysis/scientific_readback.py','plans/scientific-calculation-readback-protocol-v1.md'])
    paths.extend(['analysis/build_eac_calendar_distributions.py',
                  'analysis/build_eac_calendar_distribution_figure.py',
                  'plans/eac-section-calendar-distribution-protocol-v1.md',
                  'research/eac-section-calendar-distributions.json',
                  'research/eac-section-calendar-distributions-figure.json'])
    paths.extend(['analysis/acquire_west_australian_oscar_2d.py',
                  'analysis/build_west_australian_oscar_2d_source.py',
                  'analysis/build_west_australian_oscar_2d_source_figure.py',
                  'plans/west-australian-oscar-2d-source-selection-protocol-v1.md',
                  'research/west-australian-oscar-2d-monthly-source-fields.json',
                  'research/west-australian-oscar-2d-source-figure.json',
                  'research/source-data/oscar-west-australian-2d-2013/acquisition.json'])
    paths.extend(['analysis/west_australian_regional_streamlines.py',
                  'analysis/west_australian_regional_streamlines_rk4.py',
                  'analysis/build_west_australian_regional_streamline_figures.py',
                  'analysis/build_west_australian_regional_streamline_rk4_figures.py',
                  'analysis/west_australian_streamline_evidence.py',
                  'plans/west-australian-regional-streamline-protocol-v1.md',
                  'plans/west-australian-regional-streamline-rk4-protocol-v2.md',
                  'research/west-australian-regional-streamlines.json',
                  'research/west-australian-regional-streamlines-rk4.json',
                  'research/west-australian-regional-streamline-figures.json',
                  'research/west-australian-regional-streamline-rk4-figures.json'])
    paths.extend(['analysis/build_redsox_section3_spans.py','analysis/build_redsox_section3_figure.py',
                  'plans/redsox-section3-width-protocol-v1.md','research/redsox-section3-source-selection.json',
                  'research/redsox-winter-section3-component-spans.json','research/redsox-winter-section3-figure.json'])
    paths.extend(['analysis/build_redsox_section3_repeat.py','analysis/build_redsox_section3_repeat_figure.py',
                  'plans/redsox-section3-repeat-survey-protocol-v1.md','research/redsox-section3-repeat-source-selection.json',
                  'research/redsox-section3-repeat-surveys.json','research/redsox-section3-repeat-figure.json'])
    paths.extend(['rust/osw-query/src/current_section_measurements.rs','analysis/current_section_measurements.py',
                  'plans/current-section-measurement-records-v1.md','almanac/current-research-evidence.js','almanac/query.js'])
    paths.extend(['analysis/build_asca_component_spans.py','plans/asca-alignment-indicator-readback-v1.md'])
    paths.extend(['analysis/check_eac_100m_source.py','plans/eac-fixed-array-distance-readback-v1.md'])
    paths.append('almanac/asca-component-spans.js')
    paths.extend(['analysis/eac_core_readback.py','plans/eac-section-core-calculation-readback-v1.md'])
    paths.append('plans/eac-section-core-calculation-readback-v2.md')
    paths.extend(['rust/osw-query/src/asca_calendar.rs','analysis/build_asca_calendar_distributions.py',
                  'analysis/build_asca_calendar_distribution_figure.py','plans/asca-component-calendar-distribution-protocol-v1.md',
                  'research/asca-component-calendar-distributions.json','research/asca-component-calendar-distributions-figure.json',
                  'figures/asca-component-calendar-distributions.svg','figures/asca-component-calendar-distributions.png'])
    paths.append('plans/published-local-model-snapshot-width-admission-v1.md')
    paths.append('figures/southern-east-madagascar-reported-dimensions.svg')
    paths.extend(['rust/osw-query/src/current_gap_admissions.rs',
                  'almanac/object.html', 'almanac/object.js', 'almanac/current-source-evidence-ui.js',
                  'almanac/dashboard.html', 'almanac/index.html',
                  'research/ocean-motion-dashboard.json', 'almanac/index-sources.json',
                  'analysis/current_gap_candidate_metadata.py',
                  'analysis/current_gap_index_extension.py',
                  'analysis/export_current_gap_cloud_candidate.py',
                  'analysis/check_current_gap_parent_rehearsal.py',
                  'research/current-gap-parent-query-packet-v1.json',
                  'research/indian-current-identity-query-contract-v1.json',
                  'research/indian-current-evidence-query-contract-v1.json',
                  'research/brazil-regional-reach-query-contract-v1.json',
                  'research/eicc-t24-published-width-admission-v1.json',
                  'research/indian-current-reference-route-planning-v1.json'])
    paths.extend(['rust/osw-query/src/current_catalogue.rs','analysis/current_identity_admissions.py','almanac/current-identity-ui.js',
                  'plans/current-identity-admission-protocol-v1.md','research/ocean-current-identity-admissions.json',
                  'research/ocean-current-working-catalogue.json','figures/southern-east-madagascar-admitted-identity.svg'])
    paths.extend(['rust/osw-query/src/current_measurements.rs','analysis/current_measurement_admissions.py',
                  'plans/published-prose-dimension-admission-protocol-v1.md','research/southern-east-madagascar-prose-dimension-admissions.json',
                  'research/ocean-current-working-measurements.json','figures/southern-east-madagascar-admitted-dimensions.svg'])
    paths.extend(['analysis/check_south_australian_miller_model_width.py',
                  'research/south-australian-miller-2006-model-width-scope-audit.json',
                  'research/source-data/miller-south-australian-2006/acquisition.json',
                  'research/source-data/miller-south-australian-2006/dissertation.pdf',
                  'plans/south-australian-miller-model-width-protocol-v1.md',
                  'figures/south-australian-miller-model-width.svg'])
    paths.extend(['research/norwegian-atlantic-slope-orvik-2003-dimension-candidates.json',
                  'figures/norwegian-atlantic-slope-reported-dimensions.svg'])
    paths.extend(['rust/osw-query/src/madagascar_navigation.rs','analysis/madagascar_navigation_diagnostic.py',
                  'research/southern-east-madagascar-route-definition-diagnostic.json',
                  'figures/southern-east-madagascar-route-definition-diagnostic.svg'])
    from madagascar_reference_curve import verify_inputs as coastal_curve_inputs
    paths.extend(coastal_curve_inputs()[2])
    paths.append('rust/osw-query/src/madagascar_coastal_curve.rs')
    from kuroshio_wang_query import verify_inputs as verify_kuroshio_daily
    daily_contract,_=verify_kuroshio_daily()
    paths.extend(daily_contract['input_sha256'])
    paths.extend(['research/kuroshio-wang-2024-query-contract.json','rust/osw-query/src/kuroshio_daily.rs','almanac/kuroshio-daily.js'])
    from kuroshio_axis_normal_query import verify_inputs as verify_normals
    normal_contract,_=verify_normals()
    paths.extend(normal_contract['input_sha256'])
    paths.extend(['research/kuroshio-wang-2024-axis-normal-query-contract.json','rust/osw-query/src/kuroshio_normal.rs',
                  'almanac/reference-route-atlas.js','almanac/dashboard.js'])
    from query_packet import SCHEMA, descriptors
    from agulhas_reported_dimensions import verify_inputs as verify_agulhas_reported
    _,agulhas_reported_inputs=verify_agulhas_reported()
    paths.extend(agulhas_reported_inputs)
    paths.extend(['rust/osw-query/src/agulhas_reported.rs','almanac/reported-dimensions.js','almanac/query-charts.js'])
    from nwasc_mean_core_widths import verify_inputs as verify_mean_core
    _,mean_core_inputs=verify_mean_core();paths.extend(mean_core_inputs)
    paths.extend(['rust/osw-query/src/nwasc_mean_core.rs','almanac/reference-routes.js'])
    from build_indian_secc_oscar_2d_source import verify as verify_secc_context
    _,secc_context_inputs=verify_secc_context();paths.extend(secc_context_inputs)
    from indian_secc_positive_bands import verify as verify_secc_bands
    _,secc_band_inputs=verify_secc_bands();paths.extend(secc_band_inputs)
    from indian_secc_local_normals import verify as verify_secc_normals
    _,secc_normal_inputs=verify_secc_normals();paths.extend(secc_normal_inputs)
    from indian_secc_hycom_local_normals import verify as verify_secc_hycom
    _,secc_hycom_inputs=verify_secc_hycom();paths.extend(secc_hycom_inputs)
    paths.extend(['almanac/atlas-width-evidence.js','almanac/reference-routes.js','almanac/seasons.js',
                  'almanac/query.html','almanac/reference-routes.html','almanac/seasons.html'])
    from south_indian_front_level_query import view_evidence as front_level_evidence
    _,_,_,front_level_inputs=front_level_evidence();paths.extend(front_level_inputs)
    from south_indian_front_property_query import view_evidence as property_evidence
    _,_,property_inputs=property_evidence();paths.extend(property_inputs)
    from current_gap_source_evidence import evidence as gap_source_evidence
    _,_,_,gap_inputs=gap_source_evidence();paths.extend(gap_inputs)
    from redsox_station_support_query import evidence as station_support_evidence
    _,_,station_inputs=station_support_evidence();paths.extend(station_inputs)
    from labrador_gate_bound_query import evidence as labrador_bound_evidence
    _,labrador_bound_inputs=labrador_bound_evidence();paths.extend(labrador_bound_inputs)
    paths.append('rust/osw-query/src/labrador_latitude_bound.rs')
    paths.append('rust/osw-query/src/length_assessment_overlays.rs')
    from ke_length_series_query import evidence as ke_length_evidence
    _,ke_length_inputs=ke_length_evidence();paths.extend(ke_length_inputs)
    paths.append('rust/osw-query/src/ke_regional_length.rs')
    from caribbean_ru29_query import evidence as caribbean_source_evidence
    _,caribbean_source_inputs=caribbean_source_evidence();paths.extend(caribbean_source_inputs)
    paths.append('rust/osw-query/src/caribbean_source_fields.rs')
    from published_regional_reaches_query import evidence as regional_reach_evidence
    _,regional_reach_inputs=regional_reach_evidence();paths.extend(regional_reach_inputs)
    paths.append('rust/osw-query/src/published_regional_reaches.rs')
    from angola_nansen_source_query import evidence as angola_native_evidence
    _,_,angola_native_inputs=angola_native_evidence();paths.extend(angola_native_inputs)
    packet=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    paths.extend(['rust/osw-query/src/packet.rs','analysis/query_packet.py','almanac/query-packet.js','almanac/query-worker.js','almanac/query-workspace.js','plans/query-packet-transport-protocol-v1.md'])
    if packet.get('schema')==SCHEMA:
        paths.extend('almanac/'+part['path'] for part in descriptors(packet))
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    rust=subprocess.check_output(['rustc','--version'],text=True).strip()
    (ROOT/'almanac/query-engine.manifest.json').write_text(json.dumps({'schema':'osw.query-engine-manifest.v1','engine':'rust-osw-query-v1',
        'abi_version':1,'rustc':rust,'sha256':hashes},indent=2)+'\n',encoding='utf-8')
    logical_size=packet['logical_byte_length'] if packet.get('schema')==SCHEMA else (ROOT/'almanac/query-data.json').stat().st_size
    print('Built WASM query engine:',target.stat().st_size,'bytes; logical bundle:',logical_size,'bytes; transport parts:',len(packet.get('parts',[])))

if __name__=='__main__':main()
