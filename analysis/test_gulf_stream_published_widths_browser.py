"""Published campaign widths and climatology keep their source support in the UI."""
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
from check_gulf_stream_published_widths import ROOT, AUDIT, records
from test_rust_query_browser import CLI, BASE, native


def corrupt(bundle,mode):
    bad=copy.deepcopy(bundle)
    identifier=records()[1 if mode in ['depth','dates'] else 0]['id']
    row=next(r for r in bad['collections']['widths'] if r['id']==identifier)
    receipt=bad['manifest']['seasons_receipts']['widths'];inventory=json.loads(receipt['source_json'])
    original=next(r for r in inventory['measurements'] if r['id']==identifier)
    changes={'mean':('approximate_width_km',150),'range':('width_range_km',[135,300]),
             'depth':('fixed_layer_bounds_m',[100,400]),'dates':('observed_period',{'start':'1995-01-01','end':'1995-12-31'}),
             'owner':('current_id','gulf-stream-system'),'annual':('annual_width_range_km',[120,145])}
    if mode in changes:
        key,value=changes[mode];row[key]=value;original[key]=copy.deepcopy(value)
    if mode=='extrapolation':
        row['original_regional_context'].update(author_boundary_extrapolation_present=False,inshore_negative_transport_observed=True)
        original['original_regional_context']=copy.deepcopy(row['original_regional_context'])
    if mode=='partial':
        extra=copy.deepcopy(row['original_regional_context']['complete_crossing_occupations'][0])
        extra.update(id='gulf-stream-1967-crossing-2',crossing_number=2,width_km=135)
        row['original_regional_context']['complete_crossing_occupations'].append(extra)
        original['original_regional_context']=copy.deepcopy(row['original_regional_context'])
    if mode=='missing':
        bad['collections']['widths'].remove(row);inventory['measurements'].remove(original)
        for o in bad['collections']['objects']:
            if identifier in o.get('width_ids',[]):o['width_ids'].remove(identifier);o['capabilities']['scoped_width']-=1
        for d in inventory['current_decisions']:
            if identifier in d['measurement_ids']:d['measurement_ids'].remove(identifier)
        inventory['counts']['measurements']-=1
    if mode=='audit_forgery':
        diagnostic=next(d for d in bad['collections']['diagnostics'] if d['id']=='diagnostic:gulf-stream-published-width-definitions')
        audit=diagnostic['document'];audit['measurements'][0]['approximate_width_km']=150
        raw=json.dumps(audit,ensure_ascii=False);pin=hashlib.sha256(raw.encode()).hexdigest()
        diagnostic.update(source_json=raw,source_file_sha256=pin)
        bad['manifest']['input_sha256'][AUDIT]=pin
        for r in bad['collections']['widths']:
            if r.get('original_regional_context',{}).get('audit_file')==AUDIT:
                r['original_regional_context']['audit_sha256']=pin
                if r['id']==identifier:r['approximate_width_km']=150
                target=next(v for v in inventory['measurements'] if v['id']==r['id'])
                target.update(copy.deepcopy(r))
    receipt['source_json']=json.dumps(inventory,ensure_ascii=False)
    receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest()
    bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
    return bad


