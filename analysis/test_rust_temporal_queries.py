"""Recorded-day selection and time/state feature correspondence against source records."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from test_rust_query_browser import native, browser_query

ROOT=Path(__file__).resolve().parents[1]

def allowed(feature,time):
    date=feature.get('observation_date')
    return time.get('include_undated',False) if date is None else time['from']<=date<=time['to']

def main():
    source=json.loads((ROOT/'almanac/query-data.json').read_text(encoding='utf-8'))
    objects={r['id']:r for r in source['collections']['objects']}
    imported={r['id']:r for r in native({'collection':'objects','limit':500})['rows']}
    days=sorted({f['observation_date'] for r in objects.values() for f in r.get('map_features',[]) if f.get('observation_date')})
    queries=[{'collection':'objects','limit':1,'geometry_time':{'from':day,'to':day}} for day in days]
    queries += [{'collection':'objects','geometry_time':{'from':'2026-09-25','to':'2026-09-28','include_undated':True}}]
    queries += [{'collection':'objects','geometry_time':{'from':'2024-02-29','to':'2024-02-29'}}]
    queries += [{'collection':'objects','spatial':{'state_code':'NADR','predicate':'intersects'},'geometry_time':{'from':day,'to':day}} for day in days]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page=browser.new_page(viewport={'width':1200,'height':1000});page.goto('http://127.0.0.1:8788/almanac/query.html')
        page.wait_for_function('window.oswLastQueryResult',timeout=60000)
        assert page.locator('#query-map-day option').all_text_contents()==['Choose a recorded day']+days
        for query in queries:
            time=query['geometry_time'];result=native(query);assert result['ok'],result
            reference=native({**{k:v for k,v in query.items() if k not in ['geometry_time','limit']},'limit':500})
            expected=set()
            for row in reference['rows']:
                if query.get('spatial'):
                    qualifies=any(allowed(objects[row['id']]['map_features'][r['feature_index']],time) for r in row['spatial_matches'])
                else:qualifies=any(allowed(f,time) for f in row.get('map_features',[]))
                if qualifies:expected.add(row['id'])
            assert result['total']==len(expected)
            assert {r['id'] for r in result['rows']}<=expected
            for feature in result['map_scene']['features']:
                raw=objects[feature['entity_id']]['map_features'][feature['feature_index']]
                assert allowed(raw,time)
                assert feature['undated_context']==(raw.get('observation_date') is None)
            for row in result['rows']:
                # Compare the unfiltered Rust store: Python and serde_json can round
                # input decimal coordinates by one ULP during parsing/serialization.
                assert row['map_features']==imported[row['id']]['map_features']
                for relation in row.get('spatial_matches',[]):assert allowed(row['map_features'][relation['feature_index']],time)
            assert browser_query(page,query)==result
        page.locator('#query-map-day').select_option('2026-09-28')
        expect(page.locator('#query-time-from')).to_have_value('2026-09-28')
        expect(page.locator('#query-map-time')).to_contain_text('2026-09-28')
        page.wait_for_function('window.oswLastQueryResult.map_scene.geometry_time.from==="2026-09-28"')
        with page.expect_download() as download:page.locator('#query-map-export').click()
        svg=Path(download.value.path()).read_text(encoding='utf-8');assert 'Recorded observations 2026-09-28 through 2026-09-28' in svg
        link=page.locator('#query-share').get_attribute('href');shared=browser.new_page();shared.goto(link)
        shared.wait_for_function('window.oswLastQueryResult',timeout=60000)
        assert shared.evaluate('window.oswLastQueryResult.map_scene.geometry_time.from')=='2026-09-28'
        page.set_viewport_size({'width':320,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.screenshot(path=str(ROOT/'figures/rust-query-temporal-mobile-review.png'),full_page=True)
        for query in [{'geometry_time':{'from':'2025-02-29','to':'2025-03-01'}},
                      {'geometry_time':{'from':'2026-09-28','to':'2026-09-25'}},
                      {'collection':'widths','geometry_time':{'from':'2026-09-25','to':'2026-09-25'}}]:
            assert native(query)['ok'] is False
        browser.close()
    print('PASS: recorded-day source oracle, native/WASM parity, time/state feature identity, unchanged source rows, date controls/share/SVG and mobile')

if __name__=='__main__':main()
