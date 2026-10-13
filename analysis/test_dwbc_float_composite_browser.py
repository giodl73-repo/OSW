"""Scoped float diagnostics, native geography, source inspection and WASM guards."""
import gzip,json,os,subprocess,tempfile
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect
from test_rust_query_browser import ROOT,CLI,native
from test_dwbc_float_composite import record,check_native_guard
from antarctic_slope_guard_fixtures import wasm_rejections
from test_motion_dashboard_browser import settle

BASE='http://127.0.0.1:8788/almanac/'
def panel_checks(page):
    panel=page.locator('.dwbc-float-composite');panel.wait_for(state='visible',timeout=90000)
    assert panel.locator('svg').count()==4 and panel.locator('tbody tr').count()==4
    assert panel.locator('[data-width-km="100"]').count()==1
    assert '489, not composite 500' in panel.inner_text()
    assert 'width/transport could be larger' in panel.inner_text()
    assert 'not width errors or confidence intervals' in panel.inner_text()
    assert panel.locator('svg text').evaluate_all('(es)=>es.every(e=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12)')
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    assert panel.locator('.dwbc-composite-scroll').first.evaluate('(e)=>e.scrollWidth>e.clientWidth')
    assert panel.locator('.dwbc-study-geography image').get_attribute('href').endswith('ocean-motion-dashboard-ground.svg')
    return panel

def main():
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as temporary:
        directory=Path(temporary);index=directory/'index.json';index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page=browser.new_page(viewport={'width':320,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(BASE+'reference-routes.html?atlas-feature=current%3Adeep-western-boundary#route-atlas')
            panel=panel_checks(page);assert page.locator('.original-regional-width').count()==0
            panel.screenshot(path=str(ROOT/'.pytest_cache/dwbc-composite-atlas-mobile.png'))
            atlas=page.evaluate('oswAtlasSnapshot.dwbc_float_composite_scene')
            panel.get_by_role('link',name='Inspect width record',exact=True).focus();page.keyboard.press('Enter')
            page.wait_for_function('window.oswSeasonPlan?.current_id==="deep-western-boundary"',timeout=90000)
            panel=panel_checks(page);assert page.evaluate('oswSeasonSnapshot.dwbc_float_composite_scene')==atlas
            assert page.locator('#season-title').inner_text()=='Upper-core float-composite width'
            assert page.locator('#season-play').is_disabled() and page.locator('#season-section-locator').is_hidden()
            panel.screenshot(path=str(ROOT/'.pytest_cache/dwbc-composite-season-mobile.png'))
            panel.get_by_role('link',name='Inspect source row',exact=True).nth(1).click()
            page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
            request={'document':record()['original_regional_context']['audit_file'],'pointer':'/measurement/original_regional_context/source_table_rows/1','limit':50}
            expected=json.loads(subprocess.check_output([str(CLI),'--index',str(index),'-'],input=json.dumps(request),encoding='utf8'))
            assert page.evaluate('oswSourceQueryResult')==expected
            query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'deep-western-boundary'}]}
            page.goto(BASE+'query.html?q='+quote(json.dumps(query)))
            page.wait_for_function('window.oswLastQueryResult?.total===1',timeout=90000)
            panel=panel_checks(page);assert page.evaluate('oswLastQueryResult')==native(query)
            assert page.evaluate('oswLastQueryResult.chart_scene')==atlas
            panel.get_by_role('button',name='Inspect width record',exact=True).click()
            expect(page.locator('#query-detail')).to_contain_text(record()['id'])
            page.goto(BASE+'query.html?q='+quote(json.dumps({'collection':'widths','limit':1})))
            page.wait_for_function('window.oswLastQueryResult?.total===127',timeout=90000)
            assert page.locator('.dwbc-float-composite').count()==1 and page.locator('.coastal-composite-widths').count()==1
            assert page.evaluate('oswLastQueryResult')==native({'collection':'widths','limit':1})
            page.goto(BASE+'dashboard.html');page.wait_for_function('window.oswDashboardSnapshot?.snapshot',timeout=90000)
            for metric in ['scoped_width','time_samples','observed_velocity']:
                page.locator('#dashboard-metric').select_option(metric);settle(page)
                station=page.locator('.beck-station[data-current-id="current:deep-western-boundary"]')
                assert ('lit' in station.get_attribute('class').split())==(metric=='scoped_width')
            owner=native({'collection':'objects','filters':[{'field':'id','op':'eq','value':'current:deep-western-boundary'}]})['rows'][0]
            assert owner['capabilities']['scoped_width']==1 and owner['capabilities']['reference_route']==1
            assert owner['capabilities']['observed_velocity']==0 and owner['capabilities']['time_samples']==0
            page.goto(BASE+'query.html?q='+quote(json.dumps(query)));page.wait_for_function('window.oswLastQueryResult?.total===1',timeout=90000)
            results=wasm_rejections(page,check_native_guard(directory))
            assert all(r['ok'] is False and ('Original regional width' in r['error'] or 'DWBC float composite inventory' in r['error']) for r in results),results
            assert not errors,errors;browser.close()
    print('PASS: float width/subset diagnostics, native study geography, source-index parity, mobile, keyboard, combined comparisons, dashboard scope and ten coherent native/WASM guards')

if __name__=='__main__':main()
