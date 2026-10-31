"""Cloud-only, single-CPU browser verification of the eddy register."""
import functools
import hashlib
import http.server
import json
import os
from pathlib import Path
import threading
from urllib.parse import parse_qs, urlsplit

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.pytest_cache/eddy-measurement-register-browser-v1'
REQUEST='research/eddy-measurement-register-browser-request-v1.json'
PREFLIGHT='research/eddy-measurement-register-browser-preflight-v1.json'


def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def run():
    assert os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true'
    assert os.environ.get('OSW_EDDY_REGISTER_BROWSER_V1')=='1'
    assert os.environ.get('GITHUB_REPOSITORY')=='giodl73-repo/OSW'
    assert os.environ.get('GITHUB_REF')=='refs/heads/codex/current-measurement-gaps'
    assert len(os.sched_getaffinity(0))==1 and os.getpriority(os.PRIO_PROCESS,0)>=15
    request=json.loads((ROOT/REQUEST).read_bytes())
    assert request['execute'] is True and request['preflight_sha256']==sha(PREFLIGHT)
    assert request['max_cloud_jobs']==1 and request['max_heavy_local_jobs']==0
    assert not any(request[k] for k in ['native_build_permitted','wasm_build_permitted','ocean_field_processing_permitted','installation_permitted','main_merge_permitted','local_bulk_sync_permitted'])
    preflight=json.loads((ROOT/PREFLIGHT).read_bytes())
    for path,pin in preflight['input_sha256'].items():assert sha(path)==pin,path
    document=json.loads((ROOT/'research/eddy-measurement-register-v1.json').read_bytes())
    OUT.mkdir(parents=True,exist_ok=True)
    handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT))
    server=http.server.HTTPServer(('127.0.0.1',0),handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{server.server_port}'
    from playwright.sync_api import sync_playwright
    errors=[];requests=[];assets=set();checks=[];page=None
    try:
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch(headless=True,args=['--disable-dev-shm-usage','--renderer-process-limit=1'])
            context=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
            page=context.new_page();page.set_default_timeout(60000)
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('request',lambda request:requests.append(request.url))
            page.goto(base+'/almanac/eddies.html')
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            assert page.locator('#eddy-rows tr').count()==136
            ids=page.locator('#eddy-rows tr').evaluate_all('(els)=>els.map(e=>e.dataset.eddyId)')
            assert set(ids)=={r['entity_id'] for r in document['records']}
            links=page.locator('#eddy-rows tr td:first-child>a').evaluate_all('(els)=>els.map(e=>e.getAttribute("href"))')
            assert all(parse_qs(urlsplit(link).query)['id']==[owner] for link,owner in zip(links,ids))
            assert '48 measurement records across 23 entries' in page.locator('#eddy-summary').inner_text()
            page.screenshot(path=str(OUT/'desktop.png'))
            for value,expected in [('individual_eddy',112),('recurrent_eddy_region',20),('eddy_family',4),('all',136)]:
                page.select_option('#eddy-identity',value);assert page.locator('#eddy-rows tr').count()==expected
            for value,expected in [('measured',23),('gap',113),('size-gap',124),('duration-gap',122),('all',136)]:
                page.select_option('#eddy-filter',value);assert page.locator('#eddy-rows tr').count()==expected
            for category in ['size','duration','recurrence','travel','all']:
                page.select_option('#eddy-category',category)
                expected=sum(category=='all' or category in r['categories'] for r in document['records'])
                assert page.locator('#eddy-rows tr').count()==expected
            checks.append('All136 identities, card href identities and all coverage/category/identity filters')
            page.fill('#eddy-search','Agulhas Ring Eliza');assert page.locator('#eddy-rows tr').count()==1
            page.locator('#eddy-rows summary').click()
            assert 'Unresolved source values' in page.locator('#eddy-rows').inner_text()
            assert '88 km' in page.locator('#eddy-rows').inner_text() and '93 km' in page.locator('#eddy-rows').inner_text()
            assert 'Source year conflict unresolved' in page.locator('#eddy-rows').inner_text()
            assert 'parent-ring' in page.locator('#eddy-rows').inner_text()
            page.screenshot(path=str(OUT/'eliza-conflicts.png'),full_page=True)
            page.fill('#eddy-search','')
            for name in ['thor-2020','ursa-2021']:
                tr=page.locator(f'tr[data-eddy-id="eddy:published:{name}"]');tr.locator('summary').click()
                assert 'Paper window:' in tr.inner_text() and 'measured lifetime' in tr.inner_text()
                assert tr.locator('.eddy-record').count()==0
            checks.append('Eliza value/year conflicts retained; parent-ring span and paper windows not promoted to individual lifetimes')
            page.select_option('#eddy-identity','eddy_family');page.fill('#eddy-search','Agulhas')
            assert page.locator('#eddy-rows tr').count()==1
            page.locator('#eddy-rows summary').click()
            assert page.locator('#eddy-rows .eddy-record').count()==7
            assert 'Table sample count: 2' in page.locator('#eddy-rows').inner_text()
            assert 'operator discrepancy' in page.locator('#eddy-rows').inner_text()
            assert '40 W' in page.locator('#eddy-rows').inner_text()
            page.screenshot(path=str(OUT/'population.png'))
            page.select_option('#eddy-identity','all');page.fill('#eddy-search','Lilian')
            page.locator('#eddy-rows summary').click()
            text=page.locator('#eddy-rows').inner_text()
            assert '3.5 years' in text and '> 5,500 km' in text
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            assert page.locator('.eddy-scroll').evaluate('(e)=>e.scrollWidth<=e.clientWidth')
            page.screenshot(path=str(OUT/'mobile-lilian.png'),full_page=True)
            checks.append('Seven population means/SD/cohorts; strict travel bound; approximate year unit; mobile expanded layout')
            page.set_viewport_size({'width':1440,'height':1000})
            for search,needles in [
                ('Kenai Eddy (2007)',['40 km','378 days','Track still present at the final study snapshot','disappearance date unknown']),
                ('Haida-1998',['Haida-1998a','Haida-1998b','no post-merger radius inferred','Approaches 50 km']),
                ('Agulhas Ring Laura',['8.6 km/day','Size reference needed'])]:
                page.fill('#eddy-search',search);assert page.locator('#eddy-rows tr').count()==1
                page.locator('#eddy-rows summary').click()
                for needle in needles:assert needle in page.locator('#eddy-rows').inner_text(),(search,needle)
                if search=='Kenai Eddy (2007)':page.screenshot(path=str(OUT/'kenai-censored.png'),full_page=True)
            page.fill('#eddy-search','Meddy Ulla');page.locator('#eddy-rows summary').click()
            text=page.locator('#eddy-rows').inner_text()
            assert '15 km' in text and '18 months' in text and 'Publisher abstract' in text
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            assert page.locator('.eddy-scroll').evaluate('(e)=>e.scrollWidth<=e.clientWidth')
            page.screenshot(path=str(OUT/'mobile-ulla.png'),full_page=True)
            checks.append('New Kenai/Sitka scope, right-censored Kenai span, distinct Haida components, Laura drift units and abstract-qualified Ulla months/radius')
            with page.expect_download() as pending:page.get_by_role('link',name='Download measurement CSV').click()
            assert hashlib.sha256(Path(pending.value.path()).read_bytes()).hexdigest()==sha('research/eddy-measurement-register-v1.csv')
            for path in set(r['source_file'] for r in document['evidence'])|{'plans/eddy-measurement-register-v1.md','research/eddy-measurement-register-v1.json'}:
                response=context.request.get(base+'/'+path);assert response.status==200 and hashlib.sha256(response.body()).hexdigest()==sha(path),path
                assets.add(path)
            page.goto(base+'/almanac/eddies.html?id=eddy%3Apublished%3Akraken-2013')
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            target=page.locator('tr[data-eddy-id="eddy:published:kraken-2013"]')
            assert target.locator('details').evaluate('(e)=>e.open')
            assert 'identity unverified' in target.inner_text()
            assert '200 days' in target.inner_text()
            assert not errors,errors
            assert not any('.wasm' in u or 'query-packet' in u or '/release/' in u for u in requests)
            checks.append('CSV/source bytes, deep link, unverified identity crosswalk, no JS errors or runtime packet load')
            result={'status':'PASS','source_commit':os.environ['GITHUB_SHA'],'counts':document['counts'],'checks':checks,'source_assets_checked':len(assets),'input_sha256':preflight['input_sha256'],'browser_scope':'Lightweight register only; card href identities verified, destinations not executed.','runtime_loaded':False,'full_goal_complete':False}
            (OUT/'result.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
            print(json.dumps(result));browser.close()
    finally:server.shutdown();server.server_close()


if __name__=='__main__':run()
