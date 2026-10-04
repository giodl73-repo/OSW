"""Complete query charts, stable source axes, missing marks and native/WASM parity."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from test_rust_query_browser import native,browser_query

ROOT=Path(__file__).resolve().parents[1]

def main():
    corpus=json.loads((ROOT/'almanac/query-data.json').read_bytes())['collections']['width_samples'];index={r['id']:r for r in corpus}
    query={'collection':'width_samples','limit':1,'offset':20};full=native(query)
    assert len(full['rows'])==1 and full['chart_scene']['matching_samples']==105
    assert len(full['chart_scene']['panels'])==7
    points=[p for panel in full['chart_scene']['panels'] for p in panel['points']];assert len(points)==105
    assert sum(p['primitive']['kind']=='missing' for p in points)==5
    for p in points:
        r=index[p['sample_id']];assert p['value_km']==r['value_km'] and p['plot_reading_interval_km']==r['plot_reading_interval_km']
        if r['value_km'] is None:assert p['primitive']['y'] is None and p['primitive']['missing_y']>220
    single={'collection':'width_samples','filters':[{'field':'id','op':'eq','value':points[0]['sample_id']}],'limit':1}
    result=native(single);panel=result['chart_scene']['panels'][0]
    source=next(p for p in full['chart_scene']['panels'] if p['id']==panel['id'])
    assert panel['x_domain']==source['x_domain'] and panel['y_domain_km']==source['y_domain_km']
    assert panel['points'][0]==source['points'][0]
    leeuwin={'collection':'width_samples','filters':[{'field':'current_id','op':'eq','value':'leeuwin'}],'limit':1}
    kuro={'collection':'width_samples','filters':[{'field':'current_id','op':'eq','value':'kuroshio'}],'limit':1}
    missing={'collection':'width_samples','filters':[{'field':'value_km','op':'exists','value':False}]}
    empty={'collection':'width_samples','filters':[{'field':'month','op':'eq','value':99}]}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER']);page=browser.new_page(viewport={'width':1280,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8788/almanac/query.html');page.wait_for_function('window.oswLastQueryResult',timeout=60000)
        for q in [query,single,leeuwin,kuro,missing,empty]:assert browser_query(page,q)==native(q)
        expect(page.locator('#query-chart-panels')).to_contain_text('No source samples match')
        browser_query(page,leeuwin);assert page.locator('.chart-sample').count()==12
        assert page.locator('.chart-allowance').count()==12
        page.locator('#query-chart-section').screenshot(path=str(ROOT/'figures/rust-query-leeuwin-chart-review.png'))
        page.locator('.chart-sample').first.focus();page.locator('.chart-sample').first.press('Enter')
        expect(page.locator('#query-detail')).to_contain_text('Leeuwin — January')
        browser_query(page,kuro);assert page.locator('.query-chart-panel').count()==4
        assert page.locator('.chart-sample').count()==64 and page.locator('.chart-missing').count()==5
        assert page.locator('.chart-reading').count()==59
        page.locator('#query-chart-section').screenshot(path=str(ROOT/'figures/rust-query-kuroshio-chart-review.png'))
        page.locator('.chart-missing').first.locator('..').focus();page.locator('.chart-missing').first.locator('..').press('Enter')
        expect(page.locator('#query-detail')).to_contain_text('Unresolved')
        page.set_viewport_size({'width':320,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert page.locator('.query-chart-frame').first.evaluate('(e)=>e.scrollWidth>e.clientWidth')
        browser_query(page,{'collection':'objects','limit':1});assert page.locator('#query-chart-section').is_hidden()
        browser_query(page,{'collection':'width_samples','filters':[{'field':'not_a_field','op':'eq','value':1}]});assert page.locator('#query-chart-section').is_hidden()
        assert not errors;browser.close()
    print('PASS: 105 complete chart marks across seven source panels; stable filtered axes; five separate missing marks; allowance/source fidelity; native/WASM and keyboard/mobile/error behavior')

if __name__=='__main__':main()
