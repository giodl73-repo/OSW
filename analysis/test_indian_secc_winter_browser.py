"""Winter surface reach must stay separate from annual and subsurface dimensions."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
    root=Path(__file__).resolve().parents[1]
    data=json.loads((root/'research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))
    row=next(r for r in data['entries'] if r['id']=='current:indian-south-equatorial-countercurrent')
    assert row['capabilities']['reference_route']==1
    assert row['capabilities']['scoped_width']==0
    assert row['latest_observation_date'] is None
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ['OSW_TEST_BROWSER'])
        page=browser.new_page(viewport={'width':1440,'height':1100}); errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=indian-south-equatorial-countercurrent',wait_until='networkidle')
        page.wait_for_function('document.querySelector("#season-value").textContent.includes("December-March")')
        assert 'eastward' in page.locator('#season-value').inner_text()
        assert 'Width: unknown' in page.locator('#season-definition').inner_text()
        assert 'wind-slip-corrected' in page.locator('#season-definition').inner_text()
        assert 'annual' in page.locator('#season-range').inner_text()
        assert '4,400 km' in page.locator('#season-length').inner_text()
        assert 'editorial sensitivity envelope' in page.locator('#season-length').inner_text()
        assert page.locator('#season-play').is_disabled()
        assert page.locator('#season-bar').is_hidden()
        assert page.locator('#season-map').is_visible()
        page.screenshot(path=str(root/'figures/indian-secc-winter-season-review.png'),full_page=True)
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Aindian-south-equatorial-countercurrent#route-atlas',wait_until='networkidle')
        page.wait_for_function('document.querySelector("#route-atlas-select").value==="current:indian-south-equatorial-countercurrent"')
        assert page.locator('#route-atlas-preview .route-map').is_visible()
        assert row['scope_notes'][0]['summary'] in page.locator('.route-atlas-scope-reviews').inner_text()
        assert page.locator('#width-rows tr').filter(has_text='Indian Ocean South Equatorial Countercurrent').count()==0
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.set_viewport_size({'width':1440,'height':1100})
        page.locator('#route-atlas').screenshot(path=str(root/'figures/indian-secc-winter-atlas-review.png'))
        related=page.locator('.route-atlas-scope-reviews a[data-atlas-current="current:indian-south-equatorial-undercurrent"]')
        related.focus(); page.keyboard.press('Enter')
        assert page.locator('#route-atlas-select').input_value()=='current:indian-south-equatorial-undercurrent'
        page.locator('#route-atlas-world').click()
        assert page.locator('#route-atlas-preview').is_hidden()
        assert not errors,errors
        browser.close()
    print('OK: winter surface route, unknown width, no annual/playback inference, separate SEUC navigation and mobile reflow')

if __name__=='__main__': main()
