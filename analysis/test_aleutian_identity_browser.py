"""Separate Bering-side proposal from canonical Aleutian geometry and dimensions."""
from browser_inventory_expectations import CURRENT_SELECT_OPTIONS, PENDING_PROPOSALS, MOTION_COUNT

import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
    root=Path(__file__).resolve().parents[1]
    data=json.loads((root/'research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))
    row=next(r for r in data['entries'] if r['id']=='current:aleutian')
    assert row['capabilities']['reference_route']==1
    assert row['capabilities']['scoped_width']==1
    assert row['latest_observation_date']=='1993-07-18'  # The undated width claim does not advance observation time.
    assert len(data['entries'])==MOTION_COUNT
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ['OSW_TEST_BROWSER'])
        page=browser.new_page(viewport={'width':320,'height':800});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Aaleutian#route-atlas',wait_until='networkidle')
        page.wait_for_function('document.querySelector("#route-atlas-select").value==="current:aleutian"')
        assert page.locator('#route-atlas-select option').count()==CURRENT_SELECT_OPTIONS
        assert page.locator('#route-atlas-preview > h3').inner_text()=='Aleutian Current'
        assert [f['role'] for f in row['map_features']]==['editorial_locator','editorial_reference_route']
        assert row['scope_notes'][0]['summary'] in page.locator('.route-atlas-scope-reviews').inner_text()
        card=page.locator('#inventory-addition-aleutian-north-slope')
        assert card.is_visible()
        assert 'not Aleutian' in card.inner_text()
        assert 'full article not acquired' in card.inner_text()
        assert 'no whole-current length or rank admitted' in card.inner_text()
        assert f'{PENDING_PROPOSALS} pending inventory additions' in page.locator('#inventory-addition-status').inner_text()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.set_viewport_size({'width':1440,'height':1100})
        out=root/'.pytest_cache/aleutian-onishi-2001';out.mkdir(parents=True,exist_ok=True)
        card.screenshot(path=str(out/'identity-proposal.png'))
        assert not errors,errors
        browser.close()
    print('OK: three Aleutian-region identities separated, proposal access limits visible, published Aleutian constraint kept separate from ANSC proposal; no identity count increase, mobile reflow')

if __name__=='__main__':main()
