"""Verify subsurface study truncation, width rejection and inline atlas navigation."""
import hashlib,json
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
    ledger=Path('research/ocean-current-almanac.json')
    assert hashlib.sha256(ledger.read_bytes()).hexdigest()=='6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e'
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
        page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#route-atlas',wait_until='networkidle')
        page.locator('#route-atlas-select').select_option('current:atlantic-south-equatorial-undercurrent')
        preview=page.locator('#route-atlas-preview')
        assert preview.locator('.route-map').is_visible()
        assert page.url.endswith('#route-atlas')
        for expected in ['2,800','2,700–2,900','Studied reach only','200 m','recirculation loops']:
            assert expected in preview.inner_text(),expected
        preview.get_by_role('link',name='Full route card, measurements and sources').click()
        card=page.locator('#atlantic-seuc-reach-reference-path-candidate')
        assert abs(card.bounding_box()['y'])<30
        assert card.locator('.route-map').is_visible()
        assert 'surface drift' in card.inner_text()
        card.locator('.route-map').screenshot(path='figures/atlantic-seuc-reach-reference-path-review.png')
        assert page.locator('#reference-route-rows tr').count()==37
        assert page.locator('#reference-route-rows a[href="#atlantic-seuc-reach-reference-path-candidate"]').count()==0
        card.get_by_role('link',name='Back to global current map').click()
        assert page.url.endswith('#route-atlas')
        assert page.locator('#route-atlas-preview').is_hidden()
        row=next(r for r in json.loads(Path('research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))['entries'] if r['id']=='current:atlantic-south-equatorial-undercurrent')
        assert row['capabilities']['reference_route']==1
        assert row['capabilities']['scope_notes']==1
        assert row['capabilities']['scoped_width']==0
        assert row['latest_observation_date'] is None
        width=json.loads(Path('research/ocean-current-width-inventory.json').read_text(encoding='utf-8'))
        decision=next(r for r in width['current_decisions'] if r['current_id']=='atlantic-south-equatorial-undercurrent')
        assert decision['width_decision']=='sources_reviewed_no_comparable_numeric_current_width'
        assert decision['whole_current_width_km'] is None
        page.set_viewport_size({'width':320,'height':800})
        page.locator('#route-atlas-select').select_option('current:atlantic-south-equatorial-undercurrent')
        assert preview.locator('.route-map').is_visible()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert not errors,errors
        browser.close()
    print('OK: Atlantic SEUC inline/map card, studied-reach exclusion, layer/sampling width rejection, dashboard provenance, canonical ledger unchanged and mobile reflow')

if __name__=='__main__':main()
