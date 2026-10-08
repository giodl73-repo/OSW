"""Model mean support on inspector/atlas/source-query and native/WASM guards."""
import gzip
import json
import os
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright
from test_rust_query_browser import ROOT, CLI, native
from test_guinea_model_width import check_compiled_model_scope

def main():
    query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'guinea'}],'limit':10}
    expected=native(query)
    assert expected['total']==1 and expected['rows'][0]['approximate_width_km']==200
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1280,'height':900});errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=guinea&phase=guinea-djakoure-2017-reference-mean-regional-width')
        page.wait_for_function('window.oswSeasonPlan?.current_id==="guinea"',timeout=90000)
        assert page.locator('#season-title').inner_text()=='Regional model-mean width'
        assert 'annual-mean reference model' in page.locator('#season-value').inner_text()
        chart=page.locator('#regional-width-range .model-regional-width svg')
        assert chart.locator('circle').count()==1 and chart.locator('text').all_text_contents()==['~200 km','0 km','300 km']
        assert 'Numerical uncertainty unknown' in chart.get_attribute('aria-label')
        assert page.locator('#season-play').is_disabled()
        assert page.locator('#season-section-locator').is_hidden()
        assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
        assert 'not calendar dates' in page.locator('#regional-width-range').inner_text()
        assert page.evaluate('oswSeasonPlan.eligible_indices')==[]
        page.set_viewport_size({'width':320,'height':800})
        assert chart.locator('text').first.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12')
        assert chart.locator('text').evaluate_all('(es)=>es.every(e=>{const b=e.getBoundingClientRect(),s=e.ownerSVGElement.getBoundingClientRect();return b.left>=s.left && b.right<=s.right})')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#regional-width-range').screenshot(path=str(ROOT/'.pytest_cache/guinea-model-width-mobile.png'))
        # Switching to a different metric clears this model-specific chart.
        page.locator('#season-current').select_option('somali')
        page.wait_for_function('window.oswSeasonPlan?.current_id==="somali"')
        assert page.locator('.model-regional-width').count()==0
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Aguinea#route-atlas')
        chart=page.locator('#route-atlas-preview .model-regional-width svg');chart.wait_for(state='visible',timeout=90000)
        assert 'reference-model width' in chart.get_attribute('aria-label')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#route-atlas-preview .model-regional-width a').click()
        page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
        request={'document':'research/guinea-djakoure-2017-model-width-source-review.json','pointer':'/measurement','limit':50}
        with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as directory:
            packet=Path(directory)/'index.json'
            packet.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
            source_expected=json.loads(subprocess.check_output([str(CLI),'--index',str(packet),'-'],input=json.dumps(request),encoding='utf8'))
            assert page.evaluate('oswSourceQueryResult')==source_expected
        page.goto('http://127.0.0.1:8788/almanac/query.html?q='+quote(json.dumps(query)))
        page.wait_for_function('window.oswLastQueryResult?.rows.length===1',timeout=90000)
        assert page.evaluate('oswLastQueryResult')==expected
        assert not errors,errors
        browser.close()
    scratch=ROOT/'.pytest_cache/guinea-native-gate';scratch.mkdir(exist_ok=True)
    check_compiled_model_scope(scratch)
    print('PASS: Guinea reference-model mean, unknown uncertainty, no annual/edge inference, mobile chart, cleanup, source query and native/WASM scope guards')

if __name__=='__main__':main()
