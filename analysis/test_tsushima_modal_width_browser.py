"""Modal estimate on map card, inspector and lossless native/WASM queries."""
import copy
import gzip
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright
from test_rust_query_browser import ROOT, CLI, native
from check_tsushima_modal_width import AUDIT

def main():
    query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'tsushima'}],'limit':50}
    expected=native(query)
    assert expected['total']==1 and expected['rows'][0]['approximate_width_km']==22
    request={'document':AUDIT,'pointer':'/measurement/modal_decay_context','limit':50}
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as directory:
        index=Path(directory)/'index.json';index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        source_expected=json.loads(subprocess.check_output([str(CLI),'--index',str(index),'-'],input=json.dumps(request),encoding='utf8'))
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page=browser.new_page(viewport={'width':1280,'height':900});errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Atsushima#route-atlas')
            figure=page.locator('#route-atlas-preview .modal-decay-width');figure.wait_for(state='visible',timeout=90000)
            assert figure.locator('dd').all_text_contents()==['22 km','About 20 km','23.1 km']
            assert 'Arithmetic discrepancy unresolved' in figure.inner_text()
            assert 'differential-equation sign remains unresolved' in figure.inner_text()
            assert 'Relative amplitude (model)' in figure.locator('svg').text_content()
            assert 'No observed offshore profile' in figure.locator('svg').get_attribute('aria-label')
            page.set_viewport_size({'width':320,'height':800})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            assert figure.locator('svg text').evaluate_all('(es)=>es.every(e=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12)')
            assert figure.locator('svg text').evaluate_all('(es)=>es.every(e=>{const b=e.getBoundingClientRect(),s=e.ownerSVGElement.getBoundingClientRect();return b.left>=s.left && b.right<=s.right})')
            figure.get_by_text('Unresolved equation sign',exact=True).click()
            assert 'does not validate the printed differential equation' in figure.inner_text()
            figure.screenshot(path=str(ROOT/'.pytest_cache/tsushima-modal-width-mobile.png'))
            figure.get_by_role('link',name='Inspect method, dates and source').click()
            page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
            assert page.evaluate('oswSourceQueryResult')==source_expected
            page.goto('http://127.0.0.1:8788/almanac/query.html?q='+quote(json.dumps(query)))
            page.wait_for_function('window.oswLastQueryResult?.total===1',timeout=90000)
            assert page.evaluate('oswLastQueryResult')==expected
            page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=tsushima&phase=tsushima-matsuyama-1990-nearshore-modal-width')
            page.wait_for_function('window.oswSeasonPlan?.current_id==="tsushima"',timeout=90000)
            assert page.locator('#season-title').inner_text()=='Campaign modal decay estimate'
            assert page.locator('#season-play').is_disabled() and page.evaluate('oswSeasonPlan.eligible_indices')==[]
            assert page.locator('#season-section-locator').is_hidden()
            assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
            assert page.locator('#regional-width-range .modal-decay-width').count()==1
            assert '26 July–14 August' in page.locator('#regional-width-range').inner_text()
            page.locator('#season-current').select_option('somali')
            page.wait_for_function('window.oswSeasonPlan?.current_id==="somali"')
            assert page.locator('.modal-decay-width').count()==0
            assert not errors,errors
            browser.close()
        packet=json.loads((ROOT/'almanac/query-data.json').read_bytes())
        for key,value in [('approximate_width_km',23.076923),('width_range_km',[20,22]),('calendar_months',[7,8]),('seasonal_playback_eligible',True),('modal_decay_context',{})]:
            bad=copy.deepcopy(packet);receipt=bad['manifest']['seasons_receipts']['widths'];doc=json.loads(receipt['source_json'])
            next(r for r in doc['measurements'] if r['current_id']=='tsushima')[key]=value
            next(r for r in bad['collections']['widths'] if r['current_id']=='tsushima')[key]=value
            receipt['source_json']=json.dumps(doc);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest()
            bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
            target=Path(directory)/'tampered.json';target.write_text(json.dumps(bad),encoding='utf8')
            result=subprocess.run([str(CLI),str(target),'-'],input=json.dumps(query),capture_output=True,text=True,encoding='utf8')
            assert result.returncode==2 and 'Tsushima modal' in result.stderr,result.stderr
        # Exercise the compiled WASM admission itself, bypassing client hash checks.
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page=browser.new_page()
            page.route('**/modal-guard.html',lambda route:route.fulfill(body='<!doctype html><title>Modal admission check</title>',content_type='text/html'))
            page.goto('http://127.0.0.1:8788/modal-guard.html')
            result=page.evaluate('''async path=>{
              const wasm=await (await fetch('/almanac/query-engine.wasm')).arrayBuffer();
              const {instance}=await WebAssembly.instantiate(wasm,{}),e=instance.exports;
              const data=new Uint8Array(await (await fetch(path)).arrayBuffer());
              const ptr=e.osw_alloc(data.length);
              try{new Uint8Array(e.memory.buffer,ptr,data.length).set(data);e.osw_load(ptr,data.length);
                return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));
              }finally{e.osw_dealloc(ptr,data.length);}
            }''','/'+target.relative_to(ROOT).as_posix())
            assert result['ok'] is False and 'Tsushima modal' in result['error'],result
            browser.close()
    print('PASS: Tsushima modal card, mobile, inspector, native/WASM query parity and coherent scope-mutation rejection')

if __name__=='__main__':main()
