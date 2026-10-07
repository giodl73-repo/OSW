"""Checked index corpus: independent source inventory and native/WASM parity.

This tests the backend in isolation; dedicated checks cover the migrated page.
"""
import gzip
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright
from test_rust_query_browser import ROOT, CLI

BASE = 'http://127.0.0.1:8788/almanac/index.html'
HARNESS = '''<!doctype html><title>Index backend check</title><script>
const worker = new Worker('index-worker.js');
let serial = 0; const pending = new Map();
worker.onmessage = ({data}) => {
  pending.get(data.id)(data.result); pending.delete(data.id);
};
window.rpc = (action, value) => new Promise(resolve => {
  const id = ++serial; pending.set(id, resolve);
  worker.postMessage({id, action, value});
});
</script>'''


def main():
    catalog = json.loads((ROOT/'almanac/index-catalog.json').read_text(encoding='utf-8'))
    compressed = (ROOT/'almanac/index-data.json.gz').read_bytes()
    payload = gzip.decompress(compressed)
    assert hashlib.sha256(compressed).hexdigest() == catalog['compressed_sha256']
    assert hashlib.sha256(payload).hexdigest() == catalog['bundle_sha256']
    bundle = json.loads(payload)
    assert len(bundle['documents']) == catalog['source_count'] == 63
    for path, digest in catalog['input_sha256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, path
    for descriptor in catalog['documents']:
        original = (ROOT/descriptor['path']).read_bytes()
        assert bundle['documents'][descriptor['path']].encode('utf-8') == original
        assert hashlib.sha256(original).hexdigest() == descriptor['source_sha256']
        assert len(original) == descriptor['source_bytes']
    seasonal = json.loads((ROOT/'research/noaa-munster-eddy-seasonal-manifest-2021-2023.json').read_text(encoding='utf-8'))
    assert len(seasonal['snapshots']) == 12
    assert all((ROOT/'almanac'/s['path']).resolve().relative_to(ROOT).as_posix()
               in bundle['documents'] for s in seasonal['snapshots'])

    queries = [
        {'document':'research/ocean-current-almanac.json', 'pointer':'/entries', 'text':'agulhas', 'limit':500},
        {'document':'research/noaa-munster-eddy-state-20230601.json', 'pointer':'/entries',
         'filters':[{'field':'record.contained_states','op':'contains','value':'CAMR'}],
         'sort':{'field':'record.radius_km','direction':'desc'},'offset':2,'limit':7},
        {'document':'research/noaa-munster-eddy-state-20210301.json','pointer':'/entries','offset':7000,'limit':11},
        {'document':'research/ocean-current-almanac.json','limit':5},
    ]
    invalid = [
        {'document':'missing.json'},
        {'document':queries[0]['document'],'pointer':'entries'},
        {'document':queries[0]['document'],'pointer':'/missing'},
        {'document':queries[0]['document'],'limit':501},
        {'document':queries[0]['document'],'filters':[{'field':'record.name','op':'invented','value':None}]},
        {'document':queries[0]['document'],'sort':{'field':'source_key','direction':'sideways'}},
    ]
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as directory:
        packet = Path(directory)/'index.json'
        packet.write_bytes(payload)

        def native(query=None):
            args = [str(CLI),'--index',str(packet)] + ([] if query is None else ['-'])
            result = subprocess.run(args, input=None if query is None else json.dumps(query),
                                    text=True, encoding='utf-8', capture_output=True)
            if not result.stdout.strip():
                assert result.returncode != 0 and result.stderr.strip(), result
                return {'ok':False,'error':result.stderr.strip()}
            return json.loads(result.stdout)

        metadata = native()
        assert metadata['ok'] and metadata['catalog'] == catalog
        expected = [native(q) for q in queries]
        assert all(r['ok'] for r in expected)
        # Independent scientific-source oracle, not a second Rust projection.
        source = json.loads(bundle['documents'][queries[1]['document']])['entries']
        matched = [(i,r) for i,r in enumerate(source) if 'CAMR' in r['contained_states']]
        matched.sort(key=lambda pair: pair[1]['radius_km'], reverse=True)
        assert expected[1]['total'] == len(matched)
        assert expected[1]['rows'] == [
            {'record':r,'source_key':str(i),'source_pointer':f'/entries/{i}'}
            for i,r in matched[2:9]]
        assert all(not native(q)['ok'] for q in invalid)
        packet.write_bytes(payload + b' ')
        assert not native()['ok']
        packet.write_bytes(payload)

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page = browser.new_page()
            requests, errors = [], []
            page.on('request', lambda request: requests.append(request.url))
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.route(BASE, lambda route: route.fulfill(body=HARNESS, content_type='text/html'))
            page.goto(BASE)
            actual = page.evaluate("rpc('load')")
            assert actual == metadata, actual
            for q, result in zip(queries, expected):
                assert page.evaluate("q => rpc('query',q)", q) == result
            for q in invalid:
                assert not page.evaluate("q => rpc('query',q)", q)['ok']
            doc = queries[0]['document']
            assert page.evaluate("document => rpc('document',{document})",doc) == {
                'ok':True,'document':doc,'value':json.loads(bundle['documents'][doc])}
            assert not errors, errors
            assert not any('/research/' in url or 'query-data.json' in url for url in requests)
            # Each checked input fails independently, with no raw-source fallback.
            for asset in ['index-catalog.json','index-data.json.gz','query-engine.wasm']:
                failed = browser.new_page()
                failed.route(BASE, lambda route: route.fulfill(body=HARNESS, content_type='text/html'))
                failed.route('**/'+asset, lambda route: route.fulfill(body=b'changed',content_type='application/octet-stream'))
                failed.goto(BASE)
                result = failed.evaluate("rpc('load')")
                assert not result['ok'] and 'Changed' in result['error'], (asset,result)
                assert not failed.evaluate("q => rpc('query',q)", queries[0])['ok']
                failed.close()
            browser.close()
    print('PASS: 63 exact sources, 12 seasonal snapshots, independent NOAA oracle, native/WASM parity and checked-input failures')


if __name__ == '__main__':
    main()
