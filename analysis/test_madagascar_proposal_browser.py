"""Missing southern Madagascar identity has exact source dimensions and accessible navigation."""
import gzip,hashlib,json,os
from urllib.parse import parse_qs,urlsplit
from playwright.sync_api import sync_playwright,expect
from test_current_research_evidence_browser import ROOT,BASE,native

SOURCE='research/ocean-current-inventory-expansion-candidates.json'
ID='southern-east-madagascar'

def main():
    out=ROOT/'.pytest_cache/madagascar-proposal';out.mkdir(exist_ok=True)
    doc=json.loads((ROOT/SOURCE).read_bytes());row=next(r for r in doc['entries'] if r['proposed_id']==ID)
    index=out/'source-index.json'
    with gzip.open(ROOT/'almanac/index-data.json.gz','rb') as src,index.open('wb') as dst:
        while chunk:=src.read(1<<20):dst.write(chunk)
    errors=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page=browser.new_page(viewport={'width':1280,'height':1000})
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(BASE+'/almanac/reference-routes.html#inventory-addition-'+ID)
            card=page.locator('#inventory-addition-'+ID)
            expect(card).to_contain_text('Reported dimensions',timeout=120000)
            expect(card).to_contain_text('Current identity admitted')
            assert page.locator('.inventory-addition-card').count()==28
            assert page.locator('.route-atlas-station').count()==100
            expect(card).to_contain_text('not include the northward branch')
            image=card.locator('.proposed-source-dimensions img');image.scroll_into_view_if_needed()
            page.wait_for_function('()=>document.querySelector("#inventory-addition-southern-east-madagascar img")?.naturalWidth>0')
            image.screenshot(path=str(out/'dimensions-desktop.png'))
            details=card.locator('.proposed-source-dimensions details')
            assert details.count()==2
            details.nth(0).locator('summary').focus();page.keyboard.press('Enter')
            assert details.nth(0).evaluate('(n)=>n.open')
            expect(details.nth(0)).to_contain_text('not a new length measured by the2001 cruise')
            details.nth(1).locator('summary').focus();page.keyboard.press('Enter')
            expect(details.nth(1)).to_contain_text('2001-04')
            page.set_viewport_size({'width':320,'height':950})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            card.screenshot(path=str(out/'card-mobile.png'))
            link=card.get_by_role('link',name='Query this current and its reported dimensions',exact=True)
            query=json.loads(parse_qs(urlsplit(link.get_attribute('href')).query)['source-q'][0])
            link.focus();page.keyboard.press('Enter')
            page.wait_for_function('window.oswSourceQueryResult',timeout=120000)
            result=page.evaluate('window.oswSourceQueryResult')
            assert result==native(query,index=index)
            assert result['total']==1 and result['rows'][0]['record']==row
            assert result['source_sha256']==hashlib.sha256((ROOT/SOURCE).read_bytes()).hexdigest()
            assert not errors,errors
            browser.close()
    finally:index.unlink(missing_ok=True)
    receipt={'status':'PASS','proposed_currents':28,'admitted_currents':101,'canonical_stations_unchanged':100,
        'source_dimensions_exact':2,'native_wasm_source_equal':True,'keyboard_details_and_link':True,
        'phone_reflow':True,'page_errors':errors}
    (out/'browser-result.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))

if __name__=='__main__':main()
