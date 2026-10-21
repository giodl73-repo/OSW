"""Repeat observations and unresolved comparisons in actual native/WASM UI."""
import gzip
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote, unquote
from playwright.sync_api import sync_playwright, expect
from build_redsox_section3_repeat import ROOT, REPORT, build
from test_current_research_evidence_browser import native
from current_section_measurements import build as typed_measurements


def main():
    report=build();out=ROOT/'.pytest_cache/redsox-repeat-browser';out.mkdir(exist_ok=True)
    with TemporaryDirectory(dir=out) as folder,sync_playwright() as pw:
        index=Path(folder)/'index.json'
        index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        browser=pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        version=browser.version
        page=browser.new_page(viewport={'width':1280,'height':1000});errors=[];originals=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('request',lambda r:originals.append(r.url) if r.url.lower().split('?')[0].endswith(('.pdf','.zip','.nc','.mat')) else None)
        for count,(pointer,key) in enumerate([('/summer_layers','summer_layers'),('/comparisons','comparisons'),('/station_correspondence','station_correspondence')]):
            query={'document':REPORT,'pointer':pointer,'limit':30,'offset':0}
            if count==0:
                page.goto('http://127.0.0.1:8788/almanac/query.html?source-q='+quote(json.dumps(query)))
            else:
                page.locator('#source-query-panel details').evaluate('(node)=>node.open=true')
                page.locator('#source-query-json').fill(json.dumps(query));page.evaluate('oswSourceQueryResult=null')
                page.locator('#source-query-run-json').click()
            page.wait_for_function('window.oswSourceQueryResult',timeout=90000)
            actual=page.evaluate('oswSourceQueryResult')
            assert actual==native(query,index=index)
            assert [row['record'] for row in actual['rows']]==report[key]
            print('PASS exact native/actualWASM',pointer,flush=True)
        assert page.locator('#source-query-export').is_enabled()
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Ared-sea-saline-overflow#route-atlas')
        panel=page.locator('#route-atlas-preview .current-research-evidence')
        expect(panel).to_be_visible(timeout=90000)
        expect(panel).to_contain_text('About 3.1 km · saline screen fails')
        expect(panel).to_contain_text('Earlier primary 20–60 m result')
        details=panel.locator('details');details.locator('summary').focus();page.keyboard.press('Enter')
        for option,path in [('1','figures/redsox-winter-section3-component-spans.svg'),('2','figures/redsox-section3-repeat-surveys.svg')]:
            details.get_by_label('Analysis view').select_option(option)
            expect(details.locator('img')).to_have_attribute('src','../'+path)
            expect(details.locator('img')).to_have_js_property('complete',True)
            assert details.locator('img').evaluate('(img)=>img.naturalWidth>0')
        table=panel.locator('table').last
        assert table.locator('tbody tr').count()==3
        assert table.locator('tbody tr td:last-child').all_text_contents()==['Unresolved']*3
        expect(table).to_contain_text('3.1 km · saline screen fails')
        page.set_viewport_size({'width':320,'height':850})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        comparison_href=panel.get_by_role('link',name='Six same-branch dated comparisons',exact=True).get_attribute('href')
        main_link=panel.get_by_role('link',name='Query all dated section measurements',exact=True)
        main_query=json.loads(unquote(main_link.get_attribute('href').split('?q=')[1]))
        main_link.click()
        page.wait_for_function('window.oswLastQueryResult',timeout=90000)
        main_result=page.evaluate('oswLastQueryResult')
        assert main_result==native(main_query)
        assert main_result['rows']==sorted(typed_measurements()[0],key=lambda row:row['id'])
        assert main_result['total']==60
        assert page.locator('#query-rows tr').count()==60
        expect(page.locator('#query-rows')).to_contain_text('local component span')
        expect(page.locator('#query-rows')).to_contain_text('saline screen fails')
        assert page.locator('#query-export').is_enabled()
        filtered={**main_query,'filters':main_query['filters']+[{'field':'is_primary_convention','op':'eq','value':True}]}
        page.locator('#query-advanced').evaluate('(node)=>node.open=true')
        page.locator('#query-json').fill(json.dumps(filtered));page.evaluate('oswLastQueryResult=null')
        page.locator('#query-run-json').click()
        page.wait_for_function('window.oswLastQueryResult',timeout=90000)
        assert page.evaluate('oswLastQueryResult')==native(filtered)
        assert page.evaluate('oswLastQueryResult')['total']==4
        page.locator('#query-rows button').first.click()
        detail=page.locator('#query-detail')
        expect(detail).to_be_visible()
        source_link=detail.get_by_role('link',name='Inspect exact section measurement source',exact=True)
        expect(source_link).to_be_visible()
        request=json.loads(unquote(source_link.get_attribute('href').split('source-q=')[1]))
        first=page.evaluate('oswLastQueryResult')['rows'][0]
        assert request['document']==first['source_file'] and request['pointer']==first['source_pointer']
        assert detail.get_by_role('link',name='Open atlas card',exact=True).count()==1
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.goto('http://127.0.0.1:8788/almanac/'+comparison_href)
        page.wait_for_function('window.oswSourceQueryResult',timeout=90000)
        result=page.evaluate('oswSourceQueryResult')
        assert result['total']==6
        assert all(row['record']['summer_minus_winter_dated_component_span_km'] is None for row in result['rows'])
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        browser.close()
        assert not errors and not originals,(errors,originals)
    receipt={'status':'PASS','exact_native_actual_wasm_summer_cases':30,'unresolved_dated_comparisons':6,
        'exact_station_pairs':12,'preserved_summer_unresolved_cases':26,'keyboard_two_analysis_views':True,
        'exact_native_actual_wasm_typed_records':60,'typed_primary_filter_matches':4,
        'typed_record_source_and_atlas_links':True,
        'source_export':True,'mobile_320px':True,'page_errors':0,'automatic_original_requests':0,'browser_version':version}
    (out/'result.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    print(json.dumps(receipt),flush=True)


if __name__=='__main__':main()
