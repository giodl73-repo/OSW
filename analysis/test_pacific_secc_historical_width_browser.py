"""Static historical SECC range, source access and original-scope rejection."""
import copy
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from urllib.parse import quote
from playwright.sync_api import sync_playwright, expect
from test_rust_query_browser import ROOT, CLI, native, browser_query

OWNER='pacific-south-equatorial-countercurrent'
ID='pacific-secc-rotschi-1972-170e-width-range'


def main():
    output=ROOT/'.pytest_cache/pacific-secc-source-review'
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':OWNER}],'limit':10}
    result=native(query)
    assert result['ok'] and result['total']==1
    assert result['rows'][0]['approximate_width_km'] is None and result['rows'][0]['width_range_km']==[300,900]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ['OSW_TEST_BROWSER'])
        page=browser.new_page(viewport={'width':1200,'height':1000});errors=[]
        page.emulate_media(reduced_motion='reduce');page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/query.html');page.wait_for_function('window.oswLastQueryResult',timeout=60000)
        assert browser_query(page,query)==result
        page.locator('#query-rows button').first.click()
        expect(page.locator('#query-detail')).to_contain_text('300')
        expect(page.locator('#query-detail')).to_contain_text('900')
        expect(page.locator('#query-detail')).to_contain_text('no midpoint')
        expect(page.locator('#query-detail')).to_contain_text('geostrophic')
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3A'+OWNER+'#route-atlas',wait_until='networkidle')
        route_count=json.loads((ROOT/'research/ocean-current-working-reference-routes.json').read_bytes())['counts']['route_candidates']
        page.wait_for_function('(count)=>document.querySelectorAll(".route-card").length===count',arg=route_count)
        preview=page.locator('#route-atlas-preview')
        assert preview.locator('.original-regional-width svg').count()==1
        expect(preview).to_contain_text('upper-300 m')
        expect(preview).to_contain_text('500 m reference')
        assert preview.locator('.route-map').count()==0
        preview.screenshot(path=str(ROOT/'figures/pacific-secc-historical-width-review.png'))
        page.set_viewport_size({'width':320,'height':900})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        preview.screenshot(path=str(output/'pacific-secc-mobile.png'))
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current='+OWNER+'&phase='+ID,wait_until='networkidle')
        page.wait_for_function('window.oswSeasonPlan',timeout=60000)
        assert page.locator('#season-play').is_disabled()
        assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
        # Frozen original interpretation survives fully editable incoming records.
        page.route('**/secc-width-guard.html',lambda route:route.fulfill(body='<title>SECC historical guard</title>',content_type='text/html'))
        page.goto('http://127.0.0.1:8788/secc-width-guard.html')
        for key,value in [('approximate_width_km',600),('fixed_layer_bounds_m',[0,300]),('current_id','south-equatorial-countercurrent')]:
            bad=copy.deepcopy(bundle);row=next(r for r in bad['collections']['widths'] if r['id']==ID);row[key]=value
            with TemporaryDirectory(dir=output) as folder:
                file=Path(folder)/'bad.json';file.write_text(json.dumps(bad),encoding='utf-8')
                native_result=subprocess.run([str(CLI),str(file),'-'],input='{}',capture_output=True,text=True,encoding='utf-8')
                assert native_result.returncode==2 and not native_result.stdout,(key,native_result.stderr)
                wasm=page.evaluate('''async path=>{
                    const {instance}=await WebAssembly.instantiate(await (await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports;
                    const b=new Uint8Array(await (await fetch(path)).arrayBuffer()),p=e.osw_alloc(b.length);
                    try{new Uint8Array(e.memory.buffer,p,b.length).set(b);e.osw_load(p,b.length);
                      return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));
                    }finally{e.osw_dealloc(p,b.length);}
                }''','/'+file.relative_to(ROOT).as_posix())
                assert wasm['ok'] is False,wasm
        assert not errors,errors
        browser.close()
    print('PASS: historical SECC range, native/WASM parity, atlas and static inspector/source access, mobile; three native/WASM scope rejections')


if __name__=='__main__':
    main()
