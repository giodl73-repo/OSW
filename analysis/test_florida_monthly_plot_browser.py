"""Graph monthly readings: source binding, charts, playback and reduced motion."""
import copy,json,os,subprocess,tempfile
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect
from test_rust_query_browser import CLI,native,browser_query
ROOT=Path(__file__).resolve().parents[1]
QUERY={'collection':'width_samples','filters':[{'field':'current_id','op':'eq','value':'florida'}],'sort':{'field':'month','direction':'asc'},'limit':100}
def main():
    result=native(QUERY);assert result['ok'] and result['total']==12,result
    assert len(result['chart_scene']['panels'])==1
    assert result['chart_scene']['panels'][0]['title'].startswith('Florida Current')
    assert [r['month'] for r in result['rows']]==list(range(1,13))
    assert all(r['observation_date'] is None and r['year'] is None and r['annual_width_range_km'] is None for r in result['rows'])
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    with tempfile.TemporaryDirectory() as directory:
        for key,value in [('value_km',99),('latitude_degrees_north',0),('annual_width_range_km',[53,64])]:
            bad=copy.deepcopy(bundle);next(r for r in bad['collections']['width_samples'] if r['current_id']=='florida')[key]=value
            path=Path(directory)/'bad.json';path.write_text(json.dumps(bad),encoding='utf-8')
            run=subprocess.run([str(CLI),str(path),'-'],input='{}',capture_output=True,text=True)
            assert run.returncode==2 and not run.stdout,(key,run.stderr)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'));page=browser.new_page(viewport={'width':1280,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/query.html');page.wait_for_function('window.oswLastQueryResult',timeout=60000)
        assert browser_query(page,QUERY)==result
        chart=page.locator('.query-chart-panel');expect(chart).to_contain_text('2005-2006 monthly surface-jet')
        expect(chart.locator('.chart-sample')).to_have_count(12)
        controls=chart.locator('.chart-playback');select=controls.locator('select')
        expect(chart.locator('.chart-selected-reading')).to_contain_text('January')
        controls.get_by_role('button',name='Next month',exact=True).click();expect(chart.locator('.chart-selected-reading')).to_contain_text('February')
        controls.get_by_role('button',name='Play monthly readings',exact=True).click()
        page.wait_for_function('document.querySelector(".chart-selected-reading").textContent.includes("March")')
        controls.get_by_role('button',name='Pause monthly readings',exact=True).click()
        page.emulate_media(reduced_motion='reduce');expect(controls.get_by_role('button',name='Play monthly readings',exact=True)).to_be_disabled()
        controls.get_by_role('button',name='Next month',exact=True).click();expect(chart.locator('.chart-selected-reading')).to_contain_text('April')
        controls.get_by_role('button',name='Inspect selected month',exact=True).click();expect(page.locator('#query-detail')).to_contain_text('April')
        share=page.locator('#query-share').get_attribute('href');page.goto(share);page.wait_for_function('window.oswLastQueryResult?.total===12',timeout=60000)
        expect(page.locator('#query-detail')).to_contain_text('April')
        expect(chart.locator('.chart-selected-reading')).to_contain_text('April')
        chart.screenshot(path=str(ROOT/'figures/florida-monthly-width-chart-review.png'))
        page.set_viewport_size({'width':320,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        # Card link reaches exactly these samples and no unrelated query.
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Aflorida#route-atlas')
        record=page.locator('.atlas-width-record[data-measurement-id="florida-hf-radar-width-statistics-2005-2006"]');record.locator('summary').click();record.get_by_role('link',name='Monthly width chart').click()
        page.wait_for_function('window.oswLastQueryResult?.total===12',timeout=60000)
        assert page.evaluate('window.oswLastQueryResult.rows.every(r=>r.current_id==="florida")')
        assert not errors,errors;browser.close()
    print('PASS: Florida source-bound monthly samples, three loader rejections, native/WASM charts, playback/pause/reduced-motion/manual controls, share/reload and mobile/card links')
if __name__=='__main__':main()
