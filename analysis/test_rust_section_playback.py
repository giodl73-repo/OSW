"""Recorded section playback preserves filters, receipts, dates and map scale."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from test_rust_query_browser import native,browser_query

ROOT=Path(__file__).resolve().parents[1]

def main():
    base={'collection':'width_samples','filters':[
        {'field':'sample_family','op':'eq','value':'gulf_stream_dated_half_peak_section'},
        {'field':'year','op':'eq','value':2026},
        {'field':'metric','op':'eq','value':'meridional_half_peak_eastward_velocity_section_span'},
        {'field':'year','op':'eq','value':2026}], 'sort':{'field':'value_km','direction':'desc'},'limit':1}
    scene=native(base)['map_scene']
    assert scene['recorded_days']==['2026-09-18','2026-09-24','2026-09-25','2026-09-26','2026-09-27']
    assert len(scene['features'])==5 and scene['display_bounds'][0]==scene['display_bounds'][2]==110
    all_days=native({'collection':'width_samples','limit':1})['map_scene']['recorded_days']
    assert len(all_days)==17 and '2026-01-15' not in all_days
    selected={**base,'filters':base['filters']+[{'field':'observation_date','op':'eq','value':'2026-09-24'}]}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page=browser.new_page(viewport={'width':1280,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/query.html')
        page.wait_for_function('window.oswLastQueryResult',timeout=60000)
        assert browser_query(page,selected)==native(selected)
        button=page.locator('#query-map-play-samples');expect(button).to_be_visible()
        button.focus();button.press('Enter')
        expect(button).to_have_attribute('aria-pressed','true')
        page.wait_for_function('document.querySelector("#query-map-time").textContent.includes("Recorded section day: 2026-09-24")')
        button.click();expect(button).to_have_attribute('aria-pressed','false')
        page.wait_for_timeout(1200)
        assert page.evaluate('window.oswLastQueryResult.rows[0].observation_date')=='2026-09-24'
        page.evaluate('''() => {
          let cached=window.oswLastQueryResult;window.sectionFrames=[];
          Object.defineProperty(window,'oswLastQueryResult',{configurable:true,get:()=>cached,set:value=>{
            cached=value;if(value?.collection==='width_samples')queueMicrotask(()=>window.sectionFrames.push({
              result:value,query:JSON.parse(document.querySelector('#query-json').value),view:document.querySelector('#query-map').getAttribute('viewBox')
            }));
          }});
        }''')
        button.click();expect(button).to_have_attribute('aria-pressed','true')
        page.wait_for_function('window.sectionFrames.length===4',timeout=15000)
        expect(button).to_have_attribute('aria-pressed','false',timeout=10000)
        frames=page.evaluate('window.sectionFrames')
        assert [f['result']['rows'][0]['observation_date'] for f in frames]==scene['recorded_days'][1:]
        assert len({f['view'] for f in frames})==1
        for frame in frames:
            assert all(f in frame['query']['filters'] for f in base['filters'])
            assert frame['query']['sort']==base['sort'] and frame['result']==native(frame['query'])
            assert frame['query']['filters'].count({'field':'year','op':'eq','value':2026})==2
            assert len(frame['result']['map_scene']['features'])==1
        expect(page.locator('#query-map-time')).to_contain_text('2026-09-27')
        expect(page.locator('#query-map-sample-playback-note')).to_contain_text('no interpolation')
        page.locator('#query-map-section').screenshot(path=str(ROOT/'figures/rust-query-section-playback-review.png'))
        duplicate={**base,'filters':base['filters']+[
            {'field':'observation_date','op':'eq','value':'2026-09-26'},
            {'field':'observation_date','op':'eq','value':'2026-09-26'}]}
        browser_query(page,duplicate);page.evaluate('window.sectionFrames=[]')
        button.click();expect(button).to_have_attribute('aria-pressed','true')
        expect(button).to_have_attribute('aria-pressed','false',timeout=10000)
        frames=page.evaluate('window.sectionFrames');assert len(frames)==1
        assert frames[0]['query']['filters'].count({'field':'observation_date','op':'eq','value':'2026-09-26'})==2
        # A new query cancels playback, including a pending inventory request.
        browser_query(page,selected);button.click()
        browser_query(page,{'collection':'objects','filters':[{'field':'id','op':'eq','value':'current:gulf-stream-system'}]})
        expect(button).to_be_hidden();page.wait_for_timeout(1200)
        assert page.evaluate('window.oswLastQueryResult.collection')=='objects'
        page.set_viewport_size({'width':320,'height':900})
        browser_query(page,selected);expect(button).to_be_visible()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert not errors;browser.close()
    print('PASS: filtered recorded-day inventory, exact source frames, fixed viewport, keyboard play/pause, duplicate filter retention, query cancellation and mobile')

if __name__=='__main__':main()
