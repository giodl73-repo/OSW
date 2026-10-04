"""Actual native/WASM SVG parity, complete scene inventory and portable rendering."""
import hashlib
import json
import os
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from test_rust_query_browser import browser_query, native

ROOT=Path(__file__).resolve().parents[1]
NS={'s':'http://www.w3.org/2000/svg'}

def inspect(svg, query, scene):
    root=ET.fromstring(svg)
    receipt=json.loads(root.find('s:metadata',NS).text)
    assert receipt['query']==query
    assert receipt['bundle_sha256']==hashlib.sha256((ROOT/'almanac/query-data.json').read_bytes()).hexdigest()
    marks=[node for node in root.iter() if 'mark' in node.get('class','').split()]
    assert len(marks)==len(scene['features'])
    assert {m.get('data-entity') for m in marks}=={f['entity_id'] for f in scene['features']}
    assert receipt['features']==scene['features'] and receipt['omitted_features']==scene['omitted_features']
    assert receipt['matching_objects']==scene['matching_objects']
    assert not root.findall('.//s:script',NS) and not root.findall('.//s:image',NS)
    assert not any('href' in key for node in root.iter() for key in node.attrib)
    assert all(node.find('s:title',NS) is not None for node in marks)
    return receipt

def main():
    exe=str(ROOT/'rust/osw-query/target/debug/osw-query-cli.exe')
    queries=[{'collection':'objects','record_type':'named_current','limit':1,'offset':10},
             {'collection':'objects','limit':1},
             {'collection':'objects','spatial':{'state_code':'NADR','predicate':'intersects'},'limit':1}]
    with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as temp, sync_playwright() as p:
        folder=Path(temp);browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page=browser.new_page(viewport={'width':1440,'height':1000})
        page.goto('http://127.0.0.1:8788/almanac/query.html');page.wait_for_function('window.oswLastQueryResult',timeout=60000)
        for index,query in enumerate(queries):
            path=folder/f'query-{index}.json';path.write_text(json.dumps(query),encoding='utf-8')
            output=folder/f'map-{index}.svg'
            command=[exe,str(ROOT/'almanac/query-data.json'),'--svg',str(path),'--output',str(output)]
            result=json.loads(subprocess.check_output(command,text=True,encoding='utf-8'));assert result['ok']
            svg=output.read_text(encoding='utf-8');scene=native(query)['map_scene'];receipt=inspect(svg,query,scene)
            if index==0:assert receipt['matching_objects']==100 and receipt['mapped_objects']==100
            if index==1:assert receipt['matching_objects']==240
            if index==2:
                assert receipt['selected_state_code']=='NADR'
                assert ET.fromstring(svg).find("s:path[@class='state']",NS) is not None
            before=output.read_bytes();failure=subprocess.run(command,capture_output=True)
            assert failure.returncode==2 and output.read_bytes()==before
            browser_query(page,query)
            with page.expect_download() as downloaded:page.locator('#query-map-export').click()
            assert Path(downloaded.value.path()).read_text(encoding='utf-8')==svg
            if index==0:
                preview=browser.new_page(viewport={'width':1440,'height':824});preview.goto(output.as_uri())
                assert preview.locator('.mark').count()==len(scene['features'])
                preview.screenshot(path=str(ROOT/'figures/rust-query-svg-export-review.png'))
                preview.close()
        browser_query(page,{'collection':'widths'})
        assert not page.locator('#query-map-export').is_visible()
        invalid=folder/'invalid.json';invalid.write_text('{"collection":"widths"}',encoding='utf-8')
        rejected=folder/'must-not-exist.svg'
        assert subprocess.run([exe,str(ROOT/'almanac/query-data.json'),'--svg',str(invalid),'--output',str(rejected)],capture_output=True).returncode==2
        assert not rejected.exists()
        browser.close()
    print('PASS: native/WASM SVG identity, 100/240 full scenes, state highlights, source receipt, portable rendering and overwrite rejection')

if __name__=='__main__':main()
