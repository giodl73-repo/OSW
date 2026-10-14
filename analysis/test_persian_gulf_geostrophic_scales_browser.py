"""Source operators, a regional map and both runtimes retain separate supports."""
import copy
import hashlib
import json
import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote
from playwright.sync_api import sync_playwright, expect
from check_persian_gulf_geostrophic_scales import ROOT, AUDIT, OWNER, IDS
from test_rust_query_browser import CLI, BASE, native


def corrupted(bundle, mode):
    bad = copy.deepcopy(bundle)
    receipt = bad['manifest']['seasons_receipts']['widths']
    document = json.loads(receipt['source_json'])
    row = next(r for r in bad['collections']['widths'] if r['id'] == IDS[0])
    original = next(r for r in document['measurements'] if r['id'] == IDS[0])
    for target in [row, original]:
        if mode == 'range': target['width_range_km'] = [5, 30]
        if mode == 'date': target['observed_period'] = {'start':'1999-10-22','end':'1999-10-22'}
        if mode == 'layer': target['fixed_layer_bounds_m'] = [30, 45]
        if mode == 'cutoff': target['original_regional_context']['velocity_boundary_threshold_m_s'] = .1
        if mode == 'reference': target['original_regional_context']['added_reference_velocity_m_s'] = 0
        if mode == 'context': target.pop('original_regional_context')
    if mode == 'missing':
        bad['collections']['widths'].remove(row)
        document['measurements'].remove(original)
        bad['manifest']['input_sha256'].pop(AUDIT)
    if mode == 'legacy':
        for rows in [bad['collections']['widths'], document['measurements']]:
            next(r for r in rows if r['id']=='persian-gulf-gogp99-core-width-2')['width_metric'] = 'velocity_core'
    if mode == 'pin': bad['manifest']['input_sha256'][AUDIT] = '0'*64
    receipt['source_json'] = json.dumps(document, ensure_ascii=False)
    receipt['source_sha256'] = hashlib.sha256(receipt['source_json'].encode()).hexdigest()
    bad['manifest']['input_sha256'][receipt['source_file']] = receipt['source_sha256']
    return bad


def main():
    out = ROOT/'.pytest_cache/persian-gulf-gap-review'
    out.mkdir(parents=True, exist_ok=True)
    query = {'collection':'widths','filters':[{'field':'current_id','op':'eq','value':OWNER}], 'limit':100}
    expected = native(query)
    assert expected['ok'] and expected['total'] == 8
    assert len([r for r in expected['rows'] if r['phase_kind']=='campaign_hydrographic_core']) == 6
    bundle = json.loads((ROOT/'almanac/query-data.json').read_bytes())
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page = browser.new_page(viewport={'width':1280,'height':1000})
        errors = []
        page.on('pageerror', lambda e:errors.append(str(e)))
        for identifier, value in zip(IDS, [30, 5]):
            page.goto(f'http://127.0.0.1:8788/almanac/seasons.html?current={OWNER}&phase={identifier}')
            page.wait_for_function('window.oswSeasonPlan?.current_id === "'+OWNER+'"', timeout=90000)
            chart = page.locator('#regional-width-range .original-regional-width')
            expect(chart).to_be_visible()
            assert chart.locator('svg circle').count() == 1
            assert f'{value} km' in page.locator('#season-value').inner_text()
            expect(chart).to_contain_text('30 m reference plus 0.09 m/s')
            assert page.locator('#season-play').is_disabled()
            assert page.evaluate('oswSeasonPlan.eligible_indices') == []
            assert page.locator('#season-section-locator').is_hidden()
            expect(chart.get_by_role('link', name='Compare the flow band and faster peak')).to_be_visible()
            source = chart.get_by_role('link', name='Inspect regional width scope and source', exact=True)
            assert '%2Fmeasurements%2F'+str(IDS.index(identifier)) in source.get_attribute('href')
            page.set_viewport_size({'width':320,'height':900})
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            chart.screenshot(path=str(out/(identifier+'-mobile.png')))
            source.click()
            page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
            assert page.evaluate('oswSourceQueryResult.document') == AUDIT
        page.goto(f'http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3A{OWNER}#route-atlas')
        preview = page.locator('#route-atlas-preview')
        expect(preview.locator('.route-map')).to_be_visible(timeout=90000)
        expect(preview).to_contain_text('Studied reach only')
        expect(preview).to_contain_text('140')
        assert preview.locator('.original-regional-width').count() == 2
        assert page.locator('#reference-route-rows a[href="#persian-gulf-cascading-reach-reference-path-candidate"]').count() == 0
        preview.get_by_role('link', name='Full route card, measurements and sources').click()
        card = page.locator('#persian-gulf-cascading-reach-reference-path-candidate')
        expect(card.locator('.route-map')).to_be_visible()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        card.locator('.route-map').screenshot(path=str(out/'regional-route-mobile.png'))
        page.goto(BASE+'?q='+quote(json.dumps(query)))
        page.wait_for_function('window.oswLastQueryResult',timeout=90000)
        assert page.evaluate('oswLastQueryResult') == expected
        page.locator('#query-rows tr button').first.click()
        expect(page.locator('#query-detail h3')).to_have_text('Persian Gulf saline overflow')
        for mode in ['range','date','layer','cutoff','reference','context','missing','legacy','pin']:
            with TemporaryDirectory(dir=out) as directory:
                path = Path(directory)/'bad.json'
                path.write_text(json.dumps(corrupted(bundle,mode),ensure_ascii=False),encoding='utf8')
                result = subprocess.run([str(CLI),str(path),'-'],input='{}',capture_output=True,text=True,encoding='utf8')
                assert result.returncode == 2 and not result.stdout, (mode,result.stderr)
                actual = page.evaluate('''async path=>{
                  const {instance}=await WebAssembly.instantiate(await(await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports;
                  const b=new Uint8Array(await(await fetch(path)).arrayBuffer()),p=e.osw_alloc(b.length);
                  try {new Uint8Array(e.memory.buffer,p,b.length).set(b);e.osw_load(p,b.length);
                    return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));
                  } finally {e.osw_dealloc(p,b.length);}
                }''','/'+path.relative_to(ROOT).as_posix())
                assert actual['ok'] is False, (mode,actual)
        assert not errors, errors
        for source in ['figures/persian-gulf-gogp99-geostrophic-scales.svg','figures/persian-gulf-cascading-reach-reference-path-candidate.svg']:
            page.set_viewport_size({'width':1100,'height':1000})
            page.set_content((ROOT/source).read_text(encoding='utf8'))
            page.locator('svg').screenshot(path=str(out/(Path(source).stem+'.png')))
        browser.close()
    print('PASS: two velocity operators, six unchanged salinity cores, regional map, source/inspector/mobile navigation, and nine coherent native/WASM rejection cases')


if __name__ == '__main__': main()
