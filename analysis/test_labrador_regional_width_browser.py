"""Regional prose width remains separate from section, seasonal and route geometry."""
import os,json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def main():
    inventory=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_text(encoding='utf-8'))
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'],headless=True)
        page=browser.new_page(viewport={'width':1200,'height':950});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=labrador',wait_until='networkidle')
        page.wait_for_function('document.querySelector("#season-title").textContent==="Regional width summary"',timeout=90000)
        assert page.locator('#season-title').inner_text()=='Regional width summary'
        assert 'about 50 km' in page.locator('#season-value').inner_text()
        assert 'bottom bathymetry' in page.locator('#season-definition').inner_text()
        assert 'No edge locator or full-width bar' in page.locator('#season-definition').inner_text()
        assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
        assert page.locator('#season-section-locator').is_hidden()
        assert page.locator('#season-play').is_disabled()
        assert 'Static route context' in page.locator('#season-map-note').inner_text()
        assert 'not available' in page.locator('#season-range').inner_text()
        assert '2008JC004859' in page.locator('#season-source').inner_text()
        page.screenshot(path=str(ROOT/'figures/labrador-regional-width-review.png'))
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#season-atlas').click()
        page.wait_for_function('document.querySelector("#route-atlas-select").value==="current:labrador"')
        assert 'Labrador Current' in page.locator('#route-atlas-preview h3').inner_text()
        row=page.locator('#width-labrador-thompson-2009-regional-width')
        assert '50' in row.inner_text() and 'published regional scalar width summary' in row.inner_text()
        assert page.locator('#width-rows tr').count()==len(inventory['measurements'])
        # The Gulf-of-Alaska typical scalar is not a winter section width.
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=alaska-coastal-gulf',wait_until='networkidle')
        page.wait_for_function('document.querySelector("#season-title").textContent==="Regional width summary"',timeout=90000)
        assert page.locator('#season-title').inner_text()=='Regional width summary'
        assert 'about 35 km' in page.locator('#season-value').inner_text()
        assert page.locator('#season-play').is_disabled()
        assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
        assert page.locator('#season-section-locator').is_hidden()
        assert 'not available' in page.locator('#season-range').inner_text()
        assert '2016JC012102' in page.locator('#season-source').inner_text()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#season-title').evaluate('(e)=>e.scrollIntoView({block:"start"})')
        page.screenshot(path=str(ROOT/'.pytest_cache/alaska-coastal-gulf-width-mobile.png'),full_page=True)
        from test_rust_query_browser import native, browser_query
        query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'alaska-coastal-gulf'}],'limit':10}
        page.goto('http://127.0.0.1:8788/almanac/query.html',wait_until='networkidle')
        page.wait_for_function('window.oswLastQueryResult',timeout=90000)
        result=browser_query(page,query);assert result==native(query)
        assert result['total']==1 and result['rows'][0]['approximate_width_km']==35
        assert result['rows'][0]['observed_period'] is None
        assert result['rows'][0]['width_range_km'] is None
        assert not errors,errors
        browser.close()
    print('OK: Labrador and Gulf-of-Alaska regional width summaries and native/WASM parity, scope, source, no annual/playback/edge inference, mapped atlas navigation, width table and mobile')
if __name__=='__main__':main()
