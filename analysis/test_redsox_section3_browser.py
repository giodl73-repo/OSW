"""Dated observed-section data and its map survive the actual browser engine."""
import gzip
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote
from playwright.sync_api import sync_playwright, expect
from build_redsox_section3_spans import ROOT, REPORT, build
from test_current_research_evidence_browser import native


def main():
    report=build();out=ROOT/'.pytest_cache/redsox-section3-browser';out.mkdir(exist_ok=True)
    with TemporaryDirectory(dir=out) as folder, sync_playwright() as pw:
        index=Path(folder)/'index.json'
        index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        browser=pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1280,'height':1000});errors=[];originals=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('request',lambda r:originals.append(r.url) if r.url.lower().split('?')[0].endswith(('.pdf','.zip','.mat','.nc')) else None)
        query={'document':REPORT,'pointer':'/layers','limit':3,'offset':0}
        page.goto('http://127.0.0.1:8788/almanac/query.html?source-q='+quote(json.dumps(query)))
        page.wait_for_function('window.oswSourceQueryResult',timeout=90000)
        result=page.evaluate('oswSourceQueryResult')
        assert result==native(query,index=index)
        assert [row['record'] for row in result['rows']]==report['layers']
        assert page.locator('#source-query-export').is_enabled()
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Ared-sea-saline-overflow#route-atlas')
        panel=page.locator('#route-atlas-preview .current-research-evidence')
        expect(panel).to_be_visible(timeout=90000)
        expect(panel).to_contain_text('About 5.0 km')
        expect(panel).to_contain_text('Earlier primary 20–60 m result')
        expect(panel).to_contain_text('Independent southern section')
        details=panel.locator('details');details.locator('summary').focus();page.keyboard.press('Enter')
        details.get_by_label('Analysis view').select_option('1')
        expect(details.locator('img')).to_have_attribute('src','../figures/redsox-winter-section3-component-spans.svg')
        expect(details.locator('img')).to_have_js_property('complete',True)
        assert details.locator('img').evaluate('(img)=>img.naturalWidth>0')
        assert panel.locator('table').last.locator('tbody tr').count()==3
        expect(panel).to_contain_text('12.6 km')
        page.set_viewport_size({'width':320,'height':850})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        panel.get_by_role('link',name='All 30 independent section cases',exact=True).click()
        page.wait_for_function('window.oswSourceQueryResult',timeout=90000)
        assert page.evaluate('oswSourceQueryResult')['total']==3
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        browser.close()
        assert not errors and not originals,(errors,originals)
    receipt={'status':'PASS','native_actual_wasm_cases':30,'preserved_unresolved':20,
        'current_card_keyboard_figure':True,'source_export':True,'mobile_320px':True,
        'automatic_original_requests':0,'page_errors':0}
    (out/'result.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    print(json.dumps(receipt),flush=True)


if __name__=='__main__':
    main()
