"""Exact new fields and summaries through the shipped Rust/WASM source store."""
import gzip,json,os
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect
from build_indian_secc_oscar_2d_source import ROOT,REPORT,verify
from test_current_research_evidence_browser import native,BASE

def main():
    d,_=verify();out=ROOT/'.pytest_cache/indian-secc-2d-browser';out.mkdir(exist_ok=True)
    errors=[];originals=[]
    with TemporaryDirectory(dir=out) as temp,sync_playwright() as pw:
        index=Path(temp)/'index.json';index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        browser=pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1360,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('request',lambda r:originals.append(r.url) if r.url.lower().endswith(('.zip','.nc','.pdf')) else None)
        for pointer,key in [('/months','months'),('/monthly_summary','monthly_summary')]:
            q={'document':REPORT,'pointer':pointer,'limit':12,'offset':0}
            page.goto(BASE+'/almanac/query.html?source-q='+quote(json.dumps(q)))
            page.wait_for_function('window.oswSourceQueryResult',timeout=120000)
            actual=page.evaluate('window.oswSourceQueryResult');assert actual==native(q,index=index)
            assert [r['record'] for r in actual['rows']]==d[key] and actual['total']==12
            page.set_viewport_size({'width':320,'height':1000});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            assert page.locator('#source-query-export').is_enabled()
            print('PASS exact native/WASM source fields',pointer,flush=True)
        page.goto(BASE+'/almanac/reference-routes.html?atlas-feature=current%3Aindian-south-equatorial-countercurrent#route-atlas')
        links=page.locator('.route-atlas-evidence-links');links.wait_for(state='attached',timeout=120000)
        links.locator('summary').focus();page.keyboard.press('Enter')
        link=links.get_by_role('link',name='Compare twelve surrounding Indian Ocean source-vector maps',exact=True)
        expect(link).to_be_visible();expect(link).to_have_attribute('href','../'+d['comparison_figure'])
        assert links.get_by_role('link',name='Query monthly source coverage and component ranges',exact=True).count()==1
        expect(links.get_by_role('link',name='Download retained source vectors and metadata (ZIP)',exact=True)).to_have_attribute('href','../research/source-data/oscar-indian-secc-2d-2013/source-responses.zip')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        links.screenshot(path=str(out/'card-mobile.png'))
        link.focus();page.keyboard.press('Enter');expect(page.locator('svg')).to_be_visible(timeout=30000)
        assert not errors and not originals,(errors,originals)
        browser.close()
    receipt={'status':'PASS','monthly_fields_exact_native_wasm':12,'summary_records_exact_native_wasm':12,
        'keyboard_current_card_navigation':True,'mobile_320px':True,'automatic_original_requests':0}
    (out/'result.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)

if __name__=='__main__':main()
