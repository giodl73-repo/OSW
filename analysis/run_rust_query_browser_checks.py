"""Run shipped-WASM UI checks against a verified local checkout server."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
URL = 'http://127.0.0.1:8788/almanac/query.html'
CHECKS = ('test_loop_durante_source_browser.py', 'test_south_australian_context_browser.py', 'test_eac_section_core_spans_browser.py', 'test_eac_source_fields_browser.py', 'test_asca_component_spans_browser.py', 'test_kuroshio_filtered_width_browser.py', 'test_selected_core_width_browser.py', 'test_current_research_evidence_browser.py', 'test_current_width_source_review_browser.py', 'test_portugal_orca_section_span_browser.py', 'test_south_atlantic_secondary_band_browser.py', 'test_south_pacific_band_constraint_browser.py', 'test_asca_sections_browser.py', 'test_loop_uhlhorn_core_width_browser.py', 'test_gulf_stream_published_widths_browser.py', 'test_southern_basin_climatology_browser.py', 'test_indian_secc_climatology_browser.py', 'test_persian_gulf_geostrophic_scales_browser.py', 'test_atlantic_seuc_core_width_browser.py', 'test_atlantic_seuc_reach_browser.py', 'test_nordic_proposal_navigation_browser.py', 'test_nordic_section_widths_browser.py', 'test_antilles_sadcp_spans_browser.py', 'test_atlas_inline_width_browser.py', 'test_antarctic_slope_jet_constraint_browser.py', 'test_balearic_socib_width_browser.py', 'test_azores_model_core_browser.py', 'test_bosse_corrected_width_browser.py', 'test_ngcc_seasonal_vein_widths_browser.py', 'test_pacific_secc_historical_width_browser.py', 'test_basin_surface_sections_browser.py', 'test_rust_width_samples.py', 'test_hiri_east_adriatic_local_widths_browser.py', 'test_caribbean_dated_width_browser.py', 'test_ursa_contour_candidate_browser.py', 'test_thor_ursa_source_panels_browser.py', 'test_pacific_neuc_isopycnal_breadths_browser.py', 'test_published_section_transports_browser.py', 'test_dwbc_float_composite_browser.py', 'test_antarctic_coastal_composites_browser.py', 'test_tasman_front_band_browser.py', 'test_monsoon_webber_widths_browser.py', 'test_antarctic_slope_coverage_browser.py', 'test_antarctic_slope_m6_velocity_browser.py', 'test_rust_query_browser.py', 'test_zeehan_seasonal_calendar_browser.py', 'test_zeehan_historical_width_browser.py', 'test_tsushima_modal_width_browser.py', 'test_humboldt_width_descriptions_browser.py', 'test_baffin_regional_widths_browser.py', 'test_western_adriatic_mean_widths_browser.py', 'test_jutland_water_mass_breadth_browser.py', 'test_jutland_satellite_widths_browser.py', 'test_solomon_coastal_confinement_browser.py', 'test_north_pacific_broad_band_browser.py', 'test_acc_udintsev_breadths_browser.py', 'test_rust_collection_coverage_browser.py', 'test_rust_source_query_browser.py',
          'test_motion_dashboard_browser.py', 'test_dashboard_diagnostic_navigation_browser.py',
          'test_rust_workspace_browser.py', 'test_rust_rebase_browser.py',
          'test_rust_taxonomy_browser.py', 'test_florida_width_statistics_browser.py',
          'test_florida_monthly_plot_browser.py', 'test_agulhas_mean_section_width_browser.py',
          'test_seasonal_atlas_navigation_browser.py',
          'test_dashboard_atlas_navigation_browser.py',
          'test_atlas_touch_zoom_browser.py',
          'test_atlas_shared_view_browser.py',
          'test_atlas_state_navigation_browser.py',
          'test_atlas_eddy_state_links_browser.py',
          'test_reference_route_atlas_browser.py',
          'test_atlas_directory_states_browser.py',
          'test_atlas_route_state_links_browser.py',
          'test_seasons_rust_snapshot_browser.py', 'test_atlantic_cruise_widths_browser.py', 'test_atlantic_station_context_browser.py', 'test_black_sea_regional_width_browser.py', 'test_guinea_model_width_browser.py', 'test_original_regional_widths_browser.py', 'test_atlantic_euc_section_properties_browser.py', 'test_ngcc_seasonal_direction_browser.py',
          'test_rust_object_view_browser.py', 'test_black_sea_eddy_recurrence_browser.py', 'test_rust_atlas_snapshot_browser.py',
          'test_atlas_timeline_browser.py', 'test_atlas_observed_sections_browser.py',
          'test_rust_cartography_browser.py', 'test_norkyst_section_browser.py',
          'test_atlas_monthly_width_browser.py',
          'test_atlas_seasonal_width_profile_browser.py',
          'test_atlas_monthly_section_browser.py', 'test_antilles_sections_browser.py',
          'test_pacific_necc_section_browser.py', 'test_dated_current_checked_browser.py',
          'test_rust_movies_browser.py', 'test_rust_model_sections_browser.py',
          'test_rust_loop_recorded_dates.py', 'test_rust_index_store_browser.py',
          'test_rust_index_page_browser.py', 'test_rust_index_currents_browser.py',
          'test_rust_index_eddies_browser.py', 'test_rust_index_nasa_browser.py',
          'test_rust_index_release_media_browser.py', 'test_rust_index_state_memberships_browser.py',
          'test_rust_index_state_context_browser.py', 'test_rust_index_noaa_browser.py',
          'test_rust_index_support_browser.py', 'test_rust_index_map_browser.py',
          'test_eac_calendar_browser.py', 'test_west_australian_oscar_2d_browser.py', 'test_west_australian_streamline_browser.py',
          'test_redsox_section3_repeat_browser.py', 'test_asca_section_measurements_browser.py')


CHECKS = ('test_asca_calendar_distributions_browser.py',) + CHECKS
CHECKS = ('test_madagascar_proposal_browser.py',) + CHECKS
CHECKS = ('test_current_identity_admission_browser.py',) + CHECKS
CHECKS = ('test_prose_dimensions_browser.py', 'test_madagascar_navigation_browser.py', 'test_madagascar_coastal_browser.py') + CHECKS
CHECKS = ('test_kuroshio_wang_query_browser.py',) + CHECKS
CHECKS = ('test_kuroshio_axis_normal_browser.py',) + CHECKS
CHECKS = ('test_agulhas_reported_dimensions_browser.py',) + CHECKS
CHECKS = ('test_nwasc_mean_core_widths_browser.py',) + CHECKS
CHECKS = ('test_aleutian_onishi_width_browser.py', 'test_neuc_glider_widths_browser.py', 'test_nwasc_reference_route_browser.py', 'test_hansen_asar_widths_browser.py', 'test_nwasc_working_admission_browser.py', 'test_north_atlantic_gate_bound_browser.py', 'test_indian_secc_local_normals_browser.py', 'test_indian_secc_positive_bands_browser.py', 'test_indian_secc_oscar_2d_browser.py') + CHECKS
CHECKS = ('test_indian_secc_hycom_view_browser.py', 'test_indian_secc_hycom_query_browser.py') + CHECKS
CHECKS = ('test_query_packet_browser.py',) + CHECKS

def wait_for_checkout(server=None):
    expected = (ROOT / 'almanac/query.html').read_bytes()
    deadline = time.monotonic() + 30
    while True:
        if server is not None and server.poll() is not None:
            raise RuntimeError('Test server exited; port 8788 may already be in use')
        try:
            with urllib.request.urlopen(URL, timeout=2) as response:
                actual = response.read()
            if actual != expected:
                raise RuntimeError('Port 8788 is serving a different checkout')
            return
        except (urllib.error.URLError, TimeoutError):
            if time.monotonic() >= deadline:
                raise RuntimeError('Local test server did not become ready within 30 seconds')
            time.sleep(.2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--start-server', action='store_true',
                        help='Start and stop a dedicated server; omit to reuse the existing local server')
    parser.add_argument('--from-check', choices=CHECKS,
                        help='Resume at this check; earlier checks are not rerun')
    args = parser.parse_args()
    environment = os.environ.copy()
    if not environment.get('OSW_TEST_BROWSER'):
        # Give every child check the same installed Playwright browser in CI.
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            environment['OSW_TEST_BROWSER'] = playwright.chromium.executable_path
    server = None
    try:
        if args.start_server:
            # Reject a occupied port before starting; never terminate a user's server.
            import socket
            with socket.socket() as probe:
                probe.bind(('127.0.0.1', 8788))
            server = subprocess.Popen([sys.executable, '-m', 'http.server', '8788',
                                       '--bind', '127.0.0.1', '--directory', str(ROOT)],
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        wait_for_checkout(server)
        checks = CHECKS[CHECKS.index(args.from_check):] if args.from_check else CHECKS
        for name in checks:
            print(f'Running {name}', flush=True)
            # These gates compare every daily record through paginated native
            # and WASM queries, then load independent corruption fixtures.
            # The source gate already exceeded the old aggregate ten-minute
            # allowance with the smaller corpus. Keep interaction assertions
            # unchanged and budget the complete matrix explicitly.
            # Shared research checks visit all owners/documents before the full corruption matrix.
            timeout = 1800 if name in {'test_current_research_evidence_browser.py', 'test_loop_durante_source_browser.py', 'test_south_australian_context_browser.py', 'test_eac_source_fields_browser.py',
                                      'test_eac_section_core_spans_browser.py', 'test_eac_calendar_browser.py', 'test_west_australian_oscar_2d_browser.py', 'test_west_australian_streamline_browser.py',
                                      'test_rust_index_support_browser.py',
                                      'test_rust_index_noaa_browser.py', 'test_nwasc_working_admission_browser.py', 'test_hansen_asar_widths_browser.py', 'test_aleutian_onishi_width_browser.py', 'test_neuc_glider_widths_browser.py', 'test_nwasc_reference_route_browser.py'} else 600
            subprocess.run([sys.executable, str(ROOT / 'analysis' / name)],
                           cwd=ROOT, env=environment, check=True, timeout=timeout)
    finally:
        if server is not None:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)


if __name__ == '__main__':
    main()
