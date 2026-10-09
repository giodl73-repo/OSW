"""Shared composite scene, source map integrity, mobile and native/WASM parity."""
import gzip,json,os,subprocess,tempfile
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright
from test_rust_query_browser import ROOT,CLI,native
from test_motion_dashboard_browser import settle
from test_antarctic_coastal_composites import records,check_native_guard
from antarctic_slope_guard_fixtures import wasm_rejections

BASE='http://127.0.0.1:8788/almanac/'
def check_panel(page):
    panel=page.locator('.coastal-composite-widths');panel.wait_for(state='visible',timeout=90000)
    image=panel.locator('.coastal-source-image');image.wait_for(state='visible',timeout=15000)
    assert image.evaluate('(i)=>i.complete&&i.naturalWidth===1474&&i.naturalHeight===912')
    assert panel.locator('svg [data-section-id]').count()==7
    assert panel.locator('tbody tr').count()==7
    assert 'Section 6 conflicts' in panel.inner_text()
    assert panel.locator('svg text').evaluate_all('(es)=>es.every(e=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12)')
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    assert panel.locator('.coastal-composite-scroll').first.evaluate('(e)=>e.scrollWidth>e.clientWidth')
    return panel

def main():
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as temporary:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page=browser.new_page(viewport={'width':320,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(BASE+'reference-routes.html?atlas-feature=current%3Aantarctic-coastal#route-atlas')
            panel=check_panel(page);assert page.locator('.original-regional-width').count()==0
            panel.screenshot(path=str(ROOT/'.pytest_cache/coastal-composites-mobile.png'))
            atlas=page.evaluate('oswAtlasSnapshot.coastal_composite_width_scene')
            panel.get_by_role('link',name='Section 6',exact=True).focus();page.keyboard.press('Enter')
            page.wait_for_function('window.oswSeasonPlan?.current_id==="antarctic-coastal"',timeout=90000)
            panel=check_panel(page)
            assert page.locator('#season-title').inner_text()=='Composite section 6'
            assert page.locator('#season-play').is_disabled() and page.locator('#season-section-locator').is_hidden()
            assert panel.locator('svg [data-selected="true"]').get_attribute('data-section-id')==records()[5]['id']
            assert page.evaluate('oswSeasonSnapshot.coastal_composite_width_scene')==atlas
            query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'antarctic-coastal'}],'limit':1}
            page.goto(BASE+'query.html?q='+quote(json.dumps(query)))
            page.wait_for_function('window.oswLastQueryResult?.total===7',timeout=90000)
            panel=check_panel(page);assert page.evaluate('oswLastQueryResult')==native(query)
            assert page.evaluate('oswLastQueryResult.chart_scene')==atlas
            panel.get_by_role('button',name='Section 6',exact=True).click()
            page.wait_for_function('document.querySelector("#query-detail").textContent.includes('+json.dumps(records()[5]['id'])+')',timeout=15000)
            panel.get_by_role('link',name='Inspect the published values and extraction scope').click()
            page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
            index=Path(temporary)/'index.json';index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
            request={'document':records()[0]['original_regional_context']['audit_file'],'pointer':'/measurements','limit':50}
            expected=json.loads(subprocess.check_output([str(CLI),'--index',str(index),'-'],input=json.dumps(request),encoding='utf8'))
            assert page.evaluate('oswSourceQueryResult')==expected
            page.goto(BASE+'dashboard.html');page.wait_for_function('window.oswDashboardSnapshot?.snapshot',timeout=90000)
            for metric in ['scoped_width','geometry','time_samples','observed_velocity']:
                page.locator('#dashboard-metric').select_option(metric);settle(page)
                station=page.locator('.beck-station[data-current-id="current:antarctic-coastal"]')
                assert ('lit' in station.get_attribute('class').split())==(metric=='scoped_width')
            object_query={'collection':'objects','filters':[{'field':'id','op':'eq','value':'current:antarctic-coastal'}]}
            owner=native(object_query)['rows'][0];assert owner['capabilities']['scoped_width']==7
            assert all(owner['capabilities'][k]==0 for k in ['geometry','time_samples','observed_velocity'])
            page.goto(BASE+'query.html?q='+quote(json.dumps(query)))
            page.wait_for_function('window.oswLastQueryResult?.total===7',timeout=90000)
            results=wasm_rejections(page,check_native_guard(Path(temporary)))
            assert all(r['ok'] is False and ('Original regional width' in r['error'] or 'Coastal composite seven-section' in r['error']) for r in results),results
            # A fresh page has no verified map cache; corrupt bytes must not display.
            broken=browser.new_page(viewport={'width':320,'height':900})
            broken.route('**/schubert-aacc-2021-source-sections.png',lambda route:route.fulfill(status=200,body=b'changed source map',content_type='image/png'))
            broken.goto(BASE+'seasons.html?current=antarctic-coastal&phase='+records()[0]['id'])
            broken.locator('.coastal-source-image-status[data-error="true"]').wait_for(timeout=90000)
            assert broken.locator('.coastal-source-image').count()==0
            assert not errors,errors;browser.close()
    print('PASS: seven-section scene shared across atlas/seasons/query, verified source map, mobile, keyboard navigation and nine coherent native/WASM rejections')

if __name__=='__main__':main()
