"""Source phase fidelity, month gaps, same-feature spatial queries and WASM parity."""
import json
import os
import subprocess
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from test_rust_query_browser import native, browser_query
from test_rust_svg_export import inspect

ROOT=Path(__file__).resolve().parents[1]


def main():
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    document=json.loads((ROOT/'research/ocean-current-seasonal-route-frames.json').read_bytes())
    phases=bundle['collections']['seasonal_routes'];assert len(phases)==6
    objects={r['id']:r for r in bundle['collections']['objects']}
    for source in document['frames']:
        phase=next(p for p in phases if p['id']==source['id'])
        assert all(phase[k]==v for k,v in source.items())
        candidate=json.loads((ROOT/source['route_candidate_file']).read_bytes())
        assert phase['coordinates_lon_lat']==candidate['coordinates_lon_lat']
        feature=next(f for f in objects[phase['entity_id']]['map_features'] if f.get('phase_id')==phase['id'])
        assert feature['geometry']['coordinates']==candidate['coordinates_lon_lat']
        assert feature.get('observation_date') is None
        assert phase['comparability']['annual_extrema_eligible'] is False
    queries=[]
    for month in range(1,13):
        query={'collection':'objects','seasonal':{'month':month},'limit':1}
        result=native(query);assert result['ok']
        expected={p['id'] for p in phases if month in (p['calendar_months'] or [])}
        assert {f['phase_id'] for f in result['map_scene']['features']}==expected
        assert result['total']==len({p['entity_id'] for p in phases if p['id'] in expected})
        assert result['map_scene']['matching_objects']==result['total']
        assert all(f['observation_date'] is None for f in result['map_scene']['features'])
        queries.append(query)
    for phase in phases:
        query={'collection':'objects','seasonal':{'phase_id':phase['id']}}
        result=native(query);assert result['total']==1
        assert [f['phase_id'] for f in result['map_scene']['features']]==[phase['id']]
        queries.append(query)
    # Spatial matching must use the selected phase, not a different route of its object.
    for state in ['MONS','EAFR','CAMR']:
        baseline=native({'collection':'objects','spatial':{'state_code':state,'predicate':'intersects'},'limit':500})
        assert baseline['ok']
        for month in [1,7]:
            query={'collection':'objects','seasonal':{'month':month},'spatial':{'state_code':state,'predicate':'intersects'}}
            result=native(query);expected=set()
            for entity,relations in baseline['map_scene']['spatial_relations'].items():
                for relation in relations:
                    feature=objects[entity]['map_features'][relation['feature_index']]
                    if feature.get('phase_id') and month in (feature['calendar_months'] or []):expected.add(entity)
            assert {r['id'] for r in result['rows']}==expected
            queries.append(query)
    bad=[{'seasonal':{}},{'seasonal':{'month':0}},{'seasonal':{'month':13}},
         {'seasonal':{'phase_id':'missing'}},{'seasonal':{'month':1,'phase_id':'somali-winter'}},
         {'collection':'widths','seasonal':{'month':1}},
         {'seasonal':{'month':1},'geometry_time':{'from':'2025-01-15','to':'2025-01-15'}}]
    for query in bad:assert native(query)['ok'] is False
    with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as temp, sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page=browser.new_page(viewport={'width':1280,'height':1000});errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto('http://127.0.0.1:8788/almanac/query.html');page.wait_for_function('window.oswLastQueryResult',timeout=60000)
        for query in queries:assert browser_query(page,query)==native(query)
        for query in bad:assert browser_query(page,query) is None
        page.locator('[data-preset="seasonal-january"]').click()
        page.wait_for_function('window.oswLastQueryResult?.map_scene?.seasonal?.month===1')
        assert page.locator('#query-map-features [data-phase]').count()==3
        expect(page.locator('#query-map-time')).to_contain_text('Source-defined regional editorial phases')
        page.locator('#query-season-phase').select_option('somali-winter');page.locator('#query-run').click()
        page.wait_for_function('window.oswLastQueryResult?.map_scene?.seasonal?.phase_id==="somali-winter"')
        assert page.locator('#query-season-month').input_value()==''
        page.locator('#query-map-features [data-phase]').focus()
        expect(page.locator('#query-map-hover')).to_contain_text('southward')
        page.locator('#query-map-features [data-phase]').press('Enter')
        expect(page.locator('#query-detail')).to_contain_text('Source-defined seasonal routes (2)')
        expect(page.locator('#query-detail')).to_contain_text('Source month convention: unresolved')
        expect(page.get_by_role('link',name='Map this source phase')).to_have_count(2)
        # April has no source month support for any of these six phases.
        page.locator('#query-season-month').select_option('4');page.locator('#query-run').click()
        page.wait_for_function('window.oswLastQueryResult?.map_scene?.seasonal?.month===4')
        assert page.evaluate('window.oswLastQueryResult.total')==0
        assert page.locator('#query-map-features').evaluate('(e)=>e.childElementCount')==0
        browser_query(page,{'collection':'objects','seasonal':{'month':3}})
        page.locator('#query-map-play-months').click()
        expect(page.locator('#query-map-play-months')).to_have_attribute('aria-pressed','true')
        page.wait_for_function('window.oswLastQueryResult?.map_scene?.seasonal?.month===4',timeout=10000)
        page.locator('#query-map-play-months').click()
        expect(page.locator('#query-map-play-months')).to_have_attribute('aria-pressed','false')
        page.wait_for_timeout(1400)
        assert page.evaluate('window.oswLastQueryResult.map_scene.seasonal.month')==4
        assert page.evaluate('window.oswLastQueryResult.total')==0
        browser_query(page,{'collection':'objects','seasonal':{'month':12}})
        page.locator('#query-map-play-months').click()
        expect(page.locator('#query-map-play-months')).to_have_attribute('aria-pressed','false',timeout=10000)
        assert page.evaluate('window.oswLastQueryResult.map_scene.seasonal.month')==12
        query={'collection':'objects','seasonal':{'phase_id':'monsoon-winter-sri-lanka'}}
        result=browser_query(page,query);page.locator('#query-map-fit').click()
        page.locator('#query-map-section').screenshot(path=str(ROOT/'figures/rust-query-seasonal-map-review.png'))
        folder=Path(temp);qfile=folder/'query.json';qfile.write_text(json.dumps(query),encoding='utf-8');svgfile=folder/'map.svg'
        subprocess.run([str(ROOT/'rust/osw-query/target/debug/osw-query-cli.exe'),str(ROOT/'almanac/query-data.json'),'--svg',str(qfile),'--output',str(svgfile)],check=True,capture_output=True)
        svg=svgfile.read_text(encoding='utf-8');receipt=inspect(svg,query,result['map_scene']);assert receipt['seasonal']==result['map_scene']['seasonal']
        with page.expect_download() as download:page.locator('#query-map-export').click()
        assert Path(download.value.path()).read_text(encoding='utf-8')==svg
        page.set_viewport_size({'width':320,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert not errors
        browser.close()
    print('PASS: six source phases; 12 month selections and gaps; named unknown-month phase; spatial same-feature filtering; native/WASM parity; keyboard/mobile and SVG provenance')


if __name__=='__main__':main()
