"""Check general angular summaries do not become measured or seasonal footprints."""
import os,json
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ['OSW_TEST_BROWSER'])
        page=browser.new_page(viewport={'width':1440,'height':1000})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        for side in ['north','south']:
            ident=f'pacific-{side}-subsurface-countercurrent'
            record=ident+'-rowe-2000-general-angular-width'
            page.goto('http://127.0.0.1:8788/almanac/seasons.html?current='+ident+'&phase='+record,wait_until='networkidle')
            page.wait_for_function('document.querySelector("#season-phase").options.length===1')
            assert page.locator('#season-title').inner_text()=='General jet width summary'
            assert '2° latitude, approximately 220 km' in page.locator('#season-value').inner_text()
            assert 'not independent jet measurements' in page.locator('#season-definition').inner_text()
            assert 'not an observed location' in page.locator('#season-definition').inner_text()
            assert page.locator('#season-play').is_disabled()
            assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
            assert page.locator('#season-section-locator').is_hidden()
            assert 'Static route context' in page.locator('#season-map-note').inner_text()
            assert 'shared across' in page.locator('#season-range').inner_text()
            page.reload(wait_until='networkidle')
            assert record in page.url
            assert '220 km' in page.locator('#season-value').inner_text()
            page.set_viewport_size({'width':320,'height':800})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.locator('#season-atlas').click()
            page.wait_for_function('(id)=>document.querySelector("#route-atlas-select").value===id',arg='current:'+ident)
            assert 'two jet records share one source claim' in page.locator('.route-atlas-scope-reviews').inner_text()
            table=page.locator('#width-'+record)
            assert '2° latitude; shared general summary' in table.inner_text()
            assert 'not two independent measurements' in table.inner_text()
            assert page.locator('#width-rows tr').count()==len(json.loads(Path('research/ocean-current-width-inventory.json').read_text(encoding='utf-8'))['measurements'])
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.set_viewport_size({'width':1440,'height':1000})
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=pacific-north-subsurface-countercurrent',wait_until='networkidle')
        page.wait_for_function('document.querySelector("#season-phase").options.length===1')
        page.screenshot(path=str(Path('figures/tsuchiya-angular-width-review.png')))
        assert not errors,errors
        browser.close()
    print('OK: both shared angular summaries, conversion labels, disabled playback, no measured-edge locator/bar, static route context, saved views and mobile reflow')


if __name__=='__main__':main()
