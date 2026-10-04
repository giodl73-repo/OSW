"""Inspect eastern naming-convention reach without importing ARC dimensions."""
import hashlib
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    read = lambda path: json.loads(Path(path).read_text(encoding='utf-8'))
    ident = 'south-indian-eastern-reach-reference-path-candidate'
    report = read('research/' + ident + '.json')
    catalog = read('research/ocean-current-reference-path-candidates.json')
    assert report['candidate_comparison_group'] == 'osw_studied_reach_routes'
    assert ident not in catalog['reference_route_length_order']
    assert report['scenario_count'] == 27
    for scenario in report['scenarios']:
        assert scenario['coordinates_lon_lat'][0][0] == 70
        assert scenario['coordinates_lon_lat'][-1][0] == 90
    row = next(r for r in read('research/ocean-motion-dashboard.json')['entries'] if r['id'] == 'current:south-indian')
    assert row['capabilities']['reference_route'] == 1
    assert row['latest_observation_date'] is None
    assert hashlib.sha256(Path('research/ocean-current-almanac.json').read_bytes()).hexdigest() == '6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e'
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=os.environ['OSW_TEST_BROWSER'])
        page = browser.new_page(viewport={'width':1440,'height':1000})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Asouth-indian#route-atlas', wait_until='networkidle')
        preview = page.locator('#route-atlas-preview')
        assert preview.locator('.route-map').is_visible()
        for text in ['1,700 km','1,600–1,800','Studied reach only','27/27 declared scenarios','all route latitudes','not a fixed-depth axis']:
            assert text.lower() in preview.inner_text().lower(), text
        assert preview.locator('.route-atlas-state-links li').count() == 2
        assert preview.locator('.route-atlas-scope-reviews a[data-atlas-current="current:agulhas-return"]').count() == 1
        assert page.locator('#reference-route-rows a[href="#' + ident + '"]').count() == 0
        page.locator('#route-atlas').screenshot(path='figures/south-indian-eastern-reach-review.png')
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.locator('#route-atlas-world').click()
        assert page.locator('#route-atlas-map').get_attribute('viewBox') == '60 90 1480 740'
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=south-indian', wait_until='networkidle')
        assert page.locator('#season-play').is_disabled()
        assert page.locator('#season-map').is_visible()
        assert 'unknown' in page.locator('#season-length').inner_text()
        assert page.locator('.season-scale').is_hidden()
        assert not errors, errors
        browser.close()
    print('OK: 70–90 E fixed gates, 27 scenarios, studied reach/no rank or date transfer, atlas map/scope/state links, seasonal unknowns and mobile')


if __name__ == '__main__':
    main()
