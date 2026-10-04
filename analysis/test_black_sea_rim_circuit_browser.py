"""Check closed-circuit navigation and transparent state-mask exclusions."""
import hashlib,json
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    assert hashlib.sha256(Path('research/ocean-current-almanac.json').read_bytes()).hexdigest()=='6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e'
    report=json.loads(Path('research/black-sea-rim-reference-path-candidate.json').read_text(encoding='utf-8'))
    assert report['route_topology']=='closed_circuit'
    assert report['scenario_count']==9 and report['reported_approximate_reference_path_km']==2100
    assert report['reported_scenario_range_km']==[1900,2200]
    assert all(s['coordinates_lon_lat'][0]==s['coordinates_lon_lat'][-1] for s in report['scenarios'])
    join=json.loads(Path('research/ocean-current-reference-route-state-join.json').read_text(encoding='utf-8'))
    excluded=[r for r in join['excluded_display_contacts'] if r['candidate_id']=='black-sea-rim-reference-path-candidate']
    assert {r['state_code']:r['crossing_scenario_count'] for r in excluded}=={'MEDI':9,'REDS':4}
    assert not any(r['current_id']=='black-sea-rim' for s in join['states'].values() for r in s['route_candidates'])
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
        page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Ablack-sea-rim#route-atlas',wait_until='networkidle')
        page.wait_for_function('document.querySelector("#route-atlas-select").value==="current:black-sea-rim"')
        preview=page.locator('#route-atlas-preview')
        for text in ['2,100 km','1,900–2,200 km','Closed counterclockwise','arbitrary anchor','no dedicated state','coarse-shape artifacts']:
            assert text in preview.inner_text(),text
        assert preview.locator('.route-atlas-state-links li').count()==0
        preview.get_by_role('link',name='Full route card, measurements and sources').click()
        card=page.locator('#black-sea-rim-reference-path-candidate')
        assert abs(card.bounding_box()['y'])<30
        assert 'coarse-shape artifacts' in card.inner_text()
        assert card.locator('a[href="object.html?id=state%3AMEDI"]').count()==0
        card.locator('.route-map').screenshot(path='figures/black-sea-rim-reference-path-review.png')
        page.set_viewport_size({'width':320,'height':800})
        card.get_by_role('link',name='Back to global current map').click()
        page.locator('#route-atlas-select').select_option('current:black-sea-rim')
        assert preview.locator('.route-map').is_visible()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert not errors,errors
        browser.close()
    print('OK: closed Black Sea circuit, all nine closed scenarios, two audited geographic exclusions, direct visual card and mobile access')


if __name__=='__main__':main()
