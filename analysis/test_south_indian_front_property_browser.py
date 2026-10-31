"""Every actual property case/mask, responsive chart, tables and shared state."""
import json
import os
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright, expect

from south_indian_front_property_query import ROOT, FOLDER, evidence

BASE = 'http://127.0.0.1:8788/' + FOLDER


def main():
    data, _, _ = evidence()
    output = ROOT/'.pytest_cache/south-indian-front-properties-2013/browser'
    output.mkdir(parents=True, exist_ok=True)
    errors = []; originals = []; selections = 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page = browser.new_page(viewport={'width': 1280, 'height': 1000})
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('request', lambda r: originals.append(r.url) if r.url.endswith(('.npz', '.zip', '.pdf', '.nc')) else None)
        page.goto(BASE);page.wait_for_function('window.oswPropertyReady', timeout=60000)
        for month in range(1, 13):
            page.locator('#month').select_option(str(month))
            for xi in range(3):
                page.locator('#longitude').select_option(str(xi))
                case = data['cases'][(month-1)*3+xi]
                assert page.evaluate('window.oswPropertySelection.case') == case
                assert page.locator('#nodes tr').count() == 326
                assert page.locator('#peaks tr').count() == len(case['surface_peaks'])
                peak_cells = page.locator('#peaks tr').evaluate_all('(rows)=>rows.map(r=>Array.from(r.cells).map(c=>c.textContent))')
                for p, cells in zip(case['surface_peaks'], peak_cells):
                    assert cells[0] == p['id'].split(':')[-1]
                    assert cells[3] == ' / '.join(f['status'] for f in p['flanks'])
                assert page.locator('#runs tr').count() == sum(len(w['runs']) for w in case['property_windows'])
                assert page.locator('svg circle[data-peak]').count() == sum(p['end_index']-p['start_index']+1 for p in case['surface_peaks'])
                for w in case['property_windows']:
                    key = w['criterion_id']
                    page.locator('#criterion').select_option(key)
                    assert page.evaluate('window.oswPropertySelection.window') == w
                    assert page.locator('#pairs tr').count() == len(w['peak_comparisons'])
                    assert page.locator('g[data-criterion="'+key+'"] path[data-native-index]').count() == sum(v is not False for v in w['membership'])
                    q = json.loads(parse_qs(urlparse(page.locator('#case-query').get_attribute('href')).query)['source-q'][0])
                    assert q == {'document': 'research/south-indian-2013-front-property-windows-v2.json',
                                 'pointer': '/cases', 'limit': 1, 'offset': (month-1)*3+xi}
                    selections += 1
                cells = page.locator('#nodes tr').evaluate_all('(rows)=>rows.map(r=>Array.from(r.cells).map(c=>c.textContent))')
                for i, cells in enumerate(cells):
                    assert abs(float(cells[0])-data['latitude_degrees_north'][i]) <= .00000051
                    expected = ['Unsupported' if w['membership'][i] is None else 'Yes' if w['membership'][i] else 'No' for w in case['property_windows']]
                    assert cells[2:] == expected
        page.locator('#month').select_option('4');page.locator('#longitude').select_option('1')
        page.locator('#criterion').select_option('stf_joint100')
        share = page.locator('#permalink').get_attribute('href')
        page.locator('#month').select_option('8');page.go_back()
        expect(page.locator('#month')).to_have_value('4')
        page.goto(share);page.wait_for_function('window.oswPropertyReady')
        expect(page.locator('#month')).to_have_value('4')
        page.locator('#month').focus();page.keyboard.press('ArrowDown')
        expect(page.locator('#month')).to_have_value('5')
        assert page.evaluate('window.oswPropertySelection.case.month') == 5
        page.locator('#plot').scroll_into_view_if_needed();page.screenshot(path=str(output/'desktop.png'))
        page.set_viewport_size({'width': 320, 'height': 1000})
        page.locator('#plot').scroll_into_view_if_needed();page.wait_for_timeout(200)
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert page.locator('svg text').evaluate_all('(ns)=>ns.every(n=>parseFloat(getComputedStyle(n).fontSize)*n.getBoundingClientRect().height/n.getBBox().height>=10)')
        page.screenshot(path=str(output/'phone.png'))
        page.goto(BASE+'?month=99&lon=0&criterion=invalid');page.wait_for_function('window.oswPropertyReady')
        expect(page.locator('#warnings')).to_contain_text('Unrecognized')
        expect(page.locator('#month')).to_have_value('1');expect(page.locator('#longitude')).to_have_value('1')
        expect(page.locator('#criterion')).to_have_value('stf_joint100')
        assert not errors and not originals, (errors, originals)
        browser.close()
    result = {'status': 'PASS', 'actual_cases': 36, 'criterion_selections': selections,
              'native_table_rows_checked': 11736, 'all_cases_masks_peaks_and_pairs_exact': True,
              'all_plateau_nodes_visible': True, 'keyboard_permalink_history': True,
              'phone320px': True, 'axis_text_at_least_10_css_pixels': True,
              'automatic_original_downloads': 0, 'front_identification_verified': False,
              'physical_width_admitted': False}
    (output/'result.json').write_bytes((json.dumps(result, indent=2)+'\n').encode())
    print(json.dumps(result))


if __name__ == '__main__':
    main()
