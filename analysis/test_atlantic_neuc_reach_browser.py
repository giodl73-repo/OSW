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
        page.locator('#route-atlas-select').select_option('current:atlantic-north-equatorial-undercurrent')
        preview=page.locator('#route-atlas-preview')
        assert preview.locator('.route-map').is_visible()
        assert page.url.endswith('#route-atlas')
        for expected in ['1,300','1,200–1,400','Studied reach only','65–270 m','not an observed continuous axis']:
            assert expected in preview.inner_text(),expected
        preview.get_by_role('link',name='Full route card, measurements and sources').click()
        card=page.locator('#atlantic-neuc-reach-reference-path-candidate')
        assert abs(card.bounding_box()['y'])<30
        assert card.locator('.route-map').is_visible()
        assert 'surface NECC flow' in card.inner_text()
        card.locator('.route-map').screenshot(path='figures/atlantic-neuc-reach-reference-path-review.png')
        assert page.locator('#reference-route-rows tr').count()==37
        assert page.locator('#reference-route-rows a[href="#atlantic-neuc-reach-reference-path-candidate"]').count()==0
        card.get_by_role('link',name='Back to global current map').click()
        assert page.url.endswith('#route-atlas')
        assert page.locator('#route-atlas-preview').is_hidden()
        row=next(r for r in json.loads(Path('research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))['entries'] if r['id']=='current:atlantic-north-equatorial-undercurrent')
        assert row['capabilities']['reference_route']==1
        assert row['capabilities']['scope_notes']==1
        assert row['capabilities']['scoped_width']==2
        assert row['latest_observation_date'] is None
        width=json.loads(Path('research/ocean-current-width-inventory.json').read_text(encoding='utf-8'))
        decision=next(r for r in width['current_decisions'] if r['current_id']=='atlantic-north-equatorial-undercurrent')
        assert decision['width_decision']=='scoped_width_evidence_present'
        audit=json.loads(Path('research/atlantic-neuc-layer-width-scope-audit.json').read_text(encoding='utf-8'))
        width_evidence=audit['historical_width_evidence']
        assert width_evidence['reported_latitude_span_degrees']==2
        assert width_evidence['observation_months']==['1993-02','1996-04']
        assert width_evidence['numeric_km_inventory_admission'] is True
        records=[r for r in width['measurements'] if r['current_id']==decision['current_id']]
        assert len(records)==2
        assert {r['observed_month'] for r in records}=={'1993-02','1996-04'}
        assert all(r['approximate_width_km']==220 and r['observed_period'] is None and r['section_geometry'] is None for r in records)
        assert decision['whole_current_width_km'] is None
        page.set_viewport_size({'width':320,'height':800})
        page.locator('#route-atlas-select').select_option('current:atlantic-north-equatorial-undercurrent')
        assert preview.locator('.route-map').is_visible()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=atlantic-north-equatorial-undercurrent',wait_until='networkidle')
        assert page.locator('#season-play').is_disabled()
        assert page.locator('#season-title').inner_text()=='Historical section observation'
        assert page.locator('#season-phase option').count()==2
        assert '220 km reported section span' in page.locator('#season-value').inner_text()
        assert 'February 1993' in page.locator('#season-value').inner_text()
        assert 'not establish seasonal states' in page.locator('#season-range').inner_text()
        assert 'Static route context' in page.locator('#season-map-note').inner_text()
        page.locator('#season-phase').select_option('1')
        assert 'April 1996' in page.locator('#season-value').inner_text()
        assert page.locator('#season-play').is_disabled()
        assert 'threshold unspecified' in page.locator('#season-definition').inner_text()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.set_viewport_size({'width':1440,'height':1000})
        page.screenshot(path='figures/atlantic-neuc-month-width-review.png')
        assert not errors,errors
        browser.close()
    print('OK: Atlantic NEUC inline/map card, studied-reach exclusion, two converted month-width records, no invented days/edges/seasonal playback, dashboard provenance, canonical ledger unchanged and mobile reflow')

if __name__=='__main__':main()
