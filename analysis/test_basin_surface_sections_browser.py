"""Five source-bound monthly charts/maps, playback, inspect/share and rejection."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from urllib.parse import quote
from playwright.sync_api import sync_playwright, expect
from test_rust_query_browser import native, browser_query, CLI, ROOT
from build_query_width_samples import build as project_samples


def main():
    output=ROOT/'.pytest_cache/basin-current-width-review'
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    new=[r for r in bundle['collections']['width_samples'] if r['sample_family']=='basin_monthly_component_section' and not r['source_context'].get('is_climatology')]
    assert len(new)==84 and sum(r['resolution_review_required'] for r in new)==49
    snapshot=json.loads((ROOT/'research/ocean-motion-dashboard.json').read_bytes())
    for owner in ['portugal','south-atlantic','south-pacific','south-indian','aleutian','south-australian','west-australian']:
        entry=next(r for r in snapshot['entries'] if r['id']=='current:'+owner)
        expected_date='2009-11-11' if owner=='portugal' else None
        assert entry['capabilities']['scoped_width']==(1 if owner=='west-australian' else 0) and entry['latest_observation_date']==expected_date
        assert any(s['frames']==12 and s['evidence_role']=='monthly_local_component_spans_current_width_unresolved' for s in entry['series'])
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ['OSW_TEST_BROWSER'])
        page=browser.new_page(viewport={'width':1400,'height':1100})
        page.emulate_media(reduced_motion='reduce');errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/query.html')
        page.wait_for_function('window.oswLastQueryResult',timeout=60000)
        for owner in ['portugal','south-atlantic','south-pacific','south-indian','aleutian','south-australian','west-australian']:
            query={'collection':'width_samples','filters':[{'field':'current_id','op':'eq','value':owner},{'field':'diagnostic_id','op':'eq','value':next(r['diagnostic_id'] for r in new if r['current_id']==owner)}],'sort':{'field':'month','direction':'asc'},'limit':5}
            expected=native(query);actual=browser_query(page,query)
            assert actual==expected and actual['total']==12
            assert actual['chart_scene']['panels'][0]['matching_samples']==12 and actual['map_scene']['mapped_objects']==12
            assert all(r['current_association_verified'] is False for r in actual['rows'])
            expect(page.locator('#chart-title')).to_have_text('Local component section spans')
            expect(page.locator('#query-chart-panels')).to_contain_text('current width unresolved')
            page.locator('.chart-sample').nth(3).focus();page.keyboard.press('Enter')
            expect(page.locator('#query-detail')).to_contain_text('Apr')
            control=page.locator('.chart-playback select');assert control.locator('option').count()==12
            control.select_option(index=11)
            page.get_by_role('button',name='Inspect selected month',exact=True).click()
            expect(page.locator('#query-detail')).to_contain_text('Current association is unresolved')
            expect(page.locator('#query-detail')).to_contain_text('Native resolution review')
            expect(page.locator('#query-detail')).to_contain_text('40–60% peak threshold sensitivity')
            assert page.locator('#query-detail').get_by_role('link',name='View all monthly velocity profiles').count()==1
            if owner=='south-australian':
                assert page.locator('#query-detail').get_by_role('link',name='View all monthly velocity profiles').get_attribute('href').endswith('-2012-monthly-component-profiles.svg')
                expect(page.locator('#query-chart-panels')).to_contain_text('2012')
            page.get_by_role('button',name='Inspect parent diagnostic',exact=True).click()
            expect(page.locator('#query-detail')).to_contain_text('diagnostic:basin-')
            page.set_viewport_size({'width':320,'height':900})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.screenshot(path=str(output/(owner+'-query-mobile.png')))
            page.set_viewport_size({'width':1400,'height':1100})
        # The source corpus contains complete original vector inventories, not just spans.
        query={'collection':'width_samples','filters':[{'field':'current_id','op':'eq','value':'portugal'}],'sort':{'field':'month'},'limit':100}
        browser_query(page,query)
        page.screenshot(path=str(ROOT/'figures/basin-surface-sections-query-review.png'))
        assert not errors,errors
        page.route('**/basin-guard.html',lambda route:route.fulfill(body='<title>Basin diagnostic guard</title>',content_type='text/html'))
        page.goto('http://127.0.0.1:8788/basin-guard.html')
        for mode in ['value','association','rebound','hycom_rebound','offshore_rebound']:
            bad=copy.deepcopy(bundle)
            if mode in ['rebound','hycom_rebound','offshore_rebound']:
                target={'rebound':'portugal-40n','hycom_rebound':'south-australian-132e-100m','offshore_rebound':'west-australian-32s'}[mode]
                diagnostic=next(r for r in bad['collections']['diagnostics'] if r['id']=='diagnostic:basin-'+target)
                diagnostic['document']['months'][0]['approximate_section_span_km']=999
                diagnostic['source_json']=json.dumps(diagnostic['document'])
                pin=hashlib.sha256(diagnostic['source_json'].encode()).hexdigest()
                diagnostic['source_file_sha256']=pin;bad['manifest']['input_sha256'][diagnostic['source_file']]=pin
                bad['collections']['width_samples']=project_samples(bad['collections']['diagnostics'])
            else:
                sample=next(r for r in bad['collections']['width_samples'] if r['sample_family']=='basin_monthly_component_section')
                sample['value_km' if mode=='value' else 'current_association_verified']=999 if mode=='value' else True
            with TemporaryDirectory(dir=output) as tmp:
                path=Path(tmp)/'forged.json';path.write_text(json.dumps(bad),encoding='utf-8')
                result=page.evaluate('''async path=>{
                    const {instance}=await WebAssembly.instantiate(await (await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports;
                    const b=new Uint8Array(await (await fetch(path)).arrayBuffer()),p=e.osw_alloc(b.length);
                    try{new Uint8Array(e.memory.buffer,p,b.length).set(b);e.osw_load(p,b.length);
                      return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));
                    }finally{e.osw_dealloc(p,b.length);}
                }''','/'+path.relative_to(ROOT).as_posix())
                assert result['ok'] is False,result
                if mode in ['rebound','hycom_rebound','offshore_rebound']:assert 'frozen basin' in result['error'].lower(),result
        browser.close()
    with TemporaryDirectory(dir=output) as tmp:
        path=Path(tmp)/'forged.json'
        for field,value in [('value_km',999),('current_association_verified',True),('width_rank_eligible',True),('resolution_review_required',False)]:
            bad=copy.deepcopy(bundle)
            row=next(r for r in bad['collections']['width_samples'] if r['sample_family']=='basin_monthly_component_section')
            row[field]=value;path.write_text(json.dumps(bad),encoding='utf-8')
            result=subprocess.run([str(CLI),str(path),'-'],input='{}',capture_output=True,text=True,encoding='utf-8')
            assert result.returncode==2 and not result.stdout,(field,result.stderr)
        bad=copy.deepcopy(bundle);row=next(r for r in bad['collections']['diagnostics'] if r['id']=='diagnostic:basin-portugal-40n')
        row['document']['months'][0]['approximate_section_span_km']=999
        row['source_json']=json.dumps(row['document']);pin=hashlib.sha256(row['source_json'].encode()).hexdigest()
        row['source_file_sha256']=pin;bad['manifest']['input_sha256'][row['source_file']]=pin
        bad['collections']['width_samples']=project_samples(bad['collections']['diagnostics'])
        path.write_text(json.dumps(bad),encoding='utf-8')
        result=subprocess.run([str(CLI),str(path),'-'],input='{}',capture_output=True,text=True,encoding='utf-8')
        assert result.returncode==2 and 'frozen basin' in result.stderr.lower()
    print('PASS: 84 monthly section samples, native/WASM parity, 12 mapped boundaries/chart points per owner before pagination, manual playback/inspect/source links/mobile; five native and five WASM rejections')


if __name__=='__main__':
    main()
