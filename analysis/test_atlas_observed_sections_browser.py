"""Observed transverse samples zoom into a current card without a route claim."""
import copy,json,os,time
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
BASE='http://127.0.0.1:8788/almanac/reference-routes.html'
DATA='**/antilles-ab0505-400m-section-diagnostic.json'

def main():
    document=json.loads((ROOT/'research/antilles-ab0505-400m-section-diagnostic.json').read_text(encoding='utf-8'))
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ['OSW_TEST_BROWSER'])
        page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(BASE+'?atlas-feature=current%3Aantilles#route-atlas',wait_until='networkidle')
        page.wait_for_function('document.querySelector(".atlas-observed-section-select")?.disabled===false')
        assert page.locator('#route-atlas-map .atlas-observed-station').count()==23
        assert 'has-observed-samples' in page.locator('#route-atlas-map').get_attribute('class')
        assert page.locator('#route-atlas-preview .atlas-observed-section-map').is_visible()
        assert 'Offshore half-peak boundary unresolved' in page.locator('.atlas-observed-section-status').inner_text()
        assert page.locator('#route-atlas-preview .route-map').count()==0
        assert page.locator('#route-atlas-map').get_attribute('viewBox')!='60 90 1480 740'
        select=page.locator('.atlas-observed-section-select');select.select_option('abaco_repeat')
        assert page.locator('#route-atlas-map .atlas-observed-station').count()==27
        assert 'About 37 km one-sided' in page.locator('.atlas-observed-section-status').inner_text()
        assert parse_qs(urlparse(page.url).query)['atlas-section']==['abaco_repeat']
        saved=page.locator('#route-atlas-preview [data-atlas-share]').get_attribute('href')
        page.reload(wait_until='networkidle')
        assert page.locator('.atlas-observed-section-select').input_value()=='abaco_repeat'
        assert page.url==saved
        x,y,w,h=map(float,page.locator('#route-atlas-map').get_attribute('viewBox').split())
        for sample in document['sections'][1]['samples']:
            lon,lat=sample['coordinates_lon_lat'];assert x<=60+(lon+180)/360*1480<=x+w;assert y<=90+(90-lat)/180*740<=y+h
        station=page.locator('#route-atlas-map .atlas-observed-station').first
        page.mouse.move(0,0);page.locator('#route-atlas-select').focus()
        assert station.locator('text').evaluate('(e)=>getComputedStyle(e).opacity')=='0'
        station.focus();page.keyboard.press('Enter')
        assert station.locator('text').evaluate('(e)=>getComputedStyle(e).opacity')=='1'
        assert 'AB0505_063' in page.locator('.atlas-observed-cast-info').inner_text(), (page.locator('.atlas-observed-cast-info').inner_text(),station.get_attribute('data-cast-id'),page.evaluate('document.activeElement.outerHTML'))
        assert 'no sample at 400 m' in page.locator('.atlas-observed-cast-info').inner_text()
        page.locator('.atlas-observed-details-link').click()
        page.wait_for_function('document.querySelector("#section-select")?.value==="abaco_repeat"')
        page.get_by_role('link',name='Return to Antilles on the atlas').click()
        page.wait_for_function('document.querySelector(".atlas-observed-section-select")?.disabled===false')
        assert page.locator('.atlas-observed-section-select').input_value()=='abaco_repeat'
        page.locator('#route-atlas').screenshot(path=str(ROOT/'figures/antilles-observed-atlas-card-review.png'))
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#route-atlas-select').select_option('current:agulhas')
        assert page.locator('.atlas-observed-overlay').count()==0
        assert 'has-observed-samples' not in (page.locator('#route-atlas-map').get_attribute('class') or '')
        assert 'atlas-section' not in parse_qs(urlparse(page.url).query)
        page.locator('#route-atlas-select').select_option('current:antilles')
        page.wait_for_function('document.querySelector(".atlas-observed-section-select")?.disabled===false')
        page.locator('#route-atlas-world').click()
        assert page.locator('.atlas-observed-overlay').count()==0
        assert page.locator('#route-atlas-preview').is_hidden()
        assert 'atlas-section' not in page.url
        # A selected card disposed during data loading must not reappear.
        def delayed(route):
            response=route.fetch();time.sleep(.3);route.fulfill(response=response)
        page.route(DATA,delayed)
        page.locator('#route-atlas-select').select_option('current:antilles')
        page.locator('#route-atlas-world').click()
        page.wait_for_load_state('networkidle')
        assert page.locator('.atlas-observed-overlay').count()==0
        assert page.locator('#route-atlas-preview').is_hidden()
        page.unroute(DATA,delayed)
        # Missing or relabeled evidence preserves the existing atlas and links.
        for invalid in [None,copy.deepcopy(document)]:
            if invalid is not None:invalid['whole_current_width_km']=74
            def bad(route):
                route.fulfill(status=503,body='Unavailable') if invalid is None else route.fulfill(json=invalid)
            page.route(DATA,bad)
            page.locator('#route-atlas-select').select_option('current:antilles')
            page.wait_for_function('document.querySelector(".atlas-observed-section-status")?.textContent.includes("standalone")')
            assert page.locator('.atlas-observed-overlay').count()==0
            assert page.locator('.atlas-observed-details-link').get_attribute('href')=='antilles-sections.html'
            page.unroute(DATA,bad)
            page.locator('#route-atlas-world').click()
        assert not errors,errors
        browser.close()
    print('OK: 23/27 observed atlas stations, local card, saved occupation, keyboard cast, standalone link, mobile reflow, global/switch cleanup and delayed/invalid/missing data fallback')

if __name__=='__main__':main()
