"""Actual Rust/WASM EAC span corpus, failure states and accessible atlas views."""
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote
import copy,gzip,hashlib,json,os,subprocess
from playwright.sync_api import sync_playwright,expect
from test_current_research_evidence_browser import native,CLI

ROOT=Path(__file__).resolve().parents[1];BASE='http://127.0.0.1:8788'
REPORT='research/eac-csiro-100m-section-core-spans.json'
SUMMARY='research/eac-csiro-100m-section-core-spans-summary.json'
FIGURE='figures/eac-csiro-100m-section-core-spans.svg'
ID='diagnostic:eac-csiro100m-section-core-spans'


def wasm_rejection(p,fixture,index=False):
    p.route('**/eac-core-guard.html',lambda r:r.fulfill(body='<title>EAC core guard</title>',content_type='text/html'))
    p.goto(BASE+'/eac-core-guard.html')
    result=p.evaluate('''async({url,index})=>{const {instance}=await WebAssembly.instantiate(await(await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports,r=await fetch(url);if(!r.ok)throw Error('Fixture unavailable');const b=new Uint8Array(await r.arrayBuffer()),ptr=e.osw_alloc(b.length);try{new Uint8Array(e.memory.buffer,ptr,b.length).set(b);(index?e.osw_index_load:e.osw_load)(ptr,b.length);return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));}finally{e.osw_dealloc(ptr,b.length);}}''',{'url':BASE+'/'+fixture.relative_to(ROOT).as_posix(),'index':index})
    assert result['ok'] is False


