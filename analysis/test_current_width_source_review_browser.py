"""Reviewed source limitations stay queryable and never turn into dimensions."""
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

ROOT=Path(__file__).resolve().parents[1]
AUDIT='research/southern-current-width-source-limitations-audit.json'
BASE=os.environ.get('OSW_SOURCE_REVIEW_BASE','http://127.0.0.1:8788')
CLI=ROOT/'rust/osw-query/target/debug'/('osw-query-cli.exe' if os.name=='nt' else 'osw-query-cli')
PREFIX='diagnostic:current-width-source-limits:'


def native(query):
    result=subprocess.run([str(CLI),str(ROOT/'almanac/query-data.json'),'-'],input=json.dumps(query),capture_output=True,text=True,encoding='utf8')
    assert result.returncode==0,result.stderr
    return json.loads(result.stdout)


def corrupt(packet,kind):
    bad=copy.deepcopy(packet)
    rows=[r for r in bad['collections']['diagnostics'] if str(r['id']).startswith(PREFIX)]
    if kind=='rank':rows[0]['rank_eligible']=True
    if kind=='owner':rows[0]['current_id']='agulhas-return';rows[0]['entity_id']='current:agulhas-return'
    if kind=='source_json':rows[0]['source_json']='{}'
    if kind=='missing':
        bad['collections']['diagnostics'].remove(rows[0])
        for obj in bad['collections']['objects']:
            if 'diagnostic_ids' in obj:obj['diagnostic_ids']=[i for i in obj['diagnostic_ids'] if i!=rows[0]['id']]
    if kind=='original_pin':
        source=rows[0]['document']['sources'][0]['source_document_file']
        bad['manifest']['input_sha256'][source]='0'*64
    if kind in ['width','isobath','box_edges','annual','review_claim']:
        doc=copy.deepcopy(rows[0]['document'])
        if kind=='width':doc['reviews'][0]['whole_current_width_km']=100
        if kind=='annual':doc['reviews'][0]['annual_width_range_km']=[50,100]
        if kind=='isobath':doc['reviews'][1]['control_volume_context']['reference_isobath_is_sampling_depth']=True
        if kind=='box_edges':doc['reviews'][1]['control_volume_context']['offsets_are_physical_current_edges']=True
        if kind=='review_claim':doc['sources'][0]['review_scope']='Full original visually reviewed.'
        raw=json.dumps(doc);pin=hashlib.sha256(raw.encode()).hexdigest()
        for row in rows:row.update(document=doc,source_json=raw,source_file_sha256=pin)
        bad['manifest']['input_sha256'][AUDIT]=pin
    return bad


