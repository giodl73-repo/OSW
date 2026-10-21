"""Source-defined core reaches atlas, inspector and both query runtimes."""
from query_packet import read_bundle_bytes
import copy
import hashlib
import json
import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote
from playwright.sync_api import sync_playwright, expect
from check_atlantic_seuc_core_width import ROOT, AUDIT, ID, OWNER
from test_rust_query_browser import CLI, BASE, native


def corrupt(bundle, mode):
    bad = copy.deepcopy(bundle)
    row = next(r for r in bad['collections']['widths'] if r['id'] == ID)
    receipt = bad['manifest']['seasons_receipts']['widths']
    source = json.loads(receipt['source_json'])
    original = next(r for r in source['measurements'] if r['id'] == ID)
    changes = {'midpoint': ('approximate_width_km', 110),
               'range': ('width_range_km', [100, 120]),
               'layer': ('fixed_layer_bounds_m', [150, 200]),
               'season': ('calendar_months', [1, 7]),
               'owner': ('current_id', 'south-equatorial-undercurrent'),
               'context': ('original_regional_context', {})}
    if mode in changes:
        key, value = changes[mode]
        row[key] = value
        original[key] = copy.deepcopy(value)
    elif mode == 'missing':
        bad['collections']['widths'].remove(row)
        source['measurements'].remove(original)
        bad['manifest']['input_sha256'].pop(AUDIT)
    else:
        bad['manifest']['input_sha256'][AUDIT] = '0'*64
    receipt['source_json'] = json.dumps(source, ensure_ascii=False)
    receipt['source_sha256'] = hashlib.sha256(receipt['source_json'].encode()).hexdigest()
    bad['manifest']['input_sha256'][receipt['source_file']] = receipt['source_sha256']
    return bad


def main():
    out = ROOT/'.pytest_cache/atlantic-seuc-core-review'
    out.mkdir(parents=True, exist_ok=True)
    query = {'collection': 'widths', 'filters': [{'field': 'id', 'op': 'eq', 'value': ID}]}
    expected = native(query)
    assert expected['total'] == 1 and expected['rows'][0]['approximate_width_km'] == 120
    bundle = json.loads(read_bundle_bytes(ROOT/'almanac/query-data.json'))
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page = browser.new_page(viewport={'width': 1280, 'height': 1000})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(f'http://127.0.0.1:8788/almanac/seasons.html?current={OWNER}&phase={ID}')
        page.wait_for_function('window.oswSeasonPlan?.current_id === "'+OWNER+'"', timeout=90000)
        chart = page.locator('#regional-width-range .original-regional-width svg')
        expect(chart).to_be_visible()
        assert chart.locator('circle').count() == 1
        assert '120 km' in page.locator('#season-value').inner_text()
        assert '100 km' in chart.get_attribute('aria-label')
        assert page.locator('#season-play').is_disabled()
        assert page.evaluate('oswSeasonPlan.eligible_indices') == []
        assert page.locator('#season-section-locator').is_hidden()
        page.set_viewport_size({'width': 320, 'height': 900})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.locator('#regional-width-range').screenshot(path=str(out/'core-mobile.png'))
        page.goto(f'http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3A{OWNER}#route-atlas')
        atlas = page.locator('#route-atlas-preview .original-regional-width')
        expect(atlas).to_be_visible(timeout=90000)
        expect(atlas).to_contain_text('20 cm/s core')
        atlas.get_by_role('link', name='Inspect regional width scope and source', exact=True).click()
        page.wait_for_function('window.oswSourceQueryResult?.ok', timeout=90000)
        assert page.evaluate('oswSourceQueryResult.document') == AUDIT
        page.goto(BASE+'?q='+quote(json.dumps(query)))
        page.wait_for_function('window.oswLastQueryResult', timeout=90000)
        assert page.evaluate('oswLastQueryResult') == expected
        page.locator('#query-rows tr button').first.click()
        expect(page.locator('#query-detail h3')).to_have_text('Atlantic South Equatorial Undercurrent')
        expect(page.locator('#query-detail')).to_contain_text(ID)
        for mode in ['midpoint', 'range', 'layer', 'season', 'owner', 'context', 'missing', 'pin']:
            with TemporaryDirectory(dir=out) as directory:
                path = Path(directory)/'bad.json'
                path.write_text(json.dumps(corrupt(bundle, mode), ensure_ascii=False), encoding='utf8')
                result = subprocess.run([str(CLI), str(path), '-'], input='{}', capture_output=True, text=True, encoding='utf8')
                assert result.returncode == 2 and not result.stdout, (mode, result.stderr)
                actual = page.evaluate('''async path => {
                    const {instance} = await WebAssembly.instantiate(await(await fetch('/almanac/query-engine.wasm')).arrayBuffer(), {}), e=instance.exports;
                    const b=new Uint8Array(await(await fetch(path)).arrayBuffer()), p=e.osw_alloc(b.length);
                    try { new Uint8Array(e.memory.buffer,p,b.length).set(b); e.osw_load(p,b.length);
                      return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));
                    } finally {e.osw_dealloc(p,b.length);}
                }''', '/'+path.relative_to(ROOT).as_posix())
                assert actual['ok'] is False, (mode, actual)
        assert not errors, errors
        page.set_content((ROOT/'figures/atlantic-seuc-molinari-1981-core-width.svg').read_text(encoding='utf8'))
        page.locator('svg').screenshot(path=str(out/'independent-figure.png'))
        browser.close()
    print('PASS: Atlantic SEUC core on atlas, seasons, exact source and real inspector; eight coherent native/WASM rejection cases')


if __name__ == '__main__':
    main()
