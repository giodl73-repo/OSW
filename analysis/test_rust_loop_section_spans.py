"""Width-family binding, native/WASM maps and recorded-day playback."""
import copy
import json
import os
import subprocess
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from test_rust_query_browser import native,browser_query

ROOT=Path(__file__).resolve().parents[1]
QUERY={'collection':'width_samples','filters':[{'field':'sample_family','op':'eq','value':'loop_dated_half_peak_section'}],'sort':{'field':'observation_date'},'limit':100}

def main():
    result=native(QUERY);assert result['ok'] and result['total']==10
    assert len(result['map_scene']['features'])==10
    assert len(result['chart_scene']['panels'])==2
    assert all(p['x_field']=='observation_date' for p in result['chart_scene']['panels'])
    for feature in result['map_scene']['features']:
        points=feature['source_sample']['coordinates']
        assert len(points)==2 and all(p[1]==21.875 for p in points) and points[0][0]<points[1][0]
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    with tempfile.TemporaryDirectory() as directory:
        for mutation in ['latitude','value','boundary','raw_source','annual','owner']:
            bad=copy.deepcopy(bundle);row=next(r for r in bad['collections']['width_samples'] if r['sample_family']=='loop_dated_half_peak_section')
            if mutation=='latitude':row['latitude_degrees_north']=0
            elif mutation=='value':row['value_km']=999
            elif mutation=='boundary':row['source_sample']['nominal']['west_boundary']['longitude']+=1
            elif mutation=='owner':next(o for o in bad['collections']['objects'] if o['id']=='current:loop')['width_sample_ids'].remove(row['id'])
            elif mutation=='annual':row['annual_width_range_km']=[70,120]
            else:next(r for r in bad['collections']['diagnostics'] if r['id']==row['diagnostic_id'])['source_json']+=' '
            path=Path(directory)/'bad.json';path.write_text(json.dumps(bad),encoding='utf-8')
            check=subprocess.run([str(ROOT/'rust/osw-query/target/debug/osw-query-cli.exe'),str(path),'-'],input='{}',capture_output=True,text=True)
            assert check.returncode==2 and not check.stdout,(mutation,check.stderr)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER']);page=browser.new_page(viewport={'width':1280,'height':1050})
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/query.html');page.wait_for_function('window.oswLastQueryResult',timeout=60000)
        assert browser_query(page,QUERY)==result
        expect(page.locator('#query-chart-panels')).to_contain_text('Loop inflow')
        page.locator('#query-chart-section').screenshot(path=str(ROOT/'figures/loop-current-section-spans-chart-review.png'))
        page.locator('#query-map-fit').click()
        page.locator('#query-map-section').screenshot(path=str(ROOT/'figures/loop-current-section-spans-review.png'))
        page.locator('#query-rows button').first.click()
        expect(page.locator('#query-detail')).to_contain_text('Section latitude (degrees north)')
        expect(page.locator('#query-detail')).to_contain_text('21.875')
        expect(page.locator('#query-detail')).to_contain_text('neither confidence intervals nor measurement uncertainty')
        page.get_by_role('button',name='Inspect parent diagnostic').click()
        expect(page.locator('#query-detail')).to_contain_text('5 recorded-day local section spans')
        browser_query(page,QUERY);page.locator('#query-map-play-samples').click()
        expect(page.locator('#query-sample-day')).to_have_value('2026-09-25',timeout=10000)
        expect(page.locator('#query-map-play-samples')).to_have_attribute('aria-pressed','false')
        assert page.evaluate('window.oswLastQueryResult.total')==2
        page.emulate_media(reduced_motion='reduce');expect(page.locator('#query-map-play-samples')).to_be_disabled()
        page.set_viewport_size({'width':320,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        assert not errors;browser.close()
    print('PASS: ten paired source-bound spans; two product panels; six loader rejections; native/WASM maps, parent cards, recorded playback and reduced-motion/mobile')

if __name__=='__main__':main()
