"""Real Rust/WASM readback and current-card navigation for HYCOM diagnostics."""
import gzip
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote

from playwright.sync_api import sync_playwright, expect
from indian_secc_hycom_local_normals import ROOT, REPORT, verify
from test_current_research_evidence_browser import native, BASE


def main():
    document, _ = verify()
    output = ROOT/'.pytest_cache/indian-secc-hycom-2013/query-browser'
    output.mkdir(parents=True, exist_ok=True)
    errors, originals = [], []
    with TemporaryDirectory(dir=output) as temp, sync_playwright() as pw:
        index = Path(temp)/'index.json'
        index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        browser = pw.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page = browser.new_page(viewport={'width': 1280, 'height': 900})
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('request', lambda r: originals.append(r.url) if r.url.endswith(('.zip', '.npz', '.nc', '.pdf')) else None)
        for key, limit, offset in [('monthly_summary', 12, 0), ('step_comparisons', 72, 0),
                                   ('cases', 100, 0), ('cases', 100, 100)]:
            query = {'document': REPORT, 'pointer': '/'+key, 'limit': limit, 'offset': offset}
            page.goto(BASE+'/almanac/query.html?source-q='+quote(json.dumps(query)))
            page.wait_for_function('window.oswSourceQueryResult', timeout=180000)
            result = page.evaluate('window.oswSourceQueryResult')
            assert result == native(query, index=index)
            assert result['total'] == len(document[key])
            assert [r['record'] for r in result['rows']] == document[key][offset:offset+limit]
            page.set_viewport_size({'width': 320, 'height': 900})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            assert page.locator('#source-query-export').is_enabled()
            print('PASS native/WASM', key, offset, len(result['rows']), flush=True)
        fields_path = 'research/source-data/hycom-indian-secc-2013/monthly-fields.json'
        fields = json.loads((ROOT/fields_path).read_bytes())
        for month_index in [0, 7, 11]:
            query = {'document': fields_path, 'pointer': '/months', 'limit': 1, 'offset': month_index}
            page.goto(BASE+'/almanac/query.html?source-q='+quote(json.dumps(query)))
            page.wait_for_function('window.oswSourceQueryResult', timeout=180000)
            result = page.evaluate('window.oswSourceQueryResult')
            assert result == native(query, index=index)
            assert result['rows'][0]['record'] == fields['months'][month_index]
            print('PASS native/WASM full native-grid month', month_index+1, flush=True)
        page.goto(BASE+'/almanac/reference-routes.html?atlas-feature=current%3Aindian-south-equatorial-countercurrent#route-atlas')
        links = page.locator('.route-atlas-evidence-links')
        links.wait_for(state='attached', timeout=180000)
        links.locator('summary').focus()
        page.keyboard.press('Enter')
        link = links.get_by_role('link', name='Explore finer-grid HYCOM monthly source and candidate tests', exact=True)
        expect(link).to_have_attribute('href', '../'+document['comparison_figure'])
        for name in ['Query HYCOM monthly candidate outcomes', 'Query every HYCOM normal-section attempt',
                     'Compare HYCOM sampling-step and resolution gates', 'Query unrounded HYCOM native-grid monthly vectors']:
            expect(links.get_by_role('link', name=name, exact=True)).to_be_visible()
        link.focus()
        page.keyboard.press('Enter')
        expect(page.get_by_role('heading', name='Indian SECC: finer-grid investigation')).to_be_visible(timeout=30000)
        expect(page.locator('.notice')).to_contain_text('No named-current width')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.screenshot(path=str(output/'card-to-map-320px.png'), full_page=True)
        assert not originals and not errors, (originals, errors)
        browser.close()
    result = {'status': 'PASS', 'exact_native_wasm_cases': 144, 'monthly_summaries': 12,
              'exact_native_grid_frames': [1, 8, 12],
              'step_comparisons': 72, 'keyboard_current_card_to_map': True,
              'phone_320px': True, 'automatic_original_requests': 0}
    (output/'result.json').write_bytes((json.dumps(result, indent=2)+'\n').encode())
    print(json.dumps(result))


if __name__ == '__main__':
    main()
