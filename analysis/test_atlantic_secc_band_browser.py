"""Reported latitude band keeps month precision and vertically complex flow."""
import copy, json, os
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
    root=Path(__file__).resolve().parents[1]
    snapshot=json.loads((root/'research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))
    row=next(r for r in snapshot['entries'] if r['id']=='current:atlantic-south-equatorial-countercurrent')
    assert row['capabilities']['scoped_width']==1
    assert row['capabilities']['reference_route']==0
    assert row['latest_observation_date'] is None
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ['OSW_TEST_BROWSER'])
        page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=atlantic-south-equatorial-countercurrent',wait_until='networkidle')
        page.wait_for_function('document.querySelector("#season-title").textContent==="Month-dated current band"')
        assert '220 km described meridional band span' in page.locator('#season-value').inner_text()
        assert '1994-03' in page.locator('#season-value').inner_text()
        for text in ['40 m','240 m','110 m','not an observed current center','basin-wide reversal']:
            assert text in page.locator('#season-definition').inner_text()
        assert page.locator('#season-play').is_disabled()
        assert page.locator('#season-bar').is_hidden()
        assert page.locator('#season-map').is_hidden()
        assert page.locator('#season-section-locator svg').is_visible()
        label=page.locator('#season-section-locator svg').get_attribute('aria-label')
        assert '1994-03 (month precision; exact days unresolved)' in label
        assert '30° W section, 8° S to 6° S' in label
        assert 'not a current axis' in label
        assert 'No annual minimum/maximum' in page.locator('#season-length').inner_text()
        assert 'phase=atlantic-secc-1994-03-described-band-span' in page.url
        page.locator('#season-current').select_option('atlantic-north-equatorial-undercurrent')
        assert page.locator('#season-bar').is_visible()
        assert page.locator('#season-section-locator').is_hidden()
        page.locator('#season-current').select_option('atlantic-south-equatorial-countercurrent')
        assert page.locator('#season-bar').is_hidden()
        page.screenshot(path=str(root/'figures/atlantic-secc-band-review.png'),full_page=True)
        page.locator('#season-atlas').click()
        page.wait_for_function('document.querySelector("#route-atlas-select").value==="current:atlantic-south-equatorial-countercurrent"')
        assert '220 km' in page.locator('.route-atlas-scope-reviews').inner_text()
        assert page.locator('#route-atlas-preview .route-map').count()==0
        assert page.locator('#route-atlas-preview .section-locator-map').is_visible()
        assert 'month precision; exact days unresolved' in page.locator('#route-atlas-status').inner_text()
        x,y,w,h=map(float,page.locator('#route-atlas-map').get_attribute('viewBox').split())
        for lat in [-8,-6]:
            assert x <= 60+(-30+180)/360*1480 <= x+w
            assert y <= 90+(90-lat)/180*740 <= y+h
        page.reload(wait_until='networkidle')
        assert page.locator('#route-atlas-preview .section-locator-map').is_visible()
        page.locator('#route-atlas-world').click()
        line=page.locator('#route-atlas-section-locators [data-current-id="current:atlantic-south-equatorial-countercurrent"]')
        line.focus();page.keyboard.press('Enter')
        assert page.locator('#route-atlas-select').input_value()=='current:atlantic-south-equatorial-countercurrent'
        page.locator('#route-atlas').screenshot(path=str(root/'figures/atlantic-secc-atlas-section-review.png'))
        widths=json.loads((root/'research/ocean-current-width-inventory.json').read_text(encoding='utf-8'))['measurements']
        band=next(r for r in widths if r['id']=='atlantic-secc-1994-03-described-band-span')
        assert page.evaluate('(r)=>currentSectionLocator.coordinates(r)',band)==[[-30,-8],[-30,-6]]
        other=next(r for r in widths if r['current_id']=='atlantic-north-equatorial-undercurrent')
        assert page.evaluate('(r)=>currentSectionLocator.coordinates(r)',other) is None
        for key,value in [('observed_month','1994-13'),('observed_period',{'start':'1994-03-01','end':'1994-03-31'}),('full_width_inference_eligible',True)]:
            invalid=copy.deepcopy(band);invalid[key]=value
            assert page.evaluate('(r)=>currentSectionLocator.coordinates(r)',invalid) is None
        for key,value in [('source_reported_center_latitude_degrees',-7),('source_reported_latitude_limits_degrees',[-6,-8]),('normalization_limits_are_observed_edges',True),('normalization_center_latitude_degrees',-6)]:
            invalid=copy.deepcopy(band);invalid['angular_span_conversion'][key]=value
            assert page.evaluate('(r)=>currentSectionLocator.coordinates(r)',invalid) is None
        width=page.locator('#width-rows tr').filter(has_text='Atlantic South Equatorial Countercurrent')
        assert 'not fixed-depth full width' in width.inner_text()
        page.locator('.route-atlas-scope-reviews a[data-atlas-current="current:atlantic-south-equatorial-undercurrent"]').focus()
        page.keyboard.press('Enter')
        assert page.locator('#route-atlas-select').input_value()=='current:atlantic-south-equatorial-undercurrent'
        assert page.locator('#route-atlas-preview .route-map').is_visible()
        page.set_viewport_size({'width':320,'height':800})
        page.locator('#route-atlas-select').select_option('current:atlantic-south-equatorial-countercurrent')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert not errors,errors
        browser.close()
    print('OK: reported-limit maps, month precision, keyboard/global/restore, computed-limit rejection, distinct SEUC navigation and mobile reflow; no full-width bar/axis/annual range')

if __name__=='__main__':main()
