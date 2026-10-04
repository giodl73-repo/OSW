"""Verify branch-profile scope in width table, seasonal inspector and dashboard."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
        page=browser.new_page();errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#width-title',wait_until='networkidle')
        row=page.locator('#width-north-cape-northern-2007-profile-scale')
        assert 'About 8 km fitted profile scale (not full width)' in row.inner_text()
        assert 'Northern branch' in row.inner_text()
        assert 'Composite vertical support unresolved' in row.inner_text()
        assert '15 crossings' in row.inner_text()
        assert page.locator('#width-rows tr').count()==9
        assert '7 of 100' in page.locator('#width-status').inner_text()
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=north-cape',wait_until='networkidle')
        assert '8 km fitted profile scale (not full width)' in page.locator('#season-value').inner_text()
        assert page.locator('#season-play').is_disabled()
        assert page.locator('#season-bar').is_hidden()
        assert 'not a seasonal pair' in page.locator('#season-range').inner_text()
        assert page.locator('#season-map').is_visible()
        assert 'Static route context' in page.locator('#season-map-note').inner_text()
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=northern-mediterranean',wait_until='networkidle')
        assert page.locator('#season-play').is_enabled()
        assert page.locator('#season-bar').is_visible()
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#route-atlas',wait_until='networkidle')
        page.locator('#route-atlas-select').select_option('current:north-cape')
        page.locator('#route-atlas-preview').get_by_role('link',name='Full route card, measurements and sources').click()
        page.wait_for_function('location.hash === "#north-cape-northern-reach-reference-path-candidate"')
        card=page.locator('#north-cape-northern-reach-reference-path-candidate')
        assert card.locator('.route-map').is_visible()
        assert 'Northern branch' in card.inner_text()
        assert '200' in card.inner_text() and '300' in card.inner_text()
        assert page.locator('#reference-route-rows tr').count()==37
        assert page.locator('#reference-route-rows [href="#north-cape-northern-reach-reference-path-candidate"]').count()==0
        card.locator('.route-map').screenshot(path='figures/north-cape-northern-reach-reference-path-review.png')
        card.get_by_role('link',name='Back to global current map').click()
        assert page.url.endswith('#route-atlas')
        snapshot=json.loads(Path('research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))
        row=next(r for r in snapshot['entries'] if r['id']=='current:north-cape')
        assert row['capabilities']['scoped_width']==1
        assert row['capabilities']['scope_notes']==1
        assert row['latest_observation_date'] is None
        assert not errors,errors
        browser.close()
    print('OK: North Cape profile scale, unresolved depth/dates, no seasonal playback/full-width bar; existing seasonal pilot retained')

if __name__=='__main__':main()
