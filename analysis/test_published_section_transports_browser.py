"""Native/WASM parity, source navigation and mobile transport cards."""
import json,os,tempfile
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect
from test_rust_query_browser import ROOT,native
from test_published_section_transports import guard_fixtures
from antarctic_slope_guard_fixtures import wasm_rejections
from test_motion_dashboard_browser import settle

BASE='http://127.0.0.1:8788/almanac/'
def panel(page):
    p=page.locator('.published-section-transports');p.wait_for(state='visible',timeout=90000)
    assert 'undefined' not in p.inner_text()
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    assert p.locator('svg text').evaluate_all('(es)=>es.every(e=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12)')
    return p

def main():
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as tmp, sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':320,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(BASE+'seasons.html?current=hiri-current');s=panel(page)
        assert s.locator('[data-transport-id]').count()==1
        guide=s.locator('svg g[tabindex]').first;label=guide.locator('text');assert label.get_attribute('visibility')=='hidden';guide.focus();assert label.get_attribute('visibility')=='visible';page.locator('#season-current').focus();assert label.get_attribute('visibility')=='hidden'
        assert page.locator('#season-play').is_disabled()
        snapshot=page.evaluate('oswSeasonSnapshot.published_transport_scenes')
        assert len(snapshot)==6 and '5 Sv seasonal range' in s.inner_text()
        page.screenshot(path=str(ROOT/'.pytest_cache/transport-hiri-mobile.png'),full_page=True)
        page.goto(BASE+'reference-routes.html?atlas-feature=current%3Ahiri-current#route-atlas');panel(page)
        assert page.evaluate('oswAtlasSnapshot.published_transport_scenes')==snapshot
        for c,n in [('section_transports',35),('transport_validations',6)]:
            q={'collection':c,'limit':1};page.goto(BASE+'query.html?q='+quote(json.dumps(q)))
            page.wait_for_function(f'window.oswLastQueryResult?.total==={n}',timeout=90000)
            s=panel(page);assert page.evaluate('oswLastQueryResult')==native(q)
            s.get_by_role('button',name='Inspect record',exact=True).first.focus();page.keyboard.press('Enter')
            expect(page.locator('#query-detail')).to_contain_text('ozroms-2018:')
            if c=='transport_validations':assert 'M1 reports W' in s.inner_text() and '17-calendar-month' in s.inner_text()
        s.get_by_role('link',name='Inspect source row',exact=True).first.click()
        page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
        assert '/transport_validations/0' in page.url or 'transport_validations' in page.url
        page.goto(BASE+'dashboard.html');page.wait_for_function('window.oswDashboardSnapshot?.snapshot',timeout=90000)
        page.locator('#dashboard-metric').select_option('section_transport');settle(page)
        assert page.locator('.beck-station.lit[data-current-id]').count()==6
        page.goto(BASE+'query.html?q='+quote(json.dumps({'collection':'section_transports'})))
        page.wait_for_function('window.oswLastQueryResult?.total===35',timeout=90000)
        results=wasm_rejections(page,guard_fixtures(Path(tmp)))
        assert all(r['ok'] is False and 'Published section transport' in r['error'] for r in results),results
        assert not errors,errors;browser.close()
    print('PASS: 35 transports / six validations, six current cards, native/WASM parity, source inspection, keyboard/mobile, dashboard scope and ten guards')

if __name__=='__main__':main()
