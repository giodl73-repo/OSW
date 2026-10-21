"""Shipped WASM, exact model contexts, accessible current views and rejection."""
from query_packet import read_bundle_bytes
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote,parse_qs,urlparse
import copy,gzip,hashlib,json,os,subprocess

from playwright.sync_api import sync_playwright,expect
from test_current_research_evidence_browser import native,CLI
from test_eac_section_core_spans_browser import wasm_rejection
from south_australian_flow_context import ID,FILE

ROOT=Path(__file__).resolve().parents[1];BASE='http://127.0.0.1:8788'
REPORT='research/south-australian-hycom-2d-flow-context.json'


def main():
    out=ROOT/'.pytest_cache/south-australian-context-browser';out.mkdir(parents=True,exist_ok=True)
    raw=json.loads((ROOT/REPORT).read_bytes());summary=json.loads((ROOT/FILE).read_bytes())
    query={'collection':'diagnostics','filters':[{'field':'id','op':'eq','value':ID}],'limit':1}
    expected=native(query)
    with TemporaryDirectory(dir=out) as temporary,sync_playwright() as pw:
        folder=Path(temporary);index=folder/'index.json';index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        browser=pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'));errors=[];originals=[]
        def page():
            p=browser.new_page(viewport={'width':1280,'height':1000});p.emulate_media(reduced_motion='reduce')
            p.on('pageerror',lambda e:errors.append(str(e)))
            p.on('request',lambda r:originals.append(r.url) if r.url.lower().split('?')[0].endswith(('.pdf','.nc','.npz','.zip','.ascii')) else None)
            return p
        urls={'card':'/almanac/reference-routes.html?atlas-feature=current%3Asouth-australian#route-atlas',
              'seasons':'/almanac/seasons.html?current=south-australian',
              'diagnostic':'/almanac/query.html?q='+quote(json.dumps(query))}
        for view,url in urls.items():
            print('Checking',view,flush=True)
            p=page();p.goto(BASE+url);panel=p.locator('.south-australian-context');expect(panel).to_be_visible(timeout=90000)
            details=panel.locator('details');
            if details.get_attribute('open') is None:details.locator('summary').focus();p.keyboard.press('Enter')
            month=panel.get_by_label('Recorded month',exact=True);threshold=panel.get_by_label('Peak threshold',exact=True)
            expect(panel.locator('[data-sac-play]')).to_be_disabled()
            for original in raw['months']:
                month.select_option(str(original['month']))
                for case in original['threshold_cases']:
                    threshold.select_option(str(case['fraction']))
                    actual=panel.locator('[data-sac-component-cell]').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.sacComponentCell)')
                    assert actual==[str(y)+','+str(x) for y,x in case['cells']]
                    expect(panel.locator('[data-sac-reading]')).to_contain_text(str(case['cell_count'])+' seed-connected cells')
                    assert panel.locator('[data-sac-map]').get_attribute('aria-label').startswith('2012-'+str(original['month']).zfill(2))
                source=parse_qs(urlparse(panel.locator('[data-sac-exact]').get_attribute('href')).query)
                assert json.loads(source['source-q'][0])['pointer']=='/months/'+str(original['month']-1)
            month.focus();p.keyboard.press('Home');expect(month).to_have_value('1');p.keyboard.press('End');expect(month).to_have_value('12')
            expect(panel.locator('[data-sac-reading]')).to_contain_text('Physical width remains unresolved')
            if view=='diagnostic':assert p.evaluate('oswLastQueryResult')==expected
            if view=='diagnostic':
                p.emulate_media(reduced_motion='no-preference');play=panel.locator('[data-sac-play]');expect(play).to_be_enabled();play.click()
                expect(month).to_have_value('1',timeout=5000);play.click();expect(play).to_have_attribute('aria-pressed','false')
                play.click();details.locator('summary').click();expect(play).to_have_attribute('aria-pressed','false');details.locator('summary').click()
                p.emulate_media(reduced_motion='reduce');expect(play).to_be_disabled();month.select_option('12')
            p.set_viewport_size({'width':320,'height':900});p.wait_for_timeout(150)
            assert p.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            panel.scroll_into_view_if_needed();p.screenshot(path=str(out/(view+'-mobile.png')))
            panel.locator('[data-sac-map]').screenshot(path=str(out/(view+'-map-mobile.png')))
            if view=='diagnostic':
                share=panel.locator('[data-sac-share]').get_attribute('href');p.goto(share)
                panel=p.locator('.south-australian-context');expect(panel).to_be_visible(timeout=90000)
                expect(panel.get_by_label('Recorded month',exact=True)).to_have_value('12')
                expect(panel.get_by_label('Peak threshold',exact=True)).to_have_value('0.6')
            p.close();print('PASS all36cases,keyboard,320px',view,flush=True)
        p=page();source={'document':REPORT,'pointer':'/months','limit':100}
        p.goto(BASE+'/almanac/query.html?source-q='+quote(json.dumps(source)))
        p.wait_for_function('window.oswSourceQueryResult',timeout=90000)
        actual=p.evaluate('oswSourceQueryResult');assert actual==native(source,index=index)
        assert [row['record'] for row in actual['rows']]==raw['months'];p.close()
        packet=json.loads(read_bundle_bytes(ROOT/'almanac/query-data.json'))
        for mode in ['source','figure','membership','admission','join','resealed','inventory_width']:
            bad=copy.deepcopy(packet);row=next(d for d in bad['collections']['diagnostics'] if d['id']==ID)
            if mode in ['source','figure']:
                path=REPORT if mode=='source' else summary['context_figure'];bad['manifest']['input_sha256'][path]='0'*64
            elif mode=='membership':row['document']['months'][0]['threshold_cases'][1]['cells']=[]
            elif mode=='admission':row['document']['width_measurement_admitted']=True
            elif mode=='join':next(o for o in bad['collections']['objects'] if o['id']=='current:south-australian')['diagnostic_ids'].remove(ID)
            elif mode=='resealed':
                row['document']['source_dates']=1;text=json.dumps(row['document']);pin=hashlib.sha256(text.encode()).hexdigest()
                row.update(source_json=text,source_file_sha256=pin);bad['manifest']['input_sha256'][FILE]=pin
            else:bad['collections']['widths'][0]['source_file']=REPORT
            fixture=folder/'bad-packet.json';fixture.write_bytes(json.dumps(bad).encode());del bad
            result=subprocess.run([str(CLI),str(fixture),'-'],input='{}',capture_output=True,text=True,encoding='utf8')
            assert result.returncode==2 and not result.stdout
            p=page();wasm_rejection(p,fixture);p.close();print('PASS native/actualWASM rejection',mode,flush=True)
        corpus=json.loads(index.read_bytes());doc=json.loads(corpus['documents'][REPORT]);doc['months'][0]['threshold_cases'][1]['cells']=[]
        corpus['documents'][REPORT]=json.dumps(doc);fixture=folder/'bad-index.json';fixture.write_bytes(json.dumps(corpus).encode());del corpus,doc
        result=subprocess.run([str(CLI),'--index',str(fixture),'-'],input='{}',capture_output=True,text=True,encoding='utf8')
        assert result.returncode==2 and not result.stdout
        p=page();wasm_rejection(p,fixture,index=True);p.close();browser.close()
        assert not errors and not originals,(errors,originals)
    result={'status':'PASS','views':list(urls),'all36cases_in_each_view':True,'all12source_rows_exact_native_wasm':True,
            'packet_corruptions':7,'index_corruptions':1,'keyboard_320px_share':True,'no_automatic_originals':True}
    (out/'browser-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))


if __name__=='__main__':main()
