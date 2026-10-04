"""Navigate each saved surface line without merging dates or identity scopes."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    snapshot=json.loads(Path('research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))
    row=next(r for r in snapshot['entries'] if r['id']=='current:gulf-stream-system')
    features=[f for f in row['map_features'] if f.get('geometry_id')]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('OSW_TEST_BROWSER',r'C:\Program Files\Google\Chrome\Application\chrome.exe'))
        page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#route-atlas',wait_until='networkidle')
        assert page.locator('#route-atlas-dated-lines path').count()==3
        preview=page.locator('#route-atlas-preview')
        for feature in features:
            mark=page.locator(f'#route-atlas-dated-lines [data-geometry-id="{feature["geometry_id"]}"]')
            assert feature['observation_date'] in mark.get_attribute('aria-label')
            mark.focus();page.keyboard.press('Enter')
            section=preview.locator('.route-atlas-dated-preview')
            assert section.locator('svg').is_visible()
            assert feature['note'] in section.inner_text()
            assert section.locator(f'a[href="../{feature["receipt_file"]}"]').count()==1
            assert section.locator(f'a[href="{feature["source_url"]}"]').count()==1
            assert section.locator(f'button[data-geometry-id="{feature["geometry_id"]}"]').get_attribute('aria-pressed')=='true'
            assert preview.locator('.route-map').count()==0
            assert preview.locator('.route-atlas-components li').count()==3
            shared=preview.locator('[data-atlas-share]').get_attribute('href')
            assert 'atlas-geometry='+feature['geometry_id'].replace(':','%3A') in shared
            fresh=browser.new_page();fresh.goto(shared,wait_until='networkidle')
            assert fresh.locator(f'.route-atlas-dated-preview button[data-geometry-id="{feature["geometry_id"]}"]').get_attribute('aria-pressed')=='true'
            fresh.close()
        page.locator('#route-atlas').screenshot(path='figures/atlas-dated-surface-card-review.png')
        page.set_viewport_size({'width':320,'height':800})
        for feature in features:
            preview.locator(f'.route-atlas-dated-preview button[data-geometry-id="{feature["geometry_id"]}"]').click()
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            assert feature['observation_date'] in page.locator('#route-atlas-status').inner_text()
        page.locator('#route-atlas-world').click()
        assert preview.is_hidden() and 'atlas-geometry' not in page.url
        assert page.locator('#route-atlas-map').get_attribute('viewBox')=='60 90 1480 740'
        page.locator('#route-atlas-select').select_option('current:gulf-stream')
        assert preview.locator('.route-atlas-dated-preview').count()==0
        assert 'source-reported length is available' in preview.inner_text()
        assert not errors,errors
        browser.close()
    print('OK: three dated surface-line selections, dates/methods/receipts, exact shared geometry, component links, mobile and global return; no identity transfer')


if __name__=='__main__':
    main()
