"""Explicit browser gate for all 72 paired source selections (after packaging)."""
import json
import os
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import numpy as np
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get('OSW_TEST_BASE_URL', 'http://127.0.0.1:8788')
SOURCE = ROOT/'research/source-data/hycom-south-indian-hydrography-2013'
FIELDS = ['water_u', 'water_v', 'water_temp', 'salinity']


def main():
    output = ROOT/'.pytest_cache/south-indian-hycom-2013/browser'
    output.mkdir(parents=True, exist_ok=True)
    doc = json.loads((SOURCE/'monthly-fields.json').read_bytes())
    with np.load(SOURCE/'monthly.npz', allow_pickle=False) as arrays:
        for f in FIELDS:
            actual = np.asarray([m['fields'][f] for m in doc['months']], dtype=float)
            np.testing.assert_array_equal(actual, arrays[f])
        np.testing.assert_array_equal(doc['latitude_degrees_north'], arrays['lat'])
        np.testing.assert_array_equal(doc['longitude_degrees_east'], arrays['lon'])
        np.testing.assert_array_equal(doc['depth_m'], arrays['depth'])
        np.testing.assert_array_equal([m['common_samples'] for m in doc['months']], arrays['common_samples'])
    errors, downloads = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page = browser.new_page(viewport={'width': 1120, 'height': 900})
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('request', lambda r: downloads.append(r.url) if r.url.endswith(('.zip', '.npz')) else None)
        page.goto(BASE+'/figures/south-indian-hydrography-2013/')
        expect(page.locator('#month')).to_be_enabled()
        expect(page.get_by_role('heading', name='South Indian Current: paired source profiles')).to_be_visible()
        expect(page.locator('.notice')).to_contain_text('No named-current width or axis')
        scales = {}
        for z in range(2):
            page.locator('#depth').select_option(str(z))
            for x in range(3):
                page.locator('#longitude').select_option(str(x))
                for mi, month in enumerate(doc['months']):
                    page.locator('#month').select_option(str(mi))
                    query=parse_qs(urlparse(page.url).query)
                    assert query['month']==[str(mi+1)]
                    assert float(query['depth'][0])==doc['depth_m'][z]
                    assert float(query['lon'][0])==doc['longitude_degrees_east'][x]
                    expect(page.locator('#status')).to_contain_text(f"{month['sample_days']} daily 00Z samples")
                    result = page.evaluate('''() => ({
                      cells:[...document.querySelectorAll('tbody tr')].map(r=>[...r.children].map(c=>c.textContent)),
                      scales:[...document.querySelectorAll('svg')].map(s=>[...s.querySelectorAll('text')].map(t=>t.textContent)),
                      paths:[...document.querySelectorAll('svg')].map(s=>s.lastElementChild.getAttribute('d'))
                    })''')
                    expected = [[lat, *[month['fields'][f][z][y][x] for f in FIELDS],
                                 month['common_samples'][z][y][x]] for y, lat in enumerate(doc['latitude_degrees_north'])]
                    assert len(result['cells']) == len(expected) == 326
                    for row, values in zip(result['cells'], expected):
                        for i, (text, v) in enumerate(zip(row, values)):
                            if v is None:
                                assert text == 'Missing'
                            else:
                                assert abs(float(text)-v) <= (0 if i == 5 else .500001e-6)
                    if z in scales:
                        assert result['scales'] == scales[z], 'Month or meridian changed a fixed scale'
                    else:
                        scales[z] = result['scales']
                    for f, path in zip(FIELDS, result['paths']):
                        values = [month['fields'][f][z][y][x] for y in range(326)]
                        valid = [v is not None for v in values]
                        assert path.count('M') == sum(v and (i == 0 or not valid[i-1]) for i,v in enumerate(valid))
                        assert path.count('M')+path.count('L') == sum(valid)
        permalink=page.locator('#permalink').get_attribute('href')
        page.goto(permalink)
        expect(page.locator('#month')).to_have_value('11')
        expect(page.locator('#depth')).to_have_value('1')
        expect(page.locator('#longitude')).to_have_value('2')
        page.locator('#month').select_option('5')
        page.go_back()
        expect(page.locator('#month')).to_have_value('11')
        page.go_forward()
        expect(page.locator('#month')).to_have_value('5')
        page.goto(BASE+'/figures/south-indian-hydrography-2013/?month=99&depth=999&lon=0')
        expect(page.locator('#route-note')).to_contain_text('Unavailable URL selections')
        expect(page.locator('#month')).to_have_value('0')
        expect(page.locator('#depth')).to_have_value('0')
        expect(page.locator('#longitude')).to_have_value('1')
        page.locator('#month').select_option('0')
        page.locator('#month').focus()
        page.keyboard.press('ArrowDown')
        page.keyboard.press('Tab')
        expect(page.locator('#month')).to_have_value('1')
        expect(page.locator('#depth')).to_be_focused()
        page.screenshot(path=str(output/'desktop.png'), full_page=True)
        page.set_viewport_size({'width': 320, 'height': 900})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('summary').click()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        expect(page.locator('.table-scroll')).to_have_attribute('tabindex', '0')
        for link in page.locator('main a').all():
            href = link.get_attribute('href')
            assert page.request.head(page.evaluate('(href)=>new URL(href,location.href).href', href)).ok
        page.screenshot(path=str(output/'phone.png'), full_page=True)
        assert not errors and not downloads
        browser.close()
    result = {'status': 'PASS', 'selections': 72, 'profiles': 288,
              'native_table_rows_checked': 72*326, 'json_npz_values_exact': True,
              'fixed_scales_and_missing_breaks': True, 'keyboard': True,
              'permalinks_reload_and_history': True, 'invalid_url_defaults_explained': True,
              'phone_320px': True, 'automatic_original_downloads': 0,
              'physical_width_admitted': False}
    (output/'result.json').write_bytes((json.dumps(result, indent=2)+'\n').encode())
    print(json.dumps(result))


if __name__ == '__main__':
    main()
