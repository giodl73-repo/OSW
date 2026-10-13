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
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=pacific-equatorial-undercurrent&phase=pacific-euc-wang-2022-background-width')
        page.wait_for_function('window.oswSeasonPlan?.current_id==="pacific-equatorial-undercurrent"',timeout=90000)
        assert page.locator('#season-title').inner_text()=='Regional width summary'
        assert '400 km' in page.locator('#season-value').inner_text()
        chart=page.locator('#regional-width-range .original-regional-width svg')
        assert chart.locator('circle').count()==1 and chart.locator('line').count()==1
        assert chart.locator('text').all_text_contents()==['≈ 400 km','0 km','425 km']
        assert page.locator('#season-play').is_disabled() and page.evaluate('oswSeasonPlan.eligible_indices')==[]
        assert page.locator('#season-section-locator').is_hidden()
        assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
        assert '3°S–3°N transport box is not a width observation' in page.locator('#regional-width-range').inner_text()
        assert chart.locator('text').first.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12')
        assert chart.locator('text').evaluate_all('(es)=>es.every(e=>{const b=e.getBoundingClientRect(),s=e.ownerSVGElement.getBoundingClientRect();return b.left>=s.left && b.right<=s.right})')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#regional-width-range').screenshot(path=str(ROOT/'.pytest_cache/pacific-euc-background-width-mobile.png'))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Apacific-equatorial-undercurrent#route-atlas')
        chart=page.locator('#route-atlas-preview .original-regional-width svg');chart.wait_for(state='visible',timeout=90000)
        assert chart.locator('circle').count()==1 and chart.locator('line').count()==1
        page.locator('#route-atlas-preview .original-regional-width a').click()
        page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
        request={'document':'research/pacific-euc-wang-2022-background-width-scope-audit.json','pointer':'/measurement','limit':50}
        with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as directory:
            packet=Path(directory)/'index.json';packet.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
            source_expected=json.loads(subprocess.check_output([str(CLI),'--index',str(packet),'-'],input=json.dumps(request),encoding='utf8'))
            assert page.evaluate('oswSourceQueryResult')==source_expected
        query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'pacific-equatorial-undercurrent'}],'limit':100}
        expected=native(query)
        page.goto('http://127.0.0.1:8788/almanac/query.html?q='+quote(json.dumps(query)))
        page.wait_for_function('window.oswLastQueryResult?.rows.length===1',timeout=90000)
        assert page.evaluate('oswLastQueryResult')==expected
        assert expected['rows'][0]['approximate_width_km']==400 and expected['rows'][0]['fixed_layer_bounds_m'] is None
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=atlantic-equatorial-undercurrent&phase=atlantic-euc-gouriou-1988-background-width')
        page.wait_for_function('window.oswSeasonPlan?.current_id==="atlantic-equatorial-undercurrent"',timeout=90000)
        assert '200 km' in page.locator('#season-value').inner_text()
        chart=page.locator('#regional-width-range .original-regional-width svg')
        assert chart.locator('circle').count()==1 and chart.locator('line').count()==1
        assert chart.locator('text').all_text_contents()==['\u2248 200 km','0 km','225 km']
        assert page.locator('#season-play').is_disabled() and page.evaluate('oswSeasonPlan.eligible_indices')==[]
        assert page.locator('#season-section-locator').is_hidden() and page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
        assert 'not two width samples' in page.locator('#regional-width-range').inner_text()
        assert chart.locator('text').first.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12')
        assert chart.locator('text').evaluate_all('(es)=>es.every(e=>{const b=e.getBoundingClientRect(),s=e.ownerSVGElement.getBoundingClientRect();return b.left>=s.left && b.right<=s.right})')
        page.locator('#regional-width-range').screenshot(path=str(ROOT/'.pytest_cache/atlantic-euc-background-width-mobile.png'))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Aatlantic-equatorial-undercurrent#route-atlas')
        chart=page.locator('#route-atlas-preview .original-regional-width svg');chart.wait_for(state='visible',timeout=90000)
        assert chart.locator('circle').count()==1 and chart.locator('line').count()==1
        page.locator('#route-atlas-preview .original-regional-width a').click()
        page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
        request={'document':'research/atlantic-euc-gouriou-1988-background-width-scope-audit.json','pointer':'/measurement','limit':50}
        with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as directory:
            packet=Path(directory)/'index.json';packet.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
            source_expected=json.loads(subprocess.check_output([str(CLI),'--index',str(packet),'-'],input=json.dumps(request),encoding='utf8'))
            assert page.evaluate('oswSourceQueryResult')==source_expected
        query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'atlantic-equatorial-undercurrent'}],'limit':100}
        expected=native(query)
        page.goto('http://127.0.0.1:8788/almanac/query.html?q='+quote(json.dumps(query)))
        page.wait_for_function('window.oswLastQueryResult?.rows.length===1',timeout=90000)
        assert page.evaluate('oswLastQueryResult')==expected
        assert expected['rows'][0]['approximate_width_km']==200 and expected['rows'][0]['fixed_layer_bounds_m'] is None
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=kuroshio-extension&phase=kuroshio-extension-sasaki-2013-monthly-field-width')
        page.wait_for_function('window.oswSeasonPlan?.current_id==="kuroshio-extension"',timeout=90000)
        chart=page.locator('#regional-width-range .original-regional-width svg')
        assert chart.locator('circle').count()==1 and chart.locator('line').count()==1
        assert chart.locator('text').all_text_contents()==['\u2248 100 km','0 km','125 km']
        assert 'monthly mean fields' in chart.get_attribute('aria-label')
        assert '200 km' in page.locator('#regional-width-range').inner_text()
        assert 'seasonal range' in page.locator('#regional-width-range').inner_text()
        assert page.locator('#season-play').is_disabled() and page.evaluate('oswSeasonPlan.eligible_indices')==[]
        assert page.locator('#season-section-locator').is_hidden() and page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
        assert chart.locator('text').first.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12')
        assert chart.locator('text').evaluate_all('(es)=>es.every(e=>{const b=e.getBoundingClientRect(),s=e.ownerSVGElement.getBoundingClientRect();return b.left>=s.left && b.right<=s.right})')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#regional-width-range').screenshot(path=str(ROOT/'.pytest_cache/kuroshio-extension-width-mobile.png'))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Akuroshio-extension#route-atlas')
        chart=page.locator('#route-atlas-preview .original-regional-width svg');chart.wait_for(state='visible',timeout=90000)
        assert 'monthly mean fields' in chart.get_attribute('aria-label')
        page.locator('#route-atlas-preview .original-regional-width a').click()
        page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
        request={'document':'research/kuroshio-extension-sasaki-2013-width-averaging-scope-audit.json','pointer':'/measurement','limit':50}
        with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as directory:
            packet=Path(directory)/'index.json';packet.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
            source_expected=json.loads(subprocess.check_output([str(CLI),'--index',str(packet),'-'],input=json.dumps(request),encoding='utf8'))
            assert page.evaluate('oswSourceQueryResult')==source_expected
        query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'kuroshio-extension'}],'limit':100}
        expected=native(query)
        page.goto('http://127.0.0.1:8788/almanac/query.html?q='+quote(json.dumps(query)))
        page.wait_for_function('window.oswLastQueryResult?.rows.length===1',timeout=90000)
        assert page.evaluate('oswLastQueryResult')==expected
        assert expected['rows'][0]['approximate_width_km']==100 and expected['rows'][0]['width_range_km'] is None
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=new-guinea-coastal-undercurrent&phase=ngcu-zenk-1999-vitiaz-width-constraint')
        page.wait_for_function('window.oswSeasonPlan?.current_id==="new-guinea-coastal-undercurrent"',timeout=90000)
        assert page.locator('#season-title').inner_text()=='Reported band size constraint'
        assert 'O(<20 km)' in page.locator('#season-value').inner_text()
        chart=page.locator('#regional-width-range .reported-width-constraint svg')
        assert chart.locator('circle,line,path').count()==0
        assert chart.locator('text').all_text_contents()==['O(<20 km)','Reported size constraint']
        assert 'not a measured 20 km width' in chart.get_attribute('aria-label')
        assert 'no 40 km width' in page.locator('#regional-width-range').inner_text()
        assert page.locator('#season-play').is_disabled() and page.evaluate('oswSeasonPlan.eligible_indices')==[]
        assert page.locator('#season-section-locator').is_hidden() and page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
        assert chart.locator('text').first.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12')
        assert chart.locator('text').evaluate_all('(es)=>es.every(e=>{const b=e.getBoundingClientRect(),s=e.ownerSVGElement.getBoundingClientRect();return b.left>=s.left && b.right<=s.right})')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#regional-width-range').screenshot(path=str(ROOT/'.pytest_cache/ngcu-width-constraint-mobile.png'))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Anew-guinea-coastal-undercurrent#route-atlas')
        chart=page.locator('#route-atlas-preview .reported-width-constraint svg');chart.wait_for(state='visible',timeout=90000)
        assert 'O(<20 km)' in page.locator('#width-ngcu-zenk-1999-vitiaz-width-constraint').inner_text()
        assert 'O(<20 km)' in page.locator('#route-atlas-preview .atlas-width-record summary').inner_text()
        page.locator('#route-atlas-preview .reported-width-constraint a').click()
        page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
        request={'document':'research/ngcu-zenk-1999-width-constraint-scope-audit.json','pointer':'/measurement','limit':50}
        with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as directory:
            packet=Path(directory)/'index.json';packet.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
            source_expected=json.loads(subprocess.check_output([str(CLI),'--index',str(packet),'-'],input=json.dumps(request),encoding='utf8'))
            assert page.evaluate('oswSourceQueryResult')==source_expected
        query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'new-guinea-coastal-undercurrent'}],'limit':100}
        expected=native(query)
        page.goto('http://127.0.0.1:8788/almanac/query.html?q='+quote(json.dumps(query)))
        page.wait_for_function('window.oswLastQueryResult?.rows.length===1',timeout=90000)
        assert page.evaluate('oswLastQueryResult')==expected
        assert expected['rows'][0]['approximate_width_km'] is None and expected['rows'][0]['width_range_km'] is None
        assert expected['rows'][0]['reported_width_constraint']['reference_scale_km']==20
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=west-australian&phase=west-australian-glenn-2008-offshore-breadth-constraint')
        page.wait_for_function('window.oswSeasonPlan?.current_id==="west-australian"',timeout=90000)
        assert page.locator('#season-title').inner_text()=='Reported offshore breadth'
        chart=page.locator('#regional-width-range .reported-width-constraint svg')
        assert chart.locator('circle,line,path').count()==0
        assert chart.locator('text').all_text_contents()==['>1000 km','Reported offshore breadth']
        assert 'not a measured velocity-core width' in chart.get_attribute('aria-label')
        assert page.locator('#season-play').is_disabled() and page.evaluate('oswSeasonPlan.eligible_indices')==[]
        assert chart.locator('text').evaluate_all('(es)=>es.every(e=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12)')
        assert chart.locator('text').evaluate_all('(es)=>es.every(e=>{const b=e.getBoundingClientRect(),s=e.ownerSVGElement.getBoundingClientRect();return b.left>=s.left && b.right<=s.right})')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#regional-width-range').screenshot(path=str(ROOT/'.pytest_cache/wac-breadth-mobile.png'))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Awest-australian#route-atlas')
        chart=page.locator('#route-atlas-preview .reported-width-constraint svg');chart.wait_for(state='visible',timeout=90000)
        page.locator('#route-atlas-preview .reported-width-constraint a').click()
        page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
        request={'document':'research/west-australian-glenn-2008-breadth-scope-audit.json','pointer':'/measurement','limit':50}
        with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as directory:
            packet=Path(directory)/'index.json';packet.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
            source_expected=json.loads(subprocess.check_output([str(CLI),'--index',str(packet),'-'],input=json.dumps(request),encoding='utf8'))
            assert page.evaluate('oswSourceQueryResult')==source_expected
        query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'west-australian'}],'limit':100}
        page.goto('http://127.0.0.1:8788/almanac/query.html?q='+quote(json.dumps(query)))
        page.wait_for_function('window.oswLastQueryResult?.rows.length===1',timeout=90000)
        assert page.evaluate('oswLastQueryResult')==native(query)
        for owner in ['equatorial-undercurrent']:
            assert native({'collection':'widths','filters':[{'field':'current_id','op':'eq','value':owner}],'limit':100})['total']==0
        assert not errors,errors
        browser.close()
    scratch=ROOT/'.pytest_cache/algerian-native-gate';scratch.mkdir(exist_ok=True)
    check_compiled_original_scope(scratch)
    # Bypass browser receipt checks to exercise compiled WASM admission directly.
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page()
        page.route('**/wac-guard.html',lambda route:route.fulfill(body='<!doctype html><title>Breadth admission check</title>',content_type='text/html'))
        page.goto('http://127.0.0.1:8788/wac-guard.html')
        result=page.evaluate("""async path=>{
          const wasm=await (await fetch('/almanac/query-engine.wasm')).arrayBuffer();
          const {instance}=await WebAssembly.instantiate(wasm,{}),e=instance.exports;
          const data=new Uint8Array(await (await fetch(path)).arrayBuffer()),ptr=e.osw_alloc(data.length);
          try{new Uint8Array(e.memory.buffer,ptr,data.length).set(data);e.osw_load(ptr,data.length);
            return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));
          }finally{e.osw_dealloc(ptr,data.length);}
        }""",'/'+(scratch/'wac-tampered.json').relative_to(ROOT).as_posix())
        assert result['ok'] is False and 'Original regional width' in result['error'],result
        browser.close()
    print('PASS: original regional spans/points, Kuroshio Extension averaging NGCU qualified size constraint and West Australian breadth; mobile card/table/inspector, source queries, native/WASM parity and coherent scope mutation guards')

if __name__=='__main__':main()
