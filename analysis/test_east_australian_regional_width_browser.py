"""EAC typical width keeps influence scales and depth extent separate."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'],headless=True)
        page=browser.new_page(viewport={'width':860,'height':1050});errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=east-australian',wait_until='networkidle')
        assert page.locator('#season-title').inner_text()=='Regional width summary'
        assert 'about 30 km' in page.locator('#season-value').inner_text()
        assert '200 m depth extent' in page.locator('#season-definition').inner_text()
        assert 'does not specify a fixed depth' in page.locator('#season-definition').inner_text()
        assert '100 km strong-influence width' in page.locator('#season-definition').inner_text()
        assert 'seasonal range' in page.locator('#season-definition').inner_text()
        assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
        assert page.locator('#season-section-locator').is_hidden()
        assert page.locator('#season-play').is_disabled()
        assert 'not a 30-100 km seasonal range' in page.locator('#season-range').inner_text()
        page.locator('#season-atlas').click()
        page.wait_for_function('document.querySelector("#route-atlas-select").value==="current:east-australian"')
        record=page.locator('.atlas-width-record[data-measurement-id="east-australian-imos-typical-regional-width"]')
        record.locator('summary').click()
        assert '30 km' in record.inner_text()
        assert '100 km strong-influence width' in record.inner_text()
        assert '200 m depth extent' in record.inner_text()
        record.screenshot(path=str(ROOT/'figures/east-australian-regional-width-review.png'))
        assert page.locator('#route-atlas-preview .route-map').is_visible()
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert not errors,errors;browser.close()
    print('OK: EAC 30 km summary, distinct influence scale and depth extent, no annual/edge/playback inference, mapped atlas and mobile')


if __name__=='__main__':main()
