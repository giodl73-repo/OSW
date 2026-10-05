"""Recorded-day query, failure omission, pair integrity and accessible playback."""
import copy
import json
import os
import subprocess
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from test_rust_query_browser import native, browser_query
ROOT=Path(__file__).resolve().parents[1]
DATES=['2025-01-15','2025-04-15','2025-07-15','2025-10-15']
def query(date):return {'collection':'objects','filters':[{'field':'id','op':'eq','value':'current:loop'}],'geometry_time':{'from':date,'to':date},'limit':1}

def main():
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    owner=next(r for r in bundle['collections']['objects'] if r['id']=='current:loop')
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
            result=subprocess.run([str(ROOT/'rust/osw-query/target/debug/osw-query-cli.exe'),str(path),'-'],input='{}',capture_output=True,text=True)
            assert result.returncode==2 and not result.stdout,(mutation,result.stdout,result.stderr)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'),headless=True)
        page=browser.new_page(viewport={'width':1280,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/query.html');page.wait_for_function('window.oswLastQueryResult',timeout=60000)
        for date in DATES:assert browser_query(page,query(date))==native(query(date))
        browser_query(page,{'collection':'diagnostics','filters':[{'field':'id','op':'eq','value':'diagnostic:loop-adt-20250715'}]})
        page.locator('#query-rows button').first.click()
        page.locator('#query-detail a:visible').filter(has_text='View mapped experiment').first.click()
        expect(page).to_have_url('http://127.0.0.1:8788/almanac/loop-current-recorded-dates.html?date=2025-07-15')
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
        assert not errors;browser.close()
    print('PASS: four source-bound days, failed NOAA geometry omitted, four loader rejections, native/WASM parity, date-preserving navigation, keyboard playback and reduced-motion/mobile access')
if __name__=='__main__':main()
