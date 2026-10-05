"""Full-state point oracle, support provenance, and locator-only query controls."""
import copy
import json
import os
import subprocess
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from test_rust_query_browser import native,browser_query
from build_passage_observation_state_audit import build

ROOT=Path(__file__).resolve().parents[1]
def query(state):return {'collection':'passage_samples','spatial':{'state_code':state,'predicate':'locator'},'limit':100}

def main():
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes());audit=build()
    for state in bundle['collections']['states']:
        result=native(query(state['code']));assert result['ok']
        expected={(r['record_id'],r['feature_index']) for r in audit['rows'] if any(m['state_code']==state['code'] for m in r['matches'])}
        actual={(r['id'],m['feature_index']) for r in result['rows'] for m in r['spatial_matches']}
        assert actual==expected,(state['code'],actual,expected)
    result=native(query('SUND'));assert result['total']==3
    assert len(result['map_scene']['features'])==8
    assert all(f['matches_selected_state'] is True for f in result['map_scene']['features'])
    assert {f['label'] for f in result['map_scene']['features']}=={r['mooring_label'] for r in audit['rows']}
    for predicate in ['intersects','within','gateway']:
        bad=query('SUND');bad['spatial']['predicate']=predicate;assert native(bad)['ok'] is False
    with tempfile.TemporaryDirectory() as directory:
        for key in ['mooring_label','deployment_start','source_url','source_file_sha256']:
            bad=copy.deepcopy(bundle);bad['collections']['passage_samples'][0]['map_features'][0][key]='wrong-source-support'
            path=Path(directory)/'bad.json';path.write_text(json.dumps(bad),encoding='utf-8')
            run=subprocess.run([str(ROOT/'rust/osw-query/target/debug/osw-query-cli.exe'),str(path),'-'],input='{}',capture_output=True,text=True)
            assert run.returncode==2 and not run.stdout,(key,run.stderr)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER']);page=browser.new_page(viewport={'width':1280,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/query.html');page.wait_for_function('window.oswLastQueryResult',timeout=60000)
        assert browser_query(page,query('SUND'))==result
        expect(page.locator('#query-state')).to_be_enabled();expect(page.locator('#query-state-mode')).to_have_value('locator')
        assert page.locator('#query-state-mode option[value="within"]').evaluate('(e)=>e.disabled')
        expect(page.locator('#query-map-play')).to_be_hidden();expect(page.locator('#query-map-day')).to_be_hidden()
        page.locator('#query-map-fit').click()
        page.locator('#query-map-section').screenshot(path=str(ROOT/'figures/throughflow-mooring-state-review.png'))
        mark=page.locator('#query-map-features [aria-label^="Lombok east"]').first;mark.focus();mark.press('Enter')
        expect(page.locator('#query-detail')).to_contain_text('Computed state relations (2)')
        expect(page.locator('#query-detail')).to_contain_text('SUND')
        expect(page.locator('#query-detail')).to_contain_text('2004-01-10')
        page.locator('#query-state').select_option('NADR');page.locator('#query-run').click()
        page.wait_for_function('window.oswLastQueryResult?.total===0')
        assert page.evaluate('window.oswLastQueryResult.collection')=='passage_samples'
        page.locator('[data-preset="itf-moorings-sund"]').click()
        page.wait_for_function('window.oswLastQueryResult?.total===3')
        share=page.locator('#query-share').get_attribute('href');page.goto(share)
        page.wait_for_function('window.oswLastQueryResult?.total===3')
        expect(page.locator('#query-state')).to_have_value('SUND')
        page.set_viewport_size({'width':320,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        assert not errors;browser.close()
    print('PASS: 56-state independent point oracle, eight source-bound SUND moorings, locator-only queries, four metadata rejections, native/WASM and keyboard/state/share/mobile access')

if __name__=='__main__':main()
