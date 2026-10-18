"""Actual compiled admission, source navigation and section-span presentation."""
import copy
import gzip
import hashlib
import json
import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote

from playwright.sync_api import sync_playwright, expect

from check_portugal_orca_section_span import AUDIT, ID, ROOT, record
from test_rust_query_browser import BASE, CLI, browser_query, native


def corrupt(bundle, mode):
    bad = copy.deepcopy(bundle)
    receipt = bad['manifest']['seasons_receipts']['widths']
    inventory = json.loads(receipt['source_json'])
    rows = [next(r for r in collection if r['id'] == ID)
            for collection in [inventory['measurements'], bad['collections']['widths']]]
    changes = {
        'width': ('approximate_width_km', 144),
        'dates': ('observed_period', {'start': '2009-10-15', 'end': '2009-11-11'}),
        'layer': ('fixed_layer_bounds_m', [0, 1600]),
        'error': ('uncertainty_km', 0.4),
        'owner': ('current_id', 'portugal-coastal'),
        'annual': ('annual_extrema_eligible', True),
    }
    if mode in changes:
        key, value = changes[mode]
        for row in rows:
            row[key] = copy.deepcopy(value)
    if mode == 'original_claim':
        for row in rows:
            row['published_section_context']['source_review']['raw_pdf_acquired'] = True
    if mode == 'missing':
        inventory['measurements'].remove(rows[0])
        bad['collections']['widths'].remove(rows[1])
        decision = next(d for d in inventory['current_decisions'] if d['current_id'] == 'portugal')
        decision.update(measurement_ids=[], width_decision='section_span_diagnostic_present_width_unresolved')
        inventory['counts']['measurements'] -= 1
        inventory['counts']['currents_with_scoped_width_evidence'] -= 1
        inventory['counts']['currents_with_section_span_diagnostics_width_unresolved'] += 1
        owner = next(r for r in bad['collections']['objects'] if r['id'] == 'current:portugal')
        owner['width_ids'].remove(ID)
        owner['capabilities']['scoped_width'] -= 1
    if mode == 'audit_forgery':
        diagnostic = next(d for d in bad['collections']['diagnostics'] if d['id'] == 'diagnostic:portugal-orca-section-span')
        audit = diagnostic['document']
        audit['measurement']['approximate_width_km'] = 144
        raw = json.dumps(audit)
        pin = hashlib.sha256(raw.encode()).hexdigest()
        diagnostic.update(source_json=raw, source_file_sha256=pin)
        bad['manifest']['input_sha256'][AUDIT] = pin
        for row in rows:
            row['approximate_width_km'] = 144
            row['published_section_context']['audit_sha256'] = pin
    receipt['source_json'] = json.dumps(inventory)
    receipt['source_sha256'] = hashlib.sha256(receipt['source_json'].encode()).hexdigest()
    bad['manifest']['input_sha256'][receipt['source_file']] = receipt['source_sha256']
    return bad


def main():
    out = ROOT / '.pytest_cache/portugal-perez-2013-review'
    out.mkdir(exist_ok=True)
    bundle = json.loads((ROOT / 'almanac/query-data.json').read_bytes())
    with TemporaryDirectory(dir=out) as folder, sync_playwright() as p:
        index = Path(folder) / 'index.json'
        index.write_bytes(gzip.decompress((ROOT / 'almanac/index-data.json.gz').read_bytes()))
        browser = p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page = browser.new_page(viewport={'width': 1280, 'height': 1000})
        errors, pdf_requests = [], []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('request', lambda r: pdf_requests.append(r.url) if '.pdf' in r.url else None)
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Aportugal#route-atlas')
        preview = page.locator('#route-atlas-preview')
        chart = preview.locator('.published-coordinate-section-span svg')
        expect(chart).to_be_visible(timeout=90000)
        assert '116 km nominal section span' in chart.get_attribute('aria-label')
        expect(preview.get_by_role('link', name='Map local component spans')).to_be_visible()
        expect(preview).to_contain_text('Original PDF bytes and page images have not been acquired')
        preview.locator('.published-coordinate-section-span').screenshot(path=str(out / 'atlas-card.png'))
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=portugal&phase=' + ID)
        page.wait_for_function('window.oswSeasonPlan?.current_id==="portugal"', timeout=90000)
        expect(page.locator('#regional-width-range .published-coordinate-section-span svg')).to_be_visible()
        assert page.locator('#season-play').is_disabled()
        page.set_viewport_size({'width': 320, 'height': 900})
        page.emulate_media(reduced_motion='reduce')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#regional-width-range').screenshot(path=str(out / 'integrated-mobile.png'))
        query = {'collection': 'widths', 'filters': [{'field': 'id', 'op': 'eq', 'value': ID}]}
        expected = native(query)
        assert expected['rows'] == [record()]
        assert expected['chart_scene']['kind'] == 'published_coordinate_section_span'
        page.goto(BASE + '?q=' + quote(json.dumps(query)))
        page.wait_for_function('window.oswLastQueryResult', timeout=90000)
        assert page.evaluate('oswLastQueryResult') == expected
        expect(page.locator('#query-chart-panels .published-coordinate-section-span svg')).to_be_visible()
        page.locator('#query-chart-panels').get_by_role('button', name='Inspect measurement').click()
        expect(page.locator('#query-detail')).to_contain_text(ID)
        combined_query = {'collection': 'widths', 'limit': 7}
        assert browser_query(page, combined_query) == native(combined_query)
        expect(page.locator('#query-chart-panels .published-coordinate-section-span svg')).to_be_visible()
        source_query = {'document': AUDIT, 'pointer': '/measurement', 'limit': 100}
        result = subprocess.run([str(CLI), '--index', str(index), '-'], input=json.dumps(source_query), capture_output=True, text=True, encoding='utf8')
        assert result.returncode == 0, result.stderr
        page.goto(BASE + '?source-q=' + quote(json.dumps(source_query)))
        page.wait_for_function('window.oswSourceQueryResult', timeout=90000)
        assert page.evaluate('oswSourceQueryResult') == json.loads(result.stdout)
        assert not pdf_requests, pdf_requests
        page.route('**/portugal-width-guard.html', lambda r: r.fulfill(body='<title>Width guard</title>', content_type='text/html'))
        page.goto('http://127.0.0.1:8788/portugal-width-guard.html')
        for mode in ['width', 'dates', 'layer', 'error', 'owner', 'annual', 'original_claim', 'missing', 'audit_forgery']:
            path = Path(folder) / 'bad.json'
            path.write_text(json.dumps(corrupt(bundle, mode)), encoding='utf8')
            rejected = subprocess.run([str(CLI), str(path), '-'], input='{}', capture_output=True, text=True, encoding='utf8')
            assert rejected.returncode == 2 and not rejected.stdout, (mode, rejected.stderr)
            actual = page.evaluate('''async path=>{
              const {instance}=await WebAssembly.instantiate(await(await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports;
              const b=new Uint8Array(await(await fetch(path)).arrayBuffer()),p=e.osw_alloc(b.length);
              try{new Uint8Array(e.memory.buffer,p,b.length).set(b);e.osw_load(p,b.length);
                return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));
              }finally{e.osw_dealloc(p,b.length);}
            }''', '/' + path.relative_to(ROOT).as_posix())
            assert actual['ok'] is False, (mode, actual)
        assert not errors, errors
        browser.close()
    print('PASS: Portugal section-span atlas/seasons/query/source/inspector/mobile parity; independent40Ndiagnostic retained; no PDF or playback; nine coherent native/WASM rejections')


if __name__ == '__main__':
    main()
