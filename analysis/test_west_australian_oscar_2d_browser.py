"""Exact monthly source maps through Rust/WASM and current-card evidence links."""
import gzip
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote

from playwright.sync_api import sync_playwright

from build_west_australian_oscar_2d_source import ROOT, REPORT, verify
from test_current_research_evidence_browser import native

BASE = 'http://127.0.0.1:8788'


def main():
    document, _ = verify()
    out = ROOT/'.pytest_cache/west-australian-2d-browser'; out.mkdir(exist_ok=True)
    with TemporaryDirectory(dir=out) as temp, sync_playwright() as pw:
        index = Path(temp)/'index.json'; index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        browser = pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page = browser.new_page(viewport={'width':1280,'height':950}); errors=[]; originals=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.on('request',lambda request:originals.append(request.url) if request.url.lower().endswith(('.zip','.nc','.pdf')) else None)
        query={'document':REPORT,'pointer':'/months','limit':12,'offset':0}
        page.goto(BASE+'/almanac/query.html?source-q='+quote(json.dumps(query)))
        page.wait_for_function('window.oswSourceQueryResult',timeout=90000)
        result=page.evaluate('oswSourceQueryResult')
        assert result==native(query,index=index)
        assert [row['record'] for row in result['rows']]==document['months'] and result['total']==12
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert page.locator('#source-query-export').is_enabled()
        print('PASS all12 source fields/counts exact native/actualWASM and320px',flush=True)
        for current,label in [('west-australian','Compare twelve surrounding offshore source-vector maps'),
                              ('east-australian','Compare calendar-month and year section-span distributions')]:
            page.goto(BASE+'/almanac/reference-routes.html?atlas-feature=current%3A'+current+'#route-atlas')
            links=page.locator('.route-atlas-evidence-links');links.wait_for(state='attached',timeout=90000)
            links.locator('summary').focus();page.keyboard.press('Enter')
            link=links.get_by_role('link',name=label,exact=True);link.wait_for()
            if current=='west-australian':
                assert link.get_attribute('href')=='../'+document['comparison_figure']
                assert links.get_by_role('link',name='Query surrounding monthly source fields and paired support',exact=True).count()==1
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            print('PASS keyboard current-card evidence navigation',current,flush=True)
        page.goto(BASE+'/'+document['comparison_figure']); assert page.locator('svg').count()==1
        browser.close();assert not errors and not originals,(errors,originals)
    receipt={'status':'PASS','monthly_fields_exact_native_actual_wasm':12,'paired_support_exact':True,
             'keyboard_current_cards':['west-australian','east-australian'],'mobile_320px':True,'automatic_original_requests':0}
    (out/'result.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8');print(json.dumps(receipt),flush=True)


if __name__=='__main__':main()
