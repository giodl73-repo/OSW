"""Regional range cards and both runtimes reject invented seasonal support."""
import copy
import json
import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from playwright.sync_api import sync_playwright, expect
from test_rust_query_browser import ROOT, CLI, native, browser_query
from check_balearic_socib_width import ID, AUDIT


def main():
    out = ROOT / '.pytest_cache/balearic-socib-review'
    out.mkdir(parents=True, exist_ok=True)
    bundle = json.loads((ROOT/'almanac/query-data.json').read_bytes())
    q = {'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'balearic'}],'limit':100}
    expected = native(q)
    assert expected['ok'] and expected['total'] == 1
    row = expected['rows'][0]
    assert row['width_range_km'] == [20,35] and row['approximate_width_km'] is None
    assert row['observed_period'] is None and row['calendar_months'] is None
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page = browser.new_page(viewport={'width':1200,'height':950})
        page.emulate_media(reduced_motion='reduce')
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=balearic&phase='+ID)
        page.wait_for_function('window.oswSeasonSnapshot', timeout=60000)
        graph = page.locator('#regional-width-range')
        expect(graph).to_contain_text('20')
        expect(graph).to_contain_text('35')
        expect(graph).to_contain_text('not a 35 km autumn width')
        expect(graph).to_contain_text('0.2 m/s is not an edge cutoff')
        expect(graph.locator('svg')).to_have_attribute('aria-label', row['original_regional_context']['display_aria_label'])
        source = page.get_by_role('link', name='Inspect regional width scope and source').get_attribute('href')
        page.set_viewport_size({'width':320,'height':900})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        graph.screenshot(path=str(out/'range-mobile.png'))
        page.locator('#season-atlas').click()
        page.wait_for_function('document.querySelector("#route-atlas-select").value === "current:balearic"', timeout=60000)
        expect(page.locator('#width-'+ID)).to_contain_text('20')
        expect(page.locator('#width-'+ID)).to_contain_text('35')
        page.goto('http://127.0.0.1:8788/almanac/'+source)
        page.wait_for_function('window.oswSourceQueryResult', timeout=60000)
        assert page.evaluate('window.oswSourceQueryResult.total') > 0
        page.goto('http://127.0.0.1:8788/almanac/query.html')
        page.wait_for_function('window.oswLastQueryResult', timeout=60000)
        assert browser_query(page,q) == expected
        page.route('**/balearic-guard.html', lambda route: route.fulfill(body='<title>SOCIB source guard</title>',content_type='text/html'))
        page.goto('http://127.0.0.1:8788/balearic-guard.html')
        for mode in ['midpoint','calendar','cutoff','missing','rebound']:
            bad = copy.deepcopy(bundle)
            row = next(r for r in bad['collections']['widths'] if r['id'] == ID)
            if mode == 'midpoint': row['approximate_width_km'] = 27.5
            if mode == 'calendar': row['calendar_months'] = [9,10,11]
            if mode == 'cutoff': row['boundary_rule'] = 'GV > 0.2 m/s'
            if mode == 'missing': bad['collections']['widths'].remove(row)
            if mode == 'rebound':
                row['width_range_km'] = [20,40]
                bad['manifest']['input_sha256'][AUDIT] = '0'*64
                row['original_regional_context']['audit_sha256'] = '0'*64
            with TemporaryDirectory(dir=out) as folder:
                file = Path(folder)/'bad.json'
                file.write_text(json.dumps(bad), encoding='utf8')
                result = subprocess.run([str(CLI),str(file),'-'],input='{}',capture_output=True,text=True,encoding='utf8')
                assert result.returncode == 2 and not result.stdout, (mode,result.stderr)
                got = page.evaluate('''async path => {
                  const {instance}=await WebAssembly.instantiate(await (await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports;
                  const b=new Uint8Array(await (await fetch(path)).arrayBuffer()),p=e.osw_alloc(b.length);
                  try {new Uint8Array(e.memory.buffer,p,b.length).set(b);e.osw_load(p,b.length);
                    return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));
                  } finally {e.osw_dealloc(p,b.length);}
                }''','/'+file.relative_to(ROOT).as_posix())
                assert got['ok'] is False, (mode,got)
        assert not errors, errors
        browser.close()
    print('PASS: SOCIB regional range, no invented seasonal widths, atlas/source/mobile navigation, native/WASM parity and five rejection cases')


if __name__ == '__main__':
    main()
