"""Actual Rust/WASM scoped sample queries, provenance binding and card navigation."""
import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile
from playwright.sync_api import sync_playwright, expect
from test_rust_query_browser import native,browser_query
from build_query_width_samples import build

ROOT=Path(__file__).resolve().parents[1]

def main():
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes());samples=bundle['collections']['width_samples']
    assert samples==build(bundle['collections']['diagnostics']) and len(samples)==115
    assert sum(row['value_km'] is None for row in samples)==5
    queries=[{'collection':'width_samples','limit':100},
        {'collection':'width_samples','filters':[{'field':'current_id','op':'eq','value':'leeuwin'}],'sort':{'field':'month'}},
        {'collection':'width_samples','filters':[{'field':'current_id','op':'eq','value':'kuroshio'},{'field':'phase_label','op':'eq','value':'winter'}],'sort':{'field':'longitude_degrees_east'}},
        {'collection':'width_samples','filters':[{'field':'value_km','op':'exists','value':False}]},
        {'collection':'width_samples','filters':[{'field':'current_id','op':'eq','value':'pacific-north-equatorial-countercurrent'}],'sort':{'field':'month'}},
        {'collection':'width_samples','sort':{'field':'value_km','direction':'desc'},'limit':1,'offset':114},
        {'collection':'objects','evidence':'width_samples'},
        {'collection':'objects','filters':[{'field':'id','op':'eq','value':'current:leeuwin'}]}]
    results=[native(q) for q in queries];assert all(r['ok'] for r in results)
    assert results[0]['total']==115 and results[0]['map_scene']['mapped_objects']==27 and results[0]['map_scene']['unmapped_objects']==88
    assert results[1]['total']==12 and [r['month'] for r in results[1]['rows']]==list(range(1,13))
    assert results[2]['total']==16 and results[3]['total']==5 and results[4]['total']==12
    assert results[5]['rows'][0]['value_km'] is None and results[6]['total']==5
    with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as temp:
        path=Path(temp)/'bad-bundle.json';exe=str(ROOT/'rust/osw-query/target/debug/osw-query-cli.exe')
        for key,value in [('value_km',9999),('month',12),('metric','whole ocean width'),('plot_reading_interval_km',[1,2]),('is_confidence_interval',True),('entity_id','current:gulf-stream-system'),('sample_family','other'),('phase_path','/months/1')]:
            bad=copy.deepcopy(bundle);bad['collections']['width_samples'][0][key]=value;path.write_text(json.dumps(bad),encoding='utf-8')
            result=subprocess.run([exe,str(path),'-'],input='{}',capture_output=True,text=True,encoding='utf-8')
            assert result.returncode==2 and not result.stdout and any(message in result.stderr.lower() for message in ['width sample','scoped samples','another object','monthly sample']), (key,result.stderr)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER']);page=browser.new_page(viewport={'width':1280,'height':1100});errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto('http://127.0.0.1:8788/almanac/query.html');page.wait_for_function('window.oswLastQueryResult',timeout=60000)
        for q,result in zip(queries,results):assert browser_query(page,q)==result
        page.locator('#query-rows button').first.click()
        link=page.get_by_role('link',name='Query scoped width samples');expect(link).to_have_count(1);link.click()
        page.wait_for_function('window.oswLastQueryResult?.collection==="width_samples"',timeout=60000)
        assert page.evaluate('window.oswLastQueryResult.total')==12
        assert page.locator('#query-sample-current').input_value()=='leeuwin'
        page.locator('#query-sort').select_option('value_km');page.evaluate('window.oswLastQueryResult=null');page.locator('#query-run').click()
        page.wait_for_function('window.oswLastQueryResult?.total===12 && document.querySelector("#query-json").value.includes("value_km")')
        assert all(row['current_id']=='leeuwin' for row in page.evaluate('window.oswLastQueryResult.rows'))
        page.locator('#query-sample-month').select_option('1');page.evaluate('window.oswLastQueryResult=null');page.locator('#query-run').click()
        page.wait_for_function('window.oswLastQueryResult?.total===1')
        assert page.evaluate('window.oswLastQueryResult.rows[0].value_km')==97
        # Unsupported or duplicate structured constraints must survive form use.
        for filters in [[{'field':'month','op':'eq','value':13}],
                        [{'field':'month','op':'eq','value':1},{'field':'month','op':'eq','value':7}],
                        [{'field':'month','op':'eq','value':'1'}]]:
            q={'collection':'width_samples','filters':filters};expected=native(q)
            assert browser_query(page,q)==expected
            expect(page.locator('#query-sample-extra')).to_be_visible()
            page.locator('#query-sort').select_option('label');page.evaluate('window.oswLastQueryResult=null');page.locator('#query-run').click()
            page.wait_for_function('window.oswLastQueryResult && document.querySelector("#query-json").value.includes("label")')
            assert page.evaluate('window.oswLastQueryResult.total')==expected['total']==0
        page.locator('[data-preset="leeuwin-samples"]').click()
        page.wait_for_function('window.oswLastQueryResult?.collection==="width_samples" && window.oswLastQueryResult.rows[0]?.month===1')
        assert page.locator('#query-map-section').is_hidden()
        expect(page.locator('#query-rows')).to_contain_text('plot reading 94–100 km')
        page.locator('#query-rows button').first.click()
        expect(page.locator('#query-detail')).to_contain_text('not confidence intervals or measurement uncertainty')
        expect(page.locator('#query-detail')).to_contain_text('Historical period labels differ')
        expect(page.locator('#query-detail')).to_contain_text('scientific review pending')
        page.screenshot(path=str(ROOT/'figures/rust-query-width-samples-review.png'))
        page.get_by_role('button',name='Inspect parent diagnostic').click()
        expect(page.locator('#query-detail')).to_contain_text('diagnostic:leeuwin-monthly-width')
        browser_query(page,queries[3]);page.locator('#query-rows button').first.click()
        expect(page.locator('#query-detail')).to_contain_text('Unresolved')
        expect(page.locator('#query-detail')).to_contain_text('Calendar months for this source season are unresolved')
        page.set_viewport_size({'width':320,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert not errors
        browser.close()
    print('PASS: 115 original scoped samples; five missing readings retained; native/WASM queries and null-last ordering; source/value/month/metric/interval binding; current-card links and mobile')

if __name__=='__main__':main()
