"""Source range chart, no invented midpoint/annual cycle, native/WASM parity."""
import json, os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_rust_query_browser import native
ROOT=Path(__file__).resolve().parents[1]

def main():
    inventory=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
    identifier='black-sea-rim-korotaev-2011-regional-width-range'
    query={'collection':'widths','filters':[{'field':'id','op':'eq','value':identifier}],'limit':10}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'),headless=True)
        page=browser.new_page(viewport={'width':1200,'height':950});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=black-sea-rim',wait_until='networkidle')
        page.wait_for_function("document.querySelector('#regional-width-range').hidden===false")
        assert page.locator('#season-title').inner_text()=='Regional width range'
        assert '40–80 km' in page.locator('#season-value').inner_text()
        assert 'No midpoint selected' in page.locator('#regional-width-range').inner_text()
        assert 'Not annual extrema' in page.locator('#regional-width-range svg').get_attribute('aria-label')
        assert page.locator('#regional-width-range svg text').all_text_contents()==['40 km','80 km','0 km','100 km']
        assert 'not a fixed measurement layer' in page.locator('#season-definition').inner_text()
        assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
        assert page.locator('#season-section-locator').is_hidden()
        assert page.locator('#season-play').is_disabled()
        assert 'not available' in page.locator('#season-range').inner_text()
        assert 'os-7-629-2011.pdf' in page.locator('#season-source a').get_attribute('href')
        page.screenshot(path=str(ROOT/'.pytest_cache/black-sea-range-review.png'))
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#regional-width-range').scroll_into_view_if_needed()
        assert page.locator('#regional-width-range svg text').first.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12')
        page.screenshot(path=str(ROOT/'.pytest_cache/black-sea-range-mobile-review.png'))
        # Switching removes stale range evidence; the earlier regional range also renders.
        page.locator('#season-current').select_option('labrador')
        assert page.locator('#regional-width-range').is_hidden()
        page.locator('#season-current').select_option('gaspe')
        assert '10–20 km' in page.locator('#regional-width-range').inner_text()
        page.locator('#season-current').select_option('black-sea-rim')
        page.locator('#season-atlas').click()
        page.wait_for_function('document.querySelector("#route-atlas-select").value==="current:black-sea-rim"')
        assert 'Black Sea Rim Current' in page.locator('#route-atlas-preview h3').inner_text()
        assert '40–80' in page.locator('#width-'+identifier).inner_text()
        assert page.locator('#width-rows tr').count()==len(inventory['measurements'])
        from urllib.parse import quote
        page.goto('http://127.0.0.1:8788/almanac/query.html?q='+quote(json.dumps(query)),wait_until='networkidle')
        page.wait_for_function('window.oswLastQueryResult?.rows?.length===1')
        wasm=page.evaluate('window.oswLastQueryResult')
        assert wasm['rows']==native(query)['rows']
        row=wasm['rows'][0];assert row['width_range_km']==[40,80] and row['approximate_width_km'] is None
        assert row['annual_extrema_eligible'] is False and row['section_geometry'] is None
        assert len(inventory['measurements'])==74
        # A mean offshore extent uses a distinct label and retains sampling metadata.
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=mindanao-current',wait_until='networkidle')
        page.wait_for_function("document.querySelector('#season-title').textContent==='Mean surface offshore extent'",timeout=90000)
        assert '250–300 km reported offshore extent' in page.locator('#season-value').inner_text()
        assert 'not a paired-boundary full width' in page.locator('#regional-width-range').inner_text()
        assert 'mean surface offshore extent' in page.locator('#regional-width-range svg').get_attribute('aria-label')
        assert page.locator('#regional-width-range svg text').evaluate_all('(es)=>es[0].getBoundingClientRect().right < es[1].getBoundingClientRect().left')
        assert 'January 2014' in page.locator('#season-definition').inner_text()
        assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
        assert page.locator('#season-play').is_disabled()
        assert page.locator('#season-section-locator').is_hidden()
        assert 'not available' in page.locator('#season-range').inner_text()
        assert 'not a fixed measurement layer' in page.locator('#season-definition').inner_text()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#regional-width-range').scroll_into_view_if_needed()
        page.screenshot(path=str(ROOT/'.pytest_cache/mindanao-extent-mobile.png'),full_page=True)
        page.locator('#season-atlas').click()
        page.wait_for_function('document.querySelector("#route-atlas-select").value==="current:mindanao-current"',timeout=90000)
        assert 'offshore extent of mean surface flow' in page.locator('#width-mindanao-schonau-2015-mean-surface-offshore-extent').inner_text()
        query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'mindanao-current'}],'limit':10}
        page.goto('http://127.0.0.1:8788/almanac/query.html?q='+quote(json.dumps(query)),wait_until='networkidle')
        page.wait_for_function('window.oswLastQueryResult?.rows?.length===1',timeout=90000)
        wasm=page.evaluate('window.oswLastQueryResult');assert wasm==native(query)
        row=wasm['rows'][0];assert row['width_range_km']==[250,300] and row['approximate_width_km'] is None
        context=row['mean_offshore_context'];assert context['campaign_context_is_mean_sampling_interval'] is False
        assert context['velocity_reference_depth_range_m']==[0,1000]
        assert context['source_date_discrepancy']
        assert not errors,errors
        browser.close()
    print('OK: Black Sea regional range, primary source, null midpoint, no seasonal/edge inference, responsive chart, cleanup and native/WASM query parity')

if __name__=='__main__':main()
