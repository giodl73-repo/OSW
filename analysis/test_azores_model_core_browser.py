"""Published model-core widths retain quarters, sources and unadmitted scope."""
from query_packet import read_bundle_bytes
import copy,json,os,subprocess
from tempfile import TemporaryDirectory
from urllib.parse import quote
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from test_rust_query_browser import ROOT,CLI,native,browser_query

def main():
    out=ROOT/'.pytest_cache/azores-integration';out.mkdir(parents=True,exist_ok=True)
    bundle=json.loads(read_bundle_bytes(ROOT/'almanac/query-data.json'))
    q={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'azores'}],'limit':100}
    expected=native(q);assert expected['total']==3
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1200,'height':950});page.emulate_media(reduced_motion='reduce')
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        for phase,value,months in [('spring',240,'April-June'),('autumn',400,'October-December')]:
            identifier='azores-carracedo-2014-'+phase+'-core-width'
            page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=azores&phase='+identifier)
            page.wait_for_function('window.oswSeasonSnapshot',timeout=60000)
            expect(page.locator('#regional-width-range')).to_contain_text(months)
            expect(page.locator('#regional-width-range')).to_contain_text(str(value)+' km')
            expect(page.locator('#regional-width-range')).to_contain_text('width uncertainty remain unknown')
            expect(page.locator('#regional-width-range')).to_contain_text('1 degree')
            assert page.get_by_role('link',name='Compare reported seasonal model-core widths').count()==1
            source=page.get_by_role('link',name='Inspect regional width scope and source').get_attribute('href')
            page.locator('#season-atlas').click()
            page.wait_for_function('document.querySelector("#route-atlas-select").value==="current:azores"',timeout=60000)
            expect(page.locator('#width-'+identifier)).to_contain_text(str(value)+' km')
            page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=azores&phase='+identifier)
            page.wait_for_function('window.oswSeasonSnapshot',timeout=60000)
            page.set_viewport_size({'width':320,'height':900})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.locator('#regional-width-range').screenshot(path=str(out/(phase+'-mobile.png')))
            page.set_viewport_size({'width':1200,'height':950})
            page.goto('http://127.0.0.1:8788/almanac/'+source)
            page.wait_for_function('window.oswSourceQueryResult',timeout=60000)
            assert page.evaluate('window.oswSourceQueryResult.total')>0
        page.goto('http://127.0.0.1:8788/almanac/query.html')
        page.wait_for_function('window.oswLastQueryResult',timeout=60000)
        assert browser_query(page,q)==expected
        model=[r for r in expected['rows'] if r['id'].startswith('azores-carracedo-2014-')]
        assert {r['source_season_label']:r['calendar_months'] for r in model}=={'spring':[4,5,6],'autumn':[10,11,12]}
        assert all(r['full_width_inference_eligible'] is False and r['observed_period'] is None for r in model)
        page.route('**/azores-guard.html',lambda route:route.fulfill(body='<title>Azores source guard</title>',content_type='text/html'))
        page.goto('http://127.0.0.1:8788/azores-guard.html')
        for mode in ['calendar','promotion','missing','rebound']:
            bad=copy.deepcopy(bundle);row=next(r for r in bad['collections']['widths'] if r['id']==model[0]['id'])
            if mode=='calendar':row['calendar_months']=[3,4,5]
            if mode=='promotion':row['full_width_inference_eligible']=True
            if mode=='missing':bad['collections']['widths'].remove(row)
            if mode=='rebound':
                row['approximate_width_km']=999
                file=row['original_regional_context']['audit_file'];pin='0'*64
                bad['manifest']['input_sha256'][file]=pin
                for r in bad['collections']['widths']:
                    if r['id'].startswith('azores-carracedo-2014-'):r['original_regional_context']['audit_sha256']=pin
            with TemporaryDirectory(dir=out) as folder:
                file=Path(folder)/'bad.json';file.write_text(json.dumps(bad),encoding='utf8')
                result=subprocess.run([str(CLI),str(file),'-'],input='{}',capture_output=True,text=True,encoding='utf8')
                assert result.returncode==2 and not result.stdout,(mode,result.stderr)
                result=page.evaluate('''async path=>{
                    const {instance}=await WebAssembly.instantiate(await (await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports;
                    const b=new Uint8Array(await (await fetch(path)).arrayBuffer()),p=e.osw_alloc(b.length);
                    try{new Uint8Array(e.memory.buffer,p,b.length).set(b);e.osw_load(p,b.length);
                      return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));
                    }finally{e.osw_dealloc(p,b.length);}
                }''','/'+file.relative_to(ROOT).as_posix())
                assert result['ok'] is False,(mode,result)
        assert not errors,errors;browser.close()
    print('PASS: three separate Azores width scopes, atlas quarters, source pointers, mobile, native/WASM parity; four native/WASM source and promotion rejections')

if __name__=='__main__':main()
