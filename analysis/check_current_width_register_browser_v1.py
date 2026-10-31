"""Cloud-only, single-CPU review of the lightweight width register."""
import functools
import hashlib
import http.server
import json
import os
from pathlib import Path
import threading
from urllib.parse import parse_qs, urlsplit

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.pytest_cache/current-width-register-browser-v1'
REQUEST='research/current-width-register-browser-request-v1.json'
PREFLIGHT='research/current-width-register-browser-preflight-v1.json'


def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def run():
    assert os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true'
    assert os.environ.get('OSW_WIDTH_REGISTER_BROWSER_V1')=='1'
    assert os.environ.get('GITHUB_REPOSITORY')=='giodl73-repo/OSW'
    assert os.environ.get('GITHUB_REF')=='refs/heads/codex/current-measurement-gaps'
    assert len(os.sched_getaffinity(0))==1 and os.getpriority(os.PRIO_PROCESS,0)>=15
    request=json.loads((ROOT/REQUEST).read_bytes())
    assert request['execute'] is True and request['preflight_sha256']==sha(PREFLIGHT)
    assert request['max_cloud_jobs']==1 and request['max_heavy_local_jobs']==0
    assert not any(request[k] for k in ['native_build_permitted','wasm_build_permitted','ocean_field_processing_permitted','installation_permitted','main_merge_permitted','local_bulk_sync_permitted'])
    preflight=json.loads((ROOT/PREFLIGHT).read_bytes())
    for path,pin in preflight['input_sha256'].items():assert sha(path)==pin,path
    document=json.loads((ROOT/'research/current-width-register-v1.json').read_bytes())
    rows=document['records'];by_id={r['entity_id']:r for r in rows}
    OUT.mkdir(parents=True,exist_ok=True)
    handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT))
    server=http.server.HTTPServer(('127.0.0.1',0),handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{server.server_port}'
    from playwright.sync_api import sync_playwright
    errors=[];requests=[];assets=set();checks=[]
    try:
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch(headless=True,args=['--disable-dev-shm-usage','--renderer-process-limit=1'])
            context=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
            page=context.new_page();page.set_default_timeout(60000)
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('request',lambda request:requests.append(request.url))
            page.goto(base+'/almanac/widths.html')
            page.wait_for_function('window.oswCurrentWidthRegister?.records.length===111')
            assert page.locator('#width-rows tr').count()==111
            ids=page.locator('#width-rows tr').evaluate_all('(els)=>els.map(e=>e.dataset.currentId)')
            assert set(ids)==set(by_id)
            links=page.locator('#width-rows tr td:first-child>a').evaluate_all('(els)=>els.map(e=>e.getAttribute("href"))')
            assert all(parse_qs(urlsplit(link).query)['id']==[owner] for link,owner in zip(links,ids))
            page.screenshot(path=str(OUT/'desktop.png'))
            state=page.evaluate('({metric:document.getElementById("width-metric").value, order:document.getElementById("width-order").value, disabled:document.querySelector("#width-order option[value=value]").disabled, summary:document.getElementById("width-summary").textContent})')
            (OUT/'initial-state.json').write_bytes((json.dumps({'state':state,'page_errors':errors},indent=2)+'\n').encode())
            assert state['metric']=='all' and state['disabled'] is True and not errors,(state,errors)
            for value,expected in [('direct',94),('new_qualified_reference',1),('member_references',8),('needs_width_evidence',9),('all',111)]:
                page.select_option('#width-filter',value)
                assert page.locator('#width-rows tr').count()==expected,(value,expected)
            checks.append('All111 identities, card link identities, coverage filters and unpooled default order')
            for current,record,needles in [
                ('south-java','south-java-sprintall-2010-ombai-thermal-front-confinement-reference',['10–15','confinement','not a rigorous upper bound']),
                ('east-african-coastal','eacc-dekeyzer-2012-bell-cited-width-lower-bound',['> 160 km']),
                ('north-equatorial-undercurrent', 'neuc-glider-2015-northern-jet-range',['0–200 km','explicitly reported range endpoint'])]:
                page.fill('#width-search','')
                owner=next(r['entity_id'] for r in document['evidence'] if r['id']==record)
                tr=page.locator(f'tr[data-current-id="{owner}"]')
                tr.locator('summary').click()
                box=tr.locator(f'[data-evidence-id="{record}"]')
                for needle in needles:assert needle in box.inner_text(),(record,needle)
                if current=='south-java':
                    page.fill('#width-search','South Java')
                    page.screenshot(path=str(OUT/'qualified-confinement.png'),full_page=True)
                    page.fill('#width-search','')
                tr.locator('summary').click()
            checks.append('Strict bound, reported zero range endpoint and qualified one-sided confinement remain distinct')
            page.select_option('#width-filter','member_references')
            assert 'No parent width assigned or added.' in page.locator('#width-rows').inner_text()
            page.locator('#width-rows summary').first.click()
            assert page.locator('#width-rows .width-record').count()>0
            page.screenshot(path=str(OUT/'family-members.png'))
            page.select_option('#width-filter','all')
            seasonal=page.locator('tr[data-current-id="current:northern-mediterranean"]')
            seasonal.locator('summary').click()
            assert 'Compatible seasonal comparison' in seasonal.inner_text()
            metric=next(r['metric'] for r in document['evidence'] if r['point_km'] is not None)
            page.select_option('#width-metric',metric);page.select_option('#width-order','value')
            selected=page.locator('#width-rows tr').evaluate_all('(els)=>els.map(e=>e.dataset.currentId)')
            points={r['entity_id']:max((e['point_km'] if e['point_km'] is not None else -1 for e in document['evidence'] if e['entity_id']==r['entity_id'] and e['metric']==metric),default=-1) for r in rows}
            assert all(points[a]>=points[b] for a,b in zip(selected,selected[1:]))
            page.select_option('#width-metric','all')
            assert page.locator('#width-order').input_value()=='name'
            checks.append('Member references, compatible seasonal comparison and single-definition point ordering')
            with page.expect_download() as pending:page.get_by_role('link',name='Download evidence CSV').click()
            assert hashlib.sha256(Path(pending.value.path()).read_bytes()).hexdigest()==sha('research/current-width-register-v1.csv')
            for path in set(r['source_file'] for r in document['evidence'])|{'plans/current-width-register-v1.md','research/current-width-register-v1.json'}:
                response=context.request.get(base+'/'+path)
                assert response.status==200 and hashlib.sha256(response.body()).hexdigest()==sha(path),path
                assets.add(path)
            page.set_viewport_size({'width':390,'height':844})
            page.fill('#width-search','South Java');page.locator('#width-rows summary').click()
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'), 'Document mobile overflow'
            assert page.locator('.width-scroll').evaluate('(e)=>e.scrollWidth<=e.clientWidth'), 'Table mobile overflow'
            page.screenshot(path=str(OUT/'mobile.png'),full_page=True)
            assert not errors,errors
            assert not any('.wasm' in u or 'query-packet' in u or '/release/' in u for u in requests)
            checks.append('CSV/source bytes, mobile layout, no JavaScript errors and no runtime packet requested')
            browser.close()
        result={'status':'PASS','source_commit':os.environ['GITHUB_SHA'],'counts':document['counts'],'checks':checks,'source_assets_checked':len(assets),'input_sha256':preflight['input_sha256'],'browser_scope':'Lightweight width register only; current card href identities verified, destinations not re-executed.','physical_width_gaps_closed':False,'runtime_loaded':False}
        (OUT/'result.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
        print(json.dumps(result))
    finally:server.shutdown();server.server_close()


if __name__=='__main__':run()
