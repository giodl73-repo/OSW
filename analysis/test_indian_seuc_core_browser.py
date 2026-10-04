"""Spatial climatological core widths never become temporal or full widths."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    root=Path(__file__).resolve().parents[1]
    snapshot=json.loads((root/'research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))
    current=next(row for row in snapshot['entries'] if row['id']=='current:indian-south-equatorial-undercurrent')
    assert current['capabilities']['reference_route']==1
    assert current['capabilities']['scoped_width']==1
    assert current['latest_observation_date'] is None
    report=json.loads((root/'research/indian-seuc-mam-reach-reference-path-candidate.json').read_text(encoding='utf-8'))
    catalog=json.loads((root/'research/ocean-current-reference-path-candidates.json').read_text(encoding='utf-8'))
    row=next(r for r in catalog['candidates'] if r['current_id']=='indian-south-equatorial-undercurrent')
    assert row['id'] not in catalog['reference_route_length_order']
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('OSW_TEST_BROWSER',r'C:\Program Files\Google\Chrome\Application\chrome.exe'))
        page=browser.new_page(viewport={'width':1440,'height':1100})
        errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=indian-south-equatorial-undercurrent',wait_until='networkidle')
        page.wait_for_function('document.querySelector("#season-title").textContent.includes("spatial variation")')
        assert '169 km median across longitudes' in page.locator('#season-value').inner_text()
        assert '26–294 km spatial range' in page.locator('#season-value').inner_text()
        assert 'not fixed-depth full widths' in page.locator('#season-definition').inner_text()
        assert '2001-2018' in page.locator('#season-definition').inner_text()
        assert 'Bar scale' not in page.locator('#season-definition').inner_text()
        assert page.locator('#season-bar').is_hidden()
        assert page.locator('#season-play').is_disabled()
        assert page.locator('#season-map').is_visible()
        assert 'Annual length/width ranges' in page.locator('#season-range').inner_text()
        page.screenshot(path=str(root/'figures/indian-seuc-core-width-review.png'),full_page=True)
        page.locator('#season-current').select_option('northern-mediterranean')
        assert page.locator('#season-bar').is_visible()
        page.locator('#season-current').select_option('indian-south-equatorial-undercurrent')
        assert page.locator('#season-bar').is_hidden()
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Aindian-south-equatorial-undercurrent#route-atlas',wait_until='networkidle')
        page.wait_for_function('document.querySelector("#route-atlas-select").value==="current:indian-south-equatorial-undercurrent"')
        assert page.locator('#route-atlas-preview .route-map').is_visible()
        assert current['scope_notes'][0]['summary'] in page.locator('.route-atlas-scope-reviews').inner_text()
        x,y,w,h=map(float,page.locator('#route-atlas-map').get_attribute('viewBox').split())
        for lon,lat in report['coordinates_lon_lat']:
            assert x<=60+(lon+180)/360*1480<=x+w
            assert y<=90+(90-lat)/180*740<=y+h
        width=page.locator('#width-rows tr').filter(has_text='Indian Ocean South Equatorial Undercurrent')
        assert 'median across longitudes' in width.inner_text()
        assert 'spatial range; not seasonal extrema' in width.inner_text()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.set_viewport_size({'width':1440,'height':1100})
        page.locator('#route-atlas').screenshot(path=str(root/'figures/indian-seuc-atlas-reach-review.png'))
        page.locator('#route-atlas-world').click()
        assert page.locator('#route-atlas-preview').is_hidden()
        # Chromium's standalone SVG viewer can stall full-page capture; render
        # the same SVG as an image in a normal document for figure inspection.
        page.set_content(f'<img alt="Editorial route preview" src="http://127.0.0.1:8788/{report["figure"]}" style="width:100%;max-width:1100px">',wait_until='networkidle')
        page.screenshot(path=str(root/'figures/indian-seuc-reference-path-review.png'),full_page=True)
        assert not errors,errors
        browser.close()
    print('OK: Indian SEUC mapped reach, spatial core median/range, no annual/playback/full-width inference, current switch reset, global return and mobile reflow')


if __name__=='__main__':main()
