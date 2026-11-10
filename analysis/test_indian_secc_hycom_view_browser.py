"""Manual browser gate for the standalone finer-grid source investigation.

Run after acquisition, offline source reconstruction, diagnostics and view build.
"""
import hashlib
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get('OSW_TEST_BASE_URL', 'http://127.0.0.1:8788')


def main():
    output = ROOT/'.pytest_cache/indian-secc-hycom-2013/browser'
    output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((ROOT/'figures/indian-secc-hycom-2013/view.json').read_bytes())
    errors, original_requests = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page = browser.new_page(viewport={'width': 1120, 'height': 900})
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('request', lambda r: original_requests.append(r.url) if r.url.endswith(('.zip', '.npz')) else None)
        page.goto(BASE+'/figures/indian-secc-hycom-2013/')
        expect(page.get_by_role('heading', name='Indian SECC: finer-grid investigation')).to_be_visible()
        for month in manifest['months']:
            m = month['month']
            page.locator('#month').select_option(str(m))
            page.wait_for_function('document.querySelector("#map").complete && document.querySelector("#map").naturalWidth>0')
            expect(page.locator('#summary')).to_contain_text(f'{month["sample_days"]} of {month["calendar_days"]} daily 00Z samples')
            expect(page.locator('#summary')).to_contain_text(f'{month["stronger_candidates"]} also pass')
            assert page.locator('#map').get_attribute('src') == month['image']
            image_response = page.request.get(BASE+'/figures/indian-secc-hycom-2013/'+month['image'])
            assert image_response.ok and hashlib.sha256(image_response.body()).hexdigest() == month['image_pin']['sha256']
        page.locator('#month').focus()
        page.keyboard.press('Home')
        page.keyboard.press('ArrowDown')
        page.keyboard.press('Tab')
        expect(page.locator('#month')).to_have_value('2')
        page.screenshot(path=str(output/'desktop.png'), full_page=True)
        page.set_viewport_size({'width': 320, 'height': 900})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        expect(page.locator('.notice')).to_contain_text('No named-current width')
        for link in page.locator('main a').all():
            href = link.get_attribute('href')
            if href and not href.startswith('https://'):
                assert page.request.head(page.evaluate('(href)=>new URL(href,location.href).href', href)).ok
        page.screenshot(path=str(output/'phone.png'), full_page=True)
        assert not errors and not original_requests
        browser.close()
    result = {'status': 'PASS', 'months': 12, 'native_grid_images_exact': True,
              'keyboard': True, 'phone_320px': True, 'automatic_original_downloads': 0,
              'named_current_width_admitted': False}
    (output/'result.json').write_bytes((json.dumps(result, indent=2)+'\n').encode())
    print(json.dumps(result))


if __name__ == '__main__':
    main()