def main():
    out=ROOT/'.pytest_cache/eac-core-browser';out.mkdir(exist_ok=True,parents=True)
    raw=json.loads((ROOT/REPORT).read_bytes());summary=json.loads((ROOT/SUMMARY).read_bytes())
    diagnostic={'collection':'diagnostics','filters':[{'field':'id','op':'eq','value':ID}],'limit':100}
    failed=next(r for r in raw['profiles'] if r['scenarios']['central']['cases'][1]['status']=='unresolved_paired_boundaries')
    with TemporaryDirectory(dir=out) as temporary,sync_playwright() as pw:
        folder=Path(temporary);index=folder/'index.json';index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        browser=pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'));errors=[];originals=[]
        def page():
            p=browser.new_page(viewport={'width':1280,'height':1000});p.emulate_media(reduced_motion='reduce')
            p.on('pageerror',lambda e:errors.append(str(e)))
            p.on('request',lambda r:originals.append(r.url) if r.url.lower().split('?')[0].endswith(('.pdf','.nc','.npz','.zip')) else None)
            return p
        urls={'card':'/almanac/reference-routes.html?atlas-feature=current%3Aeast-australian#route-atlas',
              'seasons':'/almanac/seasons.html?current=east-australian','diagnostic':'/almanac/query.html?q='+quote(json.dumps(diagnostic))}
        for view,url in urls.items():
            p=page();p.goto(BASE+url);source=p.locator('.eac-source-fields');expect(source).to_be_visible(timeout=90000)
            details=source.locator('details').first
            if details.get_attribute('open') is None:details.locator(':scope > summary').focus();p.keyboard.press('Enter')
            core=source.locator('.eac-section-core-spans')
            try:expect(core).to_have_attribute('data-eac-core-index','0',timeout=90000)
            except Exception:
                print(json.dumps({'view':view,'errors':errors,'source_status':source.locator('[data-eac-source-status]').inner_text(),'core_text':core.inner_text()}),flush=True)
                p.screenshot(path=str(out/'initial-failure.png'));raise
            assert p.evaluate('oswEacCoreSelection.profile')==raw['profiles'][0]
            assert p.evaluate('oswEacCoreSelection.source_sha256')==hashlib.sha256((ROOT/REPORT).read_bytes()).hexdigest()
            assert source.locator('[data-eac-position]').count()==124 and source.locator('[data-eac-core-crossing]').count()==2
            assert source.locator('[data-eac-field]').count()==4
            scenario=core.get_by_label('Component sensitivity',exact=True);fraction=core.get_by_label('Peak fraction',exact=True)
            assert scenario.locator('option').count()==3 and fraction.locator('option').count()==3
            for name in summary['scenario_names']:
                scenario.select_option(name)
                for f in summary['fractions']:
                    fraction.select_option(str(f));actual=p.evaluate('oswEacCoreSelection.case')
                    assert actual==next(c for c in raw['profiles'][0]['scenarios'][name]['cases'] if c['fraction']==f)
                    expect(core.locator('[data-eac-core-support]')).to_contain_text('30 attempted dates')
            scenario.select_option('central');fraction.select_option('0.5')
            expect(core.locator('[aria-live]')).to_contain_text('Resolved section span: 55 km')
            expect(core.locator('[aria-live]')).to_contain_text('not measurement error')
            month=source.get_by_label('Recorded year and month');day=source.get_by_label('Source date (UTC)')
            month.select_option('2014-05');expect(core).to_have_attribute('data-eac-core-index','760',timeout=90000)
            expect(core.locator('[aria-live]')).to_contain_text('no eligible paired component data')
            assert core.locator('svg polyline').count()==0 and source.locator('[data-eac-core-crossing]').count()==0
            assert all(c['section_span_km'] is None for s in p.evaluate('oswEacCoreSelection.profile.scenarios').values() for c in s['cases'])
            month.select_option(f"{failed['year']}-{failed['month']:02}");expect(core).to_have_attribute('data-eac-core-index',str(next(m for m in summary['months'] if (m['year'],m['month'])==(failed['year'],failed['month']))['source_time_indices'][0]),timeout=90000)
            day.select_option(str(failed['source_time_index']));expect(core).to_have_attribute('data-eac-core-index',str(failed['source_time_index']))
            expect(core.locator('[aria-live]')).to_contain_text('source section ends before a crossing')
            assert p.evaluate('oswEacCoreSelection.case.section_span_km') is None
            assert source.locator('[data-eac-core-crossing]').count()==1
            month.focus();p.keyboard.press('End');expect(month).to_have_value('2022-07')
            expect(core).to_have_attribute('data-eac-core-index','3743',timeout=90000);day.focus();p.keyboard.press('End');expect(core).to_have_attribute('data-eac-core-index','3769')
            expect(core.locator('[aria-live]')).to_contain_text('positive peak is below 0.3 m/s')
            assert p.evaluate('oswEacCoreSelection.profile')==raw['profiles'][3769]
            assert source.locator('[data-eac-core-crossing]').count()==0
            exact=core.get_by_role('link',name='Inspect this exact section-core outcome',exact=True);exact.focus();expect(exact).to_be_focused()
            if view=='diagnostic':
                assert p.evaluate('oswLastQueryResult')==native(diagnostic)
                overview=core.get_by_text('All-date outcomes, sensitivity and fixed source examples',exact=True).locator('..');overview.locator(':scope > summary').focus();p.keyboard.press('Enter')
                img=overview.locator('img');img.scroll_into_view_if_needed();expect(img).to_have_js_property('complete',True);expect(img).to_have_attribute('src','../'+FIGURE);assert img.evaluate('(n)=>n.naturalWidth>0')
                core.screenshot(path=str(out/'core-desktop.png'))
            p.set_viewport_size({'width':320,'height':900});assert p.evaluate('document.documentElement.scrollWidth<=innerWidth')
            scroll=core.get_by_role('region',name='Section-core component chart; scroll horizontally');scroll.focus();before=scroll.evaluate('(n)=>n.scrollLeft');p.keyboard.press('ArrowRight');p.wait_for_timeout(300);assert scroll.evaluate('(n)=>n.scrollLeft')>before
            if view=='card':core.screenshot(path=str(out/'core-mobile.png'))
            p.close();print('PASS',view,'all9cases / missing / domain / weak / map / keyboard320px',flush=True)
        p=page();all_rows=[]
        for offset in range(0,3770,500):
            query={'document':REPORT,'pointer':'/profiles','limit':500,'offset':offset}
            if offset==0:p.goto(BASE+'/almanac/query.html?source-q='+quote(json.dumps(query)))
            else:
                p.locator('#source-query-panel details').evaluate('(n)=>n.open=true');p.locator('#source-query-json').fill(json.dumps(query));p.evaluate('oswSourceQueryResult=null');p.locator('#source-query-run-json').click()
            p.wait_for_function('window.oswSourceQueryResult',timeout=90000);value=p.evaluate('oswSourceQueryResult');assert value==native(query,index=index)
            assert value['total']==3770;all_rows.extend(row['record'] for row in value['rows']);print('PASS exact core source page',offset,flush=True)
        assert all_rows==raw['profiles'];p.close()
        packet=json.loads((ROOT/'almanac/query-data.json').read_bytes())
        for mode in ['raw_hash','summary_hash','protocol_hash','figure_hash','readback_code_hash','readback_protocol_hash','invented_width','erased_failures','coherent_rebind','inventory_width']:
            bad=copy.deepcopy(packet);d=next(d for d in bad['collections']['diagnostics'] if d['id']==ID)
            if mode.endswith('_hash'):
                path={'raw_hash':REPORT,'summary_hash':SUMMARY,'protocol_hash':'plans/eac-csiro-100m-section-core-span-protocol-v1.md','figure_hash':FIGURE,
                    'readback_code_hash':'analysis/eac_core_readback.py','readback_protocol_hash':'plans/eac-section-core-calculation-readback-v1.md'}[mode];bad['manifest']['input_sha256'][path]='0'*64
            elif mode=='invented_width':d['document']['physical_width_admitted']=True
            elif mode=='erased_failures':d['document']['overall_outcomes'][1]['attempted_dates']=2883
            elif mode=='coherent_rebind':
                d['document']['counts']['attempts']=1;text=json.dumps(d['document']);pin=hashlib.sha256(text.encode()).hexdigest();d.update(source_json=text,source_file_sha256=pin);bad['manifest']['input_sha256'][SUMMARY]=pin
            else:bad['collections']['widths'][0]['source_file']=REPORT
            fixture=folder/'bad-packet.json';fixture.write_bytes(json.dumps(bad).encode());del bad
            result=subprocess.run([str(CLI),str(fixture),'-'],input='{}',capture_output=True,text=True,encoding='utf8');assert result.returncode==2 and not result.stdout
            p=page();wasm_rejection(p,fixture);p.close();print('PASS native/actual-WASM core rejection',mode,flush=True)
        corpus=json.loads(index.read_bytes())
        for mode in ['changed_span','invented_missing_day_span']:
            bad=copy.deepcopy(corpus);doc=json.loads(bad['documents'][REPORT]);c=doc['profiles'][0 if mode=='changed_span' else 600]['scenarios']['central']['cases'][1];c['section_span_km']=999
            bad['documents'][REPORT]=json.dumps(doc);fixture=folder/'bad-index.json';fixture.write_bytes(json.dumps(bad).encode());del bad,doc
            result=subprocess.run([str(CLI),'--index',str(fixture),'-'],input='{}',capture_output=True,text=True,encoding='utf8');assert result.returncode==2 and not result.stdout
            p=page();wasm_rejection(p,fixture,index=True);p.close();print('PASS native/actual-WASM core index rejection',mode,flush=True)
        browser.close();assert not errors and not originals,(errors,originals)
    result={'status':'PASS','views':list(urls),'dates':3770,'attempts':33930,'all_source_rows_exact_native_wasm':True,
            'source_pages':8,'packet_corruptions':10,'index_corruptions':2,'keyboard_320px':True,
            'all9sensitivity_cases':True,'missing_domain_weak_cases_retained':True,'section_intersections_not_current_edges':True,
            'no_automatic_originals':True}
    (out/'browser-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))


if __name__=='__main__':main()
