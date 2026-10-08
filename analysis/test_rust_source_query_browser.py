"""The source workspace exposes the checked catalog without eager loading or fallback."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from urllib.parse import parse_qs, quote, urlparse
from playwright.sync_api import sync_playwright
from test_rust_query_browser import ROOT, CLI, BASE


def main():
    catalog=json.loads((ROOT/'almanac/index-catalog.json').read_bytes())
    source='research/indian-sec-monthly-bifurcation-extraction.json'
    monthly=json.loads((ROOT/source).read_bytes())['series'][1]['months']
    original={'collection':'width_samples','filters':[{'field':'current_id','op':'eq','value':'florida'}],'limit':100}
    value={'document':source,'pointer':'/series/1/months','filters':[{'field':'record.month','op':'gte','value':6}],
           'sort':{'field':'record.month','direction':'desc'},'limit':2,'offset':0}
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as folder:
        packet=Path(folder)/'index.json';packet.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        def native(request):
            run=subprocess.run([str(CLI),'--index',str(packet),'-'],input=json.dumps(request),text=True,encoding='utf-8',capture_output=True)
            assert run.returncode==0,run.stderr
            return json.loads(run.stdout)
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page=browser.new_page(viewport={'width':1280,'height':1000})
            requests=[];errors=[]
            page.on('request',lambda r:requests.append(r.url));page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(BASE+'?q='+quote(json.dumps(original)))
            page.wait_for_function('window.oswLastQueryResult',timeout=90000)
            assert not any('index-data.json.gz' in url or 'index-worker.js' in url for url in requests)
            page.locator('#source-query-panel > summary').click()
            page.wait_for_function('window.oswSourceQueryResult',timeout=90000)
            assert page.locator('#source-query-document option').evaluate_all('(nodes)=>nodes.map(n=>n.value)')==[d['path'] for d in catalog['documents']]
            initial={'document':'research/ocean-current-almanac.json','pointer':'/entries','limit':25,'offset':0}
            assert page.evaluate('window.oswSourceQueryResult')==native(initial)
            assert page.locator('#source-query-rows tr').count()==25
            page.locator('#source-query-panel details summary').click()
            def query(request):
                page.locator('#source-query-json').fill(json.dumps(request))
                page.locator('#source-query-run-json').click()
                page.wait_for_function('()=>document.querySelector("#source-query-status").dataset.pending==="false"')
                return page.evaluate('window.oswSourceQueryResult')
            actual=query(value)
            assert actual==native(value)
            assert actual['total']==7 and [r['record'] for r in actual['rows']]==list(reversed(monthly[5:]))[:2]
            assert [r['source_pointer'] for r in actual['rows']]==['/series/1/months/11','/series/1/months/10']
            page.locator('#source-query-rows pre').first.focus()
            assert page.locator('#source-query-rows pre').first.evaluate('(el)=>el===document.activeElement&&el.tabIndex===0')
            assert page.locator('#source-query-rows tr').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.sourcePointer)')==[r['source_pointer'] for r in actual['rows']]
            assert hashlib.sha256((ROOT/source).read_bytes()).hexdigest() in page.locator('#source-query-receipt').inner_text()
            assert 'record.month' in page.locator('#source-query-active').inner_text()
            for offset in [2,4,6]:
                page.locator('#source-query-next').click()
                page.wait_for_function('offset=>window.oswSourceQueryResult?.offset===offset',arg=offset)
                actual=page.evaluate('window.oswSourceQueryResult')
                assert actual==native({**value,'offset':offset})
            assert page.locator('#source-query-next').is_disabled()
            assert page.locator('#source-query-rows tr').count()==1
            with page.expect_download() as download:
                page.locator('#source-query-export').click()
            downloaded=json.loads(Path(download.value.path()).read_bytes())
            assert downloaded=={'query':{**value,'offset':6},'result':actual}
            with page.expect_download() as download:
                page.locator('#source-query-rows button').first.click()
            exported=json.loads(Path(download.value.path()).read_bytes())
            assert exported['record']==monthly[5] and exported['source_pointer']=='/series/1/months/5'
            page.locator('#source-query-previous').click()
            page.wait_for_function('window.oswSourceQueryResult?.offset===4')
            # Basic text controls keep advanced constraints visible on the same source.
            page.locator('#source-query-run').click()
            page.wait_for_function('window.oswSourceQueryResult?.offset===0')
            assert page.evaluate('window.oswSourceQueryResult.total')==7
            assert page.locator('#source-query-active').is_visible()
            for bad in [{**value,'pointer':'/does-not-exist'},{**value,'pointer':'/units'},{**value,'filters':[{'field':'record.month','op':'invented','value':6}]}]:
                assert query(bad) is None
                assert page.locator('#source-query-rows tr').count()==0
                assert page.locator('#source-query-export').is_disabled()
                assert page.locator('#source-query-share').is_hidden()
                assert page.locator('#source-query-status').inner_text().startswith('Source query unavailable:')
            pacific_request={'document':'research/pacific-nec-monthly-bifurcation-extraction.json','pointer':'/series/0/months','sort':{'field':'record.month','direction':'asc'},'limit':12}
            pacific_rows=json.loads((ROOT/pacific_request['document']).read_bytes())['series'][0]['months']
            pacific_result=query(pacific_request)
            assert pacific_result==native(pacific_request)
            assert [r['record'] for r in pacific_result['rows']]==pacific_rows
            assert page.locator('#source-query-rows tr').count()==12
            assert query(value)==native(value)
            shared=page.locator('#source-query-share').get_attribute('href')
            assert json.loads(parse_qs(urlparse(shared).query)['q'][0])==original
            assert json.loads(parse_qs(urlparse(shared).query)['source-q'][0])==value
            page.set_viewport_size({'width':320,'height':800})
            page.locator('#source-query-panel').screenshot(path=str(ROOT/'.pytest_cache/source-query-mobile.png'))
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),page.evaluate('()=>[...document.querySelectorAll("#source-query-panel *")].filter(n=>n.getBoundingClientRect().right>innerWidth+1).map(n=>({tag:n.tagName,id:n.id,right:n.getBoundingClientRect().right})).slice(0,20)')
            assert not errors,errors
            page.close()
            restored=browser.new_page();restored.goto(shared)
            restored.wait_for_function('window.oswSourceQueryResult',timeout=90000)
            assert restored.locator('#source-query-panel').get_attribute('open') is not None
            assert restored.evaluate('window.oswSourceQueryResult')==native(value)
            restored.close()
            unavailable=browser.new_page()
            unavailable.route('**/index-data.json.gz',lambda r:r.fulfill(status=503,body='Unavailable'))
            unavailable.goto(BASE)
            unavailable.wait_for_function('window.oswLastQueryResult',timeout=90000)
            original_result=unavailable.evaluate('window.oswLastQueryResult')
            unavailable.locator('#source-query-panel > summary').click()
            unavailable.wait_for_function('()=>document.querySelector("#source-query-status").textContent.includes("unavailable")',timeout=90000)
            assert unavailable.locator('#source-query-rows tr').count()==0
            assert unavailable.locator('#source-query-run').is_disabled()
            assert unavailable.evaluate('window.oswLastQueryResult')==original_result
            browser.close()
    print('PASS: lazy checked source catalog, native/WASM/source equality, addresses, filters, pagination, downloads, sharing, mobile and isolated failures')


if __name__=='__main__':main()
