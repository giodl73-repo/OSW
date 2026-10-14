"""Four static source descriptors, two metrics, retained directions and rejection."""
import copy
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from playwright.sync_api import sync_playwright, expect
from test_rust_query_browser import ROOT,CLI,native,browser_query

OWNER='new-guinea-coastal-current'
PREFIX='ngcc-radenac-2016-winter-'

def main():
    output=ROOT/'.pytest_cache/ngcc-seasonal-width-review';output.mkdir(exist_ok=True)
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':OWNER}],'limit':20}
    result=native(query);assert result['ok'] and result['total']==4
    rows=result['rows'];assert [r['approximate_width_km'] for r in rows]==[120,None,200,None]
    assert len({r['width_metric'] for r in rows})==2
    assert len({r['original_regional_context']['source_claim_id'] for r in rows})==2
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ['OSW_TEST_BROWSER'])
        page=browser.new_page(viewport={'width':1350,'height':1100});page.emulate_media(reduced_motion='reduce')
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/query.html');page.wait_for_function('window.oswLastQueryResult',timeout=60000)
        assert browser_query(page,query)==result
        thermal={'collection':'widths','filters':[{'field':'id','op':'eq','value':PREFIX+'west-cold-vein'}]}
        assert browser_query(page,thermal)==native(thermal)
        page.locator('#query-rows button').first.click()
        expect(page.locator('#query-detail')).to_contain_text('thermal')
        expect(page.locator('#query-detail')).to_contain_text('100')
        expect(page.locator('#query-detail')).to_contain_text('150')
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3A'+OWNER+'#route-atlas',wait_until='networkidle')
        route_count=json.loads((ROOT/'research/ocean-current-reference-path-candidates.json').read_bytes())['counts']['route_candidates']
        page.wait_for_function('(count)=>document.querySelectorAll(".route-card").length===count',arg=route_count)
        preview=page.locator('#route-atlas-preview')
        assert preview.locator('.original-regional-width svg').count()==4
        # Reported endpoints must fit; a near-right narrow range previously
        # placed its high label outside the viewBox.
        assert preview.locator('.original-regional-width svg').evaluate_all('''svgs=>svgs.every(svg=>{
            const labels=[...svg.querySelectorAll('text')];
            return labels.every(t=>{const b=t.getBBox();return b.x>=0&&b.x+b.width<=500;});
        })''')
        expect(preview).to_contain_text('100–200')
        expect(preview).to_contain_text('Thermal water-mass span')
        expect(preview).to_contain_text('share one source claim')
        preview.screenshot(path=str(ROOT/'figures/ngcc-seasonal-vein-width-review.png'))
        page.set_viewport_size({'width':320,'height':900})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        preview.screenshot(path=str(output/'atlas-mobile.png'))
        for row in rows:
            page.goto('http://127.0.0.1:8788/almanac/seasons.html?current='+OWNER+'&phase='+row['id'],wait_until='networkidle')
            page.wait_for_function('window.oswSeasonPlan',timeout=60000)
            plan=page.evaluate('window.oswSeasonPlan')
            descriptors=[r for r in plan['phases'] if r.get('width_id') and r['width_id'].startswith(PREFIX)]
            assert len(descriptors)==4 and all(r['playback_step_eligible'] is False for r in descriptors)
            directions=[r for r in plan['phases'] if r.get('direction_id') and r['playback_step_eligible']]
            assert len(directions)==2
            assert page.locator('#season-play').is_disabled()
            assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
            expect(page.locator('#season-title')).to_have_text(row['phase_label'])
            expect(page.locator('#season-value')).to_contain_text(row['width_metric_label'])
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.screenshot(path=str(output/'thermal-season-mobile.png'))
        page.route('**/ngcc-guard.html',lambda r:r.fulfill(body='<title>NGCC source guard</title>',content_type='text/html'))
        page.goto('http://127.0.0.1:8788/ngcc-guard.html')
        for kind in ['midpoint','metric','missing']:
            bad=copy.deepcopy(bundle)
            if kind=='missing':
                bad['collections']['widths']=[r for r in bad['collections']['widths'] if r['id']!=PREFIX+'east-099']
            else:
                row=next(r for r in bad['collections']['widths'] if r['id']==PREFIX+('west-range' if kind=='midpoint' else 'west-cold-vein'))
                row['approximate_width_km' if kind=='midpoint' else 'width_metric']=150 if kind=='midpoint' else rows[0]['width_metric']
            with TemporaryDirectory(dir=output) as folder:
                file=Path(folder)/'bad.json';file.write_text(json.dumps(bad),encoding='utf-8')
                native_result=subprocess.run([str(CLI),str(file),'-'],input='{}',capture_output=True,text=True,encoding='utf-8')
                assert native_result.returncode==2 and not native_result.stdout,(kind,native_result.stderr)
                wasm=page.evaluate('''async path=>{
                    const {instance}=await WebAssembly.instantiate(await (await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports;
                    const b=new Uint8Array(await (await fetch(path)).arrayBuffer()),p=e.osw_alloc(b.length);
                    try{new Uint8Array(e.memory.buffer,p,b.length).set(b);e.osw_load(p,b.length);
                      return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));
                    }finally{e.osw_dealloc(p,b.length);}
                }''','/'+file.relative_to(ROOT).as_posix())
                assert wasm['ok'] is False,(kind,wasm)
        assert not errors,errors
        browser.close()
    print('PASS: four NGCC descriptors / two distinct metrics, shared claims, native/WASM parity, atlas and mobile, four static phases with two retained direction phases; three native/WASM rejections')

if __name__=='__main__':
    main()
