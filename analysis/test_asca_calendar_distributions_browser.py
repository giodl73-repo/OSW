"""Calendar source records and conditional ranges survive shipped native/WASM views."""
import hashlib,json,os
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect
from test_current_research_evidence_browser import ROOT,BASE,native

REPORT='research/asca-component-calendar-distributions.json'
ID='diagnostic:agulhas-asca100m-calendar-distributions'

def main():
    out=ROOT/'.pytest_cache/asca-calendar-browser';out.mkdir(exist_ok=True)
    doc=json.loads((ROOT/REPORT).read_bytes())
    query={'collection':'diagnostics','filters':[{'field':'id','op':'eq','value':ID}],'limit':1}
    errors=[];originals=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1280,'height':1000})
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('request',lambda r:originals.append(r.url) if r.url.split('?')[0].endswith(('.nc','.npz','.bin','.pdf')) else None)
        page.goto(BASE+'/almanac/reference-routes.html?atlas-feature=current%3Aagulhas#route-atlas')
        calendar=page.locator('#route-atlas-preview .asca-calendar-distributions')
        calendar.locator('summary').wait_for(timeout=120000)
        calendar.locator('summary').focus();page.keyboard.press('Enter')
        assert calendar.evaluate('(n)=>n.open')
        expect(calendar).to_contain_text('131 / 438')
        assert calendar.locator('tbody tr').count()==16
        image=calendar.locator('img');image.scroll_into_view_if_needed()
        page.wait_for_function('()=>document.querySelector("#route-atlas-preview .asca-calendar-distributions img")?.naturalWidth>0',timeout=30000)
        image.screenshot(path=str(out/'figure-desktop.png'))
        page.set_viewport_size({'width':320,'height':1000})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        scroll=calendar.get_by_role('region');scroll.focus();before=scroll.evaluate('(n)=>n.scrollLeft')
        page.keyboard.press('ArrowRight');page.wait_for_timeout(250);assert scroll.evaluate('(n)=>n.scrollLeft')>before
        scroll.screenshot(path=str(out/'table-mobile.png'))
        year=calendar.locator('[data-cohort="asca-calendar:calendar_year:2017:f50"] a')
        year.focus();page.keyboard.press('Enter')
        page.wait_for_function('window.oswSourceQueryResult',timeout=120000)
        result=page.evaluate('window.oswSourceQueryResult')
        expected=next(r for r in doc['records'] if r['id']=='asca-calendar:calendar_year:2017:f50')
        assert result['total']==1 and result['rows'][0]['record']==expected
        page.goto(BASE+'/almanac/query.html?source-q='+quote(json.dumps({'document':REPORT,'pointer':'/records','limit':100})))
        page.wait_for_function('window.oswSourceQueryResult',timeout=120000)
        result=page.evaluate('window.oswSourceQueryResult')
        assert result['total']==48 and [r['record'] for r in result['rows']]==doc['records']
        assert result['source_sha256']==hashlib.sha256((ROOT/REPORT).read_bytes()).hexdigest()
        page.goto(BASE+'/almanac/query.html?q='+quote(json.dumps(query)))
        page.wait_for_function('window.oswLastQueryResult',timeout=120000)
        assert page.evaluate('window.oswLastQueryResult')==native(query)
        expect(page.locator('.asca-calendar-distributions')).to_be_visible()
        assert not errors and not originals,(errors,originals)
        browser.close()
    receipt={'status':'PASS','calendar_records_exact':48,'primary_table_cohorts':16,
        'native_wasm_diagnostic_equal':True,'year_query_keyboard':True,'phone_reflow':True,
        'table_keyboard_scroll':True,'page_errors':errors,'original_requests':originals}
    (out/'browser-result.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))

if __name__=='__main__':main()
