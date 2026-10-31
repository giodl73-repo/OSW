"""Checked Loop source panels, complete source values and semantic guards."""
from query_packet import read_bundle_bytes
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote
import copy,gzip,hashlib,json,os,subprocess
from playwright.sync_api import sync_playwright,expect
from test_current_research_evidence_browser import native,CLI
from test_eac_section_core_spans_browser import wasm_rejection

ROOT=Path(__file__).resolve().parents[1];BASE='http://127.0.0.1:8788'
ID='diagnostic:current-research:loop'
QUALITY='research/source-data/loop-durante-2026-v0/quality.json'
VIEW='research/loop-durante-2026-source-view.json'
CONTOURS='research/loop-durante-2026-composite-contour-paths.json'


def main():
    out=ROOT/'.pytest_cache/loop-durante-browser';out.mkdir(parents=True,exist_ok=True)
    view=json.loads((ROOT/VIEW).read_bytes());query={'collection':'diagnostics','filters':[{'field':'id','op':'eq','value':ID}],'limit':1}
    expected=native(query)
    with TemporaryDirectory(dir=out) as temporary,sync_playwright() as pw:
        folder=Path(temporary);index=folder/'index.json';index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        browser=pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'));errors=[];originals=[]
        def page():
            p=browser.new_page(viewport={'width':1280,'height':1000});p.emulate_media(reduced_motion='reduce')
            p.on('pageerror',lambda e:errors.append(str(e)))
            p.on('request',lambda r:originals.append(r.url) if r.url.lower().split('?')[0].endswith(('.pdf','.nc','.npz','.zip','.mat')) else None)
            return p
        urls={'card':'/almanac/reference-routes.html?atlas-feature=current%3Aloop#route-atlas',
              'seasons':'/almanac/seasons.html?current=loop','query':'/almanac/query.html?q='+quote(json.dumps(query))}
        for name,url in urls.items():
            print('Checking Loop source',name,flush=True);p=page();p.goto(BASE+url)
            panel=p.locator('.current-research-evidence[data-current="loop"]');expect(panel).to_be_visible(timeout=90000)
            expect(panel).to_contain_text('4,111 / 4,111 / 11,902 entries');expect(panel).to_contain_text('Not supplied')
            details=panel.locator('details');
            if details.get_attribute('open') is None:details.locator('summary').focus();p.keyboard.press('Enter')
            image=panel.locator('img').first;image.scroll_into_view_if_needed();p.wait_for_function('(selector)=>{const n=document.querySelector(selector);return n.complete&&n.naturalWidth>0}',arg='.current-research-evidence[data-current="loop"] img',timeout=90000)
            expect(image).to_have_attribute('src','../figures/loop-durante-2026-source-view.svg')
            expect(panel).to_contain_text('zero-based OSW position3462 (MATLAB index3463)');expect(panel).to_contain_text('22.69 N');expect(panel).to_contain_text('23.14 N')
            assert panel.locator('table').count()==3
            expect(panel).to_contain_text('About 1,400 km positive / 600 km negative; unranked')
            assert panel.locator('table').last.locator('tbody tr').count()==54
            selector=panel.get_by_label('Analysis view')
            expect(selector.locator('option').first).to_have_text('Source composites and separate clocks')
            selector.select_option('1')
            contour_image=panel.locator('img[src="../figures/loop-durante-2026-composite-contours.svg"]')
            contour_image.scroll_into_view_if_needed()
            expect(contour_image).to_have_js_property('complete',True)
            assert contour_image.evaluate('(n)=>n.naturalWidth>0')
            assert panel.get_by_role('link',name='All original clocks',exact=True).count()==1
            if name=='query':assert p.evaluate('oswLastQueryResult')==expected
            p.set_viewport_size({'width':320,'height':900});p.wait_for_timeout(150)
            assert p.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            panel.scroll_into_view_if_needed();p.screenshot(path=str(out/(name+'-mobile.png')))
            p.close();print('PASS Loop source panel',name,flush=True)
        for pointer,key in [('/phases','phases'),('/clocks','clocks'),('/source_scalar_series','source_scalar_series')]:
            p=page();q={'document':VIEW,'pointer':pointer,'limit':100}
            p.goto(BASE+'/almanac/query.html?source-q='+quote(json.dumps(q)));p.wait_for_function('window.oswSourceQueryResult',timeout=90000)
            actual=p.evaluate('oswSourceQueryResult');assert actual==native(q,index=index)
            if key=='phases':assert [r['record'] for r in actual['rows']]==view[key]
            else:assert {r['source_key']:r['record'] for r in actual['rows']}==view[key]
            p.close();print('PASS complete native/actualWASM source',pointer,flush=True)
        contour_record=json.loads((ROOT/CONTOURS).read_bytes());p=page();all_cases=[]
        for offset in range(0,54,9):
            q={'document':CONTOURS,'pointer':'/cases','limit':9,'offset':offset}
            if offset==0:p.goto(BASE+'/almanac/query.html?source-q='+quote(json.dumps(q)))
            else:
                p.locator('#source-query-panel details').evaluate('(n)=>n.open=true');p.locator('#source-query-json').fill(json.dumps(q));p.evaluate('oswSourceQueryResult=null');p.locator('#source-query-run-json').click()
            p.wait_for_function('window.oswSourceQueryResult',timeout=90000)
            result=p.evaluate('oswSourceQueryResult');assert result==native(q,index=index)
            assert result['total']==54;all_cases.extend(row['record'] for row in result['rows'])
            print('PASS full composite contour case page',offset,flush=True)
        assert all_cases==contour_record['cases'];p.close()
        packet=json.loads(read_bundle_bytes(ROOT/'almanac/query-data.json'))
        for mode in ['missing_clock','invented_axis','scope','source','figure','area_width','contour_source','contour_figure','contour_width','contour_route','contour_length']:
            bad=copy.deepcopy(packet);row=next(r for r in bad['collections']['diagnostics'] if r['id']==ID)
            if mode=='missing_clock':row['document']['times']['tisp']['nonfinite']=0
            elif mode=='invented_axis':row['document']['source_composite_axes']['CurAxisPositive']['latitude_bounds'][1]=29
            elif mode=='scope':row['research_evidence']['new_width_record_admitted']=True
            elif mode in ['source','figure']:
                path=VIEW if mode=='source' else 'figures/loop-durante-2026-source-view.svg';bad['manifest']['input_sha256'][path]='0'*64
            elif mode in ['contour_source','contour_figure']:
                path=CONTOURS if mode=='contour_source' else 'figures/loop-durante-2026-composite-contours.svg';bad['manifest']['input_sha256'][path]='0'*64
            elif mode in ['contour_route','contour_length']:
                collection='reference_routes' if mode=='contour_route' else 'length_assessments';bad['collections'][collection][0]['source_file']=CONTOURS
            else:bad['collections']['widths'][0]['source_file']=CONTOURS if mode=='contour_width' else VIEW
            fixture=folder/'bad-packet.json';fixture.write_bytes(json.dumps(bad).encode());del bad
            result=subprocess.run([str(CLI),str(fixture),'-'],input='{}',capture_output=True,text=True,encoding='utf8');assert result.returncode==2 and not result.stdout
            p=page();wasm_rejection(p,fixture);p.close();print('PASS native/actualWASM Loop source rejection',mode,flush=True)
        corpus=json.loads(index.read_bytes());doc=json.loads(corpus['documents'][VIEW]);doc['clocks']['tisp']['source_serial_days'][3462]=doc['clocks']['tid']['source_serial_days'][3462]
        corpus['documents'][VIEW]=json.dumps(doc);fixture=folder/'bad-index.json';fixture.write_bytes(json.dumps(corpus).encode());del corpus,doc
        result=subprocess.run([str(CLI),'--index',str(fixture),'-'],input='{}',capture_output=True,text=True,encoding='utf8');assert result.returncode==2 and not result.stdout
        p=page();wasm_rejection(p,fixture,index=True);p.close()
        corpus=json.loads(index.read_bytes());doc=json.loads(corpus['documents'][CONTOURS]);doc['cases'][0]['supported_contour_path_length_km']=1
        corpus['documents'][CONTOURS]=json.dumps(doc);fixture=folder/'bad-contour-index.json';fixture.write_bytes(json.dumps(corpus).encode());del corpus,doc
        result=subprocess.run([str(CLI),'--index',str(fixture),'-'],input='{}',capture_output=True,text=True,encoding='utf8');assert result.returncode==2 and not result.stdout
        p=page();wasm_rejection(p,fixture,index=True);p.close();browser.close();assert not errors and not originals,(errors,originals)
    result={'status':'PASS','views':list(urls),'complete_phase_clock_scalar_rows_exact_native_wasm':True,
            'source_times_not_filled':True,'unjoined_points_not_complete_loop_axis':True,'all54contour_cases_exact_native_wasm':True,'packet_corruptions':11,'index_corruptions':2,
            'keyboard_320px':True,'no_automatic_originals':True}
    (out/'browser-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))


if __name__=='__main__':main()
