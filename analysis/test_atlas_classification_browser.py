"""Released classifications remain exact and do not imply route availability."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    entities={r['id']:r for r in json.loads(Path('almanac/release/v0.1.0/entities.json').read_text(encoding='utf-8'))}
    snapshot=json.loads(Path('research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))
    fields=['identity_level','source_kind','setting','time_behavior']
    for row in snapshot['entries']:
        for field in fields:
            assert row[field]==entities[row['id']].get(field, None if field=='source_kind' else 'unresolved'), (row['id'],field)
    currents=[r for r in snapshot['entries'] if r['type']=='named_current']
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('OSW_TEST_BROWSER',r'C:\Program Files\Google\Chrome\Application\chrome.exe'))
        page=browser.new_page(viewport={'width':320,'height':800})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#route-atlas',wait_until='networkidle')
        page.wait_for_function('document.querySelectorAll("#route-atlas-select option").length===101')
        for row in currents:
            page.locator('#route-atlas-select').select_option(row['id'])
            disclosure=page.locator('.route-atlas-classification')
            assert not disclosure.evaluate('(el)=>el.open')
            disclosure.locator('summary').focus()
            page.keyboard.press('Enter')
            assert disclosure.evaluate('(el)=>el.open')
            assert disclosure.locator('dt').all_text_contents()==['Inventory level','Inventory description','Setting','Time behavior']
            assert disclosure.locator('dd').all_text_contents()==[(row[field] or 'unresolved').replace('_',' ') for field in fields]
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),row['id']
        page.locator('#route-atlas-select').select_option('current:solomon-island-coastal-undercurrent')
        assert page.locator('#route-atlas-preview .route-map').count()==0
        proposed=next(r for r in currents if r['id']=='current:solomon-island-coastal-undercurrent')
        assert proposed['scope_notes'][0]['summary'] in page.locator('.route-atlas-scope-reviews').inner_text()
        page.locator('#route-atlas-select').select_option('current:agulhas')
        assert page.locator('#route-atlas-preview .route-map').is_visible()
        page.locator('#route-atlas-world').click()
        assert page.locator('#route-atlas-preview').is_hidden()
        assert not errors,errors
        browser.close()
    print('OK: 240 released classification records; all 100 current disclosures, keyboard, mobile reflow, pending and mapped routes')


if __name__=='__main__':
    main()
