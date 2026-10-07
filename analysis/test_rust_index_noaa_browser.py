"""Original NOAA state inventories and file-scoped tracks match native/WASM."""
import gzip
import json
import os
from pathlib import Path
import subprocess
import tempfile
from playwright.sync_api import sync_playwright
from test_rust_query_browser import ROOT, CLI


def main():
    def read(path): return json.loads((ROOT/path).read_bytes())
    manifest = read('research/noaa-munster-eddy-seasonal-manifest-2021-2023.json')
    crops = read('research/noaa-nasa-eddy-crop-join.json')
    tiles = {r['id']:r for r in read('research/nasa-perpetual-ocean-tile-join.json')['tiles']}
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as folder:
        packet = Path(folder)/'index.json'
        packet.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        def native(flag, request):
            run = subprocess.run([str(CLI),'--index',str(packet),flag,'-'], input=json.dumps(request),
                                 text=True,encoding='utf-8',capture_output=True)
            assert run.returncode == 0, run.stderr
            return json.loads(run.stdout)
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page = browser.new_page()
            errors = []
            page.on('pageerror',lambda e: errors.append(str(e)))
            page.goto('http://127.0.0.1:8788/almanac/index.html?state=CAMR')
            page.wait_for_function('window.oswIndexPageReady',timeout=90000)
            for snapshot in manifest['snapshots']:
                date = snapshot['date']
                print('Checking NOAA '+date,flush=True)
                doc = read(snapshot['path'].removeprefix('../'))
                entries = {r['id']:(i,r) for i,r in enumerate(doc['entries'])}
                requests = [{'date':date,'state_code':code} for code in doc['states']]
                views = page.evaluate('async requests=>{const rows=[]; for(const r of requests) rows.push(await oswIndexNoaaState(r));return rows}',requests)
                assert native('--noaa-state', requests[0]) == views[0]
                for request, view in zip(requests, views):
                    code = request['state_code']
                    assert view['date'] == date and view['state_code'] == code
                    assert view['source'] == snapshot['path'].removeprefix('../')
                    assert view['source_sha256'] == doc['source_sha256']
                    assert view['identity_limit'] == doc['identity_limit']
                    assert bool(view['weekly']) == snapshot['weekly_track_join']
                    for group in view['groups']:
                        ids = doc['states'][code][group['status']]
                        assert [r['id'] for r in group['rows']] == ids
                        for row in group['rows']:
                            index, record = entries[row['id']]
                            assert row['record'] == record
                            assert row['source_pointer'] == '/entries/'+str(index)
                            crop = crops['dates'].get(date)
                            tile_id = crop['detections'].get(row['id']) if crop else None
                            assert row['track_available'] == snapshot['weekly_track_join']
                            if tile_id:
                                assert row['crop']['tile'] == tiles[tile_id]
                                assert row['crop']['estimated_crop_seconds'] == crop['estimated_crop_seconds']
                            else: assert row['crop'] is None
                            lon,lat = record['center']
                            if lon is None or lat is None: assert row['point'] is None
                            else:
                                x,y = row['point']
                                assert abs(x-(60+(lon+180)/360*1480)) < 1e-9
                                assert abs(y-(90+(90-lat)/180*740)) < 1e-9
                if snapshot['weekly_track_join']:
                    stamp = date.replace('-','')
                    interval = stamp+'-'+stamp[:4]+'0607.json'
                    tracks = read('research/noaa-munster-eddy-weekly-join-'+interval)
                    centers = read('research/noaa-munster-eddy-weekly-state-join-'+interval)
                    contours = read('research/noaa-munster-eddy-weekly-contour-state-join-'+interval)
                    for view in views:
                        code = view['state_code']
                        assert view['weekly']['center_relations'] == centers['states'][code]
                        assert view['weekly']['contour_relations'] == contours['states'][code]
                    # Shortest, longest, seam-crossing and ordinary paths stay source-scoped.
                    records = list(tracks['tracks'].items())
                    seam = next(((id,r) for id,r in records if any(abs(a['center'][0]-b['center'][0])>180 for a,b in zip(r['positions'],r['positions'][1:]))),records[0])
                    chosen = [min(records,key=lambda pair:len(pair[1]['positions'])),max(records,key=lambda pair:len(pair[1]['positions'])),seam,records[0]]
                    for id, record in chosen:
                        req = {'date':date,'state_code':'CAMR','detection_id':id,'focus_date':record['positions'][-1]['date']}
                        view = page.evaluate('r=>oswIndexNoaaTrack(r)',req)
                        assert view == native('--noaa-track',req)
                        assert view['record'] == record
                        assert view['center_visits'] == centers['tracks'][id]
                        assert view['contour_visits'] == contours['tracks'][id]
                        assert len(view['points']) == len(record['positions'])
                        moves = 1 + sum(abs(a['center'][0]-b['center'][0])>180 for a,b in zip(record['positions'],record['positions'][1:]))
                        assert view['path'].count('M') == moves
                    id,record = records[0]
                    req = {'date':date,'state_code':'CAMR','detection_id':id,'focus_date':record['positions'][0]['date']}
                    for bad in [{**req,'focus_date':'2023-01-01'},{**req,'detection_id':'other-file'}, {**req,'state_code':'invented'},{**req,'extra':True}]:
                        assert page.evaluate('r=>oswIndexNoaaTrack(r).then(()=>false,()=>true)',bad)
            for bad in [{'date':'2023-06-02','state_code':'CAMR'},{'date':'2023-06-01','state_code':'invented'}, {'date':'2023-06-01','state_code':'CAMR','extra':True}]:
                assert page.evaluate('r=>oswIndexNoaaState(r).then(()=>false,()=>true)',bad)
            # Exercise the actual track button rather than only RPC calls.
            page.locator('.state-eddy-details button').first.evaluate('(node)=>{for(let parent=node.parentElement;parent;parent=parent.parentElement) if(parent.tagName==="DETAILS") parent.open=true;}')
            page.evaluate('''()=>{const original=Element.prototype.scrollIntoView;
                Element.prototype.scrollIntoView=function(options){
                    if(this.id==='motion-map-section')window.trackScrollCalls.push(options);
                    return original.call(this,options);};}''')
            for preference,behavior in [('no-preference','smooth'),('reduce','instant')]:
                page.emulate_media(reduced_motion=preference)
                page.evaluate('()=>{window.oswIndexNoaaTrackView=null;window.trackScrollCalls=[];}')
                page.locator('.state-eddy-details button').first.click()
                page.wait_for_function('window.oswIndexNoaaTrackView && window.trackScrollCalls.length',timeout=90000)
                assert page.locator('#selected-eddy-track path').get_attribute('d') == page.evaluate('oswIndexNoaaTrackView.path')
                assert page.evaluate('trackScrollCalls.at(-1)') == {'behavior':behavior,'block':'start'}
            assert not errors, errors
            browser.close()
    print('PASS: 12 dates × 56 original state inventories, source records/addresses/projections, weekly center/contour joins, native/WASM paths and invalid source identities, actual track navigation')


if __name__ == '__main__': main()