def main():
    out=ROOT/'.pytest_cache/gulf-stream-physical-width-review';out.mkdir(parents=True,exist_ok=True)
    bundle=json.loads(read_bundle_bytes(ROOT/'almanac/query-data.json'))
    with TemporaryDirectory(dir=out) as directory, sync_playwright() as p:
        index=Path(directory)/'index.json';index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1280,'height':1000});errors=[];pdf_requests=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('request',lambda r:pdf_requests.append(r.url) if '.pdf' in r.url else None)
        for row in records():
            page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=gulf-stream&phase='+row['id'])
            page.wait_for_function('window.oswSeasonPlan?.current_id==="gulf-stream"',timeout=90000)
            chart=page.locator('#regional-width-range .original-regional-width svg');expect(chart).to_be_visible()
            assert str(row['approximate_width_km']) in chart.get_attribute('aria-label')
            assert page.locator('#season-play').is_disabled()
            assert page.evaluate('oswSeasonPlan.eligible_indices')==[]
            if row['phase_kind']=='campaign_width_statistics':assert chart.locator('circle[data-author-mean-km="135"]').count()==1
            page.set_viewport_size({'width':320,'height':900})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.locator('#regional-width-range').screenshot(path=str(out/(row['id']+'-mobile.png')))
            query={'collection':'widths','filters':[{'field':'id','op':'eq','value':row['id']}]}
            expected=native(query);assert expected['total']==1 and expected['rows']==[row]
            page.goto(BASE+'?q='+quote(json.dumps(query)));page.wait_for_function('window.oswLastQueryResult',timeout=90000)
            assert page.evaluate('oswLastQueryResult')==expected
            page.locator('#query-rows tr button').first.click()
            expect(page.locator('#query-detail h3')).to_have_text('Gulf Stream')
            expect(page.locator('#query-detail')).to_contain_text(row['id'])
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Agulf-stream#route-atlas')
        preview=page.locator('#route-atlas-preview');expect(preview.locator('.original-regional-width')).to_have_count(2,timeout=90000)
        assert preview.locator('.atlas-width-record').count()==3
        expect(preview).to_contain_text('135 km mean (120–145 km across three complete crossings)')
        expect(preview).to_contain_text('256')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        link=preview.get_by_role('link',name='1967 transport-float widths / three multi-day occupations',exact=False)
        expect(link).to_be_visible();link.click()
        page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
        request={'document':AUDIT,'pointer':'/measurements/0/original_regional_context/complete_crossing_occupations','limit':10}
        expected=subprocess.run([str(CLI),'--index',str(index),'-'],input=json.dumps(request),capture_output=True,text=True,encoding='utf8')
        assert expected.returncode==0,expected.stderr
        actual=page.evaluate('oswSourceQueryResult');assert actual==json.loads(expected.stdout) and actual['total']==3
        assert [r['record']['width_km'] for r in actual['rows']]==[145,140,120]
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.screenshot(path=str(out/'occupations-mobile.png'),full_page=True)
        assert not pdf_requests,pdf_requests
        page.route('**/gulf-width-guard.html',lambda r:r.fulfill(body='<title>Width guard</title>',content_type='text/html'))
        page.goto('http://127.0.0.1:8788/gulf-width-guard.html')
        for mode in ['extrapolation','range','depth','dates','owner','annual','partial','missing','audit_forgery']:
            path=Path(directory)/'bad.json';path.write_text(json.dumps(corrupt(bundle,mode),ensure_ascii=False),encoding='utf8')
            result=subprocess.run([str(CLI),str(path),'-'],input='{}',capture_output=True,text=True,encoding='utf8')
            assert result.returncode==2 and not result.stdout,(mode,result.stderr)
            actual=page.evaluate('''async path=>{
              const {instance}=await WebAssembly.instantiate(await(await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports;
              const b=new Uint8Array(await(await fetch(path)).arrayBuffer()),p=e.osw_alloc(b.length);
              try{new Uint8Array(e.memory.buffer,p,b.length).set(b);e.osw_load(p,b.length);
                return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));
              }finally{e.osw_dealloc(p,b.length);}
            }''','/'+path.relative_to(ROOT).as_posix())
            assert actual['ok'] is False,(mode,actual)
        assert not errors,errors
        page.set_viewport_size({'width':1400,'height':760})
        page.set_content('<img style="width:1400px" src="http://127.0.0.1:8788/figures/gulf-stream-published-width-definitions.svg">')
        page.locator('img').screenshot(path=str(out/'independent-figure.png'))
        browser.close()
    print('PASS: two source definitions, three actual occupations, native/WASM parity, atlas/seasons/inspector/mobile, no seasonal playback, nine coherent source/admission rejections')


if __name__=='__main__':main()
