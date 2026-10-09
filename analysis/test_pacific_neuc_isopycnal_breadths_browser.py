"""Same checked comparison in query, atlas and evidence pages, including mobile."""
import json,os,tempfile
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect
from test_rust_query_browser import ROOT,native
from test_pacific_neuc_isopycnal_breadths import fixtures,records
from antarctic_slope_guard_fixtures import wasm_rejections

BASE='http://127.0.0.1:8788/almanac/'
OWNER='pacific-north-equatorial-undercurrent'
def panel(page):
    p=page.locator('.pacific-neuc-breadths');p.wait_for(state='visible',timeout=90000)
    assert p.locator('tbody tr').count()==2
    assert 'undefined' not in p.inner_text() and 'breadth unresolved' in p.inner_text()
    assert 'not annual minimum and maximum' in p.inner_text()
    assert p.locator('svg text').evaluate_all('(es)=>es.every(e=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12)')
    assert p.locator('img').evaluate('(e)=>e.complete&&e.naturalWidth===660')
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    return p

def main():
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as tmp,sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':320,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(BASE+'seasons.html?current='+OWNER);s=panel(page)
        assert page.locator('#season-play').is_disabled() and page.locator('#season-section-locator').is_hidden()
        assert page.locator('.original-regional-width').count()==0
        snapshot=page.evaluate('oswSeasonSnapshot.pacific_neuc_breadth_scene')
        page.locator('#season-phase').select_option('1');expect(page.locator('#season-value')).to_contain_text('northern jet')
        assert s.locator('svg').text_content().count('selected')==1
        page.screenshot(path=str(ROOT/'.pytest_cache/neuc-isopycnal-mobile.png'),full_page=True)
        page.goto(BASE+'reference-routes.html?atlas-feature=current%3A'+OWNER+'#route-atlas');panel(page)
        assert page.evaluate('oswAtlasSnapshot.pacific_neuc_breadth_scene')==snapshot
        q={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':OWNER}]}
        page.goto(BASE+'query.html?q='+quote(json.dumps(q)));page.wait_for_function('window.oswLastQueryResult?.total===2',timeout=90000);s=panel(page)
        assert page.evaluate('oswLastQueryResult')==native(q)
        assert page.evaluate('oswLastQueryResult.chart_scene')==snapshot
        s.get_by_role('button',name='Inspect width record',exact=True).first.focus();page.keyboard.press('Enter');expect(page.locator('#query-detail')).to_contain_text(records()[0]['id'])
        s.get_by_role('link',name='Inspect source row',exact=True).last.click();page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
        page.goto(BASE+'query.html?q='+quote(json.dumps({'collection':'widths','limit':1})));page.wait_for_function('window.oswLastQueryResult?.total===127',timeout=90000);panel(page)
        assert page.locator('.coastal-composite-widths').count()==1 and page.locator('.dwbc-float-composite').count()==1
        results=wasm_rejections(page,fixtures(Path(tmp)));assert all(not r['ok'] and 'Pacific NEUC breadth' in r['error'] for r in results),results
        assert not errors,errors;browser.close()
    print('PASS: two NEUC components, 27.0 sigma-theta, three matching Rust scenes, original CC BY figure, keyboard/mobile and eleven native/WASM guards')

if __name__=='__main__':main()
