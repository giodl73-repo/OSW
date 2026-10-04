"""Check separate-year frontal proxies stay distinct from SPC velocity geometry."""
import hashlib
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    read=lambda path:json.loads(Path(path).read_text(encoding='utf-8'))
    ident='south-pacific-eastern-front-reach-reference-path-candidate'
    candidate=read('research/'+ident+'.json')
    catalog=read('research/ocean-current-reference-path-candidates.json')
    assert candidate['candidate_comparison_group']=='osw_studied_reach_routes'
    assert ident not in catalog['reference_route_length_order']
    anchors=candidate['source_anchor_observations']
    assert [a['observed_period']['start'] for a in anchors]==['1994-02','1993-02']
    assert [a['longitude_latitude'] for a in anchors]==[[-103,-33.8],[-88,-34.5]]
    assert candidate['scenario_count']==27
    for scenario in candidate['scenarios']:
        assert scenario['coordinates_lon_lat'][0][0]==-103
        assert scenario['coordinates_lon_lat'][-1][0]==-88
    snapshot=read('research/ocean-motion-dashboard.json')
    row=next(r for r in snapshot['entries'] if r['id']=='current:south-pacific')
    assert row['latest_observation_date'] is None
    assert row['capabilities']['reference_route']==1
    assert hashlib.sha256(Path('research/ocean-current-almanac.json').read_bytes()).hexdigest()=='6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e'
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ['OSW_TEST_BROWSER'])
        page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Asouth-pacific#route-atlas',wait_until='networkidle')
        preview=page.locator('#route-atlas-preview')
        assert preview.locator('.route-map').is_visible()
        for text in ['1,400 km','1,300–1,500','Studied reach only','1994','1993','Frontal proxies are not velocity cores','not define an axis depth']:
            assert text in preview.inner_text(),text
        assert preview.locator('.route-atlas-state-links li').count()==1
        page.locator('#route-atlas').screenshot(path='figures/south-pacific-front-reach-review.png')
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#'+ident,wait_until='networkidle')
        card=page.locator('#'+ident)
        assert '1994-02 to 1994-04' in card.inner_text()
        assert '1993-02 to 1993-04' in card.inner_text()
        assert card.locator('a[href="https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2007GL030392"]').count()==1
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=south-pacific',wait_until='networkidle')
        assert page.locator('#season-play').is_disabled()
        assert page.locator('#season-map').is_visible()
        assert 'unknown' in page.locator('#season-length').inner_text()
        assert page.locator('.season-scale').is_hidden()
        assert not errors,errors
        browser.close()
    print('OK: 103/88 W frontal anchors, separate 1994/1993 sampling, no velocity-axis/depth/rank/date transfer, atlas and route cards, seasonal unknowns and mobile')


if __name__=='__main__':main()
