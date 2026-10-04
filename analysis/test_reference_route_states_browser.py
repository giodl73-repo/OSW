"""Verify every state's reference-route inventory and optional-data fallback."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]

def main():
    join=json.loads((ROOT/'research/ocean-current-reference-route-state-join.json').read_text(encoding='utf-8'))
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
        page=browser.new_page();errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/',wait_until='networkidle')
        assert page.locator('#state-select option').count()==57
        total=0
        for code,state in join['states'].items():
            page.locator('#state-select').select_option(code)
            panel=page.locator('#state-result .state-reference-routes')
            rows=panel.locator('li[data-candidate-id]')
            assert rows.count()==len(state['route_candidates']),code
            assert f"{state['current_count']} named currents" in panel.inner_text()
            assert 'not observed current passage or eddy containment' in panel.inner_text()
            assert 'not probabilities or seasonal frequency' in panel.inner_text()
            actual={r['id']:r for r in rows.evaluate_all('(els)=>els.map(el=>({id:el.dataset.candidateId,href:el.querySelector("a").getAttribute("href"),text:el.textContent}))')}
            for expected in state['route_candidates']:
                row=actual[expected['candidate_id']]
                assert row['href']==expected['route_url']
                for text in [expected['scope'],expected['layer'],expected['time_convention']]:assert text in row['text']
                assert f"{expected['crossing_scenario_count']}/{expected['scenario_count']} declared scenarios" in row['text']
            if not state['route_candidates']:assert 'Current passage remains unresolved' in panel.inner_text()
            total+=rows.count()
        assert total==join['counts']['candidate_state_pairs']
        page.locator('#state-select').select_option('BPLR')
        item=page.locator('#state-result li[data-candidate-id="north-cape-northern-reach-reference-path-candidate"]')
        item.locator('summary').click()
        assert 'Northern-branch' in item.inner_text()
        item.locator('a').first.click()
        card=page.locator('#north-cape-northern-reach-reference-path-candidate')
        page.wait_for_function('document.activeElement?.id === "north-cape-northern-reach-reference-path-candidate"')
        assert card.locator('.route-map').is_visible()
        assert abs(card.bounding_box()['y'])<30
        page.route('**/research/ocean-current-reference-route-state-join.json',lambda route:route.fulfill(status=503,body='unavailable'))
        page.goto('http://127.0.0.1:8788/almanac/',wait_until='networkidle')
        page.locator('#state-select').select_option('BPLR')
        assert 'Reference-route state inventory unavailable' in page.locator('#state-result .state-reference-routes').inner_text()
        assert page.locator('#state-select option').count()==57
        assert page.locator('#state-result .state-groups').is_visible()
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert not errors,errors
        browser.close()
    print(f'OK: all 56 states and {total} route/state pairs, scope/provenance links, direct current map card, optional 503 fallback and mobile reflow')

if __name__=='__main__':main()
