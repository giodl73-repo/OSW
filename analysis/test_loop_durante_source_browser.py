"""Checked Loop source panels, complete source values and semantic guards."""
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
            image=panel.locator('img');image.scroll_into_view_if_needed();p.wait_for_function('(selector)=>{const n=document.querySelector(selector);return n.complete&&n.naturalWidth>0}',arg='.current-research-evidence[data-current="loop"] img',timeout=90000)
            expect(image).to_have_attribute('src','../figures/loop-durante-2026-source-view.svg')
            expect(panel).to_contain_text('zero-based OSW position3462 (MATLAB index3463)');expect(panel).to_contain_text('22.69 N');expect(panel).to_contain_text('23.14 N')
            assert panel.locator('table').count()==2
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
        packet=json.loads((ROOT/'almanac/query-data.json').read_bytes())
        for mode in ['missing_clock','invented_axis','scope','source','figure','area_width']:
            bad=copy.deepcopy(packet);row=next(r for r in bad['collections']['diagnostics'] if r['id']==ID)
            if mode=='missing_clock':row['document']['times']['tisp']['nonfinite']=0
            elif mode=='invented_axis':row['document']['source_composite_axes']['CurAxisPositive']['latitude_bounds'][1]=29
            elif mode=='scope':row['research_evidence']['new_width_record_admitted']=True
            elif mode in ['source','figure']:
                path=VIEW if mode=='source' else 'figures/loop-durante-2026-source-view.svg';bad['manifest']['input_sha256'][path]='0'*64
            else:bad['collections']['widths'][0]['source_file']=VIEW
            fixture=folder/'bad-packet.json';fixture.write_bytes(json.dumps(bad).encode());del bad
            result=subprocess.run([str(CLI),str(fixture),'-'],input='{}',capture_output=True,text=True,encoding='utf8');assert result.returncode==2 and not result.stdout
            p=page();wasm_rejection(p,fixture);p.close();print('PASS native/actualWASM Loop source rejection',mode,flush=True)
        corpus=json.loads(index.read_bytes());doc=json.loads(corpus['documents'][VIEW]);doc['clocks']['tisp']['source_serial_days'][3462]=doc['clocks']['tid']['source_serial_days'][3462]
        corpus['documents'][VIEW]=json.dumps(doc);fixture=folder/'bad-index.json';fixture.write_bytes(json.dumps(corpus).encode());del corpus,doc
        result=subprocess.run([str(CLI),'--index',str(fixture),'-'],input='{}',capture_output=True,text=True,encoding='utf8');assert result.returncode==2 and not result.stdout
        p=page();wasm_rejection(p,fixture,index=True);p.close();browser.close();assert not errors and not originals,(errors,originals)
    result={'status':'PASS','views':list(urls),'complete_phase_clock_scalar_rows_exact_native_wasm':True,
            'source_times_not_filled':True,'unjoined_points_not_complete_loop_axis':True,'packet_corruptions':6,'index_corruptions':1,
            'keyboard_320px':True,'no_automatic_originals':True}
    (out/'browser-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))


if __name__=='__main__':main()
