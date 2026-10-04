"""Dated section spans, elapsed calendar spacing and distinct sensitivity ranges."""
import copy
from datetime import date
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
from playwright.sync_api import sync_playwright,expect
from test_rust_query_browser import native,browser_query

ROOT=Path(__file__).resolve().parents[1]
def source_readback_matches(saved,readback,path=()):
    """Allow only last-bit f64 JSON readback in derived speeds/edge latitudes.

    Original bundle payloads are checked exactly by projection tests. Dates,
    rounded widths, thresholds, grid brackets and flags remain exact here.
    Latitude tolerance 1e-14 degree; velocity tolerance 1e-15 m/s.
    """
    if type(saved) is not type(readback):return False
    if isinstance(saved,dict):return saved.keys()==readback.keys() and all(source_readback_matches(saved[k],readback[k],path+(k,)) for k in saved)
    if isinstance(saved,list):return len(saved)==len(readback) and all(source_readback_matches(a,b,path+(i,)) for i,(a,b) in enumerate(zip(saved,readback)))
    if isinstance(saved,float) and path:
        if path[-1] in ('eastward_m_s','peak_eastward_m_s'):return math.isclose(saved,readback,rel_tol=0,abs_tol=1e-15)
        if len(path)>1 and path[-1]=='latitude' and path[-2] in ('south_boundary','north_boundary'):return math.isclose(saved,readback,rel_tol=0,abs_tol=1e-14)
    return saved==readback
