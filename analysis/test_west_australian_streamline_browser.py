"""Both complete numerical runs survive source queries and current-card navigation."""
import gzip
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote

from playwright.sync_api import sync_playwright

from west_australian_streamline_evidence import ROOT, REPORT, verify
from test_current_research_evidence_browser import native

BASE='http://127.0.0.1:8788'


def main():
    refined,_=verify();out=ROOT/'.pytest_cache/west-australian-streamline-browser';out.mkdir(exist_ok=True)
    with TemporaryDirectory(dir=out) as temporary,sync_playwright() as pw:
        index=Path(temporary)/'index.json';index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        browser=pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1280,'height':950});errors=[];originals=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('request',lambda r:originals.append(r.url) if r.url.lower().endswith(('.zip','.nc','.pdf')) else None)
        for number,file in enumerate([REPORT,refined['euler_baseline_file']]):
            query={'document':file,'pointer':'/cases','limit':117,'offset':0}
            if number==0:page.goto(BASE+'/almanac/query.html?source-q='+quote(json.dumps(query)))
            else:
                page.locator('#source-query-panel details').evaluate('(n)=>n.open=true')
                page.locator('#source-query-json').fill(json.dumps(query));page.evaluate('oswSourceQueryResult=null')
                page.locator('#source-query-run-json').click()
            page.wait_for_function('window.oswSourceQueryResult',timeout=90000)
            actual=page.evaluate('oswSourceQueryResult');assert actual==native(query,index=index)
            assert actual['total']==117
            assert [r['record'] for r in actual['rows']]==json.loads((ROOT/file).read_bytes())['cases']
            print('PASS all117 exact native/actualWASM',file,flush=True)
        page.set_viewport_size({'width':320,'height':800});assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert page.locator('#source-query-export').is_enabled()
        page.goto(BASE+'/almanac/reference-routes.html?atlas-feature=current%3Awest-australian#route-atlas')
        links=page.locator('.route-atlas-evidence-links');links.wait_for(state='attached',timeout=90000)
        links.locator('summary').focus();page.keyboard.press('Enter')
        for label,path in [('Compare refined regional lengths with the Euler baseline',refined['comparison_figure']),
                           ('See refined regional paths and retained failures',refined['path_figure'])]:
            assert links.get_by_role('link',name=label,exact=True).get_attribute('href')=='../'+path
        assert links.get_by_role('link',name='Query all117refined regional path attempts',exact=True).count()==1
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        for path in [refined['comparison_figure'],refined['path_figure']]:
            page.goto(BASE+'/'+path);assert page.locator('svg').count()==1
        browser.close();assert not errors and not originals,(errors,originals)
    receipt={'status':'PASS','exact_native_actual_wasm_cases':234,'both_numerical_runs_retained':True,
             'keyboard_current_card':True,'source_export':True,'mobile_320px':True,'automatic_original_requests':0}
    (out/'result.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8');print(json.dumps(receipt),flush=True)


if __name__=='__main__':main()
