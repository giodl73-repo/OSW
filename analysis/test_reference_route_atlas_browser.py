"""Exercise global atlas zoom, pan, current selection and map-card navigation."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page = browser.new_page(viewport={'width':1440, 'height':1000})
        page.emulate_media(reduced_motion='reduce')  # Scroll assertions require settled, immediate navigation.
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#route-atlas', wait_until='networkidle')
        page.wait_for_function('document.querySelectorAll(".route-atlas-station").length === 100')
        page.wait_for_function('document.querySelectorAll(".route-card").length === 64 && document.querySelectorAll(".inventory-addition-card").length === 28')
        assert page.locator('#route-atlas-select option').count() == 101
        for ident,label in [('atlantic-north-equatorial','Atlantic North Equatorial Current'),('pacific-north-equatorial','Pacific North Equatorial Current'),('atlantic-south-equatorial','Atlantic South Equatorial Current'),('pacific-south-equatorial','Pacific South Equatorial Current'),('indian-south-equatorial','Indian South Equatorial Current')]:
            card=page.locator('#inventory-addition-'+ident)
            assert card.locator('h3').inner_text()==label
            assert 'no whole-current length or rank admitted' in card.inner_text()
            assert card.get_by_role('link',name='NOAA Tides & Currents glossary',exact=True).get_attribute('href')=='https://www.tidesandcurrents.noaa.gov/glossary.html'
        assert page.locator('#inventory-addition-indian-north-equatorial').count()==0
        atlas = page.locator('#route-atlas-map')
        def view():
            return list(map(float, atlas.get_attribute('viewBox').split()))
        assert view() == [60,90,1480,740]
        # Aleutian is a sourced schematic reach, crossing the date line.
        page.locator('#route-atlas-select').select_option('current:aleutian')
        assert view() == [60,90,1480,740]  # Global fit preserves both sides of the date line.
        aleutian = page.locator('#route-atlas-preview')
        assert aleutian.locator('.route-map').is_visible()
        assert 'regional' in aleutian.inner_text().lower()
        assert page.locator('#route-atlas-card-link').get_attribute('href') == '#aleutian-reach-reference-path-candidate'
        page.locator('#route-atlas-select').select_option('current:solomon-island-coastal-undercurrent')
        solomon=page.locator('#route-atlas-preview')
        assert solomon.locator('.route-map').is_visible()
        assert '900 km' in solomon.inner_text() and '800' in solomon.inner_text() and '1,000' in solomon.inner_text()
        assert 'continuity' in solomon.inner_text().lower()
        assert 'Ganachaud' in solomon.inner_text()
        assert page.locator('#route-atlas-card-link').get_attribute('href')=='#solomon-island-coastal-undercurrent-reference-path-candidate'
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        solomon.screenshot(path='.pytest_cache/solomon-reference-card-mobile.png')
        page.set_viewport_size({'width':1440,'height':1000})
        page.locator('#route-atlas-world').click()
        page.locator('#route-atlas-select').select_option('current:ligurian')
        assert view()[2] < 30  # Short coastal routes fill a local view, not a continent.
        route=json.loads(Path('research/ligurian-reach-reference-path-candidate.json').read_text(encoding='utf-8'))
        x,y,w,h=view()
        for lon,lat in route['coordinates_lon_lat']:
            assert x <= 60+(lon+180)/360*1480 <= x+w
            assert y <= 90+(90-lat)/180*740 <= y+h
        for _ in range(10):
            if page.locator('#route-atlas-in').is_enabled():
                page.locator('#route-atlas-in').click()
        assert view()[2]==8 and page.locator('#route-atlas-in').is_disabled()
        page.locator('#route-atlas-world').click()
        assert view() == [60,90,1480,740]
        page.locator('#route-atlas-in').click()
        assert view()[2] < 1480
        before=view()
        atlas.scroll_into_view_if_needed()
        box=atlas.bounding_box()
        page.mouse.move(box['x']+box['width']*.5,box['y']+box['height']*.5)
        page.mouse.down();page.mouse.move(box['x']+box['width']*.6,box['y']+box['height']*.5);page.mouse.up()
        assert view()[0] < before[0]
        atlas.focus();page.keyboard.press('Home')
        assert view() == [60,90,1480,740]
        atlas.scroll_into_view_if_needed()
        box=atlas.bounding_box()
        page.mouse.move(box['x']+box['width']*.5,box['y']+box['height']*.5)
        page.mouse.wheel(0,-100)
        page.wait_for_function('Number(document.getElementById("route-atlas-map").getAttribute("viewBox").split(" ")[2]) < 1480')
        before=view();atlas.focus();page.keyboard.press('ArrowRight')
        assert view()[0] > before[0]
        page.keyboard.press('Home')
        page.locator('#route-atlas').evaluate('(el)=>el.scrollIntoView({block:"start"})')
        page.locator('#route-atlas-select').focus()
        scroll_before=page.evaluate('scrollY')
        page.locator('#route-atlas-select').select_option('current:agulhas')
        assert page.url.endswith('#route-atlas')
        assert abs(page.evaluate('scrollY')-scroll_before)<2
        preview=page.locator('#route-atlas-preview')
        assert preview.locator('.route-map').is_visible()
        assert 'Agulhas' in preview.inner_text()
        shared_url=preview.get_by_role('link',name='Link to this atlas view').get_attribute('href')
        assert 'atlas-feature=current%3Aagulhas' in shared_url
        shared=browser.new_page()
        shared.goto(shared_url,wait_until='networkidle')
        shared.wait_for_function('document.querySelector("#route-atlas-select").value === "current:agulhas"')
        assert shared.locator('#route-atlas-preview .route-map').is_visible()
        assert float(shared.locator('#route-atlas-map').get_attribute('viewBox').split()[2])<1480
        shared.locator('#route-atlas-world').click()
        assert 'atlas-feature' not in shared.url
        shared.reload(wait_until='networkidle')
        assert shared.locator('#route-atlas-preview').is_hidden()
        shared.close()
        page.locator('#route-atlas').screenshot(path='figures/reference-route-inline-card-review.png')
        preview.get_by_role('link',name='Full route card, measurements and sources').click()
        page.wait_for_function('location.hash === "#agulhas-reference-path-candidate"')
        assert view()[2] < 1480
        card=page.locator('#agulhas-reference-path-candidate')
        assert card.locator('.route-map').is_visible()
        card.get_by_role('link',name='Back to global current map').click()
        assert page.url.endswith('#route-atlas')
        assert abs(page.locator('#route-atlas').bounding_box()['y']) < 30
        assert view() == [60,90,1480,740]
        catalog=json.loads(Path('research/ocean-current-reference-path-candidates.json').read_text(encoding='utf-8'))
        grouped={}
        for row in catalog['candidates']:
            grouped.setdefault(row['current_id'],[]).append(row)
        current_id,components=next((key,rows) for key,rows in grouped.items() if len(rows)>1)
        page.locator('#route-atlas-select').select_option('current:'+current_id)
        buttons=page.locator('#route-atlas-preview button')
        assert buttons.count()==len(components)
        buttons.nth(1).click()
        assert buttons.nth(1).get_attribute('aria-pressed')=='true'
        assert page.locator('#route-atlas-card-link').get_attribute('href')=='#'+components[1]['id']
        assert components[1]['scope'] in page.locator('#route-atlas-preview').inner_text()
        component_url=page.locator('#route-atlas-preview [data-atlas-share]').get_attribute('href')
        assert 'atlas-route='+components[1]['id'] in component_url
        shared=browser.new_page()
        shared.goto(component_url,wait_until='networkidle')
        shared.wait_for_function('(id)=>document.querySelector("#route-atlas-card-link").getAttribute("href")==="#"+id',arg=components[1]['id'])
        assert components[1]['scope'] in shared.locator('#route-atlas-preview').inner_text()
        assert shared.locator('#route-atlas-preview button').nth(1).get_attribute('aria-pressed')=='true'
        shared.close()
        page.locator('#route-atlas-world').click()
        page.locator('#route-atlas-select').select_option('current:west-australian')
        assert page.url.endswith('#route-atlas')
        assert 'no reference-route card yet' in page.locator('#route-atlas-status').inner_text()
        assert 'object.html?id=' in page.locator('#route-atlas-card-link').get_attribute('href')
        page.locator('#route-atlas-world').click()
        assert page.locator('#route-atlas-preview').is_hidden()
        snapshot=json.loads(Path('research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))
        eddies=[r for r in snapshot['entries'] if r['type'] in ('named_eddy','operational_eddy_detection')]
        assert len(eddies)==140
        assert page.locator('#route-atlas-eddy-select option').count()==141
        # Every inventory name is selectable, including names sharing a regional gateway.
        for eddy in eddies:
            page.locator('#route-atlas-eddy-select').select_option(eddy['id'])
            assert page.locator('#route-atlas-card-link').get_attribute('href')==eddy['object_url']
            status=page.locator('#route-atlas-status').inner_text()
            assert eddy['label'] in status
            if any(f['role']=='shared_regional_gateway' for f in eddy['map_features']):
                assert 'no individual center or footprint' in status
            if any(f['geometry']['type']=='Polygon' for f in eddy['map_features']):
                assert eddy['latest_observation_date'] in status
                assert 'not live extent' in status
        assert page.locator('#route-atlas-map .route-atlas-eddy-footprint').count()==5
        gateway=page.locator('[data-eddy-ids]').filter(has=page.locator('text')).filter(has_text='100 names')
        assert gateway.count()==1
        page.locator('#route-atlas-world').click()
        gateway.focus();page.keyboard.press('Enter')
        assert 'not 100 observed centers' in page.locator('#route-atlas-status').inner_text()
        assert page.locator('#route-atlas-card-link').is_hidden()
        page.locator('#route-atlas-eddy-toggle').uncheck()
        assert page.locator('#route-atlas-eddies').is_hidden()
        page.locator('#route-atlas-eddy-select').select_option(eddies[0]['id'])
        assert page.locator('#route-atlas-eddy-toggle').is_checked()
        assert page.locator('#route-atlas-eddies').is_visible()
        page.locator('#route-atlas-world').click()
        page.locator('#route-atlas').scroll_into_view_if_needed()
        page.screenshot(path='figures/reference-route-current-eddy-atlas-review.png')
        page.set_viewport_size({'width':320,'height':800})
        page.locator('#route-atlas-select').select_option('current:agulhas')
        assert page.locator('#route-atlas-preview .route-map').is_visible()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert not errors, errors
        browser.close()
    print('OK: 100 selectable currents, zoom, drag pan, keyboard reset, map-card return, pending-route record, all 140 eddy records, grouped gateways, dated footprints and mobile reflow')


if __name__ == '__main__':
    main()
