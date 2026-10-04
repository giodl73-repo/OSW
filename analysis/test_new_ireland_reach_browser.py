"""Verify NICU regional reach without transferring modeled downstream paths."""
import json,hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    ledger=Path('research/ocean-current-almanac.json')
    assert hashlib.sha256(ledger.read_bytes()).hexdigest()=='6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e'
    r=json.loads(Path('research/new-ireland-coastal-undercurrent-reference-path-candidate.json').read_text(encoding='utf-8'))
    assert r['reported_approximate_reference_path_km']==400 and r['reported_scenario_range_km']==[300,500]
    assert r['scenario_count']==81 and r['candidate_comparison_group']=='osw_studied_reach_routes'
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
        page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Anew-ireland-coastal-undercurrent#route-atlas',wait_until='networkidle')
        preview=page.locator('#route-atlas-preview')
        assert preview.locator('.route-map').is_visible()
        for text in ['400 km','300–500 km','Studied reach only','retroflection','whole-current origin','NASA surface observation']:
            assert text in preview.inner_text(),text
        assert page.locator('#reference-route-rows a[href="#new-ireland-coastal-undercurrent-reference-path-candidate"]').count()==0
        preview.get_by_role('link',name='Full route card, measurements and sources').click()
        card=page.locator('#new-ireland-coastal-undercurrent-reference-path-candidate')
        assert card.locator('.route-map').is_visible()
        assert 'Subsurface thermocline' in card.inner_text()
        assert card.locator(f'a[href="{r["source_url"]}"]').count()>=1
        card.locator('.route-map').screenshot(path='figures/new-ireland-coastal-undercurrent-route-review.png')
        page.set_viewport_size({'width':320,'height':800})
        card.get_by_role('link',name='Back to global current map').click()
        page.locator('#route-atlas-select').select_option('current:new-ireland-coastal-undercurrent')
        assert preview.locator('.route-map').is_visible()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=new-ireland-coastal-undercurrent',wait_until='networkidle')
        assert page.locator('#season-play').is_disabled()
        assert 'width' in page.locator('#season-value').inner_text().lower()
        assert 'Static route context' in page.locator('#season-map-note').inner_text()
        assert not errors,errors
        browser.close()
    print('OK: NICU 400 km regional reach, 81 scenarios, subsurface/model scope, no ranking transfer, static seasonal context and mobile reflow')


if __name__=='__main__':main()
