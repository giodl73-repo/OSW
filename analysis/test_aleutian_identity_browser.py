"""Separate Bering-side proposal from canonical Aleutian geometry and dimensions."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
    root=Path(__file__).resolve().parents[1]
    data=json.loads((root/'research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))
    row=next(r for r in data['entries'] if r['id']=='current:aleutian')
    assert row['capabilities']['reference_route']==0
    assert row['capabilities']['scoped_width']==0
    assert row['latest_observation_date'] is None
    assert len(data['entries'])==240
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ['OSW_TEST_BROWSER'])
        page=browser.new_page(viewport={'width':320,'height':800});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Aaleutian#route-atlas',wait_until='networkidle')
        page.wait_for_function('document.querySelector("#route-atlas-select").value==="current:aleutian"')
        assert page.locator('#route-atlas-select option').count()==101
        assert page.locator('#route-atlas-preview .route-map').count()==0
        assert row['scope_notes'][0]['summary'] in page.locator('.route-atlas-scope-reviews').inner_text()
        card=page.locator('#inventory-addition-aleutian-north-slope')
        assert card.is_visible()
        assert 'not Aleutian' in card.inner_text()
        assert 'full article not acquired' in card.inner_text()
        assert 'no whole-current length or rank admitted' in card.inner_text()
        assert '28 proposed inventory additions' in page.locator('#inventory-addition-status').inner_text()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.set_viewport_size({'width':1440,'height':1100})
        card.screenshot(path=str(root/'figures/aleutian-north-slope-proposal-review.png'))
        assert not errors,errors
        browser.close()
    print('OK: three Aleutian-region identities separated, proposal access limits visible, no borrowed route/width or canonical count increase, mobile reflow')

if __name__=='__main__':main()
