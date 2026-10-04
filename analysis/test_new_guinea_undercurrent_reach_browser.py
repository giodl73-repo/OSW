"""Keep NGCU reach, source season labels and local depth support distinct."""
import json,hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    assert hashlib.sha256(Path('research/ocean-current-almanac.json').read_bytes()).hexdigest()=='6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e'
    r=json.loads(Path('research/new-guinea-coastal-undercurrent-reference-path-candidate.json').read_text(encoding='utf-8'))
    assert r['scenario_count']==81 and r['reported_approximate_reference_path_km']==600
    assert r['reported_scenario_range_km']==[500,700] and r['whole_system_length'] is False
    assert r['source_season_convention']['months_by_label']=={'winter':[1,2,3],'summer':[7,8,9],'fall':[10,11,12]}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
        page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Anew-guinea-coastal-undercurrent#route-atlas',wait_until='networkidle')
        preview=page.locator('#route-atlas-preview')
        assert preview.locator('.route-map').is_visible()
        for text in ['600 km','500–700 km','Studied reach only','Vitiaz Strait itself','whole-current origin','surface New Guinea Coastal Current']:
            assert text in preview.inner_text(),text
        seasons=preview.locator('.route-atlas-source-seasons').inner_text()
        assert 'boreal' in seasons and 'summer: Jul, Aug, Sep' in seasons and 'winter: Jan, Feb, Mar' in seasons
        assert 'not seasonal route geometry' in seasons
        preview.get_by_role('link',name='Full route card, measurements and sources').click()
        card=page.locator('#new-guinea-coastal-undercurrent-reference-path-candidate')
        assert '150–250 m' in card.inner_text() and 'not a fixed-depth axis' in card.inner_text()
        assert card.locator(f'a[href="{r["source_url"]}"]').count()>=1
        assert page.locator('#reference-route-rows a[href="#new-guinea-coastal-undercurrent-reference-path-candidate"]').count()==0
        card.locator('.route-map').screenshot(path='figures/new-guinea-undercurrent-route-review.png')
        page.set_viewport_size({'width':320,'height':800})
        card.get_by_role('link',name='Back to global current map').click()
        page.locator('#route-atlas-select').select_option('current:new-guinea-coastal-undercurrent')
        assert preview.locator('.route-map').is_visible()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=new-guinea-coastal-undercurrent',wait_until='networkidle')
        assert page.locator('#season-play').is_disabled()
        assert 'Static route context' in page.locator('#season-map-note').inner_text()
        assert not errors,errors
        browser.close()
    print('OK: NGCU 600 km reach, boreal source months, local depth support, no ranking or annual geometry transfer, static seasonal context and mobile reflow')


if __name__=='__main__':main()
