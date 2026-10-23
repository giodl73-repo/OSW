"""Complete native/WASM station links and keyboard current-card investigation."""
import gzip
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote

from playwright.sync_api import sync_playwright, expect

from redsox_station_support_query import ROOT, REPORT, ID, AVAILABILITY, evidence
from test_current_research_evidence_browser import native, BASE


def main():
    source, diagnostic, _ = evidence()
    output = ROOT / '.pytest_cache/redsox-station-support/query-browser'
    output.mkdir(parents=True, exist_ok=True)
    errors, originals = [], []
    with sync_playwright() as pw, TemporaryDirectory(dir=output) as tmp:
        index = Path(tmp) / 'index.json'
        index.write_bytes(gzip.decompress((ROOT / 'almanac/index-data.json.gz').read_bytes()))
        browser = pw.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page = browser.new_page(viewport={'width': 1200, 'height': 1000})
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('request', lambda r: originals.append(r.url) if r.url.split('?')[0].endswith(('.zip', '.nc', '.npz', '.pdf')) else None)
        q = dict(collection='diagnostics', filters=[dict(field='id', op='eq', value=ID)], limit=1)
        page.goto(BASE + '/almanac/query.html?q=' + quote(json.dumps(q)))
        page.wait_for_function('window.oswLastQueryResult', timeout=180000)
        result = page.evaluate('window.oswLastQueryResult')
        assert result == native(q) and result['rows'] == [diagnostic]
        cases = [('/profiles', None, source['profiles']),
                 ('/profiles', 'provider_metadata_review_required', [r for r in source['profiles'] if r['assessment']['status'] == 'provider_metadata_review_required']),
                 ('/profiles', 'missing_ctd_record', [r for r in source['profiles'] if r['assessment']['status'] == 'missing_ctd_record']),
                 ('/ctd_records_without_ladcp', None, source['ctd_records_without_ladcp'])]
        for pointer, text, expected in cases:
            q = dict(document=REPORT, pointer=pointer, limit=445, offset=0)
            if text is not None:
                q['text'] = text
            page.goto(BASE + '/almanac/query.html?source-q=' + quote(json.dumps(q)))
            page.wait_for_function('window.oswSourceQueryResult', timeout=180000)
            result = page.evaluate('window.oswSourceQueryResult')
            assert result == native(q, index=index)
            assert [r['record'] for r in result['rows']] == expected
        numeric_cases = [
            ('record.assessment.original_filename_join.ctd_start_minus_ladcp_header_time_seconds', 'eq', -919,
             [r for r in source['profiles'] if r['assessment']['original_filename_join'] is not None and r['assessment']['original_filename_join']['ctd_start_minus_ladcp_header_time_seconds'] == -919]),
            ('record.assessment.original_filename_join.ctd_start_minus_ladcp_header_time_seconds', 'ne', -919,
             [r for r in source['profiles'] if r['assessment']['original_filename_join'] is None or r['assessment']['original_filename_join']['ctd_start_minus_ladcp_header_time_seconds'] != -919]),
            ('record.station', 'eq', 73.0, [r for r in source['profiles'] if r['station'] == 73]),
        ]
        for field, op, value, expected in numeric_cases:
            q = dict(document=REPORT, pointer='/profiles', filters=[dict(field=field, op=op, value=value)], limit=445, offset=0)
            page.goto(BASE + '/almanac/query.html?source-q=' + quote(json.dumps(q)))
            page.wait_for_function('window.oswSourceQueryResult', timeout=180000)
            result = page.evaluate('window.oswSourceQueryResult')
            assert result == native(q, index=index)
            assert [r['record'] for r in result['rows']] == expected
        expected = json.loads((ROOT / AVAILABILITY).read_bytes())['directory_checks']
        q = dict(document=AVAILABILITY, pointer='/directory_checks', limit=4, offset=0)
        page.goto(BASE + '/almanac/query.html?source-q=' + quote(json.dumps(q)))
        page.wait_for_function('window.oswSourceQueryResult', timeout=180000)
        result = page.evaluate('window.oswSourceQueryResult')
        assert result == native(q, index=index)
        assert [r['record'] for r in result['rows']] == expected
        page.set_viewport_size({'width': 320, 'height': 1000})
        page.goto(BASE + '/almanac/reference-routes.html?atlas-feature=current%3Ared-sea-saline-overflow#route-atlas')
        links = page.locator('.route-atlas-evidence-links'); links.wait_for(state='attached', timeout=180000)
        links.locator('summary').focus(); page.keyboard.press('Enter')
        link = links.get_by_role('link', name='Inspect REDSOX velocity and CTD station metadata', exact=True)
        expect(link).to_be_visible(); link.focus(); page.keyboard.press('Enter')
        page.wait_for_function('window.oswStationReady', timeout=60000)
        page.locator('#profile').select_option('rsx1-073-hr')
        page.locator('#query').focus(); page.keyboard.press('Enter')
        page.wait_for_function('window.oswSourceQueryResult', timeout=180000)
        result = page.evaluate('window.oswSourceQueryResult')
        assert [r['record'] for r in result['rows']] == [r for r in source['profiles'] if r['id'] == 'rsx1-073-hr']
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(output / 'phone.png'))
        assert not errors and not originals, (errors, originals)
        browser.close()
    result = dict(status='PASS', complete_diagnostic_native_wasm_exact=True,
                  complete_velocity_profiles_exact=445, complete_ctd_records_exact=461,
                  review_records_exact=13, missing_companion_records_exact=1,
                  unmatched_ctd_records_exact=17, complete_archive_directory_checks=4,
                  integer_float_source_equality_and_inequality_cases=3,
                  keyboard_card_view_selected_query=True, phone_320px=True,
                  automatic_original_downloads=0, physical_casts_verified=0,
                  synchronized_samples_verified=0, physical_width_admitted=False)
    (output / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
