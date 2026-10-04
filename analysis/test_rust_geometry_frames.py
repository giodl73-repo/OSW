"""Verified timeline ingestion, frame provenance, working joins and discrete playback."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from test_rust_query_browser import native, browser_query

ROOT=Path(__file__).resolve().parents[1]

def main():
    bundle=json.loads((ROOT/'almanac/query-data.json').read_text(encoding='utf-8'))
    frames=bundle['collections']['geometry_frames'];assert len(frames)==17
    sources={}
    for path in ['research/ocean-current-dated-timeline-2025.json','research/ocean-current-dated-timeline.json']:
        document=json.loads((ROOT/path).read_text(encoding='utf-8'))
        sources.update({f['date']:(document,f) for f in document['frames']})
    record=next(r for r in bundle['collections']['objects'] if r['id']=='current:gulf-stream-system')
    assert len(record['frame_ids'])==17
    assert sum(not f['reaches_downstream_gate'] for f in frames)==5
    for frame in frames:
        document,source=sources[frame['date']]
        assert all(frame[key]==value for key,value in source.items())
        assert frame['width_km'] is None and frame['annual_length_range_km'] is None
        assert frame['annual_extrema_eligible'] is False
        feature=next(f for f in record['map_features'] if f.get('frame_id')==frame['id'])
        assert feature['geometry']['coordinates']==source['coordinates_lon_lat']
        assert feature['source_subset_sha256']==source['source_subset_sha256']
        assert feature['role']==document['geometry_role']
    query={'collection':'geometry_frames','sort':{'field':'date'},'limit':50}
    result=native(query);assert result['total']==17 and result['map_scene'] is None
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page=browser.new_page(viewport={'width':1280,'height':1100});page.goto('http://127.0.0.1:8788/almanac/query.html')
        page.wait_for_function('window.oswLastQueryResult',timeout=60000)
        assert browser_query(page,query)==result
        page.locator('#query-rows button').first.click()
        expect(page.locator('#query-detail')).to_contain_text('Diagnostic trace distance (km; not current length)')
        expect(page.locator('#query-detail')).to_contain_text('Twelve selected daily fields')
        expect(page.get_by_role('link',name='Map this observation day')).to_have_count(1)
        page.locator('[data-preset="gulf-dated"]').click()
        page.wait_for_function('window.oswLastQueryResult.collection==="objects" && window.oswLastQueryResult.map_scene.geometry_time?.from==="2025-01-15"')
        scene=page.evaluate('window.oswLastQueryResult.map_scene');assert len(scene['features'])==1
        page.wait_for_function('Number(document.querySelector("#query-map").getAttribute("viewBox").split(" ")[2])<100')
        expect(page.locator('#query-map-ground')).to_have_attribute('href','../figures/ocean-motion-closeup-ground.svg')
        assert scene['features'][0]['frame_id']==frames[0]['id']
        page.locator('#query-map-play').click()
        expect(page.locator('#query-map-play')).to_have_attribute('aria-pressed','true')
        page.wait_for_function('window.oswLastQueryResult.map_scene.geometry_time.from==="2025-02-15"',timeout=10000)
        page.locator('#query-map-play').click()
        expect(page.locator('#query-map-play')).to_have_attribute('aria-pressed','false')
        selected=page.evaluate('window.oswLastQueryResult.map_scene.geometry_time.from');page.wait_for_timeout(1400)
        assert page.evaluate('window.oswLastQueryResult.map_scene.geometry_time.from')==selected
        page.locator('#query-map').screenshot(path=str(ROOT/'figures/rust-query-gulf-frame-review.png'))
        page.locator('#query-rows button').first.click()
        expect(page.locator('#query-detail')).to_contain_text('Dated diagnostic frames (17)')
        page.set_viewport_size({'width':320,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        browser.close()
    print('PASS: 17 exact source frames, five retained stopped traces, source receipts, native/WASM frame queries, map links, playback/pause and mobile')

if __name__=='__main__':main()
