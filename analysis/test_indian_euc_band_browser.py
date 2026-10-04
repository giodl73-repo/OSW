"""Dated local band dimensions never become full width or seasonal geometry."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    root=Path(__file__).resolve().parents[1]
    snapshot=json.loads((root/'research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))
    row=next(r for r in snapshot['entries'] if r['id']=='current:indian-equatorial-undercurrent')
    assert row['capabilities']['scoped_width']==1
    assert row['capabilities']['reference_route']==0
    assert row['latest_observation_date']=='2017-03-03'
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('OSW_TEST_BROWSER',r'C:\Program Files\Google\Chrome\Application\chrome.exe'))
        page=browser.new_page(viewport={'width':1440,'height':1000})
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=indian-equatorial-undercurrent',wait_until='networkidle')
        page.wait_for_function('document.querySelector("#season-title").textContent === "Dated subsurface band"')
        assert '300 km described meridional band span' in page.locator('#season-value').inner_text()
        assert '80–150 m' in page.locator('#season-definition').inner_text()
        assert 'Full-width bar omitted' in page.locator('#season-definition').inner_text()
        assert page.locator('#season-bar').is_hidden()
        assert page.locator('#season-play').is_disabled()
        assert page.locator('#season-map').is_hidden()
        assert page.locator('#season-section-locator svg').is_visible()
        assert '1.2° S to 1.5° N' in page.locator('#season-section-locator').inner_text()
        assert 'not a current axis' in page.locator('#season-section-locator svg').get_attribute('aria-label')
        # Switching to an unrelated current must clear the dated section.
        page.locator('#season-current').select_option('monsoon')
        assert page.locator('#season-section-locator').is_hidden()
        page.locator('#season-current').select_option('indian-equatorial-undercurrent')
        assert 'unknown' in page.locator('#season-length').inner_text()
        assert page.locator('#season-source a').get_attribute('href').endswith('noaa_64055_DS1.pdf')
        page.screenshot(path=str(root/'figures/indian-euc-dated-band-review.png'),full_page=True)
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Aindian-equatorial-undercurrent#route-atlas',wait_until='networkidle')
        page.wait_for_function('document.querySelector("#route-atlas-select").value === "current:indian-equatorial-undercurrent"')
        assert row['scope_notes'][0]['summary'] in page.locator('.route-atlas-scope-reviews').inner_text()
        assert page.locator('#route-atlas-preview .route-map').count()==0
        assert page.locator('#route-atlas-preview .section-locator-map').is_visible()
        assert 'dated section latitude-span locator' in page.locator('#route-atlas-status').inner_text()
        x,y,w,h=map(float,page.locator('#route-atlas-map').get_attribute('viewBox').split())
        for lat in [-1.2,1.5]:
            assert x <= 60+(90+180)/360*1480 <= x+w
            assert y <= 90+(90-lat)/180*740 <= y+h
        url=page.locator('#route-atlas-preview [data-atlas-share]').get_attribute('href')
        page.reload(wait_until='networkidle')
        assert page.locator('#route-atlas-preview .section-locator-map').is_visible()
        assert page.url==url
        page.locator('#route-atlas-world').click()
        assert page.locator('#route-atlas-preview').is_hidden()
        line=page.locator('#route-atlas-section-locators [data-current-id="current:indian-equatorial-undercurrent"]')
        assert line.get_attribute('role')=='button'
        line.focus();page.keyboard.press('Enter')
        assert page.locator('#route-atlas-select').input_value()=='current:indian-equatorial-undercurrent'
        assert page.locator('#route-atlas-preview .section-locator-map').is_visible()
        page.set_viewport_size({'width':1440,'height':1000})
        page.locator('#route-atlas').screenshot(path=str(root/'figures/indian-euc-atlas-section-review.png'))
        data=json.loads((root/'research/ocean-current-width-inventory.json').read_text(encoding='utf-8'))
        band=next(r for r in data['measurements'] if r['phase_kind']=='dated_band_section')
        assert page.evaluate('(row)=>currentSectionLocator.coordinates(row)',band)==[[90,-1.2],[90,1.5]]
        band['subsurface_band_context']['paired_velocity_edges_diagnosed']=True
        assert page.evaluate('(row)=>currentSectionLocator.coordinates(row)',band) is None
        page.set_viewport_size({'width':320,'height':800})
        widthrow=page.locator('#width-rows tr').filter(has_text='Indian Ocean Equatorial Undercurrent')
        assert 'described subsurface band span (not full width)' in widthrow.inner_text()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert not errors,errors
        browser.close()
    print('OK: dated section maps, latitude support, deep-link restore, keyboard/global return, invalid role rejection, no stale section/full-width bar/route/seasonal playback and mobile reflow')


if __name__=='__main__':main()
