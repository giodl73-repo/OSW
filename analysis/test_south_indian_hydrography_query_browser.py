"""Actual complete source-cell native/WASM readback and atlas navigation."""
import gzip
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote

from playwright.sync_api import sync_playwright,expect
from south_indian_hydrography_query import evidence,COLLECTION,ROOT
from south_indian_paired_profiles_v2 import REPORT
from test_current_research_evidence_browser import native,BASE


def main():
    rows,_,report,_=evidence()
    out=ROOT/'.pytest_cache/south-indian-hycom-2013/query-browser';out.mkdir(parents=True,exist_ok=True)
    errors=[];originals=[];checked=0
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page=browser.new_page(viewport={'width':1280,'height':900})
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('request',lambda r:originals.append(r.url) if r.url.endswith(('.npz','.zip','.pdf','.nc')) else None)
        for month in range(1,13):
            for depth in [15,1000]:
                expected=sorted([r for r in rows if r['month']==month and r['depth_m']==depth],key=lambda r:r['id'])
                assert len(expected)==978
                for offset in [0,500]:
                    query={'collection':COLLECTION,'filters':[{'field':'month','op':'eq','value':month},
                           {'field':'depth_m','op':'eq','value':depth}],
                           'sort':{'field':'id','direction':'asc'},'limit':500,'offset':offset}
                    if checked==0:
                        page.goto(BASE+'/almanac/query.html?q='+quote(json.dumps(query)))
                    else:
                        # Exercise successive queries in the loaded workspace, as a reader does.
                        page.locator('#query-advanced').evaluate('(node)=>node.open=true')
                        page.locator('#query-json').fill(json.dumps(query))
                        page.evaluate('window.oswLastQueryResult=null')
                        page.locator('#query-run-json').click()
                    page.wait_for_function('window.oswLastQueryResult',timeout=180000)
                    result=page.evaluate('window.oswLastQueryResult')
                    assert result==native(query)
                    assert result['total']==978 and result['rows']==expected[offset:offset+500]
                    assert page.locator('#query-export').is_enabled()
                    checked+=len(result['rows'])
                print('PASS all native/WASM source cells',month,depth,flush=True)
        assert checked==23472
        with TemporaryDirectory(dir=out) as temporary:
            index=Path(temporary)/'index.json'
            index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
            for document,pointer,limit,expected in [
                (REPORT,'/cases',72,report['cases']),
                ('research/source-data/hycom-south-indian-hydrography-2013/monthly-fields.json','/months',12,
                 json.loads((ROOT/'research/source-data/hycom-south-indian-hydrography-2013/monthly-fields.json').read_bytes())['months'])]:
                query={'document':document,'pointer':pointer,'limit':limit,'offset':0}
                page.goto(BASE+'/almanac/query.html?source-q='+quote(json.dumps(query)))
                page.wait_for_function('window.oswSourceQueryResult',timeout=180000)
                result=page.evaluate('window.oswSourceQueryResult')
                assert result==native(query,index=index)
                assert [r['record'] for r in result['rows']]==expected
                print('PASS full lossless source',document,flush=True)
        page.set_viewport_size({'width':320,'height':900})
        page.goto(BASE+'/almanac/reference-routes.html?atlas-feature=current%3Asouth-indian#route-atlas')
        links=page.locator('.route-atlas-evidence-links');links.wait_for(state='attached',timeout=180000)
        links.locator('summary').focus();page.keyboard.press('Enter')
        link=links.get_by_role('link',name='Explore paired velocity, temperature and salinity profiles (2013)',exact=True)
        expect(link).to_be_visible();link.focus();page.keyboard.press('Enter')
        expect(page.get_by_role('heading',name='South Indian Current: paired source profiles')).to_be_visible(timeout=30000)
        expect(page.locator('#month')).to_be_enabled()
        page.locator('#month').select_option('7');page.locator('#depth').select_option('1')
        page.locator('#cell-query').focus();page.keyboard.press('Enter')
        page.wait_for_function('window.oswLastQueryResult',timeout=180000)
        result=page.evaluate('window.oswLastQueryResult')
        assert result['collection']==COLLECTION and result['total']==326
        assert all(r['month']==8 and r['depth_m']==1000 and r['longitude_degrees_east']==80 for r in result['rows'])
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.screenshot(path=str(out/'current-card-profile-query-phone.png'),full_page=True)
        assert not errors and not originals,(errors,originals)
        browser.close()
    result={'status':'PASS','native_wasm_source_cells_exact':checked,'full_diagnostic_cases':72,
            'complete_native_source_months':12,'keyboard_card_profile_query':True,'phone320px':True,
            'automatic_original_downloads':0,'physical_width_admitted':False}
    (out/'result.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result))


if __name__=='__main__':main()