def main():
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    original=json.loads((ROOT/'research/gulf-stream-section-width-series.json').read_bytes())
    rows=[r for r in bundle['collections']['width_samples'] if r['sample_family']=='gulf_stream_dated_half_peak_section']
    assert len(rows)==17 and all(r['current_id']=='gulf-stream-system' for r in rows)
    query={'collection':'width_samples','filters':[{'field':'sample_family','op':'eq','value':'gulf_stream_dated_half_peak_section'}],'sort':{'field':'observation_date'},'limit':100}
    result=native(query);panel=result['chart_scene']['panels'][0];points=panel['points']
    scene=result['map_scene'];assert scene['mapped_objects']==17 and scene['inspection_collection']=='width_samples'
    assert len(native({**query,'limit':1})['map_scene']['features'])==17
    for row,feature in zip(result['rows'],scene['features']):
        nominal=row['source_sample']['nominal'];south=nominal['south_boundary']['latitude'];north=nominal['north_boundary']['latitude']
        assert feature['primitive']['d']==f'M 110.00000 {90-south:.5f} L 110.00000 {90-north:.5f} '
        assert feature['source_sample']['coordinates']==[[-70,south],[-70,north]]
        assert feature['owner_entity_id']=='current:gulf-stream-system' and feature['entity_id']==row['id']
        assert feature['source_subset_sha256']==row['source_sample']['source_subset_sha256']
        assert feature['source_algorithm']==row['source_algorithm'] and feature['observation_date']==row['observation_date']
    assert native({'collection':'width_samples','limit':1})['map_scene']['unmapped_objects']==88
    assert native({'collection':'width_samples','filters':[{'field':'current_id','op':'eq','value':'leeuwin'}]})['map_scene'] is None
    assert result['total']==17 and panel['x_field']=='observation_date' and len(points)==17
    assert len({r['source_algorithm'] for r in rows})==3
    for row,frame,point in zip(result['rows'],original['frames'],points):
        assert source_readback_matches(frame,row['source_sample']) and row['value_km']==frame['approximate_section_span_km']
        assert point['x_value']==date.fromisoformat(frame['date']).toordinal()-1
        assert point['diagnostic_sensitivity_interval_km']==frame['threshold_sensitivity_span_km']
        assert point['primitive']['interval_y'] is None and point['primitive']['sensitivity_y'] is not None
        assert row['sampling_bracket_interval_km']==frame['nominal']['grid_bracket_span_km']
        assert row['measurement_uncertainty_interval_km'] is None and not row['width_rank_eligible']
    assert points[-1]['x_value']-points[-2]['x_value']==1
    assert points[12]['x_value']-points[11]['x_value']>250
    for tick in panel['x_ticks']:assert tick['value']==date.fromisoformat(tick['label']).toordinal()-1
    day={**query,'filters':query['filters']+[{'field':'observation_date','op':'eq','value':'2026-09-27'}]}
    one=native(day);assert one['total']==1 and one['chart_scene']['panels'][0]['x_domain']==panel['x_domain']
    assert one['chart_scene']['panels'][0]['points'][0]==points[-1]
    with tempfile.TemporaryDirectory() as temp:
        path=Path(temp)/'bad.json'
        for key,value in [('observation_date','2026-09-26'),('year',2025),('month',1),('source_algorithm','invented'),('diagnostic_sensitivity_interval_km',[0,9999]),('sampling_bracket_interval_km',[0,9999]),('resolution_review_required',False),('metric','flow_normal_width')]:
            bad=copy.deepcopy(bundle);row=next(r for r in bad['collections']['width_samples'] if r['observation_date']=='2026-09-27');row[key]=value
            path.write_text(json.dumps(bad),encoding='utf-8')
            p=subprocess.run([str(ROOT/'rust/osw-query/target/debug/osw-query-cli.exe'),str(path),'-'],input='{}',text=True,capture_output=True)
            assert p.returncode==2 and not p.stdout,(key,p.stdout,p.stderr)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER']);page=browser.new_page(viewport={'width':1280,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/query.html');page.wait_for_function('window.oswLastQueryResult',timeout=60000)
        for q in [query,day]:assert browser_query(page,q)==native(q)
        page.locator('[data-preset="gulf-width-samples"]').click()
        expect(page.locator('#query-page')).to_contain_text('17 of 17')
        assert page.locator('#query-map-features path').count()==17
        assert 4<=float(page.locator('#query-map').get_attribute('viewBox').split()[2])<10
        expect(page.locator('#query-map-play')).to_be_hidden()
        expect(page.locator('#query-map-play-months')).to_be_hidden()
        expect(page.locator('#query-map-day')).to_be_hidden()
        expect(page.locator('#query-map-time')).to_contain_text('not current axes')
        mark=page.locator('#query-map-features path').last;mark.focus();mark.press('Enter')
        expect(page.locator('#query-detail')).to_contain_text('Observation day: 2026-09-27')
        expect(page.locator('#query-detail a',has_text='Map this local section span')).to_be_visible()
        page.locator('#query-map-section').screenshot(path=str(ROOT/'figures/rust-query-dated-section-map-review.png'))
        assert page.locator('.chart-sensitivity').count()==17 and page.locator('.chart-allowance').count()==0
        expect(page.locator('#query-chart-section')).to_contain_text('RADS 4.7.0, RADS 4.7.1, RADS 4.8.1')
        page.locator('#query-chart-section').screenshot(path=str(ROOT/'figures/rust-query-dated-width-chart-review.png'))
        page.locator('.chart-sample').last.focus();page.locator('.chart-sample').last.press('Enter')
        expect(page.locator('#query-detail')).to_contain_text('Observation day: 2026-09-27')
        expect(page.locator('#query-detail')).to_contain_text('Resolution review flag: yes')
        expect(page.locator('#query-detail')).to_contain_text('not a monthly mean')
        page.locator('#query-detail').screenshot(path=str(ROOT/'figures/rust-query-dated-width-card-review.png'))
        page.locator('#query-sample-year').select_option('2026');page.evaluate('window.oswLastQueryResult=null');page.locator('#query-run').click()
        page.wait_for_function('window.oswLastQueryResult?.total===5')
        page.locator('#query-sample-day').select_option('2026-09-27');page.evaluate('window.oswLastQueryResult=null');page.locator('#query-run').click()
        page.wait_for_function('window.oswLastQueryResult?.total===1')
        page.locator('#query-sort').select_option('value_km');page.evaluate('window.oswLastQueryResult=null');page.locator('#query-run').click()
        page.wait_for_function('window.oswLastQueryResult?.total===1')
        q=json.loads(page.locator('#query-json').input_value());assert {'field':'year','op':'eq','value':2026} in q['filters'] and {'field':'observation_date','op':'eq','value':'2026-09-27'} in q['filters']
        assert page.locator('#query-map-features path').count()==1
        page.locator('#query-map-features path').focus();page.locator('#query-map-features path').press('Enter')
        href=page.locator('#query-detail a',has_text='Map this local section span').get_attribute('href')
        page.goto(href)
        page.wait_for_function('window.oswLastQueryResult?.total===1')
        assert page.locator('#query-map-features path').count()==1
        assert float(page.locator('#query-map').get_attribute('viewBox').split()[2])==4
        page.set_viewport_size({'width':320,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        browser_query(page,{'collection':'objects','filters':[{'field':'id','op':'eq','value':'current:gulf-stream-system'}]})
        expect(page.locator('#query-map-play')).to_be_visible()
        assert not errors;browser.close()
    print('PASS: 17 source-bound dated section samples/maps; complete pre-pagination geometry; exact endpoints and source receipts; elapsed-day charts; eight source mutation rejections; native/WASM; local fit/card navigation and year/day controls; keyboard/mobile')

if __name__=='__main__':main()
