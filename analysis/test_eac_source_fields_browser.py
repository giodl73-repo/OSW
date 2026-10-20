"""Real source-index/Rust/WASM daily EAC fields, gaps, maps and access checks."""
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote,parse_qs,urlsplit
import copy,gzip,hashlib,json,os,subprocess
from playwright.sync_api import sync_playwright,expect
from test_current_research_evidence_browser import native,CLI

ROOT=Path(__file__).resolve().parents[1]
BASE='http://127.0.0.1:8788'
REPORT='research/eac-csiro-v23-100m-source-quality.json'
RAW='research/eac-csiro-v23-100m-source-profiles.json'
FIGURE='figures/eac-csiro-v23-100m-source-fields.svg'
ID='diagnostic:eac-csiro100m-source-fields'


def main():
    out=ROOT/'.pytest_cache/eac-source-browser';out.mkdir(parents=True,exist_ok=True)
    quality=json.loads((ROOT/REPORT).read_bytes());source=json.loads((ROOT/RAW).read_bytes())
    query={'collection':'diagnostics','filters':[{'field':'id','op':'eq','value':ID}],'limit':100}
    with TemporaryDirectory(dir=out) as temporary,sync_playwright() as pw:
        folder=Path(temporary);index=folder/'index.json';index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        browser=pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'));errors=[];originals=[]
        def page():
            p=browser.new_page(viewport={'width':1280,'height':1000});p.emulate_media(reduced_motion='reduce')
            p.on('pageerror',lambda e:errors.append(str(e)))
            p.on('request',lambda r:originals.append(r.url) if r.url.lower().split('?')[0].endswith(('.pdf','.nc','.npz','.zip')) else None)
            return p
        urls={'card':'/almanac/reference-routes.html?atlas-feature=current%3Aeast-australian#route-atlas',
              'seasons':'/almanac/seasons.html?current=east-australian','diagnostic':'/almanac/query.html?q='+quote(json.dumps(query))}
        for view,url in urls.items():
            p=page();p.goto(BASE+url);panel=p.locator('.eac-source-fields');expect(panel).to_be_visible(timeout=90000)
            details=panel.locator('details').first
            if details.get_attribute('open') is None:details.locator(':scope > summary').focus();p.keyboard.press('Enter')
            expect(panel).to_have_attribute('data-eac-source-index','0',timeout=90000)
            assert p.evaluate('oswEacSourceSelection.profile')==source['profiles'][0]
            assert p.evaluate('oswEacSourceSelection.source_sha256')==hashlib.sha256((ROOT/RAW).read_bytes()).hexdigest()
            assert panel.locator('[data-eac-field]').count()==4
            assert panel.locator('[data-eac-position]').count()==124
            expect(panel.locator('svg image').first).to_have_attribute('href','../figures/ocean-motion-dashboard-ground.svg')
            for i in [0,123]:
                request={'op':'project','coordinates':quality['fixed_source_geometry']['longitude_latitude_points'][i]}
                result=subprocess.run([str(CLI),'--cartography'],input=json.dumps(request),capture_output=True,text=True,encoding='utf8',check=True)
                expected=json.loads(result.stdout)['point'];point=panel.locator(f'[data-eac-position="{i}"]')
                assert abs(float(point.get_attribute('cx'))-expected[0])<1e-9 and abs(float(point.get_attribute('cy'))-expected[1])<1e-9
            month=panel.get_by_label('Recorded year and month');day=panel.get_by_label('Source date (UTC)');cell=panel.get_by_label('Source position',exact=True)
            counts=[control.locator('option').count() for control in [month,day,cell]]
            assert counts==[124,30,124],(view,counts,cell.evaluate('(n)=>n.outerHTML').replace('<option','\n<option'))
            cell.select_option('11');expect(panel.locator('[aria-live="polite"]')).to_contain_text('source bottom 100 m')
            expect(panel.locator('[aria-live="polite"]')).to_contain_text('Eastward velocity: 0 m/s; supplied uncertainty 0 m/s')
            expect(panel.get_by_role('button',name='Play days in this month',exact=True)).to_be_disabled()
            month.select_option('2014-05');missing=next(m for m in quality['monthly_support'] if (m['year'],m['month'])==(2014,5))
            expect(panel).to_have_attribute('data-eac-source-index',str(missing['source_time_indices'][0]),timeout=90000)
            expect(panel.locator('[data-eac-source-status]')).to_contain_text('No velocity data on this date; current absence is not established.')
            assert panel.locator('[data-eac-field] polyline').count()==0 and panel.locator('[data-eac-field] polygon').count()==0
            assert all(v is None for values in p.evaluate('oswEacSourceSelection.profile.fields').values() for v in values)
            month.focus();p.keyboard.press('End');expect(month).to_have_value('2022-07')
            last=quality['monthly_support'][-1];expect(panel).to_have_attribute('data-eac-source-index',str(last['source_time_indices'][0]),timeout=90000)
            assert day.locator('option').count()==27;day.focus();p.keyboard.press('End');expect(panel).to_have_attribute('data-eac-source-index','3769')
            assert p.evaluate('oswEacSourceSelection.profile')==source['profiles'][3769]
            expect(panel.locator('[data-eac-source-status]')).to_contain_text('2022-07-27T12:00:00Z')
            exact=panel.get_by_role('link',name='Inspect this exact daily source record',exact=True);exact.focus();expect(exact).to_be_focused()
            request=json.loads(parse_qs(urlsplit(exact.get_attribute('href')).query)['source-q'][0]);assert request['filters'][0]['value']==3769
            if view=='diagnostic':
                assert p.evaluate('oswLastQueryResult')==native(query)
                p.emulate_media(reduced_motion='no-preference');play=panel.get_by_role('button',name='Play days in this month',exact=True);expect(play).to_be_enabled()
                day.select_option(str(last['source_time_indices'][-2]));play.click();p.wait_for_timeout(1200);expect(panel).to_have_attribute('data-eac-source-index','3769')
                p.wait_for_timeout(1200);expect(panel.get_by_role('button',name='Play days in this month',exact=True)).to_be_visible();expect(panel).to_have_attribute('data-eac-source-index','3769')
                p.emulate_media(reduced_motion='reduce')
                overview=panel.locator('details').nth(1);overview.locator(':scope > summary').focus();p.keyboard.press('Enter')
                image=overview.locator('img');image.scroll_into_view_if_needed();expect(image).to_have_attribute('src','../'+FIGURE);expect(image).to_have_js_property('complete',True);assert image.evaluate('(n)=>n.naturalWidth>0')
                panel.locator('[data-eac-field]').nth(1).screenshot(path=str(out/'northward-desktop.png'))
            p.set_viewport_size({'width':320,'height':900});assert p.evaluate('document.documentElement.scrollWidth<=innerWidth')
            scroll=panel.locator('[data-eac-field] [role="region"]').first;scroll.focus();before=scroll.evaluate('(n)=>n.scrollLeft');p.keyboard.press('ArrowRight');p.wait_for_timeout(300);assert scroll.evaluate('(n)=>n.scrollLeft')>before
            if view=='card':panel.locator('svg').first.screenshot(path=str(out/'map-mobile.png'))
            p.close();print('PASS',view,'124months/dates/source gaps/uncertainty/bottom zeros/Rust OSW map/keyboard320px',flush=True)
        p=page();all_rows=[]
        requests=[{'document':RAW,'pointer':'/profiles','limit':500,'offset':offset} for offset in range(0,3770,500)]
        requests += [{'document':REPORT,'pointer':'','limit':100},
                     {'document':'research/eac-csiro-v23-100m-source-fields-figure.json','pointer':'','limit':100}]
        for i,request in enumerate(requests):
            if i==0:p.goto(BASE+'/almanac/query.html?source-q='+quote(json.dumps(request)))
            else:
                p.locator('#source-query-panel details').evaluate('(n)=>n.open=true');p.locator('#source-query-json').fill(json.dumps(request));p.evaluate('oswSourceQueryResult=null');p.locator('#source-query-run-json').click()
            p.wait_for_function('window.oswSourceQueryResult',timeout=90000);value=p.evaluate('oswSourceQueryResult');assert value==native(request,index=index)
            if request['document']==RAW:
                assert value['total']==3770;all_rows.extend(row['record'] for row in value['rows'])
            print('PASS exact source query',request['document'],request.get('offset'),flush=True)
        assert all_rows==source['profiles'];p.close()
        packet=json.loads((ROOT/'almanac/query-data.json').read_bytes())
        for mode in ['quality_hash','raw_source_hash','figure_hash','operator_hash','false_confidence','erased_bottom_values','coherent_rebind','inventory_width']:
            bad=copy.deepcopy(packet);diagnostic=next(d for d in bad['collections']['diagnostics'] if d['id']==ID)
            if mode.endswith('_hash'):
                path={'quality_hash':REPORT,'raw_source_hash':RAW,'figure_hash':FIGURE,'operator_hash':'plans/eac-csiro-v23-100m-source-selection-protocol-v1.md'}[mode]
                bad['manifest']['input_sha256'][path]='0'*64
            elif mode=='false_confidence':diagnostic['document']['method_scope']['provider_uncertainty_names_are_a_universal_confidence_convention']=True
            elif mode=='erased_bottom_values':diagnostic['document']['finite_paired_velocity_cells_at_or_below_source_bottom']=0
            elif mode=='coherent_rebind':
                diagnostic['document']['documentary_disagreements']=[];raw=json.dumps(diagnostic['document']);pin=hashlib.sha256(raw.encode()).hexdigest();diagnostic.update(source_json=raw,source_file_sha256=pin);bad['manifest']['input_sha256'][REPORT]=pin
            else:bad['collections']['widths'][0]['source_file']=RAW
            fixture=folder/'bad-packet.json';fixture.write_bytes(json.dumps(bad).encode());del bad
            result=subprocess.run([str(CLI),str(fixture),'-'],input='{}',capture_output=True,text=True,encoding='utf8');assert result.returncode==2 and not result.stdout
            p=page();p.route('**/eac-source-guard.html',lambda r:r.fulfill(body='<title>EAC source guard</title>',content_type='text/html'));p.goto(BASE+'/eac-source-guard.html')
            actual=p.evaluate('''async url=>{const {instance}=await WebAssembly.instantiate(await(await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports,r=await fetch(url);if(!r.ok)throw Error('Unserved fixture');const bytes=new Uint8Array(await r.arrayBuffer()),ptr=e.osw_alloc(bytes.length);try{new Uint8Array(e.memory.buffer,ptr,bytes.length).set(bytes);e.osw_load(ptr,bytes.length);return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));}finally{e.osw_dealloc(ptr,bytes.length);}}''',BASE+'/'+fixture.relative_to(ROOT).as_posix())
            assert actual['ok'] is False;p.close();print('PASS native/actual-WASM rejection',mode,flush=True)
        # Source-index admission independently protects the large daily record corpus.
        source_index=json.loads(index.read_bytes())
        for mode in ['changed_daily_velocity','filled_missing_date']:
            bad=copy.deepcopy(source_index);raw=json.loads(bad['documents'][RAW])
            if mode=='changed_daily_velocity':raw['profiles'][0]['fields']['VCUR'][20]=999
            else:raw['profiles'][600]['fields']['VCUR'][20]=0
            bad['documents'][RAW]=json.dumps(raw);fixture=folder/'bad-index.json';fixture.write_bytes(json.dumps(bad).encode());del bad,raw
            result=subprocess.run([str(CLI),'--index',str(fixture),'-'],input='{}',capture_output=True,text=True,encoding='utf8');assert result.returncode==2 and not result.stdout
            p=page();p.route('**/eac-index-guard.html',lambda r:r.fulfill(body='<title>EAC index guard</title>',content_type='text/html'));p.goto(BASE+'/eac-index-guard.html')
            actual=p.evaluate('''async url=>{const {instance}=await WebAssembly.instantiate(await(await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports,r=await fetch(url);if(!r.ok)throw Error('Unserved index fixture');const bytes=new Uint8Array(await r.arrayBuffer()),ptr=e.osw_alloc(bytes.length);try{new Uint8Array(e.memory.buffer,ptr,bytes.length).set(bytes);e.osw_index_load(ptr,bytes.length);return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));}finally{e.osw_dealloc(ptr,bytes.length);}}''',BASE+'/'+fixture.relative_to(ROOT).as_posix())
            assert actual['ok'] is False;p.close();print('PASS native/actual-WASM source-index rejection',mode,flush=True)
        browser.close();assert not errors and not originals,(errors,originals)
    result={'status':'PASS','views':list(urls),'months':124,'source_profiles':3770,'all_source_rows_exact_native_wasm_parity':True,
            'source_query_pages':8,'source_queries':10,'packet_corruptions':8,'index_corruptions':2,'map_positions':124,
            'native_rust_projection_parity':True,'missing_date_not_current_absence':True,'bottom_zero_context':True,
            'provider_uncertainty_scope':True,'playback_stops_without_wrapping':True,'reduced_motion':True,'keyboard_320px':True,'no_automatic_originals':True}
    (out/'browser-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))


if __name__=='__main__':main()
