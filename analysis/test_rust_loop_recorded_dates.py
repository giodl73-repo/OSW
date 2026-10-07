"""Recorded-day query, failure omission, pair integrity and accessible playback."""
import copy
import hashlib
import re
import json
import os
import subprocess
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from test_rust_query_browser import CLI, native, browser_query
from test_rust_atlas_snapshot_browser import route_atlas_bundle
ROOT=Path(__file__).resolve().parents[1]
DATES=['2025-01-15','2025-04-15','2025-07-15','2025-10-15']
def query(date):return {'collection':'objects','filters':[{'field':'id','op':'eq','value':'current:loop'}],'geometry_time':{'from':date,'to':date},'limit':1}

def main():
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    owner=next(r for r in bundle['collections']['objects'] if r['id']=='current:loop')
    view=json.loads(subprocess.check_output([str(CLI),str(ROOT/'almanac/query-data.json'),'--loop-recorded'],encoding='utf-8'))
    comparison=json.loads((ROOT/'research/loop-current-recorded-date-comparison.json').read_bytes())
    assert [f['date'] for f in view['frames']]==DATES
    for path,digest in view['source_sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest
    assert len(view['source_sha256'])==2
    for frame,row in zip(view['frames'],comparison['dates']):
        assert frame['difference']==row['signed_difference_duacs_minus_noaa_km']
        assert frame['failed_scenarios']==row['noaa_failed_scenario_count']
        assert frame['noaa_stop']==row['noaa_stop_reason'].replace('_',' ')
        for method,key in [('noaa','nominal'),('adt','selected')]:
            source=json.loads((ROOT/row[method+'_diagnostic_file']).read_bytes())
            points=source[key]['coordinates_lon_lat']
            projected=list(zip(*[iter([float(v) for v in re.findall(r'-?\d+(?:\.\d+)?',frame[method+'_path'])])]*2))
            assert len(points)==len(projected)
            for (lon,lat),(x,y) in zip(points,projected):
                assert abs(x-(60+(lon+180)/360*1480))<=.0000051
                assert abs(y-(90+(90-lat)/180*740))<=.0000051
            assert frame[method+'_file']=='../'+row[method+'_diagnostic_file']
        assert frame['query']==query(row['date'])
    assert [f['noaa_display'] for f in view['frames']]==['unresolved','1,600 km','unresolved','unresolved']
    assert [f['adt_display'] for f in view['frames']]==['2,100 km','1,600 km','1,700 km','1,000 km']

    assert len(owner['diagnostic_ids'])==10 and len(owner['frame_ids'])==7
    for date,count in zip(DATES,[1,2,1,1]):
        result=native(query(date));assert len(result['map_scene']['features'])==count
        assert all(f['observation_date']==date for f in result['map_scene']['features'])
        assert native({'collection':'diagnostics','filters':[{'field':'current_id','op':'eq','value':'loop'},{'field':'observation_date','op':'eq','value':date}]})['total']==2
    assert native(query('2025-01-16'))['total']==0
    # A failed trace cannot be given a map frame; incomplete pairs cannot load.
    with tempfile.TemporaryDirectory() as directory:
        for mutation in ['pair','invented_failure_frame','date','geometry']:
            data=copy.deepcopy(bundle);records=data['collections']['diagnostics'];record=next(r for r in records if r['id']=='diagnostic:loop-noaa-20250115')
            loop=next(r for r in data['collections']['objects'] if r['id']=='current:loop')
            if mutation=='pair':
                records.remove(record);loop['diagnostic_ids'].remove(record['id'])
            elif mutation=='invented_failure_frame':
                frame=copy.deepcopy(next(f for f in data['collections']['geometry_frames'] if f.get('diagnostic_id')=='diagnostic:loop-adt-20250115'))
                frame['id']='geometry-frame:loop-noaa-20250115';frame['diagnostic_id']=record['id']
                data['collections']['geometry_frames'].append(frame);loop['frame_ids'].append(frame['id'])
            elif mutation=='date':record['observation_date']='2025-01-16'
            else:
                frame=next(f for f in data['collections']['geometry_frames'] if f.get('diagnostic_id')=='diagnostic:loop-adt-20250115')
                frame['coordinates_lon_lat'][0][0]+=.1
                feature=next(f for f in loop['map_features'] if f.get('frame_id')==frame['id']);feature['geometry']['coordinates']=copy.deepcopy(frame['coordinates_lon_lat'])
            path=Path(directory)/'changed.json';path.write_text(json.dumps(data),encoding='utf-8')
            result=subprocess.run([str(CLI),str(path),'-'],input='{}',capture_output=True,text=True)
            assert result.returncode==2 and not result.stdout,(mutation,result.stdout,result.stderr)
    # Contradictory checked comparison receipts cannot be admitted by repinning the outer bundle.
    with tempfile.TemporaryDirectory() as directory:
        for mutation in ['hash','scope','outcome','dates','missing','dependency']:
            data=copy.deepcopy(bundle);path='research/loop-current-recorded-date-comparison.json'
            receipts=data['manifest']['loop_recorded_receipts']
            if mutation=='missing':del receipts[path]
            elif mutation=='hash':receipts[path]['source_json']+=' '
            else:
                document=json.loads(receipts[path]['source_json'])
                if mutation=='scope':document['rank_eligible']=True
                elif mutation=='outcome':document['dates'][0]['noaa_connected_length_km']=100
                elif mutation=='dates':document['dates'].reverse()
                else:document['source_manifest_sha256']='0'*64
                raw=json.dumps(document);digest=hashlib.sha256(raw.encode('utf-8')).hexdigest()
                receipts[path]['source_json']=raw;receipts[path]['source_sha256']=digest;data['manifest']['input_sha256'][path]=digest
            file=Path(directory)/'bad-receipt.json';file.write_text(json.dumps(data),encoding='utf-8')
            run=subprocess.run([str(CLI),str(file),'-'],input='{}',capture_output=True,text=True,encoding='utf-8')
            assert run.returncode==2 and not run.stdout,(mutation,run.stderr)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'),headless=True)
        page=browser.new_page(viewport={'width':1280,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.route('**/research/*.json',lambda r:r.abort())
        page.goto('http://127.0.0.1:8788/almanac/query.html');page.wait_for_function('window.oswLastQueryResult',timeout=60000)
        for date in DATES:assert browser_query(page,query(date))==native(query(date))
        browser_query(page,{'collection':'diagnostics','filters':[{'field':'id','op':'eq','value':'diagnostic:loop-adt-20250715'}]})
        page.locator('#query-rows button').first.click()
        page.locator('#query-detail a:visible').filter(has_text='View mapped experiment').first.click()
        expect(page).to_have_url('http://127.0.0.1:8788/almanac/loop-current-recorded-dates.html?date=2025-07-15')
        page.wait_for_function('window.oswLoopRecordedView && document.querySelector("#recorded-date").value==="2025-07-15"',timeout=90000)
        assert page.evaluate('window.oswLoopRecordedView')==view
        expect(page.locator('#recorded-date')).to_have_value('2025-07-15');expect(page.locator('#outcome')).to_contain_text('NOAA unresolved')
        assert 'failed' in page.locator('#noaa-line').get_attribute('class')
        page.locator('#previous').focus();page.locator('#previous').press('Enter')
        expect(page.locator('#recorded-date')).to_have_value('2025-04-15');expect(page.locator('#outcome')).to_contain_text('19.5 km')
        assert 'failed' not in page.locator('#noaa-line').get_attribute('class')
        page.screenshot(path=str(ROOT/'figures/loop-current-recorded-dates-review.png'),full_page=True)
        page.locator('#recorded-date').select_option('2025-01-15');page.locator('#play').click()
        expect(page.locator('#play')).to_have_attribute('aria-pressed','true')
        expect(page.locator('#recorded-date')).to_have_value('2025-10-15',timeout=10000)
        expect(page.locator('#play')).to_have_attribute('aria-pressed','false')
        page.emulate_media(reduced_motion='reduce');expect(page.locator('#play')).to_be_disabled()
        page.set_viewport_size({'width':320,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        for frame in view['frames']:
            page.locator('#recorded-date').select_option(frame['date'])
            assert page.locator('#noaa-line').get_attribute('d')==frame['noaa_path']
            assert page.locator('#adt-line').get_attribute('d')==frame['adt_path']
        selected=page.url;page.reload();page.wait_for_function('window.oswLoopRecordedView',timeout=90000)
        assert page.url==selected
        expect(page.locator('#recorded-date')).to_have_value('2025-10-15')
        page.emulate_media(reduced_motion='no-preference')
        page.locator('#recorded-date').select_option('2025-01-15');page.locator('#play').click()
        page.locator('#next').click();expect(page.locator('#play')).to_have_attribute('aria-pressed','false')
        page.locator('#play').click()
        page.evaluate('Object.defineProperty(document,"hidden",{configurable:true,get:()=>true});document.dispatchEvent(new Event("visibilitychange"))')
        expect(page.locator('#play')).to_have_attribute('aria-pressed','false')
        for kind in ['load_failure','missing_receipts','invalid_receipts']:
            failed=browser.new_page()
            if kind=='load_failure':failed.route('**/query-data.json',lambda r:r.fulfill(status=503,body='Unavailable'))
            else:
                changed=copy.deepcopy(bundle)
                if kind=='missing_receipts':del changed['manifest']['loop_recorded_receipts']
                else:changed['manifest']['loop_recorded_receipts']['research/loop-current-recorded-date-comparison.json']['source_json']+=' '
                route_atlas_bundle(failed,changed)
            failed.goto('http://127.0.0.1:8788/almanac/loop-current-recorded-dates.html')
            expect(failed.locator('#outcome')).to_contain_text('data unavailable',timeout=90000)
            assert failed.locator('#controls').is_hidden()
            assert failed.locator('#recorded-date option').count()==0
            assert failed.locator('#noaa-line').get_attribute('d') is None
            assert failed.locator('tbody tr').count()==4
            assert failed.evaluate('window.oswLoopRecordedView===undefined')
            failed.close()
        assert not errors;browser.close()
    print('PASS: four source-bound days, failed NOAA geometry omitted, ten loader rejections, exact checked native/WASM views and source vertices, no direct reads, date-preserving navigation, keyboard playback/manual/hidden/reduced-motion controls, mobile and unavailable data')
if __name__=='__main__':main()
