"""Verify atlas highlights content changes using the dashboard's shared baseline."""
import copy
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
KEY='osw-motion-dashboard-seen-v2'

def main():
    original=json.loads((ROOT/'research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))
    updated=copy.deepcopy(original)
    current=next(r for r in updated['entries'] if r['id']=='current:north-cape')
    current['fingerprint']='test-current-update';current['section_fingerprints']['measurements']='test-measurement-update'
    eddy=next(r for r in updated['entries'] if any(f['role']=='shared_regional_gateway' for f in r['map_features']))
    eddy['fingerprint']='test-eddy-update';eddy['section_fingerprints']['claims']='test-claim-update'
    baseline={r['id']:{'fingerprint':r['fingerprint'],'sections':r['section_fingerprints']} for r in original['entries']}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
        context=browser.new_context(viewport={'width':1440,'height':1050})
        context.route('**/research/ocean-motion-dashboard.json',lambda route:route.fulfill(json=updated))
        page=context.new_page();errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#route-atlas',wait_until='networkidle')
        assert '0 updated records' in page.locator('#route-atlas-update-summary').inner_text()
        page.evaluate('([key,value])=>localStorage.setItem(key,JSON.stringify(value))',[KEY,baseline])
        page.locator('#route-atlas-refresh').click();page.wait_for_load_state('networkidle')
        assert '2 updated records' in page.locator('#route-atlas-update-summary').inner_text()
        assert page.locator('.route-atlas-station.updated').count()==1
        assert page.locator('.route-atlas-eddy.updated').count()==1
        assert 'Measurements' in page.locator('.route-atlas-station.updated').get_attribute('aria-label')
        assert '1 updated records' in page.locator('.route-atlas-eddy.updated').get_attribute('aria-label')
        assert 'Measurements' in page.locator('#north-cape-northern-reach-reference-path-candidate .route-atlas-update-note').inner_text()
        page.locator('.route-atlas-eddy.updated').focus();page.keyboard.press('Enter')
        assert eddy['label'] in page.locator('#route-atlas-status').inner_text()
        page.locator('#route-atlas-eddy-select').select_option(eddy['id'])
        assert 'Claims / reviews' in page.locator('#route-atlas-status').inner_text()
        page.locator('#route-atlas-select').select_option(current['id'])
        page.locator('#route-atlas-preview').get_by_role('link',name='Full route card, measurements and sources').click()
        page.wait_for_function('location.hash === "#north-cape-northern-reach-reference-path-candidate"')
        page.locator('#north-cape-northern-reach-reference-path-candidate').get_by_role('link',name='Back to global current map').click()
        assert abs(page.locator('#route-atlas').bounding_box()['y']) < 30
        page.locator('#route-atlas').screenshot(path=str(ROOT/'figures/reference-route-update-lights-review.png'))
        # A second tab acknowledgement updates the first tab through the storage event.
        other=context.new_page()
        other.goto('http://127.0.0.1:8788/almanac/reference-routes.html#route-atlas',wait_until='networkidle')
        other.locator('#route-atlas-seen').click()
        page.wait_for_function('document.getElementById("route-atlas-update-summary").textContent.startsWith("0 updated")')
        assert page.locator('.updated').count()==0
        assert page.locator('.route-atlas-update-note').count()==0
        assert page.locator('#route-atlas-seen').is_disabled()
        saved=page.evaluate('(key)=>JSON.parse(localStorage.getItem(key))',KEY)
        assert saved[current['id']]['fingerprint']==current['fingerprint']
        assert len(saved)==240
        updated['built_at_utc']='2099-01-01T00:00:00Z'
        page.locator('#route-atlas-refresh').click();page.wait_for_load_state('networkidle')
        assert '0 updated records' in page.locator('#route-atlas-update-summary').inner_text()
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert not errors,errors
        browser.close()
    print('OK: first baseline, current/eddy/group change lights, measurement/claim labels, card notes, refresh, shared-tab acknowledgement, timestamp stability and mobile reflow')

if __name__=='__main__':main()
