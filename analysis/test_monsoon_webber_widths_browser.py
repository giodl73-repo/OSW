"""Separate width cards, source pointers, mobile and native/WASM scope bindings."""
import gzip,json,os,subprocess,tempfile
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright
from test_rust_query_browser import ROOT,CLI,native
from test_monsoon_webber_widths import records,check_native_guard
from antarctic_slope_guard_fixtures import wasm_rejections


def main():
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as temporary:
        directory=Path(temporary);index=directory/'index.json';index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page=browser.new_page(viewport={'width':320,'height':800});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Amonsoon#route-atlas')
            panels=page.locator('#route-atlas-preview .original-regional-width');panels.first.wait_for(state='visible',timeout=90000)
            assert panels.count()==2
            for i,row in enumerate(records()):
                panel=panels.nth(i)
                assert f"Approximately {row['approximate_width_km']} km" in panel.inner_text()
                assert row['original_regional_context']['display_title'] in panel.inner_text()
                assert 'July 2016' in panel.locator('svg').get_attribute('aria-label')
                assert panel.locator('svg circle').count()==1
                assert panel.locator('svg text').evaluate_all('(es)=>es.every(e=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12)')
                panel.screenshot(path=str(ROOT/'.pytest_cache'/f"monsoon-{row['approximate_width_km']}-width-mobile.png"))
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            for row in records():
                page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=monsoon&phase='+row['id'])
                page.wait_for_function('window.oswSeasonPlan?.current_id==="monsoon"',timeout=90000)
                assert page.locator('#season-title').inner_text()==row['original_regional_context']['display_title']
                assert page.locator('#season-play').is_disabled()
                assert page.evaluate('!oswSeasonPlan.eligible_indices.includes(Number(document.querySelector("#season-phase").value)) && oswSeasonPlan.phases[Number(document.querySelector("#season-phase").value)].playback_step_eligible===false')
                assert page.locator('#season-section-locator').is_hidden()
                panel=page.locator('#regional-width-range .original-regional-width');assert 'Numerical uncertainty unknown' in panel.inner_text()
                panel.locator('a').click();page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
                request={'document':row['original_regional_context']['audit_file'],'pointer':row['original_regional_context']['audit_pointer'],'limit':50}
                expected=json.loads(subprocess.check_output([str(CLI),'--index',str(index),'-'],input=json.dumps(request),encoding='utf8'))
                assert page.evaluate('oswSourceQueryResult')==expected
            page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=monsoon')
            page.wait_for_function('window.oswSeasonPlan?.current_id==="monsoon"',timeout=90000)
            assert len(page.evaluate('oswSeasonPlan.eligible_indices'))==2
            assert page.locator('#season-play').is_enabled()
            page.locator('#season-play').click()
            page.wait_for_function('document.querySelector("#season-phase").value!==String(oswSeasonPlan.eligible_indices[0])',timeout=10000)
            assert page.evaluate('oswSeasonPlan.eligible_indices.includes(Number(document.querySelector("#season-phase").value))')
            page.locator('#season-play').click()
            query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'monsoon'}],'limit':100}
            page.goto('http://127.0.0.1:8788/almanac/query.html?q='+quote(json.dumps(query)))
            page.wait_for_function('window.oswLastQueryResult?.total===2',timeout=90000)
            assert page.evaluate('oswLastQueryResult')==native(query)
            results=wasm_rejections(page,check_native_guard(directory))
            assert all(r['ok'] is False and 'Original regional width' in r['error'] for r in results),results
            assert not errors,errors;browser.close()
    print('PASS: distinct Monsoon flow/origin widths, mobile, source/query parity, and six coherent native/WASM support rejections')


if __name__=='__main__':main()
