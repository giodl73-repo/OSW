"""Calendar interaction, scope, mobile access and native/WASM source parity."""
import copy,gzip,hashlib,json,os,subprocess,tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_rust_query_browser import ROOT,CLI,native
from check_zeehan_seasonal_calendar import PATH

def main():
    audit=json.loads((ROOT/PATH).read_bytes());claims=audit['seasonal_calendar']['claims']
    request={'document':PATH,'pointer':'/seasonal_calendar/claims','limit':100}
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as folder:
        index=Path(folder)/'index.json';index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        expected=json.loads(subprocess.check_output([str(CLI),'--index',str(index),'-'],input=json.dumps(request),encoding='utf8'))
        assert [r['record'] for r in expected['rows']]==claims
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page=browser.new_page(viewport={'width':1280,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#zeehan-reference-path-candidate')
            panel=page.locator('#zeehan-reference-path-candidate .qualitative-current-calendar');panel.wait_for(state='visible',timeout=90000)
            assert panel.locator('button').count()==12
            for month in audit['seasonal_calendar']['months']:
                panel.locator('button').nth(month['month']-1).click()
                assert panel.locator('button[aria-pressed=true]').count()==1
                assert panel.locator('li strong').all_text_contents()==[next(c['label']+': ' for c in claims if c['id']==ident) for ident in month['claim_ids']]
            panel.get_by_role('button',name='Oct seasonal claims').focus();page.keyboard.press('Enter')
            assert 'anomaly relative to mean flow' in panel.inner_text()
            assert 'disappearance' not in panel.locator('[aria-live]').inner_text()
            assert panel.locator('svg,circle,path').count()==0
            assert 'Month selection does not change its geometry' in panel.inner_text()
            page.set_viewport_size({'width':320,'height':800})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            assert panel.locator('button').evaluate_all('(buttons)=>buttons.every(b=>b.getBoundingClientRect().height>=44)')
            assert panel.locator('button').evaluate_all('(buttons)=>buttons.every(b=>b.scrollWidth<=b.clientWidth)')
            assert panel.locator('button[aria-pressed=true]').inner_text()=='Oct ✓'
            panel.screenshot(path=str(ROOT/'.pytest_cache/zeehan-calendar-mobile.png'))
            panel.get_by_role('link',name='Query the six seasonal claims').click()
            page.wait_for_function('window.oswSourceQueryResult?.total===6',timeout=90000)
            assert page.evaluate('oswSourceQueryResult')==expected
            assert not errors,errors
            browser.close()
        query={'collection':'route_decisions','filters':[{'field':'current_id','op':'eq','value':'zeehan'}],'limit':10}
        result=native(query);assert result['total']==1
        assert any(r['document']==audit for r in result['rows'][0]['scope_reviews'])
        packet=json.loads((ROOT/'almanac/query-data.json').read_bytes())
        for key,value in [('width_values',[20]*12),('seasonal_geometry_playback_eligible',True),('observation_dates',['2007-06-01'])]:
            bad=copy.deepcopy(packet);doc=copy.deepcopy(audit);doc['seasonal_calendar'][key]=value
            receipt=bad['manifest']['atlas_receipts'][PATH];receipt['source_json']=json.dumps(doc);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest();bad['manifest']['input_sha256'][PATH]=receipt['source_sha256']
            owner=next(r for r in bad['collections']['route_decisions'] if r['current_id']=='zeehan')
            review=next(r for r in owner['scope_reviews'] if r['document']['current_id']=='zeehan');review['document']=doc;review['source_sha256']=receipt['source_sha256']
            target=Path(folder)/'tampered.json';target.write_text(json.dumps(bad),encoding='utf8')
            run=subprocess.run([str(CLI),str(target),'-'],input=json.dumps(query),text=True,capture_output=True,encoding='utf8')
            assert run.returncode==2 and 'Zeehan calendar' in run.stderr,run.stderr
    print('PASS: Zeehan calendar, keyboard/mobile access, source/native/WASM parity and coherent scope mutations')
if __name__=='__main__':main()
