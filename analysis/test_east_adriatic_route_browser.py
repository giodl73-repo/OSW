"""Verify the source-convention route is visible without canonical promotion."""
import hashlib,json
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    assert hashlib.sha256(Path('research/ocean-current-almanac.json').read_bytes()).hexdigest()=='6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e'
    ledger=json.loads(Path('research/ocean-current-almanac.json').read_text(encoding='utf-8'))
    current=next(row for row in ledger['entries'] if row['id']=='east-adriatic')
    assert current['length_km'] is None
    report=json.loads(Path('research/east-adriatic-reference-path-candidate.json').read_text(encoding='utf-8'))
    assert report['reported_approximate_reference_path_km']==800
    assert report['reported_scenario_range_km']==[700,800] and report['scenario_count']==81
    assert abs(report['nominal_reference_path_km']-800)>10
    assert report['whole_system_length'] is False and report['rank_eligible_published_estimates'] is False
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
        page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Aeast-adriatic#route-atlas',wait_until='networkidle')
        page.wait_for_function('document.querySelector("#route-atlas-select").value==="current:east-adriatic"')
        preview=page.locator('#route-atlas-preview')
        for text in ['800 km','700–800 km','Dalmatian','General surface','not measured seasonal variation','MEDI']:
            assert text in preview.inner_text(),text
        assert preview.locator('.route-map').is_visible()
        preview.get_by_role('link',name='Full route card, measurements and sources').click()
        card=page.locator('#east-adriatic-reference-path-candidate')
        assert abs(card.bounding_box()['y'])<30
        assert '800 km basin length' in card.inner_text()
        card.locator('.route-map').screenshot(path='figures/east-adriatic-reference-path-review.png')
        page.set_viewport_size({'width':320,'height':800})
        card.get_by_role('link',name='Back to global current map').click()
        page.locator('#route-atlas-select').select_option('current:east-adriatic')
        assert preview.locator('.route-map').is_visible()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert not errors,errors
        browser.close()
    print('OK: East Adriatic convention, computed route versus basin length, visual navigation, state link and mobile reflow')


if __name__=='__main__':main()
