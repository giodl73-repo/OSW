"""Original regional span on inspector/atlas/source query and native/WASM guards."""
import gzip
import json
import os
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright
from test_rust_query_browser import ROOT, CLI, native
from test_original_regional_widths import check_compiled_original_scope

def main():
    query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'algerian'}],'limit':10}
    expected=native(query)
    assert expected['total']==1 and expected['rows'][0]['width_range_km']==[30,50] and expected['rows'][0]['approximate_width_km'] is None
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1280,'height':900});errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=algerian&phase=algerian-cotroneo-2019-regional-width')
        page.wait_for_function('window.oswSeasonPlan?.current_id==="algerian"',timeout=90000)
        assert page.locator('#season-title').inner_text()=='Regional width range'
        assert '30–50 km' in page.locator('#season-value').inner_text()
        chart=page.locator('#regional-width-range .original-regional-width svg')
        assert chart.locator('circle').count()==0 and chart.locator('text').all_text_contents()==['30 km','50 km','0 km','75 km']
        assert 'numerical uncertainty unknown' in chart.get_attribute('aria-label')
        assert page.locator('#season-play').is_disabled()
        assert page.locator('#season-section-locator').is_hidden()
        assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
        assert 'do not define this width' in page.locator('#regional-width-range').inner_text()
        assert page.evaluate('oswSeasonPlan.eligible_indices')==[]
        page.set_viewport_size({'width':320,'height':800})
        assert chart.locator('text').first.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12')
        assert chart.locator('text').evaluate_all('(es)=>es.every(e=>{const b=e.getBoundingClientRect(),s=e.ownerSVGElement.getBoundingClientRect();return b.left>=s.left && b.right<=s.right})')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#regional-width-range').screenshot(path=str(ROOT/'.pytest_cache/algerian-regional-width-mobile.png'))
        # Switching to a different metric clears this model-specific chart.
        page.locator('#season-current').select_option('somali')
        page.wait_for_function('window.oswSeasonPlan?.current_id==="somali"')
        assert page.locator('.original-regional-width').count()==0
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Aalgerian#route-atlas')
        chart=page.locator('#route-atlas-preview .original-regional-width svg');chart.wait_for(state='visible',timeout=90000)
        assert 'Background synthesis' in chart.get_attribute('aria-label')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#route-atlas-preview .original-regional-width a').click()
        page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
        request={'document':'research/algerian-cotroneo-2019-regional-width-scope-audit.json','pointer':'/measurement','limit':50}
        with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as directory:
            packet=Path(directory)/'index.json'
            packet.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
            source_expected=json.loads(subprocess.check_output([str(CLI),'--index',str(packet),'-'],input=json.dumps(request),encoding='utf8'))
            assert page.evaluate('oswSourceQueryResult')==source_expected
        page.goto('http://127.0.0.1:8788/almanac/query.html?q='+quote(json.dumps(query)))
        page.wait_for_function('window.oswLastQueryResult?.rows.length===1',timeout=90000)
        assert page.evaluate('oswLastQueryResult')==expected
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=alaska&phase=alaska-weingartner-2002-regional-width')
        page.wait_for_function('window.oswSeasonPlan?.current_id==="alaska"',timeout=90000)
        assert page.locator('#season-title').inner_text()=='Regional width summary'
        assert '300 km' in page.locator('#season-value').inner_text()
        chart=page.locator('#regional-width-range .original-regional-width svg')
        assert chart.locator('circle').count()==1 and chart.locator('line').count()==1
        assert chart.locator('text').all_text_contents()==['≈ 300 km','0 km','325 km']
        assert 'No width range supplied' in chart.get_attribute('aria-label')
        assert page.locator('#season-play').is_disabled() and page.evaluate('oswSeasonPlan.eligible_indices')==[]
        assert page.locator('#season-section-locator').is_hidden()
        assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert chart.locator('text').first.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12')
        assert chart.locator('text').evaluate_all('(es)=>es.every(e=>{const b=e.getBoundingClientRect(),s=e.ownerSVGElement.getBoundingClientRect();return b.left>=s.left && b.right<=s.right})')
        page.locator('#regional-width-range').screenshot(path=str(ROOT/'.pytest_cache/alaska-regional-width-mobile.png'))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Aalaska#route-atlas')
        chart=page.locator('#route-atlas-preview .original-regional-width svg');chart.wait_for(state='visible',timeout=90000)
        assert chart.locator('circle').count()==1 and chart.locator('line').count()==1
        page.locator('#route-atlas-preview .original-regional-width a').click()
        page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
        request={'document':'research/alaska-weingartner-2002-regional-width-scope-audit.json','pointer':'/measurement','limit':50}
        with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as directory:
            packet=Path(directory)/'index.json';packet.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
            source_expected=json.loads(subprocess.check_output([str(CLI),'--index',str(packet),'-'],input=json.dumps(request),encoding='utf8'))
            assert page.evaluate('oswSourceQueryResult')==source_expected
        query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'alaska'}],'limit':100}
        expected=native(query)
        page.goto('http://127.0.0.1:8788/almanac/query.html?q='+quote(json.dumps(query)))
        page.wait_for_function('window.oswLastQueryResult?.rows.length===1',timeout=90000)
        assert page.evaluate('oswLastQueryResult')==expected
        assert not errors,errors
        browser.close()
    scratch=ROOT/'.pytest_cache/algerian-native-gate';scratch.mkdir(exist_ok=True)
    check_compiled_original_scope(scratch)
    print('PASS: Algerian span and Alaska approximate point, no survey/forcing support inference, mobile charts, cleanup, source queries and native/WASM scope guards')

if __name__=='__main__':main()
