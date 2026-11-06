"""Every ASCA section case survives the shared native/WASM query inventory."""
import json
import os
from pathlib import Path
from urllib.parse import unquote
from playwright.sync_api import sync_playwright,expect
from current_section_measurements import build
from test_current_research_evidence_browser import ROOT,BASE,native


def main():
    out=ROOT/'.pytest_cache/asca-section-measurements-browser';out.mkdir(exist_ok=True)
    all_rows,_=build();expected=sorted([r for r in all_rows if r['current_id']=='agulhas'],key=lambda r:r['id'])
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1280,'height':1000});errors=[];originals=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.on('request',lambda request:originals.append(request.url) if request.url.lower().split('?')[0].endswith(('.nc','.mat','.zip','.npz','.pdf')) else None)
        page.goto(BASE+'/almanac/reference-routes.html?atlas-feature=current%3Aagulhas#route-atlas')
        panel=page.locator('#route-atlas-preview .asca-component-spans')
        expect(panel).to_be_visible(timeout=90000)
        direct=panel.get_by_role('link',name='Query all dated section measurements',exact=True)
        query=json.loads(unquote(direct.get_attribute('href').split('?q=')[1]))
        assert query['filters']==[{'field':'current_id','op':'eq','value':'agulhas'}]
        direct.click();page.wait_for_function('window.oswLastQueryResult',timeout=90000)
        assert page.evaluate('oswLastQueryResult')==native(query)
        assert page.evaluate('oswLastQueryResult')['total']==2793
        def run(request):
            page.locator('#query-advanced').evaluate('(node)=>node.open=true')
            page.locator('#query-json').fill(json.dumps(request));page.evaluate('oswLastQueryResult=null')
            page.locator('#query-run-json').click();page.wait_for_function('window.oswLastQueryResult',timeout=90000)
            result=page.evaluate('oswLastQueryResult');assert result==native(request)
            return result
        base={**query,'limit':500};actual=[]
        for offset in range(0,2793,500):
            result=run({**base,'offset':offset})
            assert result['total']==2793
            actual.extend(result['rows'])
            print('PASS native/actualWASM ASCA cases',offset,len(result['rows']),flush=True)
        assert actual==expected
        assert sum(r['component_span_km'] is not None for r in actual)==1007
        primary=run({**base,'filters':query['filters']+[{'field':'is_primary_convention','op':'eq','value':True}]})
        assert primary['total']==931
        resolved=run({**base,'filters':query['filters']+[{'field':'is_primary_convention','op':'eq','value':True},
            {'field':'component_span_km','op':'gt','value':0}]})
        assert resolved['total']==330
        expected_resolved=[r for r in expected if r['is_primary_convention'] and r['component_span_km'] is not None]
        assert resolved['rows']==expected_resolved
        expect(page.locator('#query-rows')).to_contain_text('fixed-array component span')
        expect(page.locator('#query-rows')).to_contain_text('100 m below surface')
        expect(page.locator('#query-rows')).to_contain_text('source fixed-array −v')
        request={**base,'filters':query['filters']+[{'field':'year','op':'eq','value':2016},{'field':'month','op':'eq','value':5}]}
        month=run(request)
        assert month['rows']==[r for r in expected if r['year']==2016 and r['month']==5]
        row=month['rows'][0];page.locator('#query-rows button').first.click()
        detail=page.locator('#query-detail');expect(detail).to_be_visible()
        direct=detail.get_by_role('link',name='Inspect exact section measurement source',exact=True)
        source=json.loads(unquote(direct.get_attribute('href').split('source-q=')[1]))
        assert source['document']==row['source_file'] and source['pointer']==row['source_pointer']
        assert detail.get_by_role('link',name='Open atlas card',exact=True).count()==1
        page.set_viewport_size({'width':320,'height':740});page.emulate_media(reduced_motion='reduce')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert page.locator('#query-export').is_enabled()
        direct.click();page.wait_for_function('window.oswSourceQueryResult',timeout=90000)
        case=page.evaluate('oswSourceQueryResult')
        assert case['pointer']==row['source_pointer'] and case['source_sha256']==row['source_file_sha256']
        assert case['total']==len(row['source_case'])
        assert {field['source_key']:field['record'] for field in case['rows']}==row['source_case']
        assert not errors and not originals,(errors,originals)
        browser.close()
    receipt={'status':'PASS','all_asca_cases_native_actual_wasm':2793,'source_profiles':931,'finite_cases':1007,
        'primary_cases':931,'primary_finite':330,'primary_unresolved':601,'all_vertical_references_and_frames_exact':True,
        'year_month_filter':True,'direct_card_navigation':True,'source_case_and_atlas_links':True,
        'mobile_320px':True,'export':True,'originals_requested':0}
    (out/'result.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))


if __name__=='__main__':main()
