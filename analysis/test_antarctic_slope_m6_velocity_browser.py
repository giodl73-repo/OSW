"""Signed source-bound native/WASM velocity charts and mobile inspection."""
import json
import os
from urllib.parse import quote
from playwright.sync_api import sync_playwright, expect
from test_rust_query_browser import ROOT, native, browser_query


def main():
    query={'collection':'current_velocity_samples','limit':5}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':320,'height':900})
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/query.html?q='+quote(json.dumps(query)))
        page.wait_for_function('window.oswLastQueryResult?.total===61',timeout=90000)
        actual=page.evaluate('oswLastQueryResult');assert actual==native(query)
        assert page.locator('#query-chart-panels article').count()==4
        assert page.locator('#query-chart-panels [data-sample]').count()==122
        assert page.locator('#query-chart-legend').is_hidden()
        assert page.locator('#chart-title').inner_text()=='Observed current velocity'
        page.locator('#query-chart-panels button').nth(1).click()
        page.wait_for_timeout(1150)
        assert page.locator('#query-chart-panels select').first.evaluate('(e)=>e.selectedIndex')==1
        page.emulate_media(reduced_motion='reduce')
        expect(page.locator('#query-chart-panels button').nth(1)).to_be_disabled()
        page.locator('#query-chart-panels select').first.select_option(index=2)
        assert page.locator('#query-chart-panels .velocity-selected').count()==4
        assert actual['map_scene']['mapped_objects']==1
        assert actual['chart_scene']['panels'][0]['y_domain_cm_s'][0]<0
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#query-chart-panels button').first.click()
        expect(page.locator('#query-detail')).to_contain_text('M6 228 m')
        page.locator('#query-chart-panels').screenshot(path=str(ROOT/'.pytest_cache/m6-velocity-mobile.png'))
        filtered={**query,'filters':[{'field':'series_kind','op':'eq','value':'seasonal_composite'},{'field':'month','op':'eq','value':2}]}
        result=browser_query(page,filtered);assert result==native(filtered)
        assert result['total']==1 and result['rows'][0]['contributing_years']==[2018,2019,2020]
        assert result['chart_scene']['panels'][0]['y_domain_cm_s']==actual['chart_scene']['panels'][2]['y_domain_cm_s']
        rejections=page.evaluate('''async()=>{
          const original=await(await fetch('/almanac/query-data.json')).json(),results=[];
          const mutations=[b=>b.collections.current_velocity_samples[0].eastward_mean_cm_s=0,
            b=>b.collections.current_velocity_samples[0].nominal_depth_m=506,
            b=>b.collections.current_velocity_samples[0].hourly_coverage_fraction=1,
            b=>b.collections.current_velocity_samples[50].contributing_years.push(2017),
            b=>b.collections.objects.find(r=>r.id==='current:antarctic-slope').velocity_sample_ids=[],
            b=>delete b.collections.current_velocity_samples];
          for(const mutate of mutations){const b=structuredClone(original);mutate(b);
            const {instance}=await WebAssembly.instantiate(await(await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports,
              data=new TextEncoder().encode(JSON.stringify(b)),ptr=e.osw_alloc(data.length);
            try{new Uint8Array(e.memory.buffer,ptr,data.length).set(data);e.osw_load(ptr,data.length);
              results.push(JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len()))));
            }finally{e.osw_dealloc(ptr,data.length);}
          }return results;
        }''')
        assert all(r['ok'] is False for r in rejections),rejections
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Aantarctic-slope#route-atlas')
        atlas_link=page.get_by_role('link',name='Observed M6 velocity · monthly and seasonal charts →')
        atlas_link.wait_for(state='visible',timeout=90000)
        atlas_link.click()
        page.wait_for_function('window.oswLastQueryResult?.total===61',timeout=90000)
        assert page.locator('#chart-title').inner_text()=='Observed current velocity'
        assert not errors,errors
        browser.close()
    print('PASS: 61 source-bound velocity rows, fixed signed axes, native/WASM parity, mobile and February coverage')


if __name__=='__main__':main()
