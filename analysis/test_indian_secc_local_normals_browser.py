"""Exact candidate outcomes, geometry support and accessible atlas navigation."""
import gzip,json,os
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect
from indian_secc_local_normals import ROOT,REPORT,verify
from test_current_research_evidence_browser import native,BASE


def main():
    d,_=verify();out=ROOT/'.pytest_cache/indian-secc-normals-browser';out.mkdir(exist_ok=True)
    passed=next(i for i,c in enumerate(d['cases']) if c['all_five_local_axis_checks_pass'])
    failed=next(i for i,c in enumerate(d['cases']) if c['status']=='weak_or_non_eastward_seed')
    errors=[];originals=[]
    with TemporaryDirectory(dir=out) as temp,sync_playwright() as pw:
        index=Path(temp)/'index.json';index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        browser=pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1360,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('request',lambda r:originals.append(r.url) if r.url.lower().endswith(('.zip','.nc','.pdf')) else None)
        for key,limit,offset in [('monthly_summary',12,0),('case_summaries',100,0),('case_summaries',100,100),
                                 ('step_comparisons',72,0),('cases',1,passed),('cases',1,failed)]:
            q={'document':REPORT,'pointer':'/'+key,'limit':limit,'offset':offset}
            page.goto(BASE+'/almanac/query.html?source-q='+quote(json.dumps(q)))
            page.wait_for_function('window.oswSourceQueryResult',timeout=120000)
            actual=page.evaluate('window.oswSourceQueryResult');assert actual==native(q,index=index)
            assert actual['total']==len(d[key]) and [r['record'] for r in actual['rows']]==d[key][offset:offset+limit]
            page.set_viewport_size({'width':320,'height':1000});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            assert page.locator('#source-query-export').is_enabled()
            print('PASS native/WASM',key,offset,len(actual['rows']),flush=True)
        page.goto(BASE+'/almanac/reference-routes.html?atlas-feature=current%3Aindian-south-equatorial-countercurrent#route-atlas')
        links=page.locator('.route-atlas-evidence-links');links.wait_for(state='attached',timeout=120000)
        links.locator('summary').focus();page.keyboard.press('Enter')
        link=links.get_by_role('link',name='Inspect velocity-normal sections and candidate-axis checks',exact=True)
        expect(link).to_be_visible();expect(link).to_have_attribute('href','../'+d['comparison_figure'])
        for name in ['Query all 144 local-axis outcomes','Query monthly normal-section support','Compare 72 sampling-step scenarios',
                     'Inspect complete normal sections and source-cell support']:
            assert links.get_by_role('link',name=name,exact=True).count()==1
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');links.screenshot(path=str(out/'card-mobile.png'))
        link.focus();page.keyboard.press('Enter');expect(page.locator('svg')).to_be_visible(timeout=30000)
        expect(page.locator('svg')).to_have_attribute('role','img')
        expect(page.locator('#secc-normal-title')).to_have_text('Indian SECC local velocity-normal diagnostics')
        assert 'no admitted named-current axis or width' in page.locator('#secc-normal-desc').text_content()
        assert not errors and not originals,(errors,originals);browser.close()
    receipt={'status':'PASS','exact_native_actual_wasm_case_summaries':144,'monthly_summaries':12,'step_comparisons':72,
             'complete_supported_candidate_case':True,'complete_failed_seed_case':True,'keyboard_card_figure':True,
             'accessible_standalone_svg':True,'mobile_320px':True,'automatic_original_requests':0}
    (out/'result.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)


if __name__=='__main__':main()
