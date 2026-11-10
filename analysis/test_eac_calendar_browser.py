"""Calendar data survive exact native/WASM source queries and mobile display."""
import gzip
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote, unquote

from playwright.sync_api import sync_playwright

from build_eac_calendar_distributions import ROOT, REPORT, verify
from test_current_research_evidence_browser import native

BASE = 'http://127.0.0.1:8788'


def main():
    document, _ = verify()
    out = ROOT/'.pytest_cache/eac-calendar-browser'; out.mkdir(exist_ok=True)
    with TemporaryDirectory(dir=out) as temp, sync_playwright() as pw:
        index = Path(temp)/'index.json'
        index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        browser = pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page = browser.new_page(viewport={'width': 1280, 'height': 950})
        errors, originals = [], []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda request: originals.append(request.url) if request.url.lower().endswith(('.nc', '.npz', '.pdf')) else None)
        for number, pointer in enumerate(['/calendar_month_groups', '/calendar_year_groups']):
            query = {'document': REPORT, 'pointer': pointer, 'limit': 25, 'offset': 0}
            if number == 0:
                page.goto(BASE+'/almanac/query.html?source-q='+quote(json.dumps(query)))
            else:
                page.locator('#source-query-panel details').evaluate('(node)=>node.open=true')
                page.locator('#source-query-json').fill(json.dumps(query))
                page.evaluate('oswSourceQueryResult=null')
                page.locator('#source-query-run-json').click()
            page.wait_for_function('window.oswSourceQueryResult', timeout=90000)
            result = page.evaluate('oswSourceQueryResult')
            assert result == native(query, index=index)
            assert [r['record'] for r in result['rows']] == document[pointer[1:]]
            assert result['total'] == (12 if number == 0 else 11)
            print('PASS exact native/actualWASM calendar source', pointer, flush=True)
        page.set_viewport_size({'width': 320, 'height': 800})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert page.locator('#source-query-export').is_enabled()
        row = native({'collection': 'objects', 'filters': [{'field': 'id', 'op': 'eq', 'value': 'current:east-australian'}], 'limit': 1})['rows'][0]
        assert any(REPORT in unquote(link['url']) for link in row['evidence_links'])
        assert any(link['url'].endswith(document['comparison_figure']) for link in row['evidence_links'])
        page.goto(BASE+'/'+document['comparison_figure'])
        assert page.locator('svg').count() == 1
        page.set_viewport_size({'width':1280,'height':950})
        for label, address in [('card','reference-routes.html?atlas-feature=current%3Aeast-australian#route-atlas'),
                               ('seasons','seasons.html?current=east-australian'),
                               ('diagnostic','query.html?q='+quote(json.dumps({'collection':'diagnostics','filters':[{'field':'id','op':'eq','value':'diagnostic:eac-csiro100m-section-core-spans'}],'limit':1})))]:
            page.goto(BASE+'/almanac/'+address)
            comparison=page.locator('.eac-calendar-comparison')
            comparison.wait_for(state='attached',timeout=90000)
            comparison.evaluate('(node)=>{for(let p=node;p;p=p.parentElement)if(p.tagName==="DETAILS")p.open=true;}')
            comparison.get_by_role('link',name='Query calendar-month distributions',exact=True).wait_for()
            img=comparison.locator('img');img.scroll_into_view_if_needed()
            page.wait_for_function('document.querySelector(".eac-calendar-comparison img")?.naturalWidth > 0')
            page.set_viewport_size({'width':320,'height':800})
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.set_viewport_size({'width':1280,'height':950})
            print('PASS calendar comparison in',label,flush=True)
        browser.close()
        assert not errors and not originals, (errors, originals)
    receipt = {'status': 'PASS', 'exact_native_actual_wasm_month_groups': 12,
               'exact_native_actual_wasm_year_groups': 11, 'cases_per_group': 9,
               'object_navigation': True, 'mobile_320px': True, 'originals_requested': 0}
    receipt['calendar_comparison_views']=['card','seasons','diagnostic']
    (out/'result.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf8')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
