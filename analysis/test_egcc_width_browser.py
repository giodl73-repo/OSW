"""Keep the Cape Farewell threshold width separate from annual dimensions."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    inventory=json.loads(Path('research/ocean-current-width-inventory.json').read_text(encoding='utf-8'))
    row=next(r for r in inventory['measurements'] if r['current_id']=='east-greenland-coastal')
    assert row['approximate_width_km']==30 and row['velocity_threshold_fraction']==.15
    assert row['width_range_km'] is None and row['fixed_layer_bounds_m'] is None
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
        page=browser.new_page(viewport={'width':1440,'height':1000})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=east-greenland-coastal',wait_until='networkidle')
        page.wait_for_function('document.querySelector("#season-title").textContent === "Survey section observation"')
        assert page.locator('#season-phase option').count()==1
        assert page.locator('#season-play').is_disabled()
        assert '30 km' in page.locator('#season-value').inner_text()
        assert '15% of maximum inner jet velocity' in page.locator('#season-value').inner_text()
        definition=page.locator('#season-definition').inner_text()
        for text in ['75 m','exact section dates','fixed depth layer','annual or whole-current width']:
            assert text in definition,text
        assert page.locator('#season-source a').get_attribute('href')==row['source_url']
        page.screenshot(path='figures/egcc-threshold-width-review.png')
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert 'Static route context' in page.locator('#season-map-note').inner_text()
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Aeast-greenland-coastal#route-atlas',wait_until='networkidle')
        preview=page.locator('#route-atlas-preview')
        assert preview.locator('.route-map').is_visible()
        for text in ['800 km','800–900 km','Studied reach only','1000 km','63 N']:
            assert text in preview.inner_text(),text
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        preview.get_by_role('link',name='Full route card, measurements and sources').click()
        card=page.locator('#east-greenland-coastal-reach-reference-path-candidate')
        assert card.locator('.route-map').is_visible()
        assert page.locator('#reference-route-rows a[href="#east-greenland-coastal-reach-reference-path-candidate"]').count()==0
        page.set_viewport_size({'width':1440,'height':1000})
        card.locator('.route-map').screenshot(path='figures/egcc-studied-reach-review.png')
        assert not errors,errors
        browser.close()
    print('OK: EGCC 30 km local threshold width, campaign context, no annual playback, source link and mobile reflow')


if __name__=='__main__':
    main()
