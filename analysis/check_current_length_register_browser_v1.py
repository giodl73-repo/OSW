"""One cloud browser verifies the complete length register and current targets."""
import functools
import hashlib
import http.server
import json
import os
from pathlib import Path
import subprocess
import threading
from urllib.parse import parse_qs, urlsplit

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.pytest_cache/current-length-register-browser-v1'
REQUEST='research/current-length-register-browser-request-v1.json'
PREFLIGHT='research/current-length-register-browser-preflight-v1.json'


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def write(path,value):
    path.write_bytes((json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode())


def run():
    assert os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true'
    assert os.environ.get('OSW_LENGTH_REGISTER_BROWSER_V1')=='1'
    assert os.environ.get('GITHUB_REPOSITORY')=='giodl73-repo/OSW'
    assert os.environ.get('GITHUB_REF')=='refs/heads/codex/current-measurement-gaps'
    assert len(os.sched_getaffinity(0))==1 and os.getpriority(os.PRIO_PROCESS,0)>=15
    request=json.loads((ROOT/REQUEST).read_bytes())
    assert request['execute'] is True and request['preflight_sha256']==sha(PREFLIGHT)
    assert request['max_cloud_jobs']==1 and request['max_heavy_local_jobs']==0
    assert not any(request[k] for k in ['native_build_permitted','wasm_build_permitted','ocean_field_processing_permitted','installation_permitted','main_merge_permitted','local_bulk_sync_permitted'])
    preflight=json.loads((ROOT/PREFLIGHT).read_bytes())
    for path,pin in preflight['input_sha256'].items():assert sha(path)==pin,path
    installed=json.loads((ROOT/'research/current-utf8-validation-installation-result-v1.json').read_bytes())
    for path,row in installed['files'].items():
        oid=subprocess.check_output(['git','rev-parse','HEAD:'+path],cwd=ROOT).decode().strip()
        assert oid==row['git_blob_oid'] and (ROOT/path).stat().st_size==row['bytes'],path
    document=json.loads((ROOT/'research/current-length-estimate-register-v1.json').read_bytes())
    rows=document['records'];by_id={r['entity_id']:r for r in rows}
    assert len(by_id)==111 and all(r['length_estimate_km']>0 for r in rows)
    OUT.mkdir(parents=True,exist_ok=True)
    handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT))
    server=http.server.HTTPServer(('127.0.0.1',0),handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base=f'http://127.0.0.1:{server.server_port}'
    from playwright.sync_api import sync_playwright
    errors=[];length_requests=[];checked_assets=set()
    try:
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch(headless=True,args=['--disable-dev-shm-usage','--renderer-process-limit=1'])
            context=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
            page=context.new_page();page.set_default_timeout(120000)
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('request',lambda request:length_requests.append(request.url))
            page.goto(base+'/almanac/lengths.html')
            page.wait_for_function('window.oswCurrentLengthRegister?.records.length===111')
            assert page.locator('#length-rows tr').count()==111
            assert '111 of 111' in page.locator('#length-summary').inner_text()
            assert '0 estimates to finish' in page.locator('#length-summary').inner_text()
            values=page.locator('#length-rows tr .length-number').all_text_contents()
            assert len(values)==111 and 'To estimate' not in page.locator('#length-rows').inner_text()
            order=page.locator('#length-rows tr').evaluate_all('(els)=>els.map(e=>e.dataset.currentId)')
            assert set(order)==set(by_id)
            assert all(by_id[a]['length_estimate_km']>=by_id[b]['length_estimate_km'] for a,b in zip(order,order[1:]))
            links=page.locator('#length-rows tr td:first-child>a').evaluate_all('(els)=>els.map(e=>e.getAttribute("href"))')
            assert all(parse_qs(urlsplit(link).query)['id']==[owner] for link,owner in zip(links,order))
            for row in rows:
                tr=page.locator(f'tr[data-current-id="{row["entity_id"]}"]')
                assert row['scope'] in tr.text_content()
                if row['conditional_extent']:assert 'Conditional route or continuity' in tr.text_content()
            page.screenshot(path=str(OUT/'desktop.png'))
            for kind in ['family','system','individual']:
                page.select_option('#length-identity',kind)
                expected=sum((r['identity_level']==kind if kind!='individual' else r['identity_level'] not in ['family','system']) for r in rows)
                assert page.locator('#length-rows tr').count()==expected
            page.select_option('#length-identity','all')
            page.select_option('#length-filter','remaining');assert page.locator('#length-rows tr').count()==0
            page.select_option('#length-filter','all')
            page.select_option('#length-sort','name')
            assert page.locator('#length-rows tr').count()==111
            page.fill('#length-search','Azores Countercurrent')
            assert page.locator('#length-rows tr').count()==1
            page.locator('#length-rows summary').click()
            assert 'Full endpoints/continuity unresolved' in page.locator('#length-rows').inner_text()
            page.screenshot(path=str(OUT/'conditional-extent.png'),full_page=True)
            page.fill('#length-search','')
            with page.expect_download() as pending:page.get_by_role('link',name='Download CSV').click()
            download=pending.value
            assert hashlib.sha256(Path(download.path()).read_bytes()).hexdigest()==sha('research/current-length-estimate-register-v1.csv')
            for row in rows:
                for path in [row['record_file'],row.get('figure_file')]:
                    if path and path not in checked_assets:
                        response=context.request.get(base+'/'+path)
                        assert response.status==200 and hashlib.sha256(response.body()).hexdigest()==sha(path),path
                        checked_assets.add(path)
            assert not any('.wasm' in u or 'query-packet' in u or '/release/' in u for u in length_requests)
            page.set_viewport_size({'width':390,'height':844})
            page.fill('#length-search','Red Sea saline overflow')
            assert page.locator('#length-rows tr').count()==1
            page.locator('#length-rows summary').click()
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            assert page.locator('.length-scroll').evaluate('(el)=>el.scrollWidth<=el.clientWidth+1')
            page.screenshot(path=str(OUT/'mobile.png'),full_page=True)
            page.set_viewport_size({'width':1440,'height':1000})
            page.fill('#length-search','Indonesian Throughflow')
            page.locator('#length-rows summary').click()
            page.get_by_role('link',name='Map of the nominal reference extent').click()
            assert page.locator('svg').get_attribute('aria-label').startswith('Indonesian Throughflow')
            page.screenshot(path=str(OUT/'itf-map.png'))
            page.goto(base+'/almanac/lengths.html')
            page.wait_for_function('window.oswCurrentLengthRegister?.records.length===111')
            page.fill('#length-search','Kuroshio')
            page.get_by_role('link',name=by_id['current:kuroshio']['name'],exact=True).click()
            page.wait_for_function('window.oswObjectView?.id==="current:kuroshio"',timeout=180000)
            assert 'Kuroshio' in page.locator('#object-title').inner_text()
            page.screenshot(path=str(OUT/'current-card.png'))
            # Keep a single worker loaded while verifying every router target in Rust.
            targets=page.evaluate('''async ids=>{
              const worker=new Worker('query-worker.js');let next=1;
              const call=(action,value)=>new Promise((resolve,reject)=>{
                const id=next++,timer=setTimeout(()=>reject(Error('worker timeout '+action)),180000);
                worker.onmessage=event=>{if(event.data.id!==id||!event.data.result)return;clearTimeout(timer);const r=event.data.result;r.ok?resolve(r):reject(Error(r.error));};
                worker.onerror=e=>{clearTimeout(timer);reject(Error(e.message));};worker.postMessage({id,action,value});
              });
              try{await call('load');const found=[];
                for(const id of ids){const r=await call('object_view',{id});if(r.id!==id||!r.collections.entities.some(e=>e.id===id))throw Error('missing current '+id);found.push({id:r.id,engine:r.engine});}
                return found;
              }finally{worker.terminate();}
            }''',sorted(by_id))
            assert len(targets)==111 and {r['id'] for r in targets}==set(by_id)
            assert not errors,errors
            browser.close()
        projection=json.dumps(rows,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
        write(OUT/'result.json',{'schema':'osw.current-length-register-browser-result.v1','status':'PASS_COMPLETE_LENGTH_REGISTER_AND_111_CURRENT_TARGETS',
          'source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],
          'register_sha256':sha('research/current-length-estimate-register-v1.json'),'recordset_sha256':hashlib.sha256(projection).hexdigest(),
          'frontend_sha256':{p:sha(p) for p in ['almanac/lengths.html','almanac/lengths.js']},
          'counts':document['counts'],'all111_rows_positive_sorted_and_linked':True,'all111_rust_object_targets_verified':True,
          'family_system_filters_and_conditional_notes_verified':True,'csv_download_exact':True,'source_and_map_assets_checked':len(checked_assets),
          'mobile_no_document_overflow':True,'length_page_requires_runtime_packet':False,'page_errors':errors,
          'installed_runtime_files_preserved':21,'native_or_wasm_builds':0,'main_updated':False})
    finally:server.shutdown();server.server_close()


if __name__=='__main__':
    try:run()
    except Exception as error:
        if os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true':
            OUT.mkdir(parents=True,exist_ok=True);write(OUT/'failure.json',{'status':'FAIL','error':str(error)[:3000]})
        raise
