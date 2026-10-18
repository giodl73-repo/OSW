"""Research calculations survive native/WASM queries and accessible current cards."""
import copy
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from urllib.parse import quote, unquote

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get('OSW_RESEARCH_EVIDENCE_BASE', 'http://127.0.0.1:8788')
CLI = ROOT / 'rust/osw-query/target/debug' / ('osw-query-cli.exe' if os.name == 'nt' else 'osw-query-cli')
REGISTRY = 'research/current-research-evidence-registry.json'


def native(query, packet=None, index=None):
    args = [str(CLI)] + (['--index', str(index)] if index else [str(packet or ROOT / 'almanac/query-data.json')]) + ['-']
    result = subprocess.run(args, input=json.dumps(query), capture_output=True, text=True, encoding='utf8')
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def corrupt(packet, kind):
    bad = copy.deepcopy(packet)
    rows = [r for r in bad['collections']['diagnostics'] if 'research_evidence' in r]
    row = next(r for r in rows if r['current_id'] == 'red-sea-saline-overflow')
    if kind == 'rank': row['rank_eligible'] = True
    elif kind == 'owner': row['current_id'] = 'agulhas'; row['entity_id'] = 'current:agulhas'
    elif kind == 'source_json': row['source_json'] = '{}'
    elif kind == 'missing': bad['collections']['diagnostics'].remove(row)
    elif kind == 'duplicate':
        extra = copy.deepcopy(row); extra['id'] += ':copy'; bad['collections']['diagnostics'].append(extra)
    elif kind == 'owner_link':
        next(o for o in bad['collections']['objects'] if o['id'] == row['entity_id'])['research_evidence_ids'] = []
    elif kind == 'orphan':
        del bad['manifest']['input_sha256'][REGISTRY]
        owners = {r['entity_id'] for r in rows}
        bad['collections']['objects'] = [o for o in bad['collections']['objects'] if o['id'] not in owners]
    elif kind == 'original_pin':
        bad['manifest']['input_sha256']['research/source-data/ncei-redsox-2001/ladcp-ascii-originals.zip'] = '0' * 64
    elif kind in ('whole_width', 'annual', 'blinding', 'identity'):
        target = rows[0] if kind == 'identity' else row
        document = copy.deepcopy(target['document'])
        if kind == 'whole_width': document['whole_current_width_km'] = 6
        elif kind == 'annual': document['annual_width_range_km'] = [0, 6]
        elif kind == 'blinding': document['fully_blinded_before_any_selected_velocity_exposure'] = True
        else: document['current_association_verified'] = True
        raw = json.dumps(document)
        pin = hashlib.sha256(raw.encode()).hexdigest()
        target.update(document=document, source_json=raw, source_file_sha256=pin)
        bad['manifest']['input_sha256'][target['source_file']] = pin
    elif kind in ('scene_width', 'geometry', 'figure', 'primary'):
        scene = row['research_evidence']
        if kind == 'scene_width': scene['whole_current_width_km'] = 6
        elif kind == 'geometry': scene['geometry_role'] = 'physical_width_geometry'
        elif kind == 'figure': scene['figure_sha256'] = '0' * 64
        else: scene['facts'][1]['value'] = 'About 6 km'
        # Coherently change and rehash the accompanying registry too.
        registry = json.loads((ROOT / REGISTRY).read_bytes())
        registry['scenes'] = [scene if s['diagnostic_id'] == row['id'] else s for s in registry['scenes']]
        bad['manifest']['input_sha256'][REGISTRY] = hashlib.sha256(json.dumps(registry).encode()).hexdigest()
    else: raise AssertionError(kind)
    return bad


def check_source_documents(page, registry):
    """Query every new document through one loaded WASM source store."""
    page.locator('#source-query-panel details').evaluate('(node)=>node.open=true')
    for document in [REGISTRY, *registry['documents']]:
        request = {'document':document, 'pointer':'', 'limit':1}
        page.locator('#source-query-json').fill(json.dumps(request))
        page.evaluate('window.oswSourceQueryResult=null')
        page.locator('#source-query-run-json').click()
        page.wait_for_function('window.oswSourceQueryResult', timeout=90000)
        actual = page.evaluate('window.oswSourceQueryResult')
        source = json.loads((ROOT / document).read_bytes())
        key = sorted(source)[0]
        assert actual['document'] == document and actual['total'] == len(source)
        assert actual['source_sha256'] == hashlib.sha256((ROOT / document).read_bytes()).hexdigest()
        assert actual['rows'] == [{'source_key':key, 'source_pointer':'/' + key.replace('~','~0').replace('/','~1'), 'record':source[key]}]


