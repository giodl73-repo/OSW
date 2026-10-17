"""Actual query/atlas/source integration and native/WASM section admission."""
import gzip
import json
import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote

from playwright.sync_api import sync_playwright, expect

from asca_section_mutations import MODES, corrupt
from test_rust_query_browser import ROOT, BASE, CLI, native


def main():
    output = ROOT/'.pytest_cache/agulhas-act-source-review'
    output.mkdir(exist_ok=True)
    bundle = json.loads((ROOT/'almanac/query-data.json').read_bytes())
    assert len(bundle['collections']['current_sections']) == 27
    query = {'collection':'current_sections','sort':{'field':'id'},'limit':100}
    expected = native(query)
    assert expected['total'] == 27
    with TemporaryDirectory(dir=output) as folder, sync_playwright() as p:
        index = Path(folder)/'index.json'
        index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        browser = p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page = browser.new_page(viewport={'width':1280,'height':1000})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(BASE+'?q='+quote(json.dumps(query)))
        page.wait_for_function('window.oswLastQueryResult', timeout=90000)
        assert page.evaluate('oswLastQueryResult') == expected
        assert page.locator('[data-section-month] option').count() == 27
        assert page.locator('[data-section-field] svg').count() == 4
        months = page.locator('[data-section-month]')
        months.select_option('section:agulhas:asca100m:2016-05')
        expect(page.locator('[data-section-status]')).to_contain_text('37 source records')
        page.get_by_role('button', name='Inspect selected monthly section').click()
        expect(page.locator('#query-detail')).to_contain_text('section:agulhas:asca100m:2016-05')
        source_query = expected['chart_scene']['frames'][1]['source_query']
        source = subprocess.run([str(CLI),'--index',str(index),'-'],input=json.dumps(source_query),capture_output=True,text=True,encoding='utf8')
        assert source.returncode == 0, source.stderr
        page.goto(BASE+'?source-q='+quote(json.dumps(source_query)))
        page.wait_for_function('window.oswSourceQueryResult',timeout=90000)
        assert page.evaluate('oswSourceQueryResult') == json.loads(source.stdout)
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Aagulhas#route-atlas')
        preview = page.locator('#route-atlas-preview')
        chart_link = preview.get_by_role('link', name='Observed ASCA 100 m monthly sections / source profiles →')
        expect(chart_link).to_be_visible(timeout=90000)
        chart_link.click()
        page.wait_for_function('window.oswLastQueryResult',timeout=90000)
        assert page.evaluate('oswLastQueryResult.total') == 27
        page.set_viewport_size({'width':320,'height':900})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('.current-section-chart').screenshot(path=str(output/'mainline-sections-mobile.png'))
        page.emulate_media(reduced_motion='reduce')
        expect(page.get_by_role('button', name='Play months')).to_be_disabled()
        page.get_by_role('button', name='Next month').click()
        expect(page.locator('[data-section-status]')).to_contain_text('May 2016')
        page.route('**/asca-section-guard.html',lambda route: route.fulfill(body='<title>ASCA section admission</title>',content_type='text/html'))
        page.goto('http://127.0.0.1:8788/asca-section-guard.html')
        for mode in MODES:
            path = Path(folder)/'changed.json'
            path.write_text(json.dumps(corrupt(bundle,mode)),encoding='utf8')
            rejected = subprocess.run([str(CLI),str(path),'-'],input='{}',capture_output=True,text=True,encoding='utf8')
            assert rejected.returncode == 2 and not rejected.stdout,(mode,rejected.stderr)
            actual = page.evaluate('''async path=>{
                const {instance}=await WebAssembly.instantiate(await(await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports;
                const bytes=new Uint8Array(await(await fetch(path)).arrayBuffer()),ptr=e.osw_alloc(bytes.length);
                try{new Uint8Array(e.memory.buffer,ptr,bytes.length).set(bytes);e.osw_load(ptr,bytes.length);
                    return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));
                }finally{e.osw_dealloc(ptr,bytes.length);}
            }''','/'+path.relative_to(ROOT).as_posix())
            assert actual['ok'] is False,(mode,actual)
        assert not errors, errors
        browser.close()
    print('PASS: actual ASCA query/atlas/inspector/source/mobile/reduced-motion parity and eleven coherent native/WASM rejections')


if __name__ == '__main__': main()
