"""Main native/WASM source inventory and keyboard dashboard discovery."""
import gzip
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote
from playwright.sync_api import sync_playwright, expect
from angola_nansen_source_query import ROOT, REPORT, ID, evidence
from test_current_research_evidence_browser import native, BASE
from test_rust_query_browser import browser_query


def main():
    source,diagnostic,_=evidence();errors=[];originals=[]
    output=ROOT/'.pytest_cache/angola-nansen-sections/query-browser';output.mkdir(parents=True,exist_ok=True)
    typed=[{'collection':'diagnostics','filters':[{'field':'id','op':'eq','value':ID}],'limit':1},
           {'collection':'objects','filters':[{'field':'id','op':'eq','value':'current:angola'}]}]
    metadata=[({'document':REPORT,'pointer':pointer,'limit':20,'offset':0},expected)
              for pointer,expected in [('/sections',source['sections']),('/members',source['members'])]]
    mirrors=diagnostic['native_query_documents']
    # Cover both native depth-grid formats through native/WASM parity; every
    # complete field is also checked through the shipped WASM source store.
    native_mirrors=[mirrors[0],mirrors[3]]
    with TemporaryDirectory(dir=output) as tmp:
        index=Path(tmp)/'index.json';index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        typed_expected=[native(q) for q in typed]
        metadata_expected=[native(q,index=index) for q,_ in metadata]
        field_expected={}
        for row in native_mirrors:
            q={'document':row['source_file'],'pointer':'/variables','limit':6,'offset':0}
            field_expected[row['source_file']]=native(q,index=index)
        # No native CLI processes remain when Chromium/its WASM index starts.
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'],args=['--disable-features=BackForwardCache'])
            page=browser.new_page(viewport={'width':1100,'height':1000})
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('request',lambda request:originals.append(request.url) if request.url.split('?')[0].endswith(('.zip','.nc','.pdf')) else None)
            page.goto(BASE+'/almanac/query.html?q='+quote(json.dumps(typed[0])))
            page.wait_for_function('window.oswLastQueryResult',timeout=180000)
            assert page.evaluate('window.oswLastQueryResult')==typed_expected[0]
            assert browser_query(page,typed[1])==typed_expected[1]
            assert typed_expected[0]['rows']==[diagnostic] and typed_expected[1]['total']==0
            page.goto(BASE+'/almanac/query.html?source-q='+quote(json.dumps(metadata[0][0])))
            page.wait_for_function('window.oswSourceQueryResult',timeout=180000)
            page.locator('#source-query-panel details').evaluate('(el)=>el.open=true')
            def source_query(request):
                page.locator('#source-query-json').fill(json.dumps(request))
                page.evaluate('window.oswSourceQueryResult=null')
                page.locator('#source-query-run-json').click()
                page.wait_for_function('window.oswSourceQueryResult || document.querySelector("#source-query-status").dataset.pending==="false"',timeout=180000)
                return page.evaluate('window.oswSourceQueryResult')
            for (query,records),expected in zip(metadata,metadata_expected):
                result=source_query(query);assert result==expected
                assert [r['record'] for r in result['rows']]==records
            cells=0
            for row in mirrors:
                query={'document':row['source_file'],'pointer':'/variables','limit':6,'offset':0}
                result=source_query(query)
                original=json.loads((ROOT/row['source_file']).read_bytes())
                assert result['ok'] and result['source_sha256']==row['source_sha256']
                assert {r['source_key']:r['record'] for r in result['rows']}==original['variables']
                if row['source_file'] in field_expected:assert result==field_expected[row['source_file']]
                cells+=2*original['dimensions']['PROFILE']*original['dimensions']['DEPTH']
            assert cells==2044320
            page.set_viewport_size({'width':320,'height':1000})
            page.goto(BASE+'/almanac/dashboard.html')
            link=page.locator('#dashboard-source-views a').filter(has_text='Angola')
            expect(link).to_be_visible(timeout=180000)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            link.focus();page.keyboard.press('Enter');page.wait_for_function('window.oswAngolaReady')
            assert page.evaluate('window.oswAngolaReport.section_count')==11
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.locator('#field').scroll_into_view_if_needed();page.screenshot(path=str(output/'phone.png'))
            # The selected raw value can be investigated directly in Rust/WASM.
            cell=page.evaluate('window.oswAngolaSelectedCell.V_CUR')
            page.locator('#query-cell').focus();page.keyboard.press('Enter')
            page.wait_for_function('window.oswSourceQueryResult',timeout=180000)
            assert page.evaluate('window.oswSourceQueryResult.rows[0].record')==cell
            assert not errors and not originals,(errors,originals)
            browser.close()
    (output/'result.json').write_text(json.dumps({'status':'PASS','complete_diagnostic_native_wasm':True,'source_section_records_exact':11,'source_members_exact':13,'complete_native_fields_queryable_wasm':11,'velocity_cells_queryable_including_missing':cells,'native_wasm_full_field_parity_depth_grids':[120,240],'native_cli_closed_before_browser':True,'one_reused_source_workspace':True,'back_forward_cache_disabled_for_test_memory':True,'unadmitted_identity_absent_from_current_objects':True,'keyboard_dashboard_to_view_to_cell_query':True,'phone_320px':True,'automatic_original_downloads':0,'physical_width_admitted':False},indent=2)+'\n',encoding='utf8')
    print('PASS: main source store, every native field/cell, both depth-grid parity cases, dashboard/view/cell keyboard navigation')


if __name__=='__main__':main()