def main():
    out=ROOT/'.pytest_cache/current-width-source-review';out.mkdir(parents=True,exist_ok=True)
    packet=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    before=json.loads(subprocess.check_output(['git','show','HEAD:almanac/query-data.json'],cwd=ROOT))['collections']
    after=packet['collections']
    assert after['widths']==before['widths'] and after['series']==before['series']
    assert after['width_samples']==before['width_samples'] and after['reference_routes']==before['reference_routes']
    inventory=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
    assert len(after['widths'])==inventory['counts']['measurements']
    assert len({r['current_id'] for r in after['widths']})==inventory['counts']['currents_with_scoped_width_evidence']
    with TemporaryDirectory(dir=out) as temporary,sync_playwright() as p:
        folder=Path(temporary);index=folder/'index.json'
        index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1280,'height':1000});errors=[];pdf_requests=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('request',lambda r:pdf_requests.append(r.url) if '.pdf' in r.url else None)
        for owner in ['south-indian','south-australian']:
            page.goto(BASE+'/almanac/reference-routes.html?atlas-feature=current%3A'+owner+'#route-atlas')
            preview=page.locator('#route-atlas-preview');panel=preview.locator('.current-width-source-review')
            expect(panel).to_be_visible(timeout=90000)
            assert panel.locator('dd').all_text_contents()==['Unknown','Unknown','None admitted']
            details=panel.locator('details');assert details.get_attribute('open') is None
            details.locator('summary').focus();page.keyboard.press('Enter')
            assert details.get_attribute('open') is not None
            expect(details).to_contain_text('Next evidence needed:')
            details.locator('summary').focus();page.keyboard.press('Enter')
            assert details.get_attribute('open') is None
            expect(preview.get_by_role('link',name='Map local component spans')).to_be_visible()
            panel.screenshot(path=str(out/(owner+'-desktop.png')))
            panel.get_by_role('link',name='Inspect review and source limits').click()
            page.wait_for_function('window.oswSourceQueryResult',timeout=90000)
            source_query={'document':AUDIT,'pointer':'/reviews/'+str(['south-indian','south-australian'].index(owner)),'limit':100}
            source=subprocess.run([str(CLI),'--index',str(index),'-'],input=json.dumps(source_query),capture_output=True,text=True,encoding='utf8')
            assert source.returncode==0,source.stderr
            assert page.evaluate('oswSourceQueryResult')==json.loads(source.stdout)
            page.goto(BASE+'/almanac/seasons.html?current='+owner)
            page.wait_for_function('(id)=>window.oswSeasonPlan?.current_id===id',arg=owner,timeout=90000)
            expect(page.locator('#current-width-source-review .current-width-source-review')).to_be_visible()
            assert page.locator('#season-play').is_disabled()
            page.set_viewport_size({'width':320,'height':900});page.emulate_media(reduced_motion='reduce')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.locator('#current-width-source-review').screenshot(path=str(out/(owner+'-mobile.png')))
            page.locator('#season-current').select_option('portugal')
            assert page.locator('#current-width-source-review .current-width-source-review').count()==0
            page.set_viewport_size({'width':1280,'height':1000})
            query={'collection':'diagnostics','filters':[{'field':'current_id','op':'eq','value':owner}]}
            expected=native(query)
            page.goto(BASE+'/almanac/query.html?q='+quote(json.dumps(query)))
            page.wait_for_function('window.oswLastQueryResult',timeout=90000)
            assert page.evaluate('oswLastQueryResult')==expected
            expect(page.locator('#query-chart-panels .current-width-source-review')).to_be_visible()
            page.get_by_role('button',name='Inspect source-review record').click()
            expect(page.locator('#query-detail')).to_contain_text(PREFIX+owner)
        assert not pdf_requests,pdf_requests
        page.route('**/source-review-guard.html',lambda r:r.fulfill(body='<title>Source review guard</title>',content_type='text/html'))
        page.goto(BASE+'/source-review-guard.html')
        for kind in ['rank','owner','source_json','missing','original_pin','width','isobath','box_edges','annual','review_claim']:
            path=folder/'corrupt.json';path.write_bytes(json.dumps(corrupt(packet,kind)).encode())
            rejected=subprocess.run([str(CLI),str(path),'-'],input='{}',capture_output=True,text=True,encoding='utf8')
            assert rejected.returncode==2 and not rejected.stdout,(kind,rejected.stderr)
            result=page.evaluate('''async path=>{
              const {instance}=await WebAssembly.instantiate(await(await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports;
              const b=new Uint8Array(await(await fetch(path)).arrayBuffer()),p=e.osw_alloc(b.length);
              try{new Uint8Array(e.memory.buffer,p,b.length).set(b);e.osw_load(p,b.length);
                return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));
              }finally{e.osw_dealloc(p,b.length);}
            }''','/'+path.relative_to(ROOT).as_posix())
            assert result['ok'] is False,(kind,result)
        assert not errors,errors
        browser.close()
    print('PASS: both source-limit cards/seasons/query/source/inspector/mobile; no widths, playback or PDF auto-fetch;10coherent nativeWASM rejections')


if __name__=='__main__':main()
