"""Complete conditional case/diagnostic native-WASM equality and atlas access."""
import gzip
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote

from playwright.sync_api import sync_playwright, expect

from south_indian_front_property_query import ROOT, REPORT, ID, view_evidence
from test_current_research_evidence_browser import native, BASE


def main():
    report, diagnostic, _ = view_evidence()
    out = ROOT/'.pytest_cache/south-indian-front-properties-2013/query-browser'
    out.mkdir(parents=True, exist_ok=True)
    errors = []; originals = []
    with sync_playwright() as pw, TemporaryDirectory(dir=out) as temporary:
        index = Path(temporary)/'index.json'
        index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        browser = pw.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page = browser.new_page(viewport={'width': 1280, 'height': 1000})
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('request', lambda r: originals.append(r.url) if r.url.endswith(('.zip', '.npz', '.pdf', '.nc')) else None)
        query = {'collection': 'diagnostics', 'filters': [{'field': 'id', 'op': 'eq', 'value': ID}], 'limit': 1}
        page.goto(BASE+'/almanac/query.html?q='+quote(json.dumps(query)))
        page.wait_for_function('window.oswLastQueryResult', timeout=180000)
        actual = page.evaluate('window.oswLastQueryResult')
        assert actual == native(query)
        assert actual['rows'] == [diagnostic]
        print('PASS complete diagnostic native/WASM equality', flush=True)
        query = {'document': REPORT, 'pointer': '/cases', 'limit': 36, 'offset': 0}
        page.goto(BASE+'/almanac/query.html?source-q='+quote(json.dumps(query)))
        page.wait_for_function('window.oswSourceQueryResult', timeout=180000)
        actual = page.evaluate('window.oswSourceQueryResult')
        assert actual == native(query, index=index)
        assert [r['record'] for r in actual['rows']] == report['cases']
        print('PASS all36 cases,144 masks and4258 pairs through lossless source query', flush=True)
        page.set_viewport_size({'width': 320, 'height': 1000})
        page.goto(BASE+'/almanac/reference-routes.html?atlas-feature=current%3Asouth-indian#route-atlas')
        links = page.locator('.route-atlas-evidence-links');links.wait_for(state='attached', timeout=180000)
        links.locator('summary').focus();page.keyboard.press('Enter')
        link = links.get_by_role('link', name='Compare conditional property windows with every surface flow peak', exact=True)
        expect(link).to_be_visible();link.focus();page.keyboard.press('Enter')
        page.wait_for_function('window.oswPropertyReady', timeout=60000)
        page.locator('#month').select_option('8');page.locator('#longitude').select_option('2')
        page.locator('#criterion').select_option('arf_theta200')
        page.locator('#case-query').focus();page.keyboard.press('Enter')
        page.wait_for_function('window.oswSourceQueryResult', timeout=180000)
        actual = page.evaluate('window.oswSourceQueryResult')
        assert len(actual['rows']) == 1 and actual['rows'][0]['record'] == report['cases'][23]
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert not errors and not originals, (errors, originals)
        page.screenshot(path=str(out/'phone.png'))
        browser.close()
    result = {'status': 'PASS', 'complete_cases_native_wasm_exact': 36,
              'complete_criterion_masks': 144, 'complete_pairs': 4258,
              'diagnostic_native_wasm_exact': True, 'keyboard_card_view_selected_query': True,
              'phone320px': True, 'automatic_original_downloads': 0,
              'front_identification_verified': False, 'physical_width_admitted': False}
    (out/'result.json').write_bytes((json.dumps(result, indent=2)+'\n').encode())
    print(json.dumps(result))


if __name__ == '__main__':
    main()
