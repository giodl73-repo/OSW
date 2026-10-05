"""Loop data/geometry bindings, native/WASM parity and card-to-map navigation."""
import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile
from playwright.sync_api import sync_playwright, expect
from test_rust_query_browser import native, browser_query

ROOT=Path(__file__).resolve().parents[1]

def main():
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    diagnostics=[r for r in bundle['collections']['diagnostics'] if r.get('current_id')=='loop' and r.get('observation_date')=='2026-09-25']
    assert len(diagnostics)==2
    for r in diagnostics:assert json.loads(r['source_json'])==r['document']
    map_query={'collection':'objects','filters':[{'field':'id','op':'eq','value':'current:loop'}],
        'geometry_time':{'from':'2026-09-25','to':'2026-09-25'},'limit':1}
    queries=[map_query,{'collection':'diagnostics','filters':[{'field':'current_id','op':'eq','value':'loop'}],'limit':1},
        {'collection':'route_decisions','filters':[{'field':'current_id','op':'eq','value':'loop'}]}]
    result=native(map_query);assert result['total']==1 and len(result['map_scene']['features'])==2
    assert result['rows'][0]['published_length_km'] is None and result['rows'][0]['route_ids']==[]
    assert all(f['observation_date']=='2026-09-25' for f in result['map_scene']['features'])
    assert native(queries[1])['total']==10 and native(queries[2])['rows'][0]['candidate_count']==0
    # Native loading rejects altered science, source strings, ownership and geometry.
    with tempfile.TemporaryDirectory() as directory:
        path=Path(directory)/'altered.json'
        for mutation in ['rank','document','original_json','receipt','date','frame','owner','comparison']:
            altered=copy.deepcopy(bundle)
            r=next(r for r in altered['collections']['diagnostics'] if r['id']=='diagnostic:loop-adt-20260925')
            owner=next(o for o in altered['collections']['objects'] if o['id']=='current:loop')
            if mutation=='rank':r['rank_eligible']=True
            elif mutation=='document':r['document']['selected']['admissible_diagnostic_length_km']=99999
            elif mutation=='original_json':r['source_json']=r['source_json'].replace('2214.1','99999')
            elif mutation=='receipt':r['source_file_sha256']='0'*64
            elif mutation=='date':r['observation_date']='2026-09-26'
            elif mutation=='frame':
                frame=next(f for f in altered['collections']['geometry_frames'] if f.get('diagnostic_id')==r['id'])
                frame['coordinates_lon_lat'][0][0]+=.1
                feature=next(f for f in owner['map_features'] if f.get('diagnostic_id')==r['id'])
                feature['geometry']['coordinates']=copy.deepcopy(frame['coordinates_lon_lat'])
            elif mutation=='owner':owner['diagnostic_ids']=['diagnostic:leeuwin-monthly-width']
            else:r['document']['comparison']['noaa_diagnostic_sha256']='0'*64
            path.write_text(json.dumps(altered),encoding='utf-8')
            check=subprocess.run([str(ROOT/'rust/osw-query/target/debug/osw-query-cli.exe'),str(path),'-'],input='{}',text=True,capture_output=True)
            assert check.returncode==2 and not check.stdout,(mutation,check.stdout,check.stderr)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page=browser.new_page(viewport={'width':1280,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/query.html');page.wait_for_function('window.oswLastQueryResult',timeout=60000)
        for q in queries:assert browser_query(page,q)==native(q)
        browser_query(page,map_query)
        page.locator('#query-map-features .line').first.focus();page.locator('#query-map-features .line').first.press('Enter')
        expect(page.locator('#query-detail')).to_contain_text('Unranked method diagnostics (10)')
        page.get_by_text('Unranked method diagnostics (10)',exact=True).click()
        expect(page.locator('#query-detail')).to_contain_text('approximately 2,200 km')
        expect(page.locator('#query-detail')).to_contain_text('approximately 2,300 km')
        expect(page.locator('#query-detail')).to_contain_text('shared satellite inputs possible')
        page.locator('#query-detail').screenshot(path=str(ROOT/'figures/rust-query-loop-comparison-review.png'))
        page.locator('#query-detail a:visible[href*="loop-current-experiment"]').first.click()
        expect(page).to_have_url('http://127.0.0.1:8788/almanac/loop-current-experiment.html?date=2026-09-25')
        assert page.locator('path.adt').count()==1 and page.locator('path.failed').count()==4
        expect(page.locator('main')).to_contain_text('55.9 km')
        page.screenshot(path=str(ROOT/'figures/loop-current-dated-streamline-review.png'),full_page=True)
        page.set_viewport_size({'width':320,'height':900})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        assert not errors;browser.close()
    print('PASS: two source-bound Loop methods/frames, eight loader rejections, native/WASM parity, map keyboard selection, source-card navigation and mobile comparison')

if __name__=='__main__':main()