def main():
    output = ROOT / '.pytest_cache/current-research-evidence-browser'
    output.mkdir(parents=True, exist_ok=True)
    registry = json.loads((ROOT / REGISTRY).read_bytes())
    packet = json.loads((ROOT / 'almanac/query-data.json').read_bytes())
    cases = ['rank', 'owner', 'source_json', 'missing', 'duplicate', 'owner_link', 'orphan', 'original_pin',
             'whole_width', 'annual', 'blinding', 'identity', 'scene_width', 'geometry', 'figure', 'primary']
    with TemporaryDirectory(dir=output) as temporary, sync_playwright() as playwright:
        folder = Path(temporary)
        index = folder / 'index.json'
        index.write_bytes(gzip.decompress((ROOT / 'almanac/index-data.json.gz').read_bytes()))
        # Loading the native index verifies all catalog document bytes once.
        assert native({'document':REGISTRY, 'pointer':'', 'limit':1}, index=index)['ok']
        browser = playwright.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page = browser.new_page(viewport={'width':1280, 'height':1000})
        errors, automatic_originals = [], []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('request', lambda r: automatic_originals.append(r.url) if any(x in r.url.lower().split('?')[0] for x in ('.pdf', '.zip', '.mat')) else None)
        for scene in registry['scenes']:
            owner = scene['current_id']
            page.goto(BASE + '/almanac/reference-routes.html?atlas-feature=current%3A' + owner + '#route-atlas')
            panel = page.locator('#route-atlas-preview .current-research-evidence')
            expect(panel).to_be_visible(timeout=90000)
            assert panel.locator('dd').all_text_contents() == [f['value'] for f in scene['facts']]
            assert panel.get_attribute('data-current') == owner
            assert '\u00c3' not in panel.inner_text() and '\u00c2' not in panel.inner_text()
            details = panel.locator('details')
            assert details.get_attribute('open') is None
            details.locator('summary').focus(); page.keyboard.press('Enter')
            assert details.get_attribute('open') is not None
            expect(details.locator('img')).to_be_visible()
            expect(details.locator('img')).to_have_js_property('complete', True)
            assert details.locator('img').evaluate('(img)=>img.naturalWidth>0')
            expect(details).to_contain_text('Next evidence needed:')
            if owner == 'red-sea-saline-overflow':
                expect(details).to_contain_text('no fully blinded preregistration')
                expect(details).to_contain_text('not zero width')
                link = panel.get_by_role('link', name='Inspect declaration-history qualification')
            else:
                expect(details).to_contain_text('northern pattern peaks at the retained data edge')
                link = panel.get_by_role('link', name='Inspect declared calculation')
            source_query = json.loads(unquote(link.get_attribute('href').split('source-q=')[1]))
            link.click()
            page.wait_for_function('window.oswSourceQueryResult', timeout=90000)
            assert page.evaluate('oswSourceQueryResult') == native(source_query, index=index)
            if owner == registry['scenes'][0]['current_id']:
                check_source_documents(page, registry)
            page.goto(BASE + '/almanac/seasons.html?current=' + owner)
            page.wait_for_function('(id)=>window.oswSeasonPlan?.current_id===id', arg=owner, timeout=90000)
            panel = page.locator('#current-width-source-review .current-research-evidence')
            expect(panel).to_be_visible()
            page.set_viewport_size({'width':320, 'height':900}); page.emulate_media(reduced_motion='reduce')
            panel.locator('summary').focus(); page.keyboard.press('Enter')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            panel.screenshot(path=str(output / (owner + '-mobile.png')))
            page.locator('#season-current').select_option('portugal')
            assert page.locator('.current-research-evidence').count() == 0
            page.set_viewport_size({'width':1280, 'height':1000})
            query = {'collection':'diagnostics', 'filters':[{'field':'id','op':'eq','value':scene['diagnostic_id']}], 'limit':100}
            page.goto(BASE + '/almanac/query.html?q=' + quote(json.dumps(query)))
            page.wait_for_function('window.oswLastQueryResult', timeout=90000)
            assert page.evaluate('oswLastQueryResult') == native(query)
            panel = page.locator('#query-chart-panels .current-research-evidence')
            expect(panel).to_be_visible()
            assert panel.locator('details').get_attribute('open') is not None
            panel.get_by_role('button', name='Inspect research evidence record').click()
            expect(page.locator('#query-detail')).to_contain_text(scene['diagnostic_id'])
        query = {'collection':'diagnostics', 'limit':100}
        page.goto(BASE + '/almanac/query.html?q=' + quote(json.dumps(query)))
        page.wait_for_function('window.oswLastQueryResult', timeout=90000)
        assert page.evaluate('oswLastQueryResult') == native(query)
        assert page.locator('#query-chart-panels .current-research-evidence').count() == 2
        assert page.locator('#query-chart-panels .current-width-source-review').count() == 2
        assert not automatic_originals, automatic_originals
        page.route('**/research-evidence-guard.html', lambda route: route.fulfill(body='<title>Research evidence guard</title>', content_type='text/html'))
        page.goto(BASE + '/research-evidence-guard.html')
        for kind in cases:
            path = folder / 'corrupt.json'
            path.write_bytes(json.dumps(corrupt(packet, kind)).encode())
            result = subprocess.run([str(CLI), str(path), '-'], input='{}', capture_output=True, text=True, encoding='utf8')
            assert result.returncode == 2 and not result.stdout, (kind, result.stderr)
            result = page.evaluate('''async path=>{
              const {instance}=await WebAssembly.instantiate(await(await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports;
              const b=new Uint8Array(await(await fetch(path)).arrayBuffer()),p=e.osw_alloc(b.length);
              try{new Uint8Array(e.memory.buffer,p,b.length).set(b);e.osw_load(p,b.length);
                return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));
              }finally{e.osw_dealloc(p,b.length);}
            }''', '/' + path.relative_to(ROOT).as_posix())
            assert result['ok'] is False, (kind, result)
        assert not errors, errors
        browser.close()
    print(f'PASS: both research cards/seasons/query/source/inspector/mobile; 18 indexed documents; mixed diagnostics; {len(cases)} native/WASM corruption rejections; no automatic originals')


if __name__ == '__main__':
    main()
