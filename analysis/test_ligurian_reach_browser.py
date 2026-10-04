"""Verify local Ligurian reach and nonadditive parent navigation."""
import json,hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
    assert hashlib.sha256(Path('research/ocean-current-almanac.json').read_bytes()).hexdigest()=='6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e'
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
        page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#route-atlas',wait_until='networkidle')
        page.locator('#route-atlas-select').select_option('current:ligurian')
        preview=page.locator('#route-atlas-preview')
        assert preview.locator('.route-map').is_visible()
        text=preview.inner_text()
        for expected in ['100 km','100–200 km','Studied reach only','do not add its length','first metre','Genoa','Menton']:
            assert expected in text,expected
        assert preview.get_by_role('link',name='Inspect parent current route').get_attribute('href')=='#northern-mediterranean-reference-path-candidate'
        preview.get_by_role('link',name='Inspect parent current route').click()
        parent=page.locator('#northern-mediterranean-reference-path-candidate')
        assert abs(parent.bounding_box()['y'])<30
        assert parent.locator('.route-map').is_visible()
        parent.get_by_role('link',name='Back to global current map').click()
        page.locator('#route-atlas-select').select_option('current:ligurian')
        preview.get_by_role('link',name='Full route card, measurements and sources').click()
        card=page.locator('#ligurian-reach-reference-path-candidate')
        assert abs(card.bounding_box()['y'])<30
        assert 'not a separate additive current system' in card.inner_text()
        assert card.get_by_role('link',name='Inspect parent current route').count()==1
        assert page.locator('#reference-route-rows a[href="#ligurian-reach-reference-path-candidate"]').count()==0
        catalog=json.loads(Path('research/ocean-current-reference-path-candidates.json').read_text(encoding='utf-8'))
        assert page.locator('#reference-route-rows tr').count()==sum(r['comparison_group']=='osw_approximate_reference_routes' for r in catalog['candidates'])
        card.locator('.route-map').screenshot(path='figures/ligurian-reach-reference-path-review.png')
        snapshot=json.loads(Path('research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))
        row=next(r for r in snapshot['entries'] if r['id']=='current:ligurian')
        assert row['capabilities']['reference_route']==1 and row['capabilities']['scope_notes']==1
        assert row['capabilities']['scoped_width']==1 and row['latest_observation_date'] is None
        w=json.loads(Path('research/ocean-current-width-inventory.json').read_text(encoding='utf-8'))
        d=next(r for r in w['current_decisions'] if r['current_id']=='ligurian')
        assert d['width_decision']=='scoped_width_evidence_present'
        assert d['whole_current_width_km'] is None
        width=next(r for r in w['measurements'] if r['id']==d['measurement_ids'][0])
        assert width['approximate_width_km']==20 and width['width_range_km'] is None
        assert width['coast_distance_profile']['source_reported_band_limits_km']==[15,35]
        assert width['source_parent_current_id']=='northern-mediterranean'
        page.set_viewport_size({'width':320,'height':800})
        card.get_by_role('link',name='Back to global current map').click()
        page.locator('#route-atlas-select').select_option('current:ligurian')
        assert preview.locator('.route-map').is_visible()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=ligurian',wait_until='networkidle')
        assert page.locator('#season-title').inner_text()=='Composite profile observation'
        assert page.locator('#season-phase option').count()==1
        assert page.locator('#season-play').is_disabled()
        assert '20 km reported offshore flow-band span' in page.locator('#season-value').inner_text()
        assert '15 and 35 km' in page.locator('#season-definition').inner_text()
        assert 'Coast positions are not a width range' in page.locator('#season-range').inner_text()
        assert 'Static route context' in page.locator('#season-map-note').inner_text()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.set_viewport_size({'width':1440,'height':1000})
        page.screenshot(path='figures/ligurian-profile-width-review.png')
        assert not errors,errors
        browser.close()
    print('OK: Ligurian local surface reach, parent navigation, nonadditive scope, local profile span versus offshore position, seasonal play disabled, canonical ledger unchanged and mobile reflow')

if __name__=='__main__':main()
