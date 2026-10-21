"""Exercise the actual Loop card, source query and compiled admission guards."""
from query_packet import read_bundle_bytes
import copy
import gzip
import hashlib
import json
import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote
from playwright.sync_api import sync_playwright, expect
from check_loop_uhlhorn_core_width import ROOT, AUDIT, ID, record
from test_rust_query_browser import CLI, BASE, native


def corrupt(bundle, mode):
    bad=copy.deepcopy(bundle)
    receipt=bad['manifest']['seasons_receipts']['widths'];inventory=json.loads(receipt['source_json'])
    row=next(r for r in bad['collections']['widths'] if r['id']==ID)
    original=next(r for r in inventory['measurements'] if r['id']==ID)
    changes={'width':('approximate_width_km',200),'range':('width_range_km',[100,200]),
             'depth':('fixed_layer_bounds_m',[0,300]),'dates':('observed_period',{'start':'2002-10-04','end':'2002-10-04'}),
             'owner':('current_id','yucatan'),'annual':('annual_width_range_km',[100,200])}
    if mode in changes:
        key,value=changes[mode];row[key]=value;original[key]=copy.deepcopy(value)
    if mode=='relative_cutoff':
        row['original_regional_context']['source_e_folding_wording_is_adopted_threshold']=True
        original['original_regional_context']=copy.deepcopy(row['original_regional_context'])
    if mode=='missing':
        bad['collections']['widths'].remove(row);inventory['measurements'].remove(original)
        next(d for d in inventory['current_decisions'] if d['current_id']=='loop').update(measurement_ids=[],width_decision='section_span_diagnostic_present_width_unresolved')
        inventory['counts']['measurements']-=1;inventory['counts']['currents_with_scoped_width_evidence']-=1
        inventory['counts']['currents_with_section_span_diagnostics_width_unresolved']+=1
        owner=next(o for o in bad['collections']['objects'] if o['id']=='current:loop')
        owner['width_ids'].remove(ID);owner['capabilities']['scoped_width']-=1
    if mode=='audit_forgery':
        diagnostic=next(d for d in bad['collections']['diagnostics'] if d['id']=='diagnostic:uhlhorn-loop-core-width')
        audit=diagnostic['document'];audit['measurement']['approximate_width_km']=200
        raw=json.dumps(audit);pin=hashlib.sha256(raw.encode()).hexdigest()
        diagnostic.update(source_json=raw,source_file_sha256=pin)
        bad['manifest']['input_sha256'][AUDIT]=pin
        for r in [row,original]:r['approximate_width_km']=200;r['original_regional_context']['audit_sha256']=pin
    receipt['source_json']=json.dumps(inventory);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest()
    bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
    return bad


def main():
    out=ROOT/'.pytest_cache/loop-physical-width-review';out.mkdir(exist_ok=True)
    bundle=json.loads(read_bundle_bytes(ROOT/'almanac/query-data.json'))
    with TemporaryDirectory(dir=out) as folder,sync_playwright() as p:
        index=Path(folder)/'index.json';index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1280,'height':1000});errors=[];pdf_requests=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('request',lambda r:pdf_requests.append(r.url) if '.pdf' in r.url else None)
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Aloop#route-atlas')
        preview=page.locator('#route-atlas-preview');chart=preview.locator('.original-regional-width svg')
        expect(chart).to_be_visible(timeout=90000);assert '100' in chart.get_attribute('aria-label')
        expect(preview.get_by_role('link',name='Map local component spans')).to_be_visible()
        expect(preview).to_contain_text('0.4 m/s')
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=loop&phase='+ID)
        page.wait_for_function('window.oswSeasonPlan?.current_id==="loop"',timeout=90000)
        expect(page.locator('#regional-width-range .original-regional-width svg')).to_be_visible()
        assert page.locator('#season-play').is_disabled()
        page.set_viewport_size({'width':320,'height':900})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#regional-width-range').screenshot(path=str(out/'core-mobile.png'))
        query={'collection':'widths','filters':[{'field':'id','op':'eq','value':ID}]}
        expected=native(query);assert expected['rows']==[record()]
        page.goto(BASE+'?q='+quote(json.dumps(query)));page.wait_for_function('window.oswLastQueryResult',timeout=90000)
        assert page.evaluate('oswLastQueryResult')==expected
        page.locator('#query-rows tr button').first.click();expect(page.locator('#query-detail')).to_contain_text(ID)
        source_query={'document':AUDIT,'pointer':'/measurement','limit':10}
        result=subprocess.run([str(CLI),'--index',str(index),'-'],input=json.dumps(source_query),capture_output=True,text=True,encoding='utf8')
        assert result.returncode==0,result.stderr
        page.goto(BASE+'?source-q='+quote(json.dumps(source_query)))
        page.wait_for_function('window.oswSourceQueryResult',timeout=90000)
        assert page.evaluate('oswSourceQueryResult')==json.loads(result.stdout)
        assert not pdf_requests,pdf_requests
        page.route('**/loop-width-guard.html',lambda r:r.fulfill(body='<title>Width guard</title>',content_type='text/html'))
        page.goto('http://127.0.0.1:8788/loop-width-guard.html')
        for mode in ['width','range','depth','dates','owner','annual','relative_cutoff','missing','audit_forgery']:
            path=Path(folder)/'bad.json';path.write_text(json.dumps(corrupt(bundle,mode)),encoding='utf8')
            rejected=subprocess.run([str(CLI),str(path),'-'],input='{}',capture_output=True,text=True,encoding='utf8')
            assert rejected.returncode==2 and not rejected.stdout,(mode,rejected.stderr)
            actual=page.evaluate('''async path=>{
              const {instance}=await WebAssembly.instantiate(await(await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports;
              const b=new Uint8Array(await(await fetch(path)).arrayBuffer()),p=e.osw_alloc(b.length);
              try{new Uint8Array(e.memory.buffer,p,b.length).set(b);e.osw_load(p,b.length);
                return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));
              }finally{e.osw_dealloc(p,b.length);}
            }''','/'+path.relative_to(ROOT).as_posix())
            assert actual['ok'] is False,(mode,actual)
        assert not errors,errors
        page.set_viewport_size({'width':1000,'height':550})
        page.set_content('<img style="width:960px" src="http://127.0.0.1:8788/figures/loop-uhlhorn-2008-core-width.svg">')
        page.locator('img').screenshot(path=str(out/'independent-figure.png'))
        browser.close()
    print('PASS: Loop core atlas/seasons/source/inspector/mobile parity, retained altimetry diagnostics, no PDF or seasonal playback; nine coherent native/WASM rejections')


if __name__=='__main__':main()
