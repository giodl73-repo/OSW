"""Verify MUC lower-core reach scope without merging incompatible width records."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
        page=browser.new_page();errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#route-atlas',wait_until='networkidle')
        page.locator('#route-atlas-select').select_option('current:mediterranean-undercurrent')
        page.locator('#route-atlas-preview').get_by_role('link',name='Full route card, measurements and sources').click()
        page.wait_for_function('location.hash === "#mediterranean-undercurrent-reach-reference-path-candidate"')
        card=page.locator('#mediterranean-undercurrent-reach-reference-path-candidate')
        assert card.locator('.route-map').is_visible()
        text=card.inner_text()
        for expected in ['300','200','950–1250 dbar','Excludes upstream Gibraltar','Not a full-current axis','meddy looping']:
            assert expected in text,expected
        assert abs(card.bounding_box()['y'])<30
        assert page.locator('#reference-route-rows tr').count()==37
        assert page.locator('#reference-route-rows a[href="#mediterranean-undercurrent-reach-reference-path-candidate"]').count()==0
        card.locator('.route-map').screenshot(path='figures/mediterranean-undercurrent-reach-reference-path-review.png')
        card.get_by_role('link',name='Back to global current map').click()
        assert page.url.endswith('#route-atlas')
        assert abs(page.locator('#route-atlas').bounding_box()['y'])<30
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=mediterranean-undercurrent',wait_until='networkidle')
        assert page.locator('#season-play').is_disabled()
        assert page.locator('#season-map').is_visible()
        assert 'Static route context' in page.locator('#season-map-note').inner_text()
        assert 'seasonal' in page.locator('#season-range').inner_text()
        assert page.locator('#season-phase option').count()==2
        assert 'one-sided core-to-offshore-edge span' in page.locator('#season-value').inner_text()
        snapshot=json.loads(Path('research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))
        row=next(r for r in snapshot['entries'] if r['id']=='current:mediterranean-undercurrent')
        assert row['capabilities']['reference_route']==1
        assert row['capabilities']['scope_notes']==1
        assert row['capabilities']['scoped_width']==2
        assert row['latest_observation_date'] is None
        assert not errors,errors
        browser.close()
    print('OK: MUC lower-core reach, map-card/global navigation, ordering exclusion, incompatible widths retained and seasonal playback disabled')

if __name__=='__main__':main()
