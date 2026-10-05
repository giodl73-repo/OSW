"""Source integrity, bounded connectivity and accessible network query navigation."""
import copy
import json
import os
import subprocess
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from test_rust_query_browser import native, browser_query

ROOT = Path(__file__).resolve().parents[1]
NETWORK = 'flow-network:indonesian-throughflow'
QUERY = {'collection':'flow_networks', 'network_path':{'network_id':NETWORK,
         'from_id':'flow-node:itf:pacific', 'to_id':'flow-node:itf:indian', 'max_hops':8}}

def main():
    result = native(QUERY)
    assert len(result['network_paths']['paths']) == 5
    assert result['network_paths']['length_km'] is None
    limited = copy.deepcopy(QUERY); limited['network_path']['max_hops'] = 1
    assert native(limited)['network_paths']['hop_limit_reached']
    samples = {'collection':'passage_samples'}
    assert len(native(samples)['map_scene']['features']) == 8
    bundle = json.loads((ROOT/'almanac/query-data.json').read_bytes())
    with tempfile.TemporaryDirectory() as directory:
        for mutation in ['source','edge','transport','geometry','owner','orphan']:
            data = copy.deepcopy(bundle); c = data['collections']
            if mutation == 'source': c['flow_networks'][0]['source_json'] += ' '
            elif mutation == 'edge': c['flow_network_edges'][0]['to_id'] = 'unknown'
            elif mutation == 'transport': c['passage_samples'][0]['value'] = 999
            elif mutation == 'geometry': c['passage_samples'][0]['map_features'][0]['geometry']['coordinates'][0] += 1
            elif mutation == 'owner':
                next(r for r in c['objects'] if r['id']=='current:indonesian-throughflow')['flow_network_ids'] = []
            else: c['flow_network_nodes'][0]['network_id'] = 'unknown'
            path = Path(directory)/'changed.json'; path.write_text(json.dumps(data),encoding='utf-8')
            run = subprocess.run([str(ROOT/'rust/osw-query/target/debug/osw-query-cli.exe'), str(path), '-'], input='{}',capture_output=True,text=True)
            assert run.returncode == 2 and not run.stdout, (mutation,run.stderr)
    for key,value in [('max_hops',0),('max_hops',17),('from_id','unknown'),('network_id','unknown')]:
        bad = copy.deepcopy(QUERY); bad['network_path'][key] = value
        assert native(bad)['ok'] is False
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page = browser.new_page(viewport={'width':1280,'height':1000}); errors=[]
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/query.html')
        page.wait_for_function('window.oswLastQueryResult',timeout=60000)
        assert browser_query(page,QUERY) == result
        expect(page.locator('#query-status')).to_contain_text('5 conceptual connections')
        page.locator('#query-run').click()
        expect(page.locator('#query-status')).to_contain_text('5 conceptual connections')
        page.locator('#query-rows button').first.click()
        expect(page.locator('#query-detail')).to_contain_text('All twelve named nodes')
        page.screenshot(path=str(ROOT/'figures/indonesian-throughflow-network-review.png'),full_page=True)
        node = page.locator('#query-detail svg [role="button"]').first
        node.focus();node.press('Enter')
        expect(page.locator('#query-detail')).to_contain_text('Back to passage network')
        assert browser_query(page,samples) == native(samples)
        page.locator('#query-rows button').first.click()
        expect(page.locator('#query-detail')).to_contain_text('integration')
        page.set_viewport_size({'width':320,'height':900})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        assert not errors;browser.close()
    print('PASS: five conceptual paths, eight moorings, six source/owner rejections, bounded query errors, native/WASM parity and keyboard navigation')

if __name__ == '__main__': main()
