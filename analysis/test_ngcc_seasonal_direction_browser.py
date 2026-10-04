"""Check local seasonal direction, exception handling, and atlas navigation."""
import copy
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    audit = json.loads(Path('research/new-guinea-coastal-current-seasonal-direction-scope-audit.json').read_text(encoding='utf-8'))
    assert [p['calendar_months'] for p in audit['phases']] == [[11,12,1,2,3,4], [5,6,7,8,9,10], None]
    assert [p['playback_eligible'] for p in audit['phases']] == [True,True,False]
    for phase in audit['phases']:
        assert phase['site_lon_lat'] == [141.4,-1.7]
        assert phase['geometry_role'] == 'local_direction_symbol_not_current_axis'
        for key in ['length_km','width_km','route_coordinates','annual_length_range_km','annual_width_range_km']:
            assert phase[key] is None
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=os.environ['OSW_TEST_BROWSER'])
        page = browser.new_page(viewport={'width':1280,'height':950})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=new-guinea-coastal-current', wait_until='networkidle')
        assert page.locator('#season-phase option').count() == 3
        assert page.locator('#season-direction').is_visible()
        assert page.locator('#season-map').is_hidden()
        assert page.locator('.season-scale').is_hidden()
        assert 'southeastward' in page.locator('#season-value').inner_text()
        assert page.locator('#season-direction-months span').all_text_contents() == ['Nov','Dec','Jan','Feb','Mar','Apr']
        assert 'unknown' in page.locator('#season-length').inner_text()
        assert 'July 2016–March 2017' in page.locator('#season-definition').inner_text()
        page.locator('#season-phase').select_option('1')
        assert 'northwestward' in page.locator('#season-value').inner_text()
        assert '225' in page.locator('#season-direction-arrow').get_attribute('transform')
        page.locator('#season-phase').select_option('2')
        assert 'exception' in page.locator('#season-title').inner_text()
        assert page.locator('#season-direction-arrow').get_attribute('visibility') == 'hidden'
        assert page.locator('#season-direction-months span').count() == 0
        page.locator('#season-play').click()
        page.wait_for_function('document.getElementById("season-phase").value === "0"')
        page.wait_for_function('document.getElementById("season-phase").value === "1"')
        page.wait_for_function('document.getElementById("season-phase").value === "0"')
        page.locator('#season-play').click()
        page.locator('#season-current').select_option('somali')
        assert page.locator('#season-direction').is_hidden()
        assert page.locator('#season-map').is_visible()
        assert page.locator('#season-play').is_enabled()
        page.locator('#season-current').select_option('atlantic-north-equatorial-countercurrent')
        assert page.locator('#season-play').is_disabled()
        page.locator('#season-current').select_option('new-guinea-coastal-current')
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path='figures/ngcc-seasonal-direction-review.png', full_page=True)
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Anew-guinea-coastal-current#route-atlas', wait_until='networkidle')
        assert 'Local upper-ocean direction composite' in page.locator('.route-atlas-scope-reviews').inner_text()
        assert page.locator('#route-atlas-preview .route-map').count() == 0
        assert page.locator('.route-atlas-scope-reviews a[data-atlas-current="current:new-guinea-coastal-undercurrent"]').count() == 1
        proposal = page.locator('#inventory-addition-new-guinea-coastal-intermediate')
        assert 'no whole-current length or rank admitted' in proposal.inner_text()
        assert proposal.locator(f'a[href="{audit["source_url"]}"]').count() == 1
        assert not errors, errors
        altered = copy.deepcopy(audit)
        altered['phases'][2]['playback_eligible'] = True
        page.route('**/new-guinea-coastal-current-seasonal-direction-scope-audit.json', lambda route: route.fulfill(json=altered))
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=new-guinea-coastal-current', wait_until='networkidle')
        assert page.locator('#season-loading').inner_text() == 'Invalid local direction evidence'
        assert page.locator('#season-direction').is_hidden()
        browser.close()
    print('OK: NGCC month windows, no dimensions/axis, separate El Niño exception, exception excluded from playback, context cleanup, atlas scope links and 320 px layout')


if __name__ == '__main__':
    main()
