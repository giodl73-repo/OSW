"""Shipped worker rejects missing/corrupt parts; legacy snapshots still load."""
import hashlib
import json
import os
from playwright.sync_api import sync_playwright, expect
from query_packet import read_bundle_bytes
from test_rust_query_browser import ROOT, BASE, native, browser_query
from browser_bundle_fixture import install_bundle_fixture


def main():
    packet=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    assert packet['schema']=='osw.query-packet.v1'
    query={'collection':'current_dimension_samples','limit':1}
    expected=native(query)
    assert expected['total']==6588
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page();page.goto(BASE)
        page.wait_for_function('window.oswLastQueryResult',timeout=90000)
        assert browser_query(page,query)==expected
        # The WASM guard must reject oversized snapshots before reading input.
        guard=page.evaluate('''async()=>{
          const {instance}=await WebAssembly.instantiate(await (await fetch('query-engine.wasm')).arrayBuffer(),{});
          const e=instance.exports;e.osw_rebase_source(0,512*1024*1024+1);
          return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));
        }''')
        assert guard=={'ok':False,'error':'Source snapshot exceeds 512 MiB'}
        page.close()
        for kind in ['missing','changed','traversal']:
            page=browser.new_page()
            if kind=='missing':
                page.route('**/'+packet['parts'][0]['path'],lambda r:r.fulfill(status=404,body='missing'))
                error='HTTP 404'
            elif kind=='changed':
                page.route('**/'+packet['parts'][0]['path'],lambda r:r.fulfill(body=b'changed'))
                error='Changed query packet part'
            else:
                bad=json.loads(json.dumps(packet));bad['parts'][0]['path']='../outside.bin'
                raw=json.dumps(bad).encode()
                manifest=json.loads((ROOT/'almanac/query-engine.manifest.json').read_bytes())
                manifest['sha256']['almanac/query-data.json']=hashlib.sha256(raw).hexdigest()
                page.route('**/query-data.json',lambda r:r.fulfill(body=raw,content_type='application/json'))
                page.route('**/query-engine.manifest.json',lambda r:r.fulfill(json=manifest))
                error='Invalid or unpinned query packet part'
            forbidden=[]
            page.on('request',lambda r:forbidden.append(r.url) if 'outside.bin' in r.url else None)
            page.goto(BASE)
            expect(page.locator('#query-status')).to_contain_text(error,timeout=90000)
            assert not forbidden
            assert page.evaluate('!window.oswLastQueryResult')
            page.close()
        # Complete uploaded/mutated snapshots retain their old transport format.
        page=browser.new_page()
        install_bundle_fixture(page,json.loads(read_bundle_bytes(ROOT/'almanac/query-data.json')))
        page.goto(BASE);page.wait_for_function('window.oswLastQueryResult',timeout=90000)
        assert browser_query(page,query)==expected
        page.close();browser.close()
    print('PASS: seven-part native/WASM parity, missing/corrupt parts, traversal rejected before fetch, legacy complete snapshot')


if __name__=='__main__':main()
