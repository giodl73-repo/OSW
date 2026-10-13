"""Occupied-band graphic, source pointers, mobile and native/WASM scope bindings."""
import gzip,json,os,subprocess,tempfile
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright
from test_rust_query_browser import ROOT,CLI,native
from test_tasman_front_band import records,check_native_guard
from antarctic_slope_guard_fixtures import wasm_rejections
from test_motion_dashboard_browser import settle,native_selection


def main():
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as temporary:
        directory=Path(temporary);index=directory/'index.json';index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page=browser.new_page(viewport={'width':320,'height':800});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Atasman-front#route-atlas')
            panels=page.locator('#route-atlas-preview .original-regional-width');panels.first.wait_for(state='visible',timeout=90000)
            assert panels.count()==1
            for i,row in enumerate(records()):
                panel=panels.nth(i)
                assert f"Approximately {row['approximate_width_km']} km" in panel.inner_text()
                assert row['original_regional_context']['display_caption'] in panel.inner_text()
                assert 'not individual jet width' in panel.locator('svg').get_attribute('aria-label')
                assert panel.locator('svg circle').count()==1
                assert panel.locator('svg text').evaluate_all('(es)=>es.every(e=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12)')
                panel.screenshot(path=str(ROOT/'.pytest_cache'/f"tasman-front-{row['approximate_width_km']}-width-mobile.png"))
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            for row in records():
                page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=tasman-front&phase='+row['id'])
                page.wait_for_function('window.oswSeasonPlan?.current_id==="tasman-front"',timeout=90000)
                assert page.locator('#season-title').inner_text()==row['original_regional_context']['display_title']
                assert page.locator('#season-play').is_disabled()
                assert page.evaluate('!oswSeasonPlan.eligible_indices.includes(Number(document.querySelector("#season-phase").value)) && oswSeasonPlan.phases[Number(document.querySelector("#season-phase").value)].playback_step_eligible===false')
                assert page.locator('#season-section-locator').is_hidden()
                panel=page.locator('#regional-width-range .original-regional-width');assert 'numerical uncertainty unknown' in panel.inner_text().lower()
                panel.locator('a').click();page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
                request={'document':row['original_regional_context']['audit_file'],'pointer':row['original_regional_context']['audit_pointer'],'limit':50}
                expected=json.loads(subprocess.check_output([str(CLI),'--index',str(index),'-'],input=json.dumps(request),encoding='utf8'))
                assert page.evaluate('oswSourceQueryResult')==expected
            query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'tasman-front'}],'limit':100}
            page.goto('http://127.0.0.1:8788/almanac/query.html?q='+quote(json.dumps(query)))
            page.wait_for_function('window.oswLastQueryResult?.total===1',timeout=90000)
            assert page.evaluate('oswLastQueryResult')==native(query)
            results=wasm_rejections(page,check_native_guard(directory))
            assert all(r['ok'] is False and 'Original regional width' in r['error'] for r in results),results
            page.goto('http://127.0.0.1:8788/almanac/dashboard.html')
            page.wait_for_function('window.oswDashboardSnapshot',timeout=90000);settle(page)
            for metric,covered in [('geometry',False),('time_samples',False),('scoped_width',True)]:
                page.locator('#dashboard-metric').select_option(metric);settle(page)
                selection=page.evaluate('oswDashboardSelection')
                assert selection['result']==native_selection(selection['request'])
                station=next(s for s in selection['result']['beck_scene']['stations'] if s['id']=='current:tasman-front')
                assert station['covered'] is covered
            page.locator('#dashboard-card-view').click()
            card=page.locator('[data-id="current:tasman-front"]');assert 'lit' in card.get_attribute('class')
            assert 'Scoped width evidence: 1 record' in card.inner_text()
            card.screenshot(path=str(ROOT/'.pytest_cache/tasman-front-dashboard-mobile.png'))
            card.locator('h3 a').click()
            page.locator('#route-atlas-preview .original-regional-width').wait_for(state='visible',timeout=90000)
            assert records()[0]['original_regional_context']['display_caption'] in page.locator('#route-atlas-preview').inner_text()
            assert not errors,errors;browser.close()
    print('PASS: distinct Tasman occupied-band width, mobile, dashboard light/navigation, source/query parity, and eight coherent native/WASM support rejections')


if __name__=='__main__':main()
