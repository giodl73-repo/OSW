"""Browse ledger components without inventing aggregate route measurements."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    catalog=json.loads(Path('research/ocean-current-reference-path-candidates.json').read_text(encoding='utf-8'))
    families=[row for row in catalog['remaining_current_decisions'] if row['known_component_currents']]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
        page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#route-atlas',wait_until='networkidle')
        page.wait_for_function('document.querySelectorAll("#route-atlas-select option").length===101')
        total=0
        for family in families:
            ident='current:'+family['current_id']
            page.locator('#route-atlas-select').select_option(ident)
            preview=page.locator('#route-atlas-preview')
            assert 'do not sum overlapping routes' in preview.inner_text()
            assert preview.locator('.route-atlas-components li').count()==len(family['known_component_currents'])
            assert preview.locator('.route-map').count()==0
            assert 'continuous family or system route' in page.locator('#route-atlas-status').inner_text()
            for member in family['known_component_currents']:
                child='current:'+member['current_id']
                anchor=preview.locator(f'.route-atlas-components a[data-atlas-current="{child}"]')
                url=anchor.get_attribute('href');assert 'atlas-feature=' in url and '#route-atlas' in url
                anchor.focus();page.keyboard.press('Enter')
                assert page.locator('#route-atlas-select').input_value()==child
                assert page.locator('.route-atlas-related').count()==0 or preview.locator('.route-atlas-components').count()==1
                preview.locator(f'.route-atlas-parent-families a[data-atlas-current="{ident}"]').click()
                assert page.locator('#route-atlas-select').input_value()==ident
                total+=1
        page.set_viewport_size({'width':320,'height':800})
        page.locator('#route-atlas-select').select_option('current:equatorial-undercurrent')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        preview.locator('.route-atlas-components a[data-atlas-current="current:atlantic-equatorial-undercurrent"]').click()
        assert preview.locator('.route-map').is_visible()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#route-atlas-world').click()
        assert page.locator('.route-atlas-related').count()==0
        assert preview.is_hidden()
        page.set_viewport_size({'width':1440,'height':1000})
        page.locator('#route-atlas-select').select_option('current:gulf-stream-system')
        assert 'source-reported length available' in preview.inner_text()
        page.locator('#route-atlas').screenshot(path='figures/atlas-component-navigation-review.png')
        page.locator('#route-atlas-select').select_option('current:gulf-stream')
        assert 'source-reported length is available' in preview.inner_text()
        assert 'length and route remain unresolved' not in page.locator('#route-atlas-status').inner_text()
        assert not errors,errors
        browser.close()
    print(f'OK: {len(families)} family/system records, {total} component links, keyboard descent, parent return, no aggregate measurements and mobile reflow')


if __name__=='__main__':main()
