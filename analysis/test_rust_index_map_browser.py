"""Index map scene preserves every original locator and dated source geometry."""
import gzip
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from playwright.sync_api import sync_playwright
from test_rust_query_browser import ROOT, CLI


def main():
    def read(path): return json.loads((ROOT/path).read_bytes())
    currents = read('research/ocean-current-almanac.json')['entries']
    index = read('research/ocean-current-atlas-index.json')
    loops = read('research/named-loop-current-eddy-identities.json')['entries']
    context = read('research/named-loop-eddy-nasa-context.json')['entries']
    nasa = read('research/nasa-perpetual-ocean-objects.json')['objects']
    geography = read('research/named-eddy-geography.json')['entries']
    front = read('research/gulf-stream-navo-front-20260928.json')
    diagnosed = read('almanac/release/v0.1.0/source-ledgers/gulf-stream-geostrophic-path-20260925.json')
    operational = read('almanac/release/v0.1.0/source-ledgers/navo-freddies-eddy-state-join-20260925.json')
    expected = [(r['id'],'current',p,8) for r in currents for p in index['entries'][r['id']]['locators']]
    expected += [('loop-rings','loop',index['named_loop_current_eddies']['region_locator'],13)]
    expected += [(r['id'],'loop',r['published_observed_position']['coordinate'],6) for r in context if r.get('published_observed_position')]
    expected += [(r['id'],'nasa',r['locator'],6) for r in nasa if r.get('locator') and not r.get('almanac_current_id')]
    expected += [(r['id'],'geography',r['locator'],6) for r in geography]
    def project(p): return [60+(p[0]+180)/360*1480,90+(90-p[1])/180*740]
    def verify_path(path, coordinates, closed=False):
        numbers = [float(n) for n in re.findall(r'-?\d+(?:\.\d+)?',path)]
        assert len(numbers) == 2*len(coordinates)
        for i,p in enumerate(coordinates):
            assert all(abs(a-b)<=.005001 for a,b in zip(numbers[2*i:2*i+2],project(p)))
        assert path.count('M') == 1 + sum(abs(a[0]-b[0])>180 for a,b in zip(coordinates,coordinates[1:]))
        assert path.rstrip().endswith('Z') == closed
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as folder:
        packet = Path(folder)/'index.json'
        packet.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        run = subprocess.run([str(CLI),'--index',str(packet),'--map','-'],input='{}',
                             text=True,encoding='utf-8',capture_output=True)
        assert run.returncode == 0,run.stderr
        native = json.loads(run.stdout)
        assert len(native['markers']) == len(expected)
        for row,(id,kind,point,radius) in zip(native['markers'],expected):
            assert row['id']==id and row['kind']==kind and row['radius']==radius
            assert all(abs(a-b)<1e-9 for a,b in zip(row['point'],project(point)))
        for row in native['fronts']:
            assert row['record']==front['fronts'][row['side']]
            verify_path(row['path'],row['record']['geometry']['coordinates'])
        verify_path(native['diagnosed_path'],diagnosed['representative']['coordinates_lon_lat'])
        assert native['diagnosed_length_km']==diagnosed['representative']['segment_length_km']
        for row,record in zip(native['operational_polygons'],operational['features']):
            assert row['record']==record
            verify_path(row['path'],record['display_outline_lon_lat'],True)
        assert native['counts']=={'currents':len(currents),'loop_names':len(loops),
            'published_loop_positions':sum(bool(r.get('published_observed_position')) for r in context),
            'nasa_markers':sum(bool(r.get('locator')) and not r.get('almanac_current_id') for r in nasa),
            'geography_names':len(geography)}
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page=browser.new_page()
            errors=[]
            page.on('pageerror',lambda e: errors.append(str(e)))
            page.add_init_script('''window.indexRequests=[]; const OriginalWorker=Worker;
                window.Worker=class extends OriginalWorker {postMessage(message,...rest){
                  window.indexRequests.push(message);return super.postMessage(message,...rest);}};''')
            page.goto('http://127.0.0.1:8788/almanac/index.html')
            page.wait_for_function('window.oswIndexPageReady',timeout=90000)
            assert page.evaluate('oswIndexMapView')==native
            assert page.evaluate('oswIndexMap()')==native
            assert sorted(page.evaluate('indexRequests.filter(r=>r.action==="document").map(r=>r.value.document)'))==[
                'almanac/release/v0.1.0/coverage.json',
                'research/noaa-munster-eddy-seasonal-manifest-2021-2023.json']
            markers=page.locator('#motion-markers a.map-marker').evaluate_all('(nodes)=>nodes.map(n=>({id:n.dataset.record,href:n.getAttribute("href"),label:n.getAttribute("aria-label"),title:n.querySelector("title").textContent,point:[Number(n.querySelector("circle").getAttribute("cx")),Number(n.querySelector("circle").getAttribute("cy"))],radius:Number(n.querySelector("circle").getAttribute("r"))}))')
            assert markers==[{k:r[k] for k in ['id','href','label','title','point','radius']} for r in native['markers']]
            assert page.locator('#geostrophic-streamline path').get_attribute('d')==native['diagnosed_path']
            assert page.locator('#operational-eddy-polygons path').evaluate_all('(nodes)=>nodes.map(n=>n.getAttribute("d"))')==[r['path'] for r in native['operational_polygons']]
            for selector,layer in [('#show-gulf-stream-fronts','#gulf-stream-fronts'),('#show-geostrophic-streamline','#geostrophic-streamline'),('#show-operational-eddy-polygons','#operational-eddy-polygons')]:
                page.locator(selector).check()
                assert page.locator(layer).evaluate('(n)=>n.style.display')==''
                page.locator(selector).uncheck()
                assert page.locator(layer).evaluate('(n)=>n.style.display')=='none'
            assert not errors,errors
            browser.close()
    print('PASS: all original index map locators/ordering, fronts/diagnostic/polygons, native/WASM/DOM scene equality and map toggles')


if __name__=='__main__':main()
